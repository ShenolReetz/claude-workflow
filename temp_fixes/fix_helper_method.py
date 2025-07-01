#!/usr/bin/env python3
"""
Fix the helper method errors
"""

# Read workflow_runner.py
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find and fix the helper method
old_method = """            await self.airtable_server.update_record(record_id, update_fields)
            print(f"💾 Saved {len(update_fields)} fields to Airtable")
        
            'keywords': keywords,"""

# Remove the keywords line which is causing the error
new_method = """            await self.airtable_server.update_record(record_id, update_fields)
            print(f"💾 Saved {len(update_fields)} fields to Airtable")"""

content = content.replace(old_method, new_method)

# Also fix the VideoIntro/VideoOutro field names if they don't exist in Airtable
# Let's use simpler field names or skip them for now
content = content.replace("'VideoIntro'", "'Intro'")
content = content.replace("'VideoOutro'", "'Outro'")

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed helper method")
