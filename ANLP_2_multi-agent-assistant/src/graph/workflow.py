# LangGraph definition - entire multi-agent system workflow
from langgraph.graph import StateGraph, END
from src.models import AgentState
from src.agents.router import router_node
from src.agents.research_specialist import research_specialist_node
from src.agents.coding_helper import coding_helper_node
from src.agents.planner import planner_node
from src.agents.supervisor import supervisor_node


def route_after_classification(state: AgentState) -> str:
    """Determines next node based on classification - routes to first agent

    Args:
        state: Current state with classification results

    Returns:
        Name of next node to execute
    """
    classified_agents = state.get('classified_agents', [])

    if not classified_agents:
        return "supervisor"

    # Get first agent to execute
    first_agent = classified_agents[0]

    # Mapping to node names
    agent_to_node = {
        "research_specialist": "research_specialist",
        "coding_helper": "coding_helper",
        "planner": "planner",
        "supervisor": "supervisor"
    }

    return agent_to_node.get(first_agent, "supervisor")


def route_to_next_agent(state: AgentState) -> str:
    """Routes to next unexecuted agent or supervisor if all agents executed

    Args:
        state: Current agent system state

    Returns:
        Name of next node to execute
    """
    classified_agents = state.get('classified_agents', [])
    intermediate_responses = state.get('intermediate_responses', {})
    
    # Agent-to-node mapping
    agent_to_node = {
        "research_specialist": "research_specialist",
        "coding_helper": "coding_helper",
        "planner": "planner",
        "supervisor": "supervisor"
    }

    # Find first agent that hasn't been executed yet (no response in intermediate_responses)
    for agent in classified_agents:
        if agent not in intermediate_responses and agent in agent_to_node:
            return agent_to_node[agent]

    # All agents executed (all have responses), route to supervisor
    return "supervisor"


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

    # After each specialized agent -> route to next agent or supervisor
    workflow.add_conditional_edges(
        "research_specialist",
        route_to_next_agent,
        {
            "research_specialist": "research_specialist",
            "coding_helper": "coding_helper",
            "planner": "planner",
            "supervisor": "supervisor"
        }
    )
    workflow.add_conditional_edges(
        "coding_helper",
        route_to_next_agent,
        {
            "research_specialist": "research_specialist",
            "coding_helper": "coding_helper",
            "planner": "planner",
            "supervisor": "supervisor"
        }
    )
    workflow.add_conditional_edges(
        "planner",
        route_to_next_agent,
        {
            "research_specialist": "research_specialist",
            "coding_helper": "coding_helper",
            "planner": "planner",
            "supervisor": "supervisor"
        }
    )

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

