#!/usr/bin/env python3
"""
Properly add WordPress posting to workflow
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# Find the right place to insert - after the Google Drive upload
# Look for the section after gdrive_url is printed
insertion_marker = 'print(f"✅ Video uploaded to Google Drive: {gdrive_url}")'
insertion_pos = content.find(insertion_marker)

if insertion_pos > 0:
    # Find the end of this line
    line_end = content.find('\n', insertion_pos)
    
    # WordPress posting code
    wordpress_code = '''

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
                print(f"❌ Blog post error: {e}")'''
    
    # Insert the WordPress code after the Google Drive success message
    content = content[:line_end] + wordpress_code + content[line_end:]
    
    # Write back
    with open('src/workflow_runner.py', 'w') as f:
        f.write(content)
    
    print("✅ Added WordPress posting code after Google Drive upload")
else:
    print("❌ Could not find insertion point")
    
# Also check if WordPress is initialized
if 'self.wordpress_mcp' not in content:
    print("⚠️ WordPress MCP not initialized. Need to add initialization too.")
