from typing import TypedDict, List, Dict, Annotated


def merge_dicts(left, right):
    """Combine concurrent writes from parallel nodes (A and B run together)."""
    return {**(left or {}), **(right or {})}


class AgentState(TypedDict):
    user_query: str
    retrieved_information: Dict[str, List[Dict]]
    researcher_a_output: str
    researcher_b_output: str
    validation_result: Dict
    security_status: Dict
    final_report: str
    attempt_history: Dict[str, List[Dict]]
    failure_count: Dict[str, int]
    replacement_count: Dict[str, int]

    # --- remediation / simulation ---
    quarantined: List[str]
    attempt_count: Annotated[Dict[str, int], merge_dicts]
    agent_prompts: Annotated[Dict[str, str], merge_dicts]
    ground_truth: Annotated[Dict[str, bool], merge_dicts]

    # False = the agent produced nothing (API down / no articles).
    # Must be declared here: LangGraph silently drops undeclared keys.
    agent_available: Annotated[Dict[str, bool], merge_dicts]