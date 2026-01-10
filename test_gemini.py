#!/usr/bin/env python3
"""
Test script to validate Gemini API integration
"""

import asyncio
import os
import sys
import base64
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent / "backend"))

from services.gemini_client import GeminiClient

async def test_gemini():
    """Test the Gemini client with a simple request"""
    try:
        # Initialize client
        client = GeminiClient()
        print("✓ GeminiClient initialized")
        
        # Test simple text generation
        print("Testing simple text generation...")
        
        # Create a simple test image (1x1 pixel PNG)
        test_image = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77yQAAAABJRU5ErkJggg=="
        )
        
        # Test requirements
        requirements = {
            "action_type": "modify",
            "targets": ["button"],
            "properties": {"colors": ["blue"]},
            "clarifications": []
        }
        
        # Test mockup generation
        print("Testing mockup generation...")
        html = await client.generate_mockup(
            image_bytes=test_image,
            prompt="Make the button blue",
            requirements=requirements
        )
        
        print("✓ Mockup generation successful!")
        print(f"Generated HTML length: {len(html)} characters")
        print(f"HTML preview: {html[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini())
    sys.exit(0 if success else 1)