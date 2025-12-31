from pydantic import SecretStr
from src.backend.config.logger import logger
from src.backend.config.settings import settings
from src.backend.schemas.cable_validation_schema import LLMResponseSchema
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable #type: ignore
from src.backend.prompt_library.system_prompt import SYSTEM_PROMPT

@traceable(name = "cable_design_validation")
class CableDesignValidator:
    def __init__(self):
      
        self.llm = ChatGoogleGenerativeAI(
            model = settings.gemini_model_name,
            temperature = 0,
            google_api_key = SecretStr(settings.google_api_key)
        )
        logger.info("CableDesignValidator initialized with Gemini")

    @traceable(name = "cable_design_validation_validate_method")
    async def validate(self, user_input: str) -> LLMResponseSchema:
        logger.info(f"Starting cable design validation: {user_input[:50]}...")

        try:
            structured_llm = self.llm.with_structured_output(LLMResponseSchema) #type: ignore

            prompt = ChatPromptTemplate.from_messages([ #type: ignore
                ("system", SYSTEM_PROMPT), 
                ("human", "{user_input}")
            ])

            chain = prompt | structured_llm   #type: ignore
            response = await chain.ainvoke({"user_input": user_input})  #type: ignore

            return response  #type: ignore

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        




        