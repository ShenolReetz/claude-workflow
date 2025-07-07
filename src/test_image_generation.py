#!/usr/bin/env python3

import asyncio
import json
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, '/app/src')

async def test_image_generation():
    """Test the image generation MCP server."""
    print("🖼️ Testing Image Generation MCP Server...")
    
    # Test data
    test_record_id = "rec123test"
    test_video_title = "🔥5 INSANE Car Amps You Need in 2025! (Bass Test) 🚗"
    test_products = [
        {
            "number": 1,
            "name": "Rockford Fosgate T3000X",
            "description": "High-power car amplifier with advanced cooling system, 3000 watts of clean power delivery"
        },
        {
            "number": 2, 
            "name": "JL Audio XD800/8v2",
            "description": "8-channel digital amplifier with built-in DSP processing for premium sound quality"
        }
    ]
    
    print(f"📋 Test Record ID: {test_record_id}")
    print(f"📺 Test Video Title: {test_video_title}")
    print(f"📦 Test Products: {len(test_products)} items")
    
    # Import the image generation server
    try:
        from image_generation_server import handle_call_tool
        print("✅ Image generation server imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import image generation server: {e}")
        return
    
    # Test the generate_and_save_product_images function
    try:
        print("\n🎨 Testing image generation and Google Drive upload...")
        
        arguments = {
            "record_id": test_record_id,
            "video_title": test_video_title,
            "products": test_products
        }
        
        result = await handle_call_tool("generate_and_save_product_images", arguments)
        
        print("✅ Image generation test completed!")
        print("📊 Result:")
        for content in result:
            print(content.text)
            
    except Exception as e:
        print(f"❌ Error during image generation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "AIRTABLE_BASE_ID"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("🔑 Environment variables found:")
    for var in required_vars:
        value = os.environ.get(var, "")
        print(f"   {var}: {value[:10]}..." if value else f"   {var}: NOT SET")
    
    asyncio.run(test_image_generation())
