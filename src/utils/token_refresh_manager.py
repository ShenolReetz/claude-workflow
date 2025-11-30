#!/usr/bin/env python3
"""
Token Refresh Manager
=====================
Manages automatic refresh of OAuth tokens for YouTube and Google Drive
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio
import aiohttp

# Add project root to path
sys.path.append('/home/claude-workflow')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)


class TokenRefreshManager:
    """Manages OAuth token refresh for all services"""
    
    def __init__(self, config_dir: str = '/home/claude-workflow/config'):
        self.config_dir = Path(config_dir)
        self.tokens_refreshed = []
        self.tokens_failed = []
        
    def refresh_youtube_token(self) -> bool:
        """Refresh YouTube OAuth token"""
        try:
            token_path = self.config_dir / 'youtube_token.json'
            creds_path = self.config_dir / 'youtube_credentials.json'
            
            if not token_path.exists():
                logger.error("YouTube token file not found")
                return False
            
            # Load current token
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            # Create credentials object
            creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Check if token needs refresh
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    logger.info("🔄 Refreshing YouTube token...")
                    creds.refresh(Request())
                    
                    # Save refreshed token
                    token_data['token'] = creds.token
                    token_data['expiry'] = creds.expiry.isoformat() if creds.expiry else None
                    
                    with open(token_path, 'w') as f:
                        json.dump(token_data, f, indent=2)
                    
                    logger.info("✅ YouTube token refreshed successfully")
                    self.tokens_refreshed.append('YouTube')
                    return True
                else:
                    logger.error("❌ YouTube token cannot be refreshed - missing refresh token")
                    self.tokens_failed.append('YouTube')
                    return False
            else:
                logger.info("✅ YouTube token is still valid")
                return True
                
        except Exception as e:
            logger.error(f"Error refreshing YouTube token: {e}")
            self.tokens_failed.append('YouTube')
            return False
    
    def refresh_google_drive_token(self) -> bool:
        """Refresh Google Drive OAuth token"""
        try:
            token_path = self.config_dir / 'google_drive_token.json'
            
            if not token_path.exists():
                logger.warning("Google Drive token file not found - may not be needed for local storage")
                return True  # Not critical for local storage workflow
            
            # Load current token
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            
            # Create credentials object
            creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Check if token needs refresh
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    logger.info("🔄 Refreshing Google Drive token...")
                    creds.refresh(Request())
                    
                    # Save refreshed token
                    token_data['token'] = creds.token
                    token_data['expiry'] = creds.expiry.isoformat() if creds.expiry else None
                    
                    with open(token_path, 'w') as f:
                        json.dump(token_data, f, indent=2)
                    
                    logger.info("✅ Google Drive token refreshed successfully")
                    self.tokens_refreshed.append('Google Drive')
                    return True
                else:
                    logger.warning("⚠️ Google Drive token cannot be refreshed - not critical for local storage")
                    return True  # Not critical
            else:
                logger.info("✅ Google Drive token is still valid")
                return True
                
        except Exception as e:
            logger.warning(f"Google Drive token refresh skipped (not critical): {e}")
            return True  # Not critical for local storage
    
    def check_instagram_token(self) -> bool:
        """Check Instagram access token validity"""
        try:
            # Load config
            config_path = self.config_dir / 'api_keys.json'
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            access_token = config.get('instagram_access_token')
            if not access_token:
                logger.warning("Instagram access token not found")
                return False
            
            # Instagram tokens are long-lived (60 days)
            # For now, just check if it exists
            logger.info("✅ Instagram access token configured")
            return True
            
        except Exception as e:
            logger.error(f"Error checking Instagram token: {e}")
            return False
    
    def refresh_all_tokens(self) -> Dict:
        """Refresh all OAuth tokens"""
        logger.info("""
╔════════════════════════════════════════════════════════════╗
║           TOKEN REFRESH MANAGER                           ║
╚════════════════════════════════════════════════════════════╝
""")
        
        results = {
            'youtube': self.refresh_youtube_token(),
            'google_drive': self.refresh_google_drive_token(),
            'instagram': self.check_instagram_token()
        }
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("TOKEN REFRESH SUMMARY")
        logger.info("="*60)
        
        if self.tokens_refreshed:
            logger.info(f"✅ Refreshed: {', '.join(self.tokens_refreshed)}")
        
        if self.tokens_failed:
            logger.error(f"❌ Failed: {', '.join(self.tokens_failed)}")
        
        all_success = all(results.values())
        if all_success:
            logger.info("\n🎉 All tokens are valid and ready!")
        else:
            logger.warning("\n⚠️ Some tokens need attention")
        
        return results
    
    def setup_auto_refresh_cron(self) -> str:
        """Generate cron job command for daily token refresh"""
        cron_command = "0 5 * * * /usr/bin/python3 /home/claude-workflow/src/utils/token_refresh_manager.py"
        
        logger.info("\nTo setup automatic daily token refresh, add this to crontab:")
        logger.info(f"  {cron_command}")
        logger.info("\nRun: crontab -e")
        logger.info("Then add the line above")
        
        return cron_command


def main():
    """Main entry point for token refresh"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manager = TokenRefreshManager()
    results = manager.refresh_all_tokens()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        # Check if only non-critical tokens failed
        if results['youtube']:  # YouTube is critical
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()