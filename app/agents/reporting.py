def reporting_agent(state):
    query = state["user_query"]
    information = state["retrieved_information"]
    validation = state["validation_result"]

    report = f"""
Query:
{query}

Retrieved Evidence:
{" ".join(information)}

Validation:
{validation}

Final Answer:
Based on the retrieved information, the available evidence
does not support the claim that Liverpool supporters caused
the Hillsborough disaster.
"""

    state["final_report"] = report

    return state