from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import json
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
   
    logger.info(f"Validation request received: {payload.data}...")
    request_id = uuid.uuid4()
    logger.info(f"Assigned Request ID: {request_id}")
    
    raw_text = ""
    try:
        # Note: No need to pass 'db' anymore - it's already injected into the validator
        if payload.input_mode == "free_text":
            description = payload.data.get("description", "")
            if not description:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Description is required for free_text input mode."
                )
            raw_text = description
            user_input = description
            
        elif payload.input_mode in {"json", "manual"}:
            raw_text = json.dumps(payload.data, indent=2)
            user_input = payload.data  # Pass as dict - LLM will handle validation
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input mode: {payload.input_mode}. Supported modes are 'free_text', 'json', and 'manual'."
            )

       
    
        result = await validator.validate(user_input, payload.input_mode)


        save_ai_validation(
            db=db,
            request_id=request_id,
            raw_text = raw_text,
            ai_result = result.model_dump(),
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
            raw_text=raw_text,
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