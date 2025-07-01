#!/usr/bin/env python3
"""
Fix all API key parameter instances in workflow runner
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    lines = f.readlines()

# Fix any line that has ContentGenerationMCPServer with anthropic_api_key
fixed_lines = []
for line in lines:
    if 'ContentGenerationMCPServer' in line and 'anthropic_api_key=' in line:
        line = line.replace('anthropic_api_key=', 'api_key=')
    fixed_lines.append(line)

# Write the fixed content
with open('src/workflow_runner.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed all API key parameter instances")

# Let's also verify the change
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()
    if 'anthropic_api_key=' in content and 'ContentGenerationMCPServer' in content:
        print("⚠️ Warning: Still found anthropic_api_key references")
    else:
        print("✅ All anthropic_api_key references have been fixed")
