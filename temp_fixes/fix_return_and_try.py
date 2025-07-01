with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix the return statement indentation and empty try blocks
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Fix the return statement that should be inside the if block
    if i >= 55 and i <= 65:
        if stripped == 'return' and i > 0:
            # Check if previous line was the print statement
            if 'No pending titles found' in lines[i-1]:
                # This return should be indented same as the print
                prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                fixed_lines.append(' ' * prev_indent + 'return\n')
                i += 1
                continue
    
    # Check for empty try blocks
    if stripped == 'try:':
        # Look ahead to see if there's content
        j = i + 1
        has_content = False
        while j < len(lines) and j < i + 5:
            next_line = lines[j].strip()
            if next_line and not next_line.startswith('#'):
                if next_line.startswith('except'):
                    # Empty try block
                    break
                else:
                    has_content = True
                    break
            j += 1
        
        if not has_content:
            # Skip this empty try-except block
            print(f"Skipping empty try block at line {i+1}")
            i = j
            while i < len(lines) and not (lines[i].strip() and not lines[i].strip().startswith(('except', 'finally', 'pass'))):
                i += 1
            continue
    
    fixed_lines.append(line)
    i += 1

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed return statement and try blocks")

# Show the areas we fixed
print("\nArea around line 58-62:")
for i in range(57, min(62, len(fixed_lines))):
    print(f"{i+1}: {fixed_lines[i]}", end='')
