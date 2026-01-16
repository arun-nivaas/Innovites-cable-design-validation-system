from sqlalchemy.orm import Session
from src.backend.db.models.ai_validation_model import AIValidation


def save_ai_validation(
    db: Session,
    request_id,
    raw_text: str,
    ai_result,
    meta: dict,
    error_message: str = None
) -> AIValidation:

    row = AIValidation(
        request_id=request_id,
        raw_input_text=raw_text,
        ai_response=ai_result,
        model_name=meta.get("model_name"),
        pipeline_type=meta.get("pipeline_type"),
        status=meta.get("status", "SUCCESS"),
        error_message=error_message
    )

    db.add(row)
    db.commit()
    db.refresh(row)
    return row