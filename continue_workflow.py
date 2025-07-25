#!/usr/bin/env python3
"""
Continue Test workflow from platform content generation step
"""
import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from src.mcp.Test_platform_content_generator import generate_platform_content_for_workflow

async def continue_from_platform_content():
    """Continue workflow from platform content generation"""
    
    print("🔄 Continuing Test workflow from platform content generation...")
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Current record that was being processed
    record_id = "rec0WgzfdQTyzI0V4"  # Video Surveillance Equipment
    
    print(f"📋 Continuing record: {record_id}")
    print(f"🎬 Title: Top 5 New Video Surveillance Equipment Releases 2025")
    
    try:
        print("🎯 Generating platform-specific content...")
        result = await generate_platform_content_for_workflow(
            config=config,
            record_id=record_id,
            base_title="🔥 2025's Most INSANE Security Cameras You Need Right Now! 🎯",
            products=[
                {"name": "Arlo Pro 4 Spotlight Camera"},
                {"name": "2025 Upgraded 2K Security Camera"},
                {"name": "Security Cameras Wireless Outdoor"},
                {"name": "VIMTAG Security Camera Outdoor"},
                {"name": "Home Security Camera System"}
            ],
            category="video surveillance equipment"
        )
        
        print(f"✅ Platform content generation result:")
        print(f"📊 Success: {result.get('success', False)}")
        print(f"📝 Platforms processed: {result.get('platforms_processed', 0)}")
        
        if result.get('success'):
            print("🎬 Platform content complete! Workflow can now continue to video generation...")
            return True
        else:
            print(f"❌ Platform content generation failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error continuing workflow: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(continue_from_platform_content())
    if success:
        print("\n🚀 Ready to continue with video generation!")
    else:
        print("\n❌ Platform content step failed")