#!/usr/bin/env python3
"""
Production Analytics MCP Server
================================
Real MCP server for analytics tracking and cost monitoring across all platforms.

Tools:
- track_video: Track performance for a single video
- track_all_published: Track all published videos
- get_top_performers: Get top performing videos by metric
- generate_weekly_report: Generate weekly performance report
- predict_engagement: Predict engagement for title/category
- estimate_video_cost: Estimate production cost for a video
- calculate_text_cost: Calculate text generation cost
- calculate_image_cost: Calculate image generation cost
- calculate_audio_cost: Calculate audio generation cost
- get_cost_rates: Get current API cost rates

This MCP consolidates:
- production_analytics_tracker
- production_cost_tracker
- ROI calculation
- Performance monitoring
"""

import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from dataclasses import asdict

sys.path.append('/home/claude-workflow')

from mcp_servers.production_analytics_tracker import AnalyticsTracker
from mcp_servers.production_cost_tracker import CostTrackerMCP, API_COSTS

srv = Server("production-analytics")

@srv.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="track_video",
            description="Track performance metrics for a single video across all platforms",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string", "description": "Airtable record ID"}
                },
                "required": ["record_id"]
            }
        ),
        Tool(
            name="track_all_published",
            description="Track performance for all published videos",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_top_performers",
            description="Get top performing videos by specific metric",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "enum": ["total_reach", "total_engagement", "engagement_rate", "roi", "viral_score", "quality_score"],
                        "default": "total_reach",
                        "description": "Metric to sort by"
                    },
                    "limit": {"type": "number", "default": 10, "description": "Number of videos to return"}
                }
            }
        ),
        Tool(
            name="generate_weekly_report",
            description="Generate comprehensive weekly performance report",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="predict_engagement",
            description="Predict engagement metrics for a title and category before publishing",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Video title to analyze"},
                    "category": {"type": "string", "description": "Product category"}
                },
                "required": ["title", "category"]
            }
        ),
        Tool(
            name="estimate_video_cost",
            description="Estimate production cost for a video (text, images, audio, rendering)",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string", "description": "Airtable record ID"}
                },
                "required": ["record_id"]
            }
        ),
        Tool(
            name="calculate_text_cost",
            description="Calculate text generation cost for given token count",
            inputSchema={
                "type": "object",
                "properties": {
                    "tokens": {"type": "number", "description": "Total tokens (input + output)"},
                    "model": {"type": "string", "enum": ["gpt-4o", "gpt-4o-mini"], "default": "gpt-4o-mini"}
                },
                "required": ["tokens"]
            }
        ),
        Tool(
            name="calculate_image_cost",
            description="Calculate image generation cost",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {"type": "number", "description": "Number of images"},
                    "service": {"type": "string", "enum": ["openai", "google", "fal", "huggingface"], "default": "fal"},
                    "model": {"type": "string", "default": "flux-schnell"}
                },
                "required": ["count"]
            }
        ),
        Tool(
            name="calculate_audio_cost",
            description="Calculate audio generation cost for ElevenLabs or other services",
            inputSchema={
                "type": "object",
                "properties": {
                    "chars": {"type": "number", "description": "Character count"},
                    "service": {"type": "string", "enum": ["elevenlabs", "openai", "google"], "default": "elevenlabs"},
                    "model": {"type": "string", "default": "turbo"}
                },
                "required": ["chars"]
            }
        ),
        Tool(
            name="get_cost_rates",
            description="Get current API cost rates for all services",
            inputSchema={
                "type": "object",
                "properties": {}
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

    # Initialize analytics and cost trackers
    analytics_tracker = AnalyticsTracker(config)
    cost_tracker = CostTrackerMCP()

    if name == "track_video":
        record_id = arguments.get("record_id")
        try:
            analytics = await analytics_tracker.track_video(record_id)
            result = asdict(analytics)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "track_all_published":
        try:
            all_analytics = await analytics_tracker.track_all_published()
            result = [asdict(a) for a in all_analytics]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "get_top_performers":
        metric = arguments.get("metric", "total_reach")
        limit = arguments.get("limit", 10)

        try:
            top_performers = await analytics_tracker.get_top_performers(metric, limit)
            result = [asdict(a) for a in top_performers]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "generate_weekly_report":
        try:
            report = await analytics_tracker.generate_weekly_report()
            return [TextContent(type="text", text=json.dumps(report, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "predict_engagement":
        title = arguments.get("title")
        category = arguments.get("category")

        try:
            prediction = await analytics_tracker.predict_engagement(title, category)
            return [TextContent(type="text", text=json.dumps(prediction, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "estimate_video_cost":
        record_id = arguments.get("record_id")

        try:
            cost_estimate = await cost_tracker.estimate_video_cost(record_id)
            result = asdict(cost_estimate)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "calculate_text_cost":
        tokens = arguments.get("tokens")
        model = arguments.get("model", "gpt-4o-mini")

        try:
            cost = cost_tracker.calculate_text_generation_cost(tokens, model)
            result = {
                "tokens": tokens,
                "model": model,
                "cost_usd": cost
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "calculate_image_cost":
        count = arguments.get("count")
        service = arguments.get("service", "fal")
        model = arguments.get("model", "flux-schnell")

        try:
            cost = cost_tracker.calculate_image_generation_cost(count, service, model)
            result = {
                "image_count": count,
                "service": service,
                "model": model,
                "cost_usd": cost
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "calculate_audio_cost":
        chars = arguments.get("chars")
        service = arguments.get("service", "elevenlabs")
        model = arguments.get("model", "turbo")

        try:
            cost = cost_tracker.calculate_audio_generation_cost(chars, service, model)
            result = {
                "character_count": chars,
                "service": service,
                "model": model,
                "cost_usd": cost
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "get_cost_rates":
        return [TextContent(type="text", text=json.dumps(API_COSTS, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

async def main():
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())
