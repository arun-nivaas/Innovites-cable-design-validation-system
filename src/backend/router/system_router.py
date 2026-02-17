from fastapi import APIRouter, status
from typing import Dict, Any
from datetime import datetime
from src.backend.config.constants import constant  # Adjust import path as needed

# System Router - no prefix, root level endpoints
router = APIRouter(tags=["System"])

@router.get("/", status_code=status.HTTP_200_OK)
async def root_health_check() -> Dict[str, Any]:
    """
    Landing Page & Health Check
    Shows system status immediately when opening the base URL.
    """
    return {
        "status": "healthy",
        "service": constant.APP_TITLE,
        "version": constant.APP_VERSION,
        "documentation": "/docs",
        "message": "API is operational. Use /docs for API documentation."
    }

@router.get("/health", status_code=status.HTTP_200_OK)
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint
    Provides additional system information
    """
    return {
        "status": "healthy",
        "service": constant.APP_TITLE,
        "version": constant.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational"
    }
