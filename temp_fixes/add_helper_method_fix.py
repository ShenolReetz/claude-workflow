#!/usr/bin/env python3
"""
Fix: Add the missing _save_countdown_to_airtable method
"""

# Read workflow_runner.py
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find the ContentPipelineOrchestrator class
class_found = False
insert_index = -1

for i, line in enumerate(lines):
    if 'class ContentPipelineOrchestrator:' in line:
        class_found = True
    
    # Find a good place to insert (before run_complete_workflow ends or before async def close)
    if class_found and ('async def close(' in line or '# Run the workflow' in line):
        insert_index = i
        break

if insert_index > 0:
    # Insert the helper method
    helper_method = '''    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
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
    
    # Insert the method
    lines.insert(insert_index, helper_method + '\n')
    
    # Write back
    with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Added helper method at line {insert_index}")
else:
    print("❌ Could not find insertion point")
