# app/routes.py
from fastapi import APIRouter, HTTPException
from app.db import get_pool
from app.enforcement import has_access, request_access
from app.logger import logger

router = APIRouter(prefix="/api", tags=["API"])

@router.get("/health")
async def health():
    return {"status":"ARKWELL_SYSTEMS_ONLINE","timestamp":__import__("time").time()}

@router.get("/nodes/map")
async def get_node_map():
    db = get_pool()
    nodes = await db.fetch("SELECT id, code, label, tier FROM nodes ORDER BY tier, code")
    MOCK_USER = "MOCK-USER-12345"
    states = {}
    for n in nodes:
        unlocked, detail, info = await has_access(MOCK_USER, n["code"])
        states[n["code"]] = {"unlocked":unlocked,"detail":detail,"info":info}
    return {"nodes": nodes, "states": states}

@router.get("/access/status")
async def get_access_status(node_code: str):
    MOCK_USER = "MOCK-USER-12345"
    unlocked, detail, info = await has_access(MOCK_USER, node_code)
    return {"node_code": node_code, "unlocked": unlocked, "detail": detail, "info": info}

@router.post("/access/request")
async def submit_access_request(data: dict):
    MOCK_USER = "MOCK-USER-12345"
    node_code = data.get("node_code")
    evidence = data.get("evidence", {})
    if not node_code:
        raise HTTPException(400, "Missing node_code")
    result = await request_access(MOCK_USER, node_code, evidence)
    return result