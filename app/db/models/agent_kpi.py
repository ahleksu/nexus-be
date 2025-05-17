from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.agent import Agent

class AgentKpi(SQLModel, table=True):

    kpi_id: Optional[int] = Field(default=None, primary_key=True, index=True)


    grade: Optional[float] = Field(default=None)
    summary: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    updated: datetime = Field(default_factory=datetime.utcnow)

    # relationships
    call_session: Optional["CallSession"] = Relationship(back_populates="kpi")
    agent: Optional["Agent"] = Relationship(back_populates="kpi")
