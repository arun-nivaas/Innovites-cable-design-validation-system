from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.router.v1.design_router import router as design_router_v1
from src.backend.router.system_router import router as system_router
import uvicorn
from dotenv import load_dotenv
from pathlib import Path
from src.backend.config.logger import logger
from src.backend.db.database import engine, Base
from src.backend.config.constants import constant


# Load environment variables
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


app = FastAPI(
    title=f"{constant.APP_TITLE} API",
    version=constant.API_VERSION,
    description="Advanced AI-powered validation for wires and cables design.",
    openapi_tags=[
        {
            "name": "Design Validation v1",
            "description": "Endpoints for submitting and retrieving cable design validations."
        },
        {
            "name": "System",
            "description": "Health check and monitoring endpoints."
        }
    ],
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

app.include_router(design_router_v1,prefix=f"{constant.API_PREFIX}/design",tags=[f"Design Validation {constant.API_VERSION}"])  
app.include_router(system_router)



if __name__ == "__main__":
    
    logger.info(f"🌐 Starting server on http://{constant.HOST}:{constant.PORT}")
    logger.info(f"📚 API docs available at http://{constant.HOST}:{constant.PORT}/docs\n")

    uvicorn.run("main:app", host=constant.HOST, port=constant.PORT, reload=True, log_level="info")