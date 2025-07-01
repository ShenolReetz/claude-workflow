#!/usr/bin/env python3
"""
Add generate_single_product method to ContentGenerationMCPServer
"""

# Read the content generation server
with open('/home/claude-workflow/mcp_servers/content_generation_server.py', 'r') as f:
    content = f.read()

# Check if method already exists
if 'generate_single_product' not in content:
    # Add the method before the last line of the class
    method_code = '''
    
    async def generate_single_product(self, prompt: str) -> str:
        """Generate a single product based on specific requirements"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Error generating single product: {e}")
            return None
'''
    
    # Find the end of the class (before if __name__)
    class_end = content.rfind('\n\nif __name__')
    if class_end > 0:
        content = content[:class_end] + method_code + content[class_end:]
    else:
        # Try another pattern
        class_end = content.rfind('\n\n#')
        if class_end > 0:
            content = content[:class_end] + method_code + content[class_end:]
    
    # Save the updated file
    with open('/home/claude-workflow/mcp_servers/content_generation_server.py', 'w') as f:
        f.write(content)
    
    print("✅ Added generate_single_product method")
else:
    print("✅ generate_single_product method already exists")
