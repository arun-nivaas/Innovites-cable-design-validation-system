from src.backend.interfaces.LLM_Client import ExtractLLMClient
from src.backend.config.logger import logger
from pydantic import SecretStr
from src.backend.config.settings import settings
from langchain_anthropic import ChatAnthropic
from src.backend.schemas.cable_validation_schema import CableDesignSchema
from langchain_core.prompts import ChatPromptTemplate
from src.backend.prompt_library.extraction_prompt import EXTRACTION_PROMPT
from src.backend.config.exception import LLMInvocationError
from src.backend.config.constants import constant

class AnthropicLLMClient(ExtractLLMClient):

    def __init__(self):

        try:
            self.llm = ChatAnthropic(
                model_name ="claude-3-5-haiku-20241022",
                temperature =0,
                max_tokens_to_sample=200,
                api_key =SecretStr(settings.anthropic_api_key),
                timeout=60.0,
                stop=None
            )
            logger.info(f"{constant.CLAUDE} LLM client initialized")

        except Exception as e:
            logger.critical(f"Failed to initialize {constant.CLAUDE} LLM client", exc_info=True)
            raise RuntimeError(f"{constant.CLAUDE} LLM client initialization failed") from e


    async def extract(self, user_input: str) -> CableDesignSchema:

        logger.info(f"Starting entity extraction: {user_input[:50]}...")

        try:
            structured_llm = self.llm.with_structured_output(CableDesignSchema) #type: ignore

            prompt = ChatPromptTemplate.from_messages([ #type: ignore
                ("system", EXTRACTION_PROMPT), 
                ("human", "{user_input}")
            ])

            chain = prompt | structured_llm   #type: ignore
            response = await chain.ainvoke({"user_input": user_input})  #type: ignore

            return response  #type: ignore

        except Exception as e:
            logger.error(f"{constant.CLAUDE} LLM extraction failed", exc_info=True)
            raise LLMInvocationError(f"{constant.CLAUDE} LLM failed during entity extraction") from e