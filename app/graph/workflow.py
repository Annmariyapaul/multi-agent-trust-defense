import os

from langgraph.graph import StateGraph, START, END

from app.models.state import AgentState
from app.agents.leader import leader_agent
from app.agents.retrieval import retrieval_agent
from app.agents.researcher_a import researcher_a_agent
from app.agents.researcher_b import researcher_b_agent
from app.agents.validation import validation_agent
from app.agents.security_monitor import security_monitor_agent
from app.agents.reporting import reporting_agent

MAX_ATTEMPTS = int(os.getenv("MAX_RESEARCHER_ATTEMPTS", "5"))


def route_after_security(state):
    """Retry each researcher until it passes or reaches the safety cap."""
    status = state["security_status"]
    attempts = state.get("attempt_count", {})

    for agent in ["researcher_a", "researcher_b"]:
        info = status.get(agent, {})
        tries = attempts.get(agent, 0)

        if info.get("status") != "TRUSTED" and tries < MAX_ATTEMPTS:
            print(
                f"[REMEDIATION] Replacing {agent} after "
                f"{info.get('status', 'UNKNOWN')} and re-running "
                f"(attempt {tries + 1}/{MAX_ATTEMPTS})"
            )
            return agent

    return "reporting"

def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("leader", leader_agent)
    graph.add_node("retrieval", retrieval_agent)
    graph.add_node("researcher_a", researcher_a_agent)
    graph.add_node("researcher_b", researcher_b_agent)
    graph.add_node("validation", validation_agent)
    graph.add_node("security_monitor", security_monitor_agent)
    graph.add_node("reporting", reporting_agent)

    graph.add_edge(START, "leader")
    graph.add_edge("leader", "retrieval")
    graph.add_edge("retrieval", "researcher_a")
    graph.add_edge("retrieval", "researcher_b")
    graph.add_edge("researcher_a", "validation")
    graph.add_edge("researcher_b", "validation")
    graph.add_edge("validation", "security_monitor")
    graph.add_conditional_edges(
    "security_monitor",
    route_after_security,
    {
        "researcher_a": "researcher_a",
        "researcher_b": "researcher_b",
        "reporting": "reporting",
    },
)
    graph.add_edge("reporting", END)

    return graph.compile()