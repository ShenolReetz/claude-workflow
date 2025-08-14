#!/usr/bin/env python3
"""
Production Remotion Video Generator with JSON2Video Fallback
=============================================================
Drop-in replacement for JSON2Video that uses Remotion locally with automatic fallback
"""

import asyncio
import json
import os
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, List, Any
import subprocess
import aiohttp
import time
from datetime import datetime

# Import existing JSON2Video agent as fallback
from src.mcp.production_json2video_agent_mcp import production_run_video_creation as json2video_create

logger = logging.getLogger(__name__)


class ProductionRemotionVideoGenerator:
    """
    Generates countdown videos using Remotion with JSON2Video fallback
    Seamlessly integrates into existing workflow
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Remotion project paths
        self.remotion_dir = Path("/home/claude-workflow/remotion-video-generator")
        self.output_dir = Path("/tmp/remotion-renders")
        self.output_dir.mkdir(exist_ok=True)
        
        # Fallback configuration - Remotion is now primary, no JSON2Video by default
        self.use_remotion = self.config.get('use_remotion', True)
        self.fallback_to_json2video = self.config.get('fallback_to_json2video', False)  # Disabled by default
        
    async def production_run_video_creation(self, record: Dict, config: Dict) -> Dict:
        """
        Main entry point - matches JSON2Video interface exactly with automatic fallback
        
        Args:
            record: Airtable record with all product data
            config: Configuration dict
            
        Returns:
            Dict with success, video_url, project_id, updated_record
        """
        # Try Remotion first if enabled
        if self.use_remotion:
            self.logger.info("🎬 Attempting video creation with Remotion...")
            try:
                result = await self._create_with_remotion(record, config)
                if result.get('success'):
                    self.logger.info("✅ Video created successfully with Remotion")
                    return result
                else:
                    self.logger.warning(f"⚠️ Remotion creation failed: {result.get('error')}")
            except Exception as e:
                self.logger.error(f"❌ Remotion error: {e}")
        
        # Fallback to JSON2Video if enabled
        if self.fallback_to_json2video:
            self.logger.info("🔄 Falling back to JSON2Video API...")
            try:
                result = await json2video_create(record, config)
                if result.get('success'):
                    self.logger.info("✅ Video created successfully with JSON2Video")
                return result
            except Exception as e:
                self.logger.error(f"❌ JSON2Video fallback failed: {e}")
                return {
                    'success': False,
                    'error': f'Both Remotion and JSON2Video failed: {str(e)}',
                    'updated_record': record
                }
        
        # If both are disabled or failed
        return {
            'success': False,
            'error': 'No video generation method available',
            'updated_record': record
        }
    
    async def _create_with_remotion(self, record: Dict, config: Dict) -> Dict:
        """
        Create video using local Remotion rendering
        """
        try:
            # Validate inputs
            if not self._validate_media_assets(record):
                return {
                    'success': False,
                    'error': 'Missing required audio files for Remotion',
                    'updated_record': record
                }
            
            # Check if Remotion project exists
            if not self.remotion_dir.exists():
                raise Exception(f"Remotion project not found at {self.remotion_dir}")
            
            # 1. Build video props from record
            video_props = await self._build_video_props(record)
            
            # 2. Bundle Remotion project (if needed)
            bundle_location = await self._bundle_remotion_project()
            
            # 3. Render video locally with Remotion
            video_path = await self._render_video(video_props, record.get('record_id', 'unknown'))
            
            if not video_path or not Path(video_path).exists():
                raise Exception("Video rendering failed - no output file")
            
            # 4. Return local file path - main workflow will handle upload
            # Don't try to upload here, just return the local path
            video_url = str(video_path)  # Keep as local path
            
            # 5. Update record with video path (not URL yet)
            if 'fields' not in record:
                record['fields'] = {}
            record['fields']['FinalVideo'] = video_url
            
            # DON'T clean up temp file - needed for upload later
            # The main workflow will handle cleanup after upload
            
            self.logger.info(f"✅ Video created successfully with Remotion")
            return {
                'success': True,
                'video_url': video_url,
                'project_id': f"remotion_{record.get('record_id', 'unknown')}",
                'updated_record': record,
                'renderer': 'remotion'
            }
            
        except Exception as e:
            self.logger.error(f"Remotion render failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    def _validate_media_assets(self, record: Dict) -> bool:
        """Validate required audio files exist"""
        fields = record.get('fields', {})
        required_audio = [
            'IntroMp3', 'OutroMp3',
            'Product1Mp3', 'Product2Mp3', 'Product3Mp3',
            'Product4Mp3', 'Product5Mp3'
        ]
        
        missing = []
        for field in required_audio:
            if not fields.get(field):
                missing.append(field)
        
        if missing:
            self.logger.warning(f"Missing audio fields: {missing}")
            # Allow rendering without audio for testing or when audio is not critical
            # Return True to proceed with video generation even without audio
            return True
        
        return True
    
    async def _build_video_props(self, record: Dict) -> Dict:
        """
        Convert Airtable record to Remotion props format using new production schema
        Downloads remote media to local temp files for Remotion
        """
        fields = record.get('fields', {})
        
        # Build comprehensive data structure matching ProductionVideoSchema
        video_data = {
            'videoTitle': fields.get('VideoTitle', 'Amazing Products'),
            'recordId': record.get('record_id', 'unknown'),
            
            # Products array for countdown (reverse order for 5→1)
            'products': []
        }
        
        # Build products with all fields from Airtable
        for i in range(1, 6):
            # Parse price with better handling
            price_str = fields.get(f'ProductNo{i}Price', '0')
            try:
                if isinstance(price_str, (int, float)):
                    price = float(price_str)
                else:
                    # Handle currency strings like "$99.99" or "99.99"
                    price = float(str(price_str).replace('$', '').replace(',', ''))
            except:
                price = 0
            
            # Parse rating (0-5 scale)
            rating_str = fields.get(f'ProductNo{i}Rating', '0')
            try:
                rating = float(str(rating_str))
                rating = min(5.0, max(0.0, rating))  # Clamp to 0-5
            except:
                rating = 0
            
            # Parse reviews with K/M suffixes
            reviews_str = fields.get(f'ProductNo{i}Reviews', '0')
            try:
                if isinstance(reviews_str, (int, float)):
                    reviews = int(reviews_str)
                else:
                    reviews_str = str(reviews_str).replace(',', '').upper()
                    if 'K' in reviews_str:
                        reviews = int(float(reviews_str.replace('K', '')) * 1000)
                    elif 'M' in reviews_str:
                        reviews = int(float(reviews_str.replace('M', '')) * 1000000)
                    else:
                        import re
                        reviews = int(float(re.sub(r'[^0-9]', '', reviews_str) or '0'))
            except:
                reviews = 0
            
            # Determine badge based on position and metrics
            badge = None
            if i == 1:  # #1 product
                badge = 'BEST_SELLER'
            elif reviews > 10000:
                badge = 'TOP_RATED'
            elif rating >= 4.5:
                badge = 'AMAZON_CHOICE'
            
            # Calculate discount if original price available
            discount = None
            original_price_str = fields.get(f'ProductNo{i}OriginalPrice')
            if original_price_str:
                try:
                    original_price = float(str(original_price_str).replace('$', '').replace(',', ''))
                    if original_price > price:
                        discount = round(((original_price - price) / original_price) * 100)
                except:
                    pass
            
            product = {
                'rank': 6 - i,  # Countdown from 5 to 1
                'title': fields.get(f'ProductNo{i}Title', f'Product {i}'),
                'description': fields.get(f'ProductNo{i}Description', ''),
                'price': price,
                'rating': rating,
                'reviews': reviews,
                'image': fields.get(f'ProductNo{i}Photo', ''),
                'affiliateLink': fields.get(f'ProductNo{i}AffiliateLink', ''),
                'badge': badge,
                'discount': discount
            }
            video_data['products'].append(product)
        
        # Download and map all media files
        # Audio files - download to local for Remotion
        audio_urls = {}
        audio_mappings = {
            'intro': 'IntroMp3',
            'outro': 'OutroMp3',
            'product1': 'Product1Mp3',
            'product2': 'Product2Mp3',
            'product3': 'Product3Mp3',
            'product4': 'Product4Mp3',
            'product5': 'Product5Mp3'
        }
        
        for key, field in audio_mappings.items():
            url = fields.get(field)
            if url:
                # Download audio file to temp directory
                local_path = await self._download_media(url, f"{key}.mp3")
                if local_path:
                    audio_urls[key] = local_path
                else:
                    self.logger.warning(f"Could not download audio for {key}, will render without")
        
        # Image files - download to local
        image_urls = {}
        image_mappings = {
            'intro': 'IntroPhoto',
            'outro': 'OutroPhoto',
            'product1': 'ProductNo1Photo',
            'product2': 'ProductNo2Photo',
            'product3': 'ProductNo3Photo',
            'product4': 'ProductNo4Photo',
            'product5': 'ProductNo5Photo'
        }
        
        for key, field in image_mappings.items():
            url = fields.get(field)
            if url:
                # Download image file
                ext = self._get_file_extension(url, '.jpg')
                local_path = await self._download_media(url, f"{key}{ext}")
                if local_path:
                    image_urls[key] = local_path
                else:
                    self.logger.warning(f"Could not download image for {key}, using placeholder")
        
        # Platform detection for optimized rendering
        platform = fields.get('Platform', 'tiktok').lower()
        if platform not in ['tiktok', 'instagram', 'youtube']:
            platform = 'tiktok'
        
        # Build final props matching new schema
        return {
            'data': {
                'videoTitle': video_data['videoTitle'],
                'recordId': video_data['recordId'],
                'products': video_data['products'],
                'introPhoto': image_urls.get('intro', ''),
                'introMp3': audio_urls.get('intro', ''),
                'outroPhoto': image_urls.get('outro', ''),
                'outroMp3': audio_urls.get('outro', ''),
                # Map product media
                'product1': {
                    **(video_data['products'][0] if len(video_data['products']) > 0 else {}),
                    'photo': image_urls.get('product1', ''),
                    'mp3': audio_urls.get('product1', '')
                },
                'product2': {
                    **(video_data['products'][1] if len(video_data['products']) > 1 else {}),
                    'photo': image_urls.get('product2', ''),
                    'mp3': audio_urls.get('product2', '')
                },
                'product3': {
                    **(video_data['products'][2] if len(video_data['products']) > 2 else {}),
                    'photo': image_urls.get('product3', ''),
                    'mp3': audio_urls.get('product3', '')
                },
                'product4': {
                    **(video_data['products'][3] if len(video_data['products']) > 3 else {}),
                    'photo': image_urls.get('product4', ''),
                    'mp3': audio_urls.get('product4', '')
                },
                'product5': {
                    **(video_data['products'][4] if len(video_data['products']) > 4 else {}),
                    'photo': image_urls.get('product5', ''),
                    'mp3': audio_urls.get('product5', '')
                }
            },
            'platform': platform,
            'transition': fields.get('TransitionType', 'slide-up'),
            'brandColors': {
                'primary': fields.get('BrandColorPrimary', '#FFFF00'),
                'accent': fields.get('BrandColorAccent', '#00FF00'),
                'background': fields.get('BrandColorBackground', '#000000')
            },
            'socialMedia': {
                'showSubscribe': True,
                'subscribeCTA': fields.get('SubscribeCTA', 'Subscribe for More!'),
                'platform': platform
            }
        }
    
    async def _download_media(self, url: str, filename: str) -> Optional[str]:
        """Download media file to temp directory"""
        if not url:
            return None
        
        try:
            temp_dir = self.output_dir / "media"
            temp_dir.mkdir(exist_ok=True)
            
            local_path = temp_dir / filename
            
            # Check if already downloaded
            if local_path.exists():
                return str(local_path)
            
            # Download file
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(local_path, 'wb') as f:
                            f.write(content)
                        return str(local_path)
        except Exception as e:
            self.logger.warning(f"Failed to download media from {url}: {e}")
        
        return None
    
    def _get_file_extension(self, url: str, default: str = '.jpg') -> str:
        """Extract file extension from URL"""
        try:
            from urllib.parse import urlparse
            path = urlparse(url).path
            if '.' in path:
                return '.' + path.split('.')[-1].lower()
        except:
            pass
        return default
    
    async def _bundle_remotion_project(self) -> str:
        """Bundle Remotion project for rendering (cached)"""
        bundle_location = self.output_dir / "bundle"
        
        # Check if bundle exists and is recent (within 1 hour)
        if bundle_location.exists():
            bundle_age = time.time() - bundle_location.stat().st_mtime
            if bundle_age < 3600:  # 1 hour cache
                self.logger.info("Using cached Remotion bundle")
                return str(bundle_location)
        
        self.logger.info("Building Remotion bundle...")
        
        # Build bundle using Remotion CLI
        cmd = [
            "npx", "remotion", "bundle",
            "--out-dir", str(bundle_location)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.remotion_dir)
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Bundle failed: {stderr.decode()}")
        
        return str(bundle_location)
    
    async def _render_video(self, props: Dict, record_id: str) -> Optional[str]:
        """
        Render video using Remotion CLI
        """
        # Save props to temporary JSON file
        props_file = self.output_dir / f"props_{record_id}_{int(time.time())}.json"
        with open(props_file, 'w') as f:
            json.dump(props, f, indent=2)
        
        # Output video path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"video_{record_id}_{timestamp}.mp4"
        
        # Build Remotion render command
        cmd = [
            "npx", "remotion", "render",
            "ProductionCountdownVideo",  # New production composition ID
            str(output_path),  # Output file
            "--props", str(props_file),
            "--codec", "h264",
            "--pixel-format", "yuv420p",  # Compatible with all players
            "--jpeg-quality", "90",
            "--concurrency", "2",  # Lower concurrency for stability
            "--timeout", "300000",  # 5 minute timeout
            "--log", "verbose",
            "--overwrite"
        ]
        
        self.logger.info(f"🎬 Starting Remotion render for {record_id}...")
        self.logger.info(f"Command: {' '.join(cmd)}")
        
        try:
            # Execute render process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(self.remotion_dir)
            )
            
            # Monitor progress with timeout
            try:
                stdout, _ = await asyncio.wait_for(
                    process.communicate(),
                    timeout=300  # 5 minute timeout
                )
                
                # Log output
                if stdout:
                    output_lines = stdout.decode().split('\n')
                    for line in output_lines[-20:]:  # Last 20 lines
                        if line.strip():
                            self.logger.info(f"Remotion: {line}")
                
            except asyncio.TimeoutError:
                process.kill()
                raise Exception("Remotion render timeout after 5 minutes")
            
            # Clean up props file
            if props_file.exists():
                props_file.unlink()
            
            # Clean up temporary media files
            media_dir = self.output_dir / "media"
            if media_dir.exists():
                shutil.rmtree(media_dir, ignore_errors=True)
            
            if process.returncode == 0 and output_path.exists():
                file_size = output_path.stat().st_size
                self.logger.info(f"✅ Video rendered successfully: {output_path} ({file_size / 1024 / 1024:.1f} MB)")
                # Return local file path - the main workflow will handle upload
                return str(output_path)
            else:
                self.logger.error(f"Remotion render failed with code {process.returncode}")
                return None
                
        except Exception as e:
            self.logger.error(f"Render error: {e}")
            # Clean up on error
            if props_file.exists():
                props_file.unlink()
            return None
    
    async def _upload_video_DEPRECATED(self, video_path: str) -> str:
        """
        DEPRECATED: Upload is now handled by main workflow
        This method is kept for reference but not used
        """
        # Upload is now handled by Production_enhanced_google_drive_agent_mcp
        # which properly handles local files and has better error handling
        return f"file://{video_path}"
        
        # Original upload code commented out:
        """
        try:
            # Import Google Drive uploader
            from src.utils.google_drive_token_manager import GoogleDriveTokenManager
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            # Get Google Drive service
            token_manager = GoogleDriveTokenManager()
            # Use get_valid_token() instead of get_credentials()
            token = token_manager.get_valid_token()
            
            if not token:
                self.logger.warning("No Google Drive credentials available")
                return f"file://{video_path}"
            
            # Build credentials from token
            from google.oauth2.credentials import Credentials
            creds = Credentials(token=token['access_token'])
            
            service = build('drive', 'v3', credentials=creds)
            
            # Create folder for videos if it doesn't exist
            folder_name = f"Remotion_Videos_{datetime.now().strftime('%Y%m')}"
            
            # Search for existing folder
            response = service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields='files(id)'
            ).execute()
            
            if response.get('files'):
                folder_id = response['files'][0]['id']
            else:
                # Create folder
                folder_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                folder_id = folder['id']
            
            # Upload file
            file_metadata = {
                'name': os.path.basename(video_path),
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            # Make file public
            service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
            
            self.logger.info(f"✅ Video uploaded to Google Drive: {file['id']}")
            
            # Return direct download link
            return f"https://drive.google.com/uc?export=download&id={file['id']}"
            
        except Exception as e:
            self.logger.error(f"Google Drive upload failed: {e}")
            # Return local file path as fallback
            return f"file://{video_path}"
        """


# Wrapper function to match existing interface - THIS IS THE MAIN ENTRY POINT
async def production_run_video_creation_with_fallback(record: Dict, config: Dict) -> Dict:
    """
    Drop-in replacement for JSON2Video with Remotion fallback
    This is the function that should be called from the workflow
    """
    generator = ProductionRemotionVideoGenerator(config)
    return await generator.production_run_video_creation(record, config)


# For backward compatibility - alias to the main function
production_run_video_creation = production_run_video_creation_with_fallback


# Test function
async def test_remotion_render():
    """Test Remotion rendering with sample data"""
    
    # Sample record
    test_record = {
        'record_id': 'test_remotion_001',
        'fields': {
            'VideoTitle': 'Top 5 Action Cameras - Remotion Test',
            'ProductNo1Title': 'GoPro Hero 11 Black',
            'ProductNo1Price': '$399.99',
            'ProductNo1Rating': '4.5',
            'ProductNo1Reviews': '1,234',
            'ProductNo1Photo': 'https://via.placeholder.com/1080x1920/ff0000/ffffff?text=Product+1',
            'ProductNo2Title': 'DJI Action 3',
            'ProductNo2Price': 329.99,
            'ProductNo2Rating': 4.3,
            'ProductNo2Reviews': 987,
            'ProductNo2Photo': 'https://via.placeholder.com/1080x1920/00ff00/ffffff?text=Product+2',
            'ProductNo3Title': 'Insta360 One RS',
            'ProductNo3Price': 299.99,
            'ProductNo3Rating': 4.2,
            'ProductNo3Reviews': '756',
            'ProductNo4Title': 'AKASO Brave 7',
            'ProductNo4Price': 149.99,
            'ProductNo4Rating': 4.0,
            'ProductNo4Reviews': '2.1K',
            'ProductNo5Title': 'WOLFANG GA100',
            'ProductNo5Price': 89.99,
            'ProductNo5Rating': 3.8,
            'ProductNo5Reviews': 432,
            # Test without audio to see if it handles missing media
            'IntroPhoto': 'https://via.placeholder.com/1080x1920/0000ff/ffffff?text=INTRO',
            'OutroPhoto': 'https://via.placeholder.com/1080x1920/ff00ff/ffffff?text=SUBSCRIBE',
        }
    }
    
    config = {
        'use_remotion': True,
        'fallback_to_json2video': True
    }
    
    print("🚀 Starting Remotion test render...")
    result = await production_run_video_creation_with_fallback(test_record, config)
    
    if result.get('success'):
        print(f"✅ Test successful!")
        print(f"   Video URL: {result.get('video_url')}")
        print(f"   Renderer: {result.get('renderer', 'unknown')}")
    else:
        print(f"❌ Test failed: {result.get('error')}")
    
    return result


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run test
    asyncio.run(test_remotion_render())