import os
from elevenlabs import ElevenLabs

# Set up API key
api_key = os.environ.get("ELEVENLABS_API_KEY")
if not api_key:
    print("❌ ELEVENLABS_API_KEY not set")
    exit(1)

print("Testing ElevenLabs API v2.x...")

# Check what's available in the elevenlabs module
import elevenlabs
print("\nAvailable in elevenlabs module:")
print([item for item in dir(elevenlabs) if not item.startswith('_')])

# Create client and check methods
try:
    client = ElevenLabs(api_key=api_key)
    print("\n✅ Created ElevenLabs client")
    
    # Check available attributes
    attrs = [attr for attr in dir(client) if not attr.startswith('_')]
    print(f"\nClient attributes: {attrs}")
    
    # Check specific attributes
    if hasattr(client, 'text_to_speech'):
        print("\n✅ Has text_to_speech")
        tts_methods = [m for m in dir(client.text_to_speech) if not m.startswith('_')]
        print(f"text_to_speech methods: {tts_methods}")
    
    if hasattr(client, 'generate'):
        print("\n✅ Has generate method")
    else:
        print("\n❌ No generate method on client")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
