with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find and remove orphaned logger statements at module level
fixed_lines = []
skip_orphaned = False

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Check if this is at module level (not indented) and contains logger
    if line[0] not in ' \t' and 'logger' in line and i > 10 and i < 30:
        # This is likely an orphaned statement
        print(f"Found orphaned statement at line {i+1}: {stripped}")
        continue
    
    # Also skip any orphaned error handling at module level
    if i < 30 and line[0] not in ' \t' and stripped.startswith(('except', 'try:', 'pass')):
        print(f"Found orphaned error handling at line {i+1}: {stripped}")
        continue
    
    fixed_lines.append(line)

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("\n✅ Removed orphaned logger statements")
