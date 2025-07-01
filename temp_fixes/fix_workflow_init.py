#!/usr/bin/env python3
"""
Fix the ContentGenerationMCPServer initialization
"""

import re

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Use regex to find and fix the ContentGenerationMCPServer initialization
# This pattern will match multi-line initialization
pattern = r'(self\.content_server\s*=\s*ContentGenerationMCPServer\s*\(\s*\n?\s*)anthropic_api_key='
replacement = r'\1api_key='

content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Also fix single-line instances
content = content.replace('ContentGenerationMCPServer(anthropic_api_key=', 'ContentGenerationMCPServer(api_key=')

# Write the fixed content
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed ContentGenerationMCPServer initialization")

# Verify the fix
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()
    # Find the line around the initialization
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'ContentGenerationMCPServer' in line:
            print(f"Line {i+1}: {line}")
            if i+1 < len(lines) and 'anthropic_api_key' in lines[i+1]:
                print(f"Line {i+2}: {lines[i+1]}")
                print("⚠️ Still needs fixing!")
