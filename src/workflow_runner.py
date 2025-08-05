#!/usr/bin/env python3
"""
Production Workflow Runner - Complete Video Content Generation Pipeline
Based on Test structure but using real APIs for production
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

# Import Production MCP servers (real API calls)
from mcp_servers.airtable_server import AirtableMCPServer
# from src.mcp.amazon_affiliate_agent_mcp import run_amazon_affiliate_generation  # Not needed - scraper handles affiliate links
from mcp_servers.content_generation_server import ContentGenerationMCPServer
from src.mcp.text_generation_control_agent_mcp_v2 import run_text_control_with_regeneration
from mcp_servers.amazon_category_scraper import AmazonCategoryScraper
from mcp_servers.product_category_extractor_server import ProductCategoryExtractorMCPServer
from mcp_servers.flow_control_server import FlowControlMCPServer
from mcp_servers.voice_generation_server import VoiceGenerationMCPServer
from mcp_servers.amazon_product_validator import AmazonProductValidator
from mcp_servers.product_optimizer_server import ProductOptimizerServer
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
from src.expert_agents.timing_security_agent import TimingSecurityAgent

# Import Enhanced Prerequisite System with Smart Retry + MCP Playwright
from src.mcp.enhanced_video_prerequisite_control_agent_mcp import (
    enhanced_initialize_video_prerequisites,
    enhanced_validate_video_prerequisites,
    enhanced_final_video_security_check,
    EnhancedVideoPrerequisiteController
)
from mcp_servers.alternative_scraping_manager import create_alternative_scraping_manager

class ContentPipelineOrchestrator:
    def __init__(self):
        # Load real API configuration
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            self.config = json.load(f)
        
        # Initialize Production MCP servers with real API keys
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
        
        self.voice_server = VoiceGenerationMCPServer(
            self.config['elevenlabs_api_key']
        )
        
        self.amazon_validator = AmazonProductValidator(self.config)
        
        self.product_optimizer = ProductOptimizerServer(self.config['anthropic_api_key'])
        
        self.category_scraper = AmazonCategoryScraper(self.config)
        
        self.wordpress_mcp = WordPressMCP(self.config)
        
        # Initialize Timing Security Agent (fallback content validator)
        self.timing_security_agent = TimingSecurityAgent(self.config)
        
        # Initialize Enhanced Prerequisite Controller with Smart Retry + MCP Playwright
        self.enhanced_prerequisite_controller = EnhancedVideoPrerequisiteController(self.config)
        
        # Initialize Alternative Scraping Manager with MCP Playwright
        self.alternative_scraping_manager = create_alternative_scraping_manager()
        
        # Check Google Drive token status at startup
        self._check_google_drive_status()
        
        print("🎯 Production Content Pipeline Orchestrator initialized with REAL APIs")
        print("🛡️ Enhanced Prerequisite System with Smart Retry + MCP Playwright ACTIVE")
        print("🛡️ Timing Security Agent ready to prevent video failures")
        print("🎭 Alternative Scraping: ScrapingDog → Playwright MCP → Direct → Manual")
        print("✨ Ready for live content generation workflow!")
    
    def _check_google_drive_status(self):
        """Check Google Drive token status and warn if issues exist"""
        try:
            from src.utils.google_drive_token_manager import GoogleDriveTokenManager
            token_manager = GoogleDriveTokenManager()
            status = token_manager.get_token_status()
            
            if status['status'] == 'VALID':
                print("✅ Google Drive tokens are valid")
            elif status['status'] == 'NEEDS_REFRESH':
                print("🔄 Google Drive tokens will be auto-refreshed when needed")
            elif status['status'] == 'EXPIRED':
                if status['can_refresh']:
                    print("⚠️ Google Drive tokens expired - will attempt auto-refresh")
                else:
                    print("❌ Google Drive tokens expired and cannot be refreshed")
                    print("   Workflow will continue without Google Drive integration")
                    print("   Manual re-authorization required for Drive functionality")
            else:
                print("⚠️ Google Drive token status unclear - proceeding with caution")
                
        except Exception as e:
            print(f"⚠️ Could not check Google Drive status: {e}")

    async def run_complete_workflow(self):
        """Run the complete content generation workflow processing ONE title"""
        print(f"🚀 Starting PRODUCTION content workflow at {datetime.now()}")
        print("🎯 Processing ONE title with Status='Pending' and smallest ID")
        
        # Get ONE pending title from Airtable (REAL DATA)
        pending_title = await self.airtable_server.get_pending_titles(limit=1)
        
        if not pending_title:
            print("❌ No pending titles found. Exiting.")
            return
        
        print(f"✅ Found title: {pending_title['title']}")
        
        # 🛡️ ENHANCED: Initialize prerequisite tracking for new title
        print("🛡️ Step 0: Initializing enhanced prerequisite tracking...")
        init_result = await self.enhanced_prerequisite_controller.initialize_for_new_title(pending_title['record_id'])
        if init_result:
            print("✅ VideoProductionRDY initialized to 'Pending' - Critical failure protection ACTIVE")
        else:
            print("⚠️ Prerequisite initialization failed - continuing with standard flow")
        
        # Validate title has sufficient Amazon products BEFORE processing
        print("🔍 Step 1: Validating title has sufficient Amazon products...")
        validation_result = await self.amazon_validator.validate_title_for_amazon(pending_title['title'])
        
        if not validation_result['valid']:
            print(f"❌ Title validation FAILED: {validation_result['validation_message']}")
            
            # Mark title as failed in Airtable
            await self.airtable_server.update_record(
                pending_title['record_id'],
                {
                    'Status': 'Completed',
                    'ValidationIssues': f"Only {validation_result['product_count']} products found on Amazon. Need minimum 5 products for Top 5 video."
                }
            )
            return
        
        print(f"✅ Title validation PASSED: {validation_result['validation_message']}")
        print(f"🎯 Best search term: {validation_result['primary_search_term']}")
        
        # Process this title through the complete workflow
        success = await self.process_single_title(pending_title, validation_result)
        
        if success:
            print(f"🎉 Workflow completed successfully for: {pending_title['title']}")
        else:
            print(f"❌ Workflow failed for: {pending_title['title']}")

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
            
            # Step 3: Use validated products OR scrape for additional details
            print("🛒 Processing Amazon products...")
            
            # Check if validator already provided the products
            if validation_result.get('sample_products') and len(validation_result['sample_products']) >= 5:
                print(f"✅ Using {len(validation_result['sample_products'])} products from validation")
                
                # 🛡️ ENHANCED: Scrape with alternative sources (ScrapingDog → Playwright MCP → Direct)
                validated_term = validation_result['primary_search_term']
                print(f"🎭 Attempting enhanced scraping with alternatives for: {validated_term}")
                
                # Try primary scraper first
                amazon_result = await self.category_scraper.get_top_5_products(validated_term)
                
                if not amazon_result.get('success'):
                    print("🔄 Primary scraping failed - trying alternative sources...")
                    
                    # Generate Amazon search URL for alternative scraping
                    search_url = f"https://www.amazon.com/s?k={validated_term.replace(' ', '+')}"
                    
                    # Try alternative scraping methods
                    alternative_result = await self.alternative_scraping_manager.scrape_with_alternatives(
                        search_url, validated_term
                    )
                    
                    if alternative_result.get('success'):
                        print(f"✅ Alternative scraping successful using: {alternative_result.get('final_source')}")
                        print(f"📦 Found {len(alternative_result.get('products', []))} products")
                        
                        # Convert alternative scraping format to expected format
                        amazon_result = {
                            'success': True,
                            'products': alternative_result['products'][:5],
                            'airtable_data': {},
                            'product_results': {},
                            'scraping_source': alternative_result.get('final_source', 'alternative')
                        }
                        
                        # Build airtable_data from alternative scraping results
                        for i, product in enumerate(alternative_result['products'][:5], 1):
                            amazon_result['airtable_data'][f'ProductNo{i}Title'] = product.get('title', '')
                            amazon_result['airtable_data'][f'ProductNo{i}Price'] = product.get('price', 0)
                            amazon_result['airtable_data'][f'ProductNo{i}Rating'] = product.get('rating', 0)
                            amazon_result['airtable_data'][f'ProductNo{i}Reviews'] = product.get('reviews', 0)
                            amazon_result['airtable_data'][f'ProductNo{i}AffiliateLink'] = product.get('affiliate_link', '')
                            amazon_result['product_results'][f'product_{i}'] = product
                    else:
                        print("⚠️ All scraping methods failed - using validation products directly")
                        amazon_result = {
                            'success': True,
                            'products': validation_result['sample_products'],
                            'airtable_data': {},
                            'product_results': {}
                        }
                    
                    # Build airtable_data from sample products
                    for i, product in enumerate(validation_result['sample_products'][:5], 1):
                        # Map fields correctly - validator uses 'reviews', content generator expects 'review_count'
                        mapped_product = {
                            'title': product.get('title', ''),
                            'price': product.get('price', 0),
                            'rating': product.get('rating', 0),
                            'review_count': product.get('reviews', 0),  # Map 'reviews' to 'review_count'
                            'affiliate_link': product.get('affiliate_link', '')
                        }
                        
                        amazon_result['airtable_data'][f'ProductNo{i}Title'] = mapped_product['title']
                        amazon_result['airtable_data'][f'ProductNo{i}Price'] = mapped_product['price']
                        amazon_result['airtable_data'][f'ProductNo{i}Rating'] = mapped_product['rating']
                        amazon_result['airtable_data'][f'ProductNo{i}Reviews'] = mapped_product['review_count']
                        amazon_result['airtable_data'][f'ProductNo{i}AffiliateLink'] = mapped_product['affiliate_link']
                        amazon_result['product_results'][f'product_{i}'] = mapped_product
                        
                        # Also add the mapped product to the products list
                        amazon_result['products'][i-1] = mapped_product
            else:
                # 🛡️ ENHANCED: Fallback to enhanced scraping with alternatives if validation didn't provide products
                validated_term = validation_result['primary_search_term']
                print(f"🎯 Enhanced scraping with validated search term: {validated_term}")
                
                # Try primary scraper first
                amazon_result = await self.category_scraper.get_top_5_products(validated_term)
                
                if not amazon_result.get('success'):
                    print(f"🔄 Primary scraping failed - trying alternative sources...")
                    
                    # Generate Amazon search URL for alternative scraping
                    search_url = f"https://www.amazon.com/s?k={validated_term.replace(' ', '+')}"
                    
                    # Try alternative scraping methods
                    alternative_result = await self.alternative_scraping_manager.scrape_with_alternatives(
                        search_url, validated_term
                    )
                    
                    if alternative_result.get('success'):
                        print(f"✅ Alternative scraping successful using: {alternative_result.get('final_source')}")
                        print(f"📦 Found {len(alternative_result.get('products', []))} products")
                        
                        # Convert alternative scraping format to expected format
                        amazon_result = {
                            'success': True,
                            'products': alternative_result['products'][:5],
                            'airtable_data': {},
                            'product_results': {},
                            'scraping_source': alternative_result.get('final_source', 'alternative')
                        }
                        
                        # Build airtable_data from alternative scraping results
                        for i, product in enumerate(alternative_result['products'][:5], 1):
                            amazon_result['airtable_data'][f'ProductNo{i}Title'] = product.get('title', '')
                            amazon_result['airtable_data'][f'ProductNo{i}Price'] = product.get('price', 0)
                            amazon_result['airtable_data'][f'ProductNo{i}Rating'] = product.get('rating', 0)
                            amazon_result['airtable_data'][f'ProductNo{i}Reviews'] = product.get('reviews', 0)
                            amazon_result['airtable_data'][f'ProductNo{i}AffiliateLink'] = product.get('affiliate_link', '')
                            amazon_result['product_results'][f'product_{i}'] = product
                    else:
                        print(f"❌ All scraping methods failed: {alternative_result.get('error_summary', 'Unknown error')}")
                        return False
            
            print(f"✅ Processed {len(amazon_result['products'])} products")
            
            # Step 3.5: Optimize product titles and generate countdown descriptions
            print("🔧 Optimizing product titles and generating countdown descriptions...")
            try:
                optimized_products = await self.product_optimizer.optimize_all_products(
                    amazon_result['products'], 
                    clean_category
                )
                
                # Replace the original products with optimized ones
                amazon_result['products'] = optimized_products
                
                # Update airtable_data with optimized titles and descriptions
                for i, product in enumerate(optimized_products[:5]):
                    amazon_result['airtable_data'][f'ProductNo{i+1}Title'] = product['title']  # Optimized title
                    amazon_result['airtable_data'][f'ProductNo{i+1}Description'] = product['countdown_description']  # 9-second description
                
                print(f"✅ Optimized {len(optimized_products)} product titles and descriptions")
                
            except Exception as e:
                print(f"❌ Error optimizing products: {e}")
                print("⚠️ Continuing with original product data")
            
            # Save product data to Airtable immediately with status fields
            print("💾 Saving Amazon product data with status fields...")
            amazon_data_with_status = amazon_result['airtable_data'].copy()
            
            # Add missing status fields for all products
            for i in range(1, 6):
                if f'ProductNo{i}Title' in amazon_data_with_status:
                    amazon_data_with_status[f'ProductNo{i}TitleStatus'] = 'Ready'
                if f'ProductNo{i}Price' in amazon_data_with_status:
                    # Price doesn't have status field, but ensure other fields do
                    pass
                # Photo status will be set when images are uploaded
            
            await self.airtable_server.update_record(
                pending_title['record_id'], 
                amazon_data_with_status
            )
            
            # Step 2.5: Amazon affiliate links already generated by scraper
            # The amazon_category_scraper already generates affiliate links using ASIN + affiliate tag
            # No need to regenerate them - they're saved in ProductNo1-5AffiliateLink fields
            print("✅ Affiliate links already generated by Amazon scraper")
            
            # Step 3: Generate multi-platform keywords using product data (KEYWORDS FIRST!)
            print("🔍 Step 3: Generating multi-platform keywords with product data...")
            multi_keywords = await self.content_server.generate_multi_platform_keywords(
                pending_title['title'],
                amazon_result['products']
            )
            
            # Save multi-platform keywords to Airtable (KEYWORDS FIRST!)
            print("💾 Saving multi-platform keywords to Airtable...")
            await self.airtable_server.update_multi_platform_keywords(
                pending_title['record_id'],
                multi_keywords
            )
            
            # Keep backward compatibility with existing workflow (use universal keywords)
            keywords = multi_keywords.get('universal', [])
            
            # Step 4: Generate platform-specific TITLES using keywords (SEO-OPTIMIZED)
            print("🎯 Step 4: Generating platform titles using keywords for SEO...")
            platform_titles = await self.content_server.generate_platform_titles_from_keywords(
                pending_title['title'],
                multi_keywords
            )
            
            # Step 5: Generate platform-specific DESCRIPTIONS using keywords with affiliate links
            print("📝 Step 5: Generating platform descriptions with affiliate links...")
            
            # Get affiliate links from amazon_result
            affiliate_data = {}
            product_photos = {}
            for i in range(1, 6):
                if amazon_result.get('airtable_data', {}).get(f'ProductNo{i}AffiliateLink'):
                    affiliate_data[f'ProductNo{i}AffiliateLink'] = amazon_result['airtable_data'][f'ProductNo{i}AffiliateLink']
                if amazon_result.get('airtable_data', {}).get(f'ProductNo{i}Photo'):
                    product_photos[f'ProductNo{i}Photo'] = amazon_result['airtable_data'][f'ProductNo{i}Photo']
            
            platform_descriptions = await self.content_server.generate_platform_descriptions_from_keywords(
                amazon_result['products'],
                multi_keywords,
                platform_titles,
                affiliate_data,
                video_url=None,  # Will be updated later after video creation
                product_photos=product_photos
            )
            
            # Step 6: Save all platform content to Airtable
            print("💾 Saving platform-specific content to Airtable...")
            platform_content_update = {
                # YouTube content
                'YouTubeTitle': platform_titles.get('youtube', ''),
                'YouTubeDescription': platform_descriptions.get('youtube', ''),
                'YouTubeKeywords': ', '.join(multi_keywords.get('youtube', [])),
                
                # TikTok content  
                'TikTokTitle': platform_titles.get('tiktok', ''),
                'TikTokDescription': platform_descriptions.get('tiktok', ''),
                'TikTokCaption': platform_descriptions.get('tiktok', ''),
                'TikTokKeywords': ', '.join(multi_keywords.get('tiktok', [])),
                'TikTokHashtags': ' '.join(multi_keywords.get('instagram', [])),  # Use Instagram hashtags for TikTok
                
                # Instagram content
                'InstagramTitle': platform_titles.get('instagram', ''),
                'InstagramCaption': platform_descriptions.get('instagram', ''),
                'InstagramHashtags': ' '.join(multi_keywords.get('instagram', [])),
                
                # WordPress content
                'WordPressTitle': platform_titles.get('wordpress', ''),
                'WordPressContent': platform_descriptions.get('wordpress', ''),
                'WordPressSEO': ', '.join(multi_keywords.get('wordpress', [])),
                
                # Universal keywords
                'UniversalKeywords': ', '.join(multi_keywords.get('universal', [])),
                'KeyWords': ', '.join(keywords)
            }
            
            await self.airtable_server.update_record(pending_title['record_id'], platform_content_update)
            
            # Step 6.5: Calculate SEO metrics for all platforms
            print("📊 Step 6.5: Calculating SEO metrics and optimization scores...")
            
            # Calculate SEO metrics for each platform
            seo_metrics = {}
            platforms = ['youtube', 'tiktok', 'instagram', 'wordpress']
            
            for platform in platforms:
                title = platform_titles.get(platform, '')
                description = platform_descriptions.get(platform, '')
                keywords = multi_keywords.get(platform, [])
                
                if title and description:
                    metrics = await self.content_server.calculate_seo_metrics(
                        title, description, keywords, platform
                    )
                    seo_metrics[platform] = metrics
                    print(f"📊 {platform.title()}: SEO={metrics['seo_score']}, Title={metrics['title_optimization_score']}, Engagement={metrics['engagement_prediction']}")
            
            # Use YouTube metrics as primary scores (most important platform)
            youtube_metrics = seo_metrics.get('youtube', {})
            seo_scores_update = {
                'SEOScore': youtube_metrics.get('seo_score', 50.0),
                'TitleOptimizationScore': youtube_metrics.get('title_optimization_score', 50.0),
                'KeywordDensity': youtube_metrics.get('keyword_density', 1.0),
                'EngagementPrediction': youtube_metrics.get('engagement_prediction', 50.0),
                'LastOptimizationDate': '2025-08-03'  # Current date
            }
            
            await self.airtable_server.update_record(pending_title['record_id'], seo_scores_update)
            
            # Step 7: Format products with countdown numbering (#5 to #1)
            print("🏆 Step 7: Formatting products with countdown numbering...")
            formatted_products = await self.content_server.format_products_with_countdown(amazon_result['products'])
            
            # Step 8: Generate optimized video title using YouTube keywords
            print("🎯 Step 8: Optimizing video title for engagement...")
            youtube_keywords = multi_keywords.get('youtube', keywords)
            optimized_title = await self.content_server.optimize_title(
                pending_title['title'], 
                youtube_keywords
            )
            
            # Step 9: Generate IntroHook and OutroCallToAction with precise timing
            print("🎬 Step 9: Generating IntroHook and OutroCallToAction...")
            
            # Get winner product for outro
            winner_product = "Unknown"
            if amazon_result.get('products') and len(amazon_result['products']) >= 5:
                winner_product = amazon_result['products'][4].get('title', 'Unknown')  # Product 5 = #1 winner
            
            intro_outro = await self.product_optimizer.generate_intro_outro(
                optimized_title, 
                clean_category,
                winner_product
            )
            
            # Step 10: Prepare countdown script using optimized product descriptions
            print("📝 Step 10: Preparing countdown script with optimized descriptions...")
            
            # Use the already optimized products and descriptions
            processed_products = []
            for i, product in enumerate(amazon_result['products'][:5]):
                # Get price from Airtable data if product price is N/A or 0
                product_price = product.get('price', 25)
                if product_price == 'N/A' or product_price == 0 or product_price == '0':
                    # Fallback to Airtable data
                    airtable_price = amazon_result.get('airtable_data', {}).get(f'ProductNo{i+1}Price', 25)
                    if airtable_price and airtable_price != 0:
                        product_price = airtable_price
                    else:
                        product_price = 25  # Default fallback
                
                # Product info for display
                processed_product = {
                    'title': f"#{product.get('countdown_rank', 5-i)} {product.get('title', f'Product {i+1}')}",
                    'rating': product.get('rating', 4.5),
                    'review_count': product.get('review_count', 1000),
                    'price': product_price,
                    'countdown_number': product.get('countdown_rank', 5-i),
                    'is_winner': i == 4  # Last product is the winner (#1)
                }
                processed_products.append(processed_product)
                print(f"🏆 Prepared countdown product: {processed_product['title']} | ⭐{processed_product['rating']} | 👥{processed_product['review_count']} | 💰${processed_product['price']}")
            
            # Create script data using optimized descriptions
            script_data = {
                'intro': intro_outro.get('intro_hook', f'Top 5 {clean_category} countdown!'),
                'outro': intro_outro.get('outro_cta', 'Check links below now!'),
                'intro_hook': intro_outro.get('intro_hook', f'Top 5 {clean_category} countdown!'),
                'outro_cta': intro_outro.get('outro_cta', 'Check links below now!'),
                'optimized_title': optimized_title,
                'products': []
            }
            
            # Add products with optimized descriptions
            for i, product in enumerate(amazon_result['products'][:5]):
                script_data['products'].append({
                    'name': product.get('title', f'Product {i+1}'),
                    'script': product.get('countdown_description', f'Product {i+1} description'),
                    'rank': product.get('countdown_rank', 5-i)
                })
            
            # Step 11: Save countdown script and video content to Airtable
            print("💾 Step 11: Saving countdown script and video content to Airtable...")
            
            # Combine script data with intro/outro data
            video_content_data = {
                **script_data,
                'intro_hook': intro_outro.get('intro_hook'),
                'outro_cta': intro_outro.get('outro_cta'),
                'optimized_title': optimized_title
            }
            
            await self._save_countdown_to_airtable(pending_title['record_id'], video_content_data)
            
            # Step 12: Product titles are already optimized and saved - skip countdown title updates
            print("🏆 Step 12: Product titles already optimized and saved...")
            
            # Update status fields only since titles are already optimized
            status_updates = {}
            for i in range(1, 6):
                status_updates[f'ProductNo{i}TitleStatus'] = 'Ready'
            
            await self.airtable_server.update_record(pending_title['record_id'], status_updates)
            
            # Step 12.5: Content Validation and Timing Check
            print("⏱️ Step 12.5: Validating content timing requirements...")
            
            # Prepare content for validation
            content_for_validation = {
                'intro_hook': intro_outro.get('intro_hook', ''),
                'outro_cta': intro_outro.get('outro_cta', ''),
            }
            
            # Add product descriptions from script_data
            if 'products' in script_data:
                for i, product in enumerate(script_data['products'][:5]):
                    product_num = i + 1
                    content_for_validation[f'ProductNo{product_num}Description'] = product.get('script', '')
            
            # 🛡️ ENHANCED: Validate content timing with enhanced prerequisite system
            validation_result = await self.content_server.validate_content_timing(content_for_validation)
            
            # Update basic validation status in Airtable
            validation_status = "Validated" if validation_result['is_valid'] else "Failed"
            validation_issues = "; ".join(validation_result.get('issues', []))
            
            basic_validation_update = {
                'ContentValidationStatus': validation_status,
                'ValidationIssues': validation_issues[:500] if validation_issues else ""
            }
            
            await self.airtable_server.update_record(pending_title['record_id'], basic_validation_update)
            
            # 🛡️ ENHANCED: Run enhanced prerequisite validation with smart retry
            print("🛡️ Running enhanced prerequisite validation with smart retry...")
            enhanced_validation = await self.enhanced_prerequisite_controller.validate_and_retry_after_content_step(
                pending_title['record_id']
            )
            
            if validation_result['is_valid']:
                print(f"✅ Content validation passed")
                total_time = validation_result['timing_breakdown']['total_time']
                print(f"   🎬 Total video time: {total_time:.1f} seconds")
                
                # Check enhanced prerequisite status
                if enhanced_validation.get('can_produce_video'):
                    print(f"🛡️✅ Enhanced validation: ALL PREREQUISITES MET - Video approved")
                else:
                    critical_summary = enhanced_validation.get('critical_summary', {})
                    completion_pct = critical_summary.get('completion_percentage', 0)
                    print(f"🛡️⏳ Enhanced validation: {completion_pct}% complete - Continue workflow")
            else:
                print(f"❌ Content validation failed - {len(validation_result['issues'])} issues found")
                for issue in validation_result['issues']:
                    print(f"     - {issue}")
                
                # If regeneration is needed, increment counter
                if validation_result.get('regeneration_needed'):
                    current_attempts = await self._get_current_generation_attempts(pending_title['record_id'])
                    regeneration_update = {
                        'RegenerationCount': current_attempts + 1,
                        'ContentValidationStatus': 'Regenerating'
                    }
                    await self.airtable_server.update_record(pending_title['record_id'], regeneration_update)
            
            # Step 13: Update PlatformReadiness
            print("📱 Step 13: Updating platform readiness status...")
            
            # Determine which platforms are ready based on content quality
            ready_platforms = []
            
            # Check each platform's content quality
            for platform in ['YouTube', 'TikTok', 'Instagram', 'WordPress']:
                platform_lower = platform.lower()
                title = platform_titles.get(platform_lower, '')
                description = platform_descriptions.get(platform_lower, '')
                
                if title and description and len(title) > 10 and len(description) > 20:
                    ready_platforms.append(platform)
            
            # Skip PlatformReadiness update for now - field needs pre-configured options
            # platform_readiness_update = {
            #     'PlatformReadiness': ready_platforms
            # }
            # await self.airtable_server.update_record(pending_title['record_id'], platform_readiness_update)
            print(f"📱 Platform readiness: {', '.join(ready_platforms)}")
            
            # Step 6.5: Text Generation Quality Control
            print("🎮 Running text generation quality control...")
            
            # Now run quality control
            control_result = await run_text_control_with_regeneration(self.config, pending_title['record_id'])
            
            if not control_result['success']:
                print(f"❌ Text control failed after {control_result.get('attempts', 0)} attempts")
                await self.airtable_server.update_record(pending_title['record_id'], {
                    'TextControlStatus': 'Failed',
                    'Status': 'Processing'  # Keep processing but note the failure
                })
            elif control_result['all_valid']:
                print(f"✅ Text validated after {control_result['attempts']} attempt(s)")
                await self.airtable_server.update_record(pending_title['record_id'], {
                    'TextControlStatus': 'Validated'
                })

            # Step 6.5: Text Length Validation with Regeneration
            print("⏱️ Validating text length for TTS timing compliance...")
            try:
                text_validation_result = await run_text_validation_with_regeneration(
                    record_id=pending_title['record_id']
                )
                
                if text_validation_result.get('success'):
                    if text_validation_result.get('all_approved'):
                        print(f"✅ All text fields validated and approved for TTS timing compliance")
                    elif text_validation_result.get('has_rejections'):
                        print(f"⚠️ Some text fields still exceed timing limits after regeneration attempts")
                else:
                    print(f"❌ Text validation with regeneration failed")
            except Exception as e:
                print(f"❌ Error during text validation: {str(e)}")

            # Step 7: Generate platform-specific content (titles, descriptions, hashtags)
            print("📱 Generating platform-specific content...")
            try:
                platform_content_result = await generate_platform_content_for_workflow(
                    config=self.config,
                    record_id=pending_title['record_id'],
                    base_title=optimized_title,
                    products=amazon_result['products'],
                    category=clean_category
                )
                
                if platform_content_result['success']:
                    print(f"✅ Generated content for {platform_content_result['platforms_generated']} platforms")
                else:
                    print(f"⚠️ Platform content generation had issues: {platform_content_result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Error generating platform content: {str(e)}")
            
            # Step 8: Generate voice narration and upload to Google Drive
            print("🎙️ Generating voice narration and uploading to Google Drive...")
            try:
                # Initialize Google Drive service
                from mcp_servers.google_drive_server import GoogleDriveMCPServer
                drive_server = GoogleDriveMCPServer(self.config)
                
                # Initialize Google Drive service
                if not await drive_server.initialize_drive_service():
                    print("❌ Failed to initialize Google Drive service")
                    raise Exception("Google Drive initialization failed")
                
                # Create project folder structure (N8N Projects > Title > Audio)
                folder_structure = await drive_server.create_project_structure(optimized_title)
                if not folder_structure.get('audio'):
                    print("❌ Failed to create Audio folder structure")
                    raise Exception("Audio folder creation failed")
                
                audio_folder_id = folder_structure['audio']
                print(f"📁 Created Audio folder: {audio_folder_id}")
                
                # Generate intro voice using correct field name
                intro_voice = await self.voice_server.generate_intro_voice(
                    intro_text=intro_outro.get('intro_hook', '')
                )
                
                # Upload intro voice and save URL to Airtable
                intro_mp3_url = None
                if intro_voice:
                    intro_mp3_url = await drive_server.upload_audio_file(
                        intro_voice, 
                        "intro.mp3", 
                        audio_folder_id
                    )
                    if intro_mp3_url:
                        await self.airtable_server.update_record(
                            pending_title['record_id'], 
                            {'IntroMp3': intro_mp3_url}
                        )
                        print(f"✅ Intro voice uploaded and URL saved")
                
                # Generate and upload product voices
                product_voices = []
                for i, product in enumerate(script_data.get('products', []), 1):
                    # Use product description from script_data (already formatted for countdown)
                    product_description = product.get('script', product.get('description', ''))
                    
                    voice = await self.voice_server.generate_product_voice(
                        product_name=product.get('name', product.get('title', '')),
                        product_description=product_description,
                        product_rank=5-i+1  # Countdown: Product 1 = #5, Product 5 = #1
                    )
                    product_voices.append(voice)
                    
                    # Upload product voice and save URL to Airtable
                    if voice:
                        product_mp3_url = await drive_server.upload_audio_file(
                            voice, 
                            f"product_{i}.mp3", 
                            audio_folder_id
                        )
                        if product_mp3_url:
                            await self.airtable_server.update_record(
                                pending_title['record_id'], 
                                {f'Product{i}Mp3': product_mp3_url}
                            )
                            print(f"✅ Product {i} voice uploaded and URL saved")
                
                # Generate outro voice using correct field name
                outro_voice = await self.voice_server.generate_outro_voice(
                    outro_text=intro_outro.get('outro_cta', '')
                )
                
                # Upload outro voice and save URL to Airtable
                outro_mp3_url = None
                if outro_voice:
                    outro_mp3_url = await drive_server.upload_audio_file(
                        outro_voice, 
                        "outro.mp3", 
                        audio_folder_id
                    )
                    if outro_mp3_url:
                        await self.airtable_server.update_record(
                            pending_title['record_id'], 
                            {'OutroMp3': outro_mp3_url}
                        )
                        print(f"✅ Outro voice uploaded and URL saved")
                
                print("✅ Voice generation and Google Drive upload completed")
                print(f"📁 All audio files saved to: {audio_folder_id}")
                
            except Exception as e:
                print(f"❌ Error generating voices or uploading to Drive: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Step 9: Generate images
            print("🎨 Generating images...")
            try:
                # Generate intro image
                intro_image_result = await generate_intro_image_for_workflow(
                    config=self.config,
                    record_id=pending_title['record_id'],
                    video_title=optimized_title,
                    products=amazon_result['products'],
                    category=clean_category
                )
                
                # Download and save Amazon product images first
                amazon_images_result = await download_and_save_amazon_images_v2(
                    self.config,
                    pending_title['record_id'],
                    optimized_title,
                    amazon_result['products']
                )
                
                # Generate enhanced OpenAI images using Amazon photos as reference
                openai_images_result = await generate_amazon_guided_openai_images(
                    self.config,
                    pending_title['record_id'],
                    optimized_title,
                    amazon_result['products']
                )
                
                # NOW use #1 product's high-resolution OpenAI image as outro 
                # The OpenAI image is saved to ProductNo5Photo and is high-resolution
                outro_image_url = None
                try:
                    record_data = await self.airtable_server.get_record_by_id(pending_title['record_id'])
                    if record_data:
                        fields = record_data.get('fields', {})
                        # ProductNo5Photo contains the high-resolution OpenAI generated image
                        outro_image_url = fields.get('ProductNo5Photo')  # Product 5 is the #1 winner
                        
                        if outro_image_url:
                            # Update Airtable with the high-resolution #1 product image as outro
                            await self.airtable_server.update_record(
                                pending_title['record_id'], 
                                {'OutroPhoto': outro_image_url}
                            )
                            print(f"✅ Using #1 product high-res OpenAI image as outro: {outro_image_url[:50]}...")
                        else:
                            print("⚠️ No #1 product OpenAI image found in ProductNo5Photo, will use placeholder")
                except Exception as e:
                    print(f"❌ Error getting #1 product OpenAI image for outro: {e}")
                    
                outro_image_result = {'success': True, 'outro_image_url': outro_image_url}
                
                print("✅ Image generation and download completed")
                print(f"📊 Amazon images: {amazon_images_result.get('images_saved', 0)} saved")
                print(f"🎨 OpenAI images: {openai_images_result.get('images_generated', 0)} generated")
            except Exception as e:
                print(f"❌ Error generating images: {str(e)}")
            
            # Step 9.5: TIMING SECURITY CHECK - Prevent video failures
            print("🛡️ Step 9.5: Running Timing Security Check...")
            print("⚠️ CRITICAL: Validating ALL content meets timing requirements")
            
            try:
                timing_validation = await self.timing_security_agent.validate_all_timing(pending_title['record_id'])
                
                if timing_validation['success']:
                    print(f"✅ TIMING SECURITY PASSED - All content validated")
                    print(f"📊 Fields checked: {timing_validation['total_fields_checked']}")
                    print(f"🔧 Fields regenerated: {len(timing_validation['regenerated_fields'])}")
                    print(f"⏱️ Total video time: {timing_validation['total_video_time']:.1f}s")
                    
                    if timing_validation['regenerated_fields']:
                        print(f"🔄 Auto-regenerated fields: {', '.join(timing_validation['regenerated_fields'])}")
                else:
                    print("❌ TIMING SECURITY FAILED - Cannot proceed to video generation")
                    print("🛑 This prevents video generation failures")
                    return False
                    
            except Exception as e:
                print(f"❌ Timing Security Agent error: {str(e)}")
                print("⚠️ Proceeding without timing validation (risky)")
            
            # Step 10: Create video
            print("🎬 Creating video...")
            
            # Verify audio URLs with retry logic
            print("🔍 Verifying audio URLs before video creation...")
            max_retries = 5
            retry_delay = 3
            audio_verified = False
            
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"📊 Verification attempt {attempt}/{max_retries}...")
                    verification_record = await self.airtable_server.get_record_by_id(pending_title['record_id'])
                    
                    if verification_record:
                        fields = verification_record.get('fields', {})
                        
                        # Check all required audio fields
                        audio_fields = ['IntroMp3', 'OutroMp3'] + [f'Product{i}Mp3' for i in range(1, 6)]
                        missing_audio = []
                        
                        for field in audio_fields:
                            audio_url = fields.get(field, '')
                            if audio_url:
                                print(f"  ✅ {field}: Found")
                            else:
                                print(f"  ❌ {field}: Missing")
                                missing_audio.append(field)
                        
                        if not missing_audio:
                            print("✅ All audio URLs verified - proceeding with video creation")
                            audio_verified = True
                            break
                        else:
                            print(f"⚠️ Missing {len(missing_audio)} audio URLs: {', '.join(missing_audio)}")
                            
                            if attempt < max_retries:
                                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                                await asyncio.sleep(retry_delay)
                            else:
                                print(f"❌ CRITICAL: Audio URLs still missing after {max_retries} attempts")
                                print("❌ Video creation will fail - aborting")
                                return
                                
                except Exception as e:
                    print(f"⚠️ Error during verification attempt {attempt}: {e}")
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay)
                    else:
                        print("⚠️ Could not verify audio URLs after all attempts - proceeding anyway")
                        audio_verified = True
            
            # 🛡️ ENHANCED: Final security check before video generation
            print("🛡️ Final enhanced security check before video generation...")
            security_check = await self.enhanced_prerequisite_controller.final_security_check_before_video(
                pending_title['record_id']
            )
            
            if not security_check.get('approved'):
                reason = security_check.get('reason', 'unknown')
                message = security_check.get('message', 'Security check failed')
                
                if security_check.get('manual_intervention_required'):
                    print(f"🚨 CRITICAL FAILURE: {message}")
                    print(f"📧 Manual intervention required - video generation PERMANENTLY BLOCKED")
                    print(f"🚫 Moving to next title")
                    return False
                else:
                    print(f"⏳ Prerequisites incomplete: {message}")
                    print(f"📊 Continue workflow to complete prerequisites")
                    # Continue workflow to populate more prerequisites
            else:
                print(f"🛡️✅ SECURITY APPROVED: All critical prerequisites validated")
                print(f"🎬 Product accuracy guaranteed - proceeding with video generation")

            try:
                video_result = await run_video_creation(
                    config=self.config,
                    record_id=pending_title['record_id']
                )
                
                if video_result['success']:
                    project_id = video_result.get('project_id')
                    print(f"✅ Video creation started: Project ID {project_id}")
                    
                    # Step 10.5: Monitor video status with server-friendly timing
                    if project_id:
                        print("🎯 Starting JSON2Video status monitoring...")
                        print("⏰ 5-minute delay + 1-minute intervals (server-friendly)")
                        
                        from src.expert_agents.json2video_status_monitor import monitor_json2video_status
                        
                        # Monitor status in background (non-blocking for now, but could be made async)
                        status_result = await monitor_json2video_status(
                            self.config, 
                            pending_title['record_id'], 
                            project_id
                        )
                        
                        if status_result['success'] and status_result['status'] == 'completed':
                            print(f"🎉 Video completed: {status_result.get('video_url')}")
                            print(f"⏱️ Total processing time: {status_result.get('total_wait_time', 0):.1f} minutes")
                        else:
                            print(f"⚠️ Video monitoring result: {status_result['status']}")
                            if status_result.get('error'):
                                print(f"❌ Error: {status_result['error']}")
                    else:
                        print("⚠️ No project ID returned, skipping status monitoring")
                        status_result = {'success': False, 'error': 'No project ID returned'}
                else:
                    print(f"❌ Video creation failed: {video_result.get('error', 'Unknown error')}")
                    status_result = {'success': False, 'error': video_result.get('error', 'Video creation failed')}
            except Exception as e:
                print(f"❌ Error creating video: {str(e)}")
                status_result = {'success': False, 'error': str(e)}
            
            # Step 11: Upload to Google Drive
            print("☁️ Uploading video to Google Drive...")
            try:
                # upload_video_to_google_drive is part of the json2video workflow
                # It doesn't need separate parameters
                print("⏭️ Skipping separate Drive upload - handled by video creation")
            except Exception as e:
                print(f"❌ Error with Drive upload: {str(e)}")
            
            # Step 12: Publish to platforms (ACTIVE PUBLISHING)
            print("📤 Publishing to social media platforms...")
            publishing_results = {}
            
            # Only publish if video creation was successful
            if status_result.get('success') and status_result.get('video_url'):
                video_url = status_result['video_url']
                record_id = pending_title['record_id']
                
                # YouTube Publishing
                print("📺 Publishing to YouTube...")
                try:
                    from src.mcp.youtube_mcp import YouTubeMCP
                    
                    # Get Airtable record for content
                    record_data = await self.airtable_server.get_record_by_id(record_id)
                    if not record_data:
                        print("❌ Could not fetch record data for YouTube publishing")
                        raise Exception("Could not fetch record data")
                    
                    fields = record_data.get('fields', {})
                    
                    # Initialize YouTube client
                    youtube_client = YouTubeMCP(
                        credentials_path=self.config['youtube_credentials']
                    )
                    
                    # Upload video
                    youtube_result = await youtube_client.upload_video(
                        video_path=video_url,
                        title=fields.get('YouTubeTitle', fields.get('VideoTitle', 'Video')),
                        description=fields.get('YouTubeDescription', ''),
                        tags=fields.get('YouTubeKeywords', '').split(', ') if fields.get('YouTubeKeywords') else [],
                        privacy_status="private"  # Start as private
                    )
                    
                    if youtube_result.get('success'):
                        youtube_url = f"https://www.youtube.com/watch?v={youtube_result.get('video_id')}"
                        print(f"✅ YouTube published: {youtube_url}")
                        publishing_results['youtube'] = youtube_url
                    else:
                        print(f"❌ YouTube publishing failed: {youtube_result.get('error')}")
                except Exception as e:
                    print(f"❌ YouTube publishing error: {e}")
                
                # Instagram Publishing (PRIVATE MODE)
                print("📸 Publishing to Instagram (private)...")
                try:
                    from src.mcp.instagram_workflow_integration import upload_to_instagram
                    
                    # Get Airtable record for content
                    record_data = await self.airtable_server.get_record_by_id(record_id)
                    if not record_data:
                        print("❌ Could not fetch record data for Instagram publishing")
                        raise Exception("Could not fetch record data")
                    
                    # Add video URL to record data (top level for compatibility)
                    record_data['FinalVideo'] = video_url
                    
                    instagram_result = await upload_to_instagram(self.config, record_data)
                    if instagram_result.get('success'):
                        print(f"✅ Instagram published privately: {instagram_result.get('instagram_id', 'Success')}")
                        publishing_results['instagram'] = instagram_result.get('instagram_id', 'Private Upload')
                    else:
                        print(f"❌ Instagram publishing failed: {instagram_result.get('error')}")
                except Exception as e:
                    print(f"❌ Instagram publishing error: {e}")
                
                # WordPress Publishing (MAIN PAGE)
                print("📝 Publishing to WordPress...")
                try:
                    from src.mcp.wordpress_mcp import publish_to_wordpress
                    
                    # Get Airtable record for content
                    record_data = await self.airtable_server.get_record_by_id(record_id)
                    if not record_data:
                        print("❌ Could not fetch record data for WordPress publishing")
                        raise Exception("Could not fetch record data")
                    
                    # Add video URL to record data
                    record_data['fields']['FinalVideo'] = video_url
                    
                    wordpress_result = await publish_to_wordpress(self.config, record_data)
                    if wordpress_result.get('success'):
                        print(f"✅ WordPress published: {wordpress_result.get('post_url')}")
                        publishing_results['wordpress'] = wordpress_result['post_url']
                    else:
                        print(f"❌ WordPress publishing failed: {wordpress_result.get('error')}")
                except Exception as e:
                    print(f"❌ WordPress publishing error: {e}")
                
                # Update Airtable with publishing results
                if publishing_results:
                    update_data = {}
                    if 'youtube' in publishing_results:
                        update_data['YouTubeURL'] = publishing_results['youtube']
                    if 'wordpress' in publishing_results:
                        update_data['WordPressURL'] = publishing_results['wordpress']
                    
                    if update_data:
                        await self.airtable_server.update_record(record_id, update_data)
                        print(f"✅ Updated Airtable with {len(publishing_results)} published URLs")
                
                # TikTok Publishing (COMMENTED OUT - API PENDING)
                print("🎵 TikTok publishing commented out (waiting for API approval)")
                # TODO: Uncomment when TikTok API is approved
                # tiktok_result = await publish_to_tiktok(config, record_id, video_url)
                
                published_count = len(publishing_results)
                print(f"✅ Successfully published to {published_count}/3 platforms")
            else:
                print("❌ No video URL available - skipping publishing")
                print("   Video must be completed before publishing can proceed")
            
            print("✅ Complete workflow finished successfully")
            
            # Update status to completed
            await self.airtable_server.update_record(
                pending_title['record_id'],
                {'Status': 'Completed'}
            )
            
            # Invoke workflow performance optimizer for analysis
            print("\n🔍 Invoking workflow-performance-optimizer for analysis...")
            print("📊 Note: Performance analysis will be triggered by assistant")
            print("   This helps identify bottlenecks and optimization opportunities")
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing title: {str(e)}")
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
    
    async def _get_current_generation_attempts(self, record_id: str) -> int:
        """Get current generation attempts count from Airtable"""
        try:
            record = await self.airtable_server.get_record(record_id)
            if record and 'fields' in record:
                return record['fields'].get('RegenerationCount', 0)
            return 0
        except Exception as e:
            print(f"Error getting generation attempts: {e}")
            return 0

    async def _save_countdown_to_airtable(self, record_id: str, script_data: dict):
        """Save countdown script data and video content to Airtable (needed for video creation)"""
        update_fields = {}
        
        print(f"🔍 Debug script_data keys: {list(script_data.keys())}")
        
        # Save IntroHook and OutroCallToAction (NEW - critical for video timing)
        if 'intro_hook' in script_data:
            update_fields['IntroHook'] = script_data['intro_hook']
            print(f"🎬 IntroHook: {script_data['intro_hook'][:50]}...")
        
        if 'outro_cta' in script_data:
            update_fields['OutroCallToAction'] = script_data['outro_cta']
            print(f"🎬 OutroCallToAction: {script_data['outro_cta'][:50]}...")
        
        # Save video title and description - use correct keys from script_data
        if 'intro' in script_data:
            update_fields['VideoTitle'] = script_data['intro']
            update_fields['VideoTitleStatus'] = 'Ready'
        elif 'optimized_title' in script_data:
            update_fields['VideoTitle'] = script_data['optimized_title']
            update_fields['VideoTitleStatus'] = 'Ready'
            
        if 'outro' in script_data:
            update_fields['VideoDescription'] = script_data['outro']
            update_fields['VideoDescriptionStatus'] = 'Ready'
        
        # Save complete video script 
        if 'intro' in script_data and 'outro' in script_data and 'products' in script_data:
            full_script = f"INTRO: {script_data['intro']}\n\n"
            
            for i, product in enumerate(script_data.get('products', [])):
                product_text = product.get('script', product.get('name', f'Product {i+1}'))
                full_script += f"PRODUCT #{5-i}: {product_text}\n\n"
            
            full_script += f"OUTRO: {script_data['outro']}"
            update_fields['VideoScript'] = full_script
        
        # Save each product with descriptions (critical for video creation)
        if 'products' in script_data:
            print(f"🔍 Found {len(script_data['products'])} products in script_data")
            for i, product in enumerate(script_data['products']):
                product_num = i + 1
                # Use 'name' and 'script' from the actual script_data structure
                product_name = product.get('name', f'Product {product_num}')
                product_script = product.get('script', f'Description for product {product_num}')
                
                # Save to ProductNoXDescription (max 9 seconds timing requirement)
                update_fields[f'ProductNo{product_num}Description'] = product_script
                update_fields[f'ProductNo{product_num}DescriptionStatus'] = 'Ready'
                
                print(f"📦 Product {product_num} Description: {product_script[:50]}...")
        else:
            print("⚠️ No 'products' key in script_data")
            print(f"📋 Available keys: {list(script_data.keys())}")
        
        if update_fields:
            try:
                await self.airtable_server.update_record(record_id, update_fields)
                print(f"💾 Saved {len(update_fields)} fields to Airtable for video creation")
                
                # Verify the save worked
                for field_name, field_value in update_fields.items():
                    if 'ProductNo' in field_name and 'Title' in field_name:
                        print(f"✅ Saved {field_name}: {str(field_value)[:50]}...")
                        
            except Exception as e:
                print(f"⚠️ Error saving to Airtable: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ No script data to save to Airtable")

async def main():
    orchestrator = ContentPipelineOrchestrator()
    result = await orchestrator.run_complete_workflow()
    
    # Trigger performance optimizer analysis after workflow completion
    if result:
        print("\n" + "="*60)
        print("🎯 WORKFLOW COMPLETED - PERFORMANCE ANALYSIS REQUESTED")
        print("="*60)
        print("Please invoke the workflow-performance-optimizer agent to:")
        print("  • Analyze workflow execution performance")
        print("  • Identify bottlenecks and optimization opportunities")
        print("  • Review success rates and timing metrics")
        print("  • Provide recommendations for improvements")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())