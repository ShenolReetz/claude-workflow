#!/usr/bin/env python3
"""
Fix syntax error in workflow_runner.py
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find and fix the syntax error around line 113
for i, line in enumerate(lines):
    if '} fields to Airtable")' in line:
        # Fix this line
        lines[i] = '            print(f"💾 Saved {len(update_fields)} fields to Airtable")\n'
        print(f"Fixed syntax error at line {i+1}")

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.writelines(lines)

print("✅ Fixed syntax error")
