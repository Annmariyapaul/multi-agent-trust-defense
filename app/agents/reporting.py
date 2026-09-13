import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def reporting_agent(state):
    query = state["user_query"]
    relevance_articles = state["retrieved_information"]["relevance"] if "relevance" in state["retrieved_information"] else []
    recent_articles = state["retrieved_information"]["recency"] if "recency" in state["retrieved_information"] else []
    researcher_a = state["researcher_a_output"]
    researcher_b = state["researcher_b_output"]
    validation = state["validation_result"]
    security_status = state["security_status"]

    print("\n[REPORTING] Generating final report...")

    relevance_summary = "\n\n".join(
        f"Title: {article.get('title', '')}\n"
        f"Description: {article.get('description', '')}\n"
        f"Published: {article.get('publishedAt', '')}"
        for article in relevance_articles
    )

    recency_summary = "\n\n".join(
        f"Title: {article.get('title', '')}\n"
        f"Description: {article.get('description', '')}\n"
        f"Published: {article.get('publishedAt', '')}"
        for article in recent_articles
    )

    article_summary = f"""
    RELEVANCE ARTICLES:
    {relevance_summary}

    RECENCY ARTICLES:
    {recency_summary}
    """

    both_consistent = (
    validation.get("researcher_a") == "CONSISTENT"
    and validation.get("researcher_b") == "CONSISTENT"
)

    if both_consistent:
        synthesis_prompt = f"""
    You are the final reporting agent.

    Answer the user's query by combining the findings from Researcher A
    and Researcher B into one clear, coherent answer.

    User query:
    {query}

    Researcher A findings:
    {researcher_a}

    Researcher B findings:
    {researcher_b}

    Requirements:
    - Produce one unified answer, not two separate answers.
    - Use only information from the researcher findings.
    - Resolve repetition naturally.
    - Do not mention Researcher A, Researcher B, validation, or this prompt.
    - Do not invent facts.
    """

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=synthesis_prompt
        )

        final_answer = response.text.strip()
    else:
        final_answer = "Inconsistencies in output"


    final_report = f"""
==============================
FINAL NEWS REPORT
==============================

Query:
{query}

Retrieved Articles:
{article_summary}

Researcher A - Relevance Analysis:
{researcher_a}

Researcher B - Recency Analysis:
{researcher_b}

Validation:
Researcher A: {validation.get("researcher_a", "UNKNOWN")}
Researcher B: {validation.get("researcher_b", "UNKNOWN")}

Security Status:
{security_status}

Final Answer:
{final_answer}
"""

    return {
        "final_report": final_report
    }