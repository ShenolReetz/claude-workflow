with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix the indentation in the with statement
fixed_lines = []
in_with = False

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Check if this is a with statement
    if 'with open' in line and '.json' in line:
        fixed_lines.append(line)
        in_with = True
        continue
    
    # If we're in a with block and the next line is the json.load
    if in_with and 'json.load' in stripped:
        # This should be indented more than the with statement
        # Find the indentation of the with statement
        prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
        fixed_lines.append(' ' * (prev_indent + 4) + stripped + '\n')
        in_with = False
        continue
    
    fixed_lines.append(line)

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed with statement indentation")

# Show the fixed area
print("\nFixed area around line 25-27:")
for i in range(24, min(28, len(fixed_lines))):
    print(f"{i+1}: {fixed_lines[i]}", end='')
