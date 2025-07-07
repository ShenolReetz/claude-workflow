#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('/home/claude-workflow/src')
sys.path.append('/home/claude-workflow')

from mcp.youtube_mcp import YouTubeMCP

async def test_youtube():
    """Test YouTube upload with a sample video"""
    
    print("🧪 Testing YouTube Upload")
    print("========================")
    
    # Test video URL (your recent 8-second test video)
    test_video = "https://assets.json2video.com/clients/Apiha4SJJk/renders/2025-07-01-16928.mp4"
    
    youtube = YouTubeMCP(
        credentials_path='/home/claude-workflow/config/youtube_credentials.json',
        token_path='/home/claude-workflow/config/youtube_token.json'
    )
    
    result = await youtube.upload_video(
        video_path=test_video,
        title="Test Upload - Claude Workflow",
        description="Testing YouTube integration for automated video uploads.\n\n#test #automation",
        tags=['test', 'automation'],
        privacy_status='private'
    )
    
    if result['success']:
        print(f"\n✅ Success! Video uploaded:")
        print(f"   URL: {result['video_url']}")
        print(f"   ID: {result['video_id']}")
    else:
        print(f"\n❌ Failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_youtube())
