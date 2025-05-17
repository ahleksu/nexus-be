from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.company import Company
from app.db.models.resolution import Resolution


class Department(SQLModel, table=True):
    department_id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.company_id", index=True)
    department_name: str = Field(..., max_length=255, index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    company: Optional["Company"] = Relationship(back_populates="departments")
    resolutions: List["Resolution"] = Relationship(back_populates="department", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

    def __repr__(self):
        return f"<Department(department_id={self.department_id}, department_name='{self.department_name}', company_id={self.company_id})>"
