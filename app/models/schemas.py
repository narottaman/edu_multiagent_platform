from typing import Any, Literal
from pydantic import BaseModel, Field

Intent = Literal["qa", "learn", "quiz", "research"]

class UserContext(BaseModel):
    user_id: str = "dev-user"
    role: str = "student"
    course_ids: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=lambda: ["rag:query", "canvas:read", "quiz:attempt"])

class ChatRequest(BaseModel):
    message: str
    intent: Intent | None = None
    course_id: str | None = None
    session_id: str = "default"

class Evidence(BaseModel):
    source: str
    title: str = ""
    content: str
    url: str | None = None
    citation: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class AgentResult(BaseModel):
    agent: str
    answer: str
    evidence: list[Evidence] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    intent: Intent
    answer: str
    agent_results: list[AgentResult] = Field(default_factory=list)
