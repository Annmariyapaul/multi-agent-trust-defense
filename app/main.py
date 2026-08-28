from app.graph.workflow import build_graph


def main():

    graph = build_graph()

    query = input("\nEnter your query: ")

    initial_state = {
        "user_query": query,
        "retrieved_information": [],
        "validation_result": "",
        "final_report": "",
    }

    result = graph.invoke(initial_state)

    print("\n==============================")
    print("FINAL REPORT")
    print("==============================")

    print(result["final_report"])


if __name__ == "__main__":
    main()