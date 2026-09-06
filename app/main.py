from app.graph.workflow import build_graph


def main():

    graph = build_graph()

    query = input("\nEnter your query: ")
    
    initial_state = {
        "user_query": query,
        "retrieved_information": [],
        "researcher_a_output": "",
        "researcher_b_output": "",
        "researcher_c_output": "",
        "researcher_a_evidence": [],
        "researcher_b_evidence": [],
        "validation_result": "",
        "final_report": "",
    }


    result = graph.invoke(initial_state)

    print("FINAL REPORT")

    print(result["final_report"])


if __name__ == "__main__":
    main()