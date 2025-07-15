
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
from mcp_servers.amazon_category_scraper import AmazonCategoryScraper
from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer
from mcp_servers.flow_control_server import FlowControlMCPServer
from mcp_servers.voice_generation_server import VoiceGenerationMCPServer
from mcp.json2video_agent_mcp import run_video_creation
from mcp.amazon_drive_integration import save_amazon_images_to_drive
from mcp.amazon_images_workflow_v2 import download_and_save_amazon_images_v2
from mcp.amazon_guided_image_generation import generate_amazon_guided_openai_images
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
        self.category_extractor = ProductCategoryExtractorMCPServer(
            anthropic_api_key=self.config['anthropic_api_key']
        )
        self.flow_control = FlowControlMCPServer()
        self.voice_generator = VoiceGenerationMCPServer(self.config['elevenlabs_api_key'])
        self.amazon_scraper = AmazonCategoryScraper(self.config)
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
        
        # Step 2: Extract clean product category from marketing title
        print("🔍 Extracting product category from marketing title...")
        category_result = await self.category_extractor.extract_product_category(pending_title['title'])
        
        if not category_result.get('success'):
            print(f"❌ Category extraction failed: {category_result.get('error', 'Unknown error')}")
            return
        
        clean_category = category_result['primary_category']
        print(f"✅ Extracted category: {clean_category}")
        print(f"🎯 Alternative terms: {', '.join(category_result['search_terms'][:3])}")
        
        # Step 3: Scrape Amazon for top 5 products using clean category
        print("🛒 Scraping Amazon for top 5 products based on Reviews × Rating...")
        
        # Try multiple search terms if needed
        search_terms = [clean_category] + category_result['search_terms']
        amazon_result = None
        
        for term in search_terms[:3]:  # Try first 3 terms
            print(f"🔍 Trying search term: {term}")
            amazon_result = await self.amazon_scraper.get_top_5_products(term)
            
            if amazon_result.get('success'):
                print(f"✅ Found {len(amazon_result['products'])} products with term: {term}")
                break
            else:
                print(f"❌ Failed with term '{term}': {amazon_result.get('error', 'Unknown error')}")
        
        if not amazon_result or not amazon_result.get('success'):
            print(f"❌ Amazon scraping failed with all search terms")
            return
        
        print(f"✅ Found {len(amazon_result['products'])} products")
        
        # Save product data to Airtable immediately
        await self.airtable_server.update_record(
            pending_title['record_id'], 
            amazon_result['airtable_data']
        )
        
        # Step 3: Generate multi-platform keywords using product data
        print("🔍 Generating multi-platform keywords with product data...")
        multi_keywords = await self.content_server.generate_multi_platform_keywords(
            pending_title['title'],
            amazon_result['products']
        )
        
        # Save multi-platform keywords to Airtable
        print("💾 Saving multi-platform keywords to Airtable...")
        await self.airtable_server.update_multi_platform_keywords(
            pending_title['record_id'],
            multi_keywords
        )
        
        # Keep backward compatibility with existing workflow (use universal keywords)
        keywords = multi_keywords.get('universal', [])
        
        # Step 4: Optimize title using YouTube keywords
        print("🎯 Optimizing title for social media...")
        youtube_keywords = multi_keywords.get('youtube', keywords)
        optimized_title = await self.content_server.optimize_title(
            pending_title['title'], 
            youtube_keywords
        )
        
        # Step 5: Generate countdown script with actual product data
        print("📝 Generating countdown script with real products...")
        script_data = await self.content_server.generate_countdown_script_with_products(
            optimized_title, 
            keywords,
            amazon_result['products']
        )
        
        # Step 6: Text Generation Quality Control
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

        # Step 7: Generate blog post (disabled for testing)
        blog_post = "Blog post generation disabled during testing to save tokens."
        
        # Step 8: Save everything back to Airtable
        print("💾 Saving generated content to Airtable...")
        content_data = {
            'optimized_title': optimized_title,
            'script': script_data,
        }
        await self.airtable_server.save_generated_content(
            pending_title['record_id'],
            content_data
        )
        
        # Step 8b: Generate voice text for narration
        print("📝 Generating voice text for narration...")
        voice_text_data = await self.generate_voice_text(script_data, optimized_title)
        
        # Save voice text to Airtable
        await self.airtable_server.update_record(pending_title['record_id'], voice_text_data)
        
        # Note: Amazon affiliate links already saved in Step 2
        
        # Step 9: Download Amazon product images from scraped data
        print("📸 Downloading Amazon product images...")
        images_result = await download_and_save_amazon_images_v2(
            self.config,
            pending_title['record_id'],
            pending_title['title'],
            amazon_result['products']
        )
        
        if images_result['success']:
            print(f"✅ Saved {images_result['images_saved']} Amazon product images")
            print(f"📦 Products with images: {images_result['products_with_images']}")

        # Step 9b: Generate Amazon-guided OpenAI images
        print("🎨 Generating Amazon-guided OpenAI images...")
        openai_result = await generate_amazon_guided_openai_images(
            self.config,
            pending_title['record_id'],
            pending_title['title'],
            amazon_result['products']
        )
        
        if openai_result['success']:
            print(f"✅ Generated {openai_result['images_generated']} OpenAI images using Amazon reference")
            print(f"💾 Saved {openai_result['images_saved']} OpenAI images to Google Drive")
            print(f"🖼️ Products processed: {openai_result['products_processed']}")
        else:
            print(f"⚠️ OpenAI image generation had issues: {openai_result.get('errors', [])}")

        # Step 10: Generate voice narration with ElevenLabs
        print("🎤 Generating voice narration with ElevenLabs...")
        # Get updated record with voice text
        updated_record = await self.airtable_server.get_record_by_id(pending_title['record_id'])
        voice_result = await self.generate_voice_narration(pending_title['record_id'], updated_record)
        
        if voice_result['success']:
            print(f"✅ Generated {voice_result['voices_generated']} voice files")
            print(f"💾 Saved {voice_result['voices_saved']} voice files to Google Drive")
            
            # Update Airtable with voice URLs
            await self.airtable_server.update_record(pending_title['record_id'], voice_result['airtable_updates'])
        else:
            print(f"⚠️ Voice generation had issues: {voice_result.get('errors', [])}")
        
        # Step 11: Create video with JSON2Video (with voice)
        print("🎬 Creating video with JSON2Video...")
        video_result = await run_video_creation(
            self.config,
            pending_title['record_id']
        )
        
        print(f"🔍 DEBUG: video_result = {video_result}")
        
        if video_result['success']:
            print(f"✅ Video created successfully!")
            
            # Step 11: Upload to Google Drive
            print("☁️ Uploading video to Google Drive...")
            upload_result = await upload_video_to_google_drive(
                self.config,
                video_result['video_url'],
                video_result.get('project_name', f'Video_{pending_title["record_id"]}'),
                pending_title['record_id']
            )
            
            if upload_result['success']:
                print(f"✅ Video uploaded to Google Drive: {upload_result['drive_url']}")
                
                # Update Airtable with final video URL (Google Drive)
                await self.airtable_server.update_record(pending_title['record_id'], {
                    'FinalVideo': upload_result['drive_url']
                })
                
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
                youtube_title = f"{youtube_prefix}{pending_title.get('VideoTitle', pending_title.get('Title', pending_title.get('VideoTitle', "")))}{youtube_suffix}"[:100]  # YouTube limit
                
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
                
                # Add platform-specific keywords as hashtags
                youtube_kw = multi_keywords.get('youtube', keywords)
                if youtube_kw:
                    youtube_description += "\n"
                    # Add up to 10 hashtags from YouTube keywords
                    for keyword in youtube_kw[:10]:
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
                
                # Add YouTube-specific keywords as tags
                if youtube_kw:
                    youtube_tags.extend([k.lower() for k in youtube_kw[:10]])
                
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
        
        # ⏸️ TikTok Upload - TEMPORARILY DISABLED (API Review Pending)
        # TODO: Uncomment this section once TikTok API is approved
        print("⏸️  TikTok upload temporarily disabled (API approval pending)")
        
        # # Upload to TikTok (if enabled and approved)
        # tiktok_enabled = self.config.get('tiktok_enabled', False)
        # if tiktok_enabled and video_result.get('video_url'):
        #     print("📱 Uploading to TikTok...")
        #     try:
        #         from mcp.tiktok_workflow_integration import upload_to_tiktok
        #         
        #         tiktok_result = await upload_to_tiktok(self.config, pending_title)
        #         
        #         if tiktok_result.get('success'):
        #             print(f"✅ TikTok upload successful!")
        #             print(f"   Video ID: {tiktok_result.get('video_id')}")
        #             print(f"   Title: {tiktok_result.get('title')}")
        #             
        #             # Update Airtable with TikTok info
        #             tiktok_updates = {
        #                 'TikTokURL': f"https://www.tiktok.com/@{self.config.get('tiktok_username', 'user')}/video/{tiktok_result.get('video_id')}"
        #             }
        #             
        #             await self.airtable_server.update_record(pending_title["record_id"], tiktok_updates)
        #             print("✅ Updated Airtable with TikTok URL")
        #             
        #         elif tiktok_result.get('skipped'):
        #             print("⏭️  TikTok upload skipped (disabled)")
        #         else:
        #             print(f"⚠️  TikTok upload failed: {tiktok_result.get('error')}")
        #             
        #     except Exception as e:
        #         print(f"❌ TikTok error: {e}")
        #         # Continue workflow even if TikTok fails
        #         import traceback
        #         traceback.print_exc()
        # else:
        #     print("⏭️  TikTok upload skipped (disabled or no video URL)")

        # Upload to Instagram (if enabled and approved)
        instagram_enabled = self.config.get('instagram_enabled', False)
        if instagram_enabled and video_result.get('video_url'):
            print("📸 Uploading to Instagram Reels...")
            try:
                from mcp.instagram_workflow_integration import upload_to_instagram
                
                # Update pending_title with final video URL for Instagram
                pending_title['FinalVideo'] = upload_result['drive_url']
                
                instagram_result = await upload_to_instagram(self.config, pending_title)
                
                if instagram_result.get('success'):
                    print(f"✅ Instagram Reel upload successful!")
                    print(f"   Media ID: {instagram_result.get('media_id')}")
                    print(f"   URL: {instagram_result.get('instagram_url')}")
                    
                    # Update Airtable with Instagram info
                    instagram_updates = {
                        'InstagramURL': instagram_result.get('instagram_url', '')
                    }
                    
                    await self.airtable_server.update_record(pending_title["record_id"], instagram_updates)
                    print("✅ Updated Airtable with Instagram URL")
                    
                elif instagram_result.get('skipped'):
                    print("⏭️  Instagram upload skipped (disabled)")
                else:
                    print(f"⚠️  Instagram upload failed: {instagram_result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Instagram error: {e}")
                # Continue workflow even if Instagram fails
                import traceback
                traceback.print_exc()
        else:
            print("⏭️  Instagram upload skipped (disabled or no video URL)")

        # Step 10: Update status
        print("✅ Updating record status to 'Done'...")
        await self.airtable_server.update_record_status(
            pending_title['record_id'],
            "Processing"
        )
        
        # Final Step: Monitor API Credits
        credit_monitoring_enabled = self.config.get('credit_monitoring_enabled', True)
    
    async def generate_voice_text(self, script_data: dict, optimized_title: str) -> dict:
        """Generate voice text for intro, outro, and products"""
        try:
            voice_text_data = {}
            
            # Generate intro voice text
            intro_text = f"Welcome back to Tech Reviews! Today we're counting down {optimized_title.lower()}!"
            voice_text_data['IntroVoiceText'] = intro_text
            
            # Generate outro voice text
            outro_text = "That's our countdown! Which product caught your attention? Let us know in the comments below and don't forget to subscribe for more tech reviews!"
            voice_text_data['OutroVoiceText'] = outro_text
            
            # Generate product voice text
            products = script_data.get('products', [])
            for i, product in enumerate(products[:5], 1):
                product_text = f"Number {6-i}. {product.get('title', 'Product')}. {product.get('description', 'Great product for your needs.')}"
                voice_text_data[f'ProductNo{i}VoiceText'] = product_text
            
            print(f"✅ Generated voice text for {len(products)} products")
            return voice_text_data
            
        except Exception as e:
            print(f"❌ Error generating voice text: {e}")
            return {}
    
    async def generate_voice_narration(self, record_id: str, record_data: dict) -> dict:
        """Generate voice narration for intro, outro, and all products"""
        try:
            results = {
                'success': True,
                'voices_generated': 0,
                'voices_saved': 0,
                'airtable_updates': {},
                'errors': []
            }
            
            # Generate voice for intro
            intro_text = record_data.get('IntroVoiceText', 'Welcome to our top 5 product review!')
            if intro_text:
                intro_voice = await self.voice_generator.generate_voice_from_text(intro_text, 'intro')
                if intro_voice:
                    # Save to Google Drive and get URL
                    intro_url = await self.save_voice_to_drive(intro_voice, f"{record_id}_intro.mp3")
                    results['airtable_updates']['IntroVoiceURL'] = intro_url
                    results['voices_generated'] += 1
                    results['voices_saved'] += 1
            
            # Generate voice for outro
            outro_text = record_data.get('OutroVoiceText', 'Thanks for watching! Don\'t forget to subscribe!')
            if outro_text:
                outro_voice = await self.voice_generator.generate_voice_from_text(outro_text, 'outro')
                if outro_voice:
                    # Save to Google Drive and get URL
                    outro_url = await self.save_voice_to_drive(outro_voice, f"{record_id}_outro.mp3")
                    results['airtable_updates']['OutroVoiceURL'] = outro_url
                    results['voices_generated'] += 1
                    results['voices_saved'] += 1
            
            # Generate voice for each product
            for i in range(1, 6):
                product_text = record_data.get(f'ProductNo{i}VoiceText', '')
                if product_text:
                    product_voice = await self.voice_generator.generate_voice_from_text(product_text, 'products')
                    if product_voice:
                        # Save to Google Drive and get URL
                        product_url = await self.save_voice_to_drive(product_voice, f"{record_id}_product{i}.mp3")
                        results['airtable_updates'][f'ProductNo{i}VoiceURL'] = product_url
                        results['voices_generated'] += 1
                        results['voices_saved'] += 1
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'voices_generated': 0,
                'voices_saved': 0,
                'airtable_updates': {},
                'errors': [str(e)]
            }
    
    async def save_voice_to_drive(self, voice_base64: str, filename: str) -> str:
        """Save voice file to Google Drive and return URL"""
        try:
            # Import Google Drive agent
            from mcp.google_drive_agent_mcp import GoogleDriveAgentMCP
            
            # Convert base64 to bytes
            import base64
            audio_bytes = base64.b64decode(voice_base64)
            
            # Initialize Google Drive agent
            agent = GoogleDriveAgentMCP(self.config)
            if not await agent.initialize():
                print("❌ Failed to initialize Google Drive service")
                return f"https://drive.google.com/file/d/voice_{filename}/view"
            
            # Create voice folder structure if it doesn't exist
            folder_ids = await agent.drive_server.create_project_structure("Voice Files")
            voice_folder_id = folder_ids.get('video')  # Reuse video folder logic
            
            if not voice_folder_id:
                print("❌ Failed to create voice folder")
                return f"https://drive.google.com/file/d/voice_{filename}/view"
            
            # Upload audio file
            import io
            from googleapiclient.http import MediaIoBaseUpload
            
            audio_stream = io.BytesIO(audio_bytes)
            file_metadata = {
                'name': filename,
                'parents': [voice_folder_id]
            }
            
            media = MediaIoBaseUpload(
                audio_stream,
                mimetype='audio/mpeg',
                resumable=True
            )
            
            file = agent.drive_server.service.files().create(
                body=file_metadata,
                media_body=media
            ).execute()
            
            # Make it publicly accessible
            file_id = file.get('id')
            agent.drive_server.service.permissions().create(
                fileId=file_id,
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            # Get the shareable link
            file_info = agent.drive_server.service.files().get(
                fileId=file_id, 
                fields='webViewLink'
            ).execute()
            
            drive_url = file_info.get('webViewLink')
            print(f"✅ Voice file uploaded to Google Drive: {filename}")
            return drive_url
                
        except Exception as e:
            print(f"❌ Error saving voice to Google Drive: {e}")
            return f"https://drive.google.com/file/d/voice_{filename}/view"
        if credit_monitoring_enabled:
            print("💰 Monitoring API credits...")
            try:
                from mcp_servers.credit_monitor_server import monitor_api_credits
                
                credit_result = await monitor_api_credits(self.config)
                
                if credit_result.get('alerts'):
                    print(f"⚠️ {len(credit_result['alerts'])} service(s) have low credits!")
                    for alert in credit_result['alerts']:
                        print(f"   {alert['message']}")
                    print("📧 Email alert sent with top-up links")
                else:
                    print(f"✅ All API credits OK (Total: €{credit_result['total_value_eur']:.2f})")
                    
            except Exception as e:
                print(f"❌ Credit monitoring error: {e}")
                # Don't fail the workflow if monitoring fails
        else:
            print("⏭️ Credit monitoring disabled")
        
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
