# Mini Knowledge Base with tools

KB_DATA = {
    "MAS_patterns": {
        "router": "Router agent classifies incoming queries and distributes tasks among specialized agents. It analyzes the query type (research, coding, planning) and directs to the appropriate specialist.",
        "supervisor": "Supervisor coordinates agent work, synthesizes their responses and ensures the quality of the final result. It can also reassign tasks if necessary.",
        "sequential": "Sequential workflow - Agents call each other sequentially, each adding their contribution to the overall result. This ensures gradual improvement of the answer.",
        "hierarchical": "Hierarchical pattern - multi-level agent structure with clear separation of responsibilities and control at each level.",
        "parallel": "Parallel execution - several agents work simultaneously on different aspects of the task, results are combined."
    },
    "langgraph_tips": {
        "StateDict": "TypedDict is used to define graph state. All agents work with one shared state, which ensures data consistency.",
        "nodes": "Nodes are functions that update state. Each node receives the current state and returns the updated state or part of the updates.",
        "edges": "Edges are connections between nodes. There are regular (always executed) and conditional (selection of the next node based on condition).",
        "entry_point": "Entry point - initial node of the graph. Set via workflow.set_entry_point().",
        "END": "END - special constant denoting the completion of graph execution."
    },
    "python_snippets": {
        "async_function": "async def my_func():\n    result = await some_async_operation()\n    return result",
        "type_hints": "from typing import TypedDict, List, Optional\n\nclass MyState(TypedDict):\n    data: List[str]\n    count: Optional[int]",
        "pydantic_model": "from pydantic import BaseModel\n\nclass User(BaseModel):\n    name: str\n    age: int = 0",
        "context_manager": "from contextlib import contextmanager\n\n@contextmanager\ndef managed_resource():\n    resource = acquire()\n    try:\n        yield resource\n    finally:\n        release(resource)"
    },
    "llm_concepts": {
        "prompt_engineering": "Prompt engineering - the art of composing effective prompts for LLM. Includes system instructions, examples (few-shot) and output structuring.",
        "tool_calling": "Tool calling allows LLM to call external functions to perform actions (search, calculations, API calls).",
        "chain_of_thought": "Chain of Thought (CoT) - technique where LLM reasons step by step, improving the quality of complex answers.",
        "rag": "RAG (Retrieval Augmented Generation) - pattern where LLM is supplemented with external knowledge base through retrieval."
    },
    "architecture_patterns": {
        "microservices": "Microservices architecture divides the system into independent services, each with its own responsibility.",
        "event_driven": "Event-driven architecture uses events for communication between system components.",
        "layered": "Layered architecture organizes code into layers (presentation, business logic, data access) with clear boundaries."
    }
}


def query_knowledge_base(query: str) -> str:
    """Search in knowledge base

    Args:
        query: Search query

    Returns:
        Found results or message about no data available
    """
    results = []
    query_lower = query.lower()

    # Search by keywords
    for category, items in KB_DATA.items():
        for key, value in items.items():
            if query_lower in key.lower() or query_lower in value.lower():
                results.append(f"[{category}/{key}]: {value}")
    
    return "\n\n".join(results) if results else "Information not found in KB"


def get_code_example(topic: str) -> str:
    """Get code example by topic

    Args:
        topic: Topic name for code example

    Returns:
        Code example or message about absence
    """
    return KB_DATA.get("python_snippets", {}).get(topic, "Example not found")


def get_all_topics() -> list:
    """Get list of all topics in KB

    Returns:
        List of all categories and topics
    """
    topics = []
    for category, items in KB_DATA.items():
        for key in items.keys():
            topics.append(f"{category}/{key}")
    return topics

