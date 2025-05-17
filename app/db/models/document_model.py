from typing import List, Optional
import uuid
from datetime import datetime

from app.schemas.document import DocumentCreate, DocumentUpdate

# This is a placeholder. For a real DB, you'd use SQLAlchemy models:
# from sqlalchemy import Column, String, Text, DateTime, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.ext.declarative import declarative_base
# Base = declarative_base()
# class Document(Base):
#     __tablename__ = "documents"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     title = Column(String, index=True, nullable=False)
#     content = Column(Text, nullable=False)
#     source = Column(String, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlaceholderDBDocument:
    """
    A mock in-memory representation of a Document for placeholder purposes.
    Replace with actual ORM model and database interactions.
    """
    _documents_store: dict[uuid.UUID, 'PlaceholderDBDocument'] = {}

    def __init__(self, title: str, content: str, source: Optional[str] = None, id: Optional[uuid.UUID] = None):
        self.id = id if id else uuid.uuid4()
        self.title = title
        self.content = content
        self.source = source
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @classmethod
    def create(cls, db_session_placeholder, doc_data: 'DocumentCreate') -> 'PlaceholderDBDocument':
        print(f"PlaceholderDB: Creating document '{doc_data.title}'")
        new_doc = cls(title=doc_data.title, content=doc_data.content, source=doc_data.source)
        cls._documents_store[new_doc.id] = new_doc
        return new_doc

    @classmethod
    def get_by_id(cls, db_session_placeholder, doc_id: uuid.UUID) -> Optional['PlaceholderDBDocument']:
        print(f"PlaceholderDB: Getting document by ID {doc_id}")
        return cls._documents_store.get(doc_id)

    @classmethod
    def get_all(cls, db_session_placeholder, skip: int = 0, limit: int = 10) -> List['PlaceholderDBDocument']:
        print(f"PlaceholderDB: Getting all documents (skip={skip}, limit={limit})")
        all_docs = list(cls._documents_store.values())
        return sorted(all_docs, key=lambda d: d.created_at, reverse=True)[skip : skip + limit]

    @classmethod
    def update(cls, db_session_placeholder, doc_id: uuid.UUID, doc_update_data: 'DocumentUpdate') -> Optional['PlaceholderDBDocument']:
        print(f"PlaceholderDB: Updating document ID {doc_id}")
        doc = cls._documents_store.get(doc_id)
        if doc:
            update_data = doc_update_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(doc, key, value)
            doc.updated_at = datetime.utcnow()
            return doc
        return None

    @classmethod
    def delete(cls, db_session_placeholder, doc_id: uuid.UUID) -> bool:
        print(f"PlaceholderDB: Deleting document ID {doc_id}")
        if doc_id in cls._documents_store:
            del cls._documents_store[doc_id]
            return True
        return False

    # Initialize with some dummy data for testing
    @classmethod
    def initialize_dummy_data(cls):
        if not cls._documents_store: # Only if empty
            cls.create(None, DocumentCreate(title="FastAPI Introduction", content="FastAPI is a modern, fast web framework.", source="FastAPI Docs"))
            cls.create(None, DocumentCreate(title="Next.js Basics", content="Next.js is a React framework for production.", source="Next.js Blog"))
            cls.create(None, DocumentCreate(title="REST API Design", content="Principles of designing good RESTful APIs.", source="Web Standards"))
            print("PlaceholderDB: Initialized with 3 dummy documents.")

PlaceholderDBDocument.initialize_dummy_data()