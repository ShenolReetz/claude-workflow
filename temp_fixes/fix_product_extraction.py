#!/usr/bin/env python3
"""
Fix product extraction and saving to Airtable
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find where content is saved to Airtable and add product extraction
# We need to find the section after content_data is created
lines = content.split('\n')

# Find the content_data section
for i, line in enumerate(lines):
    if "'script': script_result," in line:
        print(f"Found script_result at line {i+1}")
        # Look for the next 50 lines to find where it's saved
        for j in range(i, min(len(lines), i+50)):
            if 'airtable' in lines[j].lower() or 'update_record' in lines[j].lower():
                print(f"Found Airtable save at line {j+1}: {lines[j]}")
                break

# Now let's properly fix the saving logic
# We need to add code to extract products from script_result
product_extraction = '''
            # Extract products from script_result
            fields_to_save = {
                'KeyWords': ', '.join(keywords_result) if keywords_result else '',
                'VideoTitle': optimized_title if optimized_title else ''
            }
            
            # Extract and save products
            if script_result and 'products' in script_result:
                products = script_result.get('products', [])
                for product in products:
                    product_num = product.get('number', 0)
                    if 1 <= product_num <= 5:
                        fields_to_save[f'ProductNo{product_num}Title'] = product.get('title', '')
                        fields_to_save[f'ProductNo{product_num}Description'] = product.get('description', '')
'''

# Search for where we can insert this
import re

# Pattern to find the update_record call
pattern = r"(await self\.airtable_server\.update_record\([^{]*{)"

# Function to add our extraction code before the update_record call
def add_extraction(match):
    return product_extraction + "\n            " + match.group(1)

# Apply the fix
if re.search(pattern, content):
    content = re.sub(pattern, add_extraction, content, count=1)
    print("\n✅ Added product extraction logic before Airtable update")
else:
    print("\n❌ Could not find update_record pattern. Showing relevant section...")
    # Show the section for manual inspection
    for i, line in enumerate(lines):
        if 'KeyWords' in line and 'VideoTitle' in line:
            print(f"\nFound field definition at line {i+1}:")
            for j in range(max(0, i-5), min(len(lines), i+15)):
                print(f"{j+1}: {lines[j]}")

# Write the updated content
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)
