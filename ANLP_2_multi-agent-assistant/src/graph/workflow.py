# LangGraph definition - entire multi-agent system workflow
from langgraph.graph import StateGraph, END
from src.models import AgentState
from src.agents.router import router_node
from src.agents.research_specialist import research_specialist_node
from src.agents.coding_helper import coding_helper_node
from src.agents.planner import planner_node
from src.agents.supervisor import supervisor_node


def route_after_classification(state: AgentState) -> str:
    """Determines next node based on classification

    Args:
        state: Current state with classification results

    Returns:
        Name of next node to execute
    """
    classified_agents = state.get('classified_agents', [])

    if not classified_agents:
        return "supervisor"

    # Take first agent from list
    # (for simplicity - sequential execution)
    first_agent = classified_agents[0]

    # Mapping to node names
    agent_to_node = {
        "research_specialist": "research_specialist",
        "coding_helper": "coding_helper",
        "planner": "planner",
        "supervisor": "supervisor"
    }

    return agent_to_node.get(first_agent, "supervisor")


def create_workflow() -> StateGraph:
    """Creates and compiles LangGraph workflow

    Returns:
        Compiled workflow graph
    """
    # Create graph with typed state
    workflow = StateGraph(AgentState)

    # Add nodes (Agents)
    workflow.add_node("router", router_node)
    workflow.add_node("research_specialist", research_specialist_node)
    workflow.add_node("coding_helper", coding_helper_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("supervisor", supervisor_node)

    # Set entry point - everything starts with Router
    workflow.set_entry_point("router")

    # Conditional routing after Router
    workflow.add_conditional_edges(
        "router",
        route_after_classification,
        {
            "research_specialist": "research_specialist",
            "coding_helper": "coding_helper",
            "planner": "planner",
            "supervisor": "supervisor"
        }
    )

    # After each specialized agent -> supervisor for synthesis
    workflow.add_edge("research_specialist", "supervisor")
    workflow.add_edge("coding_helper", "supervisor")
    workflow.add_edge("planner", "supervisor")

    # Supervisor -> END (completion)
    workflow.add_edge("supervisor", END)

    # Compile and return
    return workflow.compile()


# Singleton pattern for graph reuse
_graph_instance = None


def get_graph():
    """Get singleton instance of graph

    Returns:
        Compiled workflow graph
    """
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = create_workflow()
    return _graph_instance


def reset_graph():
    """Reset singleton instance (for testing)"""
    global _graph_instance
    _graph_instance = None

