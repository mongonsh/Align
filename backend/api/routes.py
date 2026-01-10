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

    try:
        # Step 1: Get image using UploadConcept
        image_bytes = await main.upload_concept.get_current(request.image_id)

        # Step 2: Parse requirements using PromptConcept (if not provided)
        if request.requirements:
            requirements = request.requirements
        else:
            requirements = main.prompt_concept.parse_intent(request.description)

        # Step 3: Generate mockup using MockupConcept
        mockup_data = await main.mockup_concept.generate(
            image_bytes=image_bytes,
            prompt=request.description,
            requirements=requirements
        )

        # Step 4: Prepare response using ExportConcept
        response = main.export_concept.prepare_response(
            mockup_html=mockup_data["html"],
            mockup_id=mockup_data["mockup_id"]
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
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
