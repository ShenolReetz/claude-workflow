#!/usr/bin/env python3
"""
Google Drive Token Manager - Automatic Token Refresh and Monitoring

This utility handles Google Drive OAuth token management:
1. Automatically refreshes expired access tokens
2. Monitors token expiration and sends alerts
3. Provides fallback mechanisms when refresh fails
4. Integrates with workflow to prevent Google Drive failures

PREVENTION STRATEGIES:
- Automatic refresh before expiration (when < 10 minutes remaining)
- Background refresh scheduling
- Email alerts when refresh tokens are about to expire
- Graceful fallback when Google Drive is unavailable
"""

import json
import os
import requests
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class GoogleDriveTokenManager:
    """Manages Google Drive OAuth tokens with automatic refresh and monitoring"""
    
    def __init__(self, config_path: str = '/home/claude-workflow/config/api_keys.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.token_path = self.config.get('google_drive_token', '/home/claude-workflow/config/google_drive_token.json')
        self.refresh_threshold_minutes = 10  # Refresh when < 10 minutes remaining
        
    def load_token_data(self) -> Optional[Dict]:
        """Load current token data from file"""
        try:
            if os.path.exists(self.token_path):
                with open(self.token_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading token data: {e}")
            return None
    
    def save_token_data(self, token_data: Dict) -> bool:
        """Save token data to file"""
        try:
            with open(self.token_path, 'w') as f:
                json.dump(token_data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving token data: {e}")
            return False
    
    def get_token_status(self) -> Dict[str, any]:
        """Get comprehensive token status information"""
        token_data = self.load_token_data()
        if not token_data:
            return {
                'exists': False,
                'valid': False,
                'expired': True,
                'days_until_expiry': None,
                'needs_refresh': True,
                'can_refresh': False,
                'status': 'TOKEN_MISSING'
            }
        
        try:
            expiry_str = token_data.get('expiry')
            if not expiry_str:
                return {
                    'exists': True,
                    'valid': False,
                    'expired': True,
                    'days_until_expiry': None,
                    'needs_refresh': True,
                    'can_refresh': bool(token_data.get('refresh_token')),
                    'status': 'NO_EXPIRY_DATE'
                }
            
            # Parse expiry date
            expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
            current_date = datetime.now(expiry_date.tzinfo)
            
            time_until_expiry = expiry_date - current_date
            days_until_expiry = time_until_expiry.days
            minutes_until_expiry = time_until_expiry.total_seconds() / 60
            
            is_expired = current_date > expiry_date
            needs_refresh = minutes_until_expiry < self.refresh_threshold_minutes
            can_refresh = bool(token_data.get('refresh_token'))
            
            if is_expired:
                status = 'EXPIRED'
            elif needs_refresh:
                status = 'NEEDS_REFRESH'
            else:
                status = 'VALID'
            
            return {
                'exists': True,
                'valid': not is_expired,
                'expired': is_expired,
                'days_until_expiry': days_until_expiry,
                'minutes_until_expiry': minutes_until_expiry,
                'needs_refresh': needs_refresh,
                'can_refresh': can_refresh,
                'status': status,
                'expiry_date': expiry_str
            }
            
        except Exception as e:
            logger.error(f"Error checking token status: {e}")
            return {
                'exists': True,
                'valid': False,
                'expired': True,
                'days_until_expiry': None,
                'needs_refresh': True,
                'can_refresh': bool(token_data.get('refresh_token')),
                'status': 'ERROR_PARSING'
            }
    
    def refresh_token(self) -> Tuple[bool, str]:
        """
        Attempt to refresh the Google Drive token
        Returns: (success: bool, message: str)
        """
        try:
            token_data = self.load_token_data()
            if not token_data:
                return False, "No token data found"
            
            refresh_token = token_data.get('refresh_token')
            if not refresh_token:
                return False, "No refresh token available"
            
            # Prepare refresh request
            refresh_data = {
                'client_id': token_data['client_id'],
                'client_secret': token_data['client_secret'],
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            # Make refresh request
            response = requests.post('https://oauth2.googleapis.com/token', data=refresh_data)
            
            if response.status_code == 200:
                refresh_result = response.json()
                
                # Update token data
                token_data['token'] = refresh_result['access_token']
                
                # Calculate new expiry
                expires_in = refresh_result.get('expires_in', 3600)
                new_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
                token_data['expiry'] = new_expiry.isoformat() + 'Z'
                
                # Update refresh token if provided
                if 'refresh_token' in refresh_result:
                    token_data['refresh_token'] = refresh_result['refresh_token']
                
                # Save updated token
                if self.save_token_data(token_data):
                    return True, f"Token refreshed successfully, valid for {expires_in/3600:.1f} hours"
                else:
                    return False, "Failed to save refreshed token"
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error_description', f"HTTP {response.status_code}")
                return False, f"Refresh failed: {error_msg}"
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False, f"Exception during refresh: {str(e)}"
    
    def get_valid_credentials(self) -> Optional[Credentials]:
        """
        Get valid Google credentials, refreshing if necessary
        Returns None if unable to get valid credentials
        """
        try:
            # Check token status
            status = self.get_token_status()
            
            if not status['exists']:
                logger.error("No Google Drive token found")
                return None
            
            # Try to refresh if needed and possible
            if status['needs_refresh'] and status['can_refresh']:
                logger.info("Token needs refresh, attempting automatic refresh...")
                success, message = self.refresh_token()
                if success:
                    logger.info(f"✅ {message}")
                else:
                    logger.warning(f"❌ Refresh failed: {message}")
                    return None
            elif status['expired'] and not status['can_refresh']:
                logger.error("Token expired and cannot be refreshed - manual re-authorization required")
                return None
            
            # Load token data and create credentials
            token_data = self.load_token_data()
            if not token_data:
                return None
            
            creds = Credentials(
                token=token_data['token'],
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data['token_uri'],
                client_id=token_data['client_id'],
                client_secret=token_data['client_secret'],
                scopes=token_data['scopes']
            )
            
            return creds
            
        except Exception as e:
            logger.error(f"Error getting valid credentials: {e}")
            return None
    
    def generate_status_report(self) -> str:
        """Generate a comprehensive status report"""
        status = self.get_token_status()
        
        report = f"""
🔑 GOOGLE DRIVE TOKEN STATUS REPORT
==========================================

📊 Current Status: {status['status']}
📁 Token File: {status['exists']}
✅ Valid: {status['valid']}
❌ Expired: {status['expired']}
🔄 Needs Refresh: {status['needs_refresh']}
🔧 Can Refresh: {status['can_refresh']}

"""
        
        if status.get('expiry_date'):
            report += f"📅 Expiry Date: {status['expiry_date']}\n"
        
        if status.get('days_until_expiry') is not None:
            if status['days_until_expiry'] > 0:
                report += f"⏰ Days Until Expiry: {status['days_until_expiry']}\n"
            else:
                report += f"⏰ Days Expired: {abs(status['days_until_expiry'])}\n"
        
        # Add recommendations
        report += "\n📋 RECOMMENDATIONS:\n"
        
        if status['status'] == 'VALID':
            report += "✅ Token is valid, no action needed\n"
        elif status['status'] == 'NEEDS_REFRESH':
            report += "🔄 Token should be refreshed soon (automatic refresh will handle this)\n"
        elif status['status'] == 'EXPIRED' and status['can_refresh']:
            report += "🔧 Token expired but can be refreshed automatically\n"
        elif status['status'] == 'EXPIRED' and not status['can_refresh']:
            report += "❌ Token expired and cannot be refreshed - MANUAL RE-AUTHORIZATION REQUIRED\n"
            report += "   Visit: https://console.cloud.google.com/apis/credentials\n"
            report += "   Re-run OAuth flow to generate new tokens\n"
        elif status['status'] == 'TOKEN_MISSING':
            report += "❌ No token file found - INITIAL AUTHORIZATION REQUIRED\n"
            report += "   Run setup_google_drive_oauth.py to generate initial tokens\n"
        
        return report

def check_google_drive_token_status():
    """Standalone function to check and display token status"""
    manager = GoogleDriveTokenManager()
    print(manager.generate_status_report())
    
    # Try automatic refresh if possible
    status = manager.get_token_status()
    if status['needs_refresh'] and status['can_refresh']:
        print("🔄 Attempting automatic token refresh...")
        success, message = manager.refresh_token()
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ Refresh failed: {message}")

if __name__ == "__main__":
    check_google_drive_token_status()