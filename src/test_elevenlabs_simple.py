import os
from elevenlabs import ElevenLabs

api_key = os.environ.get("ELEVENLABS_API_KEY")
if not api_key:
    print("No API key")
    exit(1)

client = ElevenLabs(api_key=api_key)

try:
    # Test the text_to_speech.convert method
    print("Testing ElevenLabs text-to-speech...")
    audio = client.text_to_speech.convert(
        text="Hello, this is a test",
        voice_id="21m00Tcm4TlvDq8ikWAM",
        model_id="eleven_multilingual_v2"
    )
    audio_bytes = b"".join(audio)
    print(f"✅ Success! Generated {len(audio_bytes)} bytes of audio")
except Exception as e:
    print(f"❌ Error: {e}")
