from src.backend.config.logger import logger
from src.backend.interfaces.IS_cable_validation import (
    IFieldExtractor, 
    IDatabaseValidator, 
    IEvidenceFormatter, 
    IAuditor
)
from src.backend.schemas.cable_validation_schema import GeminiValidationResponse, InScopeResponse, CableDesignSchema,OutOfScopeResponse,GroqExtractionResponse
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
        input_mode: str) -> Union[OutOfScopeResponse, InScopeResponse]:
        logger.info("Starting cable design validation workflow")
        logger.info(f"Starting cable design validation workflow | mode={input_mode}")

        # Extract fields
        if input_mode == "free_text":
            logger.info("Using LLM extractor for free text input")
            groqResult:GroqExtractionResponse = await self.field_extractor.extract(user_input)  # Returns CableDesignSchema
            logger.debug(f"Fields extracted via LLM: {groqResult}")
            
            if groqResult.is_out_of_scope:
                logger.warning("Input flagged as out of scope by LLM extractor")
                return OutOfScopeResponse(
                    is_out_of_scope=True,
                    out_of_scope_explanation = groqResult.out_of_scope_explanation or ""
                )
            
            if groqResult.fields is None:
                raise ValueError("Fields extraction failed: groqResult.fields is None")
            
            extracted_fields: CableDesignSchema = groqResult.fields

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
        logger.debug(f"Evidence formatted for auditor: {evidence_context[:500]}...")
        
        # Audit with LLM
        gemini_result: GeminiValidationResponse = await self.auditor.audit(evidence_context, extracted_fields)
        logger.info("Cable design validation completed successfully")

        # Assemble final response
        return InScopeResponse(
            is_out_of_scope=False,
            fields = extracted_fields,
            validation = gemini_result.validation,
            confidence = gemini_result.confidence
        )