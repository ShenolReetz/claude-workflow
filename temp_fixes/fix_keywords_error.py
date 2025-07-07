#!/usr/bin/env python3
"""
Remove the undefined keywords reference
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find and remove the line with 'keywords'
fixed_lines = []
for i, line in enumerate(lines):
    if "'keywords': keywords," in line:
        print(f"Removed keywords reference at line {i+1}")
        continue  # Skip this line
    fixed_lines.append(line)

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed keywords error")
