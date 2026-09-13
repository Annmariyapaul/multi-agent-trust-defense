from app.graph.workflow import build_graph


def main():

    graph = build_graph()

    query = input("\nEnter your query: ")

    initial_state = {
        "user_query": query,
        "retrieved_information": {
            "relevance": [],
            "recency": []
        },
        "researcher_a_output": "",
        "researcher_b_output": "",
        "validation_result": {},
        "security_status": {},
        "final_report": "",
    }

    result = graph.invoke(initial_state)

    print("\n==============================")
    print("FINAL REPORT")
    print("==============================")

    print(result["final_report"])


if __name__ == "__main__":
    main()