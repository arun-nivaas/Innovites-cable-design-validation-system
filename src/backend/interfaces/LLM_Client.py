from abc import ABC, abstractmethod
from src.backend.schemas.cable_validation_schema import LLMResponseSchema, CableDesignSchema

class ExtractLLMClient(ABC):
    @abstractmethod
    async def extract(self, user_input: str) -> CableDesignSchema:
        pass

class ValidateLLMClient(ABC):
    @abstractmethod
    async def validate(self, evidence_context: str, extracted_fields: CableDesignSchema) -> LLMResponseSchema:
        pass


    