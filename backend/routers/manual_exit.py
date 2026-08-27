from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from services.connection_manager import manager
from storage.redis_storage import get_position, delete_position, get_all_position,update_position
from services.dhan_broker_service import OrderService
order_service=OrderService()
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
    print("\n========== MANUAL EXIT ==========")
    print("Position ID :", received_id)
    print("Stock       :", position["stock"])
    print("Current Side:", position["action"])
    print("Quantity    :", position["quantity"])
    exit_context = {
        "stock": position["stock"],
        "stock_id": position["stock_id"],
        "quantity": position["quantity"],
        "action": "SELL" if position["action"] == "BUY" else "BUY"
    }
    print("\nExit Context")
    print(exit_context)
    exit_response = order_service.place_order(exit_context)
    print("\nBroker Exit Response")
    print(exit_response)
    if exit_response["order_status"] != "FILLED":
        print("\nExit order NOT executed.")
        print(exit_response)    
        raise HTTPException(
            status_code=500,
            detail="Broker failed to exit position."
        )
    print("\nExit order successfully filled.")
    position["status"] = "CLOSED"
    position["exit_reason"] = "MANUAL_EXIT"
    position["exit_order_id"] = exit_response["order_id"]
    position["exit_price"] = exit_response["filled_price"]
    position["exit_time"] = exit_response["order_time"]
    update_position(position)
    print("DELTING POSITION")
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
        "message": "Successfully liquidated position via  order execution",
        "active_positions": remaining_items
    }
