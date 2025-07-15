#!/usr/bin/env python3
"""
Instagram Token Auto-Refresh Script
Can be run via cron to automatically refresh tokens before expiry
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
sys.path.append('/home/claude-workflow')

from instagram_token_manager import InstagramTokenManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/claude-workflow/logs/instagram_token_refresh.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def auto_refresh_token():
    """Automatically refresh Instagram token if needed"""
    
    logger.info("Starting Instagram token auto-refresh check...")
    
    manager = InstagramTokenManager()
    
    try:
        # Check current status
        status = await manager.check_token_status()
        
        if not status.get('has_token'):
            logger.warning("No Instagram token found. Manual authentication required.")
            return {
                'success': False,
                'action': 'manual_auth_required',
                'message': 'No token found. Please authenticate manually.'
            }
        
        # Validate token
        validation = await manager.validate_token()
        
        if not validation.get('valid'):
            logger.error("Instagram token is invalid. Manual re-authentication required.")
            return {
                'success': False,
                'action': 'reauth_required',
                'message': 'Token is invalid. Please re-authenticate.'
            }
        
        # Check if refresh is needed
        cache_data = status.get('cached_data', {})
        days_remaining = cache_data.get('days_remaining')
        
        if days_remaining is None:
            # No cache data, try to refresh to get proper expiry info
            logger.info("No expiry data found. Attempting refresh to get token info...")
            refresh_result = await manager.refresh_token()
            
            if refresh_result.get('success'):
                logger.info(f"Token refreshed successfully. Expires: {refresh_result.get('expires_at')}")
                return {
                    'success': True,
                    'action': 'refreshed',
                    'expires_at': refresh_result.get('expires_at'),
                    'days_remaining': refresh_result.get('expires_in_days')
                }
            else:
                logger.warning(f"Refresh failed: {refresh_result.get('error')}")
                return {
                    'success': False,
                    'action': 'refresh_failed',
                    'error': refresh_result.get('error')
                }
        
        elif days_remaining < 30:
            # Token expiring soon, refresh it
            logger.info(f"Token expires in {days_remaining} days. Refreshing...")
            refresh_result = await manager.refresh_token()
            
            if refresh_result.get('success'):
                logger.info(f"Token refreshed successfully. New expiry: {refresh_result.get('expires_at')}")
                return {
                    'success': True,
                    'action': 'refreshed',
                    'old_days_remaining': days_remaining,
                    'new_expires_at': refresh_result.get('expires_at'),
                    'new_days_remaining': refresh_result.get('expires_in_days')
                }
            else:
                logger.error(f"Token refresh failed: {refresh_result.get('error')}")
                return {
                    'success': False,
                    'action': 'refresh_failed',
                    'error': refresh_result.get('error')
                }
        
        else:
            # Token still valid
            logger.info(f"Token is valid for {days_remaining} more days. No refresh needed.")
            return {
                'success': True,
                'action': 'no_refresh_needed',
                'days_remaining': days_remaining,
                'expires_at': cache_data.get('expires_at')
            }
            
    except Exception as e:
        logger.error(f"Error during token refresh: {e}")
        return {
            'success': False,
            'action': 'error',
            'error': str(e)
        }


def setup_cron():
    """Print cron setup instructions"""
    print("\n📅 Cron Setup Instructions")
    print("=" * 50)
    print("\nTo automatically refresh Instagram tokens, add this to your crontab:")
    print("\n# Run Instagram token refresh daily at 3 AM")
    print("0 3 * * * /usr/bin/python3 /home/claude-workflow/src/instagram_token_refresh.py >> /home/claude-workflow/logs/cron_instagram.log 2>&1")
    print("\nTo edit crontab:")
    print("crontab -e")
    print("\nTo view current crontab:")
    print("crontab -l")
    print("\n" + "=" * 50)


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Instagram Token Auto-Refresh')
    parser.add_argument('--setup-cron', action='store_true', help='Show cron setup instructions')
    
    args = parser.parse_args()
    
    if args.setup_cron:
        setup_cron()
    else:
        result = await auto_refresh_token()
        
        # Print result summary
        print("\n📊 Instagram Token Refresh Summary")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Success: {'✅' if result.get('success') else '❌'}")
        print(f"Action: {result.get('action')}")
        
        if result.get('days_remaining'):
            print(f"Days remaining: {result['days_remaining']}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        print("=" * 50)
        
        # Log to file
        with open('/home/claude-workflow/logs/instagram_token_status.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'result': result
            }, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())