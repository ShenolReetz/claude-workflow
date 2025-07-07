
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer
from mcp.amazon_affiliate_agent_mcp import run_amazon_affiliate_generation
from mcp_servers.content_generation_server import ContentGenerationMCPServer
from mcp.text_generation_control_agent_mcp_v2 import run_text_control_with_regeneration
from mcp.json2video_agent_mcp import run_video_creation
from mcp.amazon_drive_integration import save_amazon_images_to_drive
from mcp.amazon_images_workflow import download_and_save_amazon_images
from mcp.google_drive_agent_mcp import upload_video_to_google_drive
from mcp.wordpress_mcp import WordPressMCP
from mcp.youtube_mcp import YouTubeMCP

class ContentPipelineOrchestrator:
    def __init__(self):
        # Load configuration
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            self.config = json.load(f)
        
        # Initialize MCP servers
        self.airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        self.content_server = ContentGenerationMCPServer(
            anthropic_api_key=self.config['anthropic_api_key']
        )
        self.wordpress_mcp = WordPressMCP(self.config)

    async def run_complete_workflow(self):
        """Run the complete content generation workflow"""
        print(f"🚀 Starting content workflow at {datetime.now()}")
        
        # Step 1: Get pending title from Airtable
        print("📋 Getting pending title from Airtable...")
        pending_title = await self.airtable_server.get_pending_titles()
        
        if not pending_title:
            print("❌ No pending titles found. Exiting.")
            return
        
        print(f"✅ Found title: {pending_title['title']}")
        
        # Step 2: Generate SEO keywords
        print("🔍 Generating SEO keywords...")
        keywords = await self.content_server.generate_seo_keywords(
            pending_title['title'], 
            "Electronics"  # You can make this dynamic later
        )
        
        # Step 3: Optimize title
        print("🎯 Optimizing title for social media...")
        optimized_title = await self.content_server.optimize_title(
            pending_title['title'], 
            keywords
        )
        
        # Step 4: Generate countdown script
        print("📝 Generating countdown script...")
        script_data = await self.content_server.generate_countdown_script(
            optimized_title, 
            keywords
        )
        
        # Step 4.5: Text Generation Quality Control
        print("🎮 Running text generation quality control...")
        
        # First, we need to save the countdown script to Airtable
        await self._save_countdown_to_airtable(pending_title['record_id'], script_data)
        
        # Now run quality control
        control_result = await run_text_control_with_regeneration(self.config, pending_title['record_id'])
        
        if not control_result['success']:
            print(f"❌ Text control failed after {control_result.get('attempts', 0)} attempts")
            print(f"Issues: {control_result.get('error', 'Unknown error')}")
            # Continue anyway but log the issue
            await self.airtable_server.update_record(pending_title['record_id'], {
                'TextControlStatus': 'Failed',
                'Status': 'Processing'  # Keep processing but note the failure
            })
        elif control_result['all_valid']:
            print(f"✅ Text validated after {control_result['attempts']} attempt(s)")
            await self.airtable_server.update_record(pending_title['record_id'], {
                'TextControlStatus': 'Validated'
            })

        # Step 5: Generate blog post (disabled for testing)
        blog_post = "Blog post generation disabled during testing to save tokens."
        
        # Step 6: Save everything back to Airtable
        print("💾 Saving generated content to Airtable...")
        content_data = {
            'optimized_title': optimized_title,
            'script': script_data,
        }
        await self.airtable_server.save_generated_content(
            pending_title['record_id'],
            content_data
        )
        
        # Step 7: Generate Amazon affiliate links
        print("🔗 Generating Amazon affiliate links...")
        affiliate_result = await run_amazon_affiliate_generation(
            self.config,
            pending_title['record_id']
        )
        
        if affiliate_result.get('success'):
            links_count = affiliate_result.get('links_generated', 0)
            print(f"✅ Generated {links_count} affiliate links")
        else:
            print(f"⚠️ Affiliate link generation had issues: {affiliate_result.get('error', 'Unknown error')}")
        
        
            # Step 7b: Download and save Amazon product images
            print("📸 Downloading Amazon product images...")
            
            products_list = []
            for i in range(1, 6):
                product_title = saved_content.get(f'ProductNo{i}Title')
                if product_title:
                    products_list.append({
                        'title': product_title,
                        'description': saved_content.get(f'ProductNo{i}Description', '')
                    })
            
            amazon_images_result = await save_amazon_images_to_drive(
                self.config,
                pending_title['record_id'],
                video_result.get('project_name', pending_title['title']),
                products_list
            )
            
            if amazon_images_result['success']:
                print(f"✅ Saved {amazon_images_result['images_saved']} Amazon product images")
                
                for link_info in amazon_images_result.get('affiliate_links', []):
                    await update_airtable_record(
                        self.config,
                        pending_title['record_id'],
                        {f'ProductNo{link_info["product_num"]}AffiliateLink': link_info['affiliate_link']}
                    )


            # Step 7b: Download Amazon product images if available
            if affiliate_result.get('product_results'):
                print("📸 Downloading Amazon product images...")
                
                images_result = await download_and_save_amazon_images(
                    self.config,
                    pending_title['record_id'],
                    video_result.get('project_name', pending_title['title']),
                    affiliate_result.get('product_results', {})
                )
                
                if images_result['success']:
                    print(f"✅ Saved {images_result['images_saved']} Amazon product images")
                    print(f"📦 Products with images: {images_result['products_with_images']}")

