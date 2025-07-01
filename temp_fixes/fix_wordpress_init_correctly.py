#!/usr/bin/env python3
"""
Correctly add WordPress MCP initialization to __init__ method
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find the ContentGenerationMCPServer initialization and add WordPress after it
search_pattern = '''        self.content_server = ContentGenerationMCPServer(
            anthropic_api_key=self.config['anthropic_api_key']
        )'''

if search_pattern in content:
    # Add WordPress initialization after content_server
    wordpress_init = '''

        # Initialize Google Drive agent
        self.google_drive_agent = GoogleDriveAgent()
        
        # Initialize WordPress MCP
        self.wordpress_mcp = WordPressMCP(self.config)'''
    
    # Replace the pattern with pattern + wordpress init
    content = content.replace(search_pattern, search_pattern + wordpress_init)
    
    print("✅ Added WordPress MCP initialization after ContentGenerationMCPServer")
else:
    print("❌ Could not find ContentGenerationMCPServer initialization pattern")
    print("Trying alternative approach...")
    
    # Alternative: Find where content_server is initialized
    if 'self.content_server = ContentGenerationMCPServer(' in content:
        # Find the closing parenthesis
        start = content.find('self.content_server = ContentGenerationMCPServer(')
        end = content.find(')', start) + 1
        
        # Add WordPress initialization after
        wordpress_init = '''
        
        # Initialize Google Drive agent
        self.google_drive_agent = GoogleDriveAgent()
        
        # Initialize WordPress MCP
        self.wordpress_mcp = WordPressMCP(self.config)'''
        
        content = content[:end] + wordpress_init + content[end:]
        print("✅ Added WordPress MCP initialization (alternative method)")

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

# Verify the change
print("\n=== Verifying initialization ===")
with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()
    
in_init = False
for i, line in enumerate(lines):
    if 'def __init__(self):' in line:
        in_init = True
        print("Found __init__ method:")
    elif in_init and line.strip() and not line[0].isspace():
        break
    if in_init:
        print(f"{i+1}: {line.rstrip()}")
