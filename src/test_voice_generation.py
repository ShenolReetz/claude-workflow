#!/usr/bin/env python3

import asyncio
import json
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, '/app/src')

async def test_voice_generation():
    """Test the voice generation MCP server."""
    print("🎤 Testing Voice Generation MCP Server...")
    
    # Test data
    test_record_id = "rec123test"
    test_video_title = "🔥5 INSANE Car Amps You Need in 2025! (Bass Test) 🚗"
    test_intro = "Welcome back to Tech Reviews! Today we're counting down the top 5 car amplifiers that will transform your audio experience in 2025!"
    test_outro = "That's our countdown of the best car amps for 2025! Which one caught your attention? Let us know in the comments below!"
    test_products = [
        {
            "number": 1,
            "name": "Rockford Fosgate T3000X",
            "description": "At number 5, the Rockford Fosgate T3000X delivers 3000 watts of pure power with advanced thermal management."
        },
        {
            "number": 2,
            "name": "JL Audio XD800/8v2", 
            "description": "Number 4 brings us the JL Audio XD800 with 8 channels and built-in DSP for crystal clear sound processing."
        }
    ]
    
    print(f"📋 Test Record ID: {test_record_id}")
    print(f"📺 Test Video Title: {test_video_title}")
    print(f"🎤 Test Audio Segments: {2 + len(test_products)} total")
    
    # Import the voice generation server
    try:
        from voice_generation_server import handle_call_tool
        print("✅ Voice generation server imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import voice generation server: {e}")
        return
    
    # Test the generate_and_save_all_audio function
    try:
        print("\n🎤 Testing complete audio generation and Google Drive upload...")
        
        arguments = {
            "record_id": test_record_id,
            "video_title": test_video_title,
            "intro_text": test_intro,
            "products": test_products,
            "outro_text": test_outro
        }
        
        result = await handle_call_tool("generate_and_save_all_audio", arguments)
        
        print("✅ Voice generation test completed!")
        print("📊 Result:")
        for content in result:
            print(content.text)
            
    except Exception as e:
        print(f"❌ Error during voice generation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check environment variables
    required_vars = ["ELEVENLABS_API_KEY", "AIRTABLE_BASE_ID"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("🔑 Environment variables found:")
    for var in required_vars:
        value = os.environ.get(var, "")
        print(f"   {var}: {value[:10]}..." if value else f"   {var}: NOT SET")
    
    asyncio.run(test_voice_generation())
