with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix indentation issues around line 145
fixed_lines = []
proper_indent = None

for i, line in enumerate(lines):
    # Look for the problematic line around 145
    if i >= 140 and i <= 150:
        # If this is the problematic print statement
        if "DEBUG: video_url from result" in line:
            # Find the proper indentation from previous lines
            for j in range(i-1, max(0, i-10), -1):
                if lines[j].strip() and not lines[j].strip().startswith('#'):
                    proper_indent = len(lines[j]) - len(lines[j].lstrip())
                    break
            
            if proper_indent is not None:
                # Fix the indentation
                line = ' ' * proper_indent + line.strip() + '\n'
    
    fixed_lines.append(line)

# Write the fixed file
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed indentation issues")

# Show the area around line 145 to verify
print("\nLines 140-150:")
for i in range(140, min(150, len(fixed_lines))):
    print(f"{i}: {fixed_lines[i]}", end='')
