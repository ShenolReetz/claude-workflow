#!/usr/bin/env python3
"""
Fix Google Drive Authentication
================================

This script fixes the Google Drive authentication issue by:
1. Using only the drive.file scope that we currently have
2. Properly refreshing the token without requesting new scopes
"""

import json
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_google_drive_token():
    """Fix the Google Drive token by refreshing with existing scopes"""
    
    token_path = '/home/claude-workflow/config/google_drive_token.json'
    
    # Load current token
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    print("\n🔧 Fixing Google Drive Authentication...")
    print("=" * 60)
    print(f"Current token scopes: {token_data.get('scopes')}")
    
    try:
        # Create credentials with existing scopes
        creds = Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')  # Use existing scopes
        )
        
        # Check if token is expired
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                print("🔄 Token expired, refreshing with same scopes...")
                creds.refresh(Request())
                
                # Save updated token
                token_data['token'] = creds.token
                if creds.expiry:
                    token_data['expiry'] = creds.expiry.isoformat()
                
                with open(token_path, 'w') as f:
                    json.dump(token_data, f, indent=2)
                
                print("✅ Token refreshed successfully!")
        else:
            print("✅ Token is still valid!")
        
        # Test the credentials
        print("\n🧪 Testing Google Drive access...")
        service = build('drive', 'v3', credentials=creds)
        
        # Try to create a test folder
        file_metadata = {
            'name': f'Test_Folder_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        file = service.files().create(body=file_metadata, fields='id,name,webViewLink').execute()
        print(f"✅ Successfully created test folder: {file.get('name')}")
        print(f"   Link: {file.get('webViewLink')}")
        
        # Clean up - delete test folder
        service.files().delete(fileId=file.get('id')).execute()
        print("🗑️  Test folder deleted")
        
        print("\n✅ Google Drive authentication is working properly!")
        print("   The drive.file scope is sufficient for our needs.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Solution: The token needs to be regenerated with proper authentication.")
        print("   This requires browser access for OAuth flow.")
        return False

def display_instructions():
    """Display instructions for manual token generation"""
    
    print("\n📝 MANUAL TOKEN GENERATION INSTRUCTIONS:")
    print("=" * 60)
    print("\n1. On a machine with browser access, create a file 'generate_token.py':")
    print("\n```python")
    print("from google.oauth2.credentials import Credentials")
    print("from google_auth_oauthlib.flow import InstalledAppFlow")
    print("import json")
    print("")
    print("# Use drive.file scope which is sufficient")
    print("SCOPES = ['https://www.googleapis.com/auth/drive.file']")
    print("")
    print("flow = InstalledAppFlow.from_client_secrets_file(")
    print("    'google_drive_oauth_credentials.json',")
    print("    SCOPES")
    print(")")
    print("")
    print("creds = flow.run_local_server(port=8080)")
    print("")
    print("# Save the token")
    print("token_data = {")
    print("    'token': creds.token,")
    print("    'refresh_token': creds.refresh_token,")
    print("    'token_uri': creds.token_uri,")
    print("    'client_id': creds.client_id,")
    print("    'client_secret': creds.client_secret,")
    print("    'scopes': creds.scopes,")
    print("    'expiry': creds.expiry.isoformat() if creds.expiry else None")
    print("}")
    print("")
    print("with open('google_drive_token.json', 'w') as f:")
    print("    json.dump(token_data, f, indent=2)")
    print("```")
    print("\n2. Copy the OAuth credentials file to that machine")
    print("3. Run the script and complete authentication in browser")
    print("4. Copy the generated token back to this server")

if __name__ == "__main__":
    success = fix_google_drive_token()
    
    if not success:
        display_instructions()