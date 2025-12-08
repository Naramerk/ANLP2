# Supervisor Agent - coordinates and synthesizes responses
from src.config import llm
from src.models import AgentState
from langchain_core.messages import HumanMessage, SystemMessage

SUPERVISOR_PROMPT = """You are Supervisor - coordinator of the multi-agent system.

## Your role:

1. **Response synthesis**:
   - Combine contributions from specialized agents
   - Eliminate contradictions and repetitions
   - Create a coherent final Answer

2. **Quality control**:
   - Check answer completeness
   - Ensure information relevance
   - Add missing details

3. **Formatting**:
   - Structure the final Answer
   - Highlight key points
   - Make Answer understandable to the user

## Synthesis rules:

- If Answer from one agent - improve its structure and completeness
- If responses from multiple agents - combine them, removing duplication
- If there are contradictions - give priority to the more specialized agent
- Add a brief summary at the end for long answers

## Original User query:

{user_query}

## Agent responses:

{agent_responses}
"""

SUPERVISOR_DIRECT_PROMPT = """You are Supervisor - coordinator of the multi-agent system.

You have been directly asked a general question. Answer it briefly and to the point.

If the question requires specialized knowledge (research, coding, planning),
indicate that this question should be addressed to the appropriate specialist.

Query: {user_query}
"""


def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor node - synthesizes final answer

    Args:
        state: Current agent system state

    Returns:
        Updated state with final answer
    """
    user_input = state['user_input']
    intermediate_responses = state['intermediate_responses']
    
    # Check if there are responses from other agents
    if intermediate_responses:
        # Form summary of agent responses
        responses_parts = []
        for agent, response in intermediate_responses.items():
            agent_display = {
                'research_specialist': 'Research Specialist',
                'coding_helper': 'Coding Helper',
                'planner': 'Planning Agent'
            }.get(agent, agent)

            responses_parts.append(f"### {agent_display}:\n{response}")

        responses_summary = "\n\n---\n\n".join(responses_parts)

        # Create prompt for synthesis
        prompt = SUPERVISOR_PROMPT.format(
            user_query=user_input,
            agent_responses=responses_summary
        )
    else:
        # Direct question to supervisor (general classification)
        prompt = SUPERVISOR_DIRECT_PROMPT.format(user_query=user_input)
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content="Form the final Answer for the user.")
    ]

    response = llm.invoke(messages)

    # Save the final Answer
    state['final_answer'] = response.content

    # Also save in intermediate for completeness
    state['intermediate_responses']['supervisor'] = response.content
    
    return state

