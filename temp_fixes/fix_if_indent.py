with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix indentation around line 58
fixed_lines = []

for i, line in enumerate(lines):
    # Add the line first
    fixed_lines.append(line)
    
    # If this is line 58 (0-indexed, so 57) and it's an if statement
    if i == 57 and 'if' in line:
        # Check if the next line is properly indented
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.strip()
            if next_stripped and not next_line.startswith(' ' * 12):  # Should be indented 12 spaces
                # Fix the indentation of the next line
                fixed_lines.pop()  # Remove the line we just added
                fixed_lines.append(line)  # Re-add the if line
                # Fix next line indentation
                current_indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * (current_indent + 4) + next_stripped + '\n')
                # Skip the next line in the loop
                lines[i + 1] = 'SKIP'

# Remove any lines marked as SKIP
fixed_lines = [line for line in fixed_lines if line != 'SKIP']

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed if statement indentation")

# Show the fixed area
print("\nArea around line 58:")
for i in range(55, min(65, len(fixed_lines))):
    print(f"{i+1}: {fixed_lines[i]}", end='')
