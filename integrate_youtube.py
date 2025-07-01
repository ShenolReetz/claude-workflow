#!/usr/bin/env python3
"""
Integrate YouTube into the main workflow with full features
"""

import os
import json

def update_workflow_for_youtube():
    """Update workflow_runner.py to include YouTube with all features"""
    
    # Read the current workflow
    workflow_file = '/home/claude-workflow/src/workflow_runner.py'
    with open(workflow_file, 'r') as f:
        lines = f.readlines()
    
    # Find where to add YouTube import (after wordpress import)
    import_added = False
    for i, line in enumerate(lines):
        if 'from mcp.wordpress_mcp import' in line and not import_added:
            lines.insert(i + 1, 'from mcp.youtube_mcp import YouTubeMCP\n')
            import_added = True
            break
    
    # Find where to add YouTube upload (after WordPress section)
    youtube_code = '''
        # Upload to YouTube (if enabled)
        youtube_enabled = config.get('youtube_enabled', False)
        if youtube_enabled and video_url:
            print("📹 Uploading to YouTube Shorts...")
            try:
                # Initialize YouTube MCP
                youtube_mcp = YouTubeMCP(
                    credentials_path=config.get('youtube_credentials', '/home/claude-workflow/config/youtube_credentials.json'),
                    token_path=config.get('youtube_token', '/home/claude-workflow/config/youtube_token.json')
                )
                
                # Prepare YouTube title (optimized for Shorts)
                youtube_prefix = config.get('youtube_title_prefix', '')
                youtube_suffix = config.get('youtube_title_suffix', '')
                youtube_title = f"{youtube_prefix}{video_title}{youtube_suffix}"[:100]  # YouTube limit
                
                # Build YouTube description
                youtube_description = f"{video_title}\\n\\n"
                
                # Add timestamps (for 8-second test videos)
                youtube_description += "⏱️ Timestamps:\\n"
                youtube_description += "0:00 Intro\\n"
                youtube_description += "0:02 Products\\n"
                youtube_description += "0:06 Outro\\n\\n"
                
                # Add products with affiliate links
                youtube_description += "🛒 Featured Products:\\n\\n"
                products_found = False
                
                for i in range(1, 6):
                    product_title = airtable_record.get(f'ProductNo{i}Title', '')
                    product_desc = airtable_record.get(f'ProductNo{i}Description', '')
                    affiliate_link = airtable_record.get(f'ProductNo{i}AffiliateLink', '')
                    
                    if product_title:
                        products_found = True
                        youtube_description += f"#{i} {product_title}\\n"
                        if product_desc:
                            # Add first 100 chars of description
                            youtube_description += f"{product_desc[:100]}...\\n"
                        if affiliate_link:
                            youtube_description += f"→ {affiliate_link}\\n"
                        youtube_description += "\\n"
                
                # Add keywords as hashtags
                if keywords:
                    youtube_description += "\\n"
                    # Add up to 10 hashtags
                    for keyword in keywords[:10]:
                        hashtag = keyword.replace(' ', '').replace('-', '')
                        youtube_description += f"#{hashtag} "
                    youtube_description += "\\n"
                
                # Add shorts hashtag
                shorts_tag = config.get('youtube_shorts_tag', '#shorts')
                youtube_description += f"\\n{shorts_tag}\\n"
                
                # Add disclaimer
                youtube_description += "\\n" + "="*50 + "\\n"
                youtube_description += "As an Amazon Associate I earn from qualifying purchases.\\n"
                youtube_description += "="*50
                
                # Prepare tags
                youtube_tags = config.get('youtube_tags', []).copy()
                youtube_tags.append('shorts')  # Always add shorts tag
                
                # Add keywords as tags
                if keywords:
                    youtube_tags.extend([k.lower() for k in keywords[:10]])
                
                # Remove duplicates and limit tags
                youtube_tags = list(dict.fromkeys(youtube_tags))[:30]  # YouTube allows max 30 tags
                
                # Upload video
                youtube_result = await youtube_mcp.upload_video(
                    video_path=video_url,
                    title=youtube_title,
                    description=youtube_description[:5000],  # YouTube limit
                    tags=youtube_tags,
                    category_id=config.get('youtube_category', '22'),  # People & Blogs
                    privacy_status=config.get('youtube_privacy', 'private')
                )
                
                if youtube_result.get('success'):
                    print(f"✅ YouTube upload successful!")
                    print(f"   URL: {youtube_result['video_url']}")
                    print(f"   Title: {youtube_result['title']}")
                    
                    # Update Airtable with YouTube info
                    youtube_updates = {
                        'YouTubeURL': youtube_result['video_url'],
                        'YouTubeVideoID': youtube_result['video_id'],
                        'YouTubeStatus': 'Uploaded'
                    }
                    
                    await airtable_server.update_record(record_id, youtube_updates)
                    print("✅ Updated Airtable with YouTube URL")
                    
                else:
                    print(f"⚠️ YouTube upload failed: {youtube_result.get('error')}")
                    # Don't fail the whole workflow
                    
            except Exception as e:
                print(f"❌ YouTube error: {e}")
                # Continue workflow even if YouTube fails
                import traceback
                traceback.print_exc()
        
'''
    
    # Find where to insert (look for WordPress completion or before final status update)
    insert_position = None
    for i, line in enumerate(lines):
        if '✅ Blog post created:' in line or 'print("✅ Updating record status' in line:
            # Find the end of this section
            j = i + 1
            while j < len(lines) and lines[j].startswith('    '):
                j += 1
            insert_position = j
            break
    
    if insert_position:
        # Insert YouTube code
        youtube_lines = youtube_code.split('\n')
        for youtube_line in reversed(youtube_lines):
            lines.insert(insert_position, youtube_line + '\n')
    
    # Save backup
    backup_file = workflow_file + '.backup_youtube'
    with open(workflow_file, 'r') as f:
        backup_content = f.read()
    with open(backup_file, 'w') as f:
        f.write(backup_content)
    print(f"✅ Created backup: {backup_file}")
    
    # Save updated workflow
    with open(workflow_file, 'w') as f:
        f.writelines(lines)
    
    print("✅ YouTube integration added to workflow!")
    print("\nFeatures added:")
    print("  • Custom title formatting (prefix/suffix)")
    print("  • Timestamps in description")
    print("  • Product list with affiliate links")
    print("  • Keyword hashtags")
    print("  • #shorts tag for YouTube Shorts")
    print("  • Amazon disclaimer")
    print("  • Error handling (won't break workflow)")
    print("  • Airtable updates with YouTube URL")

if __name__ == "__main__":
    update_workflow_for_youtube()
