from typing import TypedDict, List


class AgentState(TypedDict):
    user_query: str
    retrieved_information: List[str]
    validation_result: str
    final_report: str