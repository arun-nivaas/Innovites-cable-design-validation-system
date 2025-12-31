from fastapi import APIRouter, HTTPException, status
from src.backend.cable_validator import CableDesignValidator
from src.backend.schemas.cable_validation_schema import LLMResponseSchema,DesignValidationRequest
from src.backend.config.logger import logger
from langsmith import traceable #type: ignore

router = APIRouter(prefix="/design", tags=["Design Validation"])

validator = CableDesignValidator()

@traceable(name = "cable_design_validation_Api_hit")
@router.post("/validate", response_model=LLMResponseSchema, status_code=status.HTTP_200_OK)
async def validate_design(payload: DesignValidationRequest):
    
    logger.info(f"Validation request received: {payload.input[:50]}...")
    
    try:
        result = await validator.validate(payload.input)
        logger.info("Validation completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cable design validation failed. Please try again."
        )

    