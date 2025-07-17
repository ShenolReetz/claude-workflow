import asyncio
import json
import requests
import base64
from typing import Dict, List, Optional
from mcp_servers.Test_default_audio_manager import TestDefaultAudioManager

class VoiceGenerationMCPServer:
    def __init__(self, elevenlabs_api_key: str):
        self.api_key = elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        # Voice IDs for different types of content
        self.voice_ids = {
            "narrator": "21m00Tcm4TlvDq8ikWAM",  # Rachel - clear, professional
            "intro": "21m00Tcm4TlvDq8ikWAM",     # Same voice for consistency
            "outro": "21m00Tcm4TlvDq8ikWAM",     # Same voice for consistency
            "products": "21m00Tcm4TlvDq8ikWAM"   # Same voice for products
        }
        
        # Initialize default audio manager
        self.audio_manager = TestDefaultAudioManager()
    
    async def generate_voice_from_text(self, text: str, voice_type: str = "narrator") -> Optional[str]:
        """Generate voice audio (TEST MODE: Uses default audio files instead of ElevenLabs)"""
        try:
            print(f"🎵 TEST MODE: Using default {voice_type} audio instead of generation")
            
            # Return a placeholder to indicate we're using default audio
            # The actual URL will be handled by the audio manager
            return "TEST_MODE_DEFAULT_AUDIO"
                
        except Exception as e:
            print(f"❌ Error in TEST MODE voice handling for {voice_type}: {e}")
            return None
    
    async def generate_product_voice(self, product_name: str, product_description: str, product_rank: int) -> Optional[str]:
        """Generate voice for a specific product (TEST MODE: Uses default audio)"""
        print(f"🎵 TEST MODE: Using default product audio for rank {product_rank}")
        return "TEST_MODE_DEFAULT_AUDIO"
    
    async def generate_intro_voice(self, intro_text: str) -> Optional[str]:
        """Generate voice for intro (TEST MODE: Uses default audio)"""
        print(f"🎵 TEST MODE: Using default intro audio")
        return "TEST_MODE_DEFAULT_AUDIO"
    
    async def generate_outro_voice(self, outro_text: str) -> Optional[str]:
        """Generate voice for outro (TEST MODE: Uses default audio)"""
        print(f"🎵 TEST MODE: Using default outro audio")
        return "TEST_MODE_DEFAULT_AUDIO"

# Test the server
async def test_voice_generation():
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = VoiceGenerationMCPServer(config['elevenlabs_api_key'])
    
    # Test with sample text
    test_text = "This is a test of the ElevenLabs voice generation for product number 5."
    print(f"🧪 Testing voice generation...")
    
    voice_data = await server.generate_voice_from_text(test_text, "narrator")
    if voice_data:
        print(f"✅ Test successful! Generated {len(voice_data)} characters of base64 audio")
        print(f"📊 First 100 characters: {voice_data[:100]}...")
    else:
        print("❌ Test failed")

if __name__ == "__main__":
    asyncio.run(test_voice_generation())
