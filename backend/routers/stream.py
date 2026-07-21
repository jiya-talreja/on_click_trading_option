from fastapi import APIRouter,HTTPException
from fastapi import WebSocket, WebSocketDisconnect
from services.stoploss import StopLossDync
from storage.redis_storage import save_position,get_position,update_position,delete_position,get_all_position
router=APIRouter()
@router.websocket("/trade-stream")
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
                if_exit=stoploss_service.exit_check_tsl(action=_position["action"],
                current_price=_position["current_price"],
                trailing_stop=_position["trailing_stop"])
                if if_exit["exit"]:
                    print(if_exit["reason"])
                    _position["status"] = "CLOSED"
                    _position["exit_reason"] = if_exit["reason"]
                    _position["exit_price"]=updated_price
                    update_position(_position)
                    break
    except WebSocketDisconnect:
        print("Extension Disconnected")
