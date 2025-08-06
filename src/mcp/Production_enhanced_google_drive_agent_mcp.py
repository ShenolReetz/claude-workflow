#!/usr/bin/env python3
"""
Production Enhanced Google Drive Agent MCP
==========================================

Complete Google Drive integration with:
- Folder structure creation (Videos, Photos, Audio)
- Upload of ALL assets (video, intro/outro images, product images, audio files)
- Proper Airtable reference link updates
- Token refresh management
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import aiohttp
import os
import io
from typing import Dict, Optional, List
import json
from datetime import datetime

# Import Airtable server for updates
import sys
sys.path.append('/home/claude-workflow')
from mcp_servers.Production_airtable_server import ProductionAirtableMCPServer

class ProductionEnhancedGoogleDriveAgent:
    def __init__(self, config: Dict):
        self.config = config
        self.service = None
        self.airtable_server = ProductionAirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
    async def initialize_drive_service(self):
        """Initialize Google Drive service with token refresh"""
        token_path = self.config.get('google_drive_token', '/home/claude-workflow/config/google_drive_token.json')
        creds = None
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    with open(token_path, 'w') as token_file:
                        token_file.write(creds.to_json())
                    print("✅ Google Drive token refreshed successfully")
                except Exception as refresh_error:
                    raise Exception(f'Token refresh failed: {refresh_error}')
            else:
                raise Exception('Invalid Google Drive credentials - need to re-authenticate')
        
        self.service = build('drive', 'v3', credentials=creds)
        return self.service
    
    async def create_project_folder_structure(self, record_id: str, video_title: str) -> Dict[str, str]:
        """Create organized folder structure for the project"""
        try:
            await self.initialize_drive_service()
            
            # Main project folder
            project_name = f"{video_title}_{record_id[:8]}"
            main_folder = await self._create_folder(project_name, parent_id=None)
            
            # Create subfolders
            subfolders = {}
            folder_names = {
                'videos': 'Final Videos',
                'images': 'Product Images', 
                'audio': 'Audio Files',
                'generated_images': 'Generated Images (Intro/Outro)'
            }
            
            for key, name in folder_names.items():
                folder = await self._create_folder(name, parent_id=main_folder['id'])
                subfolders[key] = folder['id']
            
            print(f"✅ Created folder structure: {main_folder['webViewLink']}")
            
            return {
                'main_folder_id': main_folder['id'],
                'main_folder_url': main_folder['webViewLink'],
                'videos_folder_id': subfolders['videos'],
                'images_folder_id': subfolders['images'],
                'audio_folder_id': subfolders['audio'],
                'generated_images_folder_id': subfolders['generated_images']
            }
            
        except Exception as e:
            print(f"❌ Error creating folder structure: {e}")
            raise
    
    async def upload_all_project_assets(self, record: Dict) -> Dict:
        """Upload all project assets and update Airtable with links"""
        try:
            record_id = record.get('record_id', '')
            video_title = record['fields'].get('VideoTitle', 'Video')
            
            print(f"🗂️ Creating Google Drive folder structure...")
            folders = await self.create_project_folder_structure(record_id, video_title)
            
            # Track all uploaded files for Airtable updates
            uploaded_files = {
                'folder_structure': folders
            }
            
            # 1. Upload Final Video
            print("🎬 Uploading final video...")
            video_result = await self._upload_video_asset(record, folders['videos_folder_id'])
            uploaded_files['video'] = video_result
            
            # 2. Upload Product Images (1-5)
            print("🖼️ Uploading product images...")
            product_images = await self._upload_product_images(record, folders['images_folder_id'])
            uploaded_files['product_images'] = product_images
            
            # 3. Upload Generated Images (Intro/Outro)
            print("🎨 Uploading generated images...")
            generated_images = await self._upload_generated_images(record, folders['generated_images_folder_id'])
            uploaded_files['generated_images'] = generated_images
            
            # 4. Upload Audio Files
            print("🎙️ Uploading audio files...")
            audio_files = await self._upload_audio_files(record, folders['audio_folder_id'])
            uploaded_files['audio_files'] = audio_files
            
            # 5. Update Airtable with all Google Drive links
            print("💾 Updating Airtable with Google Drive links...")
            await self._update_airtable_with_drive_links(record_id, uploaded_files)
            
            print("✅ All assets uploaded to Google Drive successfully!")
            
            return {
                'success': True,
                'uploaded_files': uploaded_files,
                'main_folder_url': folders['main_folder_url'],
                'updated_record': record
            }
            
        except Exception as e:
            print(f"❌ Error uploading assets to Google Drive: {e}")
            return {
                'success': False,
                'error': str(e),
                'updated_record': record
            }
    
    async def _upload_video_asset(self, record: Dict, folder_id: str) -> Dict:
        """Upload final video"""
        video_url = record['fields'].get('FinalVideo', '')
        if not video_url:
            return {'error': 'No video URL found'}
        
        # Download and upload video
        video_title = record['fields'].get('VideoTitle', 'Video')
        record_id = record.get('record_id', '')[:8]
        filename = f"{video_title}_{record_id}.mp4"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status == 200:
                    video_data = await response.read()
                    temp_file = f"/tmp/{filename}"
                    
                    with open(temp_file, 'wb') as f:
                        f.write(video_data)
                    
                    # Upload to Drive
                    file_result = await self._upload_file_to_drive(
                        temp_file, filename, folder_id, 'video/mp4'
                    )
                    
                    os.remove(temp_file)
                    return file_result
                
        return {'error': 'Failed to download video'}
    
    async def _upload_product_images(self, record: Dict, folder_id: str) -> List[Dict]:
        """Upload all product images (ProductNo1Photo - ProductNo5Photo)"""
        product_images = []
        
        for i in range(1, 6):
            image_url = record['fields'].get(f'ProductNo{i}Photo', '')
            if image_url:
                try:
                    filename = f"Product_{i}_{record.get('record_id', '')[:8]}.jpg"
                    
                    # Download image
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_url) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                temp_file = f"/tmp/{filename}"
                                
                                with open(temp_file, 'wb') as f:
                                    f.write(image_data)
                                
                                # Upload to Drive
                                file_result = await self._upload_file_to_drive(
                                    temp_file, filename, folder_id, 'image/jpeg'
                                )
                                file_result['product_number'] = i
                                product_images.append(file_result)
                                
                                os.remove(temp_file)
                                print(f"✅ Uploaded Product {i} image")
                                
                except Exception as e:
                    print(f"⚠️ Failed to upload Product {i} image: {e}")
        
        return product_images
    
    async def _upload_generated_images(self, record: Dict, folder_id: str) -> Dict:
        """Upload intro and outro images"""
        generated_images = {}
        
        # Upload Intro Image
        intro_url = record['fields'].get('IntroPhoto', '')
        if intro_url:
            try:
                filename = f"Intro_{record.get('record_id', '')[:8]}.jpg"
                generated_images['intro'] = await self._download_and_upload_image(
                    intro_url, filename, folder_id
                )
                print("✅ Uploaded intro image")
            except Exception as e:
                print(f"⚠️ Failed to upload intro image: {e}")
        
        # Upload Outro Image
        outro_url = record['fields'].get('OutroPhoto', '')
        if outro_url:
            try:
                filename = f"Outro_{record.get('record_id', '')[:8]}.jpg"
                generated_images['outro'] = await self._download_and_upload_image(
                    outro_url, filename, folder_id
                )
                print("✅ Uploaded outro image")
            except Exception as e:
                print(f"⚠️ Failed to upload outro image: {e}")
        
        return generated_images
    
    async def _upload_audio_files(self, record: Dict, folder_id: str) -> Dict:
        """Upload all audio files (intro, outro, products 1-5)"""
        audio_files = {}
        
        # Audio file mappings
        audio_mappings = {
            'intro': 'IntroMp3',
            'outro': 'OutroMp3',
            'product1': 'Product1Mp3',
            'product2': 'Product2Mp3', 
            'product3': 'Product3Mp3',
            'product4': 'Product4Mp3',
            'product5': 'Product5Mp3'
        }
        
        for audio_type, field_name in audio_mappings.items():
            audio_url = record['fields'].get(field_name, '')
            if audio_url:
                try:
                    filename = f"{audio_type}_{record.get('record_id', '')[:8]}.mp3"
                    audio_files[audio_type] = await self._download_and_upload_audio(
                        audio_url, filename, folder_id
                    )
                    print(f"✅ Uploaded {audio_type} audio")
                except Exception as e:
                    print(f"⚠️ Failed to upload {audio_type} audio: {e}")
        
        return audio_files
    
    async def _download_and_upload_image(self, url: str, filename: str, folder_id: str) -> Dict:
        """Helper to download and upload image"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    temp_file = f"/tmp/{filename}"
                    
                    with open(temp_file, 'wb') as f:
                        f.write(data)
                    
                    result = await self._upload_file_to_drive(
                        temp_file, filename, folder_id, 'image/jpeg'
                    )
                    
                    os.remove(temp_file)
                    return result
        
        return {'error': 'Failed to download'}
    
    async def _download_and_upload_audio(self, url: str, filename: str, folder_id: str) -> Dict:
        """Helper to download and upload audio"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    temp_file = f"/tmp/{filename}"
                    
                    with open(temp_file, 'wb') as f:
                        f.write(data)
                    
                    result = await self._upload_file_to_drive(
                        temp_file, filename, folder_id, 'audio/mpeg'
                    )
                    
                    os.remove(temp_file)
                    return result
        
        return {'error': 'Failed to download'}
    
    async def _upload_file_to_drive(
        self, 
        file_path: str, 
        filename: str, 
        folder_id: str, 
        mime_type: str
    ) -> Dict:
        """Upload file to Google Drive"""
        try:
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink,name,size'
            ).execute()
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'filename': filename,
                'view_url': file.get('webViewLink'),
                'download_url': file.get('webContentLink'),
                'size': file.get('size'),
                'mime_type': mime_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    async def _create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Dict:
        """Create folder in Google Drive"""
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        
        folder = self.service.files().create(
            body=folder_metadata,
            fields='id,webViewLink,name'
        ).execute()
        
        return folder
    
    async def _update_airtable_with_drive_links(self, record_id: str, uploaded_files: Dict):
        """Update Airtable with all Google Drive reference links"""
        try:
            updates = {}
            
            # Main folder link
            if 'folder_structure' in uploaded_files:
                updates['GoogleDriveFolderURL'] = uploaded_files['folder_structure']['main_folder_url']
            
            # Video links
            if 'video' in uploaded_files and uploaded_files['video'].get('success'):
                updates['GoogleDriveURL'] = uploaded_files['video']['view_url']
                updates['GoogleDriveDownloadURL'] = uploaded_files['video']['download_url']
            
            # Product image links (1-5)
            if 'product_images' in uploaded_files:
                for img in uploaded_files['product_images']:
                    if img.get('success'):
                        product_num = img.get('product_number')
                        updates[f'GoogleDriveProductNo{product_num}PhotoURL'] = img['view_url']
            
            # Generated image links
            if 'generated_images' in uploaded_files:
                gen_images = uploaded_files['generated_images']
                if 'intro' in gen_images and gen_images['intro'].get('success'):
                    updates['GoogleDriveIntroPhotoURL'] = gen_images['intro']['view_url']
                if 'outro' in gen_images and gen_images['outro'].get('success'):
                    updates['GoogleDriveOutroPhotoURL'] = gen_images['outro']['view_url']
            
            # Audio file links
            if 'audio_files' in uploaded_files:
                audio_files = uploaded_files['audio_files']
                audio_mappings = {
                    'intro': 'GoogleDriveIntroMp3URL',
                    'outro': 'GoogleDriveOutroMp3URL',
                    'product1': 'GoogleDriveProduct1Mp3URL',
                    'product2': 'GoogleDriveProduct2Mp3URL',
                    'product3': 'GoogleDriveProduct3Mp3URL',
                    'product4': 'GoogleDriveProduct4Mp3URL',
                    'product5': 'GoogleDriveProduct5Mp3URL'
                }
                
                for audio_type, field_name in audio_mappings.items():
                    if audio_type in audio_files and audio_files[audio_type].get('success'):
                        updates[field_name] = audio_files[audio_type]['view_url']
            
            # Update all fields in Airtable
            for field_name, value in updates.items():
                await self.airtable_server.update_record_field(record_id, field_name, value)
            
            print(f"✅ Updated {len(updates)} Google Drive links in Airtable")
            
        except Exception as e:
            print(f"❌ Error updating Airtable with Drive links: {e}")

# Main function for workflow integration
async def production_upload_all_assets_to_google_drive(record: Dict, config: Dict) -> Dict:
    """Enhanced Google Drive upload for all project assets"""
    agent = ProductionEnhancedGoogleDriveAgent(config)
    return await agent.upload_all_project_assets(record)

if __name__ == "__main__":
    # Test the enhanced Google Drive agent
    import asyncio
    
    async def test_drive_upload():
        config = {
            'airtable_api_key': 'test',
            'airtable_base_id': 'test',
            'airtable_table_name': 'test'
        }
        
        test_record = {
            'record_id': 'test123',
            'fields': {
                'VideoTitle': 'Test Webcam Stands',
                'FinalVideo': 'https://test.com/video.mp4',
                'ProductNo1Photo': 'https://test.com/product1.jpg',
                'IntroPhoto': 'https://test.com/intro.jpg',
                'IntroMp3': 'https://test.com/intro.mp3'
            }
        }
        
        agent = ProductionEnhancedGoogleDriveAgent(config)
        result = await agent.upload_all_project_assets(test_record)
        
        print("Test Result:", result)
    
    # asyncio.run(test_drive_upload())