with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find the class definition and fix indentation
fixed_lines = []
in_class = False
class_indent = 0
method_indent = 4

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # If we find the class definition
    if stripped.startswith('class ContentPipelineOrchestrator:'):
        fixed_lines.append('class ContentPipelineOrchestrator:\n')
        in_class = True
        continue
    
    # If we're in the class
    if in_class:
        if stripped:
            # Check if this is a method definition
            if stripped.startswith('def ') or stripped.startswith('async def '):
                # Methods should be indented 4 spaces
                fixed_lines.append('    ' + stripped + '\n')
            elif i < len(lines) - 1 and 'def ' in lines[i+1]:
                # This might be a line before a method
                fixed_lines.append(line)
            else:
                # This is code inside the class, check context
                # If previous line was a method definition or colon-ending line
                if i > 0 and (lines[i-1].strip().endswith(':') or 'def ' in lines[i-1]):
                    # Indent 8 spaces (inside method)
                    fixed_lines.append('        ' + stripped + '\n')
                else:
                    # Keep existing indentation if it looks reasonable
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent >= 4:
                        fixed_lines.append(line)
                    else:
                        fixed_lines.append('        ' + stripped + '\n')
        else:
            fixed_lines.append('\n')
    else:
        fixed_lines.append(line)

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed class structure")

# Show the area around line 39
print("\nArea around line 39:")
for i in range(35, min(45, len(fixed_lines))):
    print(f"{i}: {fixed_lines[i]}", end='')
