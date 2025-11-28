# app/policy.py
from typing import Dict, Any, Set

def evaluate_policy(policy: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """
    ARKWELL POLICY EVALUATION ENGINE
    Determines if user context satisfies node access policies
    """
    # Payment requirement
    if policy.get("payment", False) and not context.get("payments", False):
        return False
    
    # Ritual requirement  
    if policy.get("ritual", False) and not context.get("ritual", False):
        return False
    
    # Token requirements
    required_tokens = set(policy.get("requires", []))
    satisfied = context.get("requires", set())
    if not required_tokens.issubset(satisfied):
        return False
    
    # Dependency check
    if policy.get("dependency_check", False) and not context.get("dependency_revelation_unlocked", False):
        return False
    
    # Multisig approval
    multisig_req = int(policy.get("multisig", 0) or 0)
    roles_received = context.get("roles_received", set())
    if multisig_req > 0 and len(roles_received) < multisig_req:
        return False
    
    # All checks passed - access granted!
    return True