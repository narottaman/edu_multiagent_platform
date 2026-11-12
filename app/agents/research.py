import asyncio
from app.core.llm import generate
from app.models.schemas import AgentResult, UserContext
from app.tools.clients import rag_search, arxiv_search, tavily_search
from app.tools.registry import authorize
from .common import evidence_text

async def run(query: str, user: UserContext, course_id: str | None = None) -> AgentResult:
    for t in ("rag", "arxiv", "tavily"):
        authorize(t, "research", user.scopes)
    batches = await asyncio.gather(rag_search(query, "deep"), arxiv_search(query), tavily_search(query))
    evidence = [x for batch in batches for x in batch]
    prompt = f"Act as a research literature analyst and critic. Propose 3 candidate project ideas tied to the student's topic. For each: evidence-supported gap, why it may be a gap (never claim exhaustive novelty), course connection, experiment, datasets/metrics if evidenced, feasibility, risks, and papers to verify. Explicitly label unsupported assumptions.\nTopic: {query}\nEvidence:\n{evidence_text(evidence, 18)}"
    return AgentResult(agent="research", answer=await generate(prompt, research=True), evidence=evidence)
