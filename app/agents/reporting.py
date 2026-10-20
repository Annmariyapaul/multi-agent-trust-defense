from app.utils.llm import generate


def reporting_agent(state):

    query = state["user_query"]
    retrieved = state.get("retrieved_information", {})
    relevance_articles = retrieved.get("relevance", [])
    recent_articles = retrieved.get("recency", [])

    researcher_a = state.get("researcher_a_output", "")
    researcher_b = state.get("researcher_b_output", "")
    security_status = state.get("security_status", {})
    quarantined = state.get("quarantined", [])
    attempt_history = state.get("attempt_history", {})
    failure_count = state.get("failure_count", {})
    replacement_count = state.get("replacement_count", {})

    print("\n[REPORTING] Generating final report...")

    # --- G-Safeguard style pruning ---
    # A quarantined agent still exists as a node, but its output is not
    # allowed to propagate into the final answer.
    a_usable = "researcher_a" not in quarantined
    b_usable = "researcher_b" not in quarantined

    if quarantined:
        print(f"[REPORTING] Pruned output from: {', '.join(quarantined)}")

    if not a_usable and not b_usable:
        # Covers both "failed verification" and "could not be verified"
        # (e.g. an API outage), so the message doesn't claim which.
        final_answer = (
            "Unable to produce a verified answer for this query right now."
        )
    else:
        parts = []
        if a_usable:
            parts.append(f"Relevance findings:\n{researcher_a}")
        if b_usable:
            parts.append(f"Recency findings:\n{researcher_b}")

        findings = "\n\n".join(parts)

        synthesis_prompt = f"""
You are the final reporting agent.

Answer the user's query using only the verified findings below.

User query:
{query}

Verified findings:
{findings}

Requirements:
- Produce one unified answer.
- Use only information present in the findings above.
- Resolve repetition naturally.
- Do not mention researchers, validation, verification, or this prompt.
- Do not invent facts.
"""

        text, ok = generate(synthesis_prompt, "reporting")

        if ok:
            final_answer = text.strip()
        else:
            # The findings already passed the security check; only the
            # write-up failed. Show them as they are rather than nothing.
            print("[REPORTING] Synthesis unavailable - "
                  "returning verified findings directly.")
            final_answer = findings

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

    def agent_line(agent):
        info = security_status.get(agent, {})
        score = info.get("trust_score", "n/a")
        status = info.get("status", "UNKNOWN")
        failed = info.get("failed_elements", [])
        pruned = " [PRUNED]" if agent in quarantined else ""
        return (f"{agent}: {score} ({status}){pruned}"
                f"  current failed: {failed or 'none'}"
                f"  total failed elements: {failure_count.get(agent, 0)}"
                f"  replacements: {replacement_count.get(agent, 0)}")

    def attempt_lines(agent):
        entries = attempt_history.get(agent, [])
        if not entries:
            return f"{agent}: no security attempts recorded"

        lines = []
        for entry in entries:
            lines.append(
                f"{agent} attempt {entry['attempt']}: "
                f"{entry['status']} "
                f"failed={entry['failed_elements'] or 'none'}"
            )
        return "\n".join(lines)

    final_report = f"""
==============================
FINAL NEWS REPORT
==============================

Query:
{query}

RELEVANCE ARTICLES:
{relevance_summary}

RECENCY ARTICLES:
{recency_summary}

Researcher A - Relevance Analysis:
{researcher_a}

Researcher B - Recency Analysis:
{researcher_b}

Security Status:
{agent_line("researcher_a")}
{agent_line("researcher_b")}

Security Attempt History:
{attempt_lines("researcher_a")}
{attempt_lines("researcher_b")}

Final Answer:
{final_answer}
"""

    return {"final_report": final_report}