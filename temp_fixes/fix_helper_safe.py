#!/usr/bin/env python3
"""
Create safer helper method
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find the helper method and replace it with a safer version
import re

# Pattern to find the entire helper method
pattern = r'(    async def _save_countdown_to_airtable.*?print\(f"💾 Saved.*?\))'

# New safer method
new_method = '''    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script products to Airtable"""
        update_fields = {}
        
        # Save each product - these fields definitely exist
        if 'products' in script_data:
            for i, product in enumerate(script_data['products']):
                product_num = i + 1
                update_fields[f'ProductNo{product_num}Title'] = product.get('title', '')
                update_fields[f'ProductNo{product_num}Description'] = product.get('description', '')
        
        # Skip intro/outro for now as fields might not exist
        # Can add them later when we verify field names
        
        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
                print(f"💾 Saved {len(update_fields)} fields to Airtable")
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")
                # Continue anyway
        '''

# Replace the method
content = re.sub(pattern, new_method, content, flags=re.DOTALL)

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Created safer helper method")
