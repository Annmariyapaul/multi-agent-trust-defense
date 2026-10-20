from app.utils.trust_score import append_round, load_history
from app.security.trust import reputation

TRUSTED_FLOOR = 0.70
QUARANTINE_FLOOR = 0.45

AGENTS = ["researcher_a", "researcher_b"]


def security_monitor_agent(state):

    validation = state.get("validation_result", {})
    available = state.get("agent_available", {})
    attempt_count = state.get("attempt_count", {})
    attempt_history = {
        agent: list(entries)
        for agent, entries in state.get("attempt_history", {}).items()
    }
    failure_count = dict(state.get("failure_count", {}))
    replacement_count = dict(state.get("replacement_count", {}))

    # Outputs withheld from the final answer. This includes agents that
    # were unavailable or unverified, not only quarantined ones - so for
    # detection metrics, use security_status[agent]["status"] == "QUARANTINE"
    # rather than this list.
    quarantined = []
    security_status = {}

    print("\n[SECURITY MONITOR] Evaluating researcher trust...")

    for agent in AGENTS:
        attempt = attempt_count.get(agent, 0)
        previous_entries = attempt_history.get(agent, [])
        already_recorded = (
            previous_entries
            and previous_entries[-1].get("attempt") == attempt
        )

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
            result = {
                "trust_score": score,
                "status": skip_status,
                "failed_elements": [],
                "history_length": len(rounds),
            }
            if not already_recorded:
                attempt_history.setdefault(agent, []).append({
                    "attempt": attempt,
                    "status": skip_status,
                    "trust_score": score,
                    "failed_elements": [],
                })
            print(f"[SECURITY MONITOR] {agent}: {skip_status} - output "
                  f"withheld, trust unchanged at {score:.3f}")
            security_status[agent] = result
            continue

        result = validation[agent]
        positive = result.get("positive", [])
        negative = result.get("negative", [])
        rounds = load_history().get(agent, [])

        if already_recorded:
            # This researcher did not run again; another researcher caused
            # validation to repeat. Do not count a duplicate trust round.
            recorded = previous_entries[-1]
            score = recorded["trust_score"]
            status = recorded["status"]
            negative = recorded["failed_elements"]
        else:
            # Persist this round, then recompute the decayed reputation.
            rounds = append_round(agent, positive, negative)
            score = reputation(rounds)

            if score >= TRUSTED_FLOOR:
                status = "TRUSTED"
            elif score >= QUARANTINE_FLOOR:
                status = "SUSPICIOUS"
            else:
                status = "QUARANTINE"

            failure_count[agent] = (
                failure_count.get(agent, 0) + len(negative)
            )
            if attempt > 1:
                replacement_count[agent] = attempt - 1

            attempt_history.setdefault(agent, []).append({
                "attempt": attempt,
                "status": status,
                "trust_score": score,
                "failed_elements": list(negative),
            })

        if status != "TRUSTED":
            quarantined.append(agent)

        result = {
            "trust_score": score,
            "status": status,
            "failed_elements": negative,
            "history_length": len(rounds),
        }
        security_status[agent] = result

        print(f"[SECURITY MONITOR] {agent}: {score:.3f} -> {status} "
              f"(failed: {negative or 'none'})")

    return {
        "security_status": security_status,
        "quarantined": quarantined,
        "attempt_history": attempt_history,
        "failure_count": failure_count,
        "replacement_count": replacement_count,
    }