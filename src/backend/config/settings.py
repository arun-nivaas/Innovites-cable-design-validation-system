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
    openai_api_key: str = Field(default="", description="OpenAI API key")
    google_api_key: str = Field(default="", description="Google API key")
    model_name: str = Field(default="", description="model name")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    groq_api_key: str = Field(default="", description="Groq API key")
    llama_cloud_api_key: str = Field(default="", description="Llama Cloud API key")

    # Database
    database_url: str = Field(default="", description="Database connection URL")

    
    # LangSmith
    langsmith_api_key: str = Field(default="", description="LangSmith API key")
    langsmith_project: str = Field(default="", description="LangSmith project name")
    langsmith_endpoint: str = Field(default="", description="LangSmith endpoint")
    langsmith_tracing_v2: bool = Field(default=False)

settings = Settings()
