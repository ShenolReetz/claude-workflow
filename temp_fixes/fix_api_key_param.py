#!/usr/bin/env python3
"""
Fix the API key parameter name in workflow runner
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Fix the parameter name from anthropic_api_key to api_key
content = content.replace(
    "self.content_server = ContentGenerationMCPServer(\n                          anthropic_api_key=",
    "self.content_server = ContentGenerationMCPServer(\n                          api_key="
)

# Also check for any other instances
content = content.replace(
    "ContentGenerationMCPServer(anthropic_api_key=",
    "ContentGenerationMCPServer(api_key="
)

# Write the fixed content
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Fixed API key parameter name in workflow runner")
