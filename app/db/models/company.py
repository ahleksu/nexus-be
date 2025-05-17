
from typing import Optional,List
from sqlmodel import SQLModel,Field,Relationship

from app.db.models.agent import Agent


class Company(SQLModel, table=True):
    company_id: Optional[int] = Field(default=None, primary_key=True)
    company_name: str
    email: str
    field: str
    password: str

    agents: List[Agent] = Relationship(back_populates="company")
    documents: List["Document"] = Relationship(back_populates="company")