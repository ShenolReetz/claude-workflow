#!/usr/bin/env python3
"""
Fix workflow runner to use OpenAI API key
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Change from anthropic_api_key to openai_api_key
content = content.replace(
    "api_key=self.config['anthropic_api_key']",
    "api_key=self.config['openai_api_key']"
)

# Write the fixed content
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Updated workflow runner to use OpenAI API key")
