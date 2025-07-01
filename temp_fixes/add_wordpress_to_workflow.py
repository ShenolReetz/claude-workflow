#!/usr/bin/env python3
"""
Add WordPress posting to the workflow
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Add WordPress import
if 'from mcp.wordpress_mcp import WordPressMCP' not in content:
    # Find the imports section and add WordPress import
    import_section = content.find('from mcp.amazon_affiliate_agent_mcp')
    if import_section > 0:
        end_of_line = content.find('\n', import_section)
        content = content[:end_of_line] + '\nfrom mcp.wordpress_mcp import WordPressMCP' + content[end_of_line:]

# Initialize WordPress MCP in __init__
init_wordpress = '''
        # Initialize WordPress MCP
        self.wordpress_mcp = WordPressMCP(self.config)'''

if 'self.wordpress_mcp' not in content:
    # Add after Google Drive agent initialization
    gdrive_init = content.find('self.google_drive_agent = GoogleDriveAgent(')
    if gdrive_init > 0:
        # Find the end of this initialization
        next_line = content.find('\n', content.find(')', gdrive_init))
        content = content[:next_line] + init_wordpress + content[next_line:]

# Add WordPress posting after Google Drive upload
wordpress_post_code = '''
            # Step 8: Create WordPress Blog Post
            print("📝 Creating WordPress blog post...")
            try:
                # Get all the data from Airtable for the blog post
                record_data = await self.airtable_server.get_record(pending_title['record_id'])
                
                # Create the blog post
                wp_result = await self.wordpress_mcp.create_review_post(record_data)
                
                if wp_result.get('enabled', True):
                    if wp_result.get('success'):
                        print(f"✅ Blog post created!")
                        print(f"   📰 URL: {wp_result.get('link', 'N/A')}")
                        
                        # Update Airtable with blog URL
                        await self.airtable_server.update_record(
                            pending_title['record_id'],
                            {'BlogURL': wp_result.get('link', '')}
                        )
                    else:
                        print(f"❌ Blog post creation failed: {wp_result.get('error', 'Unknown error')}")
                else:
                    print("ℹ️ WordPress posting is disabled in config")
                    
            except Exception as e:
                logger.error(f"Error creating blog post: {e}")
                print(f"❌ Blog post error: {e}")
'''

# Find where to insert - after Google Drive upload success
gdrive_success = content.find('print(f"✅ Video uploaded to Google Drive: {gdrive_url}")')
if gdrive_success > 0:
    # Find the next suitable insertion point
    next_section = content.find('\n\n', gdrive_success)
    if next_section > 0:
        content = content[:next_section] + '\n' + wordpress_post_code + content[next_section:]

# Write the updated content
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("✅ Added WordPress MCP to workflow")
print("✅ Blog post will be created after video upload")
print("✅ Blog URL will be saved to Airtable")
