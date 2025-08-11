#!/usr/bin/env python3
"""
Production Workflow Runner v2 - Enhanced with Scraping Variants
==============================================================

Updated workflow that:
1. Gets title from Airtable
2. Generates scraping variants from title  
3. Progressively tests variants until finding 5 products with 10+ reviews
4. Generates content based on successfully scraped products
5. Continues with rest of workflow
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

# Import resilience manager and token managers
from src.utils.api_resilience_manager import APIResilienceManager
from src.utils.google_drive_token_manager import GoogleDriveTokenManager
from src.utils.youtube_auth_manager import YouTubeAuthManager

# Import Production MCP servers
from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer
from mcp_servers.Production_content_generation_server import ProductionContentGenerationMCPServer
from mcp_servers.Production_progressive_amazon_scraper import ProductionProgressiveAmazonScraper
from mcp_servers.Production_voice_generation_server import ProductionVoiceGenerationMCPServer
from mcp_servers.Production_product_category_extractor_server import ProductionProductCategoryExtractorMCPServer
from mcp_servers.Production_flow_control_server import ProductionFlowControlMCPServer
from mcp_servers.Production_amazon_product_validator import ProductionAmazonProductValidator
from mcp_servers.Production_credential_validation_server import ProductionCredentialValidationServer

# Import Production MCP agents
from src.mcp.Production_amazon_affiliate_agent_mcp import production_run_amazon_affiliate_generation
from src.mcp.Production_text_generation_control_agent_mcp_v2 import production_run_text_control_with_regeneration
from src.mcp.Production_json2video_agent_mcp import production_run_video_creation
from src.mcp.Production_enhanced_google_drive_agent_mcp import production_upload_all_assets_to_google_drive
from src.mcp.Production_wordpress_mcp_v2 import ProductionWordPressMCPV2 as ProductionWordPressMCP
from src.mcp.Production_youtube_mcp import ProductionYouTubeMCP
from src.mcp.Production_voice_timing_optimizer import ProductionVoiceTimingOptimizer
from src.mcp.Production_intro_image_generator import production_generate_intro_image_for_workflow
from src.mcp.Production_outro_image_generator import production_generate_outro_image_for_workflow
from src.mcp.Production_platform_content_generator import production_generate_platform_content_for_workflow
from src.mcp.Production_text_length_validation_with_regeneration_agent_mcp import production_run_text_validation_with_regeneration
from src.mcp.Production_amazon_images_workflow_v2 import production_download_and_save_amazon_images_v2

# Use OpenAI Python client for DALL-E image generation
import openai

class ProductionContentPipelineOrchestratorV2:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/home/claude-workflow/workflow_output.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load real API keys from configuration
        config_path = '/home/claude-workflow/config/api_keys.json'
        with open(config_path, 'r') as f:
            self.config: Dict[str, any] = json.load(f)
        
        # Initialize API resilience manager
        self.api_manager = APIResilienceManager(self.config)
        
        # Set OpenAI API key for image generation
        openai.api_key = self.config.get('openai_api_key')
        
        # Initialize Production MCP servers with real API keys
        self.airtable_server = ProductionAirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )
        
        self.content_server = ProductionContentGenerationMCPServer(
            openai_api_key=self.config['openai_api_key']
        )
        
        # NEW: Enhanced progressive scraper with variants
        self.progressive_scraper = ProductionProgressiveAmazonScraper(
            scrapingdog_api_key=self.config['scrapingdog_api_key'],
            openai_api_key=self.config['openai_api_key']
        )
        
        self.category_extractor = ProductionProductCategoryExtractorMCPServer(
            openai_api_key=self.config['openai_api_key']
        )
        
        self.flow_control = ProductionFlowControlMCPServer(
            airtable_server=self.airtable_server
        )
        
        self.voice_server = ProductionVoiceGenerationMCPServer(
            elevenlabs_api_key=self.config['elevenlabs_api_key']
        )
        
        self.amazon_validator = ProductionAmazonProductValidator(
            scrapingdog_api_key=self.config['scrapingdog_api_key']
        )
        
        # Initialize platform services (production versions)
        self.wordpress_service = ProductionWordPressMCP(config=self.config)
        self.youtube_service = ProductionYouTubeMCP(config=self.config)
        
        # Initialize credential validation server
        self.credential_validator = ProductionCredentialValidationServer()
        
        print("🚀 PRODUCTION Content Pipeline Orchestrator V2 initialized successfully!")
        print("📋 Enhanced with scraping variants and progressive testing")
        print("🔍 Includes comprehensive credential validation checkpoint")

    async def refresh_tokens_before_workflow(self):
        """Refresh Google Drive and YouTube tokens before workflow starts"""
        print("\n🔄 Token Refresh Check")
        print("-" * 60)
        
        # Refresh Google Drive token
        print("📁 Checking Google Drive token...")
        google_token_manager = GoogleDriveTokenManager()
        google_status = google_token_manager.get_token_status()
        
        if google_status['needs_refresh'] or google_status['expired']:
            print(f"   Status: {google_status['status']} - Refreshing...")
            success, message = google_token_manager.refresh_token()
            if success:
                print(f"   ✅ Google Drive token refreshed: {message}")
            else:
                print(f"   ❌ Google Drive refresh failed: {message}")
                print("   ⚠️ Google Drive uploads may fail during workflow")
        else:
            print(f"   ✅ Google Drive token valid for {google_status.get('minutes_until_expiry', 0):.0f} minutes")
        
        # Refresh YouTube token if manager exists
        try:
            print("\n📺 Checking YouTube token...")
            youtube_manager = YouTubeAuthManager(self.config)
            youtube_status = youtube_manager.get_token_status()
            
            if youtube_status['needs_refresh'] or youtube_status['expired']:
                print(f"   Status: {youtube_status['status']} - Refreshing...")
                success, message = youtube_manager.refresh_token()
                if success:
                    print(f"   ✅ YouTube token refreshed: {message}")
                else:
                    print(f"   ❌ YouTube refresh failed: {message}")
                    print("   ⚠️ YouTube uploads may fail during workflow")
            else:
                print(f"   ✅ YouTube token valid for {youtube_status.get('minutes_until_expiry', 0):.0f} minutes")
        except Exception as e:
            print(f"   ⚠️ YouTube token check skipped: {e}")
        
        print("-" * 60)

    async def run_complete_workflow(self):
        """Run the complete production workflow with enhanced scraping variants"""
        print("\n🚀 Starting PRODUCTION WORKFLOW V2 (Enhanced Scraping)")
        print("=" * 60)
        
        # ALWAYS refresh tokens at the start since workflow runs 3x daily
        await self.refresh_tokens_before_workflow()
        
        try:
            # Step 1: Comprehensive Credential Validation Checkpoint
            print("\n🔍 Step 1: Credential Validation Checkpoint...")
            print("-" * 60)
            
            print("🔍 DEBUG: About to call validate_all_credentials()...")
            self.logger.info("🔍 DEBUG: Starting credential validation call...")
            
            # Add explicit timeout to the credential validation call
            try:
                validation_report = await asyncio.wait_for(
                    self.credential_validator.validate_all_credentials(),
                    timeout=300  # 5 minute timeout
                )
                self.logger.info("🔍 DEBUG: *** CRITICAL *** validate_all_credentials() RETURNED SUCCESSFULLY!")
                self.logger.info(f"🔍 DEBUG: Validation report keys: {list(validation_report.keys())}")
                self.logger.info("🔍 DEBUG: Credential validation completed successfully!")
                self.logger.info("🔍 DEBUG: About to print validation results...")
            except asyncio.TimeoutError:
                print("❌ CRITICAL ERROR: Credential validation timed out after 5 minutes!")
                self.logger.error("❌ CRITICAL ERROR: Credential validation timed out!")
                return
            except Exception as e:
                print(f"❌ CRITICAL ERROR: Credential validation failed with exception: {e}")
                self.logger.error(f"❌ CRITICAL ERROR: Credential validation exception: {e}")
                return
            
            # Print validation results
            self.logger.info("🔍 DEBUG: Starting validation results processing...")
            self.logger.info(f"📊 Health Score: {validation_report['health_score']}/100")
            self.logger.info(f"🚀 Status: {validation_report['overall_status'].upper()}")
            self.logger.info(f"🔍 DEBUG: can_proceed = {validation_report.get('can_proceed', 'NOT_FOUND')}")
            
            # Handle validation results
            self.logger.info("🔍 DEBUG: Checking validation results...")
            if not validation_report['can_proceed']:
                self.logger.info("🔍 DEBUG: Entering validation failure branch...")
                print("🔍 DEBUG: Entering validation failure branch...")
                print("\n❌ WORKFLOW ABORTED - Critical credential failures detected:")
                for failure in validation_report['critical_failures']:
                    print(f"   • {failure}")
                
                print("\n💡 Fix these issues before running the workflow:")
                print("   • Check /home/claude-workflow/config/api_keys.json")
                print("   • Run OAuth setup for Google Drive/YouTube if needed")
                print("   • Verify API quotas and account status")
                
                print("🔍 DEBUG: About to try Airtable update for failed validation...")
                # Update Airtable if we have a valid connection
                try:
                    pending_title = await asyncio.wait_for(
                        self.airtable_server.get_pending_title(),
                        timeout=30  # 30 second timeout
                    )
                    if pending_title:
                        record_id = pending_title.get('record_id', '')
                        await asyncio.wait_for(
                            self.airtable_server.update_record_field(
                                record_id, 'Status', 'Failed - Credential Issues'
                            ),
                            timeout=30
                        )
                        await asyncio.wait_for(
                            self.airtable_server.update_record_field(
                                record_id, 'ErrorMessage', f'Credential validation failed: {validation_report["critical_failures"][0] if validation_report["critical_failures"] else "Unknown error"}'
                            ),
                            timeout=30
                        )
                except Exception as e:
                    print(f"🔍 DEBUG: Airtable update failed with: {e}")
                    pass  # If Airtable fails, we can't update status
                
                print("🔍 DEBUG: Returning from validation failure branch...")
                return
            
            self.logger.info("🔍 DEBUG: Validation can proceed - checking warnings...")
            
            if validation_report['warnings']:
                self.logger.info("🔍 DEBUG: Entering warnings branch...")
                self.logger.info(f"🔍 DEBUG: Found {len(validation_report['warnings'])} warnings")
                print("🔍 DEBUG: Entering warnings branch...")
                print(f"\n⚠️  Proceeding with {len(validation_report['warnings'])} warnings:")
                
                # Process warnings with explicit timeout to prevent hanging
                try:
                    warnings_to_show = validation_report['warnings'][:3]  # Show first 3
                    self.logger.info(f"🔍 DEBUG: Processing {len(warnings_to_show)} warnings...")
                    
                    for i, warning in enumerate(warnings_to_show):
                        self.logger.info(f"🔍 DEBUG: Warning {i+1}: {warning}")
                        print(f"   • {warning}")
                    
                    if len(validation_report['warnings']) > 3:
                        remaining_count = len(validation_report['warnings']) - 3
                        self.logger.info(f"🔍 DEBUG: {remaining_count} additional warnings not shown")
                        print(f"   • ... and {remaining_count} more")
                    
                    print("   (Consider fixing for improved reliability)")
                    self.logger.info("🔍 DEBUG: Warnings processing completed successfully")
                    
                except Exception as e:
                    self.logger.error(f"🔍 DEBUG: Error processing warnings: {e}")
                    print("   (Error processing warnings - check logs)")
                    
                self.logger.info("🔍 DEBUG: Finished warnings branch")
            else:
                self.logger.info("🔍 DEBUG: No warnings - validation fully successful")
                print("🔍 DEBUG: No warnings - validation fully successful")
                print("✅ All credentials validated successfully")
            
            self.logger.info("🔍 DEBUG: Reached end of credential validation logic!")
            print("🔍 DEBUG: Reached end of credential validation logic!")
            print("✅ Credential validation passed - continuing with workflow")
            
            # Step 2: Get pending title from Airtable (REAL API)
            self.logger.info("🔍 DEBUG: Starting Step 2 - Fetching pending title from Airtable...")
            print("\n📋 Step 2: Fetching pending title from Airtable...")
            print("🔍 DEBUG: About to call get_pending_title()...")
            self.logger.info("🔍 DEBUG: About to call get_pending_title()...")
            pending_title = await self.airtable_server.get_pending_title()
            print(f"🔍 DEBUG: get_pending_title() returned: {pending_title}")
            
            if not pending_title:
                print("❌ No pending titles found in Airtable")
                return
            
            title = pending_title.get('Title', '')
            record_id = pending_title.get('record_id', '')
            print(f"✅ Retrieved title: {title}")
            print(f"🔍 DEBUG: Record ID: {record_id}")
            
            # Update status to Processing
            print("🔍 DEBUG: Updating status to Processing...")
            await self.airtable_server.update_record_field(record_id, 'Status', 'Processing')
            print("✅ Status updated to Processing")
            
            # Step 3: Generate scraping variants and test progressively
            print(f"\n🔍 Step 3: Progressive Amazon scraping with variants...")
            print(f"📋 Original title: {title}")
            print("🔍 DEBUG: About to call progressive_scraper.search_with_variants()...")
            
            amazon_products, successful_variant = await self.progressive_scraper.search_with_variants(
                title=title,
                target_products=5,
                min_reviews=10
            )
            
            print(f"🔍 DEBUG: search_with_variants() returned {len(amazon_products) if amazon_products else 0} products")
            
            if not amazon_products or len(amazon_products) < 5:
                print(f"❌ Could not find 5 products with sufficient reviews")
                await self.airtable_server.update_record_field(
                    record_id, 'Status', 'Failed - Insufficient Products'
                )
                return
            
            print(f"✅ SUCCESS: Found {len(amazon_products)} products using variant: '{successful_variant}'")
            
            # Note: SearchVariantUsed field doesn't exist in Airtable schema
            # Store variant info in TextControlStatus instead
            await self.airtable_server.update_record_field(
                record_id, 'TextControlStatus', f'Using search variant: {successful_variant}'
            )
            
            # Step 4: Extract product category
            print("\n🏷️ Step 4: Extracting product category...")
            category_info = await self.category_extractor.extract_category(title)
            category = category_info.get('category', 'General')
            print(f"✅ Category extracted: {category}")
            
            # Step 5: Validate Amazon products
            print("\n🔍 Step 5: Validating scraped products...")
            validation_result = await self.amazon_validator.validate_amazon_products(
                amazon_products, min_products=5
            )
            
            if not validation_result.get('valid', False):
                print(f"❌ Product validation failed: {validation_result.get('message', 'Unknown error')}")
                await self.airtable_server.update_record_field(
                    record_id, 'Status', 'Failed - Product Validation'
                )
                return
            
            print("✅ Product validation successful")
            
            # Step 6: FIRST - Save products to Airtable (names, prices, ratings, reviews, affiliate links, photos)
            print("\n💾 Step 6: Saving Amazon product data to Airtable...")
            
            # Save products FIRST
            updated_record = await self.airtable_server.save_amazon_products(
                record_id, amazon_products
            )
            
            print("✅ All 5 products saved to Airtable with complete data")
            
            # Step 5.5: Generate enhanced product images from scraped references
            print("\n🎨 Step 5.5: Generating enhanced product images with preserved details...")
            print("   📸 Using scraped images as references")
            print("   🏷️ Preserving logos, text, and specifications")
            print("   ✨ Optimizing for video content (9:16 ratio)")
            
            image_result = await production_download_and_save_amazon_images_v2(updated_record, self.config)
            
            if image_result.get('success', False):
                updated_record = image_result['updated_record']
                print("✅ Enhanced product images generated with all details preserved")
                
                # Update Airtable with generated image URLs
                for i in range(1, 6):
                    generated_url = updated_record['fields'].get(f'ProductNo{i}GeneratedPhoto')
                    if generated_url:
                        await self.airtable_server.update_record_field(
                            record_id, f'ProductNo{i}Photo', generated_url
                        )
            else:
                print("⚠️ Using original scraped images (enhancement failed)")
            
            # Step 7: THEN - Generate content based on scraped products
            print("\n📝 Step 7: Generating content based on saved products...")
            
            # Prepare product context for content generation
            product_context = self._prepare_product_context(amazon_products, successful_variant)
            
            platform_content = await production_generate_platform_content_for_workflow(
                title=title,
                category=category,
                config=self.config,
                products=amazon_products,
                variant_used=successful_variant
            )
            
            print("✅ Content generated based on scraped products")
            
            # Save keyword-optimized content with status updates (using actual Airtable field names)
            content_updates = {
                'VideoTitle': platform_content.get('video_title', title),  # ✅ Short intro title (max 7 words)
                'VideoDescription': platform_content.get('wordpress_description', ''),
                'YouTubeTitle': platform_content.get('youtube_title', ''),
                'YouTubeDescription': platform_content.get('youtube_description', ''),
                'InstagramCaption': platform_content.get('instagram_caption', ''),
                'InstagramHashtags': platform_content.get('instagram_hashtags', ''),
                'TikTokCaption': platform_content.get('tiktok_caption', ''),
                'TikTokHashtags': platform_content.get('tiktok_hashtags', ''),
                'WordPressTitle': platform_content.get('wordpress_title', ''),
                'WordPressContent': platform_content.get('wordpress_description', ''),  # Use WordPressContent instead of WordPressDescription
                'UniversalKeywords': ', '.join(platform_content.get('wordpress_keywords', [])),  # Use UniversalKeywords instead of SEOKeywords
                'VideoTitleStatus': 'Ready',
                'VideoDescriptionStatus': 'Ready'
            }
            
            for field, value in content_updates.items():
                await self.airtable_server.update_record_field(record_id, field, value)
            
            print("✅ Platform-optimized content saved to Airtable")
            
            # Step 6.5: Generate scripts for intro, outro, and products
            print("\n✍️ Step 6.5: Generating scripts for narration...")
            
            # Generate scripts using the text generation control agent
            script_result = await production_run_text_control_with_regeneration(
                updated_record, self.config
            )
            
            if script_result.get('success', False):
                updated_record = script_result['updated_record']
                print("✅ Scripts generated for intro, products, and outro")
                
                # Combine all scripts into VideoScript field
                all_scripts = []
                if 'IntroScript' in updated_record['fields']:
                    all_scripts.append(f"INTRO: {updated_record['fields']['IntroScript']}")
                for i in range(1, 6):
                    script_field = f'Product{i}Script'
                    if script_field in updated_record['fields']:
                        all_scripts.append(f"PRODUCT {i}: {updated_record['fields'][script_field]}")
                if 'OutroScript' in updated_record['fields']:
                    all_scripts.append(f"OUTRO: {updated_record['fields']['OutroScript']}")
                
                combined_script = "\n\n".join(all_scripts)
                await self.airtable_server.update_record_field(
                    record_id, 'VideoScript', combined_script
                )
            else:
                print("❌ Script generation failed")
                return
            
            # Step 8: Continue with rest of workflow (voice, images, video, publishing)
            print("\n🎙️ Step 8: Generating voice narration...")
            # Ensure we have proper record structure
            if not isinstance(updated_record, dict) or 'fields' not in updated_record:
                updated_record = {'record_id': record_id, 'fields': updated_record if isinstance(updated_record, dict) else {}}
            voice_result = await self.voice_server.generate_voice_for_record(updated_record)
            print("✅ Voice narration generated")
            
            # Step 9: Generate images
            print("\n🖼️ Step 9: Generating intro/outro images...")
            intro_result = await production_generate_intro_image_for_workflow(
                voice_result['updated_record'], self.config
            )
            
            outro_result = await production_generate_outro_image_for_workflow(
                intro_result['updated_record'], self.config
            )
            
            print("✅ Images generated")
            
            # Step 10: Content validation
            print("\n✅ Step 10: Content validation...")
            validation_result = await production_run_text_validation_with_regeneration(
                outro_result['updated_record'], self.config
            )
            
            if not validation_result.get('success', False):
                print("⚠️ Content validation issues detected")
                await self.airtable_server.update_record_field(
                    record_id, 'ContentValidationStatus', 'Failed'
                )
            else:
                await self.airtable_server.update_record_field(
                    record_id, 'ContentValidationStatus', 'Validated'
                )
            
            # Step 11: Video creation
            print("\n🎬 Step 11: Creating video...")
            video_result = await production_run_video_creation(
                validation_result.get('updated_record', outro_result['updated_record']), 
                self.config
            )
            
            if video_result.get('success', False):
                # ✅ FIXED: Save video URLs and project ID to Airtable
                project_id = video_result.get('project_id', '')
                video_url = video_result.get('video_url', '')
                dashboard_url = video_result.get('dashboard_url', '')
                
                # Update Airtable with video information
                if project_id:
                    await self.airtable_server.update_record_field(
                        record_id, 'JSON2VideoProjectID', project_id
                    )
                if video_url:
                    await self.airtable_server.update_record_field(
                        record_id, 'VideoURL', video_url
                    )
                if dashboard_url:
                    await self.airtable_server.update_record_field(
                        record_id, 'VideoDashboardURL', dashboard_url
                    )
                    
                await self.airtable_server.update_record_field(
                    record_id, 'VideoProductionRDY', 'Ready'
                )
                
                print("✅ Video created successfully")
                print(f"🎬 Direct Video URL: {video_url}")
                print(f"🌐 Dashboard URL: {dashboard_url}")
                print(f"🆔 Project ID: {project_id}")
            else:
                print("❌ Video creation failed")
                return
            
            # Step 12: Enhanced Google Drive upload (ALL assets)
            print("\n☁️ Step 12: Uploading ALL assets to Google Drive...")
            print("   📁 Creating organized folder structure")
            print("   🎬 Uploading final video")
            print("   🖼️ Uploading all product images")
            print("   🎨 Uploading intro/outro images") 
            print("   🎙️ Uploading all audio files")
            
            drive_result = await production_upload_all_assets_to_google_drive(
                video_result['updated_record'], self.config
            )
            
            if drive_result.get('success', False):
                print("✅ ALL assets uploaded to Google Drive with organized folders!")
                print(f"📂 Main folder: {drive_result.get('main_folder_url', 'N/A')}")
            else:
                print(f"❌ Google Drive upload failed: {drive_result.get('error', 'Unknown error')}")
            
            # Step 13: Platform publishing
            print("\n📤 Step 13: Publishing to platforms...")
            
            # YouTube upload
            fields = drive_result['updated_record'].get('fields', {})
            youtube_result = await self.youtube_service.upload_video(
                video_url=fields.get('VideoURL', ''),
                title=fields.get('YouTubeTitle', 'Product Review'),
                description=fields.get('YouTubeDescription', ''),
                tags=fields.get('UniversalKeywords', '').split(',')[:10]
            )
            
            # WordPress publishing
            wordpress_result = await self.wordpress_service.create_post(
                title=fields.get('WordPressTitle', 'Product Review'),
                content=fields.get('WordPressContent', ''),
                excerpt=fields.get('VideoDescription', '')[:200],
                tags=fields.get('UniversalKeywords', '').split(',')[:10]
            )
            
            # Update platform readiness
            platform_ready = []
            if youtube_result.get('success', False):
                platform_ready.append('Youtube')
            if wordpress_result.get('success', False):
                platform_ready.append('Website')
            
            await self.airtable_server.update_record_field(
                record_id, 'PlatformReadiness', platform_ready
            )
            
            print("✅ Platform publishing completed")
            
            # Step 14: Final completion
            print("\n🏁 Step 14: Workflow completion...")
            await self.airtable_server.update_record_field(record_id, 'Status', 'Completed')
            await self.airtable_server.update_record_field(
                record_id, 'LastOptimizationDate', datetime.now().isoformat()
            )
            
            print("🎉 PRODUCTION WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            self.logger.error(f"WORKFLOW ERROR ({error_type}): {error_msg}")
            
            # Handle specific error types
            if 'record_id' in locals():
                try:
                    # Determine appropriate status based on error type
                    if "quota" in error_msg.lower() or "429" in error_msg:
                        status = "Failed - API Quota Exhausted"
                        self.logger.error("OpenAI quota exhausted - workflow paused")
                    elif "rate" in error_msg.lower() and "limit" in error_msg.lower():
                        status = "Failed - Rate Limited"
                        self.logger.warning("Rate limit hit - will retry later")
                    elif "json2video" in error_msg.lower():
                        status = "Failed - Video Creation"
                        self.logger.error("JSON2Video service failed")
                    elif "amazon" in error_msg.lower() or "scraping" in error_msg.lower():
                        status = "Failed - Product Scraping"
                        self.logger.error("Amazon scraping failed")
                    else:
                        status = f"Failed - {error_type}"
                    
                    await self.airtable_server.update_record_field(record_id, 'Status', status)
                    
                    # Log detailed error for debugging
                    error_details = {
                        'timestamp': datetime.now().isoformat(),
                        'error_type': error_type,
                        'error_message': error_msg,
                        'record_id': record_id,
                        'api_health': self.api_manager.get_api_health_status()
                    }
                    
                    with open('/home/claude-workflow/error_log.json', 'a') as f:
                        f.write(json.dumps(error_details) + '\n')
                        
                except Exception as update_error:
                    self.logger.error(f"Failed to update Airtable status: {update_error}")
            
            # Don't re-raise for recoverable errors
            if "quota" not in error_msg.lower() and "429" not in error_msg:
                raise
    
    def _prepare_product_context(self, products: List[Dict], variant_used: str) -> str:
        """Prepare product context for content generation"""
        context = f"Search variant used: {variant_used}\n\n"
        context += "Products found:\n"
        
        for i, product in enumerate(products, 1):
            context += f"{i}. {product.get('title', 'Unknown')}\n"
            context += f"   Price: {product.get('price', 'N/A')}\n"
            context += f"   Rating: {product.get('rating', 'N/A')}\n"
            context += f"   Reviews: {product.get('reviews', 'N/A')}\n\n"
        
        return context
    
    async def _generate_content_with_products(
        self, 
        title: str, 
        category: str, 
        products: List[Dict], 
        variant_used: str
    ) -> Dict:
        """Generate content using actual scraped product data"""
        
        # Create enhanced prompt with product context
        product_details = "\n".join([
            f"Product {i+1}: {product.get('title', '')} - {product.get('price', '')} - {product.get('rating', '')} stars - {product.get('reviews', '')} reviews"
            for i, product in enumerate(products)
        ])
        
        enhanced_prompt = f"""
        Generate engaging video content for: {title}
        Category: {category}
        Search variant that worked: {variant_used}
        
        Based on these ACTUAL products found:
        {product_details}
        
        Create content that:
        1. References these specific products
        2. Mentions their actual prices and ratings
        3. Highlights why these products were selected
        4. Creates compelling reasons to check them out
        """
        
        try:
            # Use content generation server with enhanced prompt
            response = await self.content_server.generate_content(enhanced_prompt)
            
            return {
                'video_title': response.get('title', title),
                'video_description': response.get('description', ''),
                'youtube_title': response.get('youtube_title', title),
                'instagram_caption': response.get('instagram_caption', ''),
                'tiktok_caption': response.get('tiktok_caption', ''),
                'product_context': product_details
            }
            
        except Exception as e:
            print(f"❌ Content generation error: {e}")
            # Fallback to basic content
            return {
                'video_title': title,
                'video_description': f"Check out these amazing {category} products!",
                'youtube_title': title,
                'instagram_caption': f"Amazing {category} finds! #products #shopping",
                'tiktok_caption': f"Top {category} products you need! 🔥",
                'product_context': product_details
            }

if __name__ == "__main__":
    orchestrator = ProductionContentPipelineOrchestratorV2()
    asyncio.run(orchestrator.run_complete_workflow())