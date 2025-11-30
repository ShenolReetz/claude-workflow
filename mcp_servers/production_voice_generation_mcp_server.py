#!/usr/bin/env python3
"""
Production Voice Generation MCP Server
======================================
Real MCP server for ElevenLabs voice synthesis with local storage.

Tools:
- generate_voice: Generate single voice file from text
- generate_all_voices: Generate all voices for a record (intro, products, outro)
- get_voice_info: Get available voice IDs and settings

This MCP consolidates:
- production-voice-generation
- ElevenLabs API integration
- Local audio storage
"""

import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

sys.path.append('/home/claude-workflow')

from mcp_servers.production_voice_generation_server_local import ProductionVoiceGenerationLocal

srv = Server("production-voice-generation")

@srv.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="generate_voice",
            description="Generate a single voice file from text using ElevenLabs",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to convert to speech"},
                    "voice_type": {"type": "string", "enum": ["intro", "outro", "product"], "default": "product", "description": "Type of voice to use"},
                    "record_id": {"type": "string", "description": "Record ID for file organization"}
                },
                "required": ["text", "record_id"]
            }
        ),
        Tool(
            name="generate_all_voices",
            description="Generate all voices for a complete record (intro, product1-5, outro)",
            inputSchema={
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "description": "Record with fields: IntroScript, Product1Script-Product5Script, OutroScript",
                        "properties": {
                            "record_id": {"type": "string"},
                            "fields": {
                                "type": "object",
                                "properties": {
                                    "IntroScript": {"type": "string"},
                                    "Product1Script": {"type": "string"},
                                    "Product2Script": {"type": "string"},
                                    "Product3Script": {"type": "string"},
                                    "Product4Script": {"type": "string"},
                                    "Product5Script": {"type": "string"},
                                    "OutroScript": {"type": "string"}
                                }
                            }
                        },
                        "required": ["record_id", "fields"]
                    }
                },
                "required": ["record"]
            }
        ),
        Tool(
            name="get_voice_info",
            description="Get available voice IDs and current configuration",
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

    voice_gen = ProductionVoiceGenerationLocal(config)

    if name == "generate_voice":
        text = arguments.get("text")
        voice_type = arguments.get("voice_type", "product")
        record_id = arguments.get("record_id")

        try:
            result = await voice_gen._generate_single_voice(voice_type, text, record_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "generate_all_voices":
        record = arguments.get("record", {})

        try:
            result = await voice_gen.generate_all_voices_local(record)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "get_voice_info":
        voice_info = {
            "voice_ids": voice_gen.voice_ids,
            "base_url": voice_gen.base_url,
            "max_concurrent": voice_gen.max_concurrent,
            "supported_models": ["eleven_monolingual_v1"],
            "default_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            },
            "rate_limits": {
                "starter": 3,
                "creator": 5,
                "pro": 10
            },
            "voice_types": ["intro", "outro", "product"]
        }
        return [TextContent(type="text", text=json.dumps(voice_info, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

async def main():
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())
