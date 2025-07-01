#!/usr/bin/env python3
"""
Fix the last pending_title reference
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix line 184
for i, line in enumerate(lines):
    if i == 183:  # Line 184 (0-indexed)
        if "pending_title['title']" in line:
            # Remove this line or comment it out
            lines[i] = '            # print(f"   Original: {title}")\n'
            print(f"Fixed line {i+1}")

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.writelines(lines)

print("✅ Fixed last pending_title reference")
