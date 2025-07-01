import re

with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix any obvious indentation issues in the try/except blocks
lines = content.split('\n')
fixed_lines = []
current_indent = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Skip empty lines
    if not stripped:
        fixed_lines.append(line)
        continue
    
    # Detect indent level from keywords
    if stripped.startswith(('def ', 'class ', 'if ', 'elif ', 'else:', 'try:', 'except', 'finally:', 'with ', 'for ', 'while ')):
        if i > 0:
            # Find previous non-empty line for context
            for j in range(i-1, -1, -1):
                if lines[j].strip():
                    prev_indent = len(lines[j]) - len(lines[j].lstrip())
                    if stripped.startswith(('elif ', 'else:', 'except', 'finally:')):
                        current_indent = prev_indent
                    else:
                        current_indent = prev_indent
                    break
    
    # Fix the specific problematic line
    if "DEBUG: video_url from result" in line and i > 0:
        # Find the correct indentation from context
        for j in range(i-1, max(0, i-20), -1):
            if lines[j].strip() and 'print(' in lines[j]:
                current_indent = len(lines[j]) - len(lines[j].lstrip())
                break
        line = ' ' * current_indent + stripped
    
    # Apply proper indentation
    if line.strip():
        if "DEBUG: video_url from result" in line:
            # This should be at the same level as other print statements
            fixed_lines.append(' ' * 16 + line.strip())  # Assuming 16 spaces based on context
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Join and save
with open('src/workflow_runner.py', 'w') as f:
    f.write('\n'.join(fixed_lines))

print("✅ Fixed workflow runner indentation")
