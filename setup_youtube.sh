#!/bin/bash
# setup_youtube.sh - Set up and test YouTube integration separately

echo "🎬 YouTube Integration Setup"
echo "==========================="

cd /home/claude-workflow

# Step 1: Create the authentication script
echo -e "\n1️⃣ Creating YouTube authentication script..."
cat > youtube_auth_console.py << 'PYEOF'
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
PYEOF

chmod +x youtube_auth_console.py
echo "✅ Created youtube_auth_console.py"

# Step 2: Create the YouTube MCP
echo -e "\n2️⃣ Creating YouTube MCP..."
mkdir -p src/mcp

cat > src/mcp/youtube_mcp.py << 'PYEOF'
import os
import logging
from typing import Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import httpx

logger = logging.getLogger(__name__)

class YouTubeMCP:
    """YouTube upload MCP - fixed for headless servers"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, credentials_path: str, token_path: str = None):
        self.credentials_path = credentials_path
        self.token_path = token_path or credentials_path.replace('credentials.json', 'token.json')
        self.youtube = None
        self._initialize_youtube()
    
    def _initialize_youtube(self):
        """Initialize YouTube API client"""
        creds = None
        
        # Load token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                logger.error(f"Error loading token: {e}")
        
        # Check if valid
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed token
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    raise Exception("YouTube token expired. Please run: python3 youtube_auth_console.py")
            else:
                raise Exception("No YouTube authentication found. Please run: python3 youtube_auth_console.py")
        
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("✅ YouTube API initialized")
    
    async def upload_video(self, video_path: str, title: str, description: str, 
                          tags: list = None, category_id: str = "22", 
                          privacy_status: str = "private") -> Dict:
        """Upload video to YouTube"""
        try:
            # Download if URL
            if video_path.startswith('http'):
                logger.info(f"📥 Downloading video from: {video_path}")
                local_path = await self._download_video(video_path)
            else:
                local_path = video_path
            
            # Prepare metadata
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube limit
                    'description': description[:5000],  # YouTube limit
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload
            logger.info(f"📤 Uploading: {title}")
            media = MediaFileUpload(local_path, chunksize=-1, resumable=True, mimetype='video/mp4')
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"📊 Upload progress: {progress}%")
                except Exception as e:
                    error = e
                    retry += 1
                    if retry > 3:
                        raise e
                    logger.warning(f"Retry {retry}/3: {e}")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ Upload complete: {video_url}")
            
            # Cleanup
            if video_path.startswith('http') and os.path.exists(local_path):
                os.remove(local_path)
            
            return {
                'success': True,
                'video_id': video_id,
                'video_url': video_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _download_video(self, url: str) -> str:
        """Download video from URL to temp file"""
        import tempfile
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp.write(response.content)
                return tmp.name
PYEOF

echo "✅ Created src/mcp/youtube_mcp.py"

# Step 3: Create test script
echo -e "\n3️⃣ Creating test script..."
cat > test_youtube.py << 'PYEOF'
#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('/home/claude-workflow/src')
sys.path.append('/home/claude-workflow')

from mcp.youtube_mcp import YouTubeMCP

async def test_youtube():
    """Test YouTube upload with a sample video"""
    
    print("🧪 Testing YouTube Upload")
    print("========================")
    
    # Test video URL (your recent 8-second test video)
    test_video = "https://assets.json2video.com/clients/Apiha4SJJk/renders/2025-07-01-16928.mp4"
    
    youtube = YouTubeMCP(
        credentials_path='/home/claude-workflow/config/youtube_credentials.json',
        token_path='/home/claude-workflow/config/youtube_token.json'
    )
    
    result = await youtube.upload_video(
        video_path=test_video,
        title="Test Upload - Claude Workflow",
        description="Testing YouTube integration for automated video uploads.\n\n#test #automation",
        tags=['test', 'automation'],
        privacy_status='private'
    )
    
    if result['success']:
        print(f"\n✅ Success! Video uploaded:")
        print(f"   URL: {result['video_url']}")
        print(f"   ID: {result['video_id']}")
    else:
        print(f"\n❌ Failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_youtube())
PYEOF

chmod +x test_youtube.py
echo "✅ Created test_youtube.py"

# Step 4: Install required packages
echo -e "\n4️⃣ Installing Google API packages..."
pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client --break-system-packages

# Summary
echo -e "\n✅ YouTube setup complete!"
echo "=========================="
echo ""
echo "Files created:"
echo "  - youtube_auth_console.py (for authentication)"
echo "  - src/mcp/youtube_mcp.py (YouTube functionality)"
echo "  - test_youtube.py (test upload script)"
echo ""
echo "Next steps:"
echo "1. Run: python3 youtube_auth_console.py"
echo "2. Follow the browser authentication"
echo "3. Run: python3 test_youtube.py"
