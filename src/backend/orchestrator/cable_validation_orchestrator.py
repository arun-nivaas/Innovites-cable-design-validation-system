from src.backend.config.logger import logger
from src.backend.interfaces.IS_cable_validation import (
    IFieldExtractor, 
    IDatabaseValidator, 
    IEvidenceFormatter, 
    IAuditor
)
from src.backend.schemas.cable_validation_schema import LLMResponseSchema

class CableDesignValidator:
    
    def __init__(
        self,
        field_extractor: IFieldExtractor,
        database_validator: IDatabaseValidator,
        evidence_formatter: IEvidenceFormatter,
        auditor: IAuditor
    ):
        self.field_extractor = field_extractor
        self.database_validator = database_validator
        self.evidence_formatter = evidence_formatter
        self.auditor = auditor
        logger.info("CableDesignValidator initialized with dependency injection")
    
    async def validate(self, user_input: str) -> LLMResponseSchema:
        logger.info("Starting cable design validation workflow")
        
        # Extract fields
        extracted_fields = await self.field_extractor.extract(user_input)
        logger.debug(f"Fields extracted: {extracted_fields}")
        
        # Validate against database
        db_validations = self.database_validator.validate(extracted_fields)
        logger.debug(f"Database validation completed with {len(db_validations)} results")
        
        # Format evidence
        evidence_context = self.evidence_formatter.format(db_validations)
        
        # Audit with LLM
        result = await self.auditor.audit(evidence_context, extracted_fields)
        logger.info("Cable design validation completed successfully")
        
        return result