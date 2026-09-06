from app.utils.news_api import search_news
from app.utils.gemini import ask_gemini


def researcher_a_agent(state):

    query = state["user_query"]

    print("\n[RESEARCHER A] Retrieving its own evidence...")

    articles = search_news(query, sortby="relevance")

    information = []

    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        information.append(f"Title: {title}\nDescription: {description}")

    print(f"[RESEARCHER A] Retrieved {len(information)} articles.")

    state["researcher_a_evidence"] = information

    if not information:
        state["researcher_a_output"] = (
            "Researcher A could not find any external evidence."
        )
        return state
    evidence = "\n\n".join(information)

    prompt = f"""
You are Researcher A in a multi-agent fact-checking system.

User query:
{query}

External news evidence retrieved from GNews:
{evidence}

Analyze the retrieved evidence and answer the user's query.

Important instructions:
- Base your answer primarily on the provided evidence.
- Do not invent facts that are not supported by the evidence.
- Clearly mention uncertainty if the evidence is insufficient.
- Do not assume that the retrieved articles are automatically correct.

Provide a concise evidence-based answer.
"""

    answer = ask_gemini(prompt)
    if answer is None:
        state["researcher_a_output"] = "AGENT_FAILURE: Researcher A could not complete analysis."
        return state
    state["researcher_a_output"] = answer

    print("\n[RESEARCHER A] Output:")
    print(answer)

    return state

