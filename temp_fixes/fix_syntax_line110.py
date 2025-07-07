#!/usr/bin/env python3
"""
Fix the syntax error on line 110
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix line 110 (index 109)
for i, line in enumerate(lines):
    if i == 109 and '**name**' in line:
        lines[i] = line.replace('**name**', '__name__')
        print(f"Fixed line {i+1}: {line.strip()} -> {lines[i].strip()}")
    elif 'if __name__' in line and ':' not in line:
        lines[i] = 'if __name__ == "__main__":\n'
        print(f"Fixed line {i+1}")

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.writelines(lines)

print("✅ Fixed syntax error")
