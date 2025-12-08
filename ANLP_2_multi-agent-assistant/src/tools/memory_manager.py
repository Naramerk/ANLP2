# Session memory management
from datetime import datetime
from typing import Optional, Any
import json
import os

from src.models import SessionMemory, Query

MEMORY_FILE = "session_memory.json"


class MemoryManager:
    """Session memory manager for multi-agent system"""

    def __init__(self, session_id: str = "default"):
        """Initialize memory manager

        Args:
            session_id: Session identifier
        """
        self.session_id = session_id
        self.memory = self._load_memory()

    def _load_memory(self) -> SessionMemory:
        """Load memory from file or create new

        Returns:
            SessionMemory object
        """
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return SessionMemory(**data)
            except (json.JSONDecodeError, Exception):
                return SessionMemory(session_id=self.session_id)
        return SessionMemory(session_id=self.session_id)

    def add_query(self, query_text: str, agent_route: Optional[str] = None) -> Query:
        """Add query to history

        Args:
            query_text: Query text
            agent_route: Agent that processed the query

        Returns:
            Created Query object
        """
        query = Query(
            text=query_text,
            timestamp=datetime.now().isoformat(),
            agent_route=agent_route
        )
        self.memory.queries.append(query)
        self._save_memory()
        return query
    
    def add_note(self, note: str) -> None:
        """Add note to memory

        Args:
            note: Note text
        """
        self.memory.notes.append(note)
        self._save_memory()

    def retrieve_history(self, last_n: int = 5) -> str:
        """Get last N queries

        Args:
            last_n: Number of last queries

        Returns:
            Formatted line with query history
        """
        recent = self.memory.queries[-last_n:]
        if not recent:
            return "Query history is empty"
        return "\n".join([f"- [{q.timestamp}] ({q.agent_route or 'unknown'}): {q.text}" for q in recent])

    def get_session_summary(self) -> dict:
        """Get session summary

        Returns:
            Dictionary with session information
        """
        agent_counts = {}
        for q in self.memory.queries:
            route = q.agent_route or "unknown"
            agent_counts[route] = agent_counts.get(route, 0) + 1
        
        return {
            "session_id": self.memory.session_id,
            "total_queries": len(self.memory.queries),
            "total_notes": len(self.memory.notes),
            "queries_by_agent": agent_counts,
            "has_user_profile": bool(self.memory.user_profile)
        }
    
    def update_user_profile(self, key: str, value: any) -> None:
        """Update user profile

        Args:
            key: Profile key
            value: Value
        """
        self.memory.user_profile[key] = value
        self._save_memory()

    def clear_history(self) -> None:
        """Clear query history"""
        self.memory.queries = []
        self._save_memory()

    def _save_memory(self) -> None:
        """Save memory to file"""
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.memory.model_dump(), f, indent=2, ensure_ascii=False)

    def get_context_for_agent(self, agent_name: str, max_items: int = 3) -> str:
        """Get relevant context for agent

        Args:
            agent_name: Agent name
            max_items: Maximum context items

        Returns:
            Context for agent
        """
        # Get queries processed by this agent
        agent_queries = [q for q in self.memory.queries if q.agent_route == agent_name]
        recent = agent_queries[-max_items:] if agent_queries else []

        if not recent:
            return f"First interaction with agent {agent_name}"

        context_lines = [f"Previous queries to {agent_name}:"]
        for q in recent:
            context_lines.append(f"  - {q.text}")

        return "\n".join(context_lines)

