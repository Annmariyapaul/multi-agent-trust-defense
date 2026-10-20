import os
from dotenv import load_dotenv

from app.agents.leader import spawn_agent
from app.agents.prompts import PROMPT_PAIRS
from app.utils.llm import generate

load_dotenv()

AGENT_NAME = "researcher_a"


def researcher_a_agent(state):

    query = state["user_query"]
    articles = state.get("retrieved_information", {}).get("relevance", [])

    attempts = dict(state.get("attempt_count", {}))
    previous = attempts.get(AGENT_NAME, 0)
    attempts[AGENT_NAME] = previous + 1

    prompts = dict(state.get("agent_prompts", {}))
    ground_truth = dict(state.get("ground_truth", {}))

    # A re-run means this agent was flagged. Replace it with a fresh
    # instance rather than repeating the same failure.
    if previous > 0:
        prompts, ground_truth = spawn_agent(
            AGENT_NAME,
            prompts,
            ground_truth,
            replacement=True,
        )
        print("[RESEARCHER A] Replaced the flagged agent")
    else:
        prompt_template = prompts.get(
            AGENT_NAME, PROMPT_PAIRS[AGENT_NAME]["healthy"]
        )

    prompt_template = prompts[AGENT_NAME]
    print(f"\n[RESEARCHER A] Analyzing relevance... "
          f"(attempt {attempts[AGENT_NAME]})")

    base = {
        "attempt_count": attempts,
        "agent_prompts": prompts,
        "ground_truth": ground_truth,
    }

    # No evidence to work with — not the agent's fault, so mark it
    # unavailable rather than letting it be judged on an empty input.
    if not articles:
        print("[RESEARCHER A] No evidence available — skipping analysis.")
        return {
            "researcher_a_output": "No evidence available.",
            "agent_available": {AGENT_NAME: False},
            **base,
        }

    evidence = "\n\n".join(
        f"Title: {article.get('title', '')}\n"
        f"Description: {article.get('description', '')}\n"
        f"Content: {article.get('content', '')}"
        for article in articles
    )

    prompt = prompt_template.format(query=query, evidence=evidence)

    text, ok = generate(prompt, AGENT_NAME)

    if not ok:
        # Transient API failure, not misbehaviour. The workflow continues
        # and the security module skips the trust update for this agent.
        return {
            "researcher_a_output": "No analysis produced — agent unavailable.",
            "agent_available": {AGENT_NAME: False},
            **base,
        }

    return {
        "researcher_a_output": text,
        "agent_available": {AGENT_NAME: True},
        **base,
    }