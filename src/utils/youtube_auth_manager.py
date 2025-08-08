#!/usr/bin/env python3
"""
YouTube Authentication Manager
===============================

Robust authentication management for YouTube Data API with:
- Automatic token refresh
- OAuth flow management
- Error recovery
- Retry logic
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import time

class YouTubeAuthManager:
    # Required scopes for YouTube uploads
    REQUIRED_SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtubepartner'
    ]
    
    def __init__(self, config: Dict):
        self.config = config
        self.token_path = config.get('youtube_token', '/home/claude-workflow/config/youtube_token.json')
        self.credentials_path = config.get('youtube_credentials', '/home/claude-workflow/config/youtube_credentials.json')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.creds = None
        self.youtube = None
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    def authenticate(self) -> Credentials:
        """Authenticate with YouTube API with robust error handling"""
        
        # Try to load and refresh existing credentials
        try:
            self.creds = self._load_or_refresh_credentials()
            if self.creds and self.creds.valid:
                self.logger.info("✅ Successfully authenticated with existing credentials")
                return self.creds
        except Exception as e:
            self.logger.warning(f"Failed to use existing credentials: {e}")
            
        # If that fails, run new OAuth flow
        try:
            self.creds = self._run_oauth_flow()
            if self.creds:
                self.logger.info("✅ Successfully completed new OAuth flow")
                return self.creds
        except Exception as e:
            self.logger.error(f"Failed to complete OAuth flow: {e}")
            raise Exception("YouTube authentication failed. Please check credentials.")
    
    def _load_or_refresh_credentials(self) -> Optional[Credentials]:
        """Load existing credentials and refresh if needed"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'r') as token:
                    token_data = json.load(token)
                    
                # Create credentials from token data
                creds = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes', self.REQUIRED_SCOPES)
                )
            except Exception as e:
                self.logger.warning(f"Failed to load token file: {e}")
                return None
        
        # Refresh if expired or invalid
        if creds:
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    # Try to refresh with retries
                    for attempt in range(self.max_retries):
                        try:
                            self.logger.info(f"Token expired, refreshing... (attempt {attempt + 1}/{self.max_retries})")
                            creds.refresh(Request())
                            self._save_credentials(creds)
                            self.logger.info("✅ Token refreshed successfully")
                            break
                        except Exception as refresh_error:
                            self.logger.warning(f"Token refresh attempt {attempt + 1} failed: {refresh_error}")
                            if attempt < self.max_retries - 1:
                                time.sleep(self.retry_delay * (attempt + 1))
                            else:
                                self.logger.error("All token refresh attempts failed")
                                return None
                else:
                    self.logger.warning("Token invalid and cannot be refreshed")
                    return None
                        
        return creds
    
    def _run_oauth_flow(self) -> Optional[Credentials]:
        """Run OAuth2 flow to get new credentials"""
        if not os.path.exists(self.credentials_path):
            self.logger.error(f"YouTube OAuth credentials file not found: {self.credentials_path}")
            self.logger.info("Please ensure youtube_credentials.json is properly configured")
            return None
            
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                self.REQUIRED_SCOPES
            )
            
            # Run local server for authorization
            self.logger.info("Opening browser for YouTube authorization...")
            self.logger.info("Please authorize the application in your browser")
            
            creds = flow.run_local_server(
                port=8090,  # Different port from Google Drive
                prompt='consent',
                access_type='offline',
                include_granted_scopes='true'
            )
            
            self._save_credentials(creds)
            return creds
            
        except Exception as e:
            self.logger.error(f"OAuth flow failed: {e}")
            return None
    
    def _save_credentials(self, creds: Credentials):
        """Save credentials to token file"""
        try:
            token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes,
                'expiry': creds.expiry.isoformat() if creds.expiry else None
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            
            with open(self.token_path, 'w') as token_file:
                json.dump(token_data, token_file, indent=2)
                
            self.logger.info(f"✅ Credentials saved to {self.token_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
    
    def get_youtube_service(self):
        """Get authenticated YouTube service with retry logic"""
        if not self.creds:
            self.creds = self.authenticate()
            
        if not self.youtube:
            for attempt in range(self.max_retries):
                try:
                    self.youtube = build('youtube', 'v3', credentials=self.creds)
                    self.logger.info("✅ YouTube service built successfully")
                    break
                except Exception as e:
                    self.logger.warning(f"Failed to build YouTube service (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    else:
                        raise Exception("Failed to build YouTube service after all retries")
                        
        return self.youtube
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        try:
            youtube = self.get_youtube_service()
            
            # Try to list channels (simplest API call)
            request = youtube.channels().list(
                part="snippet",
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                channel_name = response['items'][0]['snippet']['title']
                self.logger.info(f"✅ YouTube authentication test successful")
                self.logger.info(f"   Connected to channel: {channel_name}")
                return True
            else:
                self.logger.warning("No YouTube channel found for this account")
                return False
                
        except HttpError as e:
            if e.resp.status == 403:
                self.logger.error("❌ YouTube API access forbidden. Check API key and quotas.")
            elif e.resp.status == 401:
                self.logger.error("❌ YouTube authentication failed. Token may be invalid.")
            else:
                self.logger.error(f"❌ YouTube API error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Authentication test failed: {e}")
            return False


def test_youtube_auth():
    """Test function to verify YouTube authentication"""
    config_path = '/home/claude-workflow/config/api_keys.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    auth_manager = YouTubeAuthManager(config)
    
    print("\n🔐 Testing YouTube Authentication...")
    print("=" * 60)
    
    if auth_manager.test_authentication():
        print("✅ Authentication successful! Ready to upload videos.")
    else:
        print("❌ Authentication failed. Please check credentials.")
        print("\nTo fix authentication issues:")
        print("1. Ensure youtube_credentials.json exists in config/")
        print("2. Delete youtube_token.json if it exists")
        print("3. Run this script again to re-authenticate")
        
    return auth_manager


if __name__ == "__main__":
    test_youtube_auth()