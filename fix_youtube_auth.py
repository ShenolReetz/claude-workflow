#!/usr/bin/env python3
"""
Fix YouTube Authentication
===========================
This script helps regenerate YouTube OAuth tokens when they expire.
"""

import os
import json
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def main():
    print("🔧 YouTube Authentication Fix")
    print("=" * 60)
    
    # Paths
    creds_file = '/home/claude-workflow/config/youtube_credentials.json'
    token_file = '/home/claude-workflow/config/youtube_token.json'
    
    # Check if credentials file exists
    if not os.path.exists(creds_file):
        print("❌ Error: youtube_credentials.json not found!")
        print("Please ensure the file exists at:", creds_file)
        return
    
    # Delete old token if exists
    if os.path.exists(token_file):
        os.remove(token_file)
        print("✅ Deleted old token file")
    
    # Set up OAuth flow
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
              'https://www.googleapis.com/auth/youtube',
              'https://www.googleapis.com/auth/youtube.force-ssl']
    
    flow = Flow.from_client_secrets_file(
        creds_file,
        scopes=SCOPES,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob'  # For manual copy-paste auth
    )
    
    # Get authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent to get refresh token
    )
    
    print("\n📋 Please follow these steps:")
    print("1. Open this URL in your browser:")
    print(f"\n{auth_url}\n")
    print("2. Sign in with the YouTube account")
    print("3. Grant all requested permissions")
    print("4. Copy the authorization code")
    print("5. Paste it below")
    print("\n" + "=" * 60)
    
    # Get authorization code from user
    code = input("Enter the authorization code: ").strip()
    
    try:
        # Exchange code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save credentials
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print("\n✅ Success! YouTube authentication fixed.")
        print(f"Token saved to: {token_file}")
        
        # Test the authentication
        print("\n🧪 Testing authentication...")
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Try to get channel info as a test
        request = youtube.channels().list(
            part='snippet',
            mine=True
        )
        response = request.execute()
        
        if response.get('items'):
            channel_name = response['items'][0]['snippet']['title']
            print(f"✅ Authenticated as: {channel_name}")
        else:
            print("✅ Authentication successful!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease try again. Make sure you:")
        print("1. Used the correct Google account")
        print("2. Granted all permissions")
        print("3. Copied the complete authorization code")

if __name__ == "__main__":
    main()