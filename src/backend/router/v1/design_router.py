from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import json
from src.backend.config.logger import logger
from src.backend.db.models.ai_validation_model import AIValidation
from src.backend.orchestrator.cable_validation_orchestrator import CableDesignValidator
from src.backend.validators.database_validators import ISRAGDatabaseValidator
from src.backend.formatters.evidence_formatters import EvidenceFormatter
from src.backend.extractor.llm_extractor import LLMFieldExtractor
from src.backend.providers.groq_llm_client import GroqLLMClient
from src.backend.providers.gemini_llm_client import GeminiLLMClient
from src.backend.auditors.llm_auditor import LLMAuditor
from src.backend.schemas.cable_validation_schema import (
    DesignValidationPostRequest, 
    DesignValidationGetResponse,
    DesignValidationPostResponse
)
from src.backend.db.database import get_db
from src.backend.db.crud import save_ai_validation  #type: ignore
from langsmith import traceable #type: ignore
from src.backend.tasks.validation_task import validate_cable_design_task #type: ignore


router = APIRouter()

def get_cable_validator(db: Session = Depends(get_db)) -> CableDesignValidator:
    extraction_client = GroqLLMClient()
    audit_client = GeminiLLMClient()
    
    return CableDesignValidator(
        field_extractor=LLMFieldExtractor(extraction_client),
        database_validator=ISRAGDatabaseValidator(db),
        evidence_formatter=EvidenceFormatter(),
        auditor=LLMAuditor(audit_client)
    )

@traceable(name="cable_design_validation_result_Api_hit")
@router.get("/design-validations/{request_id}", response_model=DesignValidationGetResponse, status_code=status.HTTP_200_OK)
async def get_validation_result(request_id: uuid.UUID, db: Session = Depends(get_db)):
    logger.info(f"Fetching validation result for request_id={request_id}")
    try:
        validation_record = db.query(AIValidation).filter(AIValidation.request_id == request_id).first()
        
        if not validation_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No validation record found for request_id: {request_id}"
            )
        logger.info(f"Validation record found for request_id={request_id} | job_status={validation_record.status}")

        return DesignValidationGetResponse(
            request_id=validation_record.request_id,
            job_status=validation_record.status,
            result=validation_record.ai_response,
            error=validation_record.error_message,
            meta={
                "model_name": validation_record.model_name,
                "pipeline_type": validation_record.pipeline_type
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching validation record for request_id={request_id} | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving validation record. Please try again later."
        )

@traceable(name="cable_design_validation_Api_hit")
@router.post("/design-validations", response_model=DesignValidationPostResponse, status_code=status.HTTP_202_ACCEPTED)
async def validate_design(
    payload: DesignValidationPostRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"Validation request received: {payload.data}...")
    request_id = uuid.uuid4()
    logger.info(f"Assigned Request ID: {request_id}")
    
    raw_text = ""
    try:
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
            user_input = payload.data
            
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input mode: {payload.input_mode}. Supported modes are 'free_text', 'json', and 'manual'."
            )

        # Save initial record with PENDING status
        save_ai_validation(
            db=db,
            request_id=request_id,
            raw_text=raw_text,
            ai_result=None,  # No result yet - will be updated by Celery task
            meta={
                "model_name": "Gemini 2.5 flash",
                "pipeline_type": "structured_rag",
                "status": "PENDING"
            }
        )

        # Submit task to Celery worker (background processing)
        validate_cable_design_task.delay(
            request_id=str(request_id),
            user_input=user_input,
            input_mode=payload.input_mode
        )

        logger.info(f"Validation job submitted to background worker | request_id={request_id}")

        return DesignValidationPostResponse(
            request_id=request_id,
            job_status="PENDING",
            meta={
                "model_name": "Gemini 2.5 flash",
                "pipeline_type": "structured_rag",
                "message": "Validation job submitted."
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to submit validation job | request_id={request_id} | error={str(e)}", exc_info=True)
        
        # Save failed record
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
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit validation job. Please try again."
        )
    
