#!/usr/bin/env python3
import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_youtube_console():
    """Authenticate YouTube using console flow (no browser needed)"""
    
    creds = None
    token_file = '/home/claude-workflow/config/youtube_token.json'
    credentials_file = '/home/claude-workflow/config/youtube_credentials.json'
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        print("✅ Found existing token")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing token...")
            creds.refresh(Request())
        else:
            print("\n🔑 YouTube OAuth Setup")
            print("=" * 50)
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("\n📋 Instructions:")
            print("1. Open this URL in your browser:")
            print(f"\n{auth_url}\n")
            print("2. Log in to your YouTube account")
            print("3. Click 'Allow' to grant permissions")
            print("4. Copy the authorization code")
            print("5. Paste it below:\n")
            
            code = input('Authorization code: ')
            flow.fetch_token(code=code)
            creds = flow.credentials
            
        # Save token
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            print(f"\n✅ Token saved to: {token_file}")
    
    return creds

if __name__ == "__main__":
    try:
        creds = authenticate_youtube_console()
        
        # Test the credentials
        youtube = build('youtube', 'v3', credentials=creds)
        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]['snippet']
            print(f"\n✅ Authenticated as: {channel['title']}")
            print(f"📺 Channel ready for uploads!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
