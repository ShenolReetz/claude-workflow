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

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

# Import Production MCP servers
from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer
from mcp_servers.Production_content_generation_server import ProductionContentGenerationMCPServer
from mcp_servers.Production_progressive_amazon_scraper import ProductionProgressiveAmazonScraper
from mcp_servers.Production_voice_generation_server import ProductionVoiceGenerationMCPServer
from mcp_servers.Production_product_category_extractor_server import ProductionProductCategoryExtractorMCPServer
from mcp_servers.Production_flow_control_server import ProductionFlowControlMCPServer
from mcp_servers.Production_amazon_product_validator import ProductionAmazonProductValidator

# Import Production MCP agents
from src.mcp.Production_amazon_affiliate_agent_mcp import production_run_amazon_affiliate_generation
from src.mcp.Production_text_generation_control_agent_mcp_v2 import production_run_text_control_with_regeneration
from src.mcp.Production_json2video_agent_mcp import production_run_video_creation
from src.mcp.Production_enhanced_google_drive_agent_mcp import production_upload_all_assets_to_google_drive
from src.mcp.Production_wordpress_mcp import ProductionWordPressMCP
from src.mcp.Production_youtube_mcp import ProductionYouTubeMCP
from src.mcp.Production_voice_timing_optimizer import ProductionVoiceTimingOptimizer
from src.mcp.Production_intro_image_generator import production_generate_intro_image_for_workflow
from src.mcp.Production_outro_image_generator import production_generate_outro_image_for_workflow
from src.mcp.Production_platform_content_generator import production_generate_platform_content_for_workflow
from src.mcp.Production_text_length_validation_with_regeneration_agent_mcp import production_run_text_validation_with_regeneration
from src.mcp.Production_amazon_images_workflow_v2 import production_generate_enhanced_product_images

# Use OpenAI Python client for DALL-E image generation
import openai

class ProductionContentPipelineOrchestratorV2:
    def __init__(self):
        # Load real API keys from configuration
        config_path = '/home/claude-workflow/config/api_keys.json'
        with open(config_path, 'r') as f:
            self.config: Dict[str, any] = json.load(f)
        
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
        
        print("🚀 PRODUCTION Content Pipeline Orchestrator V2 initialized successfully!")
        print("📋 Enhanced with scraping variants and progressive testing")

    async def run_complete_workflow(self):
        """Run the complete production workflow with enhanced scraping variants"""
        print("\n🚀 Starting PRODUCTION WORKFLOW V2 (Enhanced Scraping)")
        print("=" * 60)
        
        try:
            # Step 1: Get pending title from Airtable (REAL API)
            print("\n📋 Step 1: Fetching pending title from Airtable...")
            pending_title = await self.airtable_server.get_pending_title()
            if not pending_title:
                print("❌ No pending titles found in Airtable")
                return
            
            title = pending_title.get('Title', '')
            record_id = pending_title.get('record_id', '')
            print(f"✅ Retrieved title: {title}")
            
            # Update status to Processing
            await self.airtable_server.update_record_field(record_id, 'Status', 'Processing')
            
            # Step 2: Generate scraping variants and test progressively
            print(f"\n🔍 Step 2: Progressive Amazon scraping with variants...")
            print(f"📋 Original title: {title}")
            
            amazon_products, successful_variant = await self.progressive_scraper.search_with_variants(
                title=title,
                target_products=5,
                min_reviews=10
            )
            
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
            
            # Step 3: Extract product category
            print("\n🏷️ Step 3: Extracting product category...")
            category_info = await self.category_extractor.extract_category(title)
            category = category_info.get('category', 'General')
            print(f"✅ Category extracted: {category}")
            
            # Step 4: Validate Amazon products
            print("\n🔍 Step 4: Validating scraped products...")
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
            
            # Step 5: FIRST - Save products to Airtable (names, prices, ratings, reviews, affiliate links, photos)
            print("\n💾 Step 5: Saving Amazon product data to Airtable...")
            
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
            
            image_result = await production_generate_enhanced_product_images(updated_record, self.config)
            
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
            
            # Step 6: THEN - Generate content based on scraped products
            print("\n📝 Step 6: Generating content based on saved products...")
            
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
            
            # Step 7: Continue with rest of workflow (voice, images, video, publishing)
            print("\n🎙️ Step 7: Generating voice narration...")
            # Ensure we have proper record structure
            if not isinstance(updated_record, dict) or 'fields' not in updated_record:
                updated_record = {'record_id': record_id, 'fields': updated_record if isinstance(updated_record, dict) else {}}
            voice_result = await self.voice_server.generate_voice_for_record(updated_record)
            print("✅ Voice narration generated")
            
            # Step 8: Generate images
            print("\n🖼️ Step 8: Generating intro/outro images...")
            intro_result = await production_generate_intro_image_for_workflow(
                voice_result['updated_record'], self.config
            )
            
            outro_result = await production_generate_outro_image_for_workflow(
                intro_result['updated_record'], self.config
            )
            
            print("✅ Images generated")
            
            # Step 9: Content validation
            print("\n✅ Step 9: Content validation...")
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
            
            # Step 10: Video creation
            print("\n🎬 Step 10: Creating video...")
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
            
            # Step 11: Enhanced Google Drive upload (ALL assets)
            print("\n☁️ Step 11: Uploading ALL assets to Google Drive...")
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
            
            # Step 12: Platform publishing
            print("\n📤 Step 12: Publishing to platforms...")
            
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
            
            # Step 13: Final completion
            print("\n🏁 Step 13: Workflow completion...")
            await self.airtable_server.update_record_field(record_id, 'Status', 'Completed')
            await self.airtable_server.update_record_field(
                record_id, 'LastOptimizationDate', datetime.now().isoformat()
            )
            
            print("🎉 PRODUCTION WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ WORKFLOW ERROR: {e}")
            if 'record_id' in locals():
                await self.airtable_server.update_record_field(
                    record_id, 'Status', f'Failed - {str(e)[:50]}'
                )
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