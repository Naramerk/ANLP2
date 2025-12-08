# Research Specialist Agent - answers theoretical questions
from src.config import llm
from src.models import AgentState
from src.tools.knowledge_base import query_knowledge_base
from langchain_core.messages import HumanMessage, SystemMessage

RESEARCH_PROMPT = """You are Research Specialist - expert on theoretical questions in multi-agent system.

## Your specialization:

1. **Machine learning and AI**:
   - Neural network architectures
   - Training and optimization methods
   - LLM and their applications

2. **Multi-agent systems (MAS)**:
   - MAS design patterns
   - Agent coordination and communication
   - LangChain, LangGraph and similar frameworks

3. **Software system architecture**:
   - Design patterns
   - Microservices and distributed systems
   - Best practices and anti-patterns

## Response Format:

- Provide structured answers with headers
- Use examples to illustrate concepts
- Indicate knowledge sources when relevant
- Be precise and academic, but understandable

## Context from Knowledge Base:

{kb_context}
"""


def research_specialist_node(state: AgentState) -> AgentState:
    """Research Specialist node - processes theoretical queries

    Args:
        state: Current agent system state

    Returns:
        Updated state with research specialist answer
    """
    user_input = state['user_input']

    # Search in Knowledge Base
    kb_result = query_knowledge_base(user_input)
    kb_found = kb_result != "Information not found in KB"

    # Form context from KB
    if kb_found:
        kb_context = f"Found in knowledge base:\n{kb_result}"
    else:
        kb_context = "No direct matches in knowledge base. Use your knowledge."
    
    # Create prompt with context
    prompt_with_context = RESEARCH_PROMPT.format(kb_context=kb_context)

    messages = [
        SystemMessage(content=prompt_with_context),
        HumanMessage(content=f"Answer the question: {user_input}")
    ]

    response = llm.invoke(messages)

    # Save Answer in intermediate_responses
    state['intermediate_responses']['research_specialist'] = response.content
    
    # Log tool call
    state['tool_calls_log'].append({
        "agent": "research_specialist",
        "tool": "knowledge_base.query",
        "input": user_input,
        "result_found": kb_found,
        "kb_result_preview": kb_result[:100] if kb_found else None
    })
    
    return state

