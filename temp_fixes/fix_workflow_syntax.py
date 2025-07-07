with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find the problematic try block around line 132
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Look for try: without corresponding except
    if line.strip() == 'try:' and i < len(lines) - 1:
        # Check if next lines have except
        has_except = False
        j = i + 1
        indent_level = len(line) - len(line.lstrip())
        
        while j < len(lines) and len(lines[j].strip()) > 0:
            if lines[j].startswith(' ' * indent_level + 'except'):
                has_except = True
                break
            j += 1
        
        if not has_except and j < len(lines):
            # Add the try block
            fixed_lines.append(line)
            # Add content until we find the end of the try block
            i += 1
            while i < len(lines) and (lines[i].startswith(' ' * (indent_level + 4)) or lines[i].strip() == ''):
                fixed_lines.append(lines[i])
                i += 1
            # Add except block
            fixed_lines.append(' ' * indent_level + 'except Exception as e:\n')
            fixed_lines.append(' ' * (indent_level + 4) + 'logger.error(f"Error: {e}")\n')
            fixed_lines.append(' ' * (indent_level + 4) + 'pass\n')
            continue
    
    fixed_lines.append(line)
    i += 1

with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed workflow runner syntax")
