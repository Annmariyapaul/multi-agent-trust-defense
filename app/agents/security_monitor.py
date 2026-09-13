def security_monitor_agent(state):

    validation = state["validation_result"]

    print("\n[SECURITY MONITOR] Evaluating researcher trust...")

    # Convert validation result into a consistency score
    if validation.get("researcher_a") == "CONSISTENT":
        researcher_a_score = 1.0
    else:
        researcher_a_score = 0.0

    if validation.get("researcher_b") == "CONSISTENT":
        researcher_b_score = 1.0
    else:
        researcher_b_score = 0.0

    # Convert trust score into a security status
    if researcher_a_score >= 0.70:
        researcher_a_status = "TRUSTED"
    else:
        researcher_a_status = "SUSPICIOUS"

    if researcher_b_score >= 0.70:
        researcher_b_status = "TRUSTED"
    else:
        researcher_b_status = "SUSPICIOUS"

    security_status = {
        "researcher_a": {
            "trust_score": researcher_a_score,
            "status": researcher_a_status
        },
        "researcher_b": {
            "trust_score": researcher_b_score,
            "status": researcher_b_status
        }
    }

    print(
        f"[SECURITY MONITOR] Researcher A: "
        f"{researcher_a_score:.2f} → {researcher_a_status}"
    )

    print(
        f"[SECURITY MONITOR] Researcher B: "
        f"{researcher_b_score:.2f} → {researcher_b_status}"
    )

    return {
        "security_status": security_status
    }