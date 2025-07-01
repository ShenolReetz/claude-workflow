# Add a wrapper function for backward compatibility
wrapper_code = '''
# Wrapper function for backward compatibility
async def upload_video_to_google_drive(config, video_url, video_title, record_id=None):
    """Wrapper function to maintain compatibility with existing code"""
    gdrive_agent = GoogleDriveAgent()
    result = await gdrive_agent.upload_video_to_drive(
        video_url=video_url,
        video_title=video_title,
        parent_folder_name=config.get('gdrive_folder_name', 'N8N Projects')
    )
    return result
'''

# Add this to the google_drive_agent_mcp.py file
with open('src/mcp/google_drive_agent_mcp.py', 'r') as f:
    content = f.read()

# Add the wrapper at the end of the file
if 'upload_video_to_google_drive' not in content:
    content += '\n\n' + wrapper_code

    with open('src/mcp/google_drive_agent_mcp.py', 'w') as f:
        f.write(content)
    
    print("✅ Added wrapper function for compatibility")
else:
    print("✅ Wrapper function already exists")
