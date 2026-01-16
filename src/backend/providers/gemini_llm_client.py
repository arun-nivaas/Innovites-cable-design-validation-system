from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from src.backend.interfaces.LLM_Client import ValidateLLMClient
from src.backend.schemas.cable_validation_schema import CableDesignSchema, LLMResponseSchema
from src.backend.config.settings import settings
from src.backend.config.logger import logger
from src.backend.config.exception import LLMInvocationError
from langchain_core.prompts import ChatPromptTemplate
from src.backend.prompt_library.system_prompt import SYSTEM_PROMPT
from src.backend.config.constants import constant

class GeminiLLMClient(ValidateLLMClient):
    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model ="gemini-2.5-flash",
                temperature = 0,
                max_completion_tokens = 700,
                api_key = SecretStr(settings.google_api_key),
                model_kwargs={"response_format": {"type": "json_object"}}
            )
            logger.info(f"{constant.GEMINI} LLM client initialized")

        except Exception as e:
            logger.critical(f"Failed to initialize {constant.GEMINI} LLM client", exc_info=True)
            raise RuntimeError(f"{constant.GEMINI} LLM client initialization failed") from e
        
    async def validate(self, evidence_context: str, extracted_fields: CableDesignSchema) -> LLMResponseSchema:

        logger.info(f"Starting cable design validation: {evidence_context[:50]}...")

        try:
            structured_llm = self.llm.with_structured_output(LLMResponseSchema) #type: ignore

            prompt = ChatPromptTemplate.from_messages([ #type: ignore
                ("system", SYSTEM_PROMPT), 
                ("human",(
                    "### DATA TO REPORT IN 'fields':\n{extracted_fields}\n\n"
                    "### DATABASE EVIDENCE FOR AUDIT:\n{evidence_context}"
                ))
            ])

            chain = prompt | structured_llm   #type: ignore
            response = await chain.ainvoke({"evidence_context": evidence_context, "extracted_fields": extracted_fields})  #type: ignore

            return response  #type: ignore

        except Exception as e:
            logger.error(f"{constant.GEMINI} LLM invocation failed", exc_info=True)
            raise LLMInvocationError(f"{constant.GEMINI} LLM failed during cable validation") from e