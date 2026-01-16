from fastapi import FastAPI,status
from fastapi.middleware.cors import CORSMiddleware
from src.backend.router.design_router import router as design_router
import uvicorn
from dotenv import load_dotenv
from pathlib import Path
from src.backend.config.logger import logger
from typing import Dict, Any
from src.backend.db.database import engine, Base
from src.backend.config.constants import constant


# Load environment variables
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


app = FastAPI(
    title=constant.APP_TITLE,
    version=constant.APP_VERSION,
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

Base.metadata.create_all(bind=engine)

app.include_router(design_router)

@app.get("/", status_code=status.HTTP_200_OK, tags=["System"])
async def root_health_check() -> Dict[str,Any]:
    """
    Landing Page & Health Check
    Shows system status immediately when opening the base URL.
    """
    return {
        "status": "healthy",
        "service": constant.APP_TITLE,
        "version": constant.APP_VERSION,
        "documentation": "/docs",
        "message": "API is operational. Use the /docs endpoint for testing."
    }

if __name__ == "__main__":
    
    logger.info(f"🌐 Starting server on http://{constant.HOST}:{constant.PORT}")
    logger.info(f"📚 API docs available at http://{constant.HOST}:{constant.PORT}/docs\n")

    uvicorn.run("main:app", host=constant.HOST, port=constant.PORT, reload=True, log_level="info")