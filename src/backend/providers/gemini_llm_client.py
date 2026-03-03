from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr
from src.backend.interfaces.LLM_Client import ValidateLLMClient
from src.backend.schemas.cable_validation_schema import CableDesignSchema, Confidence, GeminiValidationResponse
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
                max_output_tokens = 2048,
                api_key = SecretStr(settings.google_api_key)
            )
            logger.info(f"{constant.GEMINI} LLM client initialized")

        except Exception as e:
            logger.critical(f"Failed to initialize {constant.GEMINI} LLM client", exc_info=True)
            raise RuntimeError(f"{constant.GEMINI} LLM client initialization failed") from e
        
    async def validate(self, evidence_context: str, extracted_fields: CableDesignSchema) -> GeminiValidationResponse:

        logger.info(f"Starting cable design validation audit...")
        logger.debug(f"AUDITOR INPUT - Fields: {extracted_fields.model_dump()}")
        logger.debug(f"AUDITOR INPUT - Evidence: {evidence_context}")

        try:
            structured_llm = self.llm.with_structured_output(GeminiValidationResponse) #type: ignore

            prompt = ChatPromptTemplate.from_messages([ #type: ignore
                ("system", SYSTEM_PROMPT), 
                ("human",(
                    "### AUDIT INPUTS:\n"
                    "EXTRACTED FIELDS: {extracted_fields}\n"
                    "DATABASE EVIDENCE: {evidence_context}\n\n"
                    "AUDIT TASK: You must strictly audit ALL 7 parameters (standard, voltage, conductor_material, conductor_class, csa, insulation_material, insulation_thickness). "
                    "Return one validation object for EACH parameter."
                ))
            ])

            chain = prompt | structured_llm   #type: ignore
            response = await chain.ainvoke({"evidence_context": evidence_context, "extracted_fields": extracted_fields.model_dump()})  #type: ignore
            
            logger.debug(f"Gemini Audit Response: {response}")
            return response  #type: ignore

        except Exception as e:
            logger.error(f"{constant.GEMINI} LLM invocation failed", exc_info=True)
            raise LLMInvocationError(f"{constant.GEMINI} LLM failed during cable validation") from e