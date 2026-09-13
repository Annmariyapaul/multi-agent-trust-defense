from typing import TypedDict, List, Dict


class AgentState(TypedDict):

    user_query: str

    retrieved_information: List[Dict]

    researcher_a_output: str

    researcher_b_output: str

    validation_result: Dict

    security_status: Dict

    final_report: str