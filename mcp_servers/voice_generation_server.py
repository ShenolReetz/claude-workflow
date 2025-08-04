import asyncio
import json
import requests
import base64
from typing import Dict, List, Optional

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
    
    async def generate_voice_from_text(self, text: str, voice_type: str = "narrator") -> Optional[str]:
        """Generate voice audio from text using ElevenLabs"""
        try:
            voice_id = self.voice_ids.get(voice_type, self.voice_ids["narrator"])
            
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            print(f"🎵 Generating {voice_type} voice: {text[:50]}...")
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 200:
                # Convert audio to base64 for storage
                audio_base64 = base64.b64encode(response.content).decode()
                print(f"✅ Generated {voice_type} voice ({len(audio_base64)} chars)")
                return audio_base64
            else:
                print(f"❌ ElevenLabs API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating voice for {voice_type}: {e}")
            return None
    
    async def generate_product_voice(self, product_name: str, product_description: str, product_rank: int) -> Optional[str]:
        """Generate voice for a specific product"""
        # Use only the description for voice - the title is shown visually in video
        voice_script = product_description
        
        return await self.generate_voice_from_text(voice_script, "products")
    
    async def generate_intro_voice(self, intro_text: str) -> Optional[str]:
        """Generate voice for intro"""
        return await self.generate_voice_from_text(intro_text, "intro")
    
    async def generate_outro_voice(self, outro_text: str) -> Optional[str]:
        """Generate voice for outro"""
        return await self.generate_voice_from_text(outro_text, "outro")

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
