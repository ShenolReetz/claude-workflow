#!/usr/bin/env python3
"""
Google Drive Token Refresh Script
Handles both automatic refresh and manual re-authorization flow
"""

import json
import requests
import os
import sys
from datetime import datetime, timedelta

def load_token_file(path='/home/claude-workflow/config/google_drive_token.json'):
    """Load the existing token file"""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading token file: {e}")
        return None

def save_token_file(token_data, path='/home/claude-workflow/config/google_drive_token.json'):
    """Save updated token data"""
    try:
        with open(path, 'w') as f:
            json.dump(token_data, f, indent=2)
        return True
    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False

def refresh_access_token(token_data):
    """Attempt to refresh the access token using refresh token"""
    
    print("\n🔄 Attempting to refresh Google Drive access token...")
    
    # Check for required fields
    required_fields = ['client_id', 'client_secret', 'refresh_token']
    missing_fields = [f for f in required_fields if not token_data.get(f)]
    
    if missing_fields:
        print(f"❌ Missing required fields: {', '.join(missing_fields)}")
        return False
    
    # Prepare refresh request
    refresh_url = "https://oauth2.googleapis.com/token"
    refresh_data = {
        "client_id": token_data['client_id'],
        "client_secret": token_data['client_secret'],
        "refresh_token": token_data['refresh_token'],
        "grant_type": "refresh_token"
    }
    
    print(f"📡 Sending refresh request to Google OAuth2...")
    print(f"   Client ID: {token_data['client_id'][:20]}...")
    
    try:
        response = requests.post(refresh_url, data=refresh_data)
        
        if response.status_code == 200:
            # Success! Update token data
            refresh_result = response.json()
            
            # Update access token
            token_data['token'] = refresh_result['access_token']
            
            # Calculate new expiry (typically 1 hour from now)
            expires_in = refresh_result.get('expires_in', 3600)
            new_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            token_data['expiry'] = new_expiry.isoformat() + 'Z'
            
            # Update refresh token if a new one was provided
            if 'refresh_token' in refresh_result:
                token_data['refresh_token'] = refresh_result['refresh_token']
                print("   ✅ Received new refresh token")
            
            # Save updated token
            if save_token_file(token_data):
                print(f"\n✅ Token refreshed successfully!")
                print(f"   New expiry: {token_data['expiry']}")
                print(f"   Valid for: {expires_in/3600:.1f} hours")
                return True
            else:
                print("❌ Failed to save refreshed token")
                return False
                
        else:
            # Error occurred
            print(f"\n❌ Refresh failed with status {response.status_code}")
            
            try:
                error_data = response.json()
                error = error_data.get('error', 'unknown')
                error_desc = error_data.get('error_description', 'No description')
                
                print(f"   Error: {error}")
                print(f"   Description: {error_desc}")
                
                # Common error causes and solutions
                if error == 'invalid_grant':
                    print("\n⚠️  REFRESH TOKEN EXPIRED OR REVOKED")
                    print("   This usually happens when:")
                    print("   1. The refresh token hasn't been used for 6 months")
                    print("   2. The OAuth consent was revoked")
                    print("   3. Too many refresh tokens were generated (limit ~50)")
                    print("\n   SOLUTION: You need to re-authorize manually")
                    print("   Run: python3 setup_google_drive_oauth.py")
                    
                elif error == 'invalid_client':
                    print("\n⚠️  CLIENT CREDENTIALS INVALID")
                    print("   The client_id or client_secret may be incorrect")
                    print("   Check your OAuth2 client configuration in Google Cloud Console")
                    
            except:
                print(f"   Response: {response.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ Exception during refresh: {e}")
        return False

def generate_new_authorization_url(token_data):
    """Generate URL for manual re-authorization"""
    
    print("\n📋 MANUAL RE-AUTHORIZATION REQUIRED")
    print("="*50)
    
    if not token_data or not token_data.get('client_id'):
        print("❌ Cannot generate authorization URL - missing client_id")
        print("   You'll need to set up OAuth from scratch")
        return
    
    # OAuth2 authorization URL
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    # Parameters for authorization
    params = {
        'client_id': token_data['client_id'],
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',  # For manual copy-paste flow
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/drive',
        'access_type': 'offline',  # To get refresh token
        'prompt': 'consent'  # Force consent to get new refresh token
    }
    
    # Build authorization URL
    param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{auth_url}?{param_string}"
    
    print("\n🔗 AUTHORIZATION URL:")
    print(full_url)
    print("\n📝 STEPS TO RE-AUTHORIZE:")
    print("1. Open the URL above in your browser")
    print("2. Sign in with your Google account")
    print("3. Grant permissions to access Google Drive")
    print("4. Copy the authorization code")
    print("5. Run this script with the code: python3 refresh_google_token.py --code YOUR_CODE")

def exchange_code_for_tokens(code, token_data):
    """Exchange authorization code for new tokens"""
    
    print("\n🔄 Exchanging authorization code for tokens...")
    
    token_url = "https://oauth2.googleapis.com/token"
    token_data_request = {
        'client_id': token_data['client_id'],
        'client_secret': token_data['client_secret'],
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob'
    }
    
    try:
        response = requests.post(token_url, data=token_data_request)
        
        if response.status_code == 200:
            new_tokens = response.json()
            
            # Update token data
            token_data['token'] = new_tokens['access_token']
            token_data['refresh_token'] = new_tokens['refresh_token']
            
            # Set expiry
            expires_in = new_tokens.get('expires_in', 3600)
            expiry = datetime.utcnow() + timedelta(seconds=expires_in)
            token_data['expiry'] = expiry.isoformat() + 'Z'
            
            # Save updated tokens
            if save_token_file(token_data):
                print("\n✅ New tokens obtained successfully!")
                print(f"   Access token valid for: {expires_in/3600:.1f} hours")
                print("   Refresh token saved for future use")
                return True
            else:
                print("❌ Failed to save new tokens")
                return False
        else:
            print(f"❌ Failed to exchange code: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during code exchange: {e}")
        return False

def main():
    print("🔑 Google Drive Token Refresh Tool")
    print("="*50)
    
    # Load existing token
    token_data = load_token_file()
    
    if not token_data:
        print("❌ No token file found")
        print("   Run setup_google_drive_oauth.py first to create initial tokens")
        sys.exit(1)
    
    # Check if authorization code was provided
    if len(sys.argv) > 2 and sys.argv[1] == '--code':
        # Exchange authorization code for new tokens
        code = sys.argv[2]
        if exchange_code_for_tokens(code, token_data):
            print("\n🎉 Token refresh complete! Google Drive integration restored.")
        else:
            print("\n❌ Failed to exchange authorization code")
        sys.exit(0)
    
    # Try automatic refresh first
    if refresh_access_token(token_data):
        print("\n🎉 Token refresh successful! Google Drive integration is working.")
    else:
        # Automatic refresh failed, provide manual instructions
        generate_new_authorization_url(token_data)
        
        print("\n💡 ALTERNATIVE: Google Cloud Console Method")
        print("="*50)
        print("1. Visit: https://console.cloud.google.com/apis/credentials")
        print("2. Find your OAuth 2.0 Client ID")
        print("3. Download the credentials JSON")
        print("4. Use the credentials to re-authorize")

if __name__ == "__main__":
    main()