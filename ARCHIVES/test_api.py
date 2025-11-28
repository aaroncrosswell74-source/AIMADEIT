import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def pretty_print(title, data):
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=4))

# Health check
resp = requests.get(f"{BASE_URL}/api/health")
pretty_print("Health Check", resp.json())

# Node map
resp = requests.get(f"{BASE_URL}/api/nodes/map")
pretty_print("Node Map", resp.json())

# Access status for a node
node_code = "ENGINE.CORE"  # example node
resp = requests.get(f"{BASE_URL}/api/access/status", params={"node_code": node_code})
pretty_print(f"Access Status - {node_code}", resp.json())

# Submit an access request
payload = {
    "user_id": "mock_user_1",   # mock user ID
    "node_code": node_code,
    "evidence": "Providing a glyph as proof"
}
resp = requests.post(f"{BASE_URL}/api/access/request", json=payload)
pretty_print(f"Access Request - {node_code}", resp.json())

# Admin approve example
admin_payload = {
    "user_id": "mock_user_1",
    "node_code": node_code,
    "granted_by": "admin_001"
}
resp = requests.post(f"{BASE_URL}/admin/approve", params=admin_payload)
pretty_print(f"Admin Approve - {node_code}", resp.json())
