# Update the Google Drive agent to support service account credentials
import re

with open('src/mcp/google_drive_agent_mcp.py', 'r') as f:
    content = f.read()

# Replace the _initialize_service method to handle service accounts
new_init_service = '''    def _initialize_service(self):
        """Initialize Google Drive service with authentication"""
        import os
        from google.oauth2 import service_account
        
        creds = None
        
        # Check if we have service account credentials
        if os.path.exists(self.credentials_path):
            try:
                # Try to load as service account
                creds = service_account.Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=self.SCOPES
                )
                logger.info("✅ Using service account credentials")
            except Exception as e:
                logger.error(f"Failed to load service account: {e}")
                # Fall back to OAuth flow
                token_path = 'token.json'
                
                if os.path.exists(token_path):
                    creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                    
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        logger.info("✅ Google Drive service initialized")'''

# Find and replace the _initialize_service method
pattern = r'def _initialize_service\(self\):.*?logger\.info\("✅ Google Drive service initialized"\)'
content = re.sub(pattern, new_init_service, content, flags=re.DOTALL)

# Add the service account import at the top if not already there
if 'from google.oauth2 import service_account' not in content:
    content = content.replace(
        'from google.oauth2.credentials import Credentials',
        'from google.oauth2.credentials import Credentials\nfrom google.oauth2 import service_account'
    )

# Write back
with open('src/mcp/google_drive_agent_mcp.py', 'w') as f:
    f.write(content)

print("✅ Updated Google Drive agent to support service account credentials")
