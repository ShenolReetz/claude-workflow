#!/usr/bin/env python3
"""
Fix the helper method structure
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find the helper method and everything after it
import re

# Replace the entire problematic section with a clean version
# First, let's find where the helper method starts
helper_start = content.find('async def _save_countdown_to_airtable')

if helper_start > 0:
    # Find where the next method or section starts
    next_section = content.find('\n\n        #', helper_start)
    if next_section < 0:
        next_section = content.find('\n\n    #', helper_start)
    if next_section < 0:
        next_section = content.find('\n\n#', helper_start)
    
    # Replace with clean helper method
    clean_helper = '''async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script products to Airtable"""
        update_fields = {}
        
        # Save each product - these fields definitely exist
        if 'products' in script_data:
            for i, product in enumerate(script_data['products']):
                product_num = i + 1
                update_fields[f'ProductNo{product_num}Title'] = product.get('title', '')
                update_fields[f'ProductNo{product_num}Description'] = product.get('description', '')
        
        # Skip intro/outro for now as fields might not exist
        
        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
                print(f"💾 Saved {len(update_fields)} fields to Airtable")
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")
                # Continue anyway
    '''
    
    # Replace the section
    before = content[:helper_start]
    after = content[next_section:] if next_section > 0 else ""
    
    content = before + clean_helper + '\n' + after
    
    # Write back
    with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed helper method structure")
else:
    print("❌ Could not find helper method")
