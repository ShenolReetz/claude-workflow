#!/usr/bin/env python3
"""
Fix WordPress integration issues
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# 1. Fix logger import if not present
if 'import logging' not in content:
    # Add logging import at the top
    import_pos = content.find('import asyncio')
    if import_pos > 0:
        content = 'import logging\n' + content
        print("✅ Added logging import")

# Add logger initialization if not present
if 'logger = logging.getLogger' not in content:
    # Add after imports
    imports_end = content.find('\nclass ')
    if imports_end > 0:
        logger_init = '\nlogger = logging.getLogger(__name__)\n'
        content = content[:imports_end] + logger_init + content[imports_end:]
        print("✅ Added logger initialization")

# 2. Fix the get_record issue - we already have the data in pending_title
# Replace the get_record call with the data we already have
old_code = '''            try:
                # Get all the data from Airtable for the blog post
                record_data = await self.airtable_server.get_record(pending_title['record_id'])'''

new_code = '''            try:
                # Use the pending_title data which already has all fields
                record_data = pending_title'''

content = content.replace(old_code, new_code)
print("✅ Fixed record_data to use existing pending_title data")

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("\n✅ All issues fixed!")
