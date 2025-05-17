from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.agent import Agent
from app.db.models.agent_kpi import AgentKpi
from app.db.models.call_transcription import CallTranscription
from app.db.models.company import Company
from app.db.models.customer import Customer


class CallSessionStatus(str, Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    COMPLETED = "completed"
    MISSED = "missed"
    FAILED = "failed"

class CallSession(SQLModel, table=True):
    call_session_id: Optional[int] = Field(default=None, primary_key=True)
    company_id: Optional[int] = Field(default=None, foreign_key="company.id", index=True)
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id", index=True)
    agent_id: Optional[int] = Field(default=None, foreign_key="agent.agent_id", index=True)

    status: Optional[CallSessionStatus] = Field(default=None)
    duration: Optional[int] = Field(default=None)

    # Python-side timestamps only
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships (make sure the other models have matching back_populates)
    company: Optional["Company"] = Relationship(back_populates="call_sessions_company")
    customer: Optional["Customer"] = Relationship(back_populates="call_sessions")
    agent: Optional["Agent"] = Relationship(back_populates="call_sessions")
    kpis: List["AgentKpi"] = Relationship(back_populates="call_session", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    transcriptions: List["CallTranscription"] = Relationship(back_populates="call_session", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def __repr__(self):
        return (
            f"<CallSession("
            f"id={self.call_session_id}, status={self.status}, "
            f"company_id={self.company_id})>"
        )

