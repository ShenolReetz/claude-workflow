#!/usr/bin/env python3
import re

# Read the current file
with open('src/voice_generation_server.py', 'r') as f:
    lines = f.readlines()

# Find the function and replace it
in_function = False
new_lines = []
skip_lines = 0

for i, line in enumerate(lines):
    if skip_lines > 0:
        skip_lines -= 1
        continue
        
    if 'def generate_audio_with_elevenlabs' in line:
        in_function = True
        # Add the new function
        new_lines.append('def generate_audio_with_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:\n')
        new_lines.append('    """Generate audio using ElevenLabs API and return audio bytes."""\n')
        new_lines.append('    try:\n')
        new_lines.append('        # Use text_to_speech.convert() for ElevenLabs v2.x\n')
        new_lines.append('        audio_generator = elevenlabs_client.text_to_speech.convert(\n')
        new_lines.append('            text=text,\n')
        new_lines.append('            voice_id=voice_id,  # Rachel voice\n')
        new_lines.append('            model_id="eleven_multilingual_v2"\n')
        new_lines.append('        )\n')
        new_lines.append('        audio_bytes = b"".join(audio_generator)\n')
        new_lines.append('        return audio_bytes\n')
        new_lines.append('    except Exception as e:\n')
        new_lines.append('        raise Exception(f"ElevenLabs API error: {str(e)}")\n')
        
        # Skip until we find the end of the old function
        j = i + 1
        indent_count = 0
        while j < len(lines):
            if lines[j].strip() and not lines[j].startswith(' '):
                # Found next function or top-level code
                skip_lines = j - i - 1
                break
            j += 1
    elif not in_function:
        new_lines.append(line)
    
    if in_function and skip_lines == 0 and i > 0:
        in_function = False

# Write the fixed file
with open('src/voice_generation_server.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Fixed voice_generation_server.py")
