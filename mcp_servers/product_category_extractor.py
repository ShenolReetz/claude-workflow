#!/usr/bin/env python3
import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent  # use available types in your SDK

srv = Server("product-category-extractor")

# ---- Tool registry (list_tools) ----
@srv.list_tools()  # this decorator exists in older SDKs
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="extract_category",
            description="Extract main category, subcategory, keywords from an Amazon-like product title",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "model": {"type": "string", "default": "gpt-4o"}
                },
                "required": ["title"]
            },
        ),
        Tool(
            name="batch_extract_categories",
            description="Batch category extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "titles": {"type": "array", "items": {"type": "string"}},
                    "model": {"type": "string", "default": "gpt-4o"}
                },
                "required": ["titles"]
            },
        ),
    ]

# ---- Tool dispatcher (call_tool) ----
@srv.call_tool()
async def call_tool(name: str, arguments: dict):
    # Make sure your API key is present
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Try to read from config file as fallback
        try:
            with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('openai_api_key')
        except:
            pass
    
    if not api_key:
        # Return a structured error as text; older SDKs may not have ErrorContent
        return [TextContent(type="text", text=json.dumps({"error":"OPENAI_API_KEY missing"}))]

    if name == "extract_category":
        title = arguments["title"]
        result = await extract_one(title, api_key, arguments.get("model", "gpt-4o"))
        return [TextContent(type="text", text=json.dumps(result))]
    elif name == "batch_extract_categories":
        titles = arguments["titles"]
        model = arguments.get("model", "gpt-4o")
        out = []
        for t in titles:
            out.append(await extract_one(t, api_key, model))
        return [TextContent(type="text", text=json.dumps(out))]
    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

# ---- Your actual logic ----
async def extract_one(title: str, api_key: str, model: str):
    """Extract category information from a product title using OpenAI"""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""Analyze this product title and determine its category: "{title}"
        
        Return ONLY a valid JSON object with:
        - category: Main product category (e.g., Electronics, Home & Kitchen, Beauty, etc.)
        - subcategory: Specific subcategory
        - keywords: 5 relevant category keywords
        
        Example response:
        {{"category": "Electronics", "subcategory": "Cameras", "keywords": ["camera", "photography", "video", "action", "recording"]}}
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at categorizing products. Return only valid JSON."},
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
        # Return fallback data on error
        return {
            "title": title,
            "error": str(e),
            "category": "General",
            "subcategory": "",
            "keywords": [],
            "model_used": model
        }

async def main():
    # Use the server helper to create init options compatible with your version
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())