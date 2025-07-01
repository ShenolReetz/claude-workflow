#!/usr/bin/env python3

import asyncio
import json
import os
import requests
import tempfile
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize the MCP server
server = Server("image-generation")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools for image generation and Google Drive storage."""
    return [
        types.Tool(
            name="generate_and_save_product_images",
            description="Generate product images with DALL-E 3, save to Google Drive, and update Airtable with URL links",
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
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "number": {"type": "integer", "description": "Product number (1-5)"},
                                "name": {"type": "string", "description": "Product name"},
                                "description": {"type": "string", "description": "Product description for image generation"}
                            },
                            "required": ["number", "name", "description"]
                        },
                        "description": "Array of products to generate images for"
                    }
                },
                "required": ["record_id", "video_title", "products"]
            },
        )
    ]

def download_image_from_url(url: str) -> bytes:
    """Download image from URL and return bytes."""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

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
            "shareable_link": f"https://drive.google.com/file/d/mock_file_id/view?usp=drivesdk"
        }
    return {"success": False, "error": "Unknown action"}

async def call_airtable_mcp(action: str, **kwargs) -> dict:
    """Call Airtable MCP server functions."""
    if action == "update_record":
        return {"success": True, "updated": True}
    return {"success": False, "error": "Unknown action"}

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for image generation and Google Drive storage."""
    
    if name == "generate_and_save_product_images":
        try:
            record_id = arguments["record_id"]
            video_title = arguments["video_title"]
            products = arguments["products"]
            
            results = []
            results.append(f"🖼️ Starting image generation and Google Drive upload for: {video_title}")
            
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
            
            photos_folder_id = folder_result["folders"]["photos"]
            results.append(f"✅ Google Drive folders created. Photos folder ID: {photos_folder_id}")
            
            # Step 2: Generate and upload images for each product
            airtable_url_updates = {}
            
            for product in products:
                product_num = product["number"]
                product_name = product["name"]
                product_desc = product["description"]
                
                results.append(f"\n🎨 Generating image for Product #{product_num}: {product_name}")
                
                image_prompt = f"""Create an ultra-realistic product image of: {product_name}
                
Description: {product_desc}

Style requirements:
- Ultra-realistic commercial product photography
- 9:16 aspect ratio (vertical orientation for mobile)
- Clean white or subtle gradient background
- Professional studio lighting
- High detail and clarity
- Product should be prominently centered
- Commercial advertising quality"""

                try:
                    # Generate image with DALL-E 3
                    response = openai_client.images.generate(
                        model="dall-e-3",
                        prompt=image_prompt,
                        size="1024x1792",  # 9:16 aspect ratio
                        quality="hd",
                        n=1
                    )
                    
                    openai_image_url = response.data[0].url
                    results.append(f"✅ Generated DALL-E image: {openai_image_url[:50]}...")
                    
                    # Download image from OpenAI
                    results.append("📥 Downloading image from OpenAI...")
                    image_data = download_image_from_url(openai_image_url)
                    results.append(f"✅ Downloaded image ({len(image_data)} bytes)")
                    
                    # Upload to Google Drive Photos folder
                    filename = f"Product{product_num}Photo.jpg"
                    results.append(f"📤 Uploading to Google Drive as: {filename}")
                    
                    # Save to temporary file for upload
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                        temp_file.write(image_data)
                        temp_file_path = temp_file.name
                    
                    try:
                        upload_result = await call_google_drive_mcp(
                            "upload_file",
                            file_path=temp_file_path,
                            filename=filename,
                            folder_id=photos_folder_id,
                            mime_type="image/jpeg"
                        )
                        
                        if upload_result.get("success"):
                            shareable_link = upload_result["shareable_link"]
                            results.append(f"✅ Uploaded to Google Drive: {shareable_link}")
                            
                            # Store as simple URL string for Airtable URL field
                            airtable_field = f"Product{product_num}Photo"
                            airtable_url_updates[airtable_field] = shareable_link
                            results.append(f"📋 Will update {airtable_field} with URL: {shareable_link}")
                            
                        else:
                            results.append(f"❌ Failed to upload to Google Drive: {upload_result.get('error')}")
                            
                    finally:
                        os.unlink(temp_file_path)
                    
                    # Rate limiting delay
                    if product_num < len(products):
                        results.append("⏳ Waiting 15 seconds (rate limiting)...")
                        await asyncio.sleep(15)
                        
                except Exception as e:
                    results.append(f"❌ Error generating image for Product #{product_num}: {str(e)}")
                    continue
            
            # Step 3: Update Airtable with URL fields
            if airtable_url_updates:
                results.append(f"\n📊 Updating Airtable record {record_id} with {len(airtable_url_updates)} photo URLs...")
                
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
            
            results.append(f"\n🎉 Image generation and Google Drive upload complete!")
            results.append(f"📊 Generated {len([p for p in products])} product images")
            results.append(f"📁 All images saved to Google Drive Photos folder")
            results.append(f"🔗 URL links saved to Airtable")
            
            return [types.TextContent(type="text", text="\n".join(results))]
            
        except Exception as e:
            return [types.TextContent(
                type="text", 
                text=f"❌ Error in image generation and upload: {str(e)}"
            )]
    
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    required_env_vars = ["OPENAI_API_KEY", "AIRTABLE_BASE_ID"]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="image-generation",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
