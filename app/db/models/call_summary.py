from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

class Role(str, Enum):
    AGENT = "agent"
    CUSTOMER = "customer"

class CallSummary(SQLModel, table=True):
    call_summary_id: Optional[int] = Field(default=None, primary_key=True)
    summary: Optional[str] = Field(default=None)
    role: Optional[Role] = Field(default=None)
    points: Optional[float] = Field(default=None)


    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # backref to CallSession; make sure CallSession.summary points back here
    call_session: Optional["CallSession"] = Relationship(back_populates="summary")





