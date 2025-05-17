from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.api.v1.endpoints import documents as documents_v1, helloGemini
from app.core.config import settings
from app.core.database import engine


def init_db():
    if settings.ENV == "development":
        SQLModel.metadata.create_all(engine)

init_db()
# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json", # Standard OpenAPI doc path
    description="""
NEXUS REST API for customer support augmentation.
This API provides endpoints for managing documents, searching information,
and leveraging LLM capabilities for summarization and response suggestions.
    """,
    contact={ # Optional contact info for docs
        "name": "TENEXT.AI Hackathon Team",
        "url": "http://example.com/contact", # Replace with actual URL
        "email": "devteam@example.com",     # Replace with actual email
    },
    license_info={ # Optional license info for docs
        "name": "Apache 2.0", # Or your chosen license
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)

# CORS Middleware: Allows your Next.js frontend (on a different port/domain) to access the API.
# IMPORTANT: Adjust origins for production environments.
# Using ["*"] is permissive and generally okay for local development or internal APIs.
origins = [
    "http://localhost",       # Common local origin
    "http://localhost:3000",  # Default Next.js dev port
    "http://127.0.0.1:3000", # Another way Next.js dev might be accessed

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Specific origins allowed
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all standard HTTP methods
    allow_headers=["*"],    # Allows all headers
)

# Include API routers
# All document-related endpoints will be prefixed with /api/v1/documents
app.include_router(
    documents_v1.router,
    prefix=f"{settings.API_V1_STR}/documents",
    tags=["Documents & LLM Features"] # Tag for grouping in Swagger UI
)

app.include_router(helloGemini.router)

# Root endpoint for basic API health check or welcome message
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint of the NEXUS API.
    Provides a welcome message and a link to the documentation.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} - Version {settings.PROJECT_VERSION}",
        "documentation_url": "/docs" # FastAPI's default Swagger UI
    }

# A simple status endpoint within your API version prefix
@app.get(f"{settings.API_V1_STR}/status", tags=["Health Check"])
async def get_api_status():
    """
    Provides a simple status check for the API, confirming it's operational.
    """
    return {"status": "NEXUS API v1 is up and running!"}

# Placeholder for application startup/shutdown events (e.g., init DB connections, ML models)
# @app.on_event("startup")
# async def on_startup():
#     print("NEXUS API starting up...")
#     # PlaceholderDBDocument.initialize_dummy_data() # Ensure dummy data if using in-memory store
#     # Initialize database connection pools, load ML models, etc.
#
# @app.on_event("shutdown")
# async def on_shutdown():
#     print("NEXUS API shutting down...")
#     # Clean up resources, close database connections, etc.