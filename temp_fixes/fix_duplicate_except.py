with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Remove duplicate except statements and fix pass indentation
fixed_lines = []
i = 0
just_had_except = False

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # If we just processed an except block
    if just_had_except:
        # If this is a pass statement, indent it properly
        if stripped == 'pass':
            # Get the indentation from the previous except statement
            prev_indent = len(lines[i-2]) - len(lines[i-2].lstrip()) if i >= 2 else 8
            fixed_lines.append(' ' * (prev_indent + 4) + 'pass\n')
            i += 1
            just_had_except = False
            continue
        # If this is another except statement without a try, skip it
        elif stripped.startswith('except ') and i > 0:
            # Check if there was a recent try statement
            found_try = False
            for j in range(max(0, i-5), i):
                if 'try:' in lines[j]:
                    found_try = True
                    break
            if not found_try:
                print(f"Skipping duplicate except at line {i+1}")
                i += 1
                continue
        just_had_except = False
    
    # Track if we just added an except statement
    if stripped.startswith('except ') and stripped.endswith(':'):
        just_had_except = True
    
    fixed_lines.append(line)
    i += 1

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed duplicate except and pass statements")

# Show the fixed area
print("\nFixed area around line 123-128:")
for i in range(122, min(128, len(fixed_lines))):
    print(f"{i+1}: {fixed_lines[i]}", end='')
