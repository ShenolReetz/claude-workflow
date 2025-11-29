#!/usr/bin/env python3
"""
Production Amazon Scraper MCP Server
====================================
Real MCP server for Amazon product scraping with variant generation.

Tools:
- scrape_product: Scrape single product by URL
- search_products: Search for products by title with variants
- validate_product: Validate product exists and has reviews
"""

import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

sys.path.append('/home/claude-workflow')

from mcp_servers.production_progressive_amazon_scraper_async import ProductionProgressiveAmazonScraperAsync

srv = Server("production-amazon-scraper")

@srv.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="scrape_product",
            description="Scrape Amazon product data by URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_url": {"type": "string", "description": "Amazon product URL"}
                },
                "required": ["product_url"]
            }
        ),
        Tool(
            name="search_products",
            description="Search for Amazon products by title with intelligent variant generation",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Product title to search"},
                    "target_products": {"type": "number", "default": 5, "description": "Number of products to find"},
                    "min_reviews": {"type": "number", "default": 10, "description": "Minimum reviews required"}
                },
                "required": ["title"]
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

    scraper = ProductionProgressiveAmazonScraperAsync(
        config.get('scrapingdog_api_key'),
        config.get('openai_api_key')
    )

    if name == "scrape_product":
        product_url = arguments.get("product_url")
        try:
            result = await scraper.scrape_product_async(product_url)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "search_products":
        title = arguments.get("title")
        target_products = arguments.get("target_products", 5)
        min_reviews = arguments.get("min_reviews", 10)

        try:
            products, best_variant = await scraper.search_with_variants_async(
                title, target_products, min_reviews
            )
            result = {
                "products": products,
                "best_variant": best_variant,
                "total_found": len(products)
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

async def main():
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())
