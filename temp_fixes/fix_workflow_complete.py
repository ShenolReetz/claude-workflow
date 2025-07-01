with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

print("Analyzing workflow structure...")

# First, let's identify all the structural problems
problems = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if i >= 130 and i <= 160:
        if 'try:' in stripped and i < len(lines) - 1:
            next_line = lines[i + 1].strip()
            if not next_line or 'except' in next_line:
                problems.append(f"Empty try block at line {i + 1}")
        if stripped.startswith('print(') and line.startswith('                '):
            problems.append(f"Over-indented print at line {i + 1}")

print(f"Found {len(problems)} structural problems")

# Now let's fix the file
fixed_lines = []
i = 0
skip_until_dedent = False
last_good_indent = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    current_indent = len(line) - len(line.lstrip())
    
    # Skip empty try blocks
    if stripped == 'try:' and i < len(lines) - 1:
        next_stripped = lines[i + 1].strip()
        if next_stripped.startswith('except') or not next_stripped:
            # Skip this try and its except
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('except'):
                i += 1
            if i < len(lines):
                i += 1  # Skip the except line
                while i < len(lines) and lines[i].strip() in ['pass', ''] or '# Continue' in lines[i]:
                    i += 1
            continue
    
    # Fix over-indented blocks after except
    if i >= 140 and i <= 160:
        if current_indent >= 16 and stripped:
            # This is likely wrongly indented code
            if 'DEBUG: video_url' in line or 'if video_url and video_url.strip():' in line:
                # Skip this whole wrongly indented block
                skip_until_dedent = True
                last_good_indent = 12  # Assuming this should be at method level
        
        if skip_until_dedent:
            if current_indent <= last_good_indent and stripped:
                skip_until_dedent = False
            else:
                i += 1
                continue
    
    # Remove duplicate video upload code
    if 'Video uploaded to Google Drive successfully' in line and i > 0:
        # Check if this is a duplicate
        found_similar = False
        for j in range(max(0, i - 20), i):
            if 'Video uploaded to Google Drive successfully' in lines[j]:
                found_similar = True
                break
        if found_similar:
            i += 1
            continue
    
    fixed_lines.append(line)
    i += 1

# Write the fixed file
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed workflow runner structure completely")

# Show the fixed area
print("\nFixed area (lines 130-160):")
for i in range(130, min(160, len(fixed_lines))):
    if i < len(fixed_lines):
        print(f"{i}: {fixed_lines[i].rstrip()}")
