from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from src.backend.config.logger import logger
from src.backend.orchestrator.cable_validation_orchestrator import CableDesignValidator
from src.backend.validators.database_validators import ISRAGDatabaseValidator
from src.backend.formatters.evidence_formatters import EvidenceFormatter
from src.backend.extractor.llm_extractor import LLMFieldExtractor
from src.backend.providers.groq_llm_client import GroqLLMClient
from src.backend.providers.gemini_llm_client import GeminiLLMClient
from src.backend.auditors.llm_auditor import LLMAuditor
from src.backend.schemas.cable_validation_schema import DesignValidationRequest, LLMResponseSchema
from src.backend.db.database import get_db
from src.backend.db.crud import save_ai_validation #type: ignore
from langsmith import traceable #type: ignore


router = APIRouter(prefix="/design", tags=["Design Validation"])

def get_cable_validator(db: Session = Depends(get_db)) -> CableDesignValidator:
   
    extraction_client = GroqLLMClient()
    audit_client = GeminiLLMClient()
    
    return CableDesignValidator(
        field_extractor = LLMFieldExtractor(extraction_client),
        database_validator = ISRAGDatabaseValidator(db),
        evidence_formatter = EvidenceFormatter(),
        auditor = LLMAuditor(audit_client)
    )

@traceable(name="cable_design_validation_Api_hit")
@router.post("/validate", response_model= LLMResponseSchema, status_code=status.HTTP_200_OK)
async def validate_design(
    payload: DesignValidationRequest,
    validator: CableDesignValidator = Depends(get_cable_validator),
    db: Session = Depends(get_db)):
   
    logger.info(f"Validation request received: {payload.input[:50]}...")
    request_id = uuid.uuid4()
    logger.info(f"Assigned Request ID: {request_id}")
    
    try:
        # Note: No need to pass 'db' anymore - it's already injected into the validator
        result = await validator.validate(payload.input)
        
        save_ai_validation(
            db=db,
            request_id=request_id,
            raw_text=payload.input,
            ai_result=result.model_dump(),
            meta={
                "model_name": "Gemini 2.5 flash",
                "pipeline_type": "structured_rag",
                "status": "SUCCESS"
            }
        )

        logger.info(f"Validation successful | request_id={request_id}")
        return result
        
    except Exception as e:
        save_ai_validation(
            db=db,
            request_id=request_id,
            raw_text=payload.input,
            ai_result=None,
            meta={
                "model_name": "Gemini 2.5 flash",  
                "pipeline_type": "structured_rag",
                "status": "FAILED"
            },
            error_message=str(e)
        )

        logger.error(f"Validation failed | request_id={request_id} | error={str(e)}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cable design validation failed. Please try again."
        )