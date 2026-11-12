import httpx
from urllib.parse import quote_plus
from app.core.config import get_settings
from app.models.schemas import Evidence

async def rag_search(query: str, mode: str = "auto") -> list[Evidence]:
    s = get_settings()
    if s.mock_mode:
        return [Evidence(source="rag", title="Mock internal corpus", content=f"Internal evidence for: {query}", citation="mock:rag:1")]
    headers = {"Authorization": f"Bearer {s.rag_service_api_key}"} if s.rag_service_api_key else {}
    async with httpx.AsyncClient(timeout=s.request_timeout_seconds) as c:
        r = await c.post(f"{s.rag_service_url}/retrieve", json={"query": query, "mode": mode}, headers=headers)
        r.raise_for_status()
        return [Evidence(**x) for x in r.json().get("evidence", [])]

async def canvas_search(query: str, course_id: str | None) -> list[Evidence]:
    s = get_settings()
    if not course_id:
        return []
    if s.allowed_courses and course_id not in s.allowed_courses:
        raise PermissionError("Course is outside configured Canvas allow-list")
    if s.mock_mode:
        return [Evidence(source="canvas", title=f"Course {course_id}", content=f"Canvas-only material relevant to: {query}", citation="mock:canvas:1")]
    if not s.canvas_base_url or not s.canvas_access_token:
        return []
    headers = {"Authorization": f"Bearer {s.canvas_access_token}"}
    # Canvas search APIs differ by object type; production adapters should search modules/pages/files.
    async with httpx.AsyncClient(timeout=s.request_timeout_seconds, headers=headers) as c:
        r = await c.get(f"{s.canvas_base_url.rstrip('/')}/api/v1/courses/{course_id}/modules", params={"per_page": 100})
        r.raise_for_status()
        return [Evidence(source="canvas", title=m.get("name", "Module"), content=m.get("name", ""), metadata=m) for m in r.json() if query.lower() in m.get("name", "").lower()]

async def tavily_search(query: str) -> list[Evidence]:
    s = get_settings()
    if s.mock_mode or not s.tavily_api_key:
        return []
    async with httpx.AsyncClient(timeout=s.request_timeout_seconds) as c:
        r = await c.post("https://api.tavily.com/search", json={"api_key": s.tavily_api_key, "query": query, "max_results": 5})
        r.raise_for_status()
        return [Evidence(source="tavily", title=x.get("title", ""), content=x.get("content", ""), url=x.get("url")) for x in r.json().get("results", [])]

async def arxiv_search(query: str) -> list[Evidence]:
    s = get_settings()
    if s.mock_mode:
        return [Evidence(source="arxiv", title="Mock paper", content=f"Paper abstract about {query}", url="https://arxiv.org/")]
    async with httpx.AsyncClient(timeout=s.request_timeout_seconds) as c:
        r = await c.get(s.arxiv_base_url, params={"search_query": f"all:{query}", "start": 0, "max_results": 5})
        r.raise_for_status()
        return [Evidence(source="arxiv", title="arXiv feed", content=r.text[:6000], url=str(r.url))]

async def youtube_search(query: str) -> list[Evidence]:
    s = get_settings()
    if s.mock_mode or not s.youtube_api_key:
        return []
    async with httpx.AsyncClient(timeout=s.request_timeout_seconds) as c:
        r = await c.get("https://www.googleapis.com/youtube/v3/search", params={"part":"snippet","q":query,"type":"video","maxResults":5,"key":s.youtube_api_key})
        r.raise_for_status()
        out=[]
        for x in r.json().get("items", []):
            vid=x.get("id",{}).get("videoId")
            sn=x.get("snippet",{})
            out.append(Evidence(source="youtube", title=sn.get("title",""), content=sn.get("description",""), url=f"https://www.youtube.com/watch?v={quote_plus(vid)}" if vid else None))
        return out
