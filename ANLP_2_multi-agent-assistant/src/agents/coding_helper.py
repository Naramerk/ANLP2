# Coding Helper Agent - helps with code
import re
from src.config import llm
from src.models import AgentState
from src.tools.code_tools import (
    validate_python_syntax, 
    suggest_improvements, 
    extract_function_signature,
    count_complexity
)
from langchain_core.messages import HumanMessage, SystemMessage

CODING_PROMPT = """You are Coding Helper - programming expert in multi-agent system.

## Your specialization:

1. **Python development**:
   - Syntax and best practices
   - Standard library
   - Popular frameworks (FastAPI, Django, Flask)

2. **Code analysis**:
   - Code review
   - Error detection and fixing
   - Optimization and refactoring

3. **Examples and templates**:
   - Design patterns
   - Ready-made solutions for typical tasks
   - Examples with explanations

## Response Format:

- Always show code in ```python blocks
- Explain logic and solutions
- Point out potential problems
- Suggest improvements when appropriate

## Code analysis results:

{analysis_context}
"""


def coding_helper_node(state: AgentState) -> AgentState:
    """Coding Helper node - processes code questions

    Args:
        state: Current agent system state

    Returns:
        Updated state with coding helper answer
    """
    user_input = state['user_input']

    # Extract code from query (support for different formats)
    code_blocks = re.findall(r'```(?:python)?\s*(.*?)```', user_input, re.DOTALL)

    # Also search for code without blocks (simple one-liners)
    if not code_blocks:
        # Search for lines that look like Python code
        potential_code = re.findall(r'(def\s+\w+.*?:|class\s+\w+.*?:|import\s+\w+|from\s+\w+\s+import)', user_input)
        if potential_code:
            code_blocks = [user_input]
    
    analysis_results = []
    
    for i, code in enumerate(code_blocks):
        code = code.strip()
        if not code:
            continue

        # Syntax check
        syntax_check = validate_python_syntax(code)

        # Improvement suggestions
        improvements = suggest_improvements(code)

        # Function signature (if exists)
        signature = extract_function_signature(code)

        # Complexity metrics
        complexity = count_complexity(code)
        
        result = {
            "code_block": i + 1,
            "syntax_valid": syntax_check['valid'],
            "syntax_error": syntax_check.get('error'),
            "error_line": syntax_check.get('line'),
            "function_signature": signature if signature != "Function signature not found" else None,
            "improvements": improvements,
            "complexity": complexity
        }
        analysis_results.append(result)
        
        # Log tool calls
        state['tool_calls_log'].append({
            "agent": "coding_helper",
            "tool": "validate_python_syntax",
            "code_block": i + 1,
            "valid": syntax_check['valid']
        })

        if improvements:
            state['tool_calls_log'].append({
                "agent": "coding_helper",
                "tool": "suggest_improvements",
                "code_block": i + 1,
                "suggestions_count": len(improvements)
            })

    # Form analysis context
    if analysis_results:
        analysis_lines = ["Automatic code analysis results:"]
        for result in analysis_results:
            analysis_lines.append(f"\n**Code block #{result['code_block']}:**")
            if result['syntax_valid']:
                analysis_lines.append("  ✅ Syntax is correct")
            else:
                analysis_lines.append(f"  ❌ Syntax error: {result['syntax_error']}")
                if result['error_line']:
                    analysis_lines.append(f"     Line: {result['error_line']}")
            
            if result['function_signature']:
                analysis_lines.append(f"  📝 Signature: {result['function_signature']}")
            
            if result['improvements']:
                analysis_lines.append("  💡 Suggestions:")
                for imp in result['improvements']:
                    analysis_lines.append(f"     - {imp}")
            
            if 'complexity_score' in result.get('complexity', {}):
                analysis_lines.append(f"  📊 Complexity: {result['complexity']['complexity_score']}")
        
        analysis_context = "\n".join(analysis_lines)
    else:
        analysis_context = "No code found for analysis in the query."
    
    # Create prompt with context
    prompt_with_context = CODING_PROMPT.format(analysis_context=analysis_context)
    
    messages = [
        SystemMessage(content=prompt_with_context),
        HumanMessage(content=f"Answer the Question: {user_input}")
    ]
    
    response = llm.invoke(messages)
    
    # Save Answer
    state['intermediate_responses']['coding_helper'] = response.content
    
    return state

