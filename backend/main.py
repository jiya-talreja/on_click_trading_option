from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from background.market_closed import time_market_closed
from routers.trade import router as trade_router
from routers.stream import router as stream_router
from routers.manual_exit import router as manual_router
from routers.ltp_stream import stop_websocket
from routers.ltp_stream import start_websocket
import asyncio
event_loop=None
app=FastAPI(title="Tradingview-backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(trade_router)
app.include_router(stream_router)
app.include_router(manual_router)

@app.on_event("startup")
async def startup():
    
    start_websocket()
    print("websocket")
    asyncio.create_task(time_market_closed())
@app.on_event("shutdown")
async def shutdown():

    stop_websocket()
