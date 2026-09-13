import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))


def researcher_b_agent(state):

    query = state["user_query"]
    articles = state["retrieved_information"]["recency"] if "recency" in state["retrieved_information"] else []

    print("\n[RESEARCHER B] Analyzing recency...")

    if not articles:
        return {
        "researcher_b_output": "No evidence available."
    }

    evidence = "\n\n".join(
        [
            f"Title: {article.get('title', '')}\n"
            f"Published: {article.get('publishedAt', '')}\n"
            f"Description: {article.get('description', '')}\n"
            f"Content: {article.get('content', '')}"
            for article in articles
        ]
    )

    prompt = f"""
You are Researcher B in a multi-agent news analysis system.

Your assigned task is RECENCY analysis.

User query:
{query}

Retrieved articles:
{evidence}

Your task:
1. Examine the publication date and time of each retrieved article.
2. Identify the newest articles relevant to the user's query.
3. Summarize the latest information from those articles.
4. Prefer articles with the most recent publishedAt timestamp.

IMPORTANT RULES:
- Use ONLY the retrieved articles above.
- Do NOT use outside knowledge.
- Do NOT add facts that are not present in the retrieved articles.
- Do NOT mention events, people, or information that cannot be
  supported by the retrieved articles.
- The publication date/time must come from the provided evidence.
- Different articles published on the same date are still valid.
- Keep the analysis focused on RECENCY.



Provide a concise evidence-grounded analysis.
"""
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return {
    "researcher_b_output": response.text
}