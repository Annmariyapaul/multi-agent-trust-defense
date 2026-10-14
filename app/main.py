from app.graph.workflow import build_graph


def main():

    graph = build_graph()

    query = input("\nEnter your query: ")

    initial_state = {
        "user_query": query,
        "retrieved_information": {"relevance": [], "recency": []},
        "researcher_a_output": "",
        "researcher_b_output": "",
        "validation_result": {},
        "security_status": {},
        "final_report": "",
        "quarantined": [],
        "attempt_count": {},
        "agent_prompts": {},
        "ground_truth": {},
        "agent_available": {},
    }

    result = graph.invoke(initial_state, config={"recursion_limit": 50})

    print("\n==============================")
    print("FINAL REPORT")
    print("==============================")
    print(result["final_report"])

    print("\n[GROUND TRUTH]", result.get("ground_truth", {}))
    print("[ATTEMPTS]", result.get("attempt_count", {}))


if __name__ == "__main__":
    main()