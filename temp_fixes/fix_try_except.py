#!/usr/bin/env python3
"""
Fix the try-except block syntax error
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the try-except block
old_code = """        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
            print(f"💾 Saved {len(update_fields)} fields to Airtable")
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")
                # Continue anyway"""

new_code = """        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
                print(f"💾 Saved {len(update_fields)} fields to Airtable")
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")
                # Continue anyway"""

content = content.replace(old_code, new_code)

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed try-except block")
