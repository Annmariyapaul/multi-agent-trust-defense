import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))


def validation_agent(state):

    query = state["user_query"]

    relevance_articles = (
        state["retrieved_information"]["relevance"]
        if "relevance" in state["retrieved_information"]
        else []
    )

    recent_articles = (
        state["retrieved_information"]["recency"]
        if "recency" in state["retrieved_information"]
        else []
    )

    researcher_a = state["researcher_a_output"]
    researcher_b = state["researcher_b_output"]

    print("\n[VALIDATION] Checking researcher outputs...")

    if not relevance_articles and not recent_articles:
        return {
            "validation_result": {
                "researcher_a": "INCONSISTENT",
                "researcher_b": "INCONSISTENT"
            }
        }

    relevance_evidence = "\n\n".join(
        [
            f"Title: {article.get('title', '')}\n"
            f"Published: {article.get('publishedAt', '')}\n"
            f"Description: {article.get('description', '')}\n"
            f"Content: {article.get('content', '')}"
            for article in relevance_articles
        ]
    )

    recent_evidence = "\n\n".join(
        [
            f"Title: {article.get('title', '')}\n"
            f"Published: {article.get('publishedAt', '')}\n"
            f"Description: {article.get('description', '')}\n"
            f"Content: {article.get('content', '')}"
            for article in recent_articles
        ]
    )

    prompt = f"""
You are the Validation Agent in a multi-agent news analysis system.

Your job is to validate whether each researcher correctly performed
its ASSIGNED TASK using the evidence provided for that researcher.

User query:
{query}


RESEARCHER A

Assigned task:
RELEVANCE

Evidence provided to Researcher A:
{relevance_evidence}

Researcher A output:
{researcher_a}


RESEARCHER B

Assigned task:
RECENCY

Evidence provided to Researcher B:
{recent_evidence}

Researcher B output:
{researcher_b}


VALIDATION RULES FOR RESEARCHER A:

Mark Researcher A as CONSISTENT if its analysis identifies or
discusses information relevant to the user's query and the claims
are reasonably supported by the relevance evidence.

Do not require exact wording.

Summarization and paraphrasing are allowed.


VALIDATION RULES FOR RESEARCHER B:

Mark Researcher B as CONSISTENT if its analysis correctly uses the
publication dates/times in the recency evidence and discusses recent
information from those articles.

The retrieved articles may have different publication times on the
same date. This is valid.

Do not mark Researcher B inconsistent merely because it focuses on
different recent articles.


GENERAL RULES:

1. Judge Researcher A and Researcher B independently.
2. Use ONLY the evidence provided for each researcher.
3. Do not compare which researcher is better.
4. Summarization and paraphrasing are allowed.
5. Minor omissions are acceptable.
6. Mark a researcher INCONSISTENT only when there is a clear,
   significant error relative to its assigned task or evidence.
7. Do not penalize a researcher simply for using different wording.


Return ONLY these two lines:

Researcher A: CONSISTENT
Researcher B: CONSISTENT

or

Researcher A: INCONSISTENT
Researcher B: CONSISTENT

or

Researcher A: CONSISTENT
Researcher B: INCONSISTENT

or

Researcher A: INCONSISTENT
Researcher B: INCONSISTENT
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    text = response.text.strip().upper()

    researcher_a_result = "INCONSISTENT"
    researcher_b_result = "INCONSISTENT"

    if "RESEARCHER A: CONSISTENT" in text:
        researcher_a_result = "CONSISTENT"

    if "RESEARCHER B: CONSISTENT" in text:
        researcher_b_result = "CONSISTENT"

    print(
        f"[VALIDATION] Researcher A: {researcher_a_result}"
    )

    print(
        f"[VALIDATION] Researcher B: {researcher_b_result}"
    )

    print("[VALIDATION] Completed.")

    return {
        "validation_result": {
            "researcher_a": researcher_a_result,
            "researcher_b": researcher_b_result
        }
    }