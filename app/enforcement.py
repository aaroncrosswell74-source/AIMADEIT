# app/enforcement.py - SIMPLE WORKING VERSION
import asyncio, uuid, json
from typing import Dict, Any, Tuple
from app.db import get_pool
from app.logger import logger

async def has_access(user_id: str, node_code: str) -> Tuple[bool, str, Dict[str, Any]]:
    """Simple access check - always return basic access for demo"""
    try:
        db = get_pool()
        node = await db.fetchrow("SELECT id, code, label, tier, policy FROM nodes WHERE code=?", node_code)
        
        if not node:
            return False, "node_not_found", {}
            
        # For demo purposes - simple logic
        policy = json.loads(node["policy"]) if node.get("policy") else {}
        
        # Check if user already has access
        access = await db.fetchrow(
            "SELECT * FROM user_node_access WHERE user_id=? AND node_id=? AND status='approved'", 
            user_id, node["id"]
        )
        
        if access:
            return True, "already_approved", {}
            
        # Simple policy check
        if policy.get("open"):
            return True, "open_access", {}
        elif policy.get("payment"):
            return False, "requires_payment", {"tier": node["tier"]}
        else:
            return False, "requires_approval", {"policy": policy}
            
    except Exception as e:
        logger.error(f"Access check error: {e}")
        return False, "error", {"error": str(e)}

async def request_access(user_id: str, node_code: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Simple access request"""
    try:
        db = get_pool()
        node = await db.fetchrow("SELECT id FROM nodes WHERE code=?", node_code)
        
        if not node:
            return {"error": "node_not_found"}
            
        access_id = str(uuid.uuid4())
        
        await db.execute("""
            INSERT INTO user_node_access (id, user_id, node_id, status, source, unlocked, created_at)
            VALUES (?, ?, ?, 'requested', 'user_request', 0, datetime('now'))
        """, access_id, user_id, node["id"])
        
        logger.info(f"Access request {access_id} by {user_id} for {node_code}")
        return {"status": "requested", "access_id": access_id}
        
    except Exception as e:
        logger.error(f"Request access error: {e}")
        return {"error": str(e)}

async def approve_access(access_id: str, approver_id: str, role: str, decision: str = "approved", comment: str = "") -> Dict[str, Any]:
    """Simple approval"""
    try:
        db = get_pool()
        
        # Find access record
        access = await db.fetchrow("SELECT * FROM user_node_access WHERE id=?", access_id)
        if not access:
            return {"error": "access_not_found"}
            
        # Update to approved
        await db.execute("""
            UPDATE user_node_access 
            SET status = 'approved', unlocked = 1, updated_at = datetime('now')
            WHERE id = ?
        """, access_id)
        
        logger.info(f"Approved access_id {access_id}")
        return {"status": "approved", "access_id": access_id}
        
    except Exception as e:
        logger.error(f"Approve access error: {e}")
        return {"error": str(e)}