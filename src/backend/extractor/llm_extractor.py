from src.backend.interfaces.IS_cable_validation import IFieldExtractor
from src.backend.interfaces.LLM_Client import ExtractLLMClient
from src.backend.config.logger import logger
from src.backend.schemas.cable_validation_schema import CableDesignSchema
from typing import Union, Dict, Any

class LLMFieldExtractor(IFieldExtractor):
    
    def __init__(self, extract_client: ExtractLLMClient):
        self.extract_client = extract_client
        logger.info("LLMFieldExtractor initialized")
    
    async def extract(self, user_input: Union[str, Dict[str, Any]]) -> CableDesignSchema:
        logger.debug("Extracting fields from user input")
        return await self.extract_client.extract(user_input)
