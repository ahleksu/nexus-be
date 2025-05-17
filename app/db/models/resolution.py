from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.agent import Agent
from app.db.models.company import Company
from app.db.models.department import Department


class Resolution(SQLModel, table=True):
    resolution_id: Optional[int] = Field(default=None, primary_key=True)

    company_id: int = Field(foreign_key="company.company_id", index=True)
    agent_id: Optional[int] = Field(default=None, foreign_key="agent.agent_id", index=True)
    department_id: Optional[int] = Field(default=None, foreign_key="department.department_id", index=True)

    rank: Optional[float] = Field(default=None, index=True)
    title: Optional[str] = Field(default=None, max_length=255)
    resolution: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    company: Optional["Company"] = Relationship(back_populates="resolutions")
    agent: Optional["Agent"] = Relationship(back_populates="resolutions")
    department: Optional["Department"] = Relationship(back_populates="resolutions")

    def __repr__(self):
        return f"<Resolution(resolution_id={self.resolution_id}, title='{self.title}')>"
