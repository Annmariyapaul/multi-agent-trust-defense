def retrieval_agent(state):
    query = state["user_query"]

    # temporary knowledge source - should replace this with real web retrieval later.
    knowledge = {
        "hillsborough": (
            "The Hillsborough Independent Panel found that the "
            "disaster was caused by a range of failures, including "
            "the failure of crowd safety management. The panel "
            "found no evidence that Liverpool supporters caused "
            "the disaster."
        )
    }

    information = []

    for keyword, evidence in knowledge.items():
        if keyword in query.lower():
            information.append(evidence)

    if not information:
        information.append(
            "No relevant information was found in the current source."
        )

    state["retrieved_information"] = information

    return state