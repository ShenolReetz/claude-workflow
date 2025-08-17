#!/usr/bin/env python3
"""
Test Workflow Runner with Dummy Data
=====================================
Uses hardcoded test data to avoid API calls and token usage.
Perfect for testing Remotion and workflow flow without costs.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestWorkflowRunner:
    """Test runner with mock data - no API calls"""
    
    def __init__(self):
        self.test_data = self._load_test_data()
        self.temp_dir = tempfile.mkdtemp(prefix="test_workflow_")
        logger.info(f"🧪 Test workflow initialized with temp dir: {self.temp_dir}")
        
    def _load_test_data(self) -> Dict:
        """Load hardcoded test data"""
        return {
            "record_id": "recTEST123456789",
            "title": "Top 5 Best Wireless Headphones 2025",
            "category": "Electronics & Audio",
            "products": [
                {
                    "title": "Sony WH-1000XM5 Wireless Headphones",
                    "description": "Industry-leading noise canceling with Auto NC Optimizer",
                    "price": "$399.99",
                    "rating": 4.8,
                    "total_reviews": 12543,
                    "image": "https://m.media-amazon.com/images/I/71o8Q5XJS5L._AC_SL1500_.jpg",
                    "link": "https://www.amazon.com/dp/B09XS7JWHH"
                },
                {
                    "title": "Bose QuietComfort 45",
                    "description": "Premium noise-cancelling wireless headphones",
                    "price": "$329.00",
                    "rating": 4.5,
                    "total_reviews": 8921,
                    "image": "https://m.media-amazon.com/images/I/51JbsHSktkL._AC_SL1500_.jpg",
                    "link": "https://www.amazon.com/dp/B098FKXT8L"
                },
                {
                    "title": "Apple AirPods Max",
                    "description": "High-fidelity audio with Active Noise Cancellation",
                    "price": "$549.00",
                    "rating": 4.4,
                    "total_reviews": 6789,
                    "image": "https://m.media-amazon.com/images/I/81jqUPkIVRL._AC_SL1500_.jpg",
                    "link": "https://www.amazon.com/dp/B08PZHYWJS"
                },
                {
                    "title": "Sennheiser Momentum 4",
                    "description": "Exceptional sound quality with 60-hour battery life",
                    "price": "$379.95",
                    "rating": 4.3,
                    "total_reviews": 4567,
                    "image": "https://m.media-amazon.com/images/I/71PZHIp9mwL._AC_SL1500_.jpg",
                    "link": "https://www.amazon.com/dp/B0B5V2D6QV"
                },
                {
                    "title": "JBL Tour One M2",
                    "description": "True Adaptive Noise Cancelling with Smart Ambient",
                    "price": "$249.95",
                    "rating": 4.2,
                    "total_reviews": 3421,
                    "image": "https://m.media-amazon.com/images/I/61nNLsOWByL._AC_SL1500_.jpg",
                    "link": "https://www.amazon.com/dp/B0B5JZ3S3K"
                }
            ],
            "scripts": {
                "intro": "Welcome to our countdown of the top 5 best wireless headphones for 2025!",
                "product1": "At number 5, we have the JBL Tour One M2 with True Adaptive Noise Cancelling.",
                "product2": "Coming in at number 4, the Sennheiser Momentum 4 offers exceptional sound quality.",
                "product3": "Number 3 goes to the Apple AirPods Max with high-fidelity audio.",
                "product4": "At number 2, the Bose QuietComfort 45 delivers premium noise cancellation.",
                "product5": "And our number 1 pick is the Sony WH-1000XM5 with industry-leading features!",
                "outro": "Thanks for watching! Check the links in the description for these amazing headphones."
            },
            "voice_urls": {
                "intro": "https://drive.google.com/file/d/1_test_intro_audio/view",
                "product1": "https://drive.google.com/file/d/1_test_product1_audio/view",
                "product2": "https://drive.google.com/file/d/1_test_product2_audio/view",
                "product3": "https://drive.google.com/file/d/1_test_product3_audio/view",
                "product4": "https://drive.google.com/file/d/1_test_product4_audio/view",
                "product5": "https://drive.google.com/file/d/1_test_product5_audio/view",
                "outro": "https://drive.google.com/file/d/1_test_outro_audio/view"
            },
            "images": {
                "intro": "https://oaidalleapiprodscus.blob.core.windows.net/test-intro-image.jpg",
                "outro": "https://oaidalleapiprodscus.blob.core.windows.net/test-outro-image.jpg"
            },
            "platform_content": {
                "youtube_title": "Top 5 Best Wireless Headphones 2025 - Ultimate Buyer's Guide",
                "youtube_description": "Discover the best wireless headphones of 2025...",
                "instagram_caption": "🎧 Top 5 Wireless Headphones 2025! #headphones #tech",
                "tiktok_caption": "Best wireless headphones countdown! #tech #headphones",
                "wordpress_title": "Top 5 Best Wireless Headphones 2025",
                "wordpress_content": "Complete review and comparison of the best wireless headphones..."
            }
        }
    
    async def run(self):
        """Run the test workflow"""
        logger.info("=" * 60)
        logger.info("🧪 STARTING TEST WORKFLOW WITH DUMMY DATA")
        logger.info("📅 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("=" * 60)
        
        try:
            # Phase 1: Mock credential validation
            logger.info("✅ Phase 1: Mock credential validation - SKIPPED (test mode)")
            await asyncio.sleep(0.1)
            
            # Phase 2: Mock fetch title
            logger.info(f"✅ Phase 2: Using test title: {self.test_data['title']}")
            await asyncio.sleep(0.1)
            
            # Phase 3: Mock category extraction
            logger.info(f"✅ Phase 3: Using test category: {self.test_data['category']}")
            await asyncio.sleep(0.1)
            
            # Phase 4: Mock product scraping
            logger.info(f"✅ Phase 4: Using {len(self.test_data['products'])} test products")
            for i, product in enumerate(self.test_data['products'], 1):
                logger.info(f"  Product {i}: {product['title'][:50]}...")
            await asyncio.sleep(0.1)
            
            # Phase 5: Mock content generation
            logger.info("✅ Phase 5: Using pre-generated test content")
            await asyncio.sleep(0.1)
            
            # Phase 6: Create test audio files
            logger.info("✅ Phase 6: Creating dummy audio files")
            audio_files = await self._create_dummy_audio_files()
            
            # Phase 7: Create test images
            logger.info("✅ Phase 7: Using test image URLs")
            await asyncio.sleep(0.1)
            
            # Phase 8: Test Remotion video generation
            logger.info("⚡ Phase 8: Testing Remotion video generation")
            video_path = await self._test_remotion_generation()
            
            if video_path and os.path.exists(video_path):
                logger.info(f"✅ Video created successfully: {video_path}")
                file_size = os.path.getsize(video_path) / (1024 * 1024)
                logger.info(f"📊 Video size: {file_size:.2f} MB")
            else:
                logger.error("❌ Video creation failed")
            
            # Phase 9: Mock upload and publishing
            logger.info("✅ Phase 9: Mock upload to platforms - SKIPPED (test mode)")
            
            logger.info("=" * 60)
            logger.info("🎉 TEST WORKFLOW COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Test workflow failed: {e}")
            raise
        finally:
            # Cleanup
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"🧹 Cleaned up temp directory: {self.temp_dir}")
    
    async def _create_dummy_audio_files(self) -> Dict[str, str]:
        """Create dummy audio files for testing"""
        audio_files = {}
        
        for key in ['intro', 'product1', 'product2', 'product3', 'product4', 'product5', 'outro']:
            # Create a tiny dummy MP3 file (just a few bytes of valid MP3 header)
            file_path = os.path.join(self.temp_dir, f"voice_{key}.mp3")
            
            # Minimal MP3 header (ID3v2 tag)
            mp3_header = bytes([
                0x49, 0x44, 0x33, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # ID3v2 header
                0xFF, 0xFB, 0x90, 0x00  # MP3 frame header
            ])
            
            with open(file_path, 'wb') as f:
                f.write(mp3_header)
            
            audio_files[key] = file_path
            logger.info(f"  Created dummy audio: {key} -> {file_path}")
        
        return audio_files
    
    async def _test_remotion_generation(self) -> str:
        """Test Remotion video generation with dummy data"""
        try:
            # Import the Remotion generator
            from src.mcp.production_remotion_video_generator import ProductionRemotionVideoGenerator
            
            generator = ProductionRemotionVideoGenerator()
            
            # Prepare Remotion input data matching the countdown structure
            remotion_data = {
                # Main video title
                "VideoTitle": self.test_data["title"],
                
                # Product data in Airtable format
                "ProductNo1Title": self.test_data["products"][0]["title"],
                "ProductNo1Description": self.test_data["products"][0]["description"],
                "ProductNo1Photo": self.test_data["products"][0]["image"],
                "ProductNo1AffiliateLink": self.test_data["products"][0]["link"],
                "ProductNo1Price": float(self.test_data["products"][0]["price"].replace("$", "").replace(",", "")),
                "ProductNo1Rating": self.test_data["products"][0]["rating"],
                "ProductNo1Reviews": self.test_data["products"][0]["total_reviews"],
                
                "ProductNo2Title": self.test_data["products"][1]["title"],
                "ProductNo2Description": self.test_data["products"][1]["description"],
                "ProductNo2Photo": self.test_data["products"][1]["image"],
                "ProductNo2AffiliateLink": self.test_data["products"][1]["link"],
                "ProductNo2Price": float(self.test_data["products"][1]["price"].replace("$", "").replace(",", "")),
                "ProductNo2Rating": self.test_data["products"][1]["rating"],
                "ProductNo2Reviews": self.test_data["products"][1]["total_reviews"],
                
                "ProductNo3Title": self.test_data["products"][2]["title"],
                "ProductNo3Description": self.test_data["products"][2]["description"],
                "ProductNo3Photo": self.test_data["products"][2]["image"],
                "ProductNo3AffiliateLink": self.test_data["products"][2]["link"],
                "ProductNo3Price": float(self.test_data["products"][2]["price"].replace("$", "").replace(",", "")),
                "ProductNo3Rating": self.test_data["products"][2]["rating"],
                "ProductNo3Reviews": self.test_data["products"][2]["total_reviews"],
                
                "ProductNo4Title": self.test_data["products"][3]["title"],
                "ProductNo4Description": self.test_data["products"][3]["description"],
                "ProductNo4Photo": self.test_data["products"][3]["image"],
                "ProductNo4AffiliateLink": self.test_data["products"][3]["link"],
                "ProductNo4Price": float(self.test_data["products"][3]["price"].replace("$", "").replace(",", "")),
                "ProductNo4Rating": self.test_data["products"][3]["rating"],
                "ProductNo4Reviews": self.test_data["products"][3]["total_reviews"],
                
                "ProductNo5Title": self.test_data["products"][4]["title"],
                "ProductNo5Description": self.test_data["products"][4]["description"],
                "ProductNo5Photo": self.test_data["products"][4]["image"],
                "ProductNo5AffiliateLink": self.test_data["products"][4]["link"],
                "ProductNo5Price": float(self.test_data["products"][4]["price"].replace("$", "").replace(",", "")),
                "ProductNo5Rating": self.test_data["products"][4]["rating"],
                "ProductNo5Reviews": self.test_data["products"][4]["total_reviews"],
                
                # Audio files in Airtable format (use actual paths, not file:// URLs)
                "IntroMp3": f"{self.temp_dir}/voice_intro.mp3",
                "OutroMp3": f"{self.temp_dir}/voice_outro.mp3",
                "Product1Mp3": f"{self.temp_dir}/voice_product1.mp3",
                "Product2Mp3": f"{self.temp_dir}/voice_product2.mp3",
                "Product3Mp3": f"{self.temp_dir}/voice_product3.mp3",
                "Product4Mp3": f"{self.temp_dir}/voice_product4.mp3",
                "Product5Mp3": f"{self.temp_dir}/voice_product5.mp3",
                
                # Scripts
                "IntroScript": self.test_data["scripts"]["intro"],
                "OutroScript": self.test_data["scripts"]["outro"],
                "Product1Script": self.test_data["scripts"]["product1"],
                "Product2Script": self.test_data["scripts"]["product2"],
                "Product3Script": self.test_data["scripts"]["product3"],
                "Product4Script": self.test_data["scripts"]["product4"],
                "Product5Script": self.test_data["scripts"]["product5"],
                
                # Images
                "IntroPhoto": self.test_data["images"]["intro"],
                "OutroPhoto": self.test_data["images"]["outro"]
            }
            
            # Generate video
            logger.info("🎬 Calling Remotion to render test video...")
            
            # Save the test data for debugging
            import json
            debug_file = "/tmp/test_remotion_data.json"
            with open(debug_file, 'w') as f:
                json.dump(remotion_data, f, indent=2)
            logger.info(f"📝 Saved test data to: {debug_file}")
            
            result = await generator.production_run_video_creation(
                record={"fields": remotion_data},
                config={}
            )
            
            if result.get('success') and result.get('video_path'):
                # Copy video to a persistent location
                import shutil
                output_path = "/tmp/test_video_output.mp4"
                shutil.copy2(result['video_path'], output_path)
                logger.info(f"📹 Video copied to: {output_path}")
                return output_path
            else:
                logger.error(f"Remotion generation failed: {result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error in Remotion test: {e}")
            return None

async def main():
    """Main entry point for test workflow"""
    runner = TestWorkflowRunner()
    await runner.run()

if __name__ == "__main__":
    asyncio.run(main())