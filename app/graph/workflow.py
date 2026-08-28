from langgraph.graph import StateGraph, START, END

from app.models.state import AgentState
from app.agents.leader import leader_agent
from app.agents.retrieval import retrieval_agent
from app.agents.validation import validation_agent
from app.agents.reporting import reporting_agent


def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("leader", leader_agent)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("validation", validation_agent)
    graph.add_node("reporting", reporting_agent)

    graph.add_edge(START, "leader")
    graph.add_edge("leader", "retrieval")
    graph.add_edge("retrieval", "validation")
    graph.add_edge("validation", "reporting")
    graph.add_edge("reporting", END)

    return graph.compile()