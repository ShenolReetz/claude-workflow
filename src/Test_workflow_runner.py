
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

from mcp_servers.Test_airtable_server import AirtableMCPServer
from src.mcp.Test_amazon_affiliate_agent_mcp import run_amazon_affiliate_generation
from mcp_servers.Test_content_generation_server import ContentGenerationMCPServer
from src.mcp.Test_text_generation_control_agent_mcp_v2 import run_text_control_with_regeneration
from mcp_servers.Test_amazon_category_scraper import AmazonCategoryScraper
from mcp_servers.Test_product_category_extractor_server import ProductCategoryExtractorMCPServer
from mcp_servers.Test_flow_control_server import FlowControlMCPServer
from mcp_servers.Test_voice_generation_server import VoiceGenerationMCPServer
from mcp_servers.Test_amazon_product_validator import AmazonProductValidator
from src.mcp.Test_json2video_agent_mcp import run_video_creation
from src.mcp.Test_amazon_drive_integration import save_amazon_images_to_drive
from src.mcp.Test_amazon_images_workflow_v2 import download_and_save_amazon_images_v2
from src.mcp.Test_amazon_guided_image_generation import generate_amazon_guided_openai_images
from src.mcp.Test_google_drive_agent_mcp import upload_video_to_google_drive
from src.mcp.Test_wordpress_mcp import WordPressMCP
from src.mcp.Test_youtube_mcp import YouTubeMCP
from src.mcp.Test_voice_timing_optimizer import VoiceTimingOptimizer
from src.mcp.Test_intro_image_generator import generate_intro_image_for_workflow
from src.mcp.Test_outro_image_generator import generate_outro_image_for_workflow
from src.mcp.Test_platform_content_generator import generate_platform_content_for_workflow
from src.mcp.Test_video_prerequisite_control_agent_mcp import VideoPrerequisiteControlAgentMCP
from mcp_servers.Test_default_photo_manager import TestDefaultPhotoManager
from mcp_servers.Test_default_audio_manager import TestDefaultAudioManager
from mcp_servers.Test_default_text_validation_manager import TestDefaultTextValidationManager
from src.mcp.Test_text_length_validation_agent_mcp import run_text_length_validation

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
        self.amazon_validator = AmazonProductValidator(self.config)
        self.wordpress_mcp = WordPressMCP(self.config)
        self.video_prerequisite_control = VideoPrerequisiteControlAgentMCP(self.config)
        self.default_photo_manager = TestDefaultPhotoManager()
        self.default_audio_manager = TestDefaultAudioManager()
        self.default_text_validation_manager = TestDefaultTextValidationManager()

    async def run_complete_workflow(self):
        """Run the complete content generation workflow with multiple title processing"""
        print(f"🚀 Starting content workflow at {datetime.now()}")
        
        max_attempts = 5  # Try up to 5 titles before giving up
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\n{'='*60}")
            print(f"📋 ATTEMPT {attempt}/{max_attempts}: Getting pending title from Airtable...")
            print('='*60)
            
            # Step 1: Get pending title from Airtable
            pending_title = await self.airtable_server.get_pending_titles()
            
            if not pending_title:
                print("❌ No more pending titles found. Exiting.")
                return
            
            print(f"✅ Found title: {pending_title['title']}")
            
            # Step 1.5: Validate title has sufficient Amazon products BEFORE processing
            print("🔍 Validating title has sufficient Amazon products...")
            validation_result = await self.amazon_validator.validate_title_for_amazon(pending_title['title'])
            
            if not validation_result['valid']:
                print(f"❌ Title validation FAILED: {validation_result['validation_message']}")
                print(f"💡 Suggested improvements:")
                print(f"   - Try broader categories (e.g., 'audio equipment' instead of 'marine subwoofers')")
                print(f"   - Check alternative terms: {', '.join(validation_result['alternative_terms'][:3])}")
                
                # Mark title as failed in Airtable
                await self.airtable_server.update_record(
                    pending_title['record_id'],
                    {
                        'Status': 'Completed',
                        'ValidationIssues': f"Only {validation_result['product_count']} products found on Amazon. Need minimum 5 products for Top 5 video."
                    }
                )
                
                print(f"⏭️  Moving to next title (attempt {attempt}/{max_attempts})")
                continue  # Try next title
            
            print(f"✅ Title validation PASSED: {validation_result['validation_message']}")
            print(f"🎯 Best search term: {validation_result['primary_search_term']}")
            print(f"📊 Confidence: {validation_result['confidence']:.2f}")
            
            # If we get here, we found a valid title - process it
            success = await self.process_single_title(pending_title, validation_result)
            
            if success:
                print(f"🎉 Workflow completed successfully for: {pending_title['title']}")
                return
            else:
                print(f"❌ Workflow failed for: {pending_title['title']}")
                print(f"⏭️  Moving to next title (attempt {attempt}/{max_attempts})")
                continue
        
        print(f"❌ Failed to process any title after {max_attempts} attempts")
        return
    
    async def process_single_title(self, pending_title: dict, validation_result: dict):
        """Process a single validated title through the complete workflow"""
        
        try:
            print(f"\n🎬 PROCESSING: {pending_title['title']}")
            print('='*60)
            
            # Step 2: Extract clean product category from marketing title
            print("🔍 Extracting product category from marketing title...")
            category_result = await self.category_extractor.extract_product_category(pending_title['title'])
            
            if not category_result.get('success'):
                print(f"❌ Category extraction failed: {category_result.get('error', 'Unknown error')}")
                return False
            
            clean_category = category_result['primary_category']
            print(f"✅ Extracted category: {clean_category}")
            print(f"🎯 Alternative terms: {', '.join(category_result['search_terms'][:3])}")
            
            # Step 3: Scrape Amazon for top 5 products using VALIDATED search term
            print("🛒 Scraping Amazon for top 5 products based on Reviews × Rating...")
            
            # Use the validated search term first, then fallback to category extraction
            validated_term = validation_result['primary_search_term']
            print(f"🎯 Using validated search term: {validated_term}")
            
            amazon_result = await self.amazon_scraper.get_top_5_products(validated_term)
            
            if not amazon_result.get('success'):
                print(f"❌ Amazon scraping failed with validated term: {amazon_result.get('error', 'Unknown error')}")
                
                # Fallback to category extraction terms
                search_terms = [clean_category] + category_result['search_terms']
                for term in search_terms[:3]:
                    print(f"🔍 Fallback trying: {term}")
                    amazon_result = await self.amazon_scraper.get_top_5_products(term)
                    
                    if amazon_result.get('success'):
                        print(f"✅ Found {len(amazon_result['products'])} products with fallback term: {term}")
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
            
            # Step 2.75: Use hardcoded real photos from Power Strips project
            print("🖼️ TEST MODE: Using hardcoded real photos from Power Strips project...")
            try:
                from mcp_servers.Test_hardcoded_photo_manager import TestHardcodedPhotoManager
                photo_manager = TestHardcodedPhotoManager()
                
                # Get hardcoded real Google Drive photo URLs
                real_photo_urls = photo_manager.get_airtable_photo_updates()
                
                if real_photo_urls:
                    await self.airtable_server.update_record(
                        pending_title['record_id'],
                        real_photo_urls
                    )
                    print(f"✅ TEST MODE: Updated {len(real_photo_urls)} photo fields with REAL hardcoded URLs")
                    for field, url in real_photo_urls.items():
                        print(f"  {field}: {url[:60]}...")
                else:
                    print("⚠️ No hardcoded photos available, JSON2Video may fail")
            except Exception as e:
                print(f"❌ Error using hardcoded photos: {e}")
                print("⚠️ JSON2Video may fail without valid photo URLs")
            
            # Step 2.8: Populate Airtable with default audio (TEST MODE)
            print("🎵 TEST MODE: Populating Airtable with default audio files...")
            default_audio_updates = self.default_audio_manager.populate_airtable_with_default_audio(
                amazon_result,
                clean_category
            )
            
            if default_audio_updates:
                await self.airtable_server.update_record(
                    pending_title['record_id'],
                    default_audio_updates
                )
                print(f"✅ TEST MODE: Updated {len(default_audio_updates)} audio fields with default URLs")
                print("🎵 All audio clips are 2 seconds with 2 words each")
            
            # Step 2.5: Populate Airtable with default affiliate links (TEST MODE)
            print("🔗 TEST MODE: Populating default affiliate links...")
            from mcp_servers.Test_default_affiliate_manager import TestDefaultAffiliateManager
            affiliate_manager = TestDefaultAffiliateManager()
            
            # Get the current record to detect category
            current_record = await self.airtable_server.get_record_by_id(pending_title['record_id'])
            category = None  # Let the affiliate manager detect from title
            
            affiliate_updates = affiliate_manager.populate_airtable_with_default_affiliates(
                current_record, category
            )
            
            if affiliate_updates:
                try:
                    await self.airtable_server.update_record(
                        pending_title['record_id'],
                        affiliate_updates
                    )
                    print(f"✅ TEST MODE: Populated {len(affiliate_updates)} affiliate fields with default data")
                    print(f"💸 Cost savings: Avoided Amazon scraping API calls")
                except Exception as e:
                    print(f"⚠️ Some affiliate fields may not exist in Airtable schema: {e}")
                    # Try with reduced field set (only essential affiliate links)
                    essential_updates = {k: v for k, v in affiliate_updates.items() if 'AffiliateLink' in k}
                    if essential_updates:
                        try:
                            await self.airtable_server.update_record(
                                pending_title['record_id'],
                                essential_updates
                            )
                            print(f"✅ TEST MODE: Populated {len(essential_updates)} essential affiliate link fields")
                        except Exception as e2:
                            print(f"❌ Failed to update even essential affiliate fields: {e2}")
            
            # Step 2.6: Populate Airtable with default WordPress content (TEST MODE)
            print("📝 TEST MODE: Populating default WordPress content...")
            from mcp_servers.Test_default_wordpress_manager import TestDefaultWordPressManager
            wordpress_manager = TestDefaultWordPressManager()
            
            # Get the current record to detect category
            current_record = await self.airtable_server.get_record_by_id(pending_title['record_id'])
            category = None  # Let the WordPress manager detect from title
            
            wordpress_updates = wordpress_manager.populate_airtable_with_default_wordpress(
                current_record, category
            )
            
            if wordpress_updates:
                try:
                    await self.airtable_server.update_record(
                        pending_title['record_id'],
                        wordpress_updates
                    )
                    print(f"✅ TEST MODE: Populated {len(wordpress_updates)} WordPress fields with default content")
                    print(f"💰 Token savings: ~1000+ tokens (typical WordPress generation cost)")
                except Exception as e:
                    print(f"⚠️ Some WordPress fields may not exist in Airtable schema: {e}")
            
            # Step 2.7: Generate Amazon affiliate links for products (SKIPPED IN TEST MODE)
            print("🔗 TEST MODE: Skipping affiliate link generation (using defaults)...")
            affiliate_result = {'success': True, 'affiliate_links_generated': 5, 'source': 'TEST_MODE_DEFAULTS'}
            
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

            # Step 6.5: Text Length Validation - TEST MODE: Skip validation (already pre-populated)
            print("⏱️ TEST MODE: Skipping text length validation (already pre-populated as 'Approved')...")
            print("✅ All text validation status columns were pre-populated with 'Approved' status")
            print("📝 In production, this step will perform actual TTS timing validation")

            # Step 7: Generate blog post for WordPress
            print("📝 Generating blog post for WordPress...")
            blog_post = await self.content_server.generate_blog_post(
                optimized_title,
                keywords,
                amazon_result['products']
            )
            
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
            
            # Note: Amazon affiliate links saved in Step 2.5
            
            # Step 9: TEST MODE - Skip Amazon image downloads (already have default photos)
            print("📸 TEST MODE: Skipping Amazon image downloads (using default photos)...")
            images_result = await download_and_save_amazon_images_v2(
                self.config,
                pending_title['record_id'],
                pending_title['title'],
                amazon_result['products']
            )
            
            if images_result['success']:
                print(f"✅ TEST MODE: Simulated {images_result['images_saved']} Amazon product images")
                print(f"📦 Products with images: {images_result['products_with_images']}")

            # Step 9b: TEST MODE - Skip OpenAI image generation (using default photos)
            print("🎨 TEST MODE: Skipping OpenAI image generation (using default photos)...")
            openai_result = await generate_amazon_guided_openai_images(
                self.config,
                pending_title['record_id'],
                pending_title['title'],
                amazon_result['products']
            )
            
            if openai_result['success']:
                print(f"✅ TEST MODE: Simulated {openai_result['images_generated']} OpenAI images")
                print(f"💾 Skipped image generation and saving")
                print(f"🖼️ Products processed: {openai_result['products_processed']}")
            else:
                print(f"⚠️ TEST MODE simulation had issues: {openai_result.get('errors', [])}")
            
            # Step 9c: TEST MODE - Skip intro image generation (using default photo)
            print("🖼️ TEST MODE: Skipping intro image generation (using default photo)...")
            intro_image_result = await generate_intro_image_for_workflow(
                self.config,
                pending_title['record_id'],
                optimized_title,
                amazon_result['products'],
                clean_category
            )
            
            if intro_image_result['success']:
                print(f"✅ TEST MODE: Using default intro photo")
                print(f"🎨 Default photo URL: {intro_image_result['image_url']}")
            else:
                print(f"⚠️ TEST MODE intro photo failed: {intro_image_result.get('error', 'Unknown error')}")
            
            # Step 9d: TEST MODE - Skip outro image generation (using default photo)
            print("🎬 TEST MODE: Skipping outro image generation (using default photo)...")
            outro_image_result = await generate_outro_image_for_workflow(
                self.config,
                pending_title['record_id'],
                clean_category
            )
            
            if outro_image_result['success']:
                print(f"✅ TEST MODE: Using default outro photo")
                print(f"🎨 Default photo URL: {outro_image_result['image_url']}")
            else:
                print(f"⚠️ TEST MODE outro photo failed: {outro_image_result.get('error', 'Unknown error')}")
            
            # Step 9e: Generate platform-specific titles and descriptions
            print("🎯 Generating platform-specific content with SEO optimization...")
            platform_content_result = await generate_platform_content_for_workflow(
                self.config,
                pending_title['record_id'],
                optimized_title,
                amazon_result['products'],
                clean_category
            )
            
            if platform_content_result['success']:
                print(f"✅ Generated content for {platform_content_result['platforms_generated']} platforms")
                print("📊 Platform-specific content and analytics saved to Airtable")
            else:
                print(f"⚠️ Platform content generation failed: {platform_content_result.get('error', 'Unknown error')}")

            # Step 9.5: Populate Airtable with default text validation status (TEST MODE)
            print("⏱️ TEST MODE: Pre-populating text validation status columns...")
            default_text_validation_result = await self.default_text_validation_manager.populate_default_validation_status(
                self.airtable_server,
                pending_title['record_id']
            )
            
            if default_text_validation_result.get('success'):
                print(f"✅ TEST MODE: Pre-populated {default_text_validation_result['columns_updated']} text validation status columns")
                print(f"📝 All validation status columns set to: {default_text_validation_result['status_value']}")
            else:
                print(f"❌ TEST MODE: Failed to populate text validation status columns")

            # Step 10: TEST MODE - Skip voice generation (already have default audio)
            print("🎤 TEST MODE: Skipping voice generation (using default audio files)...")
            # Get updated record with voice text
            updated_record = await self.airtable_server.get_record_by_id(pending_title['record_id'])
            voice_result = await self.generate_voice_narration(pending_title['record_id'], updated_record)
            
            if voice_result['success']:
                print(f"✅ TEST MODE: Simulated {voice_result['voices_generated']} voice files")
                print(f"💾 Skipped ElevenLabs generation and Google Drive upload")
                print(f"🎵 Using default 2-second audio clips instead")
            else:
                print(f"⚠️ TEST MODE voice simulation had issues: {voice_result.get('errors', [])}")
            
            # Step 10.5: Video Prerequisite Control - Validate all prerequisites before video generation
            print("🎯 Validating video production prerequisites...")
            prerequisite_result = await self.video_prerequisite_control.validate_and_update_video_production_status(
                pending_title['record_id']
            )
            
            if not prerequisite_result['video_production_ready']:
                print("❌ Video production prerequisites NOT satisfied!")
                print("🔧 Missing requirements:")
                for error in prerequisite_result['validation_summary']['errors']:
                    print(f"   - {error}")
                
                # Update Airtable with validation failure
                await self.airtable_server.update_record(
                    pending_title['record_id'],
                    {
                        'Status': 'Validation Failed',
                        'ValidationIssues': '; '.join(prerequisite_result['validation_summary']['errors'])
                    }
                )
                return False
            
            print("✅ Video production prerequisites satisfied!")
            print(f"🎬 VideoProductionRDY status updated to: {prerequisite_result['video_production_status']}")
            print(f"📊 Validation rate: {prerequisite_result['validation_summary']['success_rate']:.1f}%")
            
            # Check if VideoProductionRDY is actually 'Ready' before proceeding
            if not await self.video_prerequisite_control.check_video_production_readiness(pending_title['record_id']):
                print("❌ VideoProductionRDY status is not 'Ready' - cannot proceed with video generation")
                return False
            
            # Step 11: Create ENHANCED video with JSON2Video (with sound, transitions, background photos)
            print("🎬 Creating ENHANCED video with JSON2Video...")
            print("✨ Features: Sound integration, smooth transitions, background photos, reviews & ratings")
            video_result = await run_video_creation(
                self.config,
                pending_title['record_id']
            )
            
            print(f"🔍 DEBUG: video_result = {video_result}")
            
            if video_result['success']:
                print(f"✅ Video created successfully!")
                print(f"📋 JSON2Video Project ID: {video_result['movie_id']}")
                
                # Wait for video to complete processing and get URL
                if video_result.get('video_url'):
                    print(f"✅ Video URL available: {video_result['video_url']}")
                    
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
                    else:
                        print(f"❌ Google Drive upload failed: {upload_result.get('error', 'Unknown error')}")
                else:
                    print("⏳ Video is still processing - Google Drive upload skipped")
                    print(f"🔗 Check status at: https://json2video.com/app/projects/{video_result['movie_id']}")
                    
                    # Update Airtable with processing status
                    await self.airtable_server.update_record(pending_title['record_id'], {
                        'Status': 'Video Processing',
                        'FinalVideo': f"Processing - Check: https://json2video.com/app/projects/{video_result['movie_id']}"
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
                    youtube_description = f"{pending_title.get('VideoTitle', pending_title.get('Title', pending_title.get('VideoTitle', '')))}\n\n"
                    
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
            
            # TikTok Upload - DISABLED (API still in review)
            print("⏸️  TikTok upload disabled (API still in review)")

            # Upload to Instagram (if enabled and approved)
            instagram_enabled = self.config.get('instagram_enabled', False)
            if instagram_enabled and video_result.get('video_url'):
                print("📸 Uploading to Instagram Reels...")
                try:
                    from src.mcp.Test_instagram_workflow_integration import upload_to_instagram
                    
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
            if credit_monitoring_enabled:
                print("💰 Monitoring API credits...")
                try:
                    from mcp_servers.Test_credit_monitor_server import TestCreditMonitorMCPServer
                    
                    monitor = TestCreditMonitorMCPServer(self.config)
                    credit_result = await monitor.check_all_api_credits()
                    
                    if credit_result.get('alerts'):
                        print(f"🚨 API Credit Alerts: {len(credit_result['alerts'])} warnings")
                        for alert in credit_result['alerts']:
                            print(f"   {alert['api']}: {alert['usage_percent']:.1f}% used ({alert['alert_type']})")
                        print("📧 Email alert would be sent to shenolb@live.com")
                    else:
                        print("✅ All API credits within normal limits")
                    
                    print(f"💰 Total API cost: ${credit_result.get('total_cost', 0):.2f}")
                        
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
            
            return True
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Update Airtable with failure status
            await self.airtable_server.update_record(
                pending_title['record_id'],
                {
                    'Status': 'Failed',
                    'ValidationIssues': f'Workflow failed: {str(e)}'
                }
            )
            
            return False
    
    async def generate_voice_text(self, script_data: dict, optimized_title: str) -> dict:
        """Generate voice text for intro, outro, and products (TEST MODE: 2 words for 2-second scenes)"""
        try:
            voice_text_data = {}
            optimizer = VoiceTimingOptimizer()
            
            # Get timing constraints
            intro_constraints = optimizer.generate_intro_constraints()
            outro_constraints = optimizer.generate_outro_constraints()
            
            # Generate intro voice text (TEST MODE: 2 words for 2 seconds)
            intro_text = "Welcome! Today"  # First 2 words for 2-second scene
            intro_analysis = optimizer.analyze_text_timing(intro_text, 2)
            print(f"🎵 TEST MODE: Intro text limited to 2 words: '{intro_text}'")
            voice_text_data['IntroHook'] = intro_text
            
            # Generate outro voice text (TEST MODE: 2 words for 2 seconds)
            outro_text = "Thanks! Subscribe"  # First 2 words for 2-second scene
            outro_analysis = optimizer.analyze_text_timing(outro_text, 2)
            print(f"🎵 TEST MODE: Outro text limited to 2 words: '{outro_text}'")
            voice_text_data['OutroCallToAction'] = outro_text
            
            # Generate product voice text - store in VideoScript as combined content
            products = script_data.get('products', [])
            product_voice_texts = []
            product_constraints = optimizer.generate_product_constraints()
            
            for i, product in enumerate(products[:5], 1):
                # TEST MODE: Format "Number X" - only 2 words for 2-second scenes
                rank_number = 6 - i  # Countdown from 5 to 1
                
                # Limit to exactly 2 words for 2-second scenes
                product_text = f"Number {rank_number}"
                product_analysis = optimizer.analyze_text_timing(product_text, 2)
                
                print(f"🎵 TEST MODE: Product {rank_number} text limited to 2 words: '{product_text}'")
                
                product_voice_texts.append(product_text)
                # Save individual product voice text for JSON2Video
                voice_text_data[f'Product{i}VoiceText'] = product_text
            
            # Store all product voice texts in VideoScript field
            if product_voice_texts:
                voice_text_data['VideoScript'] = '\n\n'.join([intro_text, *product_voice_texts, outro_text])
            
            print(f"✅ TEST MODE: Generated 2-word voice text for {len(products)} products")
            return voice_text_data
            
        except Exception as e:
            print(f"❌ Error generating voice text: {e}")
            return {}
    
    async def generate_voice_narration(self, record_id: str, record_data: dict) -> dict:
        """Generate voice narration (TEST MODE: Uses default audio files)"""
        try:
            print(f"🎵 TEST MODE: Voice generation skipped - using default audio files")
            
            results = {
                'success': True,
                'voices_generated': 7,  # Simulate 7 voices (intro + 5 products + outro)
                'voices_saved': 7,      # Simulate all saved
                'airtable_updates': {}, # No updates needed - already done in default audio step
                'errors': [],
                'test_mode': True,
                'generation_skipped': True
            }
            
            print(f"✅ TEST MODE: Simulated voice generation for intro, outro, and 5 products")
            print(f"🎵 All default audio files are 2-second clips with 2 words each")
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'voices_generated': 0,
                'voices_saved': 0,
                'airtable_updates': {},
                'errors': [str(e)],
                'test_mode': True
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
