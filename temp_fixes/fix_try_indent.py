with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix the try block indentation around line 111
fixed_lines = []
in_try_block = False
try_indent = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # If we find a try statement around line 111
    if i >= 108 and i <= 115 and stripped == 'try:':
        fixed_lines.append(line)
        in_try_block = True
        try_indent = len(line) - len(line.lstrip())
        continue
    
    # If we're in the problematic try block
    if in_try_block and i >= 110 and i <= 120:
        if stripped.startswith('except') or (stripped and not line.startswith(' ')):
            # End of try block
            in_try_block = False
            fixed_lines.append(line)
        elif stripped:
            # This should be indented inside the try block
            fixed_lines.append(' ' * (try_indent + 4) + stripped + '\n')
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed try block indentation")

# Show the fixed area
print("\nFixed area around line 111:")
for i in range(108, min(118, len(fixed_lines))):
    print(f"{i+1}: {fixed_lines[i]}", end='')
