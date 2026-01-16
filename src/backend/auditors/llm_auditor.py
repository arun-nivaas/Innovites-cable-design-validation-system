from src.backend.config.logger import logger
from src.backend.interfaces.IS_cable_validation import IAuditor
from src.backend.schemas.cable_validation_schema import LLMResponseSchema
from src.backend.interfaces.LLM_Client import ValidateLLMClient
from src.backend.schemas.cable_validation_schema import CableDesignSchema

class LLMAuditor(IAuditor):
    
    def __init__(self, audit_client: ValidateLLMClient):
        self.audit_client = audit_client
        logger.info("LLMAuditor initialized")
    
    async def audit(self, evidence_context: str, extracted_fields:CableDesignSchema) -> LLMResponseSchema:
        logger.debug("Performing LLM audit")
        return await self.audit_client.validate(evidence_context, extracted_fields)