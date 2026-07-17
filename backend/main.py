from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from services.account_info import AccountService
import requests
from fastapi import WebSocket, WebSocketDisconnect

from services.quantity_info import QuantityInfo
from services.stoploss import StopLossDync
from services.validation import ValidationService
from services.order_service import OrderService
from services.position_service import PositionService
from storage.redis_storage import save_position,get_position
CAPITAL_PERCENTAGE = 90
app=FastAPI(title="Tradingview-backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
df=pd.read_csv("api-scrip-master.csv")
token_lookup=dict(
    zip(df['SEM_TRADING_SYMBOL'].str.upper(),df['SEM_SMST_SECURITY_ID'])
    )#hashmap or dictionary from two list club together by zip
class Tradeinput(BaseModel):
    stock:str
    action:str
    price:str
@app.post("/trade")
async def inputs(payloads : Tradeinput):
    try:
        stock_name=payloads.stock.upper()
        action_side=payloads.action
        price_current=float(payloads.price)

        secur_id=token_lookup.get(stock_name)
        if not secur_id:
            print("COULDNT GET SECUR_ID")

        trade_context={
            "stock":stock_name,
            "action":action_side,
            "cp":price_current,
            "stock_id":secur_id
        }

        account_service = AccountService()    
        funds=account_service.get_funds() 
        avail_amount=funds["data"]["availabelBalance"]  
        trade_context["balance"]=avail_amount
        print("FUNDS : ",funds)

        quantity_service=QuantityInfo()
        quantity=quantity_service.calculate_quantity(avail_amount,price_current,CAPITAL_PERCENTAGE)
        print(quantity)
        trade_context["quantity"]=quantity

        stoploss_service=StopLossDync()
        print(stoploss_service.stoploss(action_side,price_current,1))
        trade_context["stoploss"]=stoploss_service.stoploss(action_side,price_current,1)
        trade_context["tsl"]=stoploss_service.initialtsl(action_side,price_current,1)

        validate_service=ValidationService()
        if_true=validate_service.validate(trade_context)
        print(if_true)
        if(if_true):
            order_service=OrderService()
            trade_context=order_service.mock_order(trade_context)
            print("update trade_context")
            print(trade_context)
        if(trade_context["order_status"]=="FILLED"):
            print("a")
            position_service=PositionService()
            position=position_service.create_position(trade_context)
            print("psotion created : ",position)
            save_position(position)
            saved_position = get_position(position["position_id"])
            print(saved_position)
            trade_context["position_id"] = position["position_id"]
        return {
            "trade":trade_context
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))


@app.websocket("/trade-stream")
async def trade_stream(websocket: WebSocket):
    await websocket.accept()
    print("Extension Connected")
    stoploss_service=StopLossDync()
    try:
        while True:
            data = await websocket.receive_json()
            print("PRICE UPDATE :", data)
            if(data["position_id"]):
                updated_price=data["current_price"]
                _position=get_position(data["position_id"])
                _position["current_price"]= updated_price
                tsl, extreme_price = stoploss_service.update_trailing_stop(
                    action=_position["action"],
                    current_price=updated_price,
                    highest_price=_position["highest_price"],
                    lowest_price=_position["lowest_price"],
                    trailing_percent=1
                )
                if _position["action"] == "BUY":
                    _position["highest_price"] = extreme_price
                    _position["trailing_stop"] = max(_position["trailing_stop"],tsl)
                else:
                    _position["lowest_price"] = extreme_price
                    _position["trailing_stop"] = min(_position["trailing_stop"],tsl)
                print(_position)
                update_position(_position)
                if_exit=stoploss_service.exit_check(action=_position["action"],
                current_price=_position["current_price"],
                trailing_stop=_position["trailing_stop"])
                if if_exit["exit"]:
                    print(if_exit["reason"])#actual order to be updated
    except WebSocketDisconnect:
        print("Extension Disconnected")
