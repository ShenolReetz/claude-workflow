#!/usr/bin/env python3
"""
Fix missing imports and remove duplicate initialization
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# 1. Add missing GoogleDriveAgent import
if 'from mcp.google_drive_agent_mcp import GoogleDriveAgent' not in content:
    # Find where to add the import (after other mcp imports)
    wordpress_import = content.find('from mcp.wordpress_mcp import WordPressMCP')
    if wordpress_import > 0:
        line_end = content.find('\n', wordpress_import)
        new_import = '\nfrom mcp.google_drive_agent_mcp import GoogleDriveAgent'
        content = content[:line_end] + new_import + content[line_end:]
        print("✅ Added GoogleDriveAgent import")
    else:
        # Add after amazon import
        amazon_import = content.find('from mcp.amazon_affiliate_agent_mcp import')
        if amazon_import > 0:
            line_end = content.find('\n', amazon_import)
            new_import = '\nfrom mcp.google_drive_agent_mcp import GoogleDriveAgent'
            content = content[:line_end] + new_import + content[line_end:]
            print("✅ Added GoogleDriveAgent import")

# 2. Remove duplicate initialization
# Find and remove the duplicate WordPress and GoogleDrive initialization
lines = content.split('\n')
cleaned_lines = []
skip_next = 0

for i, line in enumerate(lines):
    if skip_next > 0:
        skip_next -= 1
        continue
        
    # Check for duplicate initialization pattern
    if i < len(lines) - 5:
        if (lines[i].strip() == '# Initialize Google Drive agent' and
            lines[i+1].strip() == 'self.google_drive_agent = GoogleDriveAgent()' and
            lines[i+2].strip() == '' and
            lines[i+3].strip() == '# Initialize WordPress MCP' and
            lines[i+4].strip() == 'self.wordpress_mcp = WordPressMCP(self.config)'):
            
            # Check if this is a duplicate (appears after line 45)
            if i > 45:
                print(f"✅ Removed duplicate initialization at line {i+1}")
                skip_next = 4  # Skip the next 4 lines
                continue
    
    cleaned_lines.append(line)

# Rejoin the content
content = '\n'.join(cleaned_lines)

# Write back
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

# Verify imports
print("\n=== Verifying imports ===")
imports = []
for line in content.split('\n'):
    if line.startswith('from ') or line.startswith('import '):
        imports.append(line)
        if 'GoogleDriveAgent' in line or 'WordPressMCP' in line:
            print(f"✅ {line}")

print("\n=== Verifying initialization (no duplicates) ===")
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'self.google_drive_agent' in line or 'self.wordpress_mcp' in line:
        print(f"Line {i+1}: {line.strip()}")
