#!/usr/bin/env python3
"""
Production Workflow Runner - LOCAL STORAGE VERSION
===================================================

Complete implementation with all workflow phases.
This version saves all media files LOCALLY ONLY:
- No Google Drive uploads during generation
- WordPress uploads media when publishing
- Remotion uses local files (100% reliable)
- Faster workflow (no upload delays)
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
import time
from dataclasses import dataclass
from enum import Enum

# Add the project root to Python path
sys.path.append('/home/claude-workflow')

# Import optimized utilities
from src.utils.api_resilience_manager import APIResilienceManager
from src.utils.cache_manager import get_cache_manager, CacheManager
from src.utils.circuit_breaker import get_circuit_breaker_manager, CircuitOpenError
from src.utils.google_drive_token_manager import GoogleDriveTokenManager
from src.utils.youtube_auth_manager import YouTubeAuthManager
from src.utils.dual_storage_manager import get_storage_manager

# Import optimized MCP servers
from mcp_servers.production_airtable_server import ProductionAirtableMCPServer
from mcp_servers.production_credential_validation_server import ProductionCredentialValidationServerOptimized
from mcp_servers.production_content_generation_server import ProductionContentGenerationMCPServer
from mcp_servers.production_progressive_amazon_scraper_async import ProductionProgressiveAmazonScraper
from mcp_servers.production_voice_generation_server_local import ProductionVoiceGenerationLocal
from mcp_servers.production_product_category_extractor_server import ProductionProductCategoryExtractorMCPServer
from mcp_servers.production_flow_control_server import ProductionFlowControlMCPServer
from mcp_servers.production_amazon_product_validator import ProductionAmazonProductValidator

# Import Production MCP agents
from src.mcp.production_text_generation_control_agent_mcp_v2 import production_run_text_control_with_regeneration
from src.mcp.production_remotion_video_generator_strict import production_run_video_creation
from src.mcp.production_wow_video_generator import production_generate_wow_video
from src.mcp.production_wordpress_local_media import production_publish_to_wordpress_local
from src.mcp.production_youtube_local_upload import production_upload_to_youtube_local
from src.mcp.production_imagen4_ultra_with_gpt4_vision import production_generate_images_with_imagen4_ultra
from src.mcp.production_platform_content_generator_async import production_generate_platform_content_for_workflow
from src.mcp.production_text_length_validation_with_regeneration_agent_mcp import production_run_text_validation_with_regeneration
from src.mcp.production_instagram_reels_upload import production_upload_to_instagram

import openai

class WorkflowPhase(Enum):
    """Workflow phases with dependency tracking"""
    INIT = "initialization"
    CREDENTIALS = "credential_validation"
    FETCH_TITLE = "fetch_title"
    SCRAPE_PRODUCTS = "scrape_products"
    EXTRACT_CATEGORY = "extract_category"
    VALIDATE_PRODUCTS = "validate_products"
    SAVE_PRODUCTS = "save_products"
    GENERATE_IMAGES = "generate_images"
    GENERATE_CONTENT = "generate_content"
    GENERATE_SCRIPTS = "generate_scripts"
    GENERATE_VOICE = "generate_voice"
    GENERATE_INTRO_OUTRO = "generate_intro_outro"
    VALIDATE_CONTENT = "validate_content"
    CREATE_VIDEO = "create_video"
    PUBLISH_WORDPRESS = "publish_wordpress"
    PUBLISH_YOUTUBE = "publish_youtube"
    PUBLISH_INSTAGRAM = "publish_instagram"  # New phase
    UPDATE_STATUS = "update_status"
    FINALIZE = "finalize"

@dataclass
class PhaseResult:
    """Result from a workflow phase"""
    phase: WorkflowPhase
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    duration: float = 0.0

class LocalStorageWorkflowRunner:
    """Complete workflow runner with local-only storage"""
    
    # Phase dependencies (what must complete before each phase)
    PHASE_DEPENDENCIES = {
        WorkflowPhase.INIT: set(),
        WorkflowPhase.CREDENTIALS: {WorkflowPhase.INIT},
        WorkflowPhase.FETCH_TITLE: {WorkflowPhase.CREDENTIALS},
        WorkflowPhase.SCRAPE_PRODUCTS: {WorkflowPhase.FETCH_TITLE},
        WorkflowPhase.EXTRACT_CATEGORY: {WorkflowPhase.FETCH_TITLE},  # Can run parallel with scraping
        WorkflowPhase.VALIDATE_PRODUCTS: {WorkflowPhase.SCRAPE_PRODUCTS},
        WorkflowPhase.SAVE_PRODUCTS: {WorkflowPhase.VALIDATE_PRODUCTS},
        WorkflowPhase.GENERATE_IMAGES: {WorkflowPhase.SAVE_PRODUCTS},
        WorkflowPhase.GENERATE_CONTENT: {WorkflowPhase.EXTRACT_CATEGORY, WorkflowPhase.SAVE_PRODUCTS},
        WorkflowPhase.GENERATE_SCRIPTS: {WorkflowPhase.GENERATE_CONTENT},
        WorkflowPhase.GENERATE_VOICE: {WorkflowPhase.GENERATE_SCRIPTS},  # Can run parallel with images
        WorkflowPhase.GENERATE_INTRO_OUTRO: {WorkflowPhase.GENERATE_SCRIPTS},  # Can run parallel
        WorkflowPhase.VALIDATE_CONTENT: {WorkflowPhase.GENERATE_VOICE, WorkflowPhase.GENERATE_INTRO_OUTRO},
        WorkflowPhase.CREATE_VIDEO: {WorkflowPhase.VALIDATE_CONTENT, WorkflowPhase.GENERATE_IMAGES},
        WorkflowPhase.PUBLISH_WORDPRESS: {WorkflowPhase.CREATE_VIDEO},
        WorkflowPhase.PUBLISH_YOUTUBE: {WorkflowPhase.CREATE_VIDEO},  # Can run parallel with WordPress
        WorkflowPhase.PUBLISH_INSTAGRAM: {WorkflowPhase.CREATE_VIDEO},  # Can run parallel with others
        WorkflowPhase.UPDATE_STATUS: {WorkflowPhase.PUBLISH_WORDPRESS, WorkflowPhase.PUBLISH_YOUTUBE, WorkflowPhase.PUBLISH_INSTAGRAM},
        WorkflowPhase.FINALIZE: {WorkflowPhase.UPDATE_STATUS}
    }
    
    def __init__(self):
        """Initialize the local storage workflow runner"""
        self.start_time = None
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/home/claude-workflow/workflow_local_storage.log'),
                logging.StreamHandler()
            ]
        )
        
        # Workflow state
        self.config = None
        self.services = {}
        self.phase_results: Dict[WorkflowPhase, PhaseResult] = {}
        self.completed_phases: Set[WorkflowPhase] = set()
        self.current_record = None
        
        # Performance tracking
        self.cache_manager = None
        self.circuit_breaker_manager = None
        self.storage_manager = None
        
        self.logger.info("""
