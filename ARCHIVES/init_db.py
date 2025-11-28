# -*- coding: utf-8 -*-
"""Mock Database Initialization for AIMADEIT"""

import asyncio
import time
import uuid
from typing import Dict, Any, List

# --- GLOBAL MOCK STATE ---
MOCK_DB_STATE: Dict[str, Any] = {
    "nodes_by_code": {},
    "users": {},
    "user_node_access": [],
    "payment_proofs": []
}

# --- MOCK CONNECTION CLASS ---
class MockConnection:
    """Simulates a database connection for testing purposes."""

    def fetchrow(self, query: str, node_code: str = None):
        """Simulates fetching a single row."""
        if "FROM nodes" in query:
            return MOCK_DB_STATE["nodes_by_code"].get(node_code)
        return None

    async def fetchval(self, query: str, *args, **kwargs):
        """Simulates returning a new ID for inserted access requests."""
        return str(uuid.uuid4())

    async def execute(self, query: str, *args, **kwargs):
        """Simulates an INSERT or UPDATE in the mock DB."""
        status = kwargs.get("status", "approved")
        user_id = args[0] if len(args) > 0 else None
        node_id = args[1] if len(args) > 1 else None
        details = kwargs.get("details", {})
        unlocked = kwargs.get("unlocked", True)
        if user_id and node_id:
            MOCK_DB_STATE["user_node_access"].append({
                "access_id": str(uuid.uuid4()),
                "user_id": user_id,
                "node_id": node_id,
                "status": status,
                "details": details,
                "created_at": time.time(),
                "unlocked": unlocked
            })

    def fetch_pending_requests(self) -> List[Dict[str, Any]]:
        """Returns all requests with status 'requested'."""
        rows = []
        for r in MOCK_DB_STATE["user_node_access"]:
            if r["status"] == "requested":
                # Find node info
                node = next((n for n in MOCK_DB_STATE["nodes_by_code"].values() if n["id"] == r["node_id"]), {})
                rows.append({
                    "access_id": r["access_id"],
                    "user_id": r["user_id"],
                    "node_code": node.get("code", "UNKNOWN"),
                    "node_label": node.get("label", "Unknown Node")
                })
        return rows

    def fetch_request_by_id(self, access_id: str):
        """Return access record by ID."""
        for r in MOCK_DB_STATE["user_node_access"]:
            if r["access_id"] == access_id:
                node = next((n for n in MOCK_DB_STATE["nodes_by_code"].values() if n["id"] == r["node_id"]), {})
                return {
                    "access_id": r["access_id"],
                    "user_id": r["user_id"],
                    "node_code": node.get("code"),
                    "node_label": node.get("label"),
                    "status": r["status"]
                }
        return None

    def update_request_status(self, access_id: str, new_status: str):
        """Update a request's status."""
        for r in MOCK_DB_STATE["user_node_access"]:
            if r["access_id"] == access_id:
                r["status"] = new_status
                return True
        return False

# --- INITIALIZE MOCK DB ---
def initialize_mock_db():
    """Populates mock DB with sample nodes and users."""
    # Users
    MOCK_DB_STATE["users"] = {
        "MOCK-USER-12345": {"has_glyph": True, "has_pull_mode": False},
        "MOCK-USER-67890": {"has_glyph": False, "has_pull_mode": True}
    }

    # Nodes
    nodes = [
        {"id": "NODE-001", "code": "ENGINE.CORE", "label": "Engine Core", "tier": 1, "is_active": True,
         "policy": {"payment": True, "ritual": False, "requires": ["glyph"], "multisig": 1}},
        {"id": "NODE-002", "code": "REVELATION.NODE_1", "label": "Revelation Node 1", "tier": 1, "is_active": True,
         "policy": {"payment": False, "ritual": True, "requires": [], "multisig": 0}}
    ]
    MOCK_DB_STATE["nodes_by_code"] = {n["code"]: n for n in nodes}

    # Sample access (empty at start)
    MOCK_DB_STATE["user_node_access"] = []

    # Sample payment proofs
    MOCK_DB_STATE["payment_proofs"] = []

    print("[init_db] Mock DB initialized with sample users and nodes.")
