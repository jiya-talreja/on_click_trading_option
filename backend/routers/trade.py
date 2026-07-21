from fastapi import APIRouter,HTTPException
from services.trade_manager import Trade_manager
import pandas as pd
router=APIRouter()
trade_manager=Trade_manager()
from models.trade_model import Tradeinput
df=pd.read_csv("api-scrip-master.csv")
token_lookup=dict(
    zip(df['SEM_TRADING_SYMBOL'].str.upper(),df['SEM_SMST_SECURITY_ID'])
    )#hashmap or dictionary from two list club together by zip
@router.post("/trade")
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
        trade_order=trade_manager.business_logic(trade_context)
        return {
            "trade":trade_order
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
