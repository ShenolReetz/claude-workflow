#!/usr/bin/env python3
import asyncio
import sys
import os
import logging

sys.path.append('/home/claude-workflow/src')
sys.path.append('/home/claude-workflow')

logging.basicConfig(level=logging.INFO)

async def test_youtube_upload():
    """Test YouTube upload with a sample video"""
    
    print("🧪 Testing YouTube Upload")
    print("========================")
    
    from mcp.youtube_mcp import YouTubeMCP
    
    test_video = "https://assets.json2video.com/clients/Apiha4SJJk/renders/2025-07-01-16928.mp4"
    
    print(f"\n📹 Test video: {test_video}")
    print("🔐 Using saved authentication token")
    
    try:
        youtube = YouTubeMCP(
            credentials_path='/home/claude-workflow/config/youtube_credentials.json',
            token_path='/home/claude-workflow/config/youtube_token.json'
        )
        
        print("✅ YouTube MCP initialized")
        print("\n📤 Starting upload...")
        
        result = await youtube.upload_video(
            video_path=test_video,
            title="Test Upload - Claude Workflow Automation",
            description=(
                "This is a test upload from Claude Workflow automation system.\n\n"
                "Testing automated video uploads to YouTube.\n\n"
                "#test #automation #claudeworkflow"
            ),
            tags=['test', 'automation', 'claude', 'workflow'],
            privacy_status='private'
        )
        
        if result['success']:
            print(f"\n✅ SUCCESS! Video uploaded to YouTube!")
            print(f"📺 Video URL: {result['video_url']}")
            print(f"🔑 Video ID: {result['video_id']}")
            print(f"📝 Title: {result['title']}")
        else:
            print(f"\n❌ Upload failed: {result['error']}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_youtube_upload())
