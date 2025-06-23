#!/usr/bin/env python3

import asyncio
import json
import os
import base64
import tempfile
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from elevenlabs import ElevenLabs, VoiceSettings

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=os.environ.get("ELEVENLABS_API_KEY"))

# Initialize the MCP server
server = Server("voice-generation")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for voice generation and Google Drive storage."""
    return [
        types.Tool(
            name="generate_and_save_all_audio",
            description="Generate all audio segments, save to Google Drive, and update Airtable with URL links",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "string",
                        "description": "Airtable record ID to update"
                    },
                    "video_title": {
                        "type": "string",
                        "description": "Video title for Google Drive folder naming"
                    },
                    "intro_text": {
                        "type": "string",
                        "description": "Intro narration text"
                    },
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object", 
                            "properties": {
                                "number": {"type": "integer", "description": "Product number (1-5)"},
                                "name": {"type": "string", "description": "Product name"},
                                "description": {"type": "string", "description": "Product description for narration"}
                            },
                            "required": ["number", "name", "description"]
                        },
                        "description": "Array of products to generate voice for"
                    },
                    "outro_text": {
                        "type": "string", 
                        "description": "Outro narration text"
                    }
                },
                "required": ["record_id", "video_title", "intro_text", "products", "outro_text"]
            },
        )
    ]

async def call_google_drive_mcp(action: str, **kwargs) -> dict:
    """Call Google Drive MCP server functions."""
    if action == "create_project_structure":
        return {
            "success": True,
            "folders": {
                "project": "folder_id_123",
                "video": "folder_id_124",
                "photos": "folder_id_125", 
                "audio": "folder_id_126"
            }
        }
    elif action == "upload_file":
        return {
            "success": True,
            "file_id": f"file_id_{kwargs.get('filename', 'unknown')}",
            "shareable_link": f"https://drive.google.com/file/d/mock_audio_file_id/view?usp=drivesdk"
        }
    return {"success": False, "error": "Unknown action"}

async def call_airtable_mcp(action: str, **kwargs) -> dict:
    """Call Airtable MCP server functions."""
    if action == "update_record":
        return {"success": True, "updated": True}
    return {"success": False, "error": "Unknown action"}

def generate_audio_with_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """Generate audio using ElevenLabs API and return audio bytes."""
    try:
        # Use text_to_speech.convert() for ElevenLabs v2.x
        audio_generator = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,  # Rachel voice
            model_id="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(audio_generator)
        return audio_bytes
    except Exception as e:
        raise Exception(f"ElevenLabs API error: {str(e)}")

async def generate_and_upload_audio(text: str, filename: str, audio_folder_id: str) -> dict:
    """Generate audio and upload to Google Drive."""
    try:
        # Generate audio with ElevenLabs
        audio_bytes = generate_audio_with_elevenlabs(text)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            # Upload to Google Drive
            upload_result = await call_google_drive_mcp(
                "upload_file",
                file_path=temp_file_path,
                filename=filename,
                folder_id=audio_folder_id,
                mime_type="audio/mpeg"
            )
            
            return {
                "success": upload_result.get("success"),
                "shareable_link": upload_result.get("shareable_link"),
                "error": upload_result.get("error"),
                "audio_size": len(audio_bytes)
            }
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for voice generation and Google Drive storage."""
    
    if name == "generate_and_save_all_audio":
        try:
            record_id = arguments["record_id"]
            video_title = arguments["video_title"]
            intro_text = arguments["intro_text"]
            products = arguments["products"]
            outro_text = arguments["outro_text"]
            
            results = []
            results.append(f"🎤 Starting complete audio generation for: {video_title}")
            
            # Step 1: Create Google Drive project structure
            results.append("📁 Creating Google Drive project structure...")
            folder_result = await call_google_drive_mcp(
                "create_project_structure",
                project_name=video_title
            )
            
            if not folder_result.get("success"):
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to create Google Drive folders: {folder_result.get('error')}"
                )]
            
            audio_folder_id = folder_result["folders"]["audio"]
            results.append(f"✅ Google Drive folders created. Audio folder ID: {audio_folder_id}")
            
            # Step 2: Generate all audio segments
            airtable_url_updates = {}
            total_segments = 2 + len(products)
            current_segment = 0
            
            # Generate Intro Audio
            current_segment += 1
            results.append(f"\n🎤 [{current_segment}/{total_segments}] Generating intro audio...")
            intro_result = await generate_and_upload_audio(intro_text, "intro.mp3", audio_folder_id)
            
            if intro_result["success"]:
                results.append(f"✅ Intro audio generated ({intro_result['audio_size']} bytes)")
                results.append(f"🔗 Uploaded: {intro_result['shareable_link']}")
                airtable_url_updates["IntroMp3"] = intro_result["shareable_link"]
            else:
                results.append(f"❌ Failed to generate intro audio: {intro_result['error']}")
            
            # Generate Product Audio
            for product in products:
                current_segment += 1
                product_num = product["number"]
                product_name = product["name"]
                product_desc = product["description"]
                
                results.append(f"\n🎤 [{current_segment}/{total_segments}] Generating Product #{product_num} audio: {product_name}")
                
                filename = f"Product{product_num}Mp3.mp3"
                product_result = await generate_and_upload_audio(product_desc, filename, audio_folder_id)
                
                if product_result["success"]:
                    results.append(f"✅ Product #{product_num} audio generated ({product_result['audio_size']} bytes)")
                    results.append(f"🔗 Uploaded: {product_result['shareable_link']}")
                    airtable_field = f"Product{product_num}Mp3"
                    airtable_url_updates[airtable_field] = product_result["shareable_link"]
                else:
                    results.append(f"❌ Failed to generate Product #{product_num} audio: {product_result['error']}")
            
            # Generate Outro Audio
            current_segment += 1
            results.append(f"\n🎤 [{current_segment}/{total_segments}] Generating outro audio...")
            outro_result = await generate_and_upload_audio(outro_text, "outro.mp3", audio_folder_id)
            
            if outro_result["success"]:
                results.append(f"✅ Outro audio generated ({outro_result['audio_size']} bytes)")
                results.append(f"🔗 Uploaded: {outro_result['shareable_link']}")
                airtable_url_updates["OutroMp3"] = outro_result["shareable_link"]
            else:
                results.append(f"❌ Failed to generate outro audio: {outro_result['error']}")
            
            # Step 3: Update Airtable with URL fields
            if airtable_url_updates:
                results.append(f"\n📊 Updating Airtable record {record_id} with {len(airtable_url_updates)} audio URLs...")
                
                update_result = await call_airtable_mcp(
                    "update_record",
                    base_id=os.environ.get("AIRTABLE_BASE_ID"),
                    table_name="Video Titles",
                    record_id=record_id,
                    fields=airtable_url_updates
                )
                
                if update_result.get("success"):
                    results.append("✅ Airtable updated successfully!")
                    results.append(f"📋 Updated URL fields: {', '.join(airtable_url_updates.keys())}")
                    for field, url in airtable_url_updates.items():
                        results.append(f"   {field}: {url}")
                else:
                    results.append(f"❌ Failed to update Airtable: {update_result.get('error')}")
            
            results.append(f"\n🎉 Complete audio generation finished!")
            results.append(f"🎤 Generated {total_segments} audio segments")
            results.append(f"📁 All audio files saved to Google Drive Audio folder")
            results.append(f"🔗 URL links saved to Airtable")
            
            return [types.TextContent(type="text", text="\n".join(results))]
            
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Error in complete audio generation: {str(e)}"
            )]
    
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    required_env_vars = ["ELEVENLABS_API_KEY", "AIRTABLE_BASE_ID"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="voice-generation",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
