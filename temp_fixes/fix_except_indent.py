with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix except block indentation
fixed_lines = []

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Add the current line
    fixed_lines.append(line)
    
    # If this is an except statement
    if stripped.startswith('except ') and stripped.endswith(':'):
        # Check if the next line needs indentation
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.strip()
            
            # If next line has content but isn't indented properly
            if next_stripped and not next_line.startswith(' ' * (len(line) - len(line.lstrip()) + 4)):
                # Fix the indentation of the next line
                current_indent = len(line) - len(line.lstrip())
                lines[i + 1] = ' ' * (current_indent + 4) + next_stripped + '\n'

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed except block indentation")

# Show the area around line 123-125
print("\nArea around line 123-125:")
for i in range(122, min(126, len(fixed_lines))):
    print(f"{i+1}: {fixed_lines[i]}", end='')
