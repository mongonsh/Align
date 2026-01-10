"""
MockupConcept: Generate visual representation of changes
Purpose: Submit requirements -> Generate HTML mockup
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import aiofiles


class MockupConcept:
    """
    Generates HTML mockups using AI.
    Depends on GeminiClient service but remains conceptually independent.
    """

    def __init__(self, gemini_client, mockup_dir: str = "mockups"):
        self.gemini = gemini_client
        self.mockup_dir = Path(mockup_dir)
        self.mockup_dir.mkdir(parents=True, exist_ok=True)
        self.mockups = {}

    async def generate(
        self,
        image_bytes: bytes,
        prompt: str,
        requirements: dict
    ) -> dict:
        """
        Generate HTML mockup using Gemini.

        Args:
            image_bytes: Original screenshot
            prompt: User's description
            requirements: Structured requirements

        Returns:
            dict with mockup_id, html, and metadata
        """
        mockup_id = str(uuid.uuid4())

        # Generate HTML using Gemini
        html_content = await self.gemini.generate_mockup(
            image_bytes=image_bytes,
            prompt=prompt,
            requirements=requirements
        )

        # Save mockup to file
        filepath = self.mockup_dir / f"{mockup_id}.html"
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(html_content)

        # Store metadata
        metadata = {
            "mockup_id": mockup_id,
            "filepath": str(filepath),
            "html": html_content,
            "prompt": prompt,
            "requirements": requirements,
            "generated_at": datetime.now().isoformat(),
            "status": "complete",
        }

        self.mockups[mockup_id] = metadata
        return metadata

    async def get_mockup(self, mockup_id: str) -> dict:
        """
        Retrieve mockup by ID.

        Args:
            mockup_id: UUID of the mockup

        Returns:
            Mockup metadata including HTML content
        """
        if mockup_id not in self.mockups:
            raise ValueError(f"Mockup {mockup_id} not found")

        return self.mockups[mockup_id]

    async def get_html(self, mockup_id: str) -> str:
        """
        Get HTML content for a mockup.

        Args:
            mockup_id: UUID of the mockup

        Returns:
            HTML string
        """
        if mockup_id not in self.mockups:
            raise ValueError(f"Mockup {mockup_id} not found")

        filepath = self.mockups[mockup_id]["filepath"]
        async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
            return await f.read()

    def list_mockups(self) -> list[dict]:
        """List all generated mockups."""
        return [
            {
                "mockup_id": m["mockup_id"],
                "generated_at": m["generated_at"],
                "status": m["status"],
                "prompt": m["prompt"]
            }
            for m in self.mockups.values()
        ]

    async def regenerate(self, mockup_id: str) -> dict:
        """
        Regenerate an existing mockup with the same requirements.

        Args:
            mockup_id: UUID of the mockup to regenerate

        Returns:
            New mockup metadata
        """
        if mockup_id not in self.mockups:
            raise ValueError(f"Mockup {mockup_id} not found")

        original = self.mockups[mockup_id]

        # Note: This would need access to original image_bytes
        # For MVP, we'll return a placeholder
        raise NotImplementedError("Regeneration requires storing original images")
