# Planning Agent - helps with planning
from src.config import llm
from src.models import AgentState
from src.tools.memory_manager import MemoryManager
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


def planner_node(state: AgentState) -> AgentState:
    """Planning Agent node - creates plans and decomposes tasks

    Args:
        state: Current agent system state

    Returns:
        Updated state with plan
    """
    user_input = state['user_input']

    # Get history from memory
    memory_manager = MemoryManager()
    history = memory_manager.retrieve_history(last_n=3)

    # Also get context specific to planner
    agent_context = memory_manager.get_context_for_agent('planner', max_items=2)

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
        "tool": "memory_manager.retrieve_history",
        "retrieved_items": 3,
        "history_available": history != "Query history is empty"
    })
    
    state['tool_calls_log'].append({
        "agent": "planner",
        "tool": "memory_manager.get_context_for_agent",
        "agent_name": "planner"
    })
    
    # Save query to memory for future sessions
    memory_manager.add_query(user_input, agent_route='planner')
    
    return state

