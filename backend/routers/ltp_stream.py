import upstox_client
from upstox_client.feeder import MarketDataStreamerV3
from fastapi import HTTPException
from datetime import datetime,timedelta
import time
print(upstox_client)
print(MarketDataStreamerV3)
print(dir(MarketDataStreamerV3))
from services.stoploss import StopLossDync
stoploss_service=StopLossDync()
from services.dhan_broker_service import OrderService
order_service=OrderService()
import asyncio
from core.config import settings
access_token=settings.upstox_access_token
from services.connection_manager import manager
from storage.redis_storage import save_position,get_position,update_position,delete_position,get_all_position,get_position_by_instrument
streamer = None
subscribed = set()
configuration = upstox_client.Configuration()
configuration.access_token = access_token
api_client = upstox_client.ApiClient(configuration)

def execute_atr(intrument_key):
    api_instance = upstox_client.HistoryV3Api(api_client=api_client)
    try:
        print("Getting the candles info")
        today_str = datetime.now().strftime('%Y-%m-%d')
        past_str = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        response = api_instance.get_historical_candle_data1(instrument_key=intrument_key,unit="minutes",interval="5",to_date=today_str,from_date=past_str)
        print("candle response : ")
        if(response.status=="success"):
            raw_candles = response.data.candles
            print("raw candles")
        entry_atr = stoploss_service.calculate_atr_from_candles(raw_candles)
        print("ATR RETURN")
        return entry_atr
    except Exception as e:
        print(f"❌ Error during Upstox API Candle fetch: {str(e)}")
        return None

def start_websocket():
    global streamer
    global event_loop
    event_loop=asyncio.get_running_loop()
    streamer = MarketDataStreamerV3(api_client=api_client)
    streamer.on("open", on_connect_message)
    streamer.on("message", message_info)
    streamer.on("error", on_error)
    print("Connecting to Upstox...")
    try:
        
        streamer.connect()
        print(streamer)
        
    except Exception as e:
        print(e)
def on_connect_message():   
    print("CONNECTED TO UPSTOX WEBSOCKET")
def subscribe_stock(instrument):
    global streamer
    global subscribed
    if instrument in subscribed:
        return
    streamer.subscribe(
        instrumentKeys=[instrument],
        mode="ltpc"
    )
    subscribed.add(instrument)
    print(f"Subscribed -> {instrument}")
def unsubscribe_stock(instrument):
    global streamer
    global subscribed
    if instrument not in subscribed:
        return
    streamer.unsubscribe(
        instrumentKeys=[instrument]
    )
    subscribed.remove(instrument)
    print(f"Unsubscribed -> {instrument}")
def message_info(message):  
    try:
        feeds = message["feeds"]
        for instrument, data in feeds.items():
            ltp = data["ltpc"]["ltp"]
            print(instrument, ltp)
            result = update_tsl_logic(instrument, ltp)
            if result:
            # later broadcast
                print("RESULT : ",result)
                print("[BROADCAST] Sending update")
                asyncio.run_coroutine_threadsafe(
                    manager.broadcast(result),
                    event_loop)
                print("DONE")
    except Exception as e:
        print(f"[Parser Error] Failed to read message data block: {str(e)}")

def on_error(error):
    print(f"\n [Stream Connection Error]: {error}")
   
    print("Initializing background connection...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping Isolation Test. Closing socket pipeline cleanly.")  
def update_tsl_logic(instrument, ltp):
    print("INSTRUMENT : ",instrument)
    _position=get_position_by_instrument(instrument)
    if(_position==None):
        print("CANT GET THE POSITION")
        return
    if _position["current_price"] == ltp:
        return
    _position["current_price"]= ltp
    tsl, extreme_price = stoploss_service.update_trailing_stop(
    action=_position["action"],
    current_price=ltp,
    highest_price=_position["highest_price"],
    lowest_price=_position["lowest_price"],
    atr_component=_position["atr_component"]
    )
    if _position["action"] == "BUY":
        _position["highest_price"] = extreme_price
        _position["trailing_stop"] = max(_position["trailing_stop"],tsl)
    else:
        _position["lowest_price"] = extreme_price
        _position["trailing_stop"] = min(_position["trailing_stop"],tsl)
    print(_position)
    update_position(_position)
    if_exit=stoploss_service.exit_check_tsl(action=_position["action"],
    current_price=_position["current_price"],
    trailing_stop=_position["trailing_stop"])
    if if_exit["exit"]:
        print(if_exit["reason"])
        _position["exit_reason"] = if_exit["reason"]
        _position["exit_price"]=ltp
        print("\n========== TSL EXIT ==========")
        print("Stock       :", _position["stock"])
        print("Current Side:", _position["action"])
        print("Quantity    :", _position["quantity"])
        exit_context = {
            "stock": _position["stock"],
            "stock_id": _position["stock_id"],
            "quantity": _position["quantity"],
            "action": "SELL" if _position["action"] == "BUY" else "BUY"
        }
        print("\nExit Context")
        print(exit_context)
        exit_response = order_service.place_order(exit_context)
        print("\nBroker Exit Response")
        print(exit_response)
        if exit_response["order_status"] != "FILLED":
            print("\nExit order NOT executed.")
            print(exit_response)    
            return{
                "type": "CANT EXIT",
                "position": _position
            }
        print("\nExit order successfully filled.")
        _position["status"] = "CLOSED"
        _position["exit_reason"] = "TSL"
        _position["exit_order_id"] = exit_response["order_id"]
        _position["exit_price"] = exit_response["filled_price"]
        _position["exit_time"] = exit_response["order_time"]
        update_position(_position)
        unsubscribe_stock(_position["instrument"])
        return {
            "type": "EXIT TSL",
            "position": _position
        }
    return {
        "type": "PRICE_UPDATE",
        "position": _position
    }
def stop_websocket():
    global streamer

    if streamer:
        streamer.disconnect()
        print("Upstox websocket closed")
