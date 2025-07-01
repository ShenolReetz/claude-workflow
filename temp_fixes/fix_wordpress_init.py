#!/usr/bin/env python3
"""
Fix WordPress MCP initialization in ContentPipelineOrchestrator
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find the __init__ method of ContentPipelineOrchestrator
init_start = content.find('class ContentPipelineOrchestrator:')
if init_start > 0:
    # Find the __init__ method
    init_method_start = content.find('def __init__(self):', init_start)
    if init_method_start > 0:
        # Find where to add WordPress initialization
        # Look for where other MCPs are initialized
        google_drive_init = content.find('self.google_drive_agent = GoogleDriveAgent(', init_method_start)
        
        if google_drive_init > 0:
            # Find the end of the google drive initialization line
            line_end = content.find('\n', google_drive_init)
            
            # Check if WordPress MCP is already initialized
            if 'self.wordpress_mcp = WordPressMCP' not in content[init_method_start:google_drive_init + 500]:
                # Add WordPress initialization
                wordpress_init = '''
        
        # Initialize WordPress MCP
        self.wordpress_mcp = WordPressMCP(self.config)'''
                
                content = content[:line_end] + wordpress_init + content[line_end:]
                print("✅ Added WordPress MCP initialization in __init__ method")
            else:
                print("ℹ️ WordPress MCP already initialized")
        else:
            print("❌ Could not find GoogleDriveAgent initialization")
    else:
        print("❌ Could not find __init__ method")
else:
    print("❌ Could not find ContentPipelineOrchestrator class")

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

# Verify the initialization
print("\n=== Verifying WordPress initialization ===")
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()
    
# Check if WordPress MCP is initialized
if 'self.wordpress_mcp = WordPressMCP(self.config)' in content:
    print("✅ WordPress MCP initialization found in code")
    
    # Find and show the context
    init_pos = content.find('self.wordpress_mcp = WordPressMCP(self.config)')
    if init_pos > 0:
        # Show a few lines before and after
        start = max(0, init_pos - 100)
        end = min(len(content), init_pos + 150)
        print("\nContext:")
        print("..." + content[start:end] + "...")
else:
    print("❌ WordPress MCP initialization NOT found")
