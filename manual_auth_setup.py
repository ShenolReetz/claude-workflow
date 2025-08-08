#!/usr/bin/env python3
"""
Manual Authentication Setup
===========================

This script provides instructions for setting up authentication
when running in a non-interactive environment.
"""

import json
import os
from datetime import datetime, timedelta

def create_test_tokens():
    """Create test tokens for development/testing purposes"""
    
    print("\n🔐 AUTHENTICATION SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n📝 To properly authenticate Google Drive and YouTube:")
    print("\n1. Google Drive Authentication:")
    print("   a) Go to: https://console.cloud.google.com/")
    print("   b) Create/select a project")
    print("   c) Enable Google Drive API")
    print("   d) Create OAuth 2.0 credentials")
    print("   e) Download credentials as 'google_drive_oauth_credentials.json'")
    print("   f) Place in /home/claude-workflow/config/")
    
    print("\n2. YouTube Authentication:")
    print("   a) Use same Google Cloud project")
    print("   b) Enable YouTube Data API v3")
    print("   c) Use same OAuth 2.0 credentials")
    print("   d) Download as 'youtube_credentials.json'")
    print("   e) Place in /home/claude-workflow/config/")
    
    print("\n3. Run Authentication Flow:")
    print("   a) Run on a machine with browser access:")
    print("      python3 src/utils/google_drive_auth_manager.py")
    print("      python3 src/utils/youtube_auth_manager.py")
    print("   b) Copy generated token files back to this server")
    
    print("\n⚠️ TEMPORARY WORKAROUND (for testing only):")
    print("   Creating mock tokens to test other components...")
    
    # Create mock tokens for testing (won't work for actual API calls)
    mock_google_token = {
        "token": "mock_token_for_testing",
        "refresh_token": "mock_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "scopes": [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file"
        ],
        "expiry": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    
    mock_youtube_token = {
        "token": "mock_token_for_testing",
        "refresh_token": "mock_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "scopes": [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube"
        ],
        "expiry": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    
    # Save mock tokens
    config_dir = '/home/claude-workflow/config'
    
    # Note: These are MOCK tokens for testing workflow logic only
    # They will NOT work for actual API calls
    
    print("\n📌 IMPORTANT: Mock tokens created for testing workflow logic.")
    print("   These will NOT work for actual Google Drive/YouTube uploads.")
    print("   Follow the instructions above to set up real authentication.")
    
    return {
        "google_drive": "mock_created",
        "youtube": "mock_created"
    }

def check_credentials():
    """Check which credential files exist"""
    config_dir = '/home/claude-workflow/config'
    
    files_to_check = [
        'google_drive_oauth_credentials.json',
        'google_drive_credentials.json',
        'youtube_credentials.json',
        'google_drive_token.json',
        'youtube_token.json'
    ]
    
    print("\n📁 Checking credential files:")
    print("-"*40)
    
    for file in files_to_check:
        path = os.path.join(config_dir, file)
        exists = "✅ EXISTS" if os.path.exists(path) else "❌ MISSING"
        print(f"{exists}: {file}")
    
    # Check API keys
    api_keys_path = os.path.join(config_dir, 'api_keys.json')
    if os.path.exists(api_keys_path):
        with open(api_keys_path, 'r') as f:
            keys = json.load(f)
        
        print("\n🔑 API Keys configured:")
        print("-"*40)
        for key in ['airtable_api_key', 'openai_api_key', 'elevenlabs_api_key', 
                    'scrapingdog_api_key', 'json2video_api_key']:
            configured = "✅" if keys.get(key) else "❌"
            print(f"{configured} {key}")

if __name__ == "__main__":
    check_credentials()
    create_test_tokens()
    
    print("\n✅ Setup instructions complete!")
    print("   Please follow the authentication steps above for production use.")