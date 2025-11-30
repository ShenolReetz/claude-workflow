#!/usr/bin/env python3
"""
Production Content Generation MCP Server
=========================================
Real MCP server for AI-powered content generation across all platforms.

Tools:
- generate_seo_keywords: Generate SEO keywords for product
- optimize_title: Optimize title for engagement
- generate_video_script: Generate video narration script
- generate_platform_content: Generate YouTube, Instagram, WordPress content
- generate_product_descriptions: Enhance product descriptions
- generate_hashtags: Generate trending hashtags

This MCP consolidates:
- production-content-generation
- production-variant-generator
- title optimization
- hashtag optimization
"""

import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

sys.path.append('/home/claude-workflow')

from mcp_servers.production_content_generation_server import ProductionContentGenerationMCPServer

srv = Server("production-content-generation")

@srv.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="generate_seo_keywords",
            description="Generate SEO keywords for a product using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Product title"},
                    "category": {"type": "string", "description": "Product category"}
                },
                "required": ["title", "category"]
            }
        ),
        Tool(
            name="optimize_title",
            description="Optimize title for maximum social media engagement",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_title": {"type": "string", "description": "Original title"},
                    "keywords": {"type": "array", "items": {"type": "string"}, "description": "SEO keywords to include"}
                },
                "required": ["base_title"]
            }
        ),
        Tool(
            name="generate_video_script",
            description="Generate video narration script (intro, product descriptions, outro)",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Video title"},
                    "products": {
                        "type": "array",
                        "description": "Array of products (name, price, rating)",
                        "items": {"type": "object"}
                    }
                },
                "required": ["title", "products"]
            }
        ),
        Tool(
            name="generate_platform_content",
            description="Generate platform-specific content (YouTube, Instagram, WordPress)",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "category": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "category"]
            }
        ),
        Tool(
            name="generate_product_descriptions",
            description="Generate enhanced product descriptions",
            inputSchema={
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "description": "Array of products to enhance",
                        "items": {"type": "object"}
                    }
                },
                "required": ["products"]
            }
        ),
        Tool(
            name="generate_hashtags",
            description="Generate trending hashtags for social media",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Product title"},
                    "category": {"type": "string", "description": "Product category"},
                    "count": {"type": "number", "default": 30, "description": "Number of hashtags"}
                },
                "required": ["title", "category"]
            }
        ),
    ]

@srv.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Failed to load config: {str(e)}"}))]

    generator = ProductionContentGenerationMCPServer(config.get('openai_api_key'))

    if name == "generate_seo_keywords":
        title = arguments.get("title")
        category = arguments.get("category")
        keywords = await generator.generate_seo_keywords(title, category)
        return [TextContent(type="text", text=json.dumps({"keywords": keywords}, indent=2))]

    elif name == "optimize_title":
        base_title = arguments.get("base_title")
        keywords = arguments.get("keywords", [])
        optimized = await generator.optimize_title(base_title, keywords)
        return [TextContent(type="text", text=json.dumps({"optimized_title": optimized}, indent=2))]

    elif name == "generate_video_script":
        title = arguments.get("title")
        products = arguments.get("products", [])
        scripts = await generator.generate_countdown_script(title, products)
        return [TextContent(type="text", text=json.dumps(scripts, indent=2))]

    elif name == "generate_platform_content":
        title = arguments.get("title")
        category = arguments.get("category")
        keywords = arguments.get("keywords", [])
        content = await generator.generate_platform_content(title, category, keywords)
        return [TextContent(type="text", text=json.dumps(content, indent=2))]

    elif name == "generate_product_descriptions":
        products = arguments.get("products", [])
        enhanced = await generator.generate_product_descriptions(products)
        return [TextContent(type="text", text=json.dumps({"products": enhanced}, indent=2))]

    elif name == "generate_hashtags":
        title = arguments.get("title")
        category = arguments.get("category")
        count = arguments.get("count", 30)

        # Generate hashtags using keywords
        keywords = await generator.generate_seo_keywords(title, category)
        hashtags = [f"#{kw.replace(' ', '').replace('-', '')}" for kw in keywords[:count]]

        return [TextContent(type="text", text=json.dumps({"hashtags": hashtags}, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

async def main():
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())
