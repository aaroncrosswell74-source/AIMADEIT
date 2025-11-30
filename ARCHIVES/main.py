# app/main.py
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db import setup_db_pool, shutdown_db_pool
from app.ws import manager
from app.admin import router as admin_router
from app.routes import router as api_router
from app.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("--- [STARTUP] ARKWELL SYSTEMS STARTING ---")
    await setup_db_pool()
    logger.info("--- [LIFESPAN] ARKWELL DB READY ---")
    yield
    logger.info("--- [SHUTDOWN] CLOSING DB ---")
    await shutdown_db_pool()

app = FastAPI(title="ARKWELL SYSTEMS - Sovereign Access Engine", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(admin_router)

@app.websocket("/ws/updates")
async def ws_updates(ws: WebSocket, token: str = None):
    user_id = None
    is_admin = False
    
    if token == "ADMIN":
        is_admin = True
        user_id = "ADMIN.AARON"
    elif token:
        user_id = token
        
    await manager.connect(ws, user_id=user_id, is_admin=is_admin)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)
    except Exception:
        manager.disconnect(ws)

@app.get("/")
async def root():
    return {"message": "ARKWELL SYSTEMS CORP - SOVEREIGN ACCESS ENGINE ONLINE"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)