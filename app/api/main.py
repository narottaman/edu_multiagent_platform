from fastapi import FastAPI, Header
from app.graphs.supervisor import graph
from app.models.schemas import ChatRequest, ChatResponse, UserContext

app = FastAPI(title="Edu Multi-Agent Platform", version="0.1.0")

@app.get("/healthz")
async def healthz(): return {"status":"ok"}

@app.get("/readyz")
async def readyz(): return {"status":"ready"}

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, x_user_id: str | None = Header(default=None), x_scopes: str | None = Header(default=None)):
    scopes = x_scopes.split(",") if x_scopes else ["rag:query","canvas:read","quiz:attempt"]
    user = UserContext(user_id=x_user_id or "dev-user", scopes=scopes, course_ids=[req.course_id] if req.course_id else [])
    out = await graph.ainvoke({"query":req.message,"intent":req.intent,"course_id":req.course_id,"user":user})
    result = out["result"]
    return ChatResponse(intent=out["intent"], answer=result.answer, agent_results=[result])
