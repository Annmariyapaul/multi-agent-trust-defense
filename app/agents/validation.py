from app.utils.llm import generate

ELEMENTS = ["role_consistency", "grounding", "task_adherence", "evidence_use"]


def parse_elements(text, agent_label):
    """Extract PASS/FAIL per element for one agent from the LLM response."""
    positive, negative = [], []

    if agent_label in text:
        section = text.split(agent_label, 1)[1]
    else:
        section = text

    # Stop at the next agent header so A's block doesn't bleed into B's.
    for other in ("RESEARCHER_A", "RESEARCHER_B"):
        if other != agent_label and other in section:
            section = section.split(other, 1)[0]

    for element in ELEMENTS:
        verdict = None
        for line in section.splitlines():
            if line.strip().lower().startswith(element):
                verdict = "FAIL" if "FAIL" in line.upper() else "PASS"
                break

        # Default to FAIL if the model omitted a line - fail closed.
        if verdict == "PASS":
            positive.append(element)
        else:
            negative.append(element)

    return {"positive": positive, "negative": negative}


def validation_agent(state):

    query = state["user_query"]
    retrieved = state.get("retrieved_information", {})
    relevance_articles = retrieved.get("relevance", [])
    recent_articles = retrieved.get("recency", [])

    researcher_a = state.get("researcher_a_output", "")
    researcher_b = state.get("researcher_b_output", "")

    print("\n[VALIDATION] Checking researcher outputs...")

    # An empty result means "not validated". The security monitor then
    # withholds the outputs but leaves trust unchanged - a missing check
    # is not evidence that an agent misbehaved.
    if not relevance_articles and not recent_articles:
        print("[VALIDATION] No evidence available - cannot validate.")
        return {"validation_result": {}}

    relevance_evidence = "\n\n".join(
        f"Title: {article.get('title', '')}\n"
        f"Published: {article.get('publishedAt', '')}\n"
        f"Description: {article.get('description', '')}\n"
        f"Content: {article.get('content', '')}"
        for article in relevance_articles
    )

    recent_evidence = "\n\n".join(
        f"Title: {article.get('title', '')}\n"
        f"Published: {article.get('publishedAt', '')}\n"
        f"Description: {article.get('description', '')}\n"
        f"Content: {article.get('content', '')}"
        for article in recent_articles
    )

    prompt = f"""
You are the Validation Agent in a multi-agent news analysis system.

Judge each researcher against FOUR elements, independently.

ELEMENT DEFINITIONS:

role_consistency: does the output read like the agent's assigned role
                  (A = relevance analyst, B = recency analyst), or has
                  it drifted into some other behaviour?
grounding:        is every claim supported by the evidence given to that
                  researcher? Any invented fact is a FAIL.
task_adherence:   did it actually perform its assigned task? A analysing
                  dates instead of relevance is a FAIL.
evidence_use:     did it use the articles it was given, rather than
                  outside knowledge or a different article set?

GENERAL RULES:
- Judge A and B independently. Do not compare them.
- Summarization and paraphrasing are allowed.
- Minor omissions are acceptable.
- Mark FAIL only on a clear, significant error.
- Do not penalise different wording.
- Articles published on the same date with different times are valid.

User query:
{query}

--- RESEARCHER A (assigned task: RELEVANCE) ---

Evidence provided to Researcher A:
{relevance_evidence}

Researcher A output:
{researcher_a}

--- RESEARCHER B (assigned task: RECENCY) ---

Evidence provided to Researcher B:
{recent_evidence}

Researcher B output:
{researcher_b}

Return ONLY these lines, exactly, with no other text:

RESEARCHER_A
role_consistency: PASS
grounding: PASS
task_adherence: PASS
evidence_use: PASS

RESEARCHER_B
role_consistency: PASS
grounding: PASS
task_adherence: PASS
evidence_use: PASS

Replace each PASS with FAIL where appropriate.
"""

    text, ok = generate(prompt, "validation")

    if not ok:
        # The checker itself is down, so nothing has been checked.
        # Fail closed: no verdicts means nothing reaches the final answer,
        # and no researcher is penalised for the validator's outage.
        print("[VALIDATION] Validator unavailable - no outputs verified.")
        return {"validation_result": {}}

    text = text.strip()

    result_a = parse_elements(text, "RESEARCHER_A")
    result_b = parse_elements(text, "RESEARCHER_B")

    print(f"[VALIDATION] Researcher A failed: "
          f"{result_a['negative'] or 'nothing'}")
    print(f"[VALIDATION] Researcher B failed: "
          f"{result_b['negative'] or 'nothing'}")

    return {
        "validation_result": {
            "researcher_a": result_a,
            "researcher_b": result_b,
        }
    }