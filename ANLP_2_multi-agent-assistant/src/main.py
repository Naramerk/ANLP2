# Entry point - launching multi-agent system
from datetime import datetime
from typing import Optional
from src.models import AgentState, SessionMemory
from src.graph.workflow import get_graph
from src.tools.memory_manager import MemoryManager


def run_query(user_input: str, session_id: str = "default", verbose: bool = False) -> dict:
    """Main function - runs query through multi-agent system

    Args:
        user_input: User query
        session_id: Session identifier for memory
        verbose: Output detailed information about process

    Returns:
        Dictionary with query processing results
    """
    # Initialize session memory
    memory_manager = MemoryManager(session_id)
    session_memory = memory_manager.memory

    # Prepare initial state
    initial_state: AgentState = {
        "user_input": user_input,
        "classification": None,
        "classified_agents": [],
        "intermediate_responses": {},
        "memory": session_memory,
        "final_answer": "",
        "tool_calls_log": [],
        "metadata": {
            "session_id": session_id,
            "start_time": datetime.now().isoformat()
        }
    }
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"🚀 Starting query: {user_input[:50]}...")
        print(f"📍 Session ID: {session_id}")
        print(f"{'='*60}\n")

    # Get graph and run
    graph = get_graph()
    result_state = graph.invoke(initial_state)

    # Add completion time
    result_state["metadata"]["end_time"] = datetime.now().isoformat()

    # Save query to memory
    memory_manager.add_query(user_input, agent_route=result_state.get('classification'))
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"✅ Query processed")
        print(f"📊 Classification: {result_state.get('classification')}")
        print(f"🤖 Agents: {result_state.get('classified_agents')}")
        print(f"🔧 Tool calls: {len(result_state.get('tool_calls_log', []))}")
        print(f"{'='*60}\n")

    # Form result
    return {
        "question": user_input,
        "classification": result_state.get('classification'),
        "agents_involved": result_state.get('classified_agents', []),
        "intermediate_responses": result_state.get('intermediate_responses', {}),
        "final_answer": result_state.get('final_answer', ''),
        "tool_calls": result_state.get('tool_calls_log', []),
        "session_id": session_id,
        "metadata": result_state.get('metadata', {})
    }


def interactive_mode():
    """Launch interactive mode for testing"""
    print("\n" + "="*60)
    print("🤖 Multi-Agent Research & Coding Assistant")
    print("="*60)
    print("Enter query or 'exit' to quit")
    print("Commands: 'history' - show history, 'clear' - clear\n")
    
    session_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    memory_manager = MemoryManager(session_id)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'exit':
                print("\n👋 Goodbye!")
                break

            if user_input.lower() == 'history':
                history = memory_manager.retrieve_history(last_n=10)
                print(f"\n📜 History:\n{history}")
                continue

            if user_input.lower() == 'clear':
                memory_manager.clear_history()
                print("🗑️ History cleared")
                continue

            # Process query
            result = run_query(user_input, session_id=session_id, verbose=True)
            
            print(f"\n{'─'*60}")
            print(f"📋 Classification: {result['classification']}")
            print(f"🤖 Agents: {', '.join(result['agents_involved'])}")
            print(f"{'─'*60}")
            print(f"\n📝 Answer:\n{result['final_answer']}")

            if result['tool_calls']:
                print(f"\n🔧 Tools used ({len(result['tool_calls'])}):")
                for call in result['tool_calls']:
                    print(f"   - {call.get('agent', 'unknown')}: {call.get('tool', 'unknown')}")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def demo_queries():
    """Launch demonstration queries"""
    demo_inputs = [
        "What are the main patterns of multi-agent systems?",
        "Write a function to sort a list in descending order",
        "Help plan REST API development from scratch",
    ]

    print("\n" + "="*60)
    print("🎯 Multi-Agent Assistant Demonstration")
    print("="*60)

    for i, query in enumerate(demo_inputs, 1):
        print(f"\n\n{'='*60}")
        print(f"📌 Demo #{i}: {query}")
        print("="*60)

        result = run_query(query, session_id="demo", verbose=True)

        print(f"\n📝 Answer:\n{result['final_answer'][:500]}...")
        print(f"\n✅ Classification: {result['classification']}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            demo_queries()
        elif sys.argv[1] == "--interactive":
            interactive_mode()
        else:
            # Single query from command line
            query = " ".join(sys.argv[1:])
            result = run_query(query, verbose=True)
            print(f"\n📝 Answer:\n{result['final_answer']}")
    else:
        # Default - usage example
        result = run_query("What are the main patterns of multi-agent systems?")

        print("\n" + "="*80)
        print("QUERY RESULT")
        print("="*80)
        print(f"Question: {result['question']}")
        print(f"Classification: {result['classification']}")
        print(f"Agents involved: {result['agents_involved']}")
        print(f"\nFinal answer:\n{result['final_answer']}")
        print(f"\nTool calls: {len(result['tool_calls'])}")
        for call in result['tool_calls']:
            print(f"  - {call}")

