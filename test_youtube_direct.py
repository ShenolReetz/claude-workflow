#!/usr/bin/env python3
import asyncio
import sys
import os

# Add paths explicitly
sys.path.insert(0, '/home/claude-workflow/src')
sys.path.insert(0, '/home/claude-workflow')

print("Python paths:")
for p in sys.path[:5]:
    print(f"  {p}")

print("\nImporting YouTube MCP...")

try:
    from mcp.youtube_mcp import YouTubeMCP
    print("✅ Import successful!")
    
    async def test():
        youtube = YouTubeMCP(
            credentials_path='/home/claude-workflow/config/youtube_credentials.json',
            token_path='/home/claude-workflow/config/youtube_token.json'
        )
        
        result = await youtube.upload_video(
            video_path="https://assets.json2video.com/clients/Apiha4SJJk/renders/2025-07-01-16928.mp4",
            title="Test Upload - Claude Workflow",
            description="Testing YouTube integration",
            privacy_status='private'
        )
        
        if result['success']:
            print(f"\n✅ SUCCESS!")
            print(f"📺 Video URL: {result['video_url']}")
        else:
            print(f"\n❌ Failed: {result['error']}")
    
    # Run the test
    asyncio.run(test())
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nChecking file directly...")
    if os.path.exists('/home/claude-workflow/src/mcp/youtube_mcp.py'):
        print("✅ File exists")
        # Try to read it
        with open('/home/claude-workflow/src/mcp/youtube_mcp.py', 'r') as f:
            first_line = f.readline()
            print(f"First line: {first_line[:50]}...")
    else:
        print("❌ File not found")
