#!/usr/bin/env python3
"""
Google Drive Authentication Manager
====================================

Robust authentication management for Google Drive API with:
- Automatic token refresh
- Scope validation
- Fallback to service account
- Error recovery
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

class GoogleDriveAuthManager:
    # Required scopes for full Drive access
    REQUIRED_SCOPES = [
        'https://www.googleapis.com/auth/drive',  # Full Drive access
        'https://www.googleapis.com/auth/drive.file',  # Create and manage files
        'https://www.googleapis.com/auth/drive.metadata',  # View and manage metadata
    ]
    
    def __init__(self, config: Dict):
        self.config = config
        self.token_path = config.get('google_drive_token', '/home/claude-workflow/config/google_drive_token.json')
        self.credentials_path = config.get('google_drive_credentials', '/home/claude-workflow/config/google_drive_oauth_credentials.json')
        self.service_account_path = config.get('google_drive_service_account', '/home/claude-workflow/config/google_drive_credentials.json')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.creds = None
        self.service = None
        
    def authenticate(self) -> Credentials:
        """Authenticate with Google Drive API with robust error handling"""
        
        # Try OAuth2 first
        try:
            self.creds = self._load_or_refresh_oauth_credentials()
            if self.creds and self.creds.valid:
                self.logger.info("✅ Successfully authenticated with OAuth2")
                return self.creds
        except Exception as oauth_error:
            self.logger.warning(f"OAuth2 authentication failed: {oauth_error}")
            
        # Fallback to service account
        try:
            self.creds = self._authenticate_with_service_account()
            if self.creds:
                self.logger.info("✅ Successfully authenticated with service account")
                return self.creds
        except Exception as sa_error:
            self.logger.warning(f"Service account authentication failed: {sa_error}")
            
        # If all fails, trigger new OAuth flow
        try:
            self.creds = self._run_oauth_flow()
            if self.creds:
                self.logger.info("✅ Successfully completed new OAuth flow")
                return self.creds
        except Exception as flow_error:
            self.logger.error(f"Failed to complete OAuth flow: {flow_error}")
            raise Exception("All authentication methods failed. Please check credentials.")
    
    def _load_or_refresh_oauth_credentials(self) -> Optional[Credentials]:
        """Load existing OAuth credentials and refresh if needed"""
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
                    scopes=self.REQUIRED_SCOPES  # Use our required scopes
                )
            except Exception as e:
                self.logger.warning(f"Failed to load token file: {e}")
                return None
        
        # Refresh if expired
        if creds:
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    try:
                        self.logger.info("Token expired, refreshing...")
                        creds.refresh(Request())
                        self._save_credentials(creds)
                        self.logger.info("✅ Token refreshed successfully")
                    except Exception as refresh_error:
                        self.logger.error(f"Token refresh failed: {refresh_error}")
                        return None
                        
            # Validate scopes
            if not self._validate_scopes(creds):
                self.logger.warning("Token has insufficient scopes, need re-authentication")
                return None
                
        return creds
    
    def _authenticate_with_service_account(self) -> Optional[Credentials]:
        """Authenticate using service account credentials"""
        if not os.path.exists(self.service_account_path):
            self.logger.warning(f"Service account file not found: {self.service_account_path}")
            return None
            
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.service_account_path,
                scopes=self.REQUIRED_SCOPES
            )
            return creds
        except Exception as e:
            self.logger.error(f"Service account authentication failed: {e}")
            return None
    
    def _run_oauth_flow(self) -> Optional[Credentials]:
        """Run OAuth2 flow to get new credentials"""
        if not os.path.exists(self.credentials_path):
            self.logger.error(f"OAuth credentials file not found: {self.credentials_path}")
            return None
            
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                self.REQUIRED_SCOPES
            )
            
            # Run local server for authorization
            creds = flow.run_local_server(
                port=8080,
                prompt='consent',
                access_type='offline'
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
            
            with open(self.token_path, 'w') as token_file:
                json.dump(token_data, token_file, indent=2)
                
            self.logger.info(f"✅ Credentials saved to {self.token_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
    
    def _validate_scopes(self, creds: Credentials) -> bool:
        """Validate that credentials have required scopes"""
        if not creds.scopes:
            return False
            
        # Check if we have at least the minimum required scope
        return any(scope in creds.scopes for scope in [
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file'
        ])
    
    def get_drive_service(self):
        """Get authenticated Google Drive service"""
        if not self.creds:
            self.creds = self.authenticate()
            
        if not self.service:
            self.service = build('drive', 'v3', credentials=self.creds)
            
        return self.service
    
    def test_authentication(self) -> bool:
        """Test if authentication is working"""
        try:
            service = self.get_drive_service()
            # Try to list files (limited to 1 for speed)
            result = service.files().list(
                pageSize=1,
                fields="files(id, name)"
            ).execute()
            
            self.logger.info("✅ Google Drive authentication test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Authentication test failed: {e}")
            return False


def test_google_drive_auth():
    """Test function to verify authentication"""
    config_path = '/home/claude-workflow/config/api_keys.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    auth_manager = GoogleDriveAuthManager(config)
    
    print("\n🔐 Testing Google Drive Authentication...")
    print("=" * 60)
    
    if auth_manager.test_authentication():
        print("✅ Authentication successful! Ready to upload files.")
    else:
        print("❌ Authentication failed. Please check credentials.")
        
    return auth_manager


if __name__ == "__main__":
    test_google_drive_auth()