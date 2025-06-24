#!/usr/bin/env python3
"""
Clean up the helper method completely
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find the helper method and clean it up
import re

# Find the helper method
pattern = r'(async def _save_countdown_to_airtable\(self, record_id: str, script_data: dict\):.*?)(\n    async def|\n\n# |\nif __name__|$)'

match = re.search(pattern, content, re.DOTALL)

if match:
    # Create a clean version of the helper method
    clean_helper = '''async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script products to Airtable"""
        update_fields = {}
        
        # Save each product - these fields definitely exist
        if 'products' in script_data:
            for i, product in enumerate(script_data['products']):
                product_num = i + 1
                update_fields[f'ProductNo{product_num}Title'] = product.get('title', '')
                update_fields[f'ProductNo{product_num}Description'] = product.get('description', '')
        
        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
                print(f"💾 Saved {len(update_fields)} fields to Airtable")
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")
'''
    
    # Replace the method
    content = content[:match.start()] + clean_helper + match.group(2)
    
    # Write back
    with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
        f.write(content)
    
    print("✅ Cleaned up helper method")
else:
    print("❌ Could not find helper method pattern")
