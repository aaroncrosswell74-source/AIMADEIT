import time
import hashlib
import random
import json
from datetime import datetime

# --- Engine Configuration ---
NUM_RITUAL_PHASES = 10
# ----------------------------


def generate_lore(seed: str, phase: str, tier: int):
    """Generates mock lore based on the phase and seed."""
    base_lore = (
        f"The {phase} phase transmuted the seed. "
        f"The result indicates {hashlib.sha256(seed.encode()).hexdigest()[8]}."
    )
    if tier == 0 and "Limitation Check" in phase:
        return (
            base_lore
            + " The ritual halted due to insufficient canonical access (Tier 0). HALTED."
        )
    return base_lore


def execute_canonical_ritual(initial_seed: str, user_id: str, ritual_tier: int):
    """
    Executes the multi-phase Trideva Engine ritual.
    The process is gated by the ritual_tier.
    """

    ritual_results = []
    current_seed = initial_seed
    cycles_completed = 0

    # Define phases
    phases = [
        "Phase 1 – Seed Inception",
        "Phase 2 – Limitation Check",
        "Phase 3 – Deep Recursion",
        "Phase 4 – Coherence Mapping",
        "Phase 5 – Archetype Synthesis",
        "Phase 6 – Animus Infusion",
        "Phase 7 – Resonance Alignment",
        "Phase 8 – Temporal Staking",
        "Phase 9 – Final Encryption",
        "Phase 10 – Canonical Write",
    ]

    # Start Ritual
    for i, phase in enumerate(phases):

        # --- GATING LOGIC ---
        if ritual_tier == 0 and i == 1:  # Phase 2
            lore_output = generate_lore(current_seed, phase, ritual_tier)
            ritual_results.append({"phase": phase, "seed_output": lore_output})
            break

        # --- ENGINE LOGIC ---
        base_hash = hashlib.sha256(current_seed.encode()).hexdigest()
        new_seed = base_hash + str(int(time.time() * 1000))
        current_seed = new_seed

        lore_output = generate_lore(current_seed, phase, ritual_tier)

        ritual_results.append(
            {
                "phase": phase,
                "seed_output": lore_output,
            }
        )

        cycles_completed += 1

    final_seed = current_seed
    archetype_id = hashlib.sha256(final_seed.encode()).hexdigest()[16:24].upper()

    card_names = [
        "The Foldrider",
        "The Oracle of Elysia",
        "The Temporal Staker",
        "The Animus Weaver",
    ]

    return {
        "success": True,
        "archetype_id": archetype_id,
        "final_seed": final_seed,
        "cycles_completed": cycles_completed,
        "ritual_results": ritual_results,
        "lore_entry": f"Canonical Archetype {archetype_id}",
        "lore_description": (
            f"The Trideva Engine completed {cycles_completed} cycles "
            f"for Tier {ritual_tier}. This archetype embodies the convergence "
            f"of the seed concept."
        ),
        "card_icon": "⚛️",
        "card_name": random.choice(card_names),
    }


if __name__ == "__main__":
    test_seed = "Seek deep knowledge"
    test_user = "12345"

    print("--- Running Tier 1 Ritual ---")
    result_tier1 = execute_canonical_ritual(test_seed, test_user, ritual_tier=1)
    print(json.dumps(result_tier1, indent=2))

    print("\n--- Running Tier 0 Ritual ---")
    result_tier0 = execute_canonical_ritual(test_seed, test_user, ritual_tier=0)
    print(json.dumps(result_tier0, indent=2))
