import asyncio
from app.core.llm import generate
from app.models.schemas import AgentResult, UserContext
from app.tools.clients import rag_search, canvas_search, arxiv_search, youtube_search, tavily_search
from app.tools.registry import authorize
from .common import evidence_text

async def run(query: str, user: UserContext, course_id: str | None = None) -> AgentResult:
    for t in ("rag", "canvas", "arxiv", "youtube", "tavily"):
        authorize(t, "learning", user.scopes)
    batches = await asyncio.gather(rag_search(query), canvas_search(query, course_id), arxiv_search(query), youtube_search(query), tavily_search(query))
    evidence = [x for batch in batches for x in batch]
    prompt = f"You are a teaching planner. Build a prerequisite-aware ordered learning path, prioritize Canvas/internal course material, then scholarly and visual/open-web resources. Explain what to learn, why, and how to check mastery.\nTopic/request: {query}\nResources:\n{evidence_text(evidence)}"
    return AgentResult(agent="learning", answer=await generate(prompt), evidence=evidence)
