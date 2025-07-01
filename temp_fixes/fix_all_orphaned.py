with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Clean up all orphaned lines between imports and class definition
cleaned_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # If we're between line 15 and 25 (the problematic area)
    if 15 <= i <= 25:
        # Skip any indented lines that aren't part of a proper structure
        if line.startswith((' ', '\t')) and not line.startswith('class '):
            print(f"Removing orphaned line {i+1}: {stripped[:50]}...")
            i += 1
            continue
        # Skip orphaned logger/error statements
        if 'logger.' in line or '✅' in line or '⚠️' in line:
            print(f"Removing orphaned statement {i+1}: {stripped[:50]}...")
            i += 1
            continue
        # Skip comments that are orphaned
        if stripped.startswith('#') and 'Continue workflow' in stripped:
            print(f"Removing orphaned comment {i+1}: {stripped[:50]}...")
            i += 1
            continue
    
    # Keep valid lines
    if stripped or i < 10 or i > 25:  # Keep empty lines outside problem area
        cleaned_lines.append(line)
    
    i += 1

# Write cleaned file
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(cleaned_lines)

print("\n✅ Cleaned all orphaned lines")

# Show the cleaned area
print("\nCleaned area (lines 13-23):")
for i in range(13, min(23, len(cleaned_lines))):
    if i < len(cleaned_lines):
        print(f"{i}: {cleaned_lines[i].rstrip()}")
