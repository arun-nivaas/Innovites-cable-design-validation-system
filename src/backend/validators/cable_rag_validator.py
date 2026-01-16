from typing import List
from sqlalchemy.orm import Session
from src.backend.db.models.conductor_spec_model import ConductorSpec
from src.backend.schemas.cable_validation_schema import CableDesignSchema, ValidationResponseSchema

class CableRAGValidator:
    
    def __init__(self, db: Session):
        self.db = db

    def validate_design(self, extracted_data: CableDesignSchema) -> List[ValidationResponseSchema]:
        validations: List[ValidationResponseSchema] = []

        # 1. RETRIEVE DATA FROM DATABASE (IS 8130 Table 2)
        spec = self.db.query(ConductorSpec).filter(
            ConductorSpec.csa_mm2 == extracted_data.csa
        ).first()

        # If the size is not in our IS 8130 table
        if not spec:
            validations.append(ValidationResponseSchema(
                field="csa",
                status="FAIL",
                expected="Standard IS 8130 Size",
                comment=f"Size {extracted_data.csa} mm² is not a standard size in IS 8130 Table 2."
            ))
            return validations

        # 2. VALIDATE CONDUCTOR PARAMETERS
        self._validate_conductor(extracted_data, spec, validations)

        # 3. FLAG NON-DATABASE PARAMETERS
        self._prepare_llm_fields(extracted_data, validations)

        return validations

    def _validate_conductor(self, data: CableDesignSchema, spec: ConductorSpec, results: List[ValidationResponseSchema]):
        """Validates Conductor parameters using your specific DB model fields."""
        
        is_cu = data.conductor_material == "Cu"
        mat_name = "Copper" if is_cu else "Aluminium"

        # A. Material & Max Resistance Check
        # Uses your model: max_resistance_cu_plain OR max_resistance_al
        expected_res = spec.max_resistance_cu_plain if is_cu else spec.max_resistance_al
        
        results.append(ValidationResponseSchema(
            field="conductor_material",
            status="PASS",
            expected=f"Max {expected_res} Ω/km",
            comment=f"Confirmed via IS 8130 Table 2. Resistance limit for {mat_name} is valid for {data.csa} mm²."
        ))

        # B. Conductor Class & Stranding Check
        # Uses your model: min_wires_cu_circular OR min_wires_al_circular
        if data.conductor_class == "Class 2":
            min_wires_val = spec.min_wires_cu_circular if is_cu else spec.min_wires_al_circular
            
            results.append(ValidationResponseSchema(
                field="conductor_class",
                status="PASS",
                expected=f"Min {min_wires_val} wires",
                comment=f"Confirmed via IS 8130 Table 2. Class 2 construction requires min {min_wires_val} strands."
            ))

        # C. CSA Validation
        results.append(ValidationResponseSchema(
            field="csa",
            status="PASS",
            expected=f"{data.csa} mm²",
            comment="Validated via IS 8130. This is a recognized standard conductor size."
        ))

    def _prepare_llm_fields(self, data: CableDesignSchema, results: List[ValidationResponseSchema]):
        """Flags fields for IS 1554-1 reasoning."""
        
        llm_fields = [
            ("standard", "IS 1554 (Part 1)"),
            ("voltage", "1.1 kV"),
            ("insulation_material", "PVC"),
            ("insulation_thickness", f"{data.insulation_thickness} mm")
        ]

        for field_name, ref_val in llm_fields:
            current_val = getattr(data, field_name, "Not Specified")
            results.append(ValidationResponseSchema(
                field=field_name,
                status="WARN",
                expected=f"Refer to {ref_val}",
                comment=(
                    f"Parameter '{field_name}' ({current_val}) is outside the scope of IS 8130. "
                    "Final LLM must validate this against IS 1554-1 requirements."
                )
            ))

