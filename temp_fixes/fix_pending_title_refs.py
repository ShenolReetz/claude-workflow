#!/usr/bin/env python3
"""
Fix all pending_title references in the helper method
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix any line that has pending_title in the helper method
in_helper = False
fixed_lines = []

for i, line in enumerate(lines):
    # Check if we're in the helper method
    if '_save_countdown_to_airtable' in line and 'async def' in line:
        in_helper = True
    elif in_helper and ('async def' in line or 'def ' in line) and '_save_countdown_to_airtable' not in line:
        in_helper = False
    
    # Fix pending_title references in the helper method
    if in_helper and 'pending_title[' in line:
        # Replace pending_title['record_id'] with just record_id
        fixed_line = line.replace("pending_title['record_id']", "record_id")
        print(f"Fixed line {i+1}: {line.strip()} -> {fixed_line.strip()}")
        fixed_lines.append(fixed_line)
    else:
        fixed_lines.append(line)

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed pending_title references")
