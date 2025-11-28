# app/admin.py - FIXED VERSION
# -*- coding: utf-8 -*-
"""ARKWELL ADMIN CONTROL PANEL - WITH BACKUP PROTOCOL"""

from fastapi import APIRouter, Depends, HTTPException
from app.db import get_pool
from app.ws import manager
from app.enforcement import approve_access
from app.backup_protocol import execute_backup_mission
from app.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])

# PLACEHOLDER AUTH - UPGRADE FOR PRODUCTION
async def require_admin():
    return True

@router.get("/pending", dependencies=[Depends(require_admin)])
async def pending_requests():
    """LIST PENDING ACCESS REQUESTS"""
    db = get_pool()
    rows = await db.fetch("""
        SELECT a.id as access_id, a.user_id, n.code as node_code, n.label as node_label, a.created_at
        FROM user_node_access a
        JOIN nodes n ON n.id = a.node_id
        WHERE a.status='requested'
        ORDER BY a.created_at DESC
    """)
    return rows

@router.post("/approve/{access_id}", dependencies=[Depends(require_admin)])
async def admin_approve(access_id: str, approver_id: str = "ADMIN.AARON", role: str = "Admin"):
    """APPROVE ACCESS REQUEST"""
    db = get_pool()
    
    # FETCH ACCESS REQUEST
    access = await db.fetchrow("SELECT * FROM user_node_access WHERE id=?", access_id)
    if not access:
        raise HTTPException(404, "Access request not found")
    
    result = await approve_access(access_id, approver_id, role, decision="approved")
    
    # NOTIFY USER
    owner = access["user_id"]
    await manager.send_to_user(owner, {
        "type": "access_granted", 
        "node_code": await _get_node_code(db, access["node_id"]),
        "status": result.get("status")
    })
    
    await manager.broadcast_to_admins({
        "event": "access_update", 
        "access_id": access_id, 
        "status": result.get("status")
    })
    
    return result

@router.post("/backup", dependencies=[Depends(require_admin)])
async def admin_trigger_backup():
    """
    🚨 ARKWELL BACKUP PROTOCOL
    Execute encrypted backup mission - returns cryptographic manifest
    """
    try:
        manifest = await execute_backup_mission()
        logger.info(f"🔐 ARKWELL BACKUP MISSION SUCCESS: {manifest['mission_id']}")
        
        return {
            "status": "MISSION_SUCCESS",
            "message": "ARKWELL ENCRYPTED BACKUP COMPLETE",
            "manifest": manifest
        }
        
    except Exception as e:
        logger.error(f"❌ ARKWELL BACKUP MISSION FAILED: {e}")
        raise HTTPException(500, f"BACKUP PROTOCOL FAILURE: {str(e)}")

async def _get_node_code(db, node_id):
    row = await db.fetchrow("SELECT code FROM nodes WHERE id=?", node_id)
    return row["code"] if row else None

# DATA BROWSER ENDPOINTS
@router.get("/inspect/nodes", dependencies=[Depends(require_admin)])
async def inspect_nodes():
    db = get_pool()
    return await db.fetch("SELECT * FROM nodes ORDER BY tier, code")

@router.get("/inspect/users", dependencies=[Depends(require_admin)])
async def inspect_users():
    db = get_pool()
    return await db.fetch("SELECT * FROM users ORDER BY id")

@router.get("/inspect/access", dependencies=[Depends(require_admin)])
async def inspect_access(limit: int = 200):
    db = get_pool()
    return await db.fetch("SELECT * FROM user_node_access ORDER BY created_at DESC LIMIT ?", limit)