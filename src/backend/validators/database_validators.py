from sqlalchemy.orm import Session
from typing import List
from src.backend.config.logger import logger
from src.backend.validators.cable_rag_validator import CableRAGValidator
from src.backend.schemas.cable_validation_schema import CableDesignSchema, ValidationResponseSchema
from src.backend.interfaces.IS_cable_validation import IDatabaseValidator


class ISRAGDatabaseValidator(IDatabaseValidator):
    
    def __init__(self, db: Session):
        self.db = db
        logger.info("ISRAGDatabaseValidator initialized")
    
    def validate(self, extracted_fields: CableDesignSchema) -> List[ValidationResponseSchema]:
        logger.debug("Validating extracted fields against database")
       
        rag_checker = CableRAGValidator(self.db)
        return rag_checker.validate_design(extracted_fields)