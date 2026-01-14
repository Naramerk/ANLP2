#!/usr/bin/env python3
"""
Demo Script for Multi-Agent Research & Coding Assistant

Running full Demo pipeline with 5 test queries.
Shows work of all agents and tools.
"""

import sys
import os
import time
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import run_query
from src.tools.memory_manager import MemoryManager


def print_separator(title: str = "", length: int = 80) -> None:
    """Print beautiful separator"""
    if title:
        print(f"\n{'='*length}")
        print(f"{' '*((length-len(title))//2)}{title}")
        print(f"{'='*length}\n")
    else:
        print(f"\n{'-'*length}\n")


def print_result(result: Dict[str, Any], show_intermediate: bool = False) -> None:
    """Beautiful output of query result"""
    print(f"Question: {result['question'][:80]}{'...' if len(result['question']) > 80 else ''}")
    print(f"Classification: {result['classification']}")
    print(f"Agents: {', '.join(result['agents_involved'])}")
    print(f"Tool calls: {len(result['tool_calls'])}")

    if show_intermediate and result.get('intermediate_responses'):
        print(f"\n Intermediate responses:")
        for agent, response in result['intermediate_responses'].items():
            agent_display = {
                'research_specialist': 'Research Specialist',
                'coding_helper': 'Coding Helper',
                'planner': 'Planning Agent',
                'supervisor': 'Supervisor'
            }.get(agent, agent)
            print(f"\n--- {agent_display} ---")
            print(response[:200] + "..." if len(response) > 200 else response)

    print(f"\n Final Answer:")
    print(result['final_answer'])

    if result.get('tool_calls'):
        print(f"\n🔧 Tools used:")
        for call in result['tool_calls']:
            print(f"   - {call.get('agent', 'unknown')}: {call.get('tool', 'unknown')}")


def test_queries() -> list:
    """Test queries for Demo"""
    return [
        {
            "query": "What are the main patterns of multi-agent systems and how do they differ?",
            "expected_category": "research",
            "description": "Theoretical question about MAS"
        },
        {
            "query": """Check this code and suggest improvements:

```python
def process_data(data):
    result = []
    for item in data:
        if item > 10:
            print(item)
            result.append(item * 2)
    return result
```""",
            "expected_category": "coding",
            "description": "Code analysis"
        },
        {
            "query": "Help plan REST API development from scratch. What are the main stages?",
            "expected_category": "planning",
            "description": "Project planning"
        },
        {
            "query": "What is prompt engineering and what are the main techniques?",
            "expected_category": "research",
            "description": "Question about LLM"
        },
        {
            "query": "Write an async function for HTTP requests with retry logic in Python",
            "expected_category": "coding",
            "description": "Code writing"
        }
    ]


def run_demo() -> None:
    """Run full Demo"""
    print_separator("Multi-Agent Assistant Demo", 80)

    # Memory initialization
    session_id = f"demo_{int(time.time())}"
    memory = MemoryManager(session_id)

    print(f"Session ID: {session_id}")
    print("Memory initialization...")
    print("Setup complete!\n")

    # Get test queries
    queries = test_queries()
    results = []

    # Run tests
    for i, test_case in enumerate(queries, 1):
        print_separator(f"Test {i}: {test_case['description']}", 60)

        try:
            # Run query
            print(f"Processing query...")
            result = run_query(test_case['query'], session_id=session_id, verbose=False)

            # Output result
            print_result(result, show_intermediate=False)
            results.append(result)

            # Check classification
            expected = test_case['expected_category']
            actual = result['classification']
            status = "Success" if actual == expected else "Failure"
            print(f"\n{status} Expected: {expected}, Got: {actual}")

            # Small pause between queries
            time.sleep(0.5)

        except Exception as e:
            print(f"Error in test {i}: {e}")
            print(f"Query: {test_case['query'][:100]}...")
            results.append({"error": str(e)})

    # Results analysis
    print_separator("RESULTS ANALYSIS", 60)

    successful_tests = [r for r in results if 'error' not in r]
    failed_tests = [r for r in results if 'error' in r]

    print(f"Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"Failed tests: {len(failed_tests)}")

    if successful_tests:
        # Statistics by categories
        categories = {}
        total_tools = 0
        for r in successful_tests:
            cat = r['classification']
            categories[cat] = categories.get(cat, 0) + 1
            total_tools += len(r.get('tool_calls', []))

        print("\nStatistics by categories:")
        for cat, count in categories.items():
            print(f"   {cat}: {count} tests")

        print(f"\nTotal tool calls: {total_tools}")
        print(f"   Average per test: {total_tools / len(successful_tests):.1f}")
        # Session history 
        print_separator("SESSION HISTORY", 40)
        # Create new MemoryManager to load latest data from file
        memory_updated = MemoryManager(session_id)
        history = memory_updated.retrieve_history(last_n=10)
        if history and history != "Query history is empty":
            print(history)
        else:
            print("History is empty")

        # Session summary
        summary = memory_updated.get_session_summary()
        print("\nSession summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")

    if failed_tests:
        print_separator("ERRORS", 40)
        for i, error in enumerate(failed_tests, 1):
            print(f"{i}. {error['error']}")

    print_separator("🎉 DEMO COMPLETED!", 60)


def main():
    """Main function"""
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nCritical error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
