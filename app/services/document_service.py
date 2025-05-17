import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import Depends # <<<<<<<<<<<< ADDED THIS IMPORT
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse,
    DocumentSearchQuery, DocumentSearchResultItem, DocumentSearchResponse
)
from app.db.models.document_model import PlaceholderDBDocument # Using placeholder DB model
from app.services.llm_service import LLMService, get_llm_service # For potential future use & dependency
from app.db.session import get_db_placeholder # For db dependency

class DocumentService:
    def __init__(self, db_session_placeholder, llm_service: Optional[LLMService] = None):
        # In a real app, db_session would be an actual DB session (e.g., SQLAlchemy session)
        self.db = db_session_placeholder # Placeholder for actual DB session
        self.llm_service = llm_service # Optional LLM service for advanced features

    async def create_document(self, doc_in: DocumentCreate) -> DocumentResponse:
        print(f"DocumentService: Creating document titled '{doc_in.title}'")
        # In a real app, you'd use self.db to interact with the database
        # Example: new_doc_orm = DocumentModel(**doc_in.model_dump(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        # self.db.add(new_doc_orm)
        # self.db.commit()
        # self.db.refresh(new_doc_orm)
        # return DocumentResponse.from_orm(new_doc_orm)
        created_doc_model = PlaceholderDBDocument.create(self.db, doc_in)
        return DocumentResponse.model_validate(created_doc_model) # Pydantic v2

    async def get_document_by_id(self, doc_id: uuid.UUID) -> Optional[DocumentResponse]:
        print(f"DocumentService: Retrieving document with ID: {doc_id}")
        doc_model = PlaceholderDBDocument.get_by_id(self.db, doc_id)
        if doc_model:
            return DocumentResponse.model_validate(doc_model)
        return None

    async def get_all_documents(self, skip: int = 0, limit: int = 10) -> List[DocumentResponse]:
        print(f"DocumentService: Retrieving all documents (skip={skip}, limit={limit})")
        doc_models = PlaceholderDBDocument.get_all(self.db, skip=skip, limit=limit)
        return [DocumentResponse.model_validate(doc) for doc in doc_models]

    async def update_document(self, doc_id: uuid.UUID, doc_update: DocumentUpdate) -> Optional[DocumentResponse]:
        print(f"DocumentService: Updating document with ID: {doc_id}")
        # For a real DB:
        # doc_orm = self.db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        # if not doc_orm: return None
        # update_data = doc_update.model_dump(exclude_unset=True) # Important for PATCH-like behavior
        # for key, value in update_data.items():
        #   setattr(doc_orm, key, value)
        # doc_orm.updated_at = datetime.utcnow()
        # self.db.commit()
        # self.db.refresh(doc_orm)
        # return DocumentResponse.from_orm(doc_orm)
        updated_doc_model = PlaceholderDBDocument.update(self.db, doc_id, doc_update)
        if updated_doc_model:
            return DocumentResponse.model_validate(updated_doc_model)
        return None

    async def delete_document(self, doc_id: uuid.UUID) -> bool:
        print(f"DocumentService: Deleting document with ID: {doc_id}")
        # For a real DB:
        # doc_orm = self.db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        # if not doc_orm: return False
        # self.db.delete(doc_orm)
        # self.db.commit()
        # return True
        return PlaceholderDBDocument.delete(self.db, doc_id)

    async def search_documents(self, search_query: DocumentSearchQuery) -> DocumentSearchResponse:
        """
        Placeholder search logic. (US1)
        For actual semantic search, this would involve:
        1. Getting an embedding for search_query.query using self.llm_service.
        2. Querying a vector database or performing similarity search against embeddings of stored documents.
        """
        print(f"DocumentService: Searching documents with query '{search_query.query}'")
        # Basic keyword matching for placeholder
        all_docs = PlaceholderDBDocument.get_all(self.db, limit=1000) # Get all for local filtering
        
        results: List[DocumentSearchResultItem] = []
        query_lower = search_query.query.lower()

        for doc_model in all_docs:
            if query_lower in doc_model.title.lower() or query_lower in doc_model.content.lower():
                # Simulate a relevance score
                score = 0.75 if query_lower in doc_model.title.lower() else 0.5
                if query_lower in doc_model.content.lower(): # Boost if also in content
                    score +=0.1
                
                results.append(DocumentSearchResultItem(
                    id=doc_model.id,
                    title=doc_model.title,
                    content_snippet=doc_model.content[:150] + "..." if len(doc_model.content) > 150 else doc_model.content,
                    source=doc_model.source,
                    score=min(score, 1.0) # Cap score at 1.0
                ))
        
        # Sort by score (descending) and limit
        results.sort(key=lambda r: r.score, reverse=True)
        final_results = results[:search_query.top_k]

        return DocumentSearchResponse(query_received=search_query.query, results=final_results)


# FastAPI Dependency provider for DocumentService
def get_document_service(
    db_session_placeholder = Depends(get_db_placeholder), # Corrected: Depends is now imported
    llm_service: LLMService = Depends(get_llm_service)    # Corrected: Depends is now imported
):
    return DocumentService(db_session_placeholder=db_session_placeholder, llm_service=llm_service)