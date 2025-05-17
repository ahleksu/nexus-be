from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from typing import List
import uuid

from app.schemas.document import (
    DocumentResponse, DocumentCreate, DocumentUpdate,
    DocumentSearchQuery, DocumentSearchResponse
)
from app.services.document_service import DocumentService, get_document_service
from app.services.llm_service import LLMService, get_llm_service # For summarization/suggestion

router = APIRouter()

# CRUD Endpoints for Documents
@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
    description="Adds a new document to the system. The ID and timestamps are auto-generated."
)
async def create_new_document(
    doc_in: DocumentCreate,
    doc_service: DocumentService = Depends(get_document_service)
):
    created_doc = await doc_service.create_document(doc_in=doc_in)
    return created_doc

@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Get a specific document by ID",
    responses={404: {"description": "Document not found"}}
)
async def read_document_by_id(
    doc_id: uuid.UUID,
    doc_service: DocumentService = Depends(get_document_service)
):
    document = await doc_service.get_document_by_id(doc_id=doc_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document

@router.get(
    "/",
    response_model=List[DocumentResponse],
    summary="List all documents with pagination"
)
async def read_all_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of documents to return"),
    doc_service: DocumentService = Depends(get_document_service)
):
    documents = await doc_service.get_all_documents(skip=skip, limit=limit)
    return documents

@router.put(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Update an existing document by ID",
    responses={404: {"description": "Document not found"}}
)
async def update_existing_document(
    doc_id: uuid.UUID,
    doc_update: DocumentUpdate, # Note: Pydantic model for update allows partial updates
    doc_service: DocumentService = Depends(get_document_service)
):
    updated_doc = await doc_service.update_document(doc_id=doc_id, doc_update=doc_update)
    if not updated_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found or update failed")
    return updated_doc

@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document by ID",
    responses={404: {"description": "Document not found"}}
)
async def delete_existing_document(
    doc_id: uuid.UUID,
    doc_service: DocumentService = Depends(get_document_service)
):
    success = await doc_service.delete_document(doc_id=doc_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    # No content returned for 204

# Search Endpoint (US1)
@router.post(
    "/search",
    response_model=DocumentSearchResponse,
    summary="Search documents using a query string (US1)",
    description="Performs a search over documents. Placeholder uses basic keyword matching."
)
async def search_documents_endpoint(
    search_params: DocumentSearchQuery = Body(...),
    doc_service: DocumentService = Depends(get_document_service)
):
    search_results = await doc_service.search_documents(search_query=search_params)
    return search_results

# LLM-powered Endpoints (Placeholders for US2, US3)
@router.post(
    "/summarize-text",
    response_model=str, # Assuming summary is a string
    summary="Summarize provided text (US2 - LLM Placeholder)",
    description="Takes a string of text and returns a summary. Uses a placeholder LLM service."
)
async def summarize_text_content(
    text_to_summarize: str = Body(..., media_type="text/plain", example="This is a long piece of text that needs to be summarized concisely."),
    llm_service: LLMService = Depends(get_llm_service)
):
    if not text_to_summarize.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Text content cannot be empty.")
    summary = await llm_service.summarize_text(text_to_summarize)
    return summary

@router.post(
    "/suggest-response",
    response_model=str, # Assuming suggestion is a string
    summary="Generate a response suggestion based on query and context (US3 - LLM Placeholder)",
    description="Takes a customer query and optional context document content to suggest a response. Uses placeholder LLM."
)
async def suggest_customer_response(
    customer_query: str = Body(..., embed=True, example="How do I reset my password?"),
    context_docs_content: List[str] = Body(None, embed=True, example=["Document 1 content...", "Document 2 content..."]),
    llm_service: LLMService = Depends(get_llm_service)
):
    if not customer_query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer query cannot be empty.")
    
    suggestion = await llm_service.generate_response_suggestion(
        query=customer_query,
        context_docs_content=context_docs_content if context_docs_content else []
    )
    return suggestion

# Note: For the US2 (summarize long customer emails/chat transcripts) that might involve fetching a document first,
# you could have an endpoint like /documents/{doc_id}/summarize
@router.get(
    "/{doc_id}/summarize",
    response_model=str,
    summary="Summarize a specific document's content (US2 - LLM Placeholder)",
    responses={404: {"description": "Document not found"}}
)
async def summarize_document_by_id(
    doc_id: uuid.UUID,
    doc_service: DocumentService = Depends(get_document_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    document = await doc_service.get_document_by_id(doc_id=doc_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if not document.content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document content is empty, cannot summarize.")
    
    summary = await llm_service.summarize_text(document.content)
    return summary