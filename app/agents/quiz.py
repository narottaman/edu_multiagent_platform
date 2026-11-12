from app.core.llm import generate
from app.models.schemas import AgentResult, UserContext
from app.tools.clients import canvas_search
from app.tools.registry import authorize
from .common import evidence_text

async def run(query: str, user: UserContext, course_id: str | None = None) -> AgentResult:
    authorize("canvas", "quiz", user.scopes)
    evidence = await canvas_search(query, course_id)
    prompt = f"Create a rigorous quiz using ONLY the Canvas evidence below. Do not use outside facts. Include answers and brief rationales after a separator. If evidence is insufficient, say so instead of inventing questions.\nRequest: {query}\nCanvas evidence:\n{evidence_text(evidence)}"
    return AgentResult(agent="quiz", answer=await generate(prompt), evidence=evidence, metadata={"source_policy":"canvas-only"})
