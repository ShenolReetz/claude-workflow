#!/usr/bin/env python3
"""
Complete WordPress integration fix
"""

# Read the workflow runner
with open('src/workflow_runner.py', 'r') as f:
    content = f.read()

# 1. Add WordPress import if not present
if 'from mcp.wordpress_mcp import WordPressMCP' not in content:
    # Find imports section
    import_pos = content.find('from mcp.google_drive_agent_mcp import GoogleDriveAgent')
    if import_pos > 0:
        line_end = content.find('\n', import_pos)
        content = content[:line_end] + '\nfrom mcp.wordpress_mcp import WordPressMCP' + content[line_end:]
        print("✅ Added WordPress import")

# 2. Initialize WordPress MCP if not present
if 'self.wordpress_mcp' not in content:
    # Find where to add initialization (after google_drive_agent)
    init_pos = content.find('self.google_drive_agent = GoogleDriveAgent(')
    if init_pos > 0:
        # Find the end of the GoogleDriveAgent initialization
        paren_count = 1
        i = content.find('(', init_pos) + 1
        while paren_count > 0 and i < len(content):
            if content[i] == '(':
                paren_count += 1
            elif content[i] == ')':
                paren_count -= 1
            i += 1
        
        # Insert WordPress initialization after the closing parenthesis
        wordpress_init = '\n        \n        # Initialize WordPress MCP\n        self.wordpress_mcp = WordPressMCP(self.config)'
        content = content[:i] + wordpress_init + content[i:]
        print("✅ Added WordPress MCP initialization")

# 3. Add WordPress posting after Google Drive upload
# Use the correct variable name from the grep output
insertion_marker = "print(f\"✅ Video uploaded to Google Drive: {upload_result['drive_url']}\")"
insertion_pos = content.find(insertion_marker)

if insertion_pos > 0:
    # Find the end of this line
    line_end = content.find('\n', insertion_pos)
    
    # WordPress posting code
    wordpress_code = '''

            # Step 8: Create WordPress Blog Post
            print("\\n📝 Creating WordPress blog post...")
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
    
    # Insert the WordPress code
    content = content[:line_end] + wordpress_code + content[line_end:]
    print("✅ Added WordPress posting step after Google Drive upload")
else:
    print("❌ Could not find Google Drive upload success message")

# Write back the updated content
with open('src/workflow_runner.py', 'w') as f:
    f.write(content)

print("\n✅ WordPress integration complete!")
print("The workflow will now create blog posts after video upload.")
