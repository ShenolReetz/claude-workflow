"""
Test Image Generation MCP Server

Test mode stub that skips actual image generation to save API calls and time.
Returns success without making actual OpenAI API calls.
"""

import os
import asyncio
from typing import Dict, Any

class ImageGenerationMCPServer:
    """Test mode image generation server - skips actual API calls"""
    
    def __init__(self):
        self.name = "test-image-generation"
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "test-key")
    
    async def start(self):
        """Start the test server"""
        pass
    
    async def generate_image(self, prompt: str, size: str = "1024x1024") -> Dict[str, Any]:
        """
        Test mode: Returns success without actual image generation
        
        Args:
            prompt: The image generation prompt
            size: Image size (ignored in test mode)
            
        Returns:
            Dict with simulated image URL
        """
        print(f"🎨 TEST MODE: Simulating image generation for prompt: {prompt[:50]}...")
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Return a test image URL
        return {
            "success": True,
            "image_url": "https://via.placeholder.com/1024x1024.png?text=TEST+IMAGE",
            "test_mode": True,
            "prompt": prompt,
            "size": size
        }
    
    async def run_forever(self):
        """Keep the server running"""
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("Test image generation server stopped.")

async def main():
    """Main entry point for the test image generation server"""
    server = ImageGenerationMCPServer()
    await server.start()
    await server.run_forever()

if __name__ == "__main__":
    asyncio.run(main())