from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class CableDesignSchema(BaseModel):
    standard: Optional[str] = Field(None, examples=["IEC 60502-1"])
    voltage: Optional[str] = Field(None, examples=["0.6/1 kV"])
    conductor_material: Optional[str] = Field(None, examples=["Cu"])
    conductor_class: Optional[str] = Field(None, examples=["Class 2"])
    csa: Optional[float] = Field(None, examples=[10.0])
    insulation_material: Optional[str] = Field(None, examples=["PVC"])
    insulation_thickness: Optional[float] = Field(None, examples=[1.0])

class ValidationResponseSchema(BaseModel):
    field: str = Field(..., examples=["insulation_thickness"])
    status: Literal["PASS", "WARN", "FAIL"]
    expected: Optional[str] = Field(None, examples=["≈ 1.0 mm"])
    comment: str = Field(...,examples=["Consistent with typical IEC expectations for PVC insulated 10 mm² LV cable."])

class Confidence(BaseModel):
    overall: float = Field(..., ge=0.0, le=1.0, examples=[0.91])

class LLMResponseSchema(BaseModel):

    is_out_of_scope: bool = Field(..., description="Set to true if the input text is not a cable design or is completely unrelated to IEC standards.")
  
    fields: Optional[CableDesignSchema] = None
    validation: Optional[List[ValidationResponseSchema]] = Field(default_factory=list)
    confidence: Optional[Confidence] = None
    
    out_of_scope_explanation: Optional[str] = Field(
        None, 
        description="Explain why the input is out of scope (e.g., 'Input is about medical advice, not cables')."
    )

class DesignValidationRequest(BaseModel):
    input: str = Field(..., min_length=1, description="Cable design input to validate")
