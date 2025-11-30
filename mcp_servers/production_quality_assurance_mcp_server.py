#!/usr/bin/env python3
"""
Production Quality Assurance MCP Server
========================================
Real MCP server for content quality validation before publishing.

Tools:
- validate_all: Run complete quality validation (scripts, images, audio, video, compliance)
- validate_scripts: Validate voice scripts only
- validate_images: Validate product images only
- validate_audio: Validate voice files only
- validate_video: Validate rendered video only
- validate_compliance: Validate FTC compliance only
- get_quality_score: Get quick quality score without full validation

This MCP consolidates:
- production-product-validator
- production-credential-validation
- quality assurance checks
- compliance validation
"""

import os, sys, json, asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from dataclasses import asdict

sys.path.append('/home/claude-workflow')

from mcp_servers.production_quality_assurance import QualityAssuranceManager

srv = Server("production-quality-assurance")

@srv.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="validate_all",
            description="Run complete quality validation on all content (scripts, images, audio, video, compliance)",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string", "description": "Airtable record ID to validate"}
                },
                "required": ["record_id"]
            }
        ),
        Tool(
            name="validate_scripts",
            description="Validate voice scripts for quality, readability, grammar, profanity",
            inputSchema={
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "description": "Record with fields containing scripts (IntroVoiceScript, Product1VoiceScript, etc.)"
                    }
                },
                "required": ["record"]
            }
        ),
        Tool(
            name="validate_images",
            description="Validate product images exist and have proper quality",
            inputSchema={
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "description": "Record with fields containing image URLs"
                    }
                },
                "required": ["record"]
            }
        ),
        Tool(
            name="validate_audio",
            description="Validate voice files exist and match scripts",
            inputSchema={
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "description": "Record with fields containing audio URLs"
                    }
                },
                "required": ["record"]
            }
        ),
        Tool(
            name="validate_video",
            description="Validate rendered video exists and has proper format (MP4, 1080x1920)",
            inputSchema={
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "description": "Record with VideoURL field"
                    }
                },
                "required": ["record"]
            }
        ),
        Tool(
            name="validate_compliance",
            description="Validate FTC affiliate disclosure and compliance requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "record": {
                        "type": "object",
                        "description": "Record with affiliate links and content"
                    }
                },
                "required": ["record"]
            }
        ),
        Tool(
            name="get_quality_thresholds",
            description="Get quality validation thresholds and requirements",
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

    qa_manager = QualityAssuranceManager(config)

    if name == "validate_all":
        record_id = arguments.get("record_id")

        try:
            report = await qa_manager.validate_all(record_id)
            if report:
                # Save report to file
                await qa_manager.save_report(report)

                # Return report as JSON
                result = asdict(report)
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            else:
                return [TextContent(type="text", text=json.dumps({"error": "Record not found"}))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "validate_scripts":
        record = arguments.get("record")

        try:
            result = await qa_manager.validate_scripts(record)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "validate_images":
        record = arguments.get("record")

        try:
            result = await qa_manager.validate_images(record)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "validate_audio":
        record = arguments.get("record")

        try:
            result = await qa_manager.validate_audio(record)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "validate_video":
        record = arguments.get("record")

        try:
            result = await qa_manager.validate_video(record)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "validate_compliance":
        record = arguments.get("record")

        try:
            result = await qa_manager.validate_compliance(record)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    elif name == "get_quality_thresholds":
        thresholds = {
            "min_passing_score": qa_manager.MIN_PASSING_SCORE,
            "min_script_length": qa_manager.MIN_SCRIPT_LENGTH,
            "max_script_length": qa_manager.MAX_SCRIPT_LENGTH,
            "min_readability_score": qa_manager.MIN_READABILITY_SCORE,
            "max_profanity_occurrences": qa_manager.MAX_PROFANITY_OCCURRENCES,
            "required_disclosures": qa_manager.REQUIRED_DISCLOSURES,
            "component_weights": {
                "script": 0.30,
                "image": 0.20,
                "audio": 0.15,
                "video": 0.20,
                "compliance": 0.15
            },
            "validation_checks": {
                "scripts": ["length", "readability", "grammar", "profanity"],
                "images": ["file_exists", "resolution", "file_size"],
                "audio": ["file_exists", "duration", "quality"],
                "video": ["file_exists", "format", "resolution", "duration"],
                "compliance": ["ftc_disclosure", "affiliate_links", "brand_safety"]
            }
        }
        return [TextContent(type="text", text=json.dumps(thresholds, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

async def main():
    init = srv.create_initialization_options()
    async with stdio_server() as (read, write):
        await srv.run(read, write, init)

if __name__ == "__main__":
    asyncio.run(main())
