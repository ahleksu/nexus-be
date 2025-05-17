from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from app.db.models.company import Company


class Document(SQLModel, table=True):
    document_id: Optional[int] = Field(default=None, primary_key=True)
    company_id: Optional[int] = Field(default=None, foreign_key="company.id", index=True)
    document_name: str = Field(..., max_length=255)
    document_type: Optional[str] = Field(default=None, max_length=100)
    document_file: Optional[str] = Field(default=None, max_length=500)

    company: Optional["Company"] = Relationship(back_populates="documents")
