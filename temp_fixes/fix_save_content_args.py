#!/usr/bin/env python3
"""
Fix the save_generated_content call arguments
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find and fix the save_generated_content call
# It's being called with 4 args but needs 3
old_call = """await self.airtable_server.save_generated_content(
            pending_title['record_id'],
            keywords,
            content_data
        )"""

new_call = """await self.airtable_server.save_generated_content(
            pending_title['record_id'],
            content_data
        )"""

content = content.replace(old_call, new_call)

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed save_generated_content arguments")
