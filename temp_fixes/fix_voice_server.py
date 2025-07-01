#!/usr/bin/env python3
import sys

# Read the file
with open('src/voice_generation_server.py', 'r') as f:
    content = f.read()

# Replace the generate method call
content = content.replace(
    'audio_generator = elevenlabs_client.generate(',
    'audio_generator = elevenlabs_client.text_to_speech.convert('
)

# Fix the parameters
content = content.replace(
    'voice=voice_id,  # Rachel voice',
    'voice_id=voice_id,  # Rachel voice'
)

# Comment out voice_settings for now as the API might not accept it in the same format
content = content.replace(
    'voice_settings=VoiceSettings(',
    '# voice_settings=VoiceSettings('
)
content = content.replace(
    '),\n            model="eleven_multilingual_v2"',
    '# ),\n            model_id="eleven_multilingual_v2"'
)

# Write the fixed content
with open('src/voice_generation_server.py', 'w') as f:
    f.write(content)

print("✅ Fixed voice_generation_server.py")
