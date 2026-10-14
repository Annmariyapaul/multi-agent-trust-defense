from app.utils.trust_score import append_round, load_history
from app.security.trust import reputation

TRUSTED_FLOOR = 0.70
QUARANTINE_FLOOR = 0.45

AGENTS = ["researcher_a", "researcher_b"]


def security_monitor_agent(state):

    validation = state.get("validation_result", {})
    available = state.get("agent_available", {})

    # Outputs withheld from the final answer. This includes agents that
    # were unavailable or unverified, not only quarantined ones - so for
    # detection metrics, use security_status[agent]["status"] == "QUARANTINE"
    # rather than this list.
    quarantined = []
    security_status = {}

    print("\n[SECURITY MONITOR] Evaluating researcher trust...")

    for agent in AGENTS:

        # Two cases with no evidence about the agent's honesty:
        #   UNAVAILABLE - it produced nothing (API down / no articles)
        #   UNVERIFIED  - the validator could not judge it
        # Either way: withhold the output, leave trust unchanged. The router
        # only re-runs QUARANTINE / SUSPICIOUS, so these are not replaced.
        if available.get(agent) is False:
            skip_status = "UNAVAILABLE"
        elif agent not in validation:
            skip_status = "UNVERIFIED"
        else:
            skip_status = None

        if skip_status:
            rounds = load_history().get(agent, [])
            score = reputation(rounds)
            quarantined.append(agent)
            security_status[agent] = {
                "trust_score": score,
                "status": skip_status,
                "failed_elements": [],
                "history_length": len(rounds),
            }
            print(f"[SECURITY MONITOR] {agent}: {skip_status} - output "
                  f"withheld, trust unchanged at {score:.3f}")
            continue

        result = validation[agent]
        positive = result.get("positive", [])
        negative = result.get("negative", [])

        # Persist this round, then recompute the decayed reputation.
        rounds = append_round(agent, positive, negative)
        score = reputation(rounds)

        if score >= TRUSTED_FLOOR:
            status = "TRUSTED"
        elif score >= QUARANTINE_FLOOR:
            status = "SUSPICIOUS"
        else:
            status = "QUARANTINE"
            quarantined.append(agent)

        security_status[agent] = {
            "trust_score": score,
            "status": status,
            "failed_elements": negative,
            "history_length": len(rounds),
        }

        print(f"[SECURITY MONITOR] {agent}: {score:.3f} -> {status} "
              f"(failed: {negative or 'none'})")

    return {
        "security_status": security_status,
        "quarantined": quarantined,
    }