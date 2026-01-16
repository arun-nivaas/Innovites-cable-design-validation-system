from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from ..database import Base

class AIValidation(Base):
    __tablename__ = "ai_validations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False)

    raw_input_text = Column(Text, nullable=False)
    ai_response = Column(JSONB, nullable=True)

    model_name = Column(String(100))
    pipeline_type = Column(String(50))

    status = Column(String(20), default="SUCCESS")
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())