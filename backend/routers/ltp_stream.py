import upstox_client
from upstox_client.feeder import MarketDataStreamerV3

import json
import time
print(upstox_client)
print(MarketDataStreamerV3)
print(dir(MarketDataStreamerV3))
from services.stoploss import StopLossDync
stoploss_service=StopLossDync()
import asyncio
from services.connection_manager import manager
from storage.redis_storage import save_position,get_position,update_position,delete_position,get_all_position,get_position_by_instrument
streamer = None
subscribed = set()


access_token = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI2M0NRTTUiLCJqdGkiOiI2YTZhZmU1MWY4MzIyMzdkNDA5MmJkZjkiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc4NTM5NjgxNywiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzg1NDQ4ODAwfQ.pvGPio4Y8DiGpTQ9Kksl6nR0x0alSP6YRvCcHwBBm_0"
def start_websocket():
    global streamer
    global event_loop
    event_loop=asyncio.get_running_loop()
    configuration = upstox_client.Configuration()
    configuration.access_token = access_token
    api_client = upstox_client.ApiClient(configuration)
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
    if_exit=stoploss_service.exit_check_tsl(action=_position["action"],
    current_price=_position["current_price"],
    trailing_stop=_position["trailing_stop"])
    if if_exit["exit"]:
        print(if_exit["reason"])
        _position["status"] = "CLOSED"
        _position["exit_reason"] = if_exit["reason"]
        _position["exit_price"]=ltp
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
