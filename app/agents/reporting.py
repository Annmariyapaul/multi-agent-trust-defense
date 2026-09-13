def reporting_agent(state):

    query = state["user_query"]
    articles = state["retrieved_information"]
    researcher_a = state["researcher_a_output"]
    researcher_b = state["researcher_b_output"]
    validation = state["validation_result"]
    security_status = state["security_status"]

    print("\n[REPORTING] Generating final report...")

    article_summary = "\n\n".join(
        [
            f"Title: {article.get('title', '')}\n"
            f"Description: {article.get('description', '')}\n"
            f"Published: {article.get('publishedAt', '')}"
            for article in articles
        ]
    )

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
The answer above is based on the retrieved news evidence and the
independent analyses produced by Researcher A and Researcher B.
"""

    return {
        "final_report": final_report
    }