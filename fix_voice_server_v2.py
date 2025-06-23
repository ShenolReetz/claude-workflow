#!/usr/bin/env python3
import re

# Read the file
with open('src/voice_generation_server.py', 'r') as f:
    content = f.read()

# Find and replace the entire generate_audio_with_elevenlabs function
old_function = r'''def generate_audio_with_elevenlabs\(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"\) -> bytes:
    """Generate audio using ElevenLabs API and return audio bytes\."""
    try:
        audio_generator = elevenlabs_client\.generate\(
            text=text,
            voice=voice_id,  # Rachel voice
            voice_settings=VoiceSettings\(
                stability=0\.5,
                similarity_boost=0\.8,
                style=0\.2,
                use_speaker_boost=True
            \),
            model="eleven_multilingual_v2"
        \)
        audio_bytes = b""\.join\(audio_generator\)
        return audio_bytes
    except Exception as e:
        raise Exception\(f"ElevenLabs API error: {str\(e\)}"\)'''

new_function = '''def generate_audio_with_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """Generate audio using ElevenLabs API and return audio bytes."""
    try:
        # Use text_to_speech.convert() for ElevenLabs v2.x
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,  # Rachel voice
            model_id="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(audio_generator)
        return audio_bytes
    except Exception as e:
        raise Exception(f"ElevenLabs API error: {str(e)}")'''

# Replace the function
content = re.sub(old_function, new_function, content, flags=re.DOTALL)

# Write the fixed content
with open('src/voice_generation_server.py', 'w') as f:
    f.write(content)

print("✅ Fixed voice_generation_server.py with proper v2.x API")
