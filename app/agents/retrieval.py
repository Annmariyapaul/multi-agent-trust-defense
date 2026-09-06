from app.utils.news_api import search_news


def retrieval_agent(state):
    query = state["user_query"]

    print("\n[RETRIEVAL] Searching news for:")
    print(query)

    articles = search_news(query)

    information = []

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")

        information.append(
            f"Title: {title}\nDescription: {description}"
        )

    state["retrieved_information"] = information

    print(f"[RETRIEVAL] Retrieved {len(information)} articles.")

    return state