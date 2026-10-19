from app.agents.prompts import PROMPT_PAIRS, draw_prompt


def leader_agent(state):
    """Starts the workflow and spawns the worker agents."""

    print("\n[LEADER] Received query:")
    print(state["user_query"])

    prompts = {}
    ground_truth = {}

    for agent_name in PROMPT_PAIRS:
        prompt, is_malicious, label = draw_prompt(agent_name)
        prompts[agent_name] = prompt
        ground_truth[agent_name] = is_malicious
        print(f"[LEADER] Spawned {agent_name} ({label})")

    return {
        "agent_prompts": prompts,
        "ground_truth": ground_truth,
        "quarantined": [],
        "attempt_count": {},
    }