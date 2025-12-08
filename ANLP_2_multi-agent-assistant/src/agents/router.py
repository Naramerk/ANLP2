# Router Agent - classifies and routes queries
import json
import re
from src.config import llm
from src.models import AgentState
from langchain_core.messages import HumanMessage, SystemMessage

ROUTER_PROMPT = """You are Router Agent in multi-agent system. Your only task is to classify user query and select appropriate agents.

## Query Categories:

1. **research** - theoretical questions about:
   - Multi-agent systems (MAS)
   - LLM, machine learning, neural networks
   - System architecture and design
   - Programming concepts

2. **coding** - practical code questions:
   - Python and other language syntax
   - Debugging and error fixing
   - Code examples and templates
   - Code review and improvements

3. **planning** - planning questions:
   - Step-by-step instructions
   - Project planning
   - Task decomposition
   - Roadmap and strategies

4. **general** - other queries:
   - General questions
   - Unclear queries
   - Combined topics

## Response Format:

Respond ONLY with valid JSON without additional text:
{"classification": "category", "agents": ["agent_name"]}

Where agent_name can be: research_specialist, coding_helper, planner, supervisor

## Examples:

Query: "What are MAS patterns?"
Answer: {"classification": "research", "agents": ["research_specialist"]}

Query: "Write a sorting function"
Answer: {"classification": "coding", "agents": ["coding_helper"]}

Query: "How to plan API development?"
Answer: {"classification": "planning", "agents": ["planner"]}
"""


def router_node(state: AgentState) -> AgentState:
    """Router node in graph - classifies query and selects agents

    Args:
        state: Current agent system state

    Returns:
        Updated state with classification and agent list
    """
    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=f"Classify this query: {state['user_input']}")
    ]

    response = llm.invoke(messages)
    response_text = response.content

    # Try to extract JSON from response
    try:
        # Search for JSON in response
        json_match = re.search(r'\{[^}]+\}', response_text)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response_text)

        classification = result.get("classification", "general")
        agents = result.get("agents", ["supervisor"])

        # Validate classification
        valid_classifications = ["research", "coding", "planning", "general"]
        if classification not in valid_classifications:
            classification = "general"

        # Validate agents
        valid_agents = ["research_specialist", "coding_helper", "planner", "supervisor"]
        agents = [a for a in agents if a in valid_agents]
        if not agents:
            agents = ["supervisor"]

        state["classification"] = classification
        state["classified_agents"] = agents

    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback on parsing error
        state["classification"] = "general"
        state["classified_agents"] = ["supervisor"]

    # Log routing
    state["metadata"]["routing_info"] = {
        "classification": state["classification"],
        "agents": state["classified_agents"],
        "raw_response": response_text[:200]  # First 200 characters for debugging
    }
    
    return state

