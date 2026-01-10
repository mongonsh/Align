"""
Align - FastAPI Application
AI-Powered Mockup Generator with Concept-Based Architecture
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from concepts import UploadConcept, PromptConcept, MockupConcept, ExportConcept
from services import GeminiClient
from api import router


# Global concept instances (singleton pattern for MVP)
upload_concept = None
prompt_concept = None
mockup_concept = None
export_concept = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize concepts on startup."""
    global upload_concept, prompt_concept, mockup_concept, export_concept

    # Initialize Gemini client
    gemini_client = GeminiClient()

    # Initialize concepts
    upload_concept = UploadConcept(upload_dir="uploads")
    prompt_concept = PromptConcept()
    mockup_concept = MockupConcept(gemini_client, mockup_dir="mockups")
    export_concept = ExportConcept()

    print("✓ Concepts initialized")
    print("✓ Align API ready")

    yield

    # Cleanup
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Align API",
    description="AI-Powered Mockup Generator - Align customer and engineer expectations",
    version="1.0.0",
    lifespan=lifespan
)

# Get allowed origins from environment or use defaults
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "http://frontend:3000",
    "http://0.0.0.0:3000",
]

# CORS middleware with comprehensive configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
    expose_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Align API",
        "version": "1.0.0",
        "description": "AI-Powered Mockup Generator",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "upload": "POST /api/upload",
            "prompt": "POST /api/prompt",
            "generate": "POST /api/generate",
            "mockup": "GET /api/mockup/{mockup_id}",
            "preview": "GET /api/mockup/{mockup_id}/preview",
            "export": "GET /api/export/{mockup_id}",
        },
        "architecture": "Concept-based design (Daniel Jackson)",
        "hackathon": "De-Vibed Hackathon",
        "sponsor": "CommandCenter (cc.dev)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
