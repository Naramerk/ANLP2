# Multi-Agent Research & Coding Assistant

Multi-agent system for research, coding, and planning using LangChain + LangGraph.

## Features

- Router Agent for intelligent query classification
- Research Specialist for theoretical questions
- Coding Helper for code analysis and best practices
- Planning Agent for task decomposition
- Supervisor for answer synthesis
- Session memory and tool calling

## Quick Start

1. Install: `pip install -r requirements.txt`
2. Configure `.env` with LLM credentials
3. Run: `python -m src.main "Your query"`

## Architecture

User Query → Router → Specialist(s) → Supervisor → Final Answer

See [ARCHITECTURE.md](src/ARCHITECTURE.md) for details.

## Testing

Results in [evaluation/test_queries.md](evaluation/test_queries.md)

## Reflection

Analysis in [REFLECTION.md](REFLECTION.md)

