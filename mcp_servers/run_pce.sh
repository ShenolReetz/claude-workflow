#!/usr/bin/env bash
set -euo pipefail

# Load API key from config file (since we don't have /etc/claude-secrets yet)
# In production, you should use a more secure location
if [ -f "/home/claude-workflow/config/api_keys.json" ]; then
    export OPENAI_API_KEY=$(python3 -c "import json; print(json.load(open('/home/claude-workflow/config/api_keys.json'))['openai_api_key'])")
fi

# Execute the MCP server
exec python3 /home/claude-workflow/mcp_servers/product_category_extractor.py