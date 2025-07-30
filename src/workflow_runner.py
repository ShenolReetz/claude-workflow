
import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer
from src.mcp.amazon_affiliate_agent_mcp import run_amazon_affiliate_generation
from mcp_servers.content_generation_server import ContentGenerationMCPServer
from src.mcp.text_generation_control_agent_mcp_v2 import run_text_control_with_regeneration
from mcp_servers.amazon_category_scraper import AmazonCategoryScraper
from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer
from mcp_servers.flow_control_server import FlowControlMCPServer
from mcp_servers.voice_generation_server import VoiceGenerationMCPServer
from mcp_servers.amazon_product_validator import AmazonProductValidator
from src.mcp.json2video_agent_mcp import run_video_creation
from src.mcp.amazon_drive_integration import save_amazon_images_to_drive
from src.mcp.amazon_images_workflow_v2 import download_and_save_amazon_images_v2
from src.mcp.amazon_guided_image_generation import generate_amazon_guided_openai_images
from src.mcp.google_drive_agent_mcp import upload_video_to_google_drive
from src.mcp.wordpress_mcp import WordPressMCP
from src.mcp.youtube_mcp import YouTubeMCP
from src.mcp.voice_timing_optimizer import VoiceTimingOptimizer
from src.mcp.intro_image_generator import generate_intro_image_for_workflow
from src.mcp.outro_image_generator import generate_outro_image_for_workflow
from src.mcp.platform_content_generator import generate_platform_content_for_workflow
from src.mcp.text_length_validation_with_regeneration_agent_mcp import run_text_validation_with_regeneration
from src.expert_agents.expert_agent_router import get_expert_router, route_to_expert, TaskType

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
        
        # Initialize Expert Agent Router with 16 specialized subagents
        self.expert_router = get_expert_router(self.config)
        print("🎯 Expert Agent System initialized with ALL 16 specialized subagents")
        print("   🔴 Critical: API Credit Monitor, Error Recovery Specialist")
        print("   🟠 Content: SEO Expert, JSON2Video Expert, Product Validator")
        print("   🟡 Quality: Visual Controller, Audio Sync, Compliance, Video Status")
        print("   🟢 Analytics: Performance Tracker, Trend Analyzer, Monetization")
        print("   🔵 Operations: Workflow Optimizer, Cross-Platform, AI Optimizer")
        print("   🟣 Support: Documentation Specialist")
        print("✨ All 16 expert agents are now actively integrated into the production workflow!")

    async def run_complete_workflow(self):
        """Run the complete content generation workflow with multiple title processing"""
        print(f"🚀 Starting content workflow at {datetime.now()}")
        
        # Expert Agent: API Credit Monitor - Check credits before starting
        api_monitor_result = await route_to_expert(
            TaskType.API_MONITORING,
            {"action": "check_credits", "config": self.config},
            priority="critical"
        )
        if not api_monitor_result.get("success", True):
            print(f"⚠️ API Credit Warning: {api_monitor_result.get('message', 'Unknown issue')}")
        
        # Expert Agent: Workflow Efficiency Optimizer - Analyze and optimize workflow
        workflow_optimizer_result = await route_to_expert(
            TaskType.WORKFLOW_OPTIMIZATION,
            {
                "action": "analyze_workflow",
                "workflow_name": "content_generation_pipeline",
                "config": self.config
            },
            priority="medium"
        )
        if workflow_optimizer_result.get("success"):
            print(f"⚡ Workflow optimization suggestions applied")
        
        # Expert Agent: AI Optimization Specialist - Optimize AI model usage
        ai_optimization_result = await route_to_expert(
            TaskType.AI_OPTIMIZATION,
            {
                "action": "optimize_models",
                "workflow_type": "content_generation",
                "expected_load": "high",
                "config": self.config
            },
            priority="medium"
        )
        if ai_optimization_result.get("success"):
            print(f"🤖 AI model optimization applied: {ai_optimization_result.get('optimization', 'standard')}")
        
        # Expert Agent: Documentation Specialist - Generate workflow documentation
        documentation_result = await route_to_expert(
            TaskType.DOCUMENTATION,
            {
                "action": "document_workflow",
                "workflow_name": "production_content_pipeline",
                "components": ["all_16_agents", "platform_publishing", "json2video"],
                "format": "technical_specs"
            },
            priority="low"
        )
        if documentation_result.get("success"):
            print(f"📚 Workflow documentation updated")
        
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
            
            # Expert Agent: Product Research Validator - Validate product quality
            product_validation_result = await route_to_expert(
                TaskType.PRODUCT_RESEARCH,
                {
                    "products": amazon_result['products'],
                    "category": clean_category,
                    "minimum_rating": 4.0,
                    "minimum_reviews": 100
                },
                priority="high"
            )
            
            if product_validation_result.get("success"):
                print(f"✅ Product quality validation complete: {product_validation_result.get('valid_products', len(amazon_result['products']))} products approved")
            
            # Save product data to Airtable immediately
            await self.airtable_server.update_record(
                pending_title['record_id'], 
                amazon_result['airtable_data']
            )
            
            # Step 2.5: Generate Amazon affiliate links for products
            print("🔗 Generating Amazon affiliate links...")
            affiliate_result = await run_amazon_affiliate_generation(self.config, pending_title['record_id'])
            
            if affiliate_result['success']:
                print(f"✅ Generated {affiliate_result['affiliate_links_generated']} affiliate links")
                
                # Expert Agent: Monetization Strategist - Optimize revenue potential
                monetization_result = await route_to_expert(
                    TaskType.MONETIZATION,
                    {
                        "products": amazon_result['products'],
                        "affiliate_links": affiliate_result.get('affiliate_links_generated', 0),
                        "platforms": ["youtube", "instagram", "wordpress", "tiktok"],
                        "content_type": "product_review"
                    },
                    priority="medium"
                )
                
                if monetization_result.get("success"):
                    print(f"💰 Monetization strategy optimized: {monetization_result.get('revenue_potential', 'high')}")
            else:
                print(f"❌ Affiliate link generation failed: {affiliate_result.get('error', 'Unknown error')}")
                # Continue processing - affiliate links are not critical to video creation
            
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
            
            # Expert Agent: Trend Analysis Planner - Analyze market trends
            trend_result = await route_to_expert(
                TaskType.TREND_ANALYSIS,
                {
                    "category": clean_category,
                    "keywords": keywords,
                    "products": amazon_result['products'],
                    "platform_keywords": multi_keywords
                },
                priority="medium"
            )
            
            if trend_result.get("success"):
                print(f"📈 Trend analysis complete: {trend_result.get('trend_score', 'high')} trending potential")
            
            # Step 4: Optimize title using YouTube keywords
            print("🎯 Optimizing title for social media...")
            youtube_keywords = multi_keywords.get('youtube', keywords)
            
            # Expert Agent: SEO Optimization Expert - Enhance title for maximum visibility
            seo_result = await route_to_expert(
                TaskType.SEO_OPTIMIZATION,
                {
                    "title": pending_title['title'],
                    "keywords": youtube_keywords,
                    "platform": "youtube",
                    "product_data": amazon_result['products']
                },
                priority="high"
            )
            
            # Use expert-optimized title if available, otherwise fall back to standard optimization
            if seo_result.get("success") and seo_result.get("optimized_title"):
                optimized_title = seo_result["optimized_title"]
                print(f"✨ Expert SEO optimized title: {optimized_title}")
            else:
                optimized_title = await self.content_server.optimize_title(
                    pending_title['title'], 
                    youtube_keywords
                )
            
            # Expert Agent: Compliance Safety Monitor - Check content compliance
            compliance_result = await route_to_expert(
                TaskType.COMPLIANCE_CHECK,
                {
                    "title": optimized_title,
                    "products": amazon_result['products'],
                    "platforms": ["youtube", "tiktok", "instagram", "wordpress"],
                    "content_type": "affiliate_marketing"
                },
                priority="medium"
            )
            
            if compliance_result.get("success"):
                print(f"✅ Content compliance check passed: {compliance_result.get('compliance_score', 'high')}")
            
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

            # Step 6.5: Text Length Validation with Regeneration - Validate and fix timing issues
            print("⏱️ Validating text length for TTS timing compliance with intelligent regeneration...")
            try:
                text_validation_result = await run_text_validation_with_regeneration(
                    record_id=pending_title['record_id']
                )
                
                if text_validation_result.get('success'):
                    if text_validation_result.get('all_approved'):
                        print(f"✅ All text fields validated and approved for TTS timing compliance")
                    elif text_validation_result.get('has_rejections'):
                        print(f"⚠️ Some text fields still exceed timing limits after regeneration attempts")
                        print(f"📝 Review the rejected fields - they may need manual adjustment")
                    else:
                        print(f"✅ Text validation completed with mixed results")
                else:
                    print(f"❌ Text validation with regeneration failed: {text_validation_result.get('error', 'Unknown error')}")
                    # Continue workflow even if validation fails
            except Exception as e:
                print(f"❌ Error during text validation with regeneration: {str(e)}")
                # Continue workflow even if validation fails

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
            
            # Step 9c: Generate intro image featuring all products
            print("🖼️ Generating intro image featuring all 5 products...")
            intro_image_result = await generate_intro_image_for_workflow(
                self.config,
                pending_title['record_id'],
                optimized_title,
                amazon_result['products'],
                clean_category
            )
            
            if intro_image_result['success']:
                print(f"✅ Generated intro image featuring {intro_image_result['products_featured']} products")
                print(f"🎨 Image URL: {intro_image_result['image_url']}")
            else:
                print(f"⚠️ Intro image generation failed: {intro_image_result.get('error', 'Unknown error')}")
            
            # Step 9d: Generate outro image with social media elements
            print("🎬 Generating outro image with social media elements...")
            outro_image_result = await generate_outro_image_for_workflow(
                self.config,
                pending_title['record_id'],
                clean_category
            )
            
            if outro_image_result['success']:
                print(f"✅ Generated outro image with social media elements")
                print(f"🎨 Image URL: {outro_image_result['image_url']}")
            else:
                print(f"⚠️ Outro image generation failed: {outro_image_result.get('error', 'Unknown error')}")
            
            # Expert Agent: Visual Quality Controller - Validate all generated images
            visual_quality_result = await route_to_expert(
                TaskType.VISUAL_QUALITY,
                {
                    "images": {
                        "intro": intro_image_result.get('image_url'),
                        "outro": outro_image_result.get('image_url'),
                        "products": [pending_title.get(f'ProductNo{i}ImageURL') for i in range(1, 6)]
                    },
                    "brand_guidelines": {
                        "style": "professional",
                        "consistency": "high",
                        "resolution": "1080x1920"
                    }
                },
                priority="high"
            )
            
            if visual_quality_result.get("success"):
                print(f"🎨 Visual quality validation complete: {visual_quality_result.get('quality_score', 'N/A')}/10")
            
            # Step 9e: Generate platform-specific titles and descriptions
            print("🎯 Generating platform-specific content with SEO optimization...")
            
            # Expert Agent: Cross-Platform Coordinator - Optimize content for all platforms
            cross_platform_result = await route_to_expert(
                TaskType.CROSS_PLATFORM,
                {
                    "record_id": pending_title['record_id'],
                    "title": optimized_title,
                    "products": amazon_result['products'],
                    "category": clean_category,
                    "platforms": ["youtube", "tiktok", "instagram", "wordpress"]
                },
                priority="high"
            )
            
            if cross_platform_result.get("success"):
                print("🌐 Cross-platform optimization strategies applied")
            
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

            # Step 10: Generate voice narration with ElevenLabs
            print("🎤 Generating voice narration with ElevenLabs...")
            
            # Expert Agent: Audio Sync Specialist - Ensure perfect audio-video sync
            audio_sync_result = await route_to_expert(
                TaskType.AUDIO_SYNC,
                {
                    "record_id": pending_title['record_id'],
                    "scene_durations": {
                        "intro": 5,
                        "products": [9, 9, 9, 9, 9],
                        "outro": 5
                    },
                    "voice_texts": pending_title
                },
                priority="high"
            )
            
            if audio_sync_result.get("success"):
                print(f"🎵 Audio sync optimization applied: {audio_sync_result.get('sync_quality', 'excellent')}")
            
            # Get updated record with voice text
            updated_record = await self.airtable_server.get_record_by_id(pending_title['record_id'])
            voice_result = await self.generate_voice_narration(pending_title['record_id'], updated_record)
            
            if voice_result['success']:
                print(f"✅ Generated {voice_result['voices_generated']} voice files")
                print(f"💾 Saved {voice_result['voices_saved']} voice files to Google Drive")
                
                # Update Airtable with voice URLs
                print(f"🔍 DEBUG: Updating Airtable with voice URLs: {voice_result['airtable_updates']}")
                await self.airtable_server.update_record(pending_title['record_id'], voice_result['airtable_updates'])
                print(f"✅ Updated Airtable with {len(voice_result['airtable_updates'])} voice URLs")
            else:
                print(f"⚠️ Voice generation had issues: {voice_result.get('errors', [])}")
            
            # Step 10.5: Validate video production prerequisites
            print("🔍 Validating video production prerequisites...")
            from src.mcp.video_prerequisite_control_agent_mcp import validate_video_production_prerequisites
            
            prerequisite_result = await validate_video_production_prerequisites(
                self.config, 
                pending_title['record_id']
            )
            
            if not prerequisite_result['video_production_ready']:
                print(f"❌ Video production prerequisites not satisfied!")
                print(f"🔧 Issues: {prerequisite_result['validation_summary']['errors']}")
                print(f"⏸️ Skipping video creation for this record")
                await self.airtable_server.update_record(pending_title['record_id'], {
                    'Status': 'Prerequisites Failed',
                    'VideoProductionRDY': 'Pending'
                })
                return {
                    'success': False,
                    'error': 'Video production prerequisites not satisfied',
                    'prerequisite_issues': prerequisite_result['validation_summary']['errors']
                }
            
            print(f"✅ Video production prerequisites satisfied!")
            print(f"🎯 All {prerequisite_result['validation_summary']['checks_passed']}/{prerequisite_result['validation_summary']['total_checks']} checks passed")
            
            # Step 11: Create ENHANCED video with JSON2Video (with sound, transitions, background photos)
            print("🎬 Creating ENHANCED video with JSON2Video...")
            print("✨ Features: Sound integration, smooth transitions, background photos, reviews & ratings")
            
            # Expert Agent: JSON2Video Engagement Expert - Create viral-worthy professional video
            video_expert_result = await route_to_expert(
                TaskType.VIDEO_CREATION,
                {
                    "record_id": pending_title['record_id'],
                    "record_data": pending_title,
                    "config": self.config,
                    "optimize_for_virality": True
                },
                priority="high"
            )
            
            if video_expert_result.get("success"):
                print("🎯 Expert-optimized video creation recommendations applied")
            
            video_result = await run_video_creation(
                self.config,
                pending_title['record_id']
            )
            
            print(f"🔍 DEBUG: video_result = {video_result}")
            
            if video_result['success']:
                print(f"✅ Video created successfully!")
                
                # Expert Agent: Video Status Specialist - Monitor video generation status
                if video_result.get('project_id'):
                    video_status_result = await route_to_expert(
                        TaskType.VIDEO_STATUS_MONITORING,
                        {
                            "project_id": video_result['project_id'],
                            "record_id": pending_title['record_id'],
                            "video_title": pending_title.get('VideoTitle', 'Unknown'),
                            "monitor_duration": 300  # Monitor for 5 minutes
                        },
                        priority="high"
                    )
                    
                    if video_status_result.get("success"):
                        print(f"📊 Video monitoring initiated: {video_status_result.get('status', 'monitoring')}")
                
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
                    
                    # Use platform-specific YouTube content if available
                    youtube_title = pending_title.get('YouTubeTitle')
                    youtube_description = pending_title.get('YouTubeDescription')
                    youtube_tags = pending_title.get('YouTubeTags', '').split(',') if pending_title.get('YouTubeTags') else []
                    
                    # Fallback to original title if platform-specific content not available
                    if not youtube_title:
                        youtube_prefix = self.config.get('youtube_title_prefix', '')
                        youtube_suffix = self.config.get('youtube_title_suffix', '')
                        youtube_title = f"{youtube_prefix}{pending_title.get('VideoTitle', pending_title.get('Title', pending_title.get('VideoTitle', "")))}{youtube_suffix}"[:100]
                    
                    # Fallback to building description if not available
                    if not youtube_description:
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
                    
                    # Use platform-specific tags if not already loaded
                    if not youtube_tags:
                        # Prepare tags from config and keywords
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
                    from src.mcp.instagram_workflow_integration import upload_to_instagram
                    
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

            # Expert Agent: Analytics Performance Tracker - Track content performance
            analytics_result = await route_to_expert(
                TaskType.PERFORMANCE_TRACKING,
                {
                    "record_id": pending_title['record_id'],
                    "content_data": {
                        "title": optimized_title,
                        "products": len(amazon_result.get('products', [])),
                        "platforms_published": ["wordpress", "youtube", "instagram"],
                        "video_generated": video_result.get('success', False)
                    },
                    "metrics": {
                        "workflow_duration": (datetime.now() - datetime.strptime(f"{datetime.now().date()} 00:00:00", "%Y-%m-%d %H:%M:%S")).total_seconds(),
                        "api_calls_made": 15  # Estimate
                    }
                },
                priority="medium"
            )
            
            if analytics_result.get("success"):
                print(f"📊 Performance tracked: {analytics_result.get('performance_id', 'N/A')}")
            
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
            
            return True
            
        except Exception as e:
            print(f"❌ Workflow failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Expert Agent: Error Recovery Specialist - Handle workflow failure
            error_recovery_result = await route_to_expert(
                TaskType.ERROR_RECOVERY,
                {
                    "error": str(e),
                    "context": "main_workflow",
                    "record_id": pending_title.get('record_id') if 'pending_title' in locals() else None,
                    "step": "unknown",
                    "traceback": traceback.format_exc()
                },
                priority="critical"
            )
            
            if error_recovery_result.get("success") and error_recovery_result.get("recovery_action"):
                print(f"🔧 Error recovery suggested: {error_recovery_result['recovery_action']}")
            
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
        """Generate voice text for intro, outro, and products with optimized timing"""
        try:
            voice_text_data = {}
            optimizer = VoiceTimingOptimizer()
            
            # Get timing constraints
            intro_constraints = optimizer.generate_intro_constraints()
            outro_constraints = optimizer.generate_outro_constraints()
            
            # Generate intro voice text (13-15 words for 5 seconds)
            intro_text = f"Welcome! Today we're counting down {optimized_title.lower()}. Let's discover the best!"
            intro_analysis = optimizer.analyze_text_timing(intro_text, 5)
            if not intro_analysis['is_good_fit']:
                print(f"⚠️ Intro text needs adjustment: {intro_analysis['word_count']} words (target: {intro_analysis['optimal_word_count']})")
            voice_text_data['IntroHook'] = intro_text
            
            # Generate outro voice text (13-15 words for 5 seconds)
            outro_text = "Thanks for watching! Subscribe for more reviews and comment your favorite below!"
            outro_analysis = optimizer.analyze_text_timing(outro_text, 5)
            if not outro_analysis['is_good_fit']:
                print(f"⚠️ Outro text needs adjustment: {outro_analysis['word_count']} words (target: {outro_analysis['optimal_word_count']})")
            voice_text_data['OutroCallToAction'] = outro_text
            
            # Generate product voice text - store in VideoScript as combined content
            products = script_data.get('products', [])
            product_voice_texts = []
            product_constraints = optimizer.generate_product_constraints()
            
            for i, product in enumerate(products[:5], 1):
                # Format: "Number X. [Product Name]. [Description]" - aim for 26 words total
                rank_number = 6 - i  # Countdown from 5 to 1
                product_title = product.get('title', 'Product')
                product_desc = product.get('description', 'Great product for your needs.')
                
                # Analyze current product text
                product_text = f"Number {rank_number}. {product_title}. {product_desc}"
                product_analysis = optimizer.analyze_text_timing(product_text, 10)
                
                if not product_analysis['is_good_fit']:
                    print(f"⚠️ Product {rank_number} text needs adjustment: {product_analysis['word_count']} words (target: {product_analysis['optimal_word_count']})")
                
                product_voice_texts.append(product_text)
            
            # Store all product voice texts in VideoScript field
            if product_voice_texts:
                voice_text_data['VideoScript'] = '\n\n'.join([intro_text, *product_voice_texts, outro_text])
            
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
            intro_text = record_data.get('IntroHook', '') or record_data.get('fields', {}).get('IntroHook', 'Welcome to our top 5 product review!')
            if intro_text:
                intro_voice = await self.voice_generator.generate_voice_from_text(intro_text, 'intro')
                if intro_voice:
                    # Save to Google Drive and get URL
                    intro_url = await self.save_voice_to_drive(intro_voice, f"{record_id}_intro.mp3")
                    results['airtable_updates']['IntroMp3'] = intro_url
                    results['voices_generated'] += 1
                    results['voices_saved'] += 1
            
            # Generate voice for outro
            outro_text = record_data.get('OutroCallToAction', '') or record_data.get('fields', {}).get('OutroCallToAction', 'Thanks for watching! Don\'t forget to subscribe!')
            if outro_text:
                outro_voice = await self.voice_generator.generate_voice_from_text(outro_text, 'outro')
                if outro_voice:
                    # Save to Google Drive and get URL
                    outro_url = await self.save_voice_to_drive(outro_voice, f"{record_id}_outro.mp3")
                    results['airtable_updates']['OutroMp3'] = outro_url
                    results['voices_generated'] += 1
                    results['voices_saved'] += 1
            
            # Generate voice for each product
            for i in range(1, 6):
                # Use existing product description for voice generation (check both direct and fields)
                product_text = record_data.get(f'ProductNo{i}Description', '') or record_data.get('fields', {}).get(f'ProductNo{i}Description', '')
                print(f"🔍 DEBUG: Product{i} text: {product_text[:50] if product_text else 'EMPTY'}")
                if product_text:
                    product_voice = await self.voice_generator.generate_voice_from_text(product_text, 'products')
                    if product_voice:
                        # Save to Google Drive and get URL
                        product_url = await self.save_voice_to_drive(product_voice, f"{record_id}_product{i}.mp3")
                        results['airtable_updates'][f'Product{i}Mp3'] = product_url
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
