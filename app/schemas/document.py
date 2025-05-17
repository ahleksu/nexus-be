from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=150, example="API Best Practices")
    content: str = Field(..., example="Detailed content about API design...")
    source: Optional[str] = Field(None, max_length=100, example="Internal Wiki")

class DocumentCreate(DocumentBase):
    pass # Inherits fields from DocumentBase

class DocumentUpdate(BaseModel): # Allow partial updates
    title: Optional[str] = Field(None, min_length=3, max_length=150, example="Updated API Guide")
    content: Optional[str] = Field(None, example="Updated content with new sections...")
    source: Optional[str] = Field(None, max_length=100, example="External Blog Post")

class DocumentInDBBase(DocumentBase):
    id: uuid.UUID = Field(..., example=uuid.uuid4())
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # owner_id: Optional[int] = None # Example if you add user ownership

    class Config:
        from_attributes = True # Pydantic V2 way to read data from ORM models

class DocumentResponse(DocumentInDBBase):
    pass # This will be the model for single document responses

class DocumentSearchQuery(BaseModel):
    query: str = Field(..., example="how to build an API")
    top_k: int = Field(default=5, ge=1, le=20, example=3)

class DocumentSearchResultItem(BaseModel):
    id: uuid.UUID
    title: str
    content_snippet: str
    source: Optional[str] = None
    score: float = Field(..., example=0.85)
    # You might add other fields like created_at, updated_at if relevant for search results
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentSearchResponse(BaseModel):
    query_received: str
    results: List[DocumentSearchResultItem]