from services.time_exit import market_closed
from storage.redis_storage import save_position,get_position,update_position,delete_position,get_all_position
import asyncio
async def time_market_closed():
    while True:
        if market_closed():
            positions_list = get_all_position()
            for position in positions_list:
                if position["status"] != "ACTIVE":
                    continue
                print("Closing:", position["stock"])
                position["status"] = "CLOSED"
                position["exit_reason"] = "MARKET_CLOSE"
                position["exit_price"] = position["current_price"]
                update_position(position)
                print("TODO : Send exit order to broker")
        await asyncio.sleep(60) 
