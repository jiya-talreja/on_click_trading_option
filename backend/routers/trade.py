from fastapi import APIRouter,HTTPException
from services.trade_manager import Trade_manager
import pandas as pd
import json
from pathlib import Path
router=APIRouter()
trade_manager=Trade_manager()
from models.trade_model import Tradeinput
df=pd.read_csv("api-scrip-master.csv")
token_lookup=dict(
    zip(df['SEM_TRADING_SYMBOL'].str.upper(),df['SEM_SMST_SECURITY_ID'])
    )#hashmap or dictionary from two list club together by zip

CURRENT_DIR = Path(__file__).resolve().parent
json_path = CURRENT_DIR / "NSE.json"
with open(json_path,"r") as f:
    instruments=json.load(f)
CURRENT_DIR = Path(__file__).resolve().parent
json_path = CURRENT_DIR / "NSE.json"

with open(json_path, "r") as f:
    instruments = json.load(f)
upstox_lookup = {}
for item in instruments:
    if item.get("segment") == "NSE_EQ" and item.get("instrument_type") == "EQ":
        symbol = item.get("trading_symbol")
        if symbol:
            symbol_upper = symbol.strip().upper()
            upstox_lookup[symbol_upper] = item["instrument_key"]
            upstox_lookup[symbol_upper.replace(" ", "")] = item["instrument_key"]
print("LOOKUP DONE : ")

@router.post("/trade")
async def inputs(payloads : Tradeinput):
    try:
        stock_name=payloads.stock.upper()
        action_side=payloads.action
        price_current=float(payloads.price)
        secur_id=token_lookup.get(stock_name)
        print("SECUR ID : ",secur_id)
        if not secur_id:
            print("COULDNT GET SECUR_ID")
        instrument=upstox_lookup.get(stock_name)
        import pprint
        if not instrument:
            print("INSTRUMENT NOT FOUND")
        print(stock_name,instrument)
        trade_context={
            "stock":stock_name,
            "action":action_side,
            "cp":price_current,
            "stock_id":secur_id,
            "instrument":instrument
        }
        trade_order=await trade_manager.business_logic(trade_context)
        print(trade_order["stock_id"])
        print("2",type(trade_order))
        return {
            "trade":trade_order
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
