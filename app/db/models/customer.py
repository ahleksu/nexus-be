from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.call_session import CallSession
from app.db.models.company import Company


class Customer(SQLModel, table=True):
    customer_id: Optional[int] = Field(default=None, primary_key=True)
    company_id: Optional[int] = Field(default=None, foreign_key="company.company_id", index=True)
    customer_name: str = Field(..., max_length=255, index=True)
    customer_contact_no: Optional[str] = Field(default=None, max_length=50, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    company: Optional["Company"] = Relationship(back_populates="customers")
    call_sessions: List["CallSession"] = Relationship(back_populates="customer", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, customer_name='{self.customer_name}')>"


