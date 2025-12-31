from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Google Gemini
    google_api_key: str = Field(default="", description="Google API key")
    gemini_model_name: str = Field(default="", description="Gemini model name")

    # LangSmith
    langsmith_api_key: str = Field(default="", description="LangSmith API key")
    langsmith_project: str = Field(default="", description="LangSmith project name")
    langsmith_endpoint: str = Field(default="", description="LangSmith endpoint")
    langsmith_tracing_v2: bool = Field(default=False)

settings = Settings()
