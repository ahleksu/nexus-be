from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class Agent(SQLModel, table=True):
    agent_id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.company_id")

    agent_name: str
    email: str
    password: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None
    updated: datetime = Field(default_factory=datetime.utcnow)

    company: Optional["Company"] = Relationship(back_populates="agents")




