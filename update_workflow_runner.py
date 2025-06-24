#!/usr/bin/env python3
"""
Script to update workflow_runner.py with Text Generation Control
"""

import re

# Read the current workflow_runner.py
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# 1. Add import at the top (find other imports)
import_pattern = r'(from mcp_servers\.content_generation_server import ContentGenerationMCPServer)'
import_replacement = r'\1\nfrom mcp.text_generation_control_agent_mcp_v2 import run_text_control_with_regeneration'

content = re.sub(import_pattern, import_replacement, content)

# 2. Add text control after countdown script generation
# Find the section after generate_countdown_script
control_code = '''
        
        # Step 4.5: Text Generation Quality Control
        print("🎮 Running text generation quality control...")
        
        # First, we need to save the countdown script to Airtable
        await self._save_countdown_to_airtable(pending_title['record_id'], script_data)
        
        # Now run quality control
        control_result = await run_text_control_with_regeneration(self.config, pending_title['record_id'])
        
        if not control_result['success']:
            print(f"❌ Text control failed after {control_result.get('attempts', 0)} attempts")
            print(f"Issues: {control_result.get('error', 'Unknown error')}")
            # Continue anyway but log the issue
            await self.airtable_server.update_record(pending_title['record_id'], {
                'TextControlStatus': 'Failed',
                'Status': 'Processing'  # Keep processing but note the failure
            })
        elif control_result['all_valid']:
            print(f"✅ Text validated after {control_result['attempts']} attempt(s)")
            await self.airtable_server.update_record(pending_title['record_id'], {
                'TextControlStatus': 'Validated'
            })
'''

# Find where to insert (after script_data assignment)
pattern = r'(script_data = await self\.content_server\.generate_countdown_script\([^)]+\))'
replacement = r'\1' + control_code

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 3. Add helper method to save countdown to Airtable (if not exists)
if '_save_countdown_to_airtable' not in content:
    helper_method = '''
    
    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script products to Airtable"""
        update_fields = {}
        
        # Save each product
        for i, product in enumerate(script_data.get('products', [])):
            product_num = i + 1
            update_fields[f'ProductNo{product_num}Title'] = product.get('title', '')
            update_fields[f'ProductNo{product_num}Description'] = product.get('description', '')
        
        # Save intro/outro if present
        if 'intro' in script_data:
            update_fields['VideoIntro'] = script_data['intro']
        if 'outro' in script_data:
            update_fields['VideoOutro'] = script_data['outro']
        
        await self.airtable_server.update_record(record_id, update_fields)
'''
    
    # Add before the last line of the class
    class_end = content.rfind('\n\n# Run the workflow')
    if class_end > 0:
        content = content[:class_end] + helper_method + content[class_end:]

# Save the updated file
with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Updated workflow_runner.py with Text Generation Control")
print("✅ Added import statement")
print("✅ Added text control after countdown generation")
print("✅ Added helper method to save countdown to Airtable")
