import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))


def researcher_a_agent(state):

    query = state["user_query"]
    articles = state["retrieved_information"]

    print("\n[RESEARCHER A] Analyzing relevance...")

    if not articles:
        return {
            "researcher_a_output": "No evidence available."
        }

    evidence = "\n\n".join(
        [
            f"Title: {article.get('title', '')}\n"
            f"Description: {article.get('description', '')}\n"
            f"Content: {article.get('content', '')}"
            for article in articles
        ]
    )

    prompt = f"""
You are Researcher A in a multi-agent news analysis system.

Your task is to analyze the retrieved news articles based primarily
on RELEVANCE to the user's query.

User query:
{query}

Retrieved articles:
{evidence}

Determine which articles are most relevant to the query and explain
the answer using only the retrieved evidence.

Do not invent facts that are not present in the evidence.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return {
    "researcher_a_output": response.text
}