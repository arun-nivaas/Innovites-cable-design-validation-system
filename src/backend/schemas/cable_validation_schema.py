import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Literal,Dict,Any

# Schemas for Cable Design Validation
class CableDesignSchema(BaseModel):
    standard: Optional[str] = Field(None, examples=["IS 1554-1"])
    voltage: Optional[str] = Field(None, examples=["0.6/1 kV"])
    conductor_material: Optional[Literal["Cu", "Al"]] = Field(None, examples=["Cu"])  # Constrained
    conductor_class: Optional[str] = Field(None, examples=["Class 2"])
    csa: Optional[float] = Field(None, gt=0, examples=[10.0])  # Must be positive
    insulation_material: Optional[str] = Field(None, examples=["PVC"])
    insulation_thickness: Optional[float] = Field(None, gt=0, examples=[1.0])  # Must be positive

class ValidationResponseSchema(BaseModel):
    field: str = Field(..., examples=["insulation_thickness"])
    validation_status: Literal["PASS", "WARN", "FAIL"]
    expected: Optional[str] = Field(None, examples=["≈ 1.0 mm"])
    comment: str = Field(...,examples=["Consistent with typical IS expectations for PVC insulated 10 mm² LV cable."])

class Confidence(BaseModel):
    overall: float = Field(..., ge=0.0, le=1.0, examples=[0.91])

# Response schema from LLM after processing input
class LLMResponseSchema(BaseModel):
    is_out_of_scope: bool = Field(..., description="Set to true if the input text is not a cable design or is completely unrelated to IS standards.")
    out_of_scope_explanation: str = Field(..., description="Explain why the input is out of scope (e.g., 'Input is about medical advice, not cables').")
    fields: CableDesignSchema = Field(..., description="Extracted cable design fields from the input text.")
    validation: List[ValidationResponseSchema] = Field(default_factory=list)
    confidence: Confidence = Field(..., description="Confidence scores for the extraction and validation results.")

# Post request and response schemas (execution/job creation)
class DesignValidationPostRequest(BaseModel):
    input_mode: Literal["free_text", "json", "manual"]
    data: Dict[str, Any] = Field(..., description="Input data for cable design validation.")

class DesignValidationPostResponse(BaseModel):
    request_id: uuid.UUID
    job_status: Literal["PENDING", "SUCCESS", "FAILED"]
    meta: Dict[str, Any] = Field(default_factory=dict)

# Get request and response schemas (fetching job result)
class DesignValidationGetResponse(BaseModel):
    request_id: uuid.UUID
    job_status: Literal["PENDING", "SUCCESS", "FAILED"]
    result: Optional[LLMResponseSchema] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)