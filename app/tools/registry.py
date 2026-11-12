from dataclasses import dataclass

@dataclass(frozen=True)
class ToolPolicy:
    name: str
    allowed_agents: frozenset[str]
    required_scope: str | None = None
    risk: str = "low"

POLICIES = {
    "rag": ToolPolicy("rag", frozenset({"qa", "learning", "research"}), "rag:query"),
    "canvas": ToolPolicy("canvas", frozenset({"learning", "quiz"}), "canvas:read", "private-data"),
    "tavily": ToolPolicy("tavily", frozenset({"qa", "learning", "research"})),
    "youtube": ToolPolicy("youtube", frozenset({"learning"})),
    "arxiv": ToolPolicy("arxiv", frozenset({"learning", "research"})),
    "sandbox": ToolPolicy("sandbox", frozenset({"research"}), "sandbox:execute", "high"),
}

def authorize(tool: str, agent: str, scopes: list[str]) -> None:
    p = POLICIES[tool]
    if agent not in p.allowed_agents:
        raise PermissionError(f"Agent {agent} cannot use {tool}")
    if p.required_scope and p.required_scope not in scopes:
        raise PermissionError(f"Missing scope: {p.required_scope}")
