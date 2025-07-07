#!/usr/bin/env python3
"""
Minimal test workflow - Tests with only Product #5 to save API costs
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, '/app/src')

async def test_minimal_workflow():
    """Test with Product #5 only to save tokens/API costs."""
    print("🧪 Testing Minimal Workflow (Product #5 Only)...")
    print("💰 Cost-saving mode: Skipping intro/outro and products 1-4")
    print("=" * 60)

    test_record_id = "recTest5Only"
    test_video_title = "🔥5 INSANE Car Amps You Need in 2025! (Bass Test) 🚗"

    # Only product #5 for testing
    test_products = [{
        "number": 5,
        "name": "Rockford Fosgate T3000X",
        "description": "At number 5, the T3000X delivers 3000 watts!"
    }]

    print(f"🎯 Testing with Product #{test_products[0]['number']} only")

    # Test image generation with one product
    print("\n🖼️ Testing Image Generation (Product #5 only)...")
    try:
        from image_generation_server import handle_call_tool as image_tool
        image_args = {
            "record_id": test_record_id,
            "video_title": test_video_title,
            "products": test_products
        }
        await image_tool("generate_and_save_product_images", image_args)
        print("✅ Product #5 image generated!")
    except Exception as e:
        print(f"❌ Image generation failed: {e}")

    print("\n✅ Minimal test completed - Product #5 only")
    print("💡 Enable full generation after testing is complete")

if __name__ == "__main__":
    asyncio.run(test_minimal_workflow())
