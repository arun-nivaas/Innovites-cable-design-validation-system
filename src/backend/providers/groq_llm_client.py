from langchain_groq import ChatGroq
from src.backend.interfaces.LLM_Client import ExtractLLMClient
from src.backend.config.logger import logger
from pydantic import SecretStr
from src.backend.config.settings import settings
from src.backend.schemas.cable_validation_schema import GroqExtractionResponse
from langchain_core.prompts import ChatPromptTemplate
from src.backend.config.exception import LLMInvocationError
from src.backend.config.constants import constant
from src.backend.prompt_library.prompt_registry import get_prompt_config
from typing import Union, Dict, Any
from langsmith import traceable

@traceable(name="Extraction Model", metadata={"model": "groq", "component": "LLM_Client"})
class GroqLLMClient(ExtractLLMClient):

    def __init__(self):

        try:
            self.prompt_config = get_prompt_config("extraction_v1")
            self.llm = ChatGroq(
                model=self.prompt_config["model"],
                temperature=self.prompt_config["temperature"],
                max_tokens=self.prompt_config["max_tokens"],
                api_key=SecretStr(settings.groq_api_key)
            )
            logger.info(f"{constant.GROQ} LLM client initialized")

        except Exception as e:
            logger.critical(f"Failed to initialize {constant.GROQ} LLM client", exc_info=True)
            raise RuntimeError(f"{constant.GROQ} LLM client initialization failed") from e

    async def extract(self, user_input: Union[str, Dict[str, Any]]) -> GroqExtractionResponse:

        log_input = user_input[:50] if isinstance(user_input, str) else str(user_input)[:50]
        logger.info(f"Starting entity extraction: {log_input}...")

        try:
            structured_llm = self.llm.with_structured_output(self.prompt_config["schema"]) #type: ignore

            prompt = ChatPromptTemplate.from_messages([ #type: ignore
                ("system", self.prompt_config["system_prompt"]), 
                ("human", "{user_input}")
            ])

            chain = prompt | structured_llm #type: ignore
            response = await chain.ainvoke({"user_input": user_input}) #type: ignore
            
            logger.debug(f"LLM Extraction Response: {response.json()}") #type: ignore
            return response #type: ignore
            

        except Exception as e:
            logger.error(f"{constant.GROQ} LLM extraction failed", exc_info=True)
            raise LLMInvocationError(f"{constant.GROQ} LLM failed during entity extraction") from e