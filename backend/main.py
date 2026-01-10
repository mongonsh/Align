"""
Align - FastAPI Application
AI-Powered Mockup Generator with Concept-Based Architecture
Enhanced with hackathon features: collaboration, plugins, partner integration
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from concepts import (
    UploadConcept, PromptConcept, MockupConcept, ExportConcept,
    FeatureRequestConcept, CollaborationConcept, PluginConcept, IntegrationConcept
)
from services import GeminiClient, VoiceClient
from api import router


# Global concept instances (singleton pattern for MVP)
upload_concept = None
prompt_concept = None
mockup_concept = None
export_concept = None
feature_request_concept = None
collaboration_concept = None
plugin_concept = None
integration_concept = None
voice_client = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize concepts on startup."""
    global (
        upload_concept, prompt_concept, mockup_concept, export_concept,
        feature_request_concept, collaboration_concept, plugin_concept,
        integration_concept, voice_client
    )

    # Initialize Gemini client
    gemini_client = GeminiClient()

    # Initialize Voice client
    voice_client = VoiceClient()

    # Initialize core concepts
    upload_concept = UploadConcept(upload_dir="uploads")
    prompt_concept = PromptConcept()
    mockup_concept = MockupConcept(gemini_client, mockup_dir="mockups")
    export_concept = ExportConcept()

    # Initialize hackathon concepts
    feature_request_concept = FeatureRequestConcept()
    collaboration_concept = CollaborationConcept()
    plugin_concept = PluginConcept()
    integration_concept = IntegrationConcept()

    print("✓ Core concepts initialized")
    print("✓ Hackathon concepts initialized")
    print("✓ Voice client initialized")
    print("✓ Align API ready with partner integration")

    yield

    # Cleanup
    print("Shutting down...")


app = FastAPI(
    title="Align API",
    description="AI-Powered Mockup Generator with Team Collaboration",
    version="2.0.0",
    lifespan=lifespan
)

# Enhanced CORS for partner team integration and Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000",
        "http://0.0.0.0:3000",
        # Chrome extension origins - allow all extension IDs for development
        "chrome-extension://*",
        # Partner team origins (configurable)
        *([origin.strip() for origin in os.getenv("PARTNER_ORIGINS", "").split(",") if origin.strip()])
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


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
        "description": "AI-Powered Mockup Generator with Voice Support",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "upload": "POST /api/upload",
            "prompt": "POST /api/prompt",
            "generate": "POST /api/generate",
            "mockup": "GET /api/mockup/{mockup_id}",
            "preview": "GET /api/mockup/{mockup_id}/preview",
            "export": "GET /api/export/{mockup_id}",
            "voice": {
                "speech_to_text": "POST /api/voice/speech-to-text",
                "text_to_speech": "POST /api/voice/text-to-speech",
                "voices": "GET /api/voice/voices",
                "mockup_summary": "POST /api/voice/mockup-summary/{mockup_id}"
            }
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
