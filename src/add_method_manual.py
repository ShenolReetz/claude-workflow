#!/usr/bin/env python3
"""
Manually add the helper method
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find where to insert - look for the close method or end of run_complete_workflow
helper_method = '''
    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script products to Airtable"""
        update_fields = {}
        
        # Save each product
        if 'products' in script_data:
            for i, product in enumerate(script_data['products']):
                product_num = i + 1
                update_fields[f'ProductNo{product_num}Title'] = product.get('title', '')
                update_fields[f'ProductNo{product_num}Description'] = product.get('description', '')
        
        # Save intro/outro if present
        if 'intro' in script_data:
            update_fields['VideoIntro'] = script_data.get('intro', '')
        if 'outro' in script_data:
            update_fields['VideoOutro'] = script_data.get('outro', '')
        
        if update_fields:
            await self.airtable_server.update_record(record_id, update_fields)
            print(f"💾 Saved {len(update_fields)} fields to Airtable")
'''

# Find the line with "async def close" or end of class
if "async def close" in content:
    # Insert before close method
    content = content.replace("    async def close", helper_method + "\n    async def close")
elif "# Run the workflow" in content:
    # Insert before the main section
    content = content.replace("\n# Run the workflow", helper_method + "\n\n# Run the workflow")
else:
    # Find the last method in the class
    import re
    # Find all async def methods
    methods = list(re.finditer(r'    async def \w+', content))
    if methods:
        # Get the last method position
        last_method = methods[-1]
        # Find the end of this method (next dedent or end of file)
        end_pos = content.find('\n\n', last_method.end())
        if end_pos > 0:
            content = content[:end_pos] + helper_method + content[end_pos:]

# Write back
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Method added")
