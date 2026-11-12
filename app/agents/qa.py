from app.core.llm import generate
from app.models.schemas import AgentResult, UserContext
from app.tools.clients import rag_search, tavily_search
from app.tools.registry import authorize
from .common import evidence_text

async def run(query: str, user: UserContext, course_id: str | None = None) -> AgentResult:
    authorize("rag", "qa", user.scopes)
    evidence = await rag_search(query)
    if len(evidence) < 2:
        authorize("tavily", "qa", user.scopes)
        evidence += await tavily_search(query)
    prompt = f"Answer the student's question using only the evidence below. Cite evidence numbers and state uncertainty.\nQuestion: {query}\nEvidence:\n{evidence_text(evidence)}"
    return AgentResult(agent="qa", answer=await generate(prompt), evidence=evidence)
