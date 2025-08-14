#!/usr/bin/env python3
"""
Remotion Video Generator for Production Workflow
================================================
Drop-in replacement for JSON2Video using local Remotion rendering
"""

import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional
import subprocess
import logging

class ProductionRemotionVideoGenerator:
    """
    Generates countdown videos using Remotion instead of JSON2Video
    Maintains exact same interface as JSON2Video for seamless integration
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.template_dir = Path("/home/claude-workflow/remotion-countdown")
        self.output_dir = Path("/tmp/remotion-renders")
        self.output_dir.mkdir(exist_ok=True)
        
    async def production_run_video_creation(self, record: Dict, config: Dict) -> Dict:
        """
        Main entry point - matches JSON2Video interface exactly
        
        Args:
            record: Airtable record with all product data
            config: Configuration dict
            
        Returns:
            Dict with success, video_url, project_id, updated_record
        """
        try:
            # Validate inputs
            if not self._validate_media_assets(record):
                return {
                    'success': False,
                    'error': 'Missing required audio files',
                    'updated_record': record
                }
            
            # 1. Prepare video props from record
            video_props = self._build_video_props(record)
            
            # 2. Render video locally with Remotion
            video_path = await self._render_video(video_props, record['record_id'])
            
            # 3. Upload to Google Drive or S3
            video_url = await self._upload_video(video_path)
            
            # 4. Update record with video URL
            record['fields']['FinalVideo'] = video_url
            
            # Clean up temp file
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
            
            return {
                'success': True,
                'video_url': video_url,
                'project_id': f"remotion_{record['record_id']}",
                'updated_record': record
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
        
        for field in required_audio:
            if not fields.get(field):
                self.logger.error(f"Missing required audio: {field}")
                return False
        return True
    
    def _build_video_props(self, record: Dict) -> Dict:
        """
        Convert Airtable record to Remotion props format
        """
        fields = record.get('fields', {})
        
        # Build products array for countdown
        products = []
        for i in range(1, 6):
            product = {
                'rank': 6 - i,  # Countdown from 5 to 1
                'title': fields.get(f'ProductNo{i}Title', f'Product {i}'),
                'description': fields.get(f'ProductNo{i}Description', ''),
                'price': fields.get(f'ProductNo{i}Price', 0),
                'rating': fields.get(f'ProductNo{i}Rating', 0),
                'reviews': fields.get(f'ProductNo{i}Reviews', 0),
                'image': fields.get(f'ProductNo{i}Photo', ''),
                'affiliateLink': fields.get(f'ProductNo{i}AffiliateLink', '')
            }
            products.append(product)
        
        # Audio URLs mapping
        audio_urls = {
            'intro': fields.get('IntroMp3', ''),
            'outro': fields.get('OutroMp3', ''),
            'product1': fields.get('Product1Mp3', ''),
            'product2': fields.get('Product2Mp3', ''),
            'product3': fields.get('Product3Mp3', ''),
            'product4': fields.get('Product4Mp3', ''),
            'product5': fields.get('Product5Mp3', '')
        }
        
        # Image URLs mapping
        image_urls = {
            'intro': fields.get('IntroPhoto', 'https://via.placeholder.com/1080x1920/2a2a2a/ffff00?text=INTRO'),
            'outro': fields.get('OutroPhoto', 'https://via.placeholder.com/1080x1920/0a0a0a/ffff00?text=SUBSCRIBE'),
            'product1': fields.get('ProductNo1Photo', ''),
            'product2': fields.get('ProductNo2Photo', ''),
            'product3': fields.get('ProductNo3Photo', ''),
            'product4': fields.get('ProductNo4Photo', ''),
            'product5': fields.get('ProductNo5Photo', '')
        }
        
        return {
            'title': fields.get('VideoTitle', 'Amazing Products'),
            'products': products,
            'audioUrls': audio_urls,
            'imageUrls': image_urls,
            'duration': 55,  # Total video duration in seconds
            'fps': 30,
            'resolution': {
                'width': 1080,
                'height': 1920
            }
        }
    
    async def _render_video(self, props: Dict, record_id: str) -> str:
        """
        Render video using Remotion CLI
        """
        # Save props to temporary JSON file
        props_file = self.output_dir / f"props_{record_id}.json"
        with open(props_file, 'w') as f:
            json.dump(props, f, indent=2)
        
        # Output video path
        output_path = self.output_dir / f"video_{record_id}.mp4"
        
        # Build Remotion render command
        cmd = [
            "npx", "remotion", "render",
            "CountdownVideo",  # Composition ID
            str(output_path),  # Output file
            "--props", str(props_file),
            "--codec", "h264",
            "--pixel-format", "yuv420p",  # Compatible with all players
            "--image-format", "jpeg",
            "--jpeg-quality", "90",
            "--scale", "1",  # 1080x1920 resolution
            "--concurrency", "4",  # Parallel frame rendering
            "--verbose",
            "--overwrite"
        ]
        
        self.logger.info(f"🎬 Starting Remotion render for {record_id}...")
        
        # Execute render process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.template_dir)
        )
        
        # Monitor progress
        async def read_stream(stream, prefix):
            while True:
                line = await stream.readline()
                if not line:
                    break
                line_text = line.decode().strip()
                if line_text:
                    self.logger.info(f"{prefix}: {line_text}")
        
        # Read both stdout and stderr
        await asyncio.gather(
            read_stream(process.stdout, "Remotion"),
            read_stream(process.stderr, "Remotion")
        )
        
        await process.wait()
        
        # Clean up props file
        if props_file.exists():
            props_file.unlink()
        
        if process.returncode == 0 and output_path.exists():
            self.logger.info(f"✅ Video rendered successfully: {output_path}")
            return str(output_path)
        else:
            raise Exception(f"Remotion render failed with code {process.returncode}")
    
    async def _upload_video(self, video_path: str) -> str:
        """
        Upload rendered video to storage (Google Drive or S3)
        Returns public URL
        """
        # For now, return local file URL
        # In production, implement Google Drive upload here
        
        try:
            # Import Google Drive uploader
            from src.utils.google_drive_token_manager import GoogleDriveTokenManager
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            
            # Get Google Drive service
            token_manager = GoogleDriveTokenManager()
            creds = token_manager.get_credentials()
            
            if creds:
                service = build('drive', 'v3', credentials=creds)
                
                # Upload file
                file_metadata = {
                    'name': os.path.basename(video_path),
                    'mimeType': 'video/mp4'
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
                return file.get('webContentLink', '')
                
        except Exception as e:
            self.logger.warning(f"Google Drive upload failed: {e}, using local file")
        
        # Fallback to local file URL
        return f"file://{video_path}"


# Wrapper function to match existing interface
async def production_run_video_creation(record: Dict, config: Dict) -> Dict:
    """
    Drop-in replacement for JSON2Video function
    """
    generator = ProductionRemotionVideoGenerator(config)
    return await generator.production_run_video_creation(record, config)


# Test function
async def test_remotion_render():
    """Test Remotion rendering with sample data"""
    
    # Sample record
    test_record = {
        'record_id': 'test_001',
        'fields': {
            'VideoTitle': 'Top 5 Action Cameras',
            'ProductNo1Title': 'GoPro Hero 11',
            'ProductNo1Price': 399.99,
            'ProductNo1Rating': 4.5,
            'ProductNo1Reviews': 1234,
            'ProductNo2Title': 'DJI Action 3',
            'ProductNo2Price': 329.99,
            'ProductNo2Rating': 4.3,
            'ProductNo2Reviews': 987,
            # Add audio URLs here
            'IntroMp3': 'https://example.com/intro.mp3',
            'OutroMp3': 'https://example.com/outro.mp3',
            'Product1Mp3': 'https://example.com/p1.mp3',
            'Product2Mp3': 'https://example.com/p2.mp3',
            'Product3Mp3': 'https://example.com/p3.mp3',
            'Product4Mp3': 'https://example.com/p4.mp3',
            'Product5Mp3': 'https://example.com/p5.mp3',
        }
    }
    
    config = {}
    
    result = await production_run_video_creation(test_record, config)
    print(f"Test result: {result}")
    
if __name__ == "__main__":
    asyncio.run(test_remotion_render())