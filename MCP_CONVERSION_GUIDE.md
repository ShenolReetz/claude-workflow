# Complete MCP Server Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Implementation](#step-by-step-implementation)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Security Best Practices](#security-best-practices)
6. [Testing and Validation](#testing-and-validation)
7. [Common Issues and Solutions](#common-issues-and-solutions)

## Overview

This guide documents the complete process of implementing a Model Context Protocol (MCP) server for Claude Code, enabling subagents to use custom tools via the MCP protocol.

### What is MCP?
MCP (Model Context Protocol) is an open-source standard that allows Claude to connect to external tools and data sources. MCP servers provide tools, resources, and prompts that can be discovered and used by Claude and its subagents.

### Architecture
```
Claude Code CLI
    ├── MCP Servers (JSON-RPC over stdio)
    │   ├── product-category-extractor
    │   ├── airtable
    │   └── other servers...
    └── Subagents (.claude/agents/)
        ├── amazon-product-expert
        └── other agents...
```

## Prerequisites

### Required Software
- **Node.js**: v18+ 
- **Python**: 3.10+
- **Claude CLI**: v1.0.72+
- **MCP SDK**: `pip install modelcontextprotocol`

### Check Versions
```bash
# Check Claude CLI
claude --version  # Should show 1.0.72 or higher

# Check Node.js
node -v  # Should be v18 or higher

# Check Python
python3 --version  # Should be 3.10+

# Check MCP SDK
python3 -c "import mcp; print('MCP SDK installed')"
```

## Step-by-Step Implementation

### Step 1: Create the MCP Server

Create `/home/claude-workflow/mcp_servers/product_category_extractor.py`:

```python
#!/usr/bin/env python3
import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

srv = Server("product-category-extractor")

# ---- Tool registry ----
@srv.list_tools()
async def list_tools() -> List[Tool]:
    """Define available tools for this MCP server"""
    return [
        Tool(
            name="extract_category",
            description="Extract category from product title",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Product title"},
                    "model": {"type": "string", "default": "gpt-4o"}
                },
                "required": ["title"]
            },
        ),
        Tool(
            name="batch_extract_categories",
            description="Extract categories for multiple products",
            inputSchema={
                "type": "object",
                "properties": {
                    "titles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of product titles"
                    },
                    "model": {"type": "string", "default": "gpt-4o"}
                },
                "required": ["titles"]
            },
        ),
    ]

# ---- Tool dispatcher ----
@srv.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls from clients"""
    
    # Get API key from environment or config
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        try:
            with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('openai_api_key')
        except:
            pass
    
    if not api_key:
        return [TextContent(
            type="text", 
            text=json.dumps({"error": "OPENAI_API_KEY missing"})
        )]

    if name == "extract_category":
        title = arguments["title"]
        result = await extract_one(title, api_key, arguments.get("model", "gpt-4o"))
        return [TextContent(type="text", text=json.dumps(result))]
        
    elif name == "batch_extract_categories":
        titles = arguments["titles"]
        model = arguments.get("model", "gpt-4o")
        results = []
        for title in titles:
            results.append(await extract_one(title, api_key, model))
        return [TextContent(type="text", text=json.dumps(results))]
        
    else:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"})
        )]

# ---- Business logic ----
async def extract_one(title: str, api_key: str, model: str):
    """Extract category information using OpenAI"""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""Analyze this product title: "{title}"
        Return JSON with: category, subcategory, keywords (5 items)"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return only valid JSON"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=150,
            temperature=0.3
        )
        
        result = json.loads(response.choices[0].message.content)
        return {
            "title": title,
            "category": result.get('category', 'General'),
            "subcategory": result.get('subcategory', ''),
            "keywords": result.get('keywords', []),
            "model_used": model
        }
    except Exception as e:
        return {
            "title": title,
            "error": str(e),
            "category": "General",
            "subcategory": "",
            "keywords": [],
            "model_used": model
        }

async def main():
    """Main entry point"""
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 2: Create Secure Wrapper Script

Create `/home/claude-workflow/mcp_servers/run_pce.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Load API key securely
if [ -f "/home/claude-workflow/config/api_keys.json" ]; then
    export OPENAI_API_KEY=$(python3 -c "
import json
with open('/home/claude-workflow/config/api_keys.json') as f:
    print(json.load(f)['openai_api_key'])
")
fi

# Execute MCP server
exec python3 /home/claude-workflow/mcp_servers/product_category_extractor.py
```

Make it executable:
```bash
chmod +x /home/claude-workflow/mcp_servers/run_pce.sh
```

### Step 3: Configure Project Settings

Create `/home/claude-workflow/.claude/settings.json`:

```json
{
  "enableAllProjectMcpServers": true,
  "permissions": {
    "deny": ["Read(./.env)", "Read(./secrets/**)"]
  }
}
```

### Step 4: Register MCP Server

```bash
# Remove any existing registration
claude mcp remove product-category-extractor 2>/dev/null || true

# Add the server using wrapper script
claude mcp add product-category-extractor /home/claude-workflow/mcp_servers/run_pce.sh

# Verify connection
claude mcp list
# Should show: product-category-extractor - ✓ Connected
```

### Step 5: Create Subagent Configuration

Create `/home/claude-workflow/.claude/agents/amazon-product-expert.md`:

```markdown
---
name: amazon-product-expert
description: Extracts categories and optimizes Amazon product data
tools:
  - extract_category
  - batch_extract_categories
  - Read
  - Write
  - Grep
---

You are an Amazon product specialist.

## Using MCP Tools

When asked to categorize products:
- Use `extract_category` for single products: {"title": "product name"}
- Use `batch_extract_categories` for multiple: {"titles": ["p1", "p2"]}

Return structured JSON with category, subcategory, and keywords.

## Core Competencies
- Product categorization using MCP tools
- Title optimization
- Keyword extraction
- Listing validation
```

### Step 6: Reload and Test

```bash
# Reload agents (may fail with credit error)
claude agents reload

# If reload fails due to credits, start new chat in project folder
cd /home/claude-workflow
claude chat
```

## Troubleshooting Guide

### Issue: MCP Server Not Connecting

**Symptom**: `claude mcp list` shows "✗ Failed to connect"

**Solutions**:
1. Test server directly:
   ```bash
   timeout 2 /home/claude-workflow/mcp_servers/run_pce.sh
   # Should run without errors
   ```

2. Check for import errors:
   ```bash
   python3 /home/claude-workflow/mcp_servers/product_category_extractor.py
   ```

3. Verify MCP SDK installation:
   ```bash
   pip install -U modelcontextprotocol
   ```

### Issue: Subagent Can't See MCP Tools

**Symptom**: Agent doesn't list MCP tools as available

**Solutions**:
1. Ensure `enableAllProjectMcpServers: true` in settings.json
2. Check tool names match exactly in agent config
3. Reload agents or start new chat session
4. Verify MCP server is connected (`claude mcp list`)

### Issue: Credit Balance Too Low

**Symptom**: "Credit balance is too low" when reloading agents

**Solutions**:
1. This is Claude CLI billing, not OpenAI
2. Check account at claude.ai
3. Add credits or wait for billing cycle reset
4. MCP servers still work, just can't reload agents

### Issue: SDK Version Incompatibility

**Symptom**: Import errors for InitializationOptions, @srv.tool decorator

**Solutions**:
1. Use compatible patterns:
   ```python
   # Instead of: from mcp.types import InitializationOptions
   # Use: srv.create_initialization_options()
   
   # Instead of: @srv.tool("name", {...})
   # Use: @srv.list_tools() and @srv.call_tool()
   ```

## Security Best Practices

### 1. Never Hardcode Secrets
❌ **Bad**: API keys in source code or /root/.claude.json
✅ **Good**: Use environment variables via wrapper scripts

### 2. Secure File Permissions
```bash
# Config files with secrets
chmod 600 /home/claude-workflow/config/api_keys.json

# Wrapper scripts
chmod 700 /home/claude-workflow/mcp_servers/run_pce.sh
```

### 3. Rotate Compromised Keys
If keys are exposed in logs:
1. Generate new API keys immediately
2. Update config files
3. Restart MCP servers

### 4. Use Dedicated Secrets Directory
```bash
# Create secure directory
sudo mkdir -p /etc/claude-secrets
sudo chmod 700 /etc/claude-secrets

# Store keys securely
echo "your-api-key" | sudo tee /etc/claude-secrets/openai_key
sudo chmod 600 /etc/claude-secrets/openai_key
```

## Testing and Validation

### 1. Test MCP Server Directly
```bash
# Should run without errors
timeout 2 /home/claude-workflow/mcp_servers/run_pce.sh
```

### 2. Verify Connection
```bash
claude mcp list | grep product-category
# Should show: ✓ Connected
```

### 3. Test with Subagent
```bash
cd /home/claude-workflow
claude chat

# In chat:
/agents amazon-product-expert
> List available tools
> Use extract_category to analyze "Sony Headphones WH-1000XM5"
```

### 4. Manual Tool Testing
```python
# Test script
import asyncio
import json

async def test():
    from product_category_extractor import extract_one
    result = await extract_one(
        "Apple MacBook Pro 14-inch",
        "your-api-key",
        "gpt-4o"
    )
    print(json.dumps(result, indent=2))

asyncio.run(test())
```

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| ImportError: InitializationOptions | SDK version mismatch | Use srv.create_initialization_options() |
| @srv.tool not found | Older SDK version | Use @srv.list_tools() pattern |
| Tools not visible to agents | Agents not reloaded | Run `claude agents reload` or start new chat |
| API key missing | Env var not set | Check wrapper script and config file |
| Credit balance low | Claude CLI billing | Add credits to Claude account |
| Server fails to start | Python errors | Check imports and syntax |
| Connection refused | Server not running | Verify wrapper script is executable |

## Summary

This implementation provides:
- ✅ **Working MCP server** using correct SDK patterns
- ✅ **Secure API key handling** via wrapper scripts
- ✅ **Proper agent configuration** with tool access
- ✅ **Connected status** in MCP server list

Current limitation:
- ⚠️ Subagents may not see tools until `claude agents reload` succeeds (requires credits)

The infrastructure is ready and will work once agent reload is possible.