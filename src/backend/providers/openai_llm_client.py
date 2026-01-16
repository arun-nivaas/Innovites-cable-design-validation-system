from src.backend.interfaces.LLM_Client import ExtractLLMClient
from pydantic import SecretStr
from src.backend.config.logger import logger
from src.backend.config.settings import settings
from langchain_openai import ChatOpenAI
from src.backend.schemas.cable_validation_schema import CableDesignSchema
from langchain_core.prompts import ChatPromptTemplate
from src.backend.prompt_library.extraction_prompt import EXTRACTION_PROMPT
from src.backend.config.exception import LLMInvocationError
from src.backend.config.constants import constant


class OpenAILLMClient(ExtractLLMClient):

    def __init__(self):

        try:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature = 0,
                max_completion_tokens = 200,
                api_key=SecretStr(settings.openai_api_key),
                model_kwargs={"response_format": {"type": "json_object"}}
            )
            logger.info(f"{constant.GPT} LLM client initialized")

        except Exception as e:
            logger.critical(f"Failed to initialize {constant.GPT} LLM client", exc_info=True)
            raise RuntimeError(f"{constant.GPT} LLM client initialization failed") from e


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
            logger.error(f"{constant.GPT} LLM extraction failed", exc_info=True)
            raise LLMInvocationError(f"{constant.GPT} LLM failed during entity extraction") from e
