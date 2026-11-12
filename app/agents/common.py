from app.models.schemas import Evidence

def evidence_text(items: list[Evidence], limit: int = 12) -> str:
    return "\n\n".join(f"[{i+1}] {e.source} | {e.title}\n{e.content[:1800]}\n{e.url or e.citation or ''}" for i,e in enumerate(items[:limit]))
