"""
FastAPI routes implementing clean concept separation
Following the AFTER pattern from CLAUDE.md
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api")


class PromptRequest(BaseModel):
    image_id: str
    description: str


class GenerateRequest(BaseModel):
    image_id: str
    description: str
    requirements: Optional[dict] = None


class TextToSpeechRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload screenshot of current system.
    Uses UploadConcept only.
    """
    import main
    
    try:
        # Read file content
        content = await file.read()

        # Upload using UploadConcept
        metadata = await main.upload_concept.upload(content, file.filename)

        return {
            "image_id": metadata["image_id"],
            "preview_url": f"/api/image/{metadata['image_id']}",
            "metadata": {
                "filename": metadata["original_filename"],
                "size": metadata["size"],
                "width": metadata["width"],
                "height": metadata["height"],
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/prompt")
async def parse_prompt(request: PromptRequest):
    """
    Parse user's change description.
    Uses PromptConcept only.
    """
    import main

    try:
        # Parse intent using PromptConcept
        requirements = main.prompt_concept.parse_intent(request.description)

        return {
            "image_id": request.image_id,
            "requirements": requirements,
            "clarifications": requirements.get("clarifications", []),
            "summary": main.prompt_concept.get_summary()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@router.post("/generate")
async def generate_mockup(request: GenerateRequest):
    """
    Generate mockup from image and requirements.
    Clean separation: Upload -> Prompt -> Mockup -> Export
    """
    import main
    import traceback
    import logging

    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Starting mockup generation for image_id: {request.image_id}")
        
        # Step 1: Get image using UploadConcept
        logger.info("Step 1: Getting image bytes")
        image_bytes = await main.upload_concept.get_current(request.image_id)
        logger.info(f"Image bytes retrieved: {len(image_bytes)} bytes")

        # Step 2: Parse requirements using PromptConcept (if not provided)
        logger.info("Step 2: Parsing requirements")
        if request.requirements:
            requirements = request.requirements
        else:
            requirements = main.prompt_concept.parse_intent(request.description)
        logger.info(f"Requirements parsed: {requirements}")

        # Step 3: Generate mockup using MockupConcept
        logger.info("Step 3: Generating mockup with Gemini")
        mockup_data = await main.mockup_concept.generate(
            image_bytes=image_bytes,
            prompt=request.description,
            requirements=requirements
        )
        logger.info(f"Mockup generated successfully: {mockup_data['mockup_id']}")

        # Step 4: Prepare response using ExportConcept
        logger.info("Step 4: Preparing response")
        response = main.export_concept.prepare_response(
            mockup_html=mockup_data["html"],
            mockup_id=mockup_data["mockup_id"]
        )
        logger.info("Response prepared successfully")

        return response

    except ValueError as e:
        logger.error(f"ValueError in mockup generation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in mockup generation: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/mockup/{mockup_id}")
async def get_mockup(mockup_id: str):
    """
    Retrieve generated mockup.
    Uses MockupConcept only.
    """
    import main

    try:
        mockup = await main.mockup_concept.get_mockup(mockup_id)

        return {
            "mockup_id": mockup["mockup_id"],
            "html": mockup["html"],
            "created_at": mockup["generated_at"],
            "status": mockup["status"],
            "prompt": mockup["prompt"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.get("/mockup/{mockup_id}/preview")
async def preview_mockup(mockup_id: str):
    """
    Preview mockup as rendered HTML.
    """
    import main

    try:
        html = await main.mockup_concept.get_html(mockup_id)
        return HTMLResponse(content=html)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")


@router.get("/export/{mockup_id}")
async def export_mockup(mockup_id: str, format: str = "html"):
    """
    Export mockup for download.
    Uses MockupConcept and ExportConcept.
    """
    import main

    try:
        # Get mockup using MockupConcept
        mockup = await main.mockup_concept.get_mockup(mockup_id)

        # Export using ExportConcept
        if format == "zip":
            export_bytes = main.export_concept.export_with_assets(
                mockup_html=mockup["html"],
                mockup_id=mockup_id
            )
            filename = main.export_concept.get_filename(mockup_id, "zip")
            media_type = "application/zip"
        else:
            export_bytes = main.export_concept.export(
                mockup_html=mockup["html"],
                mockup_id=mockup_id,
                metadata=mockup
            )
            filename = main.export_concept.get_filename(mockup_id, "html")
            media_type = "text/html"

        return Response(
            content=export_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/image/{image_id}")
async def get_image(image_id: str):
    """
    Retrieve uploaded image.
    Uses UploadConcept only.
    """
    import main

    try:
        image_bytes = await main.upload_concept.get_current(image_id)
        return Response(content=image_bytes, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image retrieval failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Align API"}


@router.post("/voice/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Convert speech to text using speech recognition.
    Accepts audio files in various formats (webm, mp3, wav, etc.)
    """
    import main

    try:
        # Read audio content
        audio_content = await audio.read()
        
        # Determine audio format from filename
        audio_format = audio.filename.split('.')[-1] if audio.filename else 'webm'
        
        # Convert speech to text using VoiceClient
        text = await main.voice_client.speech_to_text(audio_content, audio_format)
        
        return {
            "text": text,
            "audio_format": audio_format,
            "filename": audio.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition failed: {str(e)}")


@router.post("/voice/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """
    Convert text to speech using ElevenLabs.
    Returns audio file as MP3.
    """
    import main

    try:
        # Generate speech using VoiceClient
        audio_bytes = await main.voice_client.text_to_speech(
            text=request.text,
            voice_id=request.voice_id
        )
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")


@router.get("/voice/voices")
async def get_voices():
    """
    Get list of available voices from ElevenLabs.
    """
    import main

    try:
        voices = await main.voice_client.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voices: {str(e)}")


@router.post("/voice/mockup-summary")
async def generate_mockup_summary(mockup_id: str):
    """
    Generate voice summary of a completed mockup.
    """
    import main

    try:
        # Get mockup details
        mockup = await main.mockup_concept.get_mockup(mockup_id)
        
        # Generate voice summary
        audio_bytes = await main.voice_client.generate_voice_summary(
            mockup_description=mockup["prompt"],
            changes_made="I've created an updated version of your interface with the requested changes."
        )
        
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=mockup_{mockup_id}_summary.mp3"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice summary generation failed: {str(e)}")


# ============================================================================
# HACKATHON FEATURES - Feature Requests, Collaboration, Plugins, Integration
# ============================================================================

class FeatureRequestCreate(BaseModel):
    title: str
    description: str
    category: str = "enhancement"
    priority: str = "medium"
    partner_team: Optional[str] = None


class CollaborationSessionCreate(BaseModel):
    mockup_id: str
    session_name: Optional[str] = None


class PluginInstall(BaseModel):
    plugin_metadata: dict
    plugin_package_url: Optional[str] = None


class IntegrationRegister(BaseModel):
    team_name: str
    api_endpoint: str
    integration_type: str
    permissions: List[str]
    webhook_url: Optional[str] = None


# Feature Requests API
@router.post("/feature-requests")
async def create_feature_request(request: FeatureRequestCreate):
    """Create a new feature request."""
    import main
    
    try:
        feature_request = await main.feature_request_concept.create_request(
            title=request.title,
            description=request.description,
            user_id="api_user",  # Would be from auth in production
            category=request.category,
            priority=request.priority,
            partner_team=request.partner_team
        )
        
        return feature_request
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create feature request: {str(e)}")


@router.get("/feature-requests")
async def list_feature_requests(
    status: Optional[str] = None,
    category: Optional[str] = None,
    partner_team: Optional[str] = None
):
    """List feature requests with filtering."""
    import main
    
    try:
        requests = main.feature_request_concept.list_requests(
            status=status,
            category=category,
            partner_team=partner_team
        )
        return {"requests": requests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list feature requests: {str(e)}")


@router.post("/feature-requests/{request_id}/vote")
async def vote_feature_request(request_id: str):
    """Vote for a feature request."""
    import main
    
    try:
        updated_request = await main.feature_request_concept.vote_request(
            request_id=request_id,
            user_id="api_user"
        )
        return updated_request
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to vote: {str(e)}")


# Collaboration API
@router.post("/collaboration/sessions")
async def create_collaboration_session(request: CollaborationSessionCreate):
    """Create a new collaboration session."""
    import main
    
    try:
        session = await main.collaboration_concept.create_session(
            mockup_id=request.mockup_id,
            created_by="api_user",
            session_name=request.session_name
        )
        
        return {
            "session_id": session.session_id,
            "mockup_id": session.mockup_id,
            "created_at": session.created_at.isoformat(),
            "participants": list(session.participants)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.post("/collaboration/sessions/{session_id}/join")
async def join_collaboration_session(session_id: str):
    """Join a collaboration session."""
    import main
    
    try:
        success = await main.collaboration_concept.join_session(
            session_id=session_id,
            user_id="api_user"
        )
        
        if success:
            return {"status": "joined", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Session not found or inactive")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to join session: {str(e)}")


@router.get("/collaboration/sessions/{session_id}")
async def get_collaboration_session(session_id: str):
    """Get collaboration session state."""
    import main
    
    try:
        session_state = await main.collaboration_concept.get_session_state(session_id)
        return session_state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


# Plugin System API
@router.get("/plugins")
async def list_plugins(active_only: bool = False):
    """List installed plugins."""
    import main
    
    try:
        plugins = main.plugin_concept.list_plugins(active_only=active_only)
        return {"plugins": plugins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list plugins: {str(e)}")


@router.post("/plugins/install")
async def install_plugin(file: UploadFile = File(...), metadata: str = "{}"):
    """Install a new plugin."""
    import main
    import json
    
    try:
        # Read plugin package
        plugin_package = await file.read()
        plugin_metadata = json.loads(metadata)
        
        result = await main.plugin_concept.install_plugin(
            plugin_package=plugin_package,
            plugin_metadata=plugin_metadata,
            user_id="api_user"
        )
        
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to install plugin: {str(e)}")


@router.post("/plugins/{plugin_id}/activate")
async def activate_plugin(plugin_id: str):
    """Activate a plugin."""
    import main
    
    try:
        result = await main.plugin_concept.activate_plugin(plugin_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate plugin: {str(e)}")


@router.post("/plugins/{plugin_id}/deactivate")
async def deactivate_plugin(plugin_id: str):
    """Deactivate a plugin."""
    import main
    
    try:
        result = await main.plugin_concept.deactivate_plugin(plugin_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate plugin: {str(e)}")


@router.delete("/plugins/{plugin_id}")
async def uninstall_plugin(plugin_id: str):
    """Uninstall a plugin."""
    import main
    
    try:
        result = await main.plugin_concept.uninstall_plugin(
            plugin_id=plugin_id,
            user_id="api_user"
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to uninstall plugin: {str(e)}")


# Partner Integration API
@router.post("/integration/register")
async def register_partner_team(request: IntegrationRegister):
    """Register a partner team for integration."""
    import main
    
    try:
        partner = await main.integration_concept.register_partner_team(
            team_name=request.team_name,
            api_endpoint=request.api_endpoint,
            integration_type=request.integration_type,
            permissions=request.permissions,
            webhook_url=request.webhook_url
        )
        
        return {
            "team_id": partner.team_id,
            "api_key": partner.api_key,
            "webhook_secret": partner.shared_secret,
            "status": "registered"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register partner: {str(e)}")


@router.post("/integration/register-extension")
async def register_chrome_extension(request: dict):
    """Register Chrome extension for partner team."""
    import main
    
    try:
        result = await main.integration_concept.register_chrome_extension(
            extension_id=request["extension_id"],
            team_id=request["team_id"],
            permissions=request["permissions"]
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register extension: {str(e)}")


@router.post("/integration/sync")
async def sync_state_with_partner(request: dict):
    """Synchronize state with partner team."""
    import main
    
    try:
        result = await main.integration_concept.sync_state_with_partner(
            team_id=request["team_id"],
            state_key=request["state_key"],
            state_data=request["state_data"],
            sync_type=request.get("sync_type", "update")
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync state: {str(e)}")


@router.post("/integration/webhook/{team_id}")
async def handle_partner_webhook(team_id: str, request: dict):
    """Handle incoming webhook from partner team."""
    import main
    
    try:
        # Get signature from headers (would be implemented with proper auth)
        signature = "dummy_signature"  # In production, get from X-Webhook-Signature header
        
        result = await main.integration_concept.handle_partner_webhook(
            team_id=team_id,
            event_type=request["event_type"],
            payload=request["data"],
            signature=signature
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to handle webhook: {str(e)}")


@router.get("/integration/stats")
async def get_integration_stats():
    """Get integration statistics."""
    import main
    
    try:
        stats = main.integration_concept.get_integration_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# Enhanced generate endpoint with plugin hooks
@router.post("/generate")
async def generate_mockup_enhanced(request: GenerateRequest):
    """
    Generate mockup with plugin system integration.
    Enhanced version that executes plugin hooks.
    """
    import main
    
    try:
        # Get image data
        image_metadata = main.upload_concept.get_current()
        if not image_metadata or image_metadata["image_id"] != request.image_id:
            raise HTTPException(status_code=404, detail="Image not found")

        # Read image file
        image_path = image_metadata["filepath"]
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # Execute before_mockup_generate hook
        hook_data = await main.plugin_concept.execute_hook(
            "before_mockup_generate",
            image_bytes=image_bytes,
            prompt=request.description,
            requirements=request.requirements or {}
        )
        
        # Use potentially modified data from hooks
        modified_image_bytes = hook_data.get("image_bytes", image_bytes)
        modified_prompt = hook_data.get("prompt", request.description)
        modified_requirements = hook_data.get("requirements", request.requirements or {})

        # Generate mockup
        mockup_data = await main.mockup_concept.generate(
            modified_image_bytes,
            modified_prompt,
            modified_requirements
        )

        # Execute after_mockup_generate hook
        await main.plugin_concept.execute_hook(
            "after_mockup_generate",
            mockup_html=mockup_data["html"],
            mockup_id=mockup_data["mockup_id"]
        )

        return {
            "mockup_id": mockup_data["mockup_id"],
            "html": mockup_data["html"],
            "download_url": f"/api/export/{mockup_data['mockup_id']}",
            "preview_url": f"/api/mockup/{mockup_data['mockup_id']}/preview",
            "exported_at": mockup_data["generated_at"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")