from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship




class InteractionMetric(SQLModel, table=True):
    interaction_metric_id: Optional[int] = Field(default=None, primary_key=True)


    internal_qa_score: Optional[float] = Field(default=None)
    csat_score: Optional[float] = Field(default=None)
    is_first_contact_resolution: Optional[bool] = Field(default=None)
    customer_sentiment: Optional[str] = Field(default=None)
    ai_generated_summary: Optional[str] = Field(default=None)

    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    call_session_id: int = Field(foreign_key="call_sessions.call_session_id", index=True)

    def __repr__(self):
        return f"<InteractionMetric(interaction_metric_id={self.interaction_metric_id}, call_session_id={self.call_session_id})>"
