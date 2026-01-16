from abc import ABC, abstractmethod
from typing import List
from src.backend.schemas.cable_validation_schema import CableDesignSchema, ValidationResponseSchema, LLMResponseSchema

class IFieldExtractor(ABC):
    """Interface for extracting fields from user input"""
    @abstractmethod
    async def extract(self, user_input: str) -> CableDesignSchema:
        pass


class IDatabaseValidator(ABC):
    """Interface for validating against database"""
    @abstractmethod
    def validate(self, extracted_fields: CableDesignSchema) -> List[ValidationResponseSchema]:
        pass


class IEvidenceFormatter(ABC):
    """Interface for formatting validation evidence"""
    @abstractmethod
    def format(self, db_validations: List[ValidationResponseSchema]) -> str:
        pass


class IAuditor(ABC):
    """Interface for auditing with LLM"""
    @abstractmethod
    async def audit(self, evidence_context: str, extracted_fields: CableDesignSchema) -> LLMResponseSchema:
        pass