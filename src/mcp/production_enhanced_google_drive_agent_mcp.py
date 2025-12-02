#!/usr/bin/env python3
"""
Production Google Drive Upload Agent MCP
=========================================

Uploads media files to Google Drive and returns shareable URLs.
Used by DualStorageManager for cloud backup storage.

Features:
- Automatic folder organization by date and media type
- Shareable URL generation
- Robust error handling
- Async upload support
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Dict, Optional
import logging
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

sys.path.append('/home/claude-workflow')
from src.utils.google_drive_auth_manager import GoogleDriveAuthManager

logger = logging.getLogger(__name__)


class GoogleDriveUploader:
    """Upload files to Google Drive with folder organization"""

    def __init__(self, config: Dict):
        self.config = config
        self.auth_manager = GoogleDriveAuthManager(config)
        self.service = None

        # Base folder structure
        self.base_folder_name = "ReviewCh3kr_Media"
        self.base_folder_id = None

    def _get_or_create_service(self):
        """Get authenticated Google Drive service"""
        if not self.service:
            try:
                self.service = self.auth_manager.get_drive_service()
                logger.info("✅ Google Drive service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Drive service: {e}")
                raise
        return self.service

    def _get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Get existing folder or create new one"""
        service = self._get_or_create_service()

        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            if parent_id:
                query += f" and '{parent_id}' in parents"

            results = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()

            files = results.get('files', [])

            if files:
                folder_id = files[0]['id']
                logger.info(f"📁 Found existing folder: {folder_name} (ID: {folder_id})")
                return folder_id

            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                file_metadata['parents'] = [parent_id]

            folder = service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"📁 Created new folder: {folder_name} (ID: {folder_id})")

            return folder_id

        except HttpError as error:
            logger.error(f"❌ Folder creation failed: {error}")
            raise

    def _setup_folder_structure(self, media_type: str, record_id: str) -> str:
        """Setup folder structure: Base / MediaType / RecordID"""

        # Get or create base folder
        if not self.base_folder_id:
            self.base_folder_id = self._get_or_create_folder(self.base_folder_name)

        # Get or create media type folder (images, audio, videos)
        media_folder_id = self._get_or_create_folder(
            media_type.capitalize(),
            parent_id=self.base_folder_id
        )

        # Get or create record-specific folder
        record_folder_id = self._get_or_create_folder(
            record_id,
            parent_id=media_folder_id
        )

        return record_folder_id

    def upload_file(self, local_path: str, filename: str, media_type: str, record_id: str) -> Dict:
        """
        Upload file to Google Drive

        Args:
            local_path: Path to local file
            filename: Name for the file in Drive
            media_type: Type of media (audio, image, video)
            record_id: Airtable record ID for organization

        Returns:
            Dict with success status, file_id, and shareable URL
        """
        try:
            service = self._get_or_create_service()

            # Setup folder structure
            parent_folder_id = self._setup_folder_structure(media_type, record_id)

            # Determine MIME type
            mime_types = {
                'mp3': 'audio/mpeg',
                'wav': 'audio/wav',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'mp4': 'video/mp4',
                'avi': 'video/x-msvideo'
            }

            ext = Path(filename).suffix.lower().lstrip('.')
            mime_type = mime_types.get(ext, 'application/octet-stream')

            # File metadata
            file_metadata = {
                'name': filename,
                'parents': [parent_folder_id]
            }

            # Upload file
            media = MediaFileUpload(
                local_path,
                mimetype=mime_type,
                resumable=True
            )

            logger.info(f"☁️ Uploading {filename} to Google Drive...")

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink'
            ).execute()

            file_id = file.get('id')

            # Make file publicly accessible (anyone with link can view)
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }

            service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()

            # Get shareable URL
            web_view_link = file.get('webViewLink')
            web_content_link = file.get('webContentLink')

            # Create direct download link
            direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"

            logger.info(f"✅ Uploaded: {filename} (ID: {file_id})")
            logger.info(f"🔗 View: {web_view_link}")
            logger.info(f"📥 Direct: {direct_link}")

            return {
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'url': web_view_link,
                'direct_download_url': direct_link,
                'web_content_link': web_content_link,
                'media_type': media_type,
                'record_id': record_id
            }

        except Exception as e:
            logger.error(f"❌ Upload failed for {filename}: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }


# Async wrapper for use with DualStorageManager
async def production_upload_to_google_drive(file_info: Dict, config: Dict) -> Dict:
    """
    Async wrapper for Google Drive upload

    Args:
        file_info: Dict with local_path, filename, media_type, record_id
        config: Configuration dict with Google Drive credentials

    Returns:
        Dict with upload result
    """
    try:
        uploader = GoogleDriveUploader(config)

        # Run synchronous upload in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            uploader.upload_file,
            file_info['local_path'],
            file_info['filename'],
            file_info['media_type'],
            file_info['record_id']
        )

        return result

    except Exception as e:
        logger.error(f"❌ Async upload failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# Test function
def test_google_drive_upload():
    """Test Google Drive upload functionality"""
    import json

    # Load config
    config_path = '/home/claude-workflow/config/api_keys.json'
    with open(config_path, 'r') as f:
        config = json.load(f)

    uploader = GoogleDriveUploader(config)

    print("\n☁️ Testing Google Drive Upload...")
    print("=" * 60)

    # Create test file
    test_file = Path("/tmp/test_upload.txt")
    test_file.write_text("This is a test file for Google Drive upload.")

    # Upload test
    result = uploader.upload_file(
        local_path=str(test_file),
        filename="test_upload.txt",
        media_type="test",
        record_id="test_record"
    )

    if result.get('success'):
        print("✅ Upload successful!")
        print(f"📁 File ID: {result['file_id']}")
        print(f"🔗 View URL: {result['url']}")
        print(f"📥 Direct Download: {result['direct_download_url']}")
    else:
        print(f"❌ Upload failed: {result.get('error')}")

    # Cleanup
    test_file.unlink()

    return result


if __name__ == "__main__":
    test_google_drive_upload()
