#!/usr/bin/env python3
"""
Fix the save_generated_content method to properly extract and save products
"""

# Read the Airtable server
with open('mcp_servers/airtable_server.py', 'r') as f:
    content = f.read()

# Check if save_generated_content exists
if 'def save_generated_content' not in content:
    print("⚠️ save_generated_content method not found. Adding it...")
    
    # Find where to add the method (before the last closing or at the end of the class)
    # Add the method before the close of the AirtableMCPServer class
    new_method = '''
    async def save_generated_content(self, record_id: str, content_data: dict) -> bool:
        """Save generated content to Airtable record"""
        try:
            fields = {}
            
            # Save keywords
            if 'keywords' in content_data and content_data['keywords']:
                fields['KeyWords'] = ', '.join(content_data['keywords'])
            
            # Save optimized title
            if 'optimized_title' in content_data and content_data['optimized_title']:
                fields['VideoTitle'] = content_data['optimized_title']
            
            # Extract and save products from script
            if 'script' in content_data and content_data['script']:
                script = content_data['script']
                if 'products' in script:
                    products = script.get('products', [])
                    for product in products:
                        product_num = product.get('number', 0)
                        if 1 <= product_num <= 5:
                            fields[f'ProductNo{product_num}Title'] = product.get('title', '')
                            fields[f'ProductNo{product_num}Description'] = product.get('description', '')
            
            # Update the record
            if fields:
                print(f"📝 Saving to fields: {list(fields.keys())}")
                await self.update_record(record_id, fields)
                
                # Count what we saved
                product_count = sum(1 for key in fields.keys() if 'ProductNo' in key and 'Title' in key)
                print(f"   📊 Saved: Keywords, VideoTitle, VideoDescription, and {product_count} products")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error saving content: {e}")
            return False
'''
    
    # Find the right place to insert (before the last method or end of class)
    import re
    
    # Try to find the end of the AirtableMCPServer class
    class_pattern = r'(class AirtableMCPServer.*?)((?=\nclass|\Z))'
    match = re.search(class_pattern, content, re.DOTALL)
    
    if match:
        # Insert the method at the end of the class
        class_content = match.group(1)
        # Remove any trailing whitespace and add our method
        class_content = class_content.rstrip() + '\n' + new_method + '\n'
        
        # Replace in the content
        content = content[:match.start()] + class_content + content[match.end(1):]
        
        print("✅ Added save_generated_content method to AirtableMCPServer")
    else:
        print("❌ Could not find AirtableMCPServer class")
        
else:
    print("✅ save_generated_content method exists. Checking if it handles products...")
    
    # Check if the existing method properly handles products
    method_start = content.find('def save_generated_content')
    method_end = content.find('\n    def ', method_start + 1)
    if method_end == -1:
        method_end = content.find('\nclass ', method_start + 1)
    if method_end == -1:
        method_end = len(content)
    
    method_content = content[method_start:method_end]
    
    if 'ProductNo' not in method_content:
        print("⚠️ Method doesn't handle products. Need to update it.")
        # Show the current method
        print("\nCurrent method:")
        print(method_content[:500] + "..." if len(method_content) > 500 else method_content)

# Write the updated content
with open('mcp_servers/airtable_server.py', 'w') as f:
    f.write(content)
