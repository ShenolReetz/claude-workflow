import os
from elevenlabs import ElevenLabs, generate

# Set up API key
api_key = os.environ.get("ELEVENLABS_API_KEY")
if not api_key:
    print("❌ ELEVENLABS_API_KEY not set")
    exit(1)

print("Testing ElevenLabs API v2.x...")

# Test 1: Using generate function directly
try:
    from elevenlabs import generate as elevenlabs_generate
    print("✅ Found 'generate' function")
    
    # Try generating audio
    audio = elevenlabs_generate(
        text="Testing voice generation",
        voice="21m00Tcm4TlvDq8ikWAM",
        api_key=api_key
    )
    audio_bytes = b"".join(audio)
    print(f"✅ Direct generate worked! Generated {len(audio_bytes)} bytes")
except Exception as e:
    print(f"❌ Direct generate failed: {e}")

# Test 2: Using client
try:
    client = ElevenLabs(api_key=api_key)
    print("✅ Created ElevenLabs client")
    
    # Check available methods
    print("Available client methods:", [m for m in dir(client) if not m.startswith('_')])
    
    # Try text_to_speech if available
    if hasattr(client, 'text_to_speech'):
        print("✅ Found text_to_speech method")
except Exception as e:
    print(f"❌ Client creation failed: {e}")
