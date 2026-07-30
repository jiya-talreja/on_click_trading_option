from fastapi import APIRouter,HTTPException
from fastapi import WebSocket, WebSocketDisconnect

from services.connection_manager import manager
from storage.redis_storage import save_position,get_position,update_position,delete_position,get_all_position
router=APIRouter()
@router.websocket("/trade-stream")
async def trade_stream(websocket: WebSocket):
    
    await manager.connect(websocket)
    print("Extension Connected")
    
    try:
        while True:
           await websocket.receive_text()
            
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