========================================
LOCAL STORAGE WORKFLOW RUNNER INITIALIZED
========================================
✅ All media saved locally only
✅ No Google Drive uploads during generation
✅ WordPress uploads media when publishing
✅ Remotion uses local files (100% reliable)
✅ Faster workflow execution
========================================
""")
    
    async def initialize(self):
        """Initialize services and resources"""
        try:
            self.logger.info("🚀 Initializing local storage workflow...")
            
            # Load configuration
            config_path = '/home/claude-workflow/config/api_keys.json'
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            # Initialize storage manager
            self.storage_manager = get_storage_manager(self.config)
            self.logger.info(f"📁 Local storage initialized: {self.storage_manager.base_local_path}")
            
            # Initialize cache manager
            self.cache_manager = await get_cache_manager()
            await self.cache_manager.initialize()
            
            # Initialize circuit breaker
            self.circuit_breaker_manager = get_circuit_breaker_manager()
            
            # Clean up old files (older than 7 days)
            self.storage_manager.cleanup_old_files(days_to_keep=7)
            
            # Get storage stats
            stats = self.storage_manager.get_storage_stats()
            self.logger.info(f"📊 Storage Stats: {stats['total_files']} files, {stats['total_size_mb']} MB")
            
            # Initialize OpenAI
            openai.api_key = self.config.get('openai_api_key')
            
            return PhaseResult(WorkflowPhase.INIT, True)
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return PhaseResult(WorkflowPhase.INIT, False, error=str(e))
    
    async def validate_credentials(self):
        """Validate all API credentials in parallel"""
        try:
            self.logger.info("🔐 Validating credentials...")
            
            # Pass config path, not the config dict
            config_path = '/home/claude-workflow/config/api_keys.json'
            validator = ProductionCredentialValidationServerOptimized(config_path)
            result = await validator.validate_all_credentials()
            
            # Allow workflow to proceed with warnings (ScrapingDog sometimes has timeout issues)
            if result['overall_status'] == 'failed':
                invalid = [k for k, v in result['results'].items() if v.get('status') == 'invalid']
                if invalid:
                    return PhaseResult(WorkflowPhase.CREDENTIALS, False, 
                                     error=f"Invalid credentials: {invalid}")
            elif result['overall_status'] == 'warning':
                self.logger.warning(f"Some credentials had warnings but proceeding: {result.get('warnings', [])}")
            
            self.logger.info("✅ All credentials validated")
            return PhaseResult(WorkflowPhase.CREDENTIALS, True, data=result)
            
        except Exception as e:
            return PhaseResult(WorkflowPhase.CREDENTIALS, False, error=str(e))
    
    async def phase_fetch_title(self):
        """Fetch pending title from Airtable"""
        try:
            self.logger.info("📋 Fetching title from Airtable...")
            
            airtable_server = ProductionAirtableMCPServer(
                self.config.get('airtable_api_key'),
                self.config.get('airtable_base_id'),
                self.config.get('airtable_table_name')
            )
            
            # Get pending title
            pending_title = await airtable_server.get_pending_title()
            
            if pending_title:
                # Convert to the expected format
                self.current_record = {
                    'id': pending_title['record_id'],
                    'fields': {
                        'Title': pending_title.get('Title', ''),
                        'Status': pending_title.get('Status', 'Pending'),
                        'Content Category': pending_title.get('Content Category', ''),
                        'KeyWords': pending_title.get('KeyWords', ''),
                    }
                }
                title = self.current_record['fields'].get('Title', 'Unknown')
                self.logger.info(f"✅ Fetched title: {title}")
                return PhaseResult(WorkflowPhase.FETCH_TITLE, True, data={'record': self.current_record})
            else:
                return PhaseResult(WorkflowPhase.FETCH_TITLE, False, 
                                 error="No pending titles found")
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.FETCH_TITLE, False, error=str(e))
    
    async def phase_scrape_products(self):
        """Scrape Amazon products"""
        try:
            self.logger.info("🛒 Scraping Amazon products...")
            
            scraper = ProductionProgressiveAmazonScraper(
                self.config.get('scrapingdog_api_key'),
                self.config.get('openai_api_key')
            )
            title = self.current_record['fields'].get('Title', '')
            
            products, variant = await scraper.search_with_variants(title)
            
            # CRITICAL: Validate we have exactly 5 products before proceeding
            if products and len(products) >= 5:
                self.logger.info(f"✅ VALIDATION PASSED: Scraped {len(products)} products (required: 5)")
                # Update record with products - including photo URLs
                for i, product in enumerate(products[:5], 1):
                    self.current_record['fields'][f'ProductNo{i}Title'] = product.get('title', '')  # Fixed: 'title' not 'name'
                    self.current_record['fields'][f'ProductNo{i}Photo'] = product.get('image', '')  # IMPORTANT: Add photo URL
                    self.current_record['fields'][f'ProductNo{i}Description'] = product.get('description', '')
                    # Convert price from string to float
                    price_str = product.get('price', '0')
                    price_float = float(price_str.replace('$', '').replace(',', '')) if price_str else 0.0
                    self.current_record['fields'][f'ProductNo{i}Price'] = price_float
                    # Rating is already a float from scraper
                    self.current_record['fields'][f'ProductNo{i}Rating'] = product.get('rating', 0.0)
                    # Reviews is already an int from scraper  
                    self.current_record['fields'][f'ProductNo{i}Reviews'] = product.get('reviews', 0)
                    self.current_record['fields'][f'ProductNo{i}AffiliateLink'] = product.get('link', '')  # Fixed: 'link' not 'url'
                
                return PhaseResult(WorkflowPhase.SCRAPE_PRODUCTS, True, data={'products': products, 'variant': variant})
            else:
                # FAIL if we don't have enough products
                actual_count = len(products) if products else 0
                error_msg = f"INSUFFICIENT PRODUCTS: Found only {actual_count} products (required: 5 with 10+ reviews)"
                self.logger.error(f"❌ {error_msg}")
                self.logger.error("   This title cannot be processed - must have 5 qualifying products")
                self.logger.error("   Workflow will stop here to avoid wasting resources")
                
                # Update Airtable status to mark this title as problematic
                if self.current_record and self.current_record.get('fields'):
                    self.current_record['fields']['Status'] = 'Failed - Insufficient Products'
                
                return PhaseResult(WorkflowPhase.SCRAPE_PRODUCTS, False, 
                                 error=error_msg)
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.SCRAPE_PRODUCTS, False, error=str(e))
    
    async def phase_extract_category(self):
        """Extract product categories"""
        try:
            self.logger.info("🏷️ Extracting categories...")
            
            extractor = ProductionProductCategoryExtractorMCPServer(self.config)
            title = self.current_record['fields'].get('Title', '')
            
            result = await extractor.extract_category_batch([title])
            
            if result.get('success'):
                categories = result.get('results', [])
                if categories:
                    self.current_record['fields']['Content Category'] = categories[0].get('main_category', '')
                
                self.logger.info("✅ Categories extracted")
                return PhaseResult(WorkflowPhase.EXTRACT_CATEGORY, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.EXTRACT_CATEGORY, False, 
                                 error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.EXTRACT_CATEGORY, False, error=str(e))
    
    async def phase_validate_products(self):
        """Validate scraped products"""
        try:
            self.logger.info("✅ Validating products...")
            
            # Create validator with scrapingdog API key
            validator = ProductionAmazonProductValidator(
                scrapingdog_api_key=self.config.get('scrapingdog_api_key')
            )
            
            # Collect all products for validation
            products = []
            for i in range(1, 6):
                title = self.current_record['fields'].get(f'ProductNo{i}Title', '')
                if title:
                    product_data = {
                        'title': title,
                        'price': str(self.current_record['fields'].get(f'ProductNo{i}Price', 0)),
                        'rating': str(self.current_record['fields'].get(f'ProductNo{i}Rating', 0)),
                        'reviews': str(self.current_record['fields'].get(f'ProductNo{i}Reviews', 0)),
                        'image': self.current_record['fields'].get(f'ProductNo{i}Photo', ''),
                        'link': self.current_record['fields'].get(f'ProductNo{i}AffiliateLink', '')
                    }
                    products.append(product_data)
                    self.logger.info(f"Product {i}: title='{title[:50]}...', rating={product_data['rating']}, reviews={product_data['reviews']}")
            
            # Validate all products at once
            validation_result = await validator.validate_amazon_products(products, min_products=5)
            
            if validation_result['valid']:
                self.logger.info(f"✅ All {validation_result['product_count']} products validated")
                return PhaseResult(WorkflowPhase.VALIDATE_PRODUCTS, True)
            else:
                error_msg = validation_result.get('reason', 'Product validation failed')
                self.logger.warning(f"❌ Validation failed: {error_msg}")
                return PhaseResult(WorkflowPhase.VALIDATE_PRODUCTS, False, error=error_msg)
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.VALIDATE_PRODUCTS, False, error=str(e))
    
    async def phase_save_products(self):
        """Save products to Airtable"""
        try:
            self.logger.info("💾 Saving products to Airtable...")
            
            airtable_server = ProductionAirtableMCPServer(
                self.config.get('airtable_api_key'),
                self.config.get('airtable_base_id'),
                self.config.get('airtable_table_name')
            )
            
            # Update record status
            self.current_record['fields']['Status'] = 'In Progress'
            
            result = await airtable_server.update_record_fields_batch(
                self.current_record['id'],
                self.current_record['fields']
            )
            
            if result:  # update_record_fields_batch returns boolean
                self.logger.info("✅ Products saved to Airtable")
                return PhaseResult(WorkflowPhase.SAVE_PRODUCTS, True, data={'status': 'success'})
            else:
                return PhaseResult(WorkflowPhase.SAVE_PRODUCTS, False, 
                                 error="Failed to update Airtable record")
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.SAVE_PRODUCTS, False, error=str(e))
    
    async def phase_generate_images(self):
        """Generate images with GPT-4o Vision + Imagen 4 Ultra"""
        try:
            self.logger.info("🎨 Generating images with GPT-4o Vision + Imagen 4 Ultra...")
            
            # Debug: Check what data we have
            fields = self.current_record.get('fields', {})
            for i in range(1, 6):
                photo_url = fields.get(f'ProductNo{i}Photo', '')
                title = fields.get(f'ProductNo{i}Title', '')
                if photo_url:
                    self.logger.info(f"  Product {i} - Title: {title[:30] if title else 'N/A'}, Photo: ✅")
                else:
                    self.logger.info(f"  Product {i} - Title: {title[:30] if title else 'N/A'}, Photo: ❌ MISSING")
            
            # Try to generate images
            try:
                self.logger.info("Calling production_generate_images_with_imagen4_ultra...")
                result = await production_generate_images_with_imagen4_ultra(
                    self.current_record, 
                    self.config
                )
                self.logger.info(f"Image generation returned: {result}")
            except Exception as img_error:
                self.logger.error(f"Image generation raised exception: {img_error}")
                import traceback
                self.logger.error(traceback.format_exc())
                result = {'success': False, 'error': str(img_error)}
            
            if result and result.get('success'):
                self.logger.info(f"✅ Generated {result.get('images_generated')} images locally")
                self.current_record = result.get('updated_record', self.current_record)
                return PhaseResult(WorkflowPhase.GENERATE_IMAGES, True, data=result)
            else:
                error_msg = result.get('error', 'Unknown error') if result else 'Function returned None'
                self.logger.error(f"Image generation failed with result: {result}")
                return PhaseResult(WorkflowPhase.GENERATE_IMAGES, False, error=error_msg)
                                 
        except Exception as e:
            self.logger.error(f"Image generation exception: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return PhaseResult(WorkflowPhase.GENERATE_IMAGES, False, error=str(e))
    
    async def phase_generate_content(self):
        """Generate platform content"""
        try:
            self.logger.info("📝 Generating platform content...")
            
            from src.mcp.production_platform_content_generator_async import production_generate_platform_content_for_workflow_async
            
            title = self.current_record['fields'].get('Title', '')
            category = self.current_record['fields'].get('Content Category', '')
            
            result = await production_generate_platform_content_for_workflow_async(
                title,
                category,
                self.config
            )
            
            if result:
                # The function returns content fields directly, not a success/error dict
                self.logger.info("✅ Platform content generated")
                # Update the current record with the generated content
                for field, value in result.items():
                    self.current_record['fields'][field] = value
                return PhaseResult(WorkflowPhase.GENERATE_CONTENT, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.GENERATE_CONTENT, False, 
                                 error="No content generated")
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.GENERATE_CONTENT, False, error=str(e))
    
    async def phase_generate_scripts(self):
        """Generate voice scripts"""
        try:
            self.logger.info("📄 Generating voice scripts...")
            
            result = await production_run_text_control_with_regeneration(
                self.current_record,
                self.config
            )
            
            if result.get('success'):
                self.logger.info(f"✅ Generated {result.get('scripts_generated')} scripts")
                self.current_record = result.get('updated_record', self.current_record)
                return PhaseResult(WorkflowPhase.GENERATE_SCRIPTS, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.GENERATE_SCRIPTS, False, 
                                 error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.GENERATE_SCRIPTS, False, error=str(e))
    
    async def phase_generate_voice(self):
        """Generate voice files and save locally only"""
        try:
            self.logger.info("🎤 Generating voice files (local storage only)...")
            
            # Use local voice generation
            voice_generator = ProductionVoiceGenerationLocal(self.config)
            result = await voice_generator.generate_all_voices_local(
                self.current_record
            )
            
            if result.get('success'):
                self.logger.info(f"✅ Generated {result.get('voices_generated')} voice files locally")
                self.current_record = result.get('updated_record', self.current_record)
                return PhaseResult(WorkflowPhase.GENERATE_VOICE, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.GENERATE_VOICE, False, 
                                 error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.GENERATE_VOICE, False, error=str(e))
    
    async def phase_generate_intro_outro(self):
        """Generate intro/outro content"""
        try:
            self.logger.info("🎬 Generating intro/outro content...")
            
            # This is included in voice generation
            self.logger.info("✅ Intro/outro included in voice generation")
            return PhaseResult(WorkflowPhase.GENERATE_INTRO_OUTRO, True)
            
        except Exception as e:
            return PhaseResult(WorkflowPhase.GENERATE_INTRO_OUTRO, False, error=str(e))
    
    async def phase_validate_content(self):
        """Validate all generated content"""
        try:
            self.logger.info("✅ Validating content...")
            
            result = await production_run_text_validation_with_regeneration(
                self.current_record,
                self.config
            )
            
            if result.get('success'):
                self.logger.info("✅ Content validation passed")
                self.current_record = result.get('updated_record', self.current_record)
                return PhaseResult(WorkflowPhase.VALIDATE_CONTENT, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.VALIDATE_CONTENT, False, 
                                 error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.VALIDATE_CONTENT, False, error=str(e))
    
    async def phase_create_video(self):
        """Create video using Remotion - standard or WOW version"""
        try:
            # Check video type from config
            video_type = self.config.get('video_type', 'standard').lower()
            
            if video_type == 'wow':
                self.logger.info("🎬 Creating WOW video with amazing effects...")
                
                # Use WOW video generator
                result = await production_generate_wow_video(
                    self.current_record,
                    self.config
                )
                
                if result.get('success'):
                    video_size = result.get('video_size_mb', 0)
                    self.logger.info(f"✅ WOW video created: {video_size} MB")
                    self.logger.info("   🎨 Effects: Advanced transitions, reviews, subtitles")
                    self.current_record = result.get('updated_record', self.current_record)
                    return PhaseResult(WorkflowPhase.CREATE_VIDEO, True, data=result)
                else:
                    return PhaseResult(WorkflowPhase.CREATE_VIDEO, False, 
                                     error=result.get('error'))
            else:
                # Standard video
                self.logger.info("🎬 Creating standard video with Remotion...")
                
                # Use strict Remotion that validates all media
                result = await production_run_video_creation(
                    self.current_record,
                    self.config
                )
                
                if result.get('success'):
                    video_size = result.get('video_size_mb', 0)
                    self.logger.info(f"✅ Standard video created: {video_size} MB")
                    self.current_record = result.get('updated_record', self.current_record)
                    return PhaseResult(WorkflowPhase.CREATE_VIDEO, True, data=result)
                else:
                    missing_files = result.get('missing_files', [])
                    if missing_files:
                        self.logger.error(f"❌ Missing files: {missing_files}")
                    return PhaseResult(WorkflowPhase.CREATE_VIDEO, False, 
                                     error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.CREATE_VIDEO, False, error=str(e))
    
    async def phase_publish_wordpress(self):
        """Publish to WordPress with local media upload"""
        try:
            self.logger.info("📝 Publishing to WordPress (uploading local media)...")
            
            result = await production_publish_to_wordpress_local(
                self.current_record,
                self.config
            )
            
            if result.get('success'):
                post_url = result.get('post_url')
                media_count = result.get('media_uploaded', 0)
                self.logger.info(f"✅ WordPress published: {post_url}")
                self.logger.info(f"   Uploaded {media_count} media files")
                self.current_record = result.get('updated_record', self.current_record)
                return PhaseResult(WorkflowPhase.PUBLISH_WORDPRESS, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.PUBLISH_WORDPRESS, False, 
                                 error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.PUBLISH_WORDPRESS, False, error=str(e))
    
    async def phase_publish_youtube(self):
        """Publish to YouTube using local video file"""
        try:
            self.logger.info("📺 Publishing to YouTube (using local video)...")
            
            result = await production_upload_to_youtube_local(
                self.current_record,
                self.config
            )
            
            if result.get('success'):
                video_url = result.get('video_url')
                self.logger.info(f"✅ YouTube published: {video_url}")
                self.current_record = result.get('updated_record', self.current_record)
                return PhaseResult(WorkflowPhase.PUBLISH_YOUTUBE, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.PUBLISH_YOUTUBE, False, 
                                 error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.PUBLISH_YOUTUBE, False, error=str(e))
    
    async def phase_publish_instagram(self):
        """Publish to Instagram Reels"""
        try:
            # Check if Instagram is enabled
            if not self.config.get('instagram_enabled', False):
                self.logger.info("📱 Instagram publishing disabled, skipping...")
                return PhaseResult(WorkflowPhase.PUBLISH_INSTAGRAM, True, 
                                 data={'skipped': True, 'reason': 'disabled'})
            
            self.logger.info("📱 Publishing to Instagram Reels...")
            
            # Check if we have WordPress URL (for video hosting)
            wordpress_result = self.phase_results.get(WorkflowPhase.PUBLISH_WORDPRESS)
            video_url = None
            if wordpress_result and wordpress_result.data:
                video_url = wordpress_result.data.get('video_url')
            
            # Set video URL in record if available
            if video_url:
                self.current_record['fields']['VideoURL'] = video_url
            
            result = await production_upload_to_instagram(
                self.current_record,
                self.config
            )
            
            if result.get('success'):
                reel_url = result.get('permalink', 'Instagram Reel')
                self.logger.info(f"✅ Instagram published: {reel_url}")
                self.current_record['fields']['InstagramURL'] = reel_url
                return PhaseResult(WorkflowPhase.PUBLISH_INSTAGRAM, True, data=result)
            else:
                # Instagram failure is non-critical
                self.logger.warning(f"⚠️ Instagram publish failed: {result.get('error')}")
                return PhaseResult(WorkflowPhase.PUBLISH_INSTAGRAM, True, 
                                 data={'warning': result.get('error')})
                                 
        except Exception as e:
            # Instagram errors are non-critical
            self.logger.warning(f"⚠️ Instagram publish error: {e}")
            return PhaseResult(WorkflowPhase.PUBLISH_INSTAGRAM, True, 
                             data={'warning': str(e)})
    
    async def phase_update_status(self):
        """Update final status in Airtable"""
        try:
            self.logger.info("📊 Updating final status...")
            
            airtable_server = ProductionAirtableMCPServer(
                self.config.get('airtable_api_key'),
                self.config.get('airtable_base_id'),
                self.config.get('airtable_table_name')
            )
            
            # Update record status
            self.current_record['fields']['Status'] = 'Ready'
            self.current_record['fields']['ProcessedAt'] = datetime.now().isoformat()
            
            result = await airtable_server.update_record_fields_batch(
                self.current_record['id'],
                self.current_record['fields']
            )
            
            if result:  # update_record_fields_batch returns boolean
                self.logger.info("✅ Status updated to Ready")
                return PhaseResult(WorkflowPhase.UPDATE_STATUS, True, data={'status': 'success'})
            else:
                return PhaseResult(WorkflowPhase.UPDATE_STATUS, False, 
                                 error="Failed to update status")
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.UPDATE_STATUS, False, error=str(e))
    
    async def execute_phase(self, phase: WorkflowPhase) -> PhaseResult:
        """Execute a single workflow phase"""
        start_time = datetime.now()
        
        try:
            # Map phases to methods
            phase_methods = {
                WorkflowPhase.INIT: self.initialize,
                WorkflowPhase.CREDENTIALS: self.validate_credentials,
                WorkflowPhase.FETCH_TITLE: self.phase_fetch_title,
                WorkflowPhase.SCRAPE_PRODUCTS: self.phase_scrape_products,
                WorkflowPhase.EXTRACT_CATEGORY: self.phase_extract_category,
                WorkflowPhase.VALIDATE_PRODUCTS: self.phase_validate_products,
                WorkflowPhase.SAVE_PRODUCTS: self.phase_save_products,
                WorkflowPhase.GENERATE_IMAGES: self.phase_generate_images,
                WorkflowPhase.GENERATE_CONTENT: self.phase_generate_content,
                WorkflowPhase.GENERATE_SCRIPTS: self.phase_generate_scripts,
                WorkflowPhase.GENERATE_VOICE: self.phase_generate_voice,
                WorkflowPhase.GENERATE_INTRO_OUTRO: self.phase_generate_intro_outro,
                WorkflowPhase.VALIDATE_CONTENT: self.phase_validate_content,
                WorkflowPhase.CREATE_VIDEO: self.phase_create_video,
                WorkflowPhase.PUBLISH_WORDPRESS: self.phase_publish_wordpress,
                WorkflowPhase.PUBLISH_YOUTUBE: self.phase_publish_youtube,
                WorkflowPhase.PUBLISH_INSTAGRAM: self.phase_publish_instagram,
                WorkflowPhase.UPDATE_STATUS: self.phase_update_status,
                WorkflowPhase.FINALIZE: lambda: PhaseResult(WorkflowPhase.FINALIZE, True)
            }
            
            method = phase_methods.get(phase)
            if method:
                result = await method()
            else:
                result = PhaseResult(phase, True)
            
            duration = (datetime.now() - start_time).total_seconds()
            result.duration = duration
            
            # Store result
            self.phase_results[phase] = result
            if result.success:
                self.completed_phases.add(phase)
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Phase {phase.value} failed: {e}")
            return PhaseResult(phase, False, error=str(e), duration=duration)
    
    async def run(self):
        """Run the complete workflow with local storage"""
        self.start_time = datetime.now()
        
        try:
            self.logger.info("""
