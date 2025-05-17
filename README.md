# NEXUS Backend REST API

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

NEXUS is a unified platform designed to revolutionize customer service by leveraging the power of Large Language Models (LLMs). This repository contains the backend REST API for NEXUS, built to augment human customer support agents by automating repetitive tasks, instantly surfacing relevant information, and providing intelligent, context-aware response suggestions.

This API serves as the backbone for the NEXUS platform, handling document management, advanced search capabilities, and LLM-powered services for customer support agents.

## Core Features (MVP)

* **Document Management (CRUD):** Endpoints to Create, Read, Update, and Delete documents that form the knowledge base for customer support.
* **Natural Language Search (US1):** Allows customer support agents to search through company documentation using natural language queries to find accurate information quickly.
* **Automated Summarization (US2):** Provides functionality to automatically summarize long texts, such as customer emails or chat transcripts, enabling agents to grasp core issues rapidly.
* **Intelligent Response Suggestions (US3):** Generates relevant response suggestions based on customer queries and an analysis of relevant documentation, improving agent response time and consistency.

## Technology Stack

* **Python 3.11+:** Core programming language.
* **FastAPI:** High-performance web framework for building APIs.
* **Pydantic:** Data validation and settings management.
* **Uvicorn:** ASGI server for running the FastAPI application.
* **LLM Integration:** Designed for integration with LLM providers like OpenAI and Google Gemini (currently uses placeholder services).
* **Database:** Utilizes an in-memory placeholder database for the hackathon MVP. Configurable for production-grade databases (e.g., PostgreSQL, MySQL) via environment variables.
* **Docker:** Containerization for development and deployment.

## Prerequisites

* Python 3.11 or higher
* `pip` (Python package installer)
* Git (for cloning the repository)
* Docker (optional, for containerized setup)

## Getting Started

### 1. Clone the Repository

```bash
git clone [https://github.com/ahleksu/nexus-be.git](https://github.com/ahleksu/nexus-be.git)
cd nexus-be
```

### 2. Set Up a Virtual Environment

It's highly recommended to use a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:

```bash
.\venv\Scripts\activate
```

- On macOS and Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory by copying the example file:

```bash
# For Windows (Command Prompt)
copy .env.example .env

# For Windows (PowerShell)
Copy-Item .env.example .env

# For macOS/Linux
cp .env.example .env
```
Now, edit the .env file and provide the necessary configuration values. Key variables include:

```markdown
PROJECT_NAME="NEXUS API"
PROJECT_VERSION="0.1.0"
ENVIRONMENT="development" # or "production"

# Placeholder for actual database URL
DATABASE_URL="sqlite:///./test_db.db" # Example for a local SQLite file (update as needed)

# API Keys for LLM Services (replace with your actual keys if using real services)
OPENAI_API_KEY="your_openai_api_key_here"
GEMINI_API_KEY="your_google_gemini_api_key_here"

# CORS Origins (adjust as needed for your frontend)
# Example: ALLOWED_ORIGINS='["http://localhost:3000", "[http://127.0.0.1:3000](http://127.0.0.1:3000)"]'
ALLOWED_ORIGINS='["*"]' # Allows all origins for development, be more specific for production
```

**Note**: For the hackathon, the LLM services are placeholders and may not require actual API keys to run the basic API. The DATABASE_URL is also set up for a simple in-memory store for the current version.

## Running the Application

### Using Uvicorn (Development)

To run the FastAPI application with live reloading for development:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be accessible at http://127.0.0.1:8000 or http://localhost:8000.

### Accessing API Documentation

Once the server is running, you can access the interactive API documentation (Swagger UI) at: `http://localhost:8000/docs`

Alternative documentation (ReDoc) is available at: `http://localhost:8000/redoc`

You can also check the API status at: `http://localhost:8000/status`

## API Endpoints

The API provides endpoints for:

- Document Management: `/api/v1/documents/`
    - POST /: Create a new document.
    - GET /: Retrieve all documents.
    - GET /{doc_id}: Retrieve a specific document.
    - PUT /{doc_id}: Update a document.
    - DELETE /{doc_id}: Delete a document.

- Document Search: `/api/v1/documents/search/`
    - POST /: Search documents based on a natural language query.

- LLM Services (Conceptual for MVP, using placeholders):
    - /api/v1/llm/summarize/: Endpoint for text summarization.
    - /api/v1/llm/suggest-response/: Endpoint for generating response suggestions.

For detailed information on request/response schemas and to try out the endpoints, please refer to the `/docs` URL when the application is running.

## Docker Support

You can build and run the application using Docker.

1. Build the Docker Image
From the project root directory:

```bash
docker build -t nexus-backend-api .
```

2. Run the Docker Container

```bash
docker run -d -p 8000:8000 --name nexus-api-container --env-file .env nexus-backend-api
```

- -d: Run in detached mode.
- -p 8000:8000: Map port 8000 of the host to port 8000 of the container.
- --name nexus-api-container: Assign a name to the container.
- --env-file .env: Load environment variables from the .env file.

## Project Structure

```
nexus-be/
├── app/
│   ├── main.py             # FastAPI app initialization & root endpoints
│   ├── api/                # API versioning and endpoint definitions
│   │   └── v1/
│   │       └── endpoints/  # Resource-specific endpoints (e.g., documents.py)
│   ├── core/               # Configuration (e.g., config.py)
│   ├── schemas/            # Pydantic models for data validation & serialization
│   ├── services/           # Business logic (e.g., document_service.py, llm_service.py)
│   └── db/                 # Database models, session management (currently placeholders)
├── .env.example            # Example environment variables
├── .gitignore              # Files and directories to ignore in Git
├── Dockerfile              # Instructions for building the Docker image
└── requirements.txt        # Python dependencies
```