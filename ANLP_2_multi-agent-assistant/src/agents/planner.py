# Planning Agent - helps with planning
from src.config import llm
from src.models import AgentState, SessionMemory
from langchain_core.messages import HumanMessage, SystemMessage

PLANNER_PROMPT = """You are Planning Agent - planning expert and task decomposition.

## Your specialization:

1. **Task decomposition**:
   - Breaking down complex tasks into simple steps
   - Determining dependencies between tasks
   - Estimating complexity and time

2. **Project planning**:
   - Creating roadmap
   - Defining milestones
   - Task prioritization

3. **Strategic thinking**:
   - Risk analysis
   - Alternative approaches
   - Success criteria

## Response Format:

Structure the plan as follows:

### 🎯 Goal Understanding
[Brief description of what needs to be achieved]

### 📋 Action Plan
1. **Step 1**: [Description]
   - Success criterion: [How to know the step is completed]
   - Time estimate: [Approximate time]

2. **Step 2**: [Description]
   ...

### ⚠️ Risks and Recommendations
[Potential problems and how to avoid them]

### ✅ Completion Criteria
[How to know the entire task is completed]

## Context of previous queries:

{history_context}
"""


def _retrieve_history_from_memory(memory: SessionMemory, last_n: int = 5) -> str:
    """Get last N queries from SessionMemory

    Args:
        memory: SessionMemory object
        last_n: Number of last queries

    Returns:
        Formatted string with query history
    """
    recent = memory.queries[-last_n:] if memory.queries else []
    if not recent:
        return "Query history is empty"
    return "\n".join([f"- [{q.timestamp}] ({q.agent_route or 'unknown'}): {q.text}" for q in recent])


def _get_context_for_agent_from_memory(memory: SessionMemory, agent_name: str, max_items: int = 3) -> str:
    """Get relevant context for agent from SessionMemory

    Args:
        memory: SessionMemory object
        agent_name: Agent name
        max_items: Maximum context items

    Returns:
        Context for agent
    """
    # Get queries processed by this agent
    agent_queries = [q for q in memory.queries if q.agent_route == agent_name]
    recent = agent_queries[-max_items:] if agent_queries else []

    if not recent:
        return f"First interaction with agent {agent_name}"

    context_lines = [f"Previous queries to {agent_name}:"]
    for q in recent:
        context_lines.append(f"  - {q.text}")

    return "\n".join(context_lines)


def planner_node(state: AgentState) -> AgentState:
    """Planning Agent node - creates plans and decomposes tasks

    Args:
        state: Current agent system state

    Returns:
        Updated state with plan
    """
    user_input = state['user_input']
    
    memory = state.get('memory')
    if memory is None:
        from src.models import SessionMemory
        memory = SessionMemory(session_id=state.get('metadata', {}).get('session_id', 'default'))

    # Get history from state memory
    history = _retrieve_history_from_memory(memory, last_n=3)

    # Also get context specific to planner
    agent_context = _get_context_for_agent_from_memory(memory, 'planner', max_items=2)

    # Form history context
    if history and history != "Query history is empty":
        history_context = f"Recent queries history:\n{history}\n\nPlanning context:\n{agent_context}"
    else:
        history_context = "This is the first query in the session. No history."
    
    # Create prompt with context
    prompt_with_context = PLANNER_PROMPT.format(history_context=history_context)
    
    messages = [
        SystemMessage(content=prompt_with_context),
        HumanMessage(content=f"Create a plan for: {user_input}")
    ]
    
    response = llm.invoke(messages)
    
    # Save Answer
    state['intermediate_responses']['planner'] = response.content
    
    # Log tool calls
    state['tool_calls_log'].append({
        "agent": "planner",
        "tool": "memory.retrieve_history",
        "retrieved_items": 3,
        "history_available": history != "Query history is empty"
    })
    
    state['tool_calls_log'].append({
        "agent": "planner",
        "tool": "memory.get_context_for_agent",
        "agent_name": "planner"
    })
    
    
    return state

