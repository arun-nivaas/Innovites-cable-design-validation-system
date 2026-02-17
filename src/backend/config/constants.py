from typing import Final

class Constant:
    
    # Model Types
    GEMINI = "Gemini"
    GPT = "GPT"
    CLAUDE = "Claude"
    GROQ = "Groq"

    # Application Settings
    APP_TITLE = "Cable Design Validation System"
    APP_VERSION: Final[str] = "1.0.0"
    API_VERSION: Final[str] = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    HOST: Final[str] = "127.0.0.1"
    PORT: Final[int] = 8001

constant = Constant()