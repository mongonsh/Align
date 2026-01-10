"""
Gemini API client for mockup generation
"""

import os
import base64
from typing import Optional
import google.generativeai as genai


class GeminiClient:
    """
    Wrapper for Google Gemini API.
    Handles multimodal prompts for mockup generation.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        genai.configure(api_key=self.api_key)
        # Use the latest available flash model
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def generate_mockup(
        self,
        image_bytes: bytes,
        prompt: str,
        requirements: dict
    ) -> str:
        """
        Generate HTML mockup from image and requirements.

        Args:
            image_bytes: Original screenshot
            prompt: User's description
            requirements: Structured requirements from PromptConcept

        Returns:
            Complete HTML/CSS mockup as string
        """
        import asyncio
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Starting Gemini mockup generation with prompt: {prompt[:100]}...")
            
            system_prompt = self._build_system_prompt(requirements)
            full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

            # Prepare image for Gemini
            image_parts = [
                {
                    "mime_type": "image/png",
                    "data": base64.b64encode(image_bytes).decode('utf-8')
                }
            ]

            logger.info("Sending request to Gemini API...")
            
            # Generate response in a thread pool since Gemini API is synchronous
            def _generate_sync():
                try:
                    response = self.model.generate_content([
                        full_prompt,
                        image_parts[0]
                    ])
                    logger.info("Gemini API response received successfully")
                    return response
                except Exception as e:
                    logger.error(f"Gemini API error: {str(e)}")
                    raise

            response = await asyncio.get_event_loop().run_in_executor(None, _generate_sync)
            
            if not response or not response.text:
                logger.error("Empty response from Gemini API")
                raise ValueError("Empty response from Gemini API")
                
            logger.info(f"Gemini response length: {len(response.text)} characters")
            
            html_content = self._extract_html(response.text)
            logger.info(f"HTML extracted successfully, length: {len(html_content)} characters")
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error in generate_mockup: {str(e)}")
            logger.error(f"Image bytes length: {len(image_bytes) if image_bytes else 'None'}")
            logger.error(f"Prompt: {prompt}")
            logger.error(f"Requirements: {requirements}")
            raise

    def _build_system_prompt(self, requirements: dict) -> str:
        """Build comprehensive prompt for Gemini."""
        action = requirements.get("action_type", "modify")
        targets = requirements.get("targets", [])
        properties = requirements.get("properties", {})

        prompt = f"""You are a UI/UX designer and frontend developer.
Your task is to generate a complete, production-ready HTML mockup based on the provided screenshot and user requirements.

**Requirements:**
- Action: {action}
- Target elements: {', '.join(targets) if targets else 'general UI'}
- Visual properties: {properties}

**Instructions:**
1. Analyze the provided screenshot carefully
2. Generate a complete HTML page with inline CSS
3. Make the requested changes while preserving the overall design
4. Use modern CSS (Flexbox, Grid) for layouts
5. Make it responsive and visually appealing
6. Include all necessary styling inline
7. Do NOT include any explanatory text - output ONLY the HTML

**Output Format:**
Return ONLY the complete HTML, starting with <!DOCTYPE html> and ending with </html>.
Include all CSS inline in <style> tags.
Make sure the mockup is fully self-contained and can be opened in a browser immediately.
"""
        return prompt

    def _extract_html(self, response_text: str) -> str:
        """Extract HTML from Gemini response, removing markdown formatting."""
        text = response_text.strip()

        # Remove markdown code blocks if present
        if "```html" in text:
            text = text.split("```html")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # Ensure it starts with DOCTYPE or html tag
        if not text.startswith("<!DOCTYPE") and not text.startswith("<html"):
            # Find the first occurrence of <!DOCTYPE or <html
            for line in text.split("\n"):
                if line.strip().startswith("<!DOCTYPE") or line.strip().startswith("<html"):
                    idx = text.index(line.strip())
                    text = text[idx:]
                    break

        return text

    def validate_api_key(self) -> bool:
        """Validate that the API key is configured and working."""
        try:
            # Simple test request
            response = self.model.generate_content("Hello")
            return True
        except Exception:
            return False
