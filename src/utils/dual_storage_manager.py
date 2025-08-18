#!/usr/bin/env python3
"""
Dual Storage Manager - Save files locally AND to Google Drive simultaneously
============================================================================
Ensures media files are always available locally for Remotion while maintaining
cloud backups for long-term storage.
"""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import logging
import aiofiles
import aiohttp
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DualStorageManager:
    """
    Manages dual storage strategy: Local + Google Drive
    All files are saved locally first, then uploaded to cloud asynchronously
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Local storage paths
        self.base_local_path = Path("/home/claude-workflow/media_storage")
        self.base_local_path.mkdir(exist_ok=True)
        
        # Organize by date for easy cleanup
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_path = self.base_local_path / today
        self.daily_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.audio_path = self.daily_path / "audio"
        self.audio_path.mkdir(exist_ok=True)
        self.images_path = self.daily_path / "images"
        self.images_path.mkdir(exist_ok=True)
        self.videos_path = self.daily_path / "videos"
        self.videos_path.mkdir(exist_ok=True)
        
        # Track all saved files for current session
        self.session_files = {}
        
    async def save_media(self, 
                        content: bytes, 
                        filename: str,
                        media_type: str,
                        record_id: str,
                        upload_to_drive: bool = True) -> Dict:
        """
        Save media file locally and optionally to Google Drive
        
        Args:
            content: File content in bytes
            filename: Name of the file (e.g., "intro.mp3")
            media_type: Type of media ("audio", "image", "video")
            record_id: Airtable record ID for organization
            upload_to_drive: Whether to also upload to Google Drive
            
        Returns:
            Dict with local_path and drive_url (if uploaded)
        """
        try:
            # Determine local path based on media type
            if media_type == "audio":
                base_path = self.audio_path
            elif media_type == "image":
                base_path = self.images_path
            elif media_type == "video":
                base_path = self.videos_path
            else:
                base_path = self.daily_path
            
            # Create record-specific directory
            record_path = base_path / record_id
            record_path.mkdir(exist_ok=True)
            
            # Save locally first (ALWAYS)
            local_file_path = record_path / filename
            
            # Write file asynchronously
            async with aiofiles.open(local_file_path, 'wb') as f:
                await f.write(content)
            
            logger.info(f"✅ Saved locally: {local_file_path}")
            
            # Track this file for the session
            session_key = f"{record_id}_{media_type}_{filename}"
            self.session_files[session_key] = str(local_file_path)
            
            result = {
                'success': True,
                'local_path': str(local_file_path),
                'drive_url': None,
                'file_size': len(content)
            }
            
            # Upload to Google Drive asynchronously (if enabled)
            if upload_to_drive:
                try:
                    drive_url = await self._upload_to_drive_async(
                        local_file_path, 
                        filename, 
                        media_type,
                        record_id
                    )
                    result['drive_url'] = drive_url
                    logger.info(f"☁️ Uploaded to Drive: {filename}")
                except Exception as e:
                    # Drive upload failure doesn't affect local save
                    logger.warning(f"⚠️ Drive upload failed (local save OK): {e}")
                    result['drive_upload_error'] = str(e)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to save media: {e}")
            return {
                'success': False,
                'error': str(e),
                'local_path': None,
                'drive_url': None
            }
    
    async def _upload_to_drive_async(self, 
                                     local_path: Path, 
                                     filename: str,
                                     media_type: str,
                                     record_id: str) -> Optional[str]:
        """
        Upload file to Google Drive asynchronously
        Returns the shareable URL
        """
        try:
            # Import the Google Drive agent
            from src.mcp.production_enhanced_google_drive_agent_mcp import production_upload_to_google_drive
            
            # Prepare file info for upload
            file_info = {
                'local_path': str(local_path),
                'filename': filename,
                'media_type': media_type,
                'record_id': record_id
            }
            
            # Call the upload function
            result = await production_upload_to_google_drive(file_info, self.config)
            
            if result.get('success'):
                return result.get('url')
            else:
                raise Exception(result.get('error', 'Unknown upload error'))
                
        except Exception as e:
            logger.error(f"Drive upload error: {e}")
            raise
    
    async def download_and_save_locally(self, 
                                       url: str,
                                       filename: str,
                                       media_type: str,
                                       record_id: str) -> Optional[str]:
        """
        Download from URL and save locally (for migration from Google Drive URLs)
        """
        try:
            # Check if already downloaded in this session
            session_key = f"{record_id}_{media_type}_{filename}"
            if session_key in self.session_files:
                existing_path = Path(self.session_files[session_key])
                if existing_path.exists():
                    logger.info(f"♻️ Using cached file: {filename}")
                    return str(existing_path)
            
            # Download file
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save using dual storage
                        result = await self.save_media(
                            content=content,
                            filename=filename,
                            media_type=media_type,
                            record_id=record_id,
                            upload_to_drive=False  # Already from Drive, don't re-upload
                        )
                        
                        if result.get('success'):
                            return result.get('local_path')
                        
        except Exception as e:
            logger.error(f"Failed to download and save {filename}: {e}")
        
        return None
    
    def get_local_path(self, record_id: str, media_type: str, filename: str) -> Optional[str]:
        """
        Get local path for a file if it exists
        """
        # Check session cache first
        session_key = f"{record_id}_{media_type}_{filename}"
        if session_key in self.session_files:
            path = Path(self.session_files[session_key])
            if path.exists():
                return str(path)
        
        # Check on disk
        if media_type == "audio":
            base_path = self.audio_path
        elif media_type == "image":
            base_path = self.images_path
        elif media_type == "video":
            base_path = self.videos_path
        else:
            base_path = self.daily_path
        
        file_path = base_path / record_id / filename
        if file_path.exists():
            return str(file_path)
        
        return None
    
    async def validate_all_media_present(self, 
                                        record: Dict,
                                        required_files: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validate that ALL required media files are present locally
        
        Args:
            record: Airtable record
            required_files: List of dicts with 'field', 'media_type', 'filename'
            
        Returns:
            Tuple of (all_present: bool, missing_files: List[str])
        """
        missing = []
        record_id = record.get('record_id', 'unknown')
        
        for file_info in required_files:
            field = file_info['field']
            media_type = file_info['media_type']
            filename = file_info['filename']
            
            # Check if file exists locally
            local_path = self.get_local_path(record_id, media_type, filename)
            
            if not local_path or not Path(local_path).exists():
                # Try to download from URL if available
                url = record.get('fields', {}).get(field)
                if url:
                    logger.info(f"📥 Downloading missing file: {filename}")
                    local_path = await self.download_and_save_locally(
                        url=url,
                        filename=filename,
                        media_type=media_type,
                        record_id=record_id
                    )
                
                if not local_path:
                    missing.append(f"{field} ({filename})")
        
        all_present = len(missing) == 0
        
        if not all_present:
            logger.error(f"❌ Missing required files: {missing}")
        else:
            logger.info(f"✅ All {len(required_files)} required media files present locally")
        
        return all_present, missing
    
    def cleanup_old_files(self, days_to_keep: int = 7):
        """
        Clean up local files older than specified days
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 86400)
            
            for date_dir in self.base_local_path.iterdir():
                if date_dir.is_dir():
                    # Check directory age
                    dir_time = date_dir.stat().st_mtime
                    if dir_time < cutoff_date:
                        logger.info(f"🗑️ Removing old directory: {date_dir}")
                        shutil.rmtree(date_dir)
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics
        """
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.base_local_path):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.exists():
                        total_size += file_path.stat().st_size
                        file_count += 1
            
            return {
                'total_files': file_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'session_files': len(self.session_files),
                'storage_path': str(self.base_local_path)
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}


# Singleton instance
_storage_manager = None

def get_storage_manager(config: Dict) -> DualStorageManager:
    """Get or create the storage manager singleton"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = DualStorageManager(config)
    return _storage_manager