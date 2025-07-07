with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix all empty try blocks
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # If we find a try block
    if stripped == 'try:':
        # Look ahead to see what's in the try block
        j = i + 1
        has_content = False
        
        while j < len(lines):
            next_line = lines[j].strip()
            if next_line and not next_line.startswith('#'):
                if next_line.startswith('except'):
                    # Empty try block found
                    break
                else:
                    has_content = True
                    break
            j += 1
        
        if not has_content:
            # Skip this empty try-except block entirely
            i = j
            # Skip the except part too
            while i < len(lines) and not (lines[i].strip() and not lines[i].strip().startswith(('except', 'finally', 'pass', '#'))):
                i += 1
            continue
    
    # For try blocks that are at the wrong indentation level (lines 137, 145)
    if i >= 135 and i <= 150 and stripped == 'try:':
        # These are the problematic orphaned try blocks - skip them
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith('except'):
            j += 1
        if j < len(lines):
            # Skip past the except block too
            i = j
            while i < len(lines) and (lines[i].strip().startswith(('except', 'pass')) or lines[i].strip() == '' or '# Continue' in lines[i]):
                i += 1
            continue
    
    fixed_lines.append(line)
    i += 1

# Write the fixed file
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Removed all empty try blocks")

# Check the problematic area
print("\nArea around lines 135-150:")
for i in range(135, min(150, len(fixed_lines))):
    if i < len(fixed_lines):
        print(f"{i}: {fixed_lines[i].rstrip()}")
