with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix the if-else block structure around line 117-121
fixed_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Handle the specific problematic area around line 117-121
    if i >= 116 and i <= 122:
        if stripped.startswith("if affiliate_result['success']:"):
            # Add the if line
            fixed_lines.append(line)
            i += 1
            
            # Add properly indented content for the if block
            indent = len(line) - len(line.lstrip())
            # Line 118 - first print
            if i < len(lines) and 'Generated' in lines[i]:
                fixed_lines.append(' ' * (indent + 4) + lines[i].strip() + '\n')
                i += 1
            # Line 119 - second print
            if i < len(lines) and 'Processed' in lines[i]:
                fixed_lines.append(' ' * (indent + 4) + lines[i].strip() + '\n')
                i += 1
            # Skip to else
            continue
            
        elif stripped == 'else:':
            # Add the else with proper indentation (same as if)
            # Find the matching if indent
            for j in range(len(fixed_lines) - 1, max(0, len(fixed_lines) - 10), -1):
                if 'if affiliate_result' in fixed_lines[j]:
                    if_indent = len(fixed_lines[j]) - len(fixed_lines[j].lstrip())
                    fixed_lines.append(' ' * if_indent + 'else:\n')
                    break
            i += 1
            # Add the content after else
            if i < len(lines) and 'had issues' in lines[i]:
                fixed_lines.append(' ' * (if_indent + 4) + lines[i].strip() + '\n')
                i += 1
            continue
    
    fixed_lines.append(line)
    i += 1

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed if-else structure")

# Show the fixed area
print("\nFixed area around line 117-122:")
for i in range(116, min(123, len(fixed_lines))):
    print(f"{i+1}: {fixed_lines[i]}", end='')
