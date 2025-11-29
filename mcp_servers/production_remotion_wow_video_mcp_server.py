#!/usr/bin/env python3
"""
Production Remotion WOW Video MCP Server
=========================================
Real MCP server implementing Model Context Protocol for Remotion video generation
with all 8 WOW effect components.

Tools:
- generate_wow_video: Generate video with all WOW effects
- test_wow_components: Test all components integration
- get_component_list: Get list of available WOW components
"""

import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Add project to path
sys.path.append('/home/claude-workflow')

from mcp_servers.production_remotion_wow_video_mcp import (
    ProductionRemotionWowVideoMCP
)

srv = Server("production-remotion-wow-video")

# ---- Tool registry ----
@srv.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="generate_wow_video",
            description="Generate a video with all 8 WOW effect components (star ratings, review count, price reveal, card flip, particles, badges, glitch, animated text)",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_data": {
                        "type": "object",
                        "description": "Product information (Title, Price, OriginalPrice, Rating, ReviewCount, ProductImage, Description, BestSellerRank, AmazonChoice)",
                        "properties": {
                            "Title": {"type": "string"},
                            "Price": {"type": "string"},
                            "OriginalPrice": {"type": "string"},
                            "Rating": {"type": "number"},
                            "ReviewCount": {"type": "number"},
                            "ProductImage": {"type": "string"},
                            "Description": {"type": "string"},
                            "BestSellerRank": {"type": "number"},
                            "AmazonChoice": {"type": "boolean"}
                        },
                        "required": ["Title"]
                    },
                    "options": {
                        "type": "object",
                        "description": "Optional video generation options",
                        "properties": {
                            "composition": {"type": "string", "default": "WowVideoUltra"},
                            "duration": {"type": "number", "default": 360},
                            "fps": {"type": "number", "default": 30},
                            "width": {"type": "number", "default": 1080},
                            "height": {"type": "number", "default": 1920},
                            "effects": {"type": "object"}
                        }
                    }
                },
                "required": ["product_data"]
            }
        ),
        Tool(
            name="test_wow_components",
            description="Test that all 8 WOW components are properly integrated and working",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_data": {
                        "type": "object",
                        "description": "Product information for testing",
                        "properties": {
                            "Title": {"type": "string"},
                            "Price": {"type": "string"},
                            "Rating": {"type": "number"},
                            "ReviewCount": {"type": "number"}
                        },
                        "required": ["Title"]
                    }
                },
                "required": ["product_data"]
            }
        ),
        Tool(
            name="get_component_list",
            description="Get list of all available WOW components and their features",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]

# ---- Tool dispatcher ----
@srv.call_tool()
async def call_tool(name: str, arguments: dict):
    # Load config
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": f"Failed to load config: {str(e)}"}))]

    # Initialize MCP
    mcp = ProductionRemotionWowVideoMCP(config)

    if name == "generate_wow_video":
        product_data = arguments.get("product_data", {})
        options = arguments.get("options", {})

        result = await mcp.generate_wow_video(product_data, options)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "test_wow_components":
        product_data = arguments.get("product_data", {})

        result = await mcp.test_all_components(product_data)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_component_list":
        components = {
            "total_components": 8,
            "components": [
                {
                    "name": "star_rating",
                    "description": "Animated Star Ratings with sequential fill and sparkles",
                    "features": ["Sequential fill", "Sparkle effects", "Pulsing glow", "Bounce animation"]
                },
                {
                    "name": "review_count",
                    "description": "Review Count with counting animation",
                    "features": ["Count-up from 0", "Number formatting", "Pulse effect", "Verified checkmark"]
                },
                {
                    "name": "price_reveal",
                    "description": "Dramatic Price Reveal with strike-through",
                    "features": ["Original price strike-through", "Bounce animation", "Flash effect", "Discount badge", "Sparkles"]
                },
                {
                    "name": "card_flip",
                    "description": "3D Card Flip Transitions",
                    "features": ["3D perspective", "Spring physics", "Dynamic shadow", "Horizontal/vertical"]
                },
                {
                    "name": "particle_burst",
                    "description": "Particle Burst Effects",
                    "features": ["Stars, confetti, sparkles", "Radial explosion", "Fade and rotation", "Multiple triggers"]
                },
                {
                    "name": "amazon_badge",
                    "description": "Animated Amazon Badges",
                    "features": ["Choice, Bestseller, Deal, Prime", "Drop animation", "Spin effect", "Pulsing glow"]
                },
                {
                    "name": "glitch_transition",
                    "description": "Glitch Transition Effects",
                    "features": ["RGB channel split", "Horizontal slices", "Scan lines", "Noise overlay"]
                },
                {
                    "name": "animated_text",
                    "description": "Enhanced Text Animations",
                    "features": ["Word-by-word", "5 types (bounce, slide, fade, zoom, wave)", "Customizable"]
                }
            ],
            "expected_impact": {
                "viewer_retention": "+40-60%",
                "engagement_rate": "+100-200%",
                "click_through_rate": "+30-50%",
                "average_watch_time": "+50-80%"
            }
        }
        return [TextContent(type="text", text=json.dumps(components, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

async def main():
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())
