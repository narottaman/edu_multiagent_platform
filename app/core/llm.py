from app.core.config import get_settings

async def generate(prompt: str, *, research: bool = False) -> str:
    s = get_settings()
    if s.mock_mode or not s.google_api_key:
        return "[MOCK] " + prompt[:700]
    from langchain_google_genai import ChatGoogleGenerativeAI
    model = s.gemini_research_model if research else s.gemini_model
    llm = ChatGoogleGenerativeAI(model=model, google_api_key=s.google_api_key, temperature=0.2)
    msg = await llm.ainvoke(prompt)
    return str(msg.content)
