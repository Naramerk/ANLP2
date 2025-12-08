# Multi-Agent Research & Coding Assistant Architecture

Multi-agent system for research, coding, and planning assistance using LangChain, LangGraph, and Qwen LLM.

## Agents

### Router Agent
- **File:** `src/agents/router.py`
- **Role:** Classifies queries into: `research`, `coding`, `planning`, `general`
- **Output:** Selected agents for processing

### Research Specialist
- **File:** `src/agents/research_specialist.py`
- **Role:** Theoretical questions (ML, AI, MAS, frameworks)
- **Tools:** Knowledge base search

### Coding Helper
- **File:** `src/agents/coding_helper.py`
- **Role:** Code analysis, syntax validation, best practices
- **Tools:** Code validation and improvement suggestions

### Planning Agent
- **File:** `src/agents/planner.py`
- **Role:** Task decomposition and planning
- **Tools:** Session history access

### Supervisor Agent
- **File:** `src/agents/supervisor.py`
- **Role:** Final answer synthesis and quality control

## System Flow

```
User Query → Router → Specialist(s) → Supervisor → Final Answer
```

## Key Components

- **Memory:** Session persistence via `session_memory.json`
- **Tools:** Knowledge base, code analysis, history retrieval
- **State:** TypedDict with query flow data
- **Configuration:** Environment variables for LLM access

