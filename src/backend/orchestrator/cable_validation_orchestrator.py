from src.backend.config.logger import logger
from src.backend.interfaces.IS_cable_validation import (
    IFieldExtractor, 
    IDatabaseValidator, 
    IEvidenceFormatter, 
    IAuditor
)
from src.backend.schemas.cable_validation_schema import LLMResponseSchema, CableDesignSchema
from typing import Union, Dict, Any

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
    
    async def validate(self, 
        user_input: Union[str, Dict[str, Any]], 
        input_mode: str) -> LLMResponseSchema:
        logger.info("Starting cable design validation workflow")
        logger.info(f"Starting cable design validation workflow | mode={input_mode}")

        # Extract fields
        if input_mode == "free_text":
            logger.info("Using LLM extractor for free text input")
            extracted_fields = await self.field_extractor.extract(user_input)  # Returns CableDesignSchema
            logger.debug(f"Fields extracted via LLM: {extracted_fields}")
            
        elif input_mode in {"json", "manual"}:
            logger.info("Bypassing LLM extractor - converting structured input to CableDesignSchema")
            # Convert dict to CableDesignSchema using Pydantic validation
            if not isinstance(user_input, dict):
                raise ValueError(f"Expected dict for {input_mode} mode, got {type(user_input).__name__}")
            extracted_fields = CableDesignSchema(**user_input)
            logger.debug(f"Structured fields converted to schema: {extracted_fields}")
            
        else:
            raise ValueError(f"Invalid input_mode: {input_mode}")
        
        # Validate against database
        db_validations = self.database_validator.validate(extracted_fields)
        logger.debug(f"Database validation completed with {len(db_validations)} results")
        
        # Format evidence
        evidence_context = self.evidence_formatter.format(db_validations)
        
        # Audit with LLM
        result = await self.auditor.audit(evidence_context, extracted_fields)
        logger.info("Cable design validation completed successfully")
        
        return result