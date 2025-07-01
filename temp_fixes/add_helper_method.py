#!/usr/bin/env python3
"""
Add missing _save_countdown_to_airtable helper method
"""

# Read workflow_runner.py
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Check if method exists
if '_save_countdown_to_airtable' not in content.split('def _save_countdown_to_airtable')[0]:
    # Add the method before the run_complete_workflow method ends
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
    
    # Find where to insert (before the last method or before main)
    insertion_point = content.rfind('\n\n# Run the workflow')
    if insertion_point > 0:
        content = content[:insertion_point] + helper_method + content[insertion_point:]
    
    # Save updated file
    with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
        f.write(content)
    
    print("✅ Added _save_countdown_to_airtable helper method")
else:
    print("✅ Helper method already exists")
