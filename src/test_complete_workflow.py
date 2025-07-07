#!/usr/bin/env python3

import asyncio
import json
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, '/app/src')

async def test_complete_workflow():
    """Test the complete media generation workflow."""
    print("🚀 Testing Complete Media Generation Workflow...")
    print("=" * 60)
    
    # Test data from your successful content generation
    test_record_id = "rec123workflow"
    test_video_title = "🔥5 INSANE Car Amps You Need in 2025! (Bass Test) 🚗"
    
    # Sample content (you can replace with real generated content)
    test_intro = "Welcome back tech lovers! Today we're diving into the 5 most insane car amplifiers that will blow your mind in 2025!"
    test_outro = "That's our top 5 car amps for 2025! Which one impressed you the most? Drop your thoughts below and don't forget to subscribe!"
    
    test_products = [
        {
            "number": 1,
            "name": "Rockford Fosgate T3000X",
            "description": "At number 5, the T3000X monster delivers 3000 watts of earth-shaking bass power!"
        },
        {
            "number": 2,
            "name": "JL Audio XD800/8v2",
            "description": "Number 4 features the XD800 with 8 channels of pure audio perfection!"
        },
        {
            "number": 3,
            "name": "Alpine PDX-M12",
            "description": "Coming in at number 3, the PDX-M12 brings premium German engineering!"
        }
    ]
    
    print(f"📺 Video: {test_video_title}")
    print(f"🎤 Audio Segments: {2 + len(test_products)} total")
    print(f"🖼️ Images: {len(test_products)} product photos")
    print("=" * 60)
    
    # Test 1: Image Generation
    print("\n🖼️ STEP 1: Testing Image Generation...")
    try:
        from image_generation_server import handle_call_tool as image_tool
        
        image_args = {
            "record_id": test_record_id,
            "video_title": test_video_title,
            "products": test_products
        }
        
        image_result = await image_tool("generate_and_save_product_images", image_args)
        print("✅ Image generation completed!")
        
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
    
    # Test 2: Voice Generation  
    print("\n🎤 STEP 2: Testing Voice Generation...")
    try:
        from voice_generation_server import handle_call_tool as voice_tool
        
        voice_args = {
            "record_id": test_record_id,
            "video_title": test_video_title,
            "intro_text": test_intro,
            "products": test_products,
            "outro_text": test_outro
        }
        
        voice_result = await voice_tool("generate_and_save_all_audio", voice_args)
        print("✅ Voice generation completed!")
        
    except Exception as e:
        print(f"❌ Voice generation failed: {e}")
    
    print("\n🎉 Complete workflow test finished!")
    print("📁 Check Google Drive for organized files")
    print("📊 Check Airtable for updated URL links")

if __name__ == "__main__":
    # Check all environment variables
    required_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY", "AIRTABLE_BASE_ID"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    print("🔑 All environment variables found!")
    asyncio.run(test_complete_workflow())
