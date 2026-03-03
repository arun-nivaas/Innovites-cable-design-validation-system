from __future__ import annotations
import uuid
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, model_validator

# Cable Design Schema - Core parameters we care about for validation
class CableDesignSchema(BaseModel):
    standard: Optional[str] = Field(None, examples=["IS 8130"])
    voltage: Optional[str] = Field(None, examples=["0.6/1 kV"])
    conductor_material: Optional[Literal["Cu", "Al"]] = Field(None, examples=["Cu"])
    conductor_class: Optional[Literal["Class 1", "Class 2"]] = Field(None, examples=["Class 2"])
    csa: Optional[float] = Field(None, gt=0, examples=[10.0])
    insulation_material: Optional[str] = Field(None, examples=["PVC"])
    insulation_thickness: Optional[float] = Field(None, gt=0, examples=[1.0])

# Groq Extraction Response - Output from the field extraction step
class GroqExtractionResponse(BaseModel):
    is_out_of_scope: bool = Field(...,description="True if the input is unrelated to cable design or IS standards.",)
    out_of_scope_explanation: Optional[str] = Field(None,description="Required when is_out_of_scope is True. Explains why the input is out of scope.",)
    fields: Optional[CableDesignSchema] = Field(None,description="Extracted cable design fields. Required when is_out_of_scope is False.",)

    @model_validator(mode="after")
    def enforce_scope_contract(self) -> GroqExtractionResponse:
        if self.is_out_of_scope:
            if self.out_of_scope_explanation is None:
                raise ValueError("'out_of_scope_explanation' is required when 'is_out_of_scope' is True.")
            if self.fields is not None:
                raise ValueError("'fields' must be null when 'is_out_of_scope' is True.")
        else:
            if self.fields is None:
                raise ValueError("'fields' is required when 'is_out_of_scope' is False.")
            if self.out_of_scope_explanation is not None:
                raise ValueError("'out_of_scope_explanation' must be null when 'is_out_of_scope' is False.")
        return self

# Validation Response Schema - Output from the LLM audit step for each field
class ValidationResponseSchema(BaseModel):
    field: str = Field(..., min_length=2, examples=["insulation_thickness"])
    validation_status: Literal["PASS", "WARN", "FAIL"] = Field(...)
    expected: Optional[str] = Field(None, examples=["≈ 1.0 mm"])
    reasoning: str = Field(
        ...,
        description="Gemini's reasoning for why this field passed, warned, or failed validation. Must reference the relevant standard, expected range, or cross-field inconsistency.",
        examples=["IS 1554-1 Table 2 specifies 1.0 mm insulation thickness for 10 mm² PVC at 0.6/1 kV. Provided value matches exactly."]
    )
    comment: str = Field(
        ...,
        examples=["Consistent with typical IS expectations for PVC insulated 10 mm² LV cable."]
    )

    @model_validator(mode="after")
    def expected_required_on_fail(self) -> ValidationResponseSchema:
        if self.validation_status == "FAIL" and self.expected is None:
            raise ValueError(
                "'expected' must be provided when 'validation_status' is 'FAIL'."
            )
        return self


class Confidence(BaseModel):
    overall: float = Field(..., ge=0.0, le=1.0, examples=[0.91])

class GeminiValidationResponse(BaseModel):
    validation: List[ValidationResponseSchema]
    confidence: Confidence

# Scope Response Schemas - Discriminated by is_out_of_scope
class OutOfScopeResponse(BaseModel):
    is_out_of_scope: Literal[True] = True
    out_of_scope_explanation: str


class InScopeResponse(BaseModel):
    is_out_of_scope: Literal[False] = False
    fields: CableDesignSchema
    validation: List[ValidationResponseSchema]
    confidence: Confidence


# API Request Schemas - Discriminated by input_mode
class FreeTextInput(BaseModel):
    input_mode: Literal["free_text"]
    data: Dict[str, str] = Field(
        ...,
        description="Must contain a 'text' key with the raw input string.",
        examples=[{"text": "IS 8130 cable, 10 sqmm Cu Class 2, PVC insulation 1.0 mm, LV 0.6/1 kV"}],
    )

    @model_validator(mode="after")
    def validate_text_key(self) -> FreeTextInput:
        if "text" not in self.data or not self.data["text"].strip():
            raise ValueError("'data' must contain a non-empty 'text' key for free_text mode.")
        return self


class JsonInput(BaseModel):
    input_mode: Literal["json"]
    data: CableDesignSchema


class ManualInput(BaseModel):
    input_mode: Literal["manual"]
    data: CableDesignSchema


DesignValidationPostRequest = Annotated[
    Union[FreeTextInput, JsonInput, ManualInput],
    Field(discriminator="input_mode"),
]


# API Response Schemas - Discriminated by job_status and result structure
class DesignValidationPostResponse(BaseModel):
    request_id: uuid.UUID
    job_status: Literal["PENDING", "SUCCESS", "FAILED", "OUT_OF_SCOPE"]
    meta: Dict[str, Any] = Field(default_factory=dict)


class DesignValidationGetResponse(BaseModel):
    request_id: uuid.UUID
    job_status: Literal["PENDING", "SUCCESS", "FAILED", "OUT_OF_SCOPE"]
    result: Optional[
        Annotated[
            Union[OutOfScopeResponse, InScopeResponse],
            Field(discriminator="is_out_of_scope"),
        ]
    ] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def enforce_status_contract(self) -> DesignValidationGetResponse:
        status = self.job_status

        # result and error are mutually exclusive
        if self.result is not None and self.error is not None:
            raise ValueError("'result' and 'error' cannot both be set simultaneously.")

        # PENDING — nothing should be resolved yet
        if status == "PENDING":
            if self.result is not None or self.error is not None:
                raise ValueError("A PENDING job must not have 'result' or 'error'.")

        # SUCCESS — must have an InScopeResponse result
        elif status == "SUCCESS":
            if not isinstance(self.result, InScopeResponse):
                raise ValueError("A SUCCESS job must have an 'InScopeResponse' as 'result'.")

        # FAILED — must have an error string
        elif status == "FAILED":
            if self.error is None:
                raise ValueError("A FAILED job must have an 'error' message.")

        # OUT_OF_SCOPE — must have an OutOfScopeResponse result
        elif status == "OUT_OF_SCOPE":
            if not isinstance(self.result, OutOfScopeResponse):
                raise ValueError("An OUT_OF_SCOPE job must have an 'OutOfScopeResponse' as 'result'.")

        return self