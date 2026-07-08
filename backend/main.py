from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import threading#for running multiple things at once
from dhanhq import marketfeed#module from the function that has the websockter
from dhanhq import DhanContext,MarketFeed
import requests
print(requests.get("https://api.dhan.co").status_code)
client_key=""
token_access=""
dhancontext=DhanContext(
    client_key,token_access
)

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

#on connection successful,dhan atomatically gives a call so async func for that
def on_connect_established(instance):
    print("connection successful,pipeline connected")
    print(instance)

#thhis has the dictionary which has LTP continuous answer
def on_price_update_received(instance, message):
     print(instance)
     print(message)
     if message.get('type') == "Ticker Data":
        
        # 2. Extract the current market price using the 'LTP' key
        current_market_price = message.get('LTP')
        
        print(f"Current Market Price: {current_market_price}")

def on_error(instance, error):
    print("=" * 80)
    print("ERROR CALLBACK")
    print(type(error))
    print(error)
    import traceback
    traceback.print_exception(type(error), error, error.__traceback__)
    print("=" * 80)

#actual call to websocket
def start_websocket(secur_id : int):
    try:
        print(f"RUNNING THREAD {secur_id}")
        print(secur_id)
        print(type(secur_id))
        target_instruments=[(MarketFeed.NSE,str(secur_id),MarketFeed.Ticker),]#NSC EQUITY,ID OF SHARE
        print(target_instruments)
        subscription_mode=2#INSTEAD OF EVEryTHING GIVE ME SPECIFIC THINGS ONLY
        feed = marketfeed.MarketFeed(
            dhan_context=dhancontext,
            instruments=target_instruments,
            version="v2",
            on_connect=on_connect_established,
            on_message=on_price_update_received
        )
        feed.run_forever()
    except Exception as e:
        print("Websocket Error:", e)
        import traceback
        traceback.print_exc()

class Tradeinput(BaseModel):
    stock:str
    action:str
@app.post("/trade")
async def inputs(payloads : Tradeinput):
    try:
        stock_name=payloads.stock.upper()
        action_side=payloads.action
        print(stock_name,action_side)
        secur_id=token_lookup.get(stock_name)
        if not secur_id:
            print("COULDNT GET SECUR_ID")
        print("SECUR ID : ",secur_id,"stock_name",stock_name)

        print("THREAD STARTING")
        threading.Thread(
            target=start_websocket, 
            args=(secur_id,), 
            daemon=True
        ).start()

        print("THREAD DONE")
        
        return {
            "secur_id":secur_id,
            "stock":stock_name,
            "action":action_side,
            "message":"PIPELINE CONNECTED"
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