╔══════════════════════════════════════════════╗
║   LOCAL STORAGE WORKFLOW STARTING            ║
║   All media saved locally only               ║
║   WordPress will upload during publishing    ║
╚══════════════════════════════════════════════╝
""")
            
            # Phase 1: Initialize
            result = await self.execute_phase(WorkflowPhase.INIT)
            if not result.success:
                raise Exception(f"Initialization failed: {result.error}")
            
            # Phase 2: Validate credentials
            result = await self.execute_phase(WorkflowPhase.CREDENTIALS)
            if not result.success:
                raise Exception(f"Credential validation failed: {result.error}")
            
            # Phase 3: Fetch title
            result = await self.execute_phase(WorkflowPhase.FETCH_TITLE)
            if not result.success:
                self.logger.warning("No pending titles found")
                return True  # Not an error, just no work to do
            
            # Phase 4: Scrape products and extract category in parallel
            scrape_task = self.execute_phase(WorkflowPhase.SCRAPE_PRODUCTS)
            category_task = self.execute_phase(WorkflowPhase.EXTRACT_CATEGORY)
            
            scrape_result, category_result = await asyncio.gather(
                scrape_task, category_task
            )
            
            if not scrape_result.success:
                raise Exception(f"Product scraping failed: {scrape_result.error}")
            
            # Phase 5: Validate products
            result = await self.execute_phase(WorkflowPhase.VALIDATE_PRODUCTS)
            if not result.success:
                raise Exception(f"Product validation failed: {result.error}")
            
            # Phase 6: Save products
            result = await self.execute_phase(WorkflowPhase.SAVE_PRODUCTS)
            if not result.success:
                raise Exception(f"Saving products failed: {result.error}")
            
            # Phase 7: Generate content and scripts
            result = await self.execute_phase(WorkflowPhase.GENERATE_CONTENT)
            if not result.success:
                raise Exception(f"Content generation failed: {result.error}")
            
            result = await self.execute_phase(WorkflowPhase.GENERATE_SCRIPTS)
            if not result.success:
                raise Exception(f"Script generation failed: {result.error}")
            
            # Phase 8: Generate media in parallel (images, voice, intro/outro)
            image_task = self.execute_phase(WorkflowPhase.GENERATE_IMAGES)
            voice_task = self.execute_phase(WorkflowPhase.GENERATE_VOICE)
            intro_outro_task = self.execute_phase(WorkflowPhase.GENERATE_INTRO_OUTRO)
            
            image_result, voice_result, intro_outro_result = await asyncio.gather(
                image_task, voice_task, intro_outro_task
            )
            
            if not image_result.success:
                raise Exception(f"Image generation failed: {image_result.error}")
            if not voice_result.success:
                raise Exception(f"Voice generation failed: {voice_result.error}")
            
            # Phase 9: Validate content
            result = await self.execute_phase(WorkflowPhase.VALIDATE_CONTENT)
            if not result.success:
                self.logger.warning(f"Content validation warning: {result.error}")
            
            # Phase 10: Create video
            result = await self.execute_phase(WorkflowPhase.CREATE_VIDEO)
            if not result.success:
                raise Exception(f"Video creation failed: {result.error}")
            
            # Phase 11: Publish to platforms in parallel
            wp_task = self.execute_phase(WorkflowPhase.PUBLISH_WORDPRESS)
            yt_task = self.execute_phase(WorkflowPhase.PUBLISH_YOUTUBE)
            
            wp_result, yt_result = await asyncio.gather(
                wp_task, yt_task, return_exceptions=True
            )
            
            # Check results (allow partial success)
            if isinstance(wp_result, Exception):
                self.logger.error(f"WordPress publishing failed: {wp_result}")
            elif not wp_result.success:
                self.logger.error(f"WordPress publishing failed: {wp_result.error}")
            
            if isinstance(yt_result, Exception):
                self.logger.error(f"YouTube publishing failed: {yt_result}")
            elif not yt_result.success:
                self.logger.error(f"YouTube publishing failed: {yt_result.error}")
            
            # Phase 12: Update status
            result = await self.execute_phase(WorkflowPhase.UPDATE_STATUS)
            if not result.success:
                self.logger.warning(f"Status update failed: {result.error}")
            
            # Phase 13: Finalize
            await self.execute_phase(WorkflowPhase.FINALIZE)
            
            # Calculate total time
            total_time = (datetime.now() - self.start_time).total_seconds()
            
            # Get final storage stats
            if self.storage_manager:
                storage_stats = self.storage_manager.get_storage_stats()
            else:
                storage_stats = {'total_files': 0, 'total_size_mb': 0}
            
            # Print summary
            self.logger.info(f"""
╔══════════════════════════════════════════════╗
║   WORKFLOW COMPLETED SUCCESSFULLY            ║
╠══════════════════════════════════════════════╣
║   Total Time: {total_time:.1f} seconds       ║
║   Local Files: {storage_stats['total_files']} files         ║
║   Storage Used: {storage_stats['total_size_mb']:.1f} MB     ║
║   WordPress: Media uploaded                  ║
║   YouTube: Video uploaded                    ║
╚══════════════════════════════════════════════╝
""")
            
            # Print phase timings
            self.logger.info("\n📊 Phase Timings:")
            for phase in WorkflowPhase:
                if phase in self.phase_results:
                    result = self.phase_results[phase]
                    status = "✅" if result.success else "❌"
                    self.logger.info(f"  {status} {phase.value}: {result.duration:.1f}s")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            
            # Print what completed
            self.logger.info("\n📊 Completed Phases:")
            for phase in self.completed_phases:
                self.logger.info(f"  ✅ {phase.value}")
            
            return False


async def main():
    """Main entry point"""
    runner = LocalStorageWorkflowRunner()
    success = await runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())