# Step 8: Create video with JSON2Video
        print("🎬 Creating video with JSON2Video...")
        video_result = await run_video_creation(
            self.config,
            pending_title['record_id']
        )
        
        print(f"🔍 DEBUG: video_result = {video_result}")
        
        if video_result['success']:
            print(f"✅ Video created successfully!")
            
            # Step 9: Upload to Google Drive
            print("☁️ Uploading video to Google Drive...")
            upload_result = await upload_video_to_google_drive(
                self.config,
                video_result['video_url'],
                video_result.get('project_name', f'Video_{pending_title["record_id"]}'),
                pending_title['record_id']
            )
            
            if upload_result['success']:
                print(f"✅ Video uploaded to Google Drive: {upload_result['drive_url']}")
                
                # Create WordPress blog post
                try:
                    wp_result = await self.wordpress_mcp.create_review_post(pending_title)
                    if wp_result.get('success'):
                        print(f"✅ Blog post created: {wp_result.get('post_url')}")
                except Exception as e:
                    print(f"❌ Blog post error: {e}")

        # Upload to YouTube (if enabled)
        youtube_enabled = self.config.get('youtube_enabled', False)
        if youtube_enabled and video_result.get('video_url'):
            print("📹 Uploading to YouTube Shorts...")
            try:
                # Initialize YouTube MCP
                self.youtube_mcp = YouTubeMCP(
                    credentials_path=self.config.get('youtube_credentials', '/home/claude-workflow/config/youtube_credentials.json'),
                    token_path=self.config.get('youtube_token', '/home/claude-workflow/config/youtube_token.json')
                )
                
                # Prepare YouTube title (optimized for Shorts)
                youtube_prefix = self.config.get('youtube_title_prefix', '')
                youtube_suffix = self.config.get('youtube_title_suffix', '')
                youtube_title = f"{youtube_prefix}{pending_title.get("VideoTitle", pending_title.get("Title", pending_title.get("VideoTitle", "")))}{youtube_suffix}"[:100]  # YouTube limit
                
                # Build YouTube description
                youtube_description = f"{pending_title.get("VideoTitle", pending_title.get("Title", pending_title.get("VideoTitle", "")))}\n\n"
                
                # Add timestamps (for 8-second test videos)
                youtube_description += "⏱️ Timestamps:\n"
                youtube_description += "0:00 Intro\n"
                youtube_description += "0:02 Products\n"
                youtube_description += "0:06 Outro\n\n"
                
                # Add products with affiliate links
                youtube_description += "🛒 Featured Products:\n\n"
                products_found = False
                
                for i in range(1, 6):
                    product_title = pending_title.get(f'ProductNo{i}Title', '')
                    product_desc = pending_title.get(f'ProductNo{i}Description', '')
                    affiliate_link = pending_title.get(f'ProductNo{i}AffiliateLink', '')
                    
                    if product_title:
                        products_found = True
                        youtube_description += f"#{i} {product_title}\n"
                        if product_desc:
                            # Add first 100 chars of description
                            youtube_description += f"{product_desc[:100]}...\n"
                        if affiliate_link:
                            youtube_description += f"→ {affiliate_link}\n"
                        youtube_description += "\n"
                
                # Add keywords as hashtags
                if keywords:
                    youtube_description += "\n"
                    # Add up to 10 hashtags
                    for keyword in keywords[:10]:
                        hashtag = keyword.replace(' ', '').replace('-', '')
                        youtube_description += f"#{hashtag} "
                    youtube_description += "\n"
                
                # Add shorts hashtag
                shorts_tag = self.config.get('youtube_shorts_tag', '#shorts')
                youtube_description += f"\n{shorts_tag}\n"
                
                # Add disclaimer
                youtube_description += "\n" + "="*50 + "\n"
                youtube_description += "As an Amazon Associate I earn from qualifying purchases.\n"
                youtube_description += "="*50
                
                # Prepare tags
                youtube_tags = self.config.get('youtube_tags', []).copy()
                youtube_tags.append('shorts')  # Always add shorts tag
                
                # Add keywords as tags
                if keywords:
                    youtube_tags.extend([k.lower() for k in keywords[:10]])
                
                # Remove duplicates and limit tags
                youtube_tags = list(dict.fromkeys(youtube_tags))[:30]  # YouTube allows max 30 tags
                
                # Upload video
                youtube_result = await self.youtube_mcp.upload_video(
                    video_path=video_result.get('video_url'),
                    title=youtube_title,
                    description=youtube_description[:5000],  # YouTube limit
                    tags=youtube_tags,
                    category_id=self.config.get('youtube_category', '22'),  # People & Blogs
                    privacy_status=self.config.get('youtube_privacy', 'private')
                )
                
                if youtube_result.get('success'):
                    print(f"✅ YouTube upload successful!")
                    print(f"   URL: {youtube_result['video_url']}")
                    print(f"   Title: {youtube_result['title']}")
                    
                    # Update Airtable with YouTube info
                    youtube_updates = {
                        'YouTubeURL': youtube_result['video_url']
                    }
                    
                    await self.airtable_server.update_record(pending_title["record_id"], youtube_updates)
                    print("✅ Updated Airtable with YouTube URL")
                    
                else:
                    print(f"⚠️ YouTube upload failed: {youtube_result.get('error')}")
                    # Don't fail the whole workflow
                    
            except Exception as e:
                print(f"❌ YouTube error: {e}")
                # Continue workflow even if YouTube fails
                import traceback
                traceback.print_exc()
        


                 # Upload to YouTube Shorts
                        
 

        # Step 10: Update status
        print("✅ Updating record status to 'Done'...")
        await self.airtable_server.update_record_status(
            pending_title['record_id'],
            "Processing"
        )
        
        print("🎉 Complete workflow finished successfully!")
        print("📊 Summary:")
        print(f"   Original: {pending_title['title']}")
        print(f"   Optimized: {optimized_title}")
        print(f"   Products: {len(script_data.get('products', []))}")
        
    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script products to Airtable"""
        update_fields = {}
        
        # Save each product - these fields definitely exist
        if 'products' in script_data:
            for i, product in enumerate(script_data['products']):
                product_num = i + 1
                update_fields[f'ProductNo{product_num}Title'] = product.get('title', '')
                update_fields[f'ProductNo{product_num}Description'] = product.get('description', '')
        
        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
                print(f"💾 Saved {len(update_fields)} fields to Airtable")
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")


# Run the workflow
async def main():
    orchestrator = ContentPipelineOrchestrator()
    await orchestrator.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())
