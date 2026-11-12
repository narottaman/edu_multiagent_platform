from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    log_level: str = "INFO"
    mock_mode: bool = True
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_research_model: str = "gemini-2.5-pro"
    tavily_api_key: str = ""
    youtube_api_key: str = ""
    arxiv_base_url: str = "https://export.arxiv.org/api/query"
    canvas_base_url: str = ""
    canvas_access_token: str = ""
    canvas_allowed_course_ids: str = ""
    rag_service_url: str = "http://rag-service:8010"
    rag_service_api_key: str = ""
    database_url: str = "postgresql+psycopg://edu:edu@postgres:5432/edu"
    redis_url: str = "redis://redis:6379/0"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "change-me"
    qdrant_url: str = "http://qdrant:6333"
    qdrant_api_key: str = ""
    oidc_issuer: str = ""
    oidc_audience: str = "edu-multiagent"
    oidc_jwks_url: str = ""
    dev_auth_bypass: bool = True
    max_tool_calls: int = 12
    max_agent_steps: int = 10
    request_timeout_seconds: int = 45
    enable_code_sandbox: bool = False
    sandbox_service_url: str = "http://sandbox:8020"

    @property
    def allowed_courses(self) -> set[str]:
        return {x.strip() for x in self.canvas_allowed_course_ids.split(",") if x.strip()}

@lru_cache
def get_settings() -> Settings:
    return Settings()
