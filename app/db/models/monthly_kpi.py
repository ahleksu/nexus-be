from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.agent import Agent
from app.db.models.call_session import CallSession


class MonthlyKpi(SQLModel, table=True):
    kpi_id: Optional[int] = Field(default=None, primary_key=True)
    call_session_id: Optional[int] = Field(default=None, foreign_key="call_sessions.call_session_id", index=True)
    agent_id: int = Field(foreign_key="agent.agent_id", index=True)

    grade: Optional[float] = Field(default=None)
    summary: Optional[str] = Field(default=None)
    field_data: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    call_session_example: Optional["CallSession"] = Relationship()
    agent: Optional["Agent"] = Relationship(back_populates="monthly_kpis")

    def __repr__(self):
        return f"<MonthlyKpi(kpi_id={self.kpi_id}, agent_id={self.agent_id})>"
