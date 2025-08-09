#!/usr/bin/env python3
"""
Check All Authentication Status
================================

This script checks the authentication status for all platforms:
- Google Drive (OAuth)
- YouTube (OAuth)
- Instagram (Long-lived token)
- WordPress (Basic auth)
"""

import json
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

sys.path.append('/home/claude-workflow')

def check_google_drive_status():
    """Check Google Drive token status"""
    try:
        from src.utils.google_drive_token_manager import GoogleDriveTokenManager
        
        manager = GoogleDriveTokenManager()
        status = manager.get_token_status()
        
        if status['status'] == 'VALID':
            minutes = status.get('minutes_until_expiry', 0)
            print(f"{Fore.GREEN}✅ Google Drive: Valid for {minutes:.0f} minutes")
        elif status['status'] == 'NEEDS_REFRESH':
            print(f"{Fore.YELLOW}⚠️  Google Drive: Needs refresh (will auto-refresh at workflow start)")
        elif status['status'] == 'EXPIRED':
            print(f"{Fore.YELLOW}⚠️  Google Drive: Expired (will auto-refresh at workflow start)")
        else:
            print(f"{Fore.RED}❌ Google Drive: {status['status']}")
            
    except Exception as e:
        print(f"{Fore.RED}❌ Google Drive: Error checking status - {e}")

def check_youtube_status():
    """Check YouTube token status"""
    try:
        # Load config
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
            
        from src.utils.youtube_auth_manager import YouTubeAuthManager
        
        manager = YouTubeAuthManager(config)
        status = manager.get_token_status()
        
        if status['status'] == 'VALID':
            minutes = status.get('minutes_until_expiry', 0)
            print(f"{Fore.GREEN}✅ YouTube: Valid for {minutes:.0f} minutes")
        elif status['status'] == 'NEEDS_REFRESH':
            print(f"{Fore.YELLOW}⚠️  YouTube: Needs refresh (will auto-refresh at workflow start)")
        elif status['status'] == 'EXPIRED':
            print(f"{Fore.YELLOW}⚠️  YouTube: Expired (will auto-refresh at workflow start)")
        else:
            print(f"{Fore.RED}❌ YouTube: {status['status']}")
            
    except Exception as e:
        print(f"{Fore.RED}❌ YouTube: Error checking status - {e}")

def check_instagram_status():
    """Check Instagram long-lived token status"""
    try:
        token_file = '/home/claude-workflow/config/instagram_token_cache.json'
        
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            expires_at = datetime.fromisoformat(token_data['expires_at'])
            now = datetime.now()
            
            days_remaining = (expires_at - now).days
            
            if days_remaining > 7:
                print(f"{Fore.GREEN}✅ Instagram: Valid for {days_remaining} days (expires {expires_at.date()})")
            elif days_remaining > 0:
                print(f"{Fore.YELLOW}⚠️  Instagram: Only {days_remaining} days remaining! (expires {expires_at.date()})")
                print(f"   {Fore.YELLOW}Consider refreshing the long-lived token soon")
            else:
                print(f"{Fore.RED}❌ Instagram: Token expired! Needs manual renewal")
        else:
            # Check if using direct access token from config
            with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
                config = json.load(f)
            
            if config.get('instagram_access_token'):
                print(f"{Fore.YELLOW}⚠️  Instagram: Using access token from config (expiry unknown)")
                print(f"   Consider implementing token caching for better monitoring")
            else:
                print(f"{Fore.RED}❌ Instagram: No token configured")
                
    except Exception as e:
        print(f"{Fore.RED}❌ Instagram: Error checking status - {e}")

def check_wordpress_status():
    """Check WordPress authentication status"""
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        if config.get('wordpress_user') and config.get('wordpress_password'):
            print(f"{Fore.GREEN}✅ WordPress: Basic auth configured (never expires)")
            print(f"   User: {config['wordpress_user']}")
            print(f"   URL: {config.get('wordpress_url', 'Not set')}")
        else:
            print(f"{Fore.RED}❌ WordPress: Missing credentials")
            
    except Exception as e:
        print(f"{Fore.RED}❌ WordPress: Error checking status - {e}")

def main():
    """Check all authentication statuses"""
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}🔐 AUTHENTICATION STATUS CHECK")
    print("="*60)
    
    print(f"\n{Style.BRIGHT}OAuth Tokens (Auto-refresh at workflow start):")
    print("-"*40)
    check_google_drive_status()
    check_youtube_status()
    
    print(f"\n{Style.BRIGHT}Long-Lived Tokens:")
    print("-"*40)
    check_instagram_status()
    
    print(f"\n{Style.BRIGHT}Basic Authentication:")
    print("-"*40)
    check_wordpress_status()
    
    print("\n" + "="*60)
    print(f"{Fore.CYAN}{Style.BRIGHT}📋 SUMMARY")
    print("="*60)
    
    print(f"""
{Fore.WHITE}Token Refresh Schedule:
- Google Drive & YouTube: Auto-refresh every workflow run
- Instagram: Manual refresh needed every 60 days
- WordPress: No refresh needed (basic auth)

{Fore.WHITE}Workflow Compatibility:
- 3x daily runs: {Fore.GREEN}✅ Fully supported
- OAuth tokens refresh automatically
- Long-lived tokens last weeks/months
- Basic auth never expires
    """)
    
    print("="*60)

if __name__ == "__main__":
    main()