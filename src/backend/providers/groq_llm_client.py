from langchain_groq import ChatGroq
from src.backend.interfaces.LLM_Client import ExtractLLMClient
from src.backend.config.logger import logger
from pydantic import SecretStr
from src.backend.config.settings import settings
from src.backend.schemas.cable_validation_schema import CableDesignSchema
from langchain_core.prompts import ChatPromptTemplate
from src.backend.prompt_library.extraction_prompt import EXTRACTION_PROMPT
from src.backend.config.exception import LLMInvocationError
from src.backend.config.constants import constant

class GroqLLMClient(ExtractLLMClient):

    def __init__(self):

        try:
            self.llm = ChatGroq(
                model="llama-3.1-8b-instant",
                temperature=0,
                max_tokens=200,
                api_key=SecretStr(settings.groq_api_key)
            )
            logger.info(f"{constant.GROQ} LLM client initialized")

        except Exception as e:
            logger.critical(f"Failed to initialize {constant.GROQ} LLM client", exc_info=True)
            raise RuntimeError(f"{constant.GROQ} LLM client initialization failed") from e


    async def extract(self, user_input: str) -> CableDesignSchema:

        logger.info(f"Starting entity extraction: {user_input[:50]}...")

        try:
            structured_llm = self.llm.with_structured_output(CableDesignSchema) #type: ignore

            prompt = ChatPromptTemplate.from_messages([ #type: ignore
                ("system", EXTRACTION_PROMPT), 
                ("human", "{user_input}")
            ])

            chain = prompt | structured_llm #type: ignore
            response = await chain.ainvoke({"user_input": user_input}) #type: ignore

            return response #type: ignore

        except Exception as e:
            logger.error(f"{constant.GROQ} LLM extraction failed", exc_info=True)
            raise LLMInvocationError(f"{constant.GROQ} LLM failed during entity extraction") from e