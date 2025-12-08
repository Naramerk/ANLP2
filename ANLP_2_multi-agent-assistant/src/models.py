# State definition for LangGraph
from typing import TypedDict, List, Optional, Any
from pydantic import BaseModel


class Query(BaseModel):
    """User query model"""
    text: str
    timestamp: str
    agent_route: Optional[str] = None


class SessionMemory(BaseModel):
    """Session memory"""
    session_id: str
    queries: List[Query] = []
    user_profile: dict = {}
    notes: List[str] = []


class AgentState(TypedDict):
    """Shared state for all agents in LangGraph"""
    user_input: str
    classification: Optional[str]  # research|coding|planning|general
    classified_agents: List[str]
    intermediate_responses: dict  # {agent_name: response}
    memory: Any  # SessionMemory (use Any for TypedDict compatibility)
    final_answer: str
    tool_calls_log: List[dict]
    metadata: dict  # timestamps, routing info, etc.

