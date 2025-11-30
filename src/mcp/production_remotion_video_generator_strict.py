#!/usr/bin/env python3
"""
Production Remotion Video Generator - STRICT Version
====================================================
This version REQUIRES all media files to be present locally before rendering.
No rendering happens if ANY file is missing.
"""

import asyncio
import json
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import subprocess
import time
from datetime import datetime

# Import dual storage manager
from src.utils.dual_storage_manager import get_storage_manager

logger = logging.getLogger(__name__)


class StrictRemotionVideoGenerator:
    """
    Strict version that validates ALL media is present before rendering
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage manager
        self.storage_manager = get_storage_manager(config)
        
        # Remotion project paths
        self.remotion_dir = Path("/home/claude-workflow/remotion-video-generator")
        self.output_dir = Path("/home/claude-workflow/media_storage/videos")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    async def production_run_video_creation(self, record: Dict, config: Dict) -> Dict:
        """
        Main entry point with STRICT validation
        """
        record_id = record.get('record_id', 'unknown')
        self.logger.info(f"🎬 Starting STRICT Remotion video creation for {record_id}")
        
        try:
            # Step 1: Define ALL required media files
            required_files = self._get_required_files(record)
            
            # Step 2: STRICT validation - download missing files if needed
            self.logger.info("🔍 Validating all media files...")
            all_present, missing_files = await self.storage_manager.validate_all_media_present(
                record=record,
                required_files=required_files
            )
            
            # Step 3: STOP if ANY file is missing
            if not all_present:
                error_msg = f"Cannot render video - missing files: {', '.join(missing_files)}"
                self.logger.error(f"❌ {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'missing_files': missing_files,
                    'updated_record': record
                }
            
            self.logger.info("✅ All media files validated successfully")
            
            # Step 4: Copy images to Remotion public folder
            public_dir = self.remotion_dir / "public"
            public_dir.mkdir(exist_ok=True, parents=True)
            self.logger.info("📁 Copying images to Remotion public folder...")
            
            # Copy all images to public folder
            for file_info in required_files:
                if file_info['media_type'] == 'image':
                    source_path = self.storage_manager.get_local_path(
                        record_id,
                        file_info['media_type'],
                        file_info['filename']
                    )
                    if source_path and Path(source_path).exists():
                        dest_path = public_dir / file_info['filename']
                        shutil.copy2(source_path, dest_path)
                        self.logger.info(f"  ✅ Copied {file_info['filename']}")
            
            # Step 5: Build video props with relative paths for images
            video_props = await self._build_video_props_local(record, required_files, use_public_paths=True)
            
            # Step 6: Check Remotion project exists
            if not self.remotion_dir.exists():
                raise Exception(f"Remotion project not found at {self.remotion_dir}")
            
            # Step 6: Bundle Remotion project (if needed)
            bundle_location = await self._bundle_remotion_project()
            
            # Step 7: Render video locally with Remotion
            self.logger.info("🎥 Starting Remotion render...")
            video_path = await self._render_video(video_props, record_id)
            
            if not video_path or not Path(video_path).exists():
                raise Exception("Video rendering failed - no output file")
            
            # Step 8: Verify output video
            video_size = Path(video_path).stat().st_size
            if video_size < 100000:  # Less than 100KB is suspicious
                raise Exception(f"Video file too small ({video_size} bytes) - rendering may have failed")
            
            self.logger.info(f"✅ Video rendered successfully: {video_size / 1024 / 1024:.2f} MB")
            
            # Step 9: Optionally upload to Google Drive
            drive_url = None
            if self.config.get('upload_video_to_drive', True):
                try:
                    with open(video_path, 'rb') as f:
                        video_content = f.read()
                    
                    result = await self.storage_manager.save_media(
                        content=video_content,
                        filename=f"countdown_{record_id}.mp4",
                        media_type="video",
                        record_id=record_id,
                        upload_to_drive=True
                    )
                    
                    if result.get('drive_url'):
                        drive_url = result['drive_url']
                        self.logger.info(f"☁️ Video uploaded to Drive: {drive_url}")
                except Exception as e:
                    self.logger.warning(f"Drive upload failed (video saved locally): {e}")
            
            # Step 10: Update record with paths
            if 'fields' not in record:
                record['fields'] = {}
            
            # Use Drive URL if available, otherwise local path
            record['fields']['FinalVideo'] = drive_url or str(video_path)
            
            return {
                'success': True,
                'video_url': drive_url or str(video_path),
                'local_path': str(video_path),
                'project_id': f"remotion_{record_id}",
                'updated_record': record,
                'renderer': 'remotion_strict',
                'video_size_mb': round(video_size / 1024 / 1024, 2)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Remotion render failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    def _get_required_files(self, record: Dict) -> List[Dict]:
        """
        Define ALL required media files for the video
        """
        required = []
        
        # Audio files (REQUIRED)
        audio_files = [
            ('IntroMp3', 'intro.mp3'),
            ('OutroMp3', 'outro.mp3'),
            ('Product1Mp3', 'product1.mp3'),
            ('Product2Mp3', 'product2.mp3'),
            ('Product3Mp3', 'product3.mp3'),
            ('Product4Mp3', 'product4.mp3'),
            ('Product5Mp3', 'product5.mp3')
        ]
        
        for field, filename in audio_files:
            required.append({
                'field': field,
                'media_type': 'audio',
                'filename': filename
            })
        
        # Image files (REQUIRED)
        image_files = [
            ('IntroPhoto', 'intro.jpg'),
            ('OutroPhoto', 'outro.jpg'),
            ('ProductNo1Photo', 'product1.jpg'),
            ('ProductNo2Photo', 'product2.jpg'),
            ('ProductNo3Photo', 'product3.jpg'),
            ('ProductNo4Photo', 'product4.jpg'),
            ('ProductNo5Photo', 'product5.jpg')
        ]
        
        for field, filename in image_files:
            required.append({
                'field': field,
                'media_type': 'image',
                'filename': filename
            })
        
        return required
    
    async def _build_video_props_local(self, record: Dict, required_files: List[Dict], use_public_paths: bool = False) -> Dict:
        """
        Build video props using LOCAL file paths only
        """
        fields = record.get('fields', {})
        record_id = record.get('record_id', 'unknown')
        
        # Build products data
        products = []
        for i in range(1, 6):
            # Parse product data
            price = self._parse_price(fields.get(f'ProductNo{i}Price', '0'))
            rating = self._parse_rating(fields.get(f'ProductNo{i}Rating', '0'))
            reviews = self._parse_reviews(fields.get(f'ProductNo{i}Reviews', '0'))
            
            # Determine badge
            badge = self._determine_badge(i, rating, reviews)
            
            # Calculate discount
            discount = self._calculate_discount(
                price,
                fields.get(f'ProductNo{i}OriginalPrice')
            )
            
            product = {
                'rank': 6 - i,  # Countdown from 5 to 1
                'title': fields.get(f'ProductNo{i}Title', f'Product {i}'),
                'description': fields.get(f'ProductNo{i}Description', ''),
                'price': price,
                'rating': rating,
                'reviews': reviews,
                'image': f"/product{i}.jpg" if use_public_paths else self.storage_manager.get_local_path(
                    record_id, 'image', f'product{i}.jpg'
                ),
                'affiliateLink': fields.get(f'ProductNo{i}AffiliateLink', ''),
                'badge': badge,
                'discount': discount
            }
            products.append(product)
        
        # Get all local paths
        local_paths = {}
        for file_info in required_files:
            if use_public_paths and file_info['media_type'] == 'image':
                # Use relative path for images in public folder
                local_paths[file_info['filename']] = f"/{file_info['filename']}"
            else:
                # Use full path for audio files
                local_path = self.storage_manager.get_local_path(
                    record_id,
                    file_info['media_type'],
                    file_info['filename']
                )
                if local_path:
                    local_paths[file_info['filename']] = local_path
        
        # Build final props
        return {
            'data': {
                'videoTitle': fields.get('VideoTitle', 'Amazing Products'),
                'recordId': record_id,
                'products': products,
                'introPhoto': local_paths.get('intro.jpg', ''),
                'introMp3': local_paths.get('intro.mp3', ''),
                'outroPhoto': local_paths.get('outro.jpg', ''),
                'outroMp3': local_paths.get('outro.mp3', ''),
                'product1': {
                    **products[0],
                    'photo': local_paths.get('product1.jpg', ''),
                    'mp3': local_paths.get('product1.mp3', '')
                },
                'product2': {
                    **products[1],
                    'photo': local_paths.get('product2.jpg', ''),
                    'mp3': local_paths.get('product2.mp3', '')
                },
                'product3': {
                    **products[2],
                    'photo': local_paths.get('product3.jpg', ''),
                    'mp3': local_paths.get('product3.mp3', '')
                },
                'product4': {
                    **products[3],
                    'photo': local_paths.get('product4.jpg', ''),
                    'mp3': local_paths.get('product4.mp3', '')
                },
                'product5': {
                    **products[4],
                    'photo': local_paths.get('product5.jpg', ''),
                    'mp3': local_paths.get('product5.mp3', '')
                }
            },
            'platform': fields.get('Platform', 'tiktok').lower(),
            'transition': fields.get('TransitionType', 'slide-up'),
            'brandColors': {
                'primary': fields.get('BrandColorPrimary', '#FFFF00'),
                'accent': fields.get('BrandColorAccent', '#00FF00'),
                'background': fields.get('BrandColorBackground', '#000000')
            }
        }
    
    def _parse_price(self, price_str) -> float:
        """Parse price from various formats"""
        try:
            if isinstance(price_str, (int, float)):
                return float(price_str)
            else:
                return float(str(price_str).replace('$', '').replace(',', ''))
        except:
            return 0
    
    def _parse_rating(self, rating_str) -> float:
        """Parse rating and clamp to 0-5"""
        try:
            rating = float(str(rating_str))
            return min(5.0, max(0.0, rating))
        except:
            return 0
    
    def _parse_reviews(self, reviews_str) -> int:
        """Parse reviews with K/M suffix support"""
        try:
            if isinstance(reviews_str, (int, float)):
                return int(reviews_str)
            else:
                reviews_str = str(reviews_str).replace(',', '').upper()
                if 'K' in reviews_str:
                    return int(float(reviews_str.replace('K', '')) * 1000)
                elif 'M' in reviews_str:
                    return int(float(reviews_str.replace('M', '')) * 1000000)
                else:
                    import re
                    return int(float(re.sub(r'[^0-9]', '', reviews_str) or '0'))
        except:
            return 0
    
    def _determine_badge(self, position: int, rating: float, reviews: int) -> Optional[str]:
        """Determine product badge"""
        if position == 1:
            return 'BEST_SELLER'
        elif reviews > 10000:
            return 'TOP_RATED'
        elif rating >= 4.5:
            return 'AMAZON_CHOICE'
        return None
    
    def _calculate_discount(self, price: float, original_price_str) -> Optional[int]:
        """Calculate discount percentage"""
        if not original_price_str:
            return None
        try:
            original_price = float(str(original_price_str).replace('$', '').replace(',', ''))
            if original_price > price:
                return round(((original_price - price) / original_price) * 100)
        except:
            pass
        return None
    
    async def _bundle_remotion_project(self) -> str:
        """Bundle Remotion project if needed"""
        bundle_path = self.remotion_dir / "bundle"
        
        # Check if bundle exists and is recent (within 1 hour)
        if bundle_path.exists():
            bundle_age = time.time() - bundle_path.stat().st_mtime
            if bundle_age < 3600:  # 1 hour
                self.logger.info("Using existing Remotion bundle")
                return str(bundle_path)
        
        self.logger.info("Building Remotion bundle...")
        
        # Run build command
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=self.remotion_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Bundle failed: {result.stderr}")
        
        return str(bundle_path)
    
    async def _render_video(self, props: Dict, record_id: str) -> str:
        """Render video with Remotion CLI"""
        try:
            # Output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"countdown_{record_id}_{timestamp}.mp4"
            output_path = self.output_dir / output_filename
            
            # Write props to temp file
            props_file = self.output_dir / f"props_{record_id}.json"
            with open(props_file, 'w') as f:
                json.dump(props, f, indent=2)
            
            # Debug: Log props structure
            self.logger.info(f"Props file created at: {props_file}")
            self.logger.info(f"Image URLs in props: intro={props.get('data', {}).get('introPhoto', 'MISSING')[:50]}...")
            self.logger.info(f"Product1 photo: {props.get('data', {}).get('product1', {}).get('photo', 'MISSING')[:50]}...")
            
            self.logger.info(f"Rendering video with Remotion CLI...")
            
            # Remotion render command
            cmd = [
                "npx", "remotion", "render",
                "WowCountdownVideo",  # Composition ID
                str(output_path),
                "--props", str(props_file),
                "--codec", "h264",
                "--image-format", "jpeg",
                "--jpeg-quality", "90",
                "--scale", "1",
                "--concurrency", "2",
                "--timeout", "30000"
            ]
            
            # Run render
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=self.remotion_dir,
                capture_output=True,
                text=True
            )
            
            render_time = time.time() - start_time
            
            # Debug: Keep props file for inspection
            # if props_file.exists():
            #     props_file.unlink()
            self.logger.info(f"Props file kept at: {props_file} for debugging")
            
            if result.returncode != 0:
                raise Exception(f"Render failed: {result.stderr}")
            
            if not output_path.exists():
                raise Exception("Output video not created")
            
            self.logger.info(f"✅ Video rendered in {render_time:.1f} seconds: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Render error: {e}")
            raise


# Export the strict version as the default
production_run_video_creation = StrictRemotionVideoGenerator().production_run_video_creation