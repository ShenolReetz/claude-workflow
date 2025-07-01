with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')

# Find the problematic section and clean it
cleaned_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # If this is around the problematic area (line 145)
    if i >= 144 and i <= 155:
        # Skip lines that are incorrectly indented after except block
        if line.strip().startswith("print(f'🔍 DEBUG: video_url"):
            i += 1
            continue
        # Skip the incorrectly indented if block
        if "if video_url and video_url.strip():" in line and line.startswith('                '):
            # Skip this whole block
            while i < len(lines) and lines[i].startswith('                '):
                i += 1
            continue
    
    cleaned_lines.append(line)
    i += 1

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.write('\n'.join(cleaned_lines))

print("✅ Cleaned workflow runner")
