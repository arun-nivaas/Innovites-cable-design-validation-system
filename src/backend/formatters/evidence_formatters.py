from typing import List
from src.backend.config.logger import logger
from src.backend.interfaces.IS_cable_validation import IEvidenceFormatter
from src.backend.schemas.cable_validation_schema import ValidationResponseSchema


class EvidenceFormatter(IEvidenceFormatter):
    
    def format(self, db_validations: List[ValidationResponseSchema]) -> str:
        logger.debug(f"Formatting {len(db_validations)} validation results")
        evidence_lines = ["### DATABASE VALIDATION EVIDENCE (IS 8130):"]
        for v in db_validations:
            icon = "✅" if v.validation_status == "PASS" else "⚠️"
            evidence_lines.append(
                f"{icon} Field: {v.field} | Status: {v.validation_status} | "
                f"Expected: {v.expected} | Comment: {v.comment}"
            )
        return "\n".join(evidence_lines)