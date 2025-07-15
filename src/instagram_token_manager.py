#!/usr/bin/env python3
"""
Instagram Token Manager - Handles long-lived token generation, storage, and refresh
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.instagram_server import InstagramMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramTokenManager:
    """Manages Instagram access tokens including long-lived tokens"""
    
    def __init__(self, config_path: str = '/home/claude-workflow/config/api_keys.json'):
        self.config_path = config_path
        self.token_cache_path = '/home/claude-workflow/config/instagram_token_cache.json'
        self.config = self._load_config()
        self.server = None
        
    def _load_config(self) -> dict:
        """Load configuration from file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("✅ Config saved successfully")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _load_token_cache(self) -> dict:
        """Load token cache"""
        if os.path.exists(self.token_cache_path):
            try:
                with open(self.token_cache_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_token_cache(self, cache: dict):
        """Save token cache"""
        try:
            with open(self.token_cache_path, 'w') as f:
                json.dump(cache, f, indent=2)
            logger.info("✅ Token cache saved")
        except Exception as e:
            logger.error(f"Failed to save token cache: {e}")
    
    async def authenticate_with_code(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate with Instagram using authorization code"""
        try:
            self.server = InstagramMCPServer(
                app_id=self.config['instagram_app_id'],
                app_secret=self.config['instagram_app_secret']
            )
            
            # Exchange code for token
            result = await self.server.authenticate(auth_code=auth_code)
            
            if 'error' in result:
                return result
            
            # Save tokens
            short_token = result.get('access_token')
            long_token = result.get('long_lived_token')
            
            if long_token:
                # Save long-lived token to config
                self.config['instagram_access_token'] = long_token
                self._save_config()
                
                # Save to cache with metadata
                cache = {
                    'long_lived_token': long_token,
                    'short_lived_token': short_token,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(days=60)).isoformat(),
                    'user_id': result.get('user_id'),
                    'permissions': result.get('permissions', [])
                }
                self._save_token_cache(cache)
                
                logger.info("✅ Long-lived token obtained and saved!")
                logger.info(f"   Token expires: {cache['expires_at']}")
                
                return {
                    'success': True,
                    'long_lived_token': long_token,
                    'expires_at': cache['expires_at'],
                    'message': 'Authentication successful! Long-lived token saved.'
                }
            else:
                # Only got short-lived token
                self.config['instagram_access_token'] = short_token
                self._save_config()
                
                return {
                    'success': True,
                    'short_lived_token': short_token,
                    'message': 'Got short-lived token. Run refresh_token() to get long-lived token.'
                }
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {'error': str(e)}
        finally:
            if self.server:
                await self.server.close()
    
    async def refresh_token(self) -> Dict[str, Any]:
        """Refresh the access token to get a new long-lived token"""
        try:
            # Load current token
            current_token = self.config.get('instagram_access_token')
            if not current_token:
                return {'error': 'No access token found. Please authenticate first.'}
            
            # Check if token is about to expire
            cache = self._load_token_cache()
            if cache.get('expires_at'):
                expires_at = datetime.fromisoformat(cache['expires_at'])
                days_until_expiry = (expires_at - datetime.now()).days
                
                if days_until_expiry > 30:
                    return {
                        'success': True,
                        'message': f'Token still valid for {days_until_expiry} days. No refresh needed.',
                        'expires_at': cache['expires_at']
                    }
            
            # Initialize server
            self.server = InstagramMCPServer(
                app_id=self.config['instagram_app_id'],
                app_secret=self.config['instagram_app_secret'],
                access_token=current_token
            )
            
            # Refresh token
            logger.info("🔄 Refreshing Instagram access token...")
            
            client = httpx.AsyncClient()
            try:
                url = "https://graph.instagram.com/refresh_access_token"
                params = {
                    "grant_type": "ig_refresh_token",
                    "access_token": current_token
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    result = response.json()
                    new_token = result.get('access_token')
                    expires_in = result.get('expires_in', 5184000)  # Default 60 days
                    
                    # Save new token
                    self.config['instagram_access_token'] = new_token
                    self._save_config()
                    
                    # Update cache
                    cache = {
                        'long_lived_token': new_token,
                        'refreshed_at': datetime.now().isoformat(),
                        'expires_at': (datetime.now() + timedelta(seconds=expires_in)).isoformat(),
                        'expires_in_seconds': expires_in,
                        'expires_in_days': expires_in // 86400
                    }
                    self._save_token_cache(cache)
                    
                    logger.info("✅ Token refreshed successfully!")
                    logger.info(f"   New token expires in {cache['expires_in_days']} days")
                    
                    return {
                        'success': True,
                        'new_token': new_token,
                        'expires_at': cache['expires_at'],
                        'expires_in_days': cache['expires_in_days'],
                        'message': 'Token refreshed successfully!'
                    }
                else:
                    error_data = response.json()
                    return {
                        'error': error_data.get('error', {}).get('message', 'Unknown error'),
                        'details': error_data
                    }
                    
            finally:
                await client.aclose()
                
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {'error': str(e)}
        finally:
            if self.server:
                await self.server.close()
    
    async def get_auth_url(self) -> str:
        """Get Instagram authorization URL"""
        auth_url = (
            f"https://api.instagram.com/oauth/authorize?"
            f"client_id={self.config['instagram_app_id']}"
            f"&redirect_uri=http://localhost:8080/callback"
            f"&scope=user_profile,user_media"
            f"&response_type=code"
        )
        return auth_url
    
    async def check_token_status(self) -> Dict[str, Any]:
        """Check current token status"""
        try:
            current_token = self.config.get('instagram_access_token')
            if not current_token:
                return {
                    'has_token': False,
                    'message': 'No Instagram access token found'
                }
            
            cache = self._load_token_cache()
            
            status = {
                'has_token': True,
                'token_preview': f"{current_token[:20]}...{current_token[-10:]}",
                'cached_data': {}
            }
            
            if cache:
                if cache.get('expires_at'):
                    expires_at = datetime.fromisoformat(cache['expires_at'])
                    days_remaining = (expires_at - datetime.now()).days
                    
                    status['cached_data'] = {
                        'expires_at': cache['expires_at'],
                        'days_remaining': days_remaining,
                        'needs_refresh': days_remaining < 30,
                        'created_at': cache.get('created_at'),
                        'refreshed_at': cache.get('refreshed_at')
                    }
                    
                    if days_remaining < 0:
                        status['message'] = '⚠️ Token has expired! Please re-authenticate.'
                    elif days_remaining < 7:
                        status['message'] = f'⚠️ Token expires in {days_remaining} days! Refresh recommended.'
                    elif days_remaining < 30:
                        status['message'] = f'Token expires in {days_remaining} days. Consider refreshing.'
                    else:
                        status['message'] = f'✅ Token is valid for {days_remaining} more days.'
            else:
                status['message'] = 'Token found but no cache data. Consider refreshing.'
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    async def validate_token(self) -> Dict[str, Any]:
        """Validate current token by making a test API call"""
        try:
            current_token = self.config.get('instagram_access_token')
            if not current_token:
                return {'valid': False, 'error': 'No token found'}
            
            # Test token with a simple API call
            client = httpx.AsyncClient()
            try:
                url = "https://graph.instagram.com/me"
                params = {
                    "fields": "id,username",
                    "access_token": current_token
                }
                
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        'valid': True,
                        'user_id': user_data.get('id'),
                        'username': user_data.get('username'),
                        'message': '✅ Token is valid and working!'
                    }
                else:
                    error_data = response.json()
                    return {
                        'valid': False,
                        'error': error_data.get('error', {}).get('message', 'Invalid token'),
                        'details': error_data
                    }
                    
            finally:
                await client.aclose()
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}


# CLI functions for easy management
async def main():
    """Main CLI interface for token management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Instagram Token Manager')
    parser.add_argument('command', choices=['status', 'auth-url', 'authenticate', 'refresh', 'validate'],
                       help='Command to execute')
    parser.add_argument('--code', help='Authorization code for authenticate command')
    
    args = parser.parse_args()
    
    manager = InstagramTokenManager()
    
    if args.command == 'status':
        result = await manager.check_token_status()
        print(json.dumps(result, indent=2))
        
    elif args.command == 'auth-url':
        url = await manager.get_auth_url()
        print(f"\n🔗 Visit this URL to authenticate:")
        print(f"   {url}\n")
        print("📝 After authorization, you'll be redirected to:")
        print("   http://localhost:8080/callback?code=YOUR_AUTH_CODE")
        print("\n✅ Copy the code and run:")
        print("   python3 instagram_token_manager.py authenticate --code YOUR_AUTH_CODE\n")
        
    elif args.command == 'authenticate':
        if not args.code:
            print("❌ Please provide authorization code with --code parameter")
            return
        result = await manager.authenticate_with_code(args.code)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'refresh':
        result = await manager.refresh_token()
        print(json.dumps(result, indent=2))
        
    elif args.command == 'validate':
        result = await manager.validate_token()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())