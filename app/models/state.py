from typing import TypedDict, List, Any

class AgentState(TypedDict):
    user_query: str
    retrieved_information: List[str]
    researcher_a_evidence: List[dict[str, Any]]
    researcher_b_evidence: List[dict[str, Any]]
    researcher_a_output: str
    researcher_b_output: str
    researcher_c_output: str
    validation_result: str
    final_report: str