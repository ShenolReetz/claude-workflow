#!/usr/bin/env python3
"""
Fix WordPress MCP initialization - version 2
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Find the __init__ method and add WordPress initialization
wordpress_added = False
for i, line in enumerate(lines):
    # Look for the GoogleDriveAgent initialization
    if 'self.google_drive_agent = GoogleDriveAgent(' in line:
        # Check if WordPress is already initialized nearby
        already_exists = False
        for j in range(max(0, i-10), min(len(lines), i+10)):
            if 'self.wordpress_mcp' in lines[j]:
                already_exists = True
                break
        
        if not already_exists:
            # Add WordPress initialization after GoogleDriveAgent
            # Find the proper indentation
            indent = len(line) - len(line.lstrip())
            wordpress_init = ' ' * indent + '\n'
            wordpress_init += ' ' * indent + '# Initialize WordPress MCP\n'
            wordpress_init += ' ' * indent + 'self.wordpress_mcp = WordPressMCP(self.config)\n'
            
            # Insert after the current line
            lines.insert(i + 1, wordpress_init)
            wordpress_added = True
            print(f"✅ Added WordPress MCP initialization after line {i+1}")
            break

if not wordpress_added:
    # Alternative: Find where self.config is set and add after all other initializations
    for i, line in enumerate(lines):
        if 'self.text_control_agent = TextGenerationControlAgent' in line:
            # Check if WordPress is already initialized
            already_exists = False
            for j in range(i, min(len(lines), i+20)):
                if 'self.wordpress_mcp' in lines[j]:
                    already_exists = True
                    break
            
            if not already_exists:
                # Find the end of current initializations
                j = i
                while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('self.')):
                    j += 1
                
                # Add WordPress initialization
                indent = len(lines[i]) - len(lines[i].lstrip())
                wordpress_init = '\n'
                wordpress_init += ' ' * indent + '# Initialize WordPress MCP\n'
                wordpress_init += ' ' * indent + 'self.wordpress_mcp = WordPressMCP(self.config)\n'
                
                lines.insert(j, wordpress_init)
                wordpress_added = True
                print(f"✅ Added WordPress MCP initialization after line {j}")
                break

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(lines)

if wordpress_added:
    print("\n✅ WordPress MCP initialization added successfully!")
else:
    print("\n❌ Could not add WordPress initialization. Showing __init__ method:")
    # Show the __init__ method for manual inspection
    in_init = False
    for line in lines:
        if 'def __init__(self):' in line:
            in_init = True
        elif in_init and line.strip() and not line.startswith('        '):
            break
        if in_init:
            print(line.rstrip())
