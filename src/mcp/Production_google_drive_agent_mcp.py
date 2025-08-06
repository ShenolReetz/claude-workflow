#!/usr/bin/env python3
"""
Production Google Drive Agent MCP - Upload Videos to Google Drive
"""

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import aiohttp
import os
import io
from typing import Dict, Optional
import json

async def production_upload_video_to_google_drive(record: Dict, config: Dict) -> Dict:
    """Upload video to Google Drive with proper token refresh"""
    try:
        # Load and refresh credentials
        token_path = config.get('google_drive_token', '/home/claude-workflow/config/google_drive_token.json')
        creds = None
        
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)
            
        # Refresh credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed token
                    with open(token_path, 'w') as token_file:
                        token_file.write(creds.to_json())
                    print("✅ Google Drive token refreshed successfully")
                except Exception as refresh_error:
                    print(f"❌ Token refresh failed: {refresh_error}")
                    return {
                        'success': False,
                        'error': f'Token refresh failed: {refresh_error}',
                        'updated_record': record
                    }
            else:
                return {
                    'success': False,
                    'error': 'Invalid Google Drive credentials - need to re-authenticate',
                    'updated_record': record
                }
        
        service = build('drive', 'v3', credentials=creds)
        
        # Get video URL from record
        video_url = record.get('fields', {}).get('FinalVideo', '')
        if not video_url:
            return {
                'success': False,
                'error': 'No video URL found in FinalVideo field',
                'updated_record': record
            }
        
        # Download video from JSON2Video URL
        video_title = record['fields'].get('VideoTitle', 'Video')
        record_id = record.get('record_id', '')[:8]
        filename = f"{video_title}_{record_id}.mp4"
        
        print(f"🔄 Downloading video from: {video_url[:50]}...")
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status == 200:
                    video_data = await response.read()
                    
                    # Create temporary file
                    temp_file_path = f"/tmp/{filename}"
                    with open(temp_file_path, 'wb') as f:
                        f.write(video_data)
                    
                    # Upload to Google Drive
                    file_metadata = {
                        'name': filename,
                        'mimeType': 'video/mp4'
                    }
                    
                    media = MediaFileUpload(temp_file_path, mimetype='video/mp4', resumable=True)
                    file = service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id,webViewLink,webContentLink'
                    ).execute()
                    
                    # Clean up temp file
                    os.remove(temp_file_path)
                    
                    drive_url = file.get('webViewLink', '')
                    download_url = file.get('webContentLink', '')
                    
                    # Update record with Google Drive URL
                    record['fields']['GoogleDriveURL'] = drive_url
                    record['fields']['GoogleDriveDownloadURL'] = download_url
                    
                    print(f"✅ Video uploaded to Google Drive: {drive_url}")
                    
                    return {
                        'success': True,
                        'drive_url': drive_url,
                        'download_url': download_url,
                        'file_id': file.get('id'),
                        'updated_record': record
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Failed to download video: HTTP {response.status}',
                        'updated_record': record
                    }
        
    except Exception as e:
        print(f"❌ Error uploading to Google Drive: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }