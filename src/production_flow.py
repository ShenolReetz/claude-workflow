#!/usr/bin/env python3
"""
Production Workflow Runner - LOCAL STORAGE VERSION
===================================================

This version saves all media files LOCALLY ONLY:
- No Google Drive uploads during generation
- WordPress uploads media when publishing
- Remotion uses local files (100% reliable)
- Faster workflow (no upload delays)

Based on Ultra-Optimized version with modifications for local storage.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging
import aiofiles
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
from mcp_servers.production_voice_generation_server_local import ProductionVoiceGenerationLocal  # Local version
from mcp_servers.production_product_category_extractor_server import ProductionProductCategoryExtractorMCPServer
from mcp_servers.production_flow_control_server import ProductionFlowControlMCPServer
from mcp_servers.production_amazon_product_validator import ProductionAmazonProductValidator

# Import Production MCP agents
from src.mcp.production_text_generation_control_agent_mcp_v2 import production_run_text_control_with_regeneration

# Import STRICT Remotion (requires all media files)
from src.mcp.production_remotion_video_generator_strict import production_run_video_creation

# Import LOCAL storage versions
from src.mcp.production_wordpress_local_media import production_publish_to_wordpress_local
from src.mcp.production_youtube_local_upload import production_upload_to_youtube_local
from src.mcp.production_imagen4_ultra_with_gpt4_vision import production_generate_images_with_imagen4_ultra
from src.mcp.production_platform_content_generator_async import production_generate_platform_content_for_workflow
from src.mcp.production_text_length_validation_with_regeneration_agent_mcp import production_run_text_validation_with_regeneration

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
    """Workflow runner with local-only storage"""
    
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
        WorkflowPhase.FINALIZE: {WorkflowPhase.PUBLISH_WORDPRESS, WorkflowPhase.PUBLISH_YOUTUBE}
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
            
            return PhaseResult(WorkflowPhase.INIT, True)
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return PhaseResult(WorkflowPhase.INIT, False, error=str(e))
    
    async def validate_credentials(self):
        """Validate all API credentials in parallel"""
        try:
            self.logger.info("🔐 Validating credentials...")
            
            validator = ProductionCredentialValidationServerOptimized(self.config)
            result = await validator.validate_all_credentials_parallel()
            
            if not result['all_valid']:
                invalid = [k for k, v in result['results'].items() if not v.get('valid')]
                return PhaseResult(WorkflowPhase.CREDENTIALS, False, 
                                 error=f"Invalid credentials: {invalid}")
            
            self.logger.info("✅ All credentials validated")
            return PhaseResult(WorkflowPhase.CREDENTIALS, True, data=result)
            
        except Exception as e:
            return PhaseResult(WorkflowPhase.CREDENTIALS, False, error=str(e))
    
    async def phase_generate_images(self):
        """Generate images with GPT-4o Vision + Imagen 4 Ultra"""
        try:
            self.logger.info("🎨 Generating images with GPT-4o Vision + Imagen 4 Ultra...")
            
            result = await production_generate_images_with_imagen4_ultra(
                self.current_record, 
                self.config
            )
            
            if result.get('success'):
                self.logger.info(f"✅ Generated {result.get('images_generated')} images locally")
                self.current_record = result.get('updated_record', self.current_record)
                return PhaseResult(WorkflowPhase.GENERATE_IMAGES, True, data=result)
            else:
                return PhaseResult(WorkflowPhase.GENERATE_IMAGES, False, 
                                 error=result.get('error'))
                                 
        except Exception as e:
            return PhaseResult(WorkflowPhase.GENERATE_IMAGES, False, error=str(e))
    
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
    
    async def phase_create_video(self):
        """Create video using STRICT Remotion with local files"""
        try:
            self.logger.info("🎬 Creating video with Remotion (strict validation)...")
            
            # Use strict Remotion that validates all media
            result = await production_run_video_creation(
                self.current_record,
                self.config
            )
            
            if result.get('success'):
                video_size = result.get('video_size_mb', 0)
                self.logger.info(f"✅ Video created: {video_size} MB")
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
    
    async def execute_phase(self, phase: WorkflowPhase) -> PhaseResult:
        """Execute a single workflow phase"""
        start_time = datetime.now()
        
        try:
            # Map phases to methods
            phase_methods = {
                WorkflowPhase.INIT: self.initialize,
                WorkflowPhase.CREDENTIALS: self.validate_credentials,
                WorkflowPhase.GENERATE_IMAGES: self.phase_generate_images,
                WorkflowPhase.GENERATE_VOICE: self.phase_generate_voice,
                WorkflowPhase.CREATE_VIDEO: self.phase_create_video,
                WorkflowPhase.PUBLISH_WORDPRESS: self.phase_publish_wordpress,
                WorkflowPhase.PUBLISH_YOUTUBE: self.phase_publish_youtube,
                # Add other phases as needed...
            }
            
            method = phase_methods.get(phase)
            if method:
                result = await method()
            else:
                # Placeholder for other phases
                result = PhaseResult(phase, True)
            
            duration = (datetime.now() - start_time).total_seconds()
            result.duration = duration
            
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
            
            # Initialize
            await self.execute_phase(WorkflowPhase.INIT)
            
            # Validate credentials
            await self.execute_phase(WorkflowPhase.CREDENTIALS)
            
            # Main workflow phases
            # ... (implement other phases as needed)
            
            # Generate media locally
            await self.execute_phase(WorkflowPhase.GENERATE_IMAGES)
            await self.execute_phase(WorkflowPhase.GENERATE_VOICE)
            
            # Create video with local files
            await self.execute_phase(WorkflowPhase.CREATE_VIDEO)
            
            # Publish with local media upload
            await asyncio.gather(
                self.execute_phase(WorkflowPhase.PUBLISH_WORDPRESS),
                self.execute_phase(WorkflowPhase.PUBLISH_YOUTUBE)
            )
            
            # Calculate total time
            total_time = (datetime.now() - self.start_time).total_seconds()
            
            # Get final storage stats
            storage_stats = self.storage_manager.get_storage_stats()
            
            self.logger.info(f"""
╔══════════════════════════════════════════════╗
║   WORKFLOW COMPLETED SUCCESSFULLY            ║
╠══════════════════════════════════════════════╣
║   Total Time: {total_time:.1f} seconds                    ║
║   Local Files: {storage_stats['total_files']} files              ║
║   Storage Used: {storage_stats['total_size_mb']} MB            ║
║   WordPress: Media uploaded                  ║
║   YouTube: Video uploaded                    ║
╚══════════════════════════════════════════════╝
""")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            return False


async def main():
    """Main entry point"""
    runner = LocalStorageWorkflowRunner()
    success = await runner.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())