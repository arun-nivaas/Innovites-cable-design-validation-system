from celery import Celery
from celery.exceptions import MaxRetriesExceededError
from src.backend.db.database import SessionLocal
from src.backend.db.models.ai_validation_model import AIValidation
from src.backend.orchestrator.cable_validation_orchestrator import CableDesignValidator
from src.backend.validators.database_validators import ISRAGDatabaseValidator
from src.backend.formatters.evidence_formatters import EvidenceFormatter
from src.backend.extractor.llm_extractor import LLMFieldExtractor
from src.backend.providers.groq_llm_client import GroqLLMClient
from src.backend.providers.gemini_llm_client import GeminiLLMClient
from src.backend.auditors.llm_auditor import LLMAuditor
from src.backend.config.logger import logger
import uuid
import asyncio
from typing import Any
from src.backend.config.settings import settings

celery_app: Celery = Celery(
    "Cable Validation",
    broker=settings.redis_url_set,
    backend=settings.redis_url_set
)

celery_config: dict[str, Any] = {
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'worker_pool': 'solo'
}
celery_app.conf.update(celery_config)  # type: ignore

@celery_app.task(name="validate_cable_design", bind=True, max_retries=3) # type: ignore
def validate_cable_design_task(self, request_id: str, user_input: Any, input_mode: str) -> dict[str, Any]:
    db = SessionLocal() 
    try:
        logger.info(f"[CELERY] Starting validation for request_id={request_id}")
        
        extraction_client = GroqLLMClient()
        audit_client = GeminiLLMClient()
        validator = CableDesignValidator(
            field_extractor=LLMFieldExtractor(extraction_client),
            database_validator=ISRAGDatabaseValidator(db),
            evidence_formatter=EvidenceFormatter(),
            auditor=LLMAuditor(audit_client)
        )

        # ✅ FIX 3: Now validator is defined
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(validator.validate(user_input, input_mode))
        loop.close()

        validation_record = db.query(AIValidation).filter(
            AIValidation.request_id == uuid.UUID(request_id)
        ).first()
        
        if validation_record:
            validation_record.ai_response = result.model_dump()
            validation_record.status = "SUCCESS"
            db.commit()
            logger.info(f"[CELERY] Validation completed successfully | request_id={request_id}")
        else:
            logger.error(f"[CELERY] Validation record not found | request_id={request_id}")
        
        return {"status": "SUCCESS", "request_id": request_id}
        
    except Exception as e:
        logger.error(f"[CELERY] Validation failed | request_id={request_id} | error={str(e)}", exc_info=True)
        
        # Update database with FAILED
        validation_record = db.query(AIValidation).filter(
            AIValidation.request_id == uuid.UUID(request_id)
        ).first()
        
        if validation_record:
            validation_record.status = "FAILED"
            validation_record.error_message = str(e)
            db.commit()
        
        # Retry logic
        try:
            raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
        except MaxRetriesExceededError:
            logger.error(f"[CELERY] Max retries exceeded | request_id={request_id}")
            return {"status": "FAILED", "request_id": request_id, "error": str(e)}
    
    finally:
        db.close()