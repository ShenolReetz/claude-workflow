#!/usr/bin/env python3

# Read the broken file
with open('src/voice_generation_server.py', 'r') as f:
    lines = f.readlines()

# Find where to insert the missing function declaration
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    
    # After the generate_audio_with_elevenlabs function ends and before the docstring
    if i > 0 and 'raise Exception(f"ElevenLabs API error:' in lines[i] and i+1 < len(lines) and '"""Generate audio and upload to Google Drive."""' in lines[i+1]:
        # Insert the missing async function declaration
        new_lines.append('\n')
        new_lines.append('async def generate_and_upload_audio(text: str, filename: str, audio_folder_id: str) -> dict:\n')

# Write the fixed file
with open('src/voice_generation_server.py', 'w') as f:
    f.writelines(new_lines)

print("✅ Added missing async function declaration")
