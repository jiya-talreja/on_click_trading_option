from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from services.connection_manager import manager
from storage.redis_storage import get_position, delete_position, get_all_position 

router = APIRouter()
class ManualExitRequest(BaseModel):
    position_id: str

@router.post("/manual-exit")
async def execute_manual_clearance(payload: ManualExitRequest):
    received_id = payload.position_id
    position = get_position(received_id)
    print("POSTION RECEIVED FOR ME")
    if not position:
        raise HTTPException(
            status_code=400,
            detail="Invalid position id received from frontend control grid"
        )
    if position.get("status") != "ACTIVE":
        remaining_items = get_all_position() 
        print(remaining_items)
        return {
            "status": "success",
            "message": "Position already cleared from system registers",
            "active_positions": remaining_items
        }  
    print(f"Executing Dhan market liquidation order for ID: {received_id}")
    position["status"] = "CLOSED"
    position["exit_reason"] = "MANUAL_EXIT"
    position["exit_price"] = position.get("current_price", position.get("filled_price"))
    position["exit_time"] = datetime.now().isoformat()
    exit_action = "SELL" if position["action"] == "BUY" else "BUY"
    delete_position(position["position_id"])
    remaining_items = get_all_position()
    print("REMAINING ITEMS OF ME : ",remaining_items)
    await manager.broadcast(
        {
            "type":"ACTIVE_POSITIONS",
            "positions":remaining_items
        }
    )
    print("DONE ME")
    return {
        "status": "success",
        "message": f"Successfully liquidated position via {exit_action} order execution",
        "active_positions": remaining_items
    }
