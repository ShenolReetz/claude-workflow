#!/usr/bin/env python3
"""
Update Claude model name to current version
"""

# Read the content generation server
with open('mcp_servers/content_generation_server.py', 'r') as f:
    content = f.read()

# Update the model name to current version
# Try claude-3-5-sonnet-latest first, or claude-3-5-sonnet-20241022
old_model = "claude-3-sonnet-20240229"
new_model = "claude-3-5-sonnet-20241022"  # Latest Sonnet 3.5 model

content = content.replace(old_model, new_model)

# Write the fixed content
with open('mcp_servers/content_generation_server.py', 'w') as f:
    f.write(content)

print(f"✅ Updated Claude model from {old_model} to {new_model}")

# Verify the change
with open('mcp_servers/content_generation_server.py', 'r') as f:
    if new_model in f.read():
        print("✅ Model name successfully updated")
    else:
        print("⚠️ Model name update may have failed")
