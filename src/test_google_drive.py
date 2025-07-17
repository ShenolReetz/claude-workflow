import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.google_drive_server import GoogleDriveMCPServer

async def test_drive_connection():
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize Google Drive server
    drive_server = GoogleDriveMCPServer(config)
    
    # Test 1: Initialize service
    print("🔑 Testing Google Drive API connection...")
    success = await drive_server.initialize_drive_service()
    if not success:
        print("❌ Failed to connect to Google Drive")
        return
    
    # Test 2: Create project structure
    print("📁 Testing folder creation...")
    test_title = "Test Project - Claude MCP"
    folder_ids = await drive_server.create_project_structure(test_title)
    
    if folder_ids:
        print("✅ Successfully created folder structure!")
        print(f"📊 Created folders: {list(folder_ids.keys())}")
        
        # Test 3: Test a small file upload
        print("📄 Testing small file upload...")
        test_content = "This is a test file from Claude MCP workflow"
        test_base64 = "VGhpcyBpcyBhIHRlc3QgZmlsZSBmcm9tIENsYXVkZSBNQ1Agd29ya2Zsb3c="  # base64 of test content
        
        if 'audio' in folder_ids:
            link = await drive_server.upload_audio_file(
                test_base64, 
                "test_audio.txt", 
                folder_ids['audio']
            )
            if link:
                print(f"✅ File uploaded successfully!")
                print(f"🔗 Link: {link}")
            else:
                print("❌ File upload failed")
    else:
        print("❌ Failed to create folder structure")

if __name__ == "__main__":
    asyncio.run(test_drive_connection())
