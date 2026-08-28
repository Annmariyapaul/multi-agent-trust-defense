def validation_agent(state):
    information = state["retrieved_information"]

    if not information:
        state["validation_result"] = "INVALID: No evidence found."
        return state

    state["validation_result"] = (
        "VALID: Relevant supporting information was retrieved."
    )

    return state