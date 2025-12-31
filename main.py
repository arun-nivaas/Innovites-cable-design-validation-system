from fastapi import FastAPI,status
from fastapi.middleware.cors import CORSMiddleware
from src.backend.router.design_router import router as design_router
import uvicorn
from dotenv import load_dotenv
from pathlib import Path
from src.backend.config.logger import logger
from typing import Dict, Any


# Load environment variables
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Application settings
APP_TITLE = "Innovites Cable Design Validation System"
APP_VERSION = "1.0.0"
HOST = "127.0.0.1"
PORT = 8000

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Advanced AI-powered validation for wires and cables design.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(design_router)

@app.get("/", status_code=status.HTTP_200_OK, tags=["System"])
async def root_health_check() -> Dict[str,Any]:
    """
    Landing Page & Health Check
    Shows system status immediately when opening the base URL.
    """
    return {
        "status": "healthy",
        "service": APP_TITLE,
        "version": APP_VERSION,
        "documentation": "/docs",
        "message": "API is operational. Use the /docs endpoint for testing."
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🌐 Starting server on http://{HOST}:{PORT}")
    logger.info(f"📚 API docs available at http://{HOST}:{PORT}/docs\n")

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True, log_level="info")