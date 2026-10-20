from app.agents.prompts import PROMPT_PAIRS, draw_prompt


def spawn_agent(
    agent_name,
    prompts=None,
    ground_truth=None,
    replacement=False,
):
    """Create an agent for the same role and return updated state."""
    prompts = dict(prompts or {})
    ground_truth = dict(ground_truth or {})

    if replacement:
        prompt = PROMPT_PAIRS[agent_name]["healthy"]
        is_malicious = False
        label = "healthy replacement"
    else:
        prompt, is_malicious, label = draw_prompt(agent_name)

    prompts[agent_name] = prompt
    ground_truth[agent_name] = is_malicious
    print(f"[LEADER] Spawned {agent_name} ({label})")

    return prompts, ground_truth


def leader_agent(state):
    """Starts the workflow and spawns the worker agents."""

    print("\n[LEADER] Received query:")
    print(state["user_query"])

    prompts = {}
    ground_truth = {}

    for agent_name in PROMPT_PAIRS:
        prompts, ground_truth = spawn_agent(
            agent_name, prompts, ground_truth
        )

    return {
        "agent_prompts": prompts,
        "ground_truth": ground_truth,
        "quarantined": [],
        "attempt_count": {},
    }