"""
UploadConcept: Capture current system state
Purpose: User uploads screenshot -> System stores image
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import aiofiles
from PIL import Image
import io


class UploadConcept:
    """
    Handles image upload and storage with metadata tracking.
    Free-standing concept with no external dependencies.
    """

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.images = {}

    async def upload(self, file_content: bytes, filename: str) -> dict:
        """
        Store uploaded image and return metadata.

        Args:
            file_content: Raw image bytes
            filename: Original filename

        Returns:
            dict with image_id, filepath, and metadata
        """
        image_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix or '.png'
        filepath = self.upload_dir / f"{image_id}{file_extension}"

        # Validate image
        try:
            image = Image.open(io.BytesIO(file_content))
            width, height = image.size
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")

        # Save file
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(file_content)

        # Store metadata
        metadata = {
            "image_id": image_id,
            "filepath": str(filepath),
            "original_filename": filename,
            "size": len(file_content),
            "width": width,
            "height": height,
            "uploaded_at": datetime.now().isoformat(),
        }

        self.images[image_id] = metadata
        return metadata

    async def get_current(self, image_id: str) -> bytes:
        """
        Retrieve image by ID.

        Args:
            image_id: UUID of the image

        Returns:
            Image bytes
        """
        if image_id not in self.images:
            raise ValueError(f"Image {image_id} not found")

        filepath = self.images[image_id]["filepath"]

        async with aiofiles.open(filepath, 'rb') as f:
            return await f.read()

    def get_metadata(self, image_id: str) -> dict:
        """Get image metadata without loading file."""
        if image_id not in self.images:
            raise ValueError(f"Image {image_id} not found")
        return self.images[image_id]

    def list_images(self) -> list[dict]:
        """List all uploaded images."""
        return list(self.images.values())
