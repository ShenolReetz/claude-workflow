#!/usr/bin/env python3
"""
Fix the complete file structure
"""

# Read the file
with open('/home/claude-workflow/src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find where the helper method starts
helper_start = content.find('async def _save_countdown_to_airtable')

if helper_start > 0:
    # Find the main function or end of file
    main_start = content.find('async def main():', helper_start)
    if_name_start = content.find('if __name__', helper_start)
    
    # Get the part before helper
    before_helper = content[:helper_start]
    
    # Create the complete helper method
    helper_method = '''    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
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


# Run the workflow
async def main():
    orchestrator = ContentPipelineOrchestrator()
    await orchestrator.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    # If we found the main function, keep it
    if main_start > 0 and main_start > helper_start:
        after_part = content[main_start:]
        # Fix any **name** to __name__
        after_part = after_part.replace('**name**', '__name__')
        new_content = before_helper + helper_method[:-55] + '\n\n' + after_part  # Remove the duplicate main/if name from helper
    else:
        new_content = before_helper + helper_method
    
    # Fix any remaining **name** issues
    new_content = new_content.replace('**name**', '__name__')
    
    # Write back
    with open('/home/claude-workflow/src/workflow_runner.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed complete file structure")
else:
    print("❌ Could not find helper method")
