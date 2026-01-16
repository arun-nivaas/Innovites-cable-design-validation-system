from pydantic import BaseModel, Field
from typing import Optional, List, Union
from src.backend.config.enums import ConductorMaterial, ValidationStatus


class ConductorSpec(BaseModel):
    
    sl_no: str = Field(..., description="Serial number identifier (e.g., 'i)', 'ii)', etc.)")
    nominal_cross_sectional_area: Union[int, float] = Field(..., description="Nominal cross-sectional area in mm²")
    min_wires_circular_cu: Optional[int] = Field(None, description="Minimum number of wires for circular copper conductor (non-compacted)")
    min_wires_circular_al: Optional[Union[int, str]] = Field(None, description="Minimum number of wires for circular aluminium conductor (non-compacted)")
    min_wires_compacted_cu: Optional[int] = Field(None, description="Minimum number of wires for circular compacted or shaped copper conductor")
    min_wires_compacted_al: Optional[Union[int, str]] = Field(None, description="Minimum number of wires for circular compacted or shaped aluminium conductor")
    max_resistance_cu_plain: float = Field(..., description="Maximum resistance at 20°C for copper conductor with plain wires (Ω/km)")
    max_resistance_cu_tinned: float = Field(..., description="Maximum resistance at 20°C for copper conductor with tinned wires (Ω/km)")
    max_resistance_al: Optional[float] = Field(None, description="Maximum resistance at 20°C for aluminium conductor (Ω/km)")
    note: Optional[str] = Field(None, description="Additional notes for this row")


class ConductorTable(BaseModel):
    
    table_number: int = Field(..., description="Table identification number")
    table_title: str = Field(..., description="Title of the table")
    reference_clauses: str = Field(..., description="Reference clauses from the standard")
    columns: List[str] = Field(..., description="List of column headers")
    rows: List[ConductorSpec] = Field(..., description="List of conductor specification rows")
    footnotes: List[str] = Field(default_factory=list, description="Footnotes for the table")
    notes: List[str] = Field(default_factory=list, description="General notes for the table")


class ConductorData(BaseModel):
    
    tables: List[ConductorTable] = Field(..., description="List of conductor specification tables")


class ValidationRequest(BaseModel):
    csa_mm2: float = Field(..., gt=0)
    material: ConductorMaterial
    measured_resistance: float = Field(..., ge=0)

class ValidationResult(BaseModel):
    status: ValidationStatus
    message: str
    expected_max: Optional[float] = None
    measured: Optional[float] = None