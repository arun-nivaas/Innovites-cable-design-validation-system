from typing import Dict, Any
from src.backend.schemas.cable_validation_schema import GroqExtractionResponse
from src.backend.prompt_library.extraction.v1 import EXTRACTION_PROMPT

PROMPT_REGISTRY:Dict[str,Any] = {
    "extraction_v1": {
        "system_prompt": EXTRACTION_PROMPT,
        "model": "llama-3.1-8b-instant",
        "temperature": 0,
        "max_tokens": 200,
        "schema": GroqExtractionResponse
    }
}



def get_prompt_config(prompt_key: str) -> Dict[str, Any]:
    if prompt_key not in PROMPT_REGISTRY:
        raise ValueError(f"Unknown prompt version: {prompt_key}")
    return PROMPT_REGISTRY[prompt_key]