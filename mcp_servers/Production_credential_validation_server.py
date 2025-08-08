#!/usr/bin/env python3
"""
Production Credential Validation MCP Server
===========================================

Comprehensive validation of all API keys, tokens, and credentials before workflow execution.
Prevents workflow failures by checking all authentication requirements upfront.

VALIDATION CATEGORIES:
1. API Keys (OpenAI, Anthropic, ElevenLabs, ScrapingDog, etc.)
2. OAuth Tokens (Google Drive, YouTube)  
3. Service Credentials (WordPress, Instagram, Amazon)
4. File-based Credentials (JSON files, certificates)

FEATURES:
- Pre-workflow validation checkpoint
- Real-time token expiry monitoring
- Automatic refresh attempts
- Detailed failure reporting
- Health scoring system
"""

import json
import os
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import aiohttp
from dataclasses import dataclass
from enum import Enum

# Import token managers
import sys
sys.path.append('/home/claude-workflow')
from src.utils.google_drive_token_manager import GoogleDriveTokenManager
from src.utils.youtube_auth_manager import YouTubeAuthManager

class CredentialStatus(Enum):
    VALID = "valid"
    EXPIRED = "expired" 
    INVALID = "invalid"
    MISSING = "missing"
    REFRESH_NEEDED = "refresh_needed"
    UNKNOWN = "unknown"

@dataclass
class CredentialResult:
    name: str
    status: CredentialStatus
    message: str
    expires_in_days: Optional[int] = None
    can_refresh: bool = False
    health_score: int = 0  # 0-100
    usage_info: Optional[Dict[str, Any]] = None  # Usage/billing information

class ProductionCredentialValidationServer:
    """Comprehensive credential validation for production workflows"""
    
    def __init__(self, config_path: str = '/home/claude-workflow/config/api_keys.json'):
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.config = {}
        
        # Initialize token managers
        self.google_drive_manager = GoogleDriveTokenManager()
        
        # Validation results cache
        self.results: Dict[str, CredentialResult] = {}
        self.overall_health_score = 0
        self.critical_failures = []
        self.warnings = []
        
    async def _get_openai_usage_info(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get OpenAI API usage and billing information"""
        try:
            from datetime import datetime, timedelta
            
            # Get usage data for the last few days
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            total_requests = 0
            total_tokens_context = 0
            total_tokens_generated = 0
            dalle_requests = 0
            tts_requests = 0
            whisper_requests = 0
            models_used = set()
            
            # Check usage for yesterday and today
            for date in [yesterday, today]:
                try:
                    # Add timeout to prevent hanging
                    timeout = aiohttp.ClientTimeout(total=10)  # 10 second timeout
                    async with session.get(f'https://api.openai.com/v1/usage?date={date}', headers=headers, timeout=timeout) as response:
                        if response.status == 200:
                            usage_data = await response.json()
                            
                            # Process regular API usage (GPT models)
                            for item in usage_data.get('data', []):
                                total_requests += item.get('n_requests', 0)
                                total_tokens_context += item.get('n_context_tokens_total', 0)
                                total_tokens_generated += item.get('n_generated_tokens_total', 0)
                                if item.get('snapshot_id'):
                                    models_used.add(item['snapshot_id'])
                            
                            # Process DALL-E usage
                            for item in usage_data.get('dalle_api_data', []):
                                dalle_requests += item.get('n_requests', 0)
                            
                            # Process TTS usage
                            for item in usage_data.get('tts_api_data', []):
                                tts_requests += item.get('n_requests', 0)
                            
                            # Process Whisper usage
                            for item in usage_data.get('whisper_api_data', []):
                                whisper_requests += item.get('n_requests', 0)
                            
                except:
                    continue  # Skip if date fails
            
            total_tokens = total_tokens_context + total_tokens_generated
            
            return {
                'type': 'token_usage',
                'total_requests': total_requests,
                'total_tokens': total_tokens,
                'context_tokens': total_tokens_context,
                'generated_tokens': total_tokens_generated,
                'dalle_requests': dalle_requests,
                'tts_requests': tts_requests,
                'whisper_requests': whisper_requests,
                'models_used': list(models_used),
                'time_period': '48 hours',
                'status': 'Active usage tracking'
            }
            
        except Exception as e:
            return {'type': 'basic', 'status': 'API key valid', 'note': f'Usage tracking unavailable: {str(e)[:50]}'}
    
    async def _get_anthropic_usage_info(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get Anthropic API usage information"""
        try:
            # Anthropic doesn't have a public usage API yet
            return {'type': 'basic', 'status': 'API key valid', 'note': 'Check usage at console.anthropic.com'}
        except:
            return {'type': 'basic', 'status': 'API key valid', 'note': 'Usage info unavailable'}
    
    async def _get_elevenlabs_usage_info(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get ElevenLabs API usage information"""
        try:
            async with session.get('https://api.elevenlabs.io/v1/user/subscription', headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    character_count = data.get('character_count', 0)
                    character_limit = data.get('character_limit', 10000)
                    tier = data.get('tier', 'Free')
                    
                    usage_percent = (character_count / character_limit * 100) if character_limit > 0 else 0
                    remaining = character_limit - character_count
                    
                    return {
                        'type': 'character_usage',
                        'tier': tier,
                        'used': character_count,
                        'limit': character_limit,
                        'remaining': remaining,
                        'usage_percent': round(usage_percent, 1),
                        'status': 'Low usage' if usage_percent < 80 else 'High usage' if usage_percent < 95 else 'Critical'
                    }
            return {'type': 'basic', 'status': 'API key valid', 'note': 'Usage info unavailable'}
        except:
            return {'type': 'basic', 'status': 'API key valid', 'note': 'Usage info unavailable'}
    
    async def _get_scrapingdog_usage_info(self, session: aiohttp.ClientSession, api_key: str) -> Dict[str, Any]:
        """Get ScrapingDog API usage information"""
        try:
            # ScrapingDog account endpoint
            async with session.get(f'https://api.scrapingdog.com/account?api_key={api_key}') as response:
                if response.status == 200:
                    data = await response.json()
                    credits_used = data.get('requestUsed', 0)
                    credits_limit = data.get('requestLimit', 0)
                    credits_remaining = credits_limit - credits_used
                    
                    usage_percent = (credits_used / credits_limit * 100) if credits_limit > 0 else 0
                    
                    plan = data.get('pack', 'Unknown')
                    plan_type = data.get('pack_type', 'Unknown')
                    validity_days = data.get('validity', 0)
                    thread_count = data.get('threadCount', 0)
                    
                    return {
                        'type': 'credit_usage',
                        'used': credits_used,
                        'remaining': credits_remaining,
                        'limit': credits_limit,
                        'usage_percent': round(usage_percent, 1),
                        'plan': f"{plan} ({plan_type})",
                        'validity_days': validity_days,
                        'active_threads': thread_count,
                        'status': 'Low usage' if usage_percent < 80 else 'High usage' if usage_percent < 95 else 'Critical'
                    }
            return {'type': 'basic', 'status': 'API key valid', 'note': 'Usage info unavailable'}
        except:
            return {'type': 'basic', 'status': 'API key valid', 'note': 'Usage info unavailable'}
    
    async def _get_json2video_usage_info(self, session: aiohttp.ClientSession, headers: Dict) -> Dict[str, Any]:
        """Get JSON2Video API usage information"""
        try:
            async with session.get('https://api.json2video.com/v2/account', headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    plan = data.get('plan', {})
                    credits = data.get('credits', {})
                    
                    return {
                        'type': 'video_credits',
                        'plan': plan.get('name', 'Unknown'),
                        'credits_used': credits.get('used', 0),
                        'credits_limit': credits.get('limit', 0),
                        'videos_rendered': data.get('videos_rendered', 0),
                        'status': 'Active'
                    }
            return {'type': 'basic', 'status': 'API access', 'note': 'Usage info unavailable'}
        except:
            return {'type': 'basic', 'status': 'API access', 'note': 'Usage info unavailable'}
    
    def _get_usage_warnings(self, report: Dict[str, Any]) -> List[str]:
        """Generate usage-based warnings for high consumption or low remaining credits"""
        warnings = []
        
        for name, result in report['results'].items():
            usage = result.get('usage_info')
            if not usage:
                continue
                
            if usage.get('type') == 'character_usage':
                percent = usage.get('usage_percent', 0)
                remaining = usage.get('remaining', 0)
                service = result.get('name', name)
                
                if percent >= 90:
                    warnings.append(f"{service}: CRITICAL - {percent}% usage, only {remaining:,} characters remaining")
                elif percent >= 80:
                    warnings.append(f"{service}: HIGH usage - {percent}% used, {remaining:,} characters remaining")
                elif remaining < 10000:  # Less than 10k characters
                    warnings.append(f"{service}: LOW remaining - Only {remaining:,} characters left")
                    
            elif usage.get('type') == 'credit_usage':
                percent = usage.get('usage_percent', 0)
                remaining = usage.get('remaining', 0)
                service = result.get('name', name)
                
                if percent >= 90:
                    warnings.append(f"{service}: CRITICAL - {percent}% usage, only {remaining:,} credits remaining")
                elif percent >= 80:
                    warnings.append(f"{service}: HIGH usage - {percent}% used, {remaining:,} credits remaining")
                elif remaining < 1000:  # Less than 1000 credits (adjusted threshold)
                    warnings.append(f"{service}: LOW remaining - Only {remaining:,} credits left")
            
            elif usage.get('type') == 'token_usage':
                total_requests = usage.get('total_requests', 0)
                total_tokens = usage.get('total_tokens', 0)
                dalle_requests = usage.get('dalle_requests', 0)
                service = result.get('name', name)
                
                # High usage warnings for OpenAI
                if total_requests > 100:  # More than 100 requests in 48h
                    warnings.append(f"{service}: HIGH activity - {total_requests} requests in 48h")
                elif total_tokens > 50000:  # More than 50k tokens in 48h
                    warnings.append(f"{service}: HIGH token usage - {total_tokens:,} tokens in 48h")
                elif dalle_requests > 20:  # More than 20 DALL-E requests in 48h
                    warnings.append(f"{service}: HIGH DALL-E usage - {dalle_requests} image requests in 48h")
        
        return warnings
        
    async def validate_all_credentials(self) -> Dict[str, Any]:
        """
        Validate all credentials and return comprehensive report
        Returns: {
            'overall_status': 'ready|warning|failed',
            'health_score': 0-100,
            'results': {...},
            'critical_failures': [...],
            'warnings': [...],
            'can_proceed': bool
        }
        """
        self.logger.info("🔍 Starting comprehensive credential validation...")
        
        # Clear previous results
        self.results.clear()
        self.critical_failures.clear()
        self.warnings.clear()
        
        try:
            # Validate each category with individual timeouts
            self.logger.info("🔑 Starting API key validation...")
            await asyncio.wait_for(self._validate_api_keys(), timeout=120)  # 2 min timeout
            
            self.logger.info("🔐 Starting OAuth token validation...")
            await asyncio.wait_for(self._validate_oauth_tokens(), timeout=60)  # 1 min timeout
            
            self.logger.info("🌐 Starting service credentials validation...")
            await asyncio.wait_for(self._validate_service_credentials(), timeout=60)  # 1 min timeout
            
            self.logger.info("📁 Starting file credentials validation...")
            await asyncio.wait_for(self._validate_file_credentials(), timeout=30)  # 30 sec timeout
            
        except asyncio.TimeoutError as e:
            self.logger.error(f"❌ Credential validation timeout: {e}")
            # Add a timeout result
            self.results['timeout_error'] = CredentialResult(
                name="Validation Timeout",
                status=CredentialStatus.UNKNOWN,
                message="Credential validation process timed out - check network connectivity",
                health_score=0
            )
        except Exception as e:
            self.logger.error(f"❌ Credential validation error: {e}")
            # Add an error result
            self.results['validation_error'] = CredentialResult(
                name="Validation Error",
                status=CredentialStatus.UNKNOWN,
                message=f"Credential validation failed: {str(e)}",
                health_score=0
            )
        
        # Calculate overall health
        self._calculate_health_scores()
        
        # Generate report
        report = self._generate_validation_report()
        
        self.logger.info(f"✅ Validation complete. Health Score: {self.overall_health_score}/100")
        return report
    
    async def _validate_api_keys(self):
        """Validate all API keys with actual API calls"""
        self.logger.info("🔑 Validating API Keys...")
        
        # OpenAI API Key
        await self._validate_openai_api()
        
        # Anthropic API Key  
        await self._validate_anthropic_api()
        
        # ElevenLabs API Key
        await self._validate_elevenlabs_api()
        
        # ScrapingDog API Key
        await self._validate_scrapingdog_api()
        
        # JSON2Video API Key
        await self._validate_json2video_api()
        
        # Airtable API Key
        await self._validate_airtable_api()
    
    async def _validate_openai_api(self):
        """Validate OpenAI API key with a test call"""
        try:
            api_key = self.config.get('openai_api_key', '')
            
            if not api_key or api_key.startswith('sk-proj-YOUR-KEY'):
                self.results['openai'] = CredentialResult(
                    name="OpenAI API",
                    status=CredentialStatus.MISSING,
                    message="OpenAI API key not configured",
                    health_score=0
                )
                return
            
            # Test API call
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Create session with timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout for API calls
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # First check if API key is valid
                async with session.get('https://api.openai.com/v1/models', headers=headers) as response:
                    if response.status == 200:
                        # Get usage information
                        usage_info = await self._get_openai_usage_info(session, headers)
                        
                        self.results['openai'] = CredentialResult(
                            name="OpenAI API",
                            status=CredentialStatus.VALID,
                            message="OpenAI API key valid and active",
                            health_score=100,
                            usage_info=usage_info
                        )
                    elif response.status == 401:
                        self.results['openai'] = CredentialResult(
                            name="OpenAI API", 
                            status=CredentialStatus.INVALID,
                            message="OpenAI API key invalid or unauthorized",
                            health_score=0
                        )
                    else:
                        self.results['openai'] = CredentialResult(
                            name="OpenAI API",
                            status=CredentialStatus.UNKNOWN,
                            message=f"OpenAI API returned status {response.status}",
                            health_score=30
                        )
                        
        except Exception as e:
            self.results['openai'] = CredentialResult(
                name="OpenAI API",
                status=CredentialStatus.UNKNOWN,
                message=f"OpenAI validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_anthropic_api(self):
        """Validate Anthropic API key"""
        try:
            api_key = self.config.get('anthropic_api_key', '')
            
            if not api_key or api_key.startswith('sk-ant-api03-YOUR-KEY'):
                self.results['anthropic'] = CredentialResult(
                    name="Anthropic API",
                    status=CredentialStatus.MISSING,
                    message="Anthropic API key not configured",
                    health_score=0
                )
                return
            
            # Test API call with explicit timeout
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            test_payload = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 10,
                'messages': [{'role': 'user', 'content': 'test'}]
            }
            
            # Add explicit timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post('https://api.anthropic.com/v1/messages', 
                                      headers=headers, json=test_payload) as response:
                    if response.status == 200:
                        usage_info = await self._get_anthropic_usage_info(session, headers)
                        self.results['anthropic'] = CredentialResult(
                            name="Anthropic API",
                            status=CredentialStatus.VALID,
                            message="Anthropic API key valid and active",
                            health_score=100,
                            usage_info=usage_info
                        )
                    elif response.status == 401:
                        self.results['anthropic'] = CredentialResult(
                            name="Anthropic API",
                            status=CredentialStatus.INVALID,
                            message="Anthropic API key invalid or unauthorized", 
                            health_score=0
                        )
                    else:
                        self.results['anthropic'] = CredentialResult(
                            name="Anthropic API",
                            status=CredentialStatus.UNKNOWN,
                            message=f"Anthropic API returned status {response.status}",
                            health_score=30
                        )
                        
        except asyncio.TimeoutError:
            self.results['anthropic'] = CredentialResult(
                name="Anthropic API",
                status=CredentialStatus.UNKNOWN,
                message="Anthropic API validation timeout - check network connection",
                health_score=0
            )
        except Exception as e:
            self.results['anthropic'] = CredentialResult(
                name="Anthropic API",
                status=CredentialStatus.UNKNOWN,
                message=f"Anthropic validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_elevenlabs_api(self):
        """Validate ElevenLabs API key"""
        try:
            api_key = self.config.get('elevenlabs_api_key', '')
            
            if not api_key or api_key.startswith('sk_YOUR-KEY'):
                self.results['elevenlabs'] = CredentialResult(
                    name="ElevenLabs API",
                    status=CredentialStatus.MISSING,
                    message="ElevenLabs API key not configured",
                    health_score=0
                )
                return
            
            # Test API call with explicit timeout
            headers = {'xi-api-key': api_key}
            
            # Add explicit timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get('https://api.elevenlabs.io/v1/user', headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        character_count = user_data.get('subscription', {}).get('character_count', 0)
                        character_limit = user_data.get('subscription', {}).get('character_limit', 10000)
                        
                        # Get detailed usage info
                        usage_info = await self._get_elevenlabs_usage_info(session, headers)
                        
                        self.results['elevenlabs'] = CredentialResult(
                            name="ElevenLabs API",
                            status=CredentialStatus.VALID,
                            message=f"ElevenLabs API valid. Usage: {character_count}/{character_limit} chars",
                            health_score=100,
                            usage_info=usage_info
                        )
                    elif response.status == 401:
                        self.results['elevenlabs'] = CredentialResult(
                            name="ElevenLabs API",
                            status=CredentialStatus.INVALID,
                            message="ElevenLabs API key invalid or unauthorized",
                            health_score=0
                        )
                    else:
                        self.results['elevenlabs'] = CredentialResult(
                            name="ElevenLabs API",
                            status=CredentialStatus.UNKNOWN,
                            message=f"ElevenLabs API returned status {response.status}",
                            health_score=30
                        )
                        
        except asyncio.TimeoutError:
            self.results['elevenlabs'] = CredentialResult(
                name="ElevenLabs API",
                status=CredentialStatus.UNKNOWN,
                message="ElevenLabs API validation timeout - check network connection",
                health_score=0
            )
        except Exception as e:
            self.results['elevenlabs'] = CredentialResult(
                name="ElevenLabs API",
                status=CredentialStatus.UNKNOWN,
                message=f"ElevenLabs validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_scrapingdog_api(self):
        """Validate ScrapingDog API key"""
        try:
            api_key = self.config.get('scrapingdog_api_key', '')
            
            if not api_key or api_key == 'YOUR-KEY-HERE':
                self.results['scrapingdog'] = CredentialResult(
                    name="ScrapingDog API",
                    status=CredentialStatus.MISSING,
                    message="ScrapingDog API key not configured",
                    health_score=0
                )
                return
            
            # Test API call with explicit timeout
            test_url = f'https://api.scrapingdog.com/scrape?api_key={api_key}&url=https://httpbin.org/ip&dynamic=false'
            
            # Add explicit timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=20)  # 20 second timeout for scraping
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url) as response:
                    if response.status == 200:
                        # Get usage information
                        usage_info = await self._get_scrapingdog_usage_info(session, api_key)
                        
                        self.results['scrapingdog'] = CredentialResult(
                            name="ScrapingDog API",
                            status=CredentialStatus.VALID,
                            message="ScrapingDog API key valid and active",
                            health_score=100,
                            usage_info=usage_info
                        )
                    elif response.status == 401:
                        self.results['scrapingdog'] = CredentialResult(
                            name="ScrapingDog API",
                            status=CredentialStatus.INVALID,
                            message="ScrapingDog API key invalid or unauthorized",
                            health_score=0
                        )
                    else:
                        self.results['scrapingdog'] = CredentialResult(
                            name="ScrapingDog API",
                            status=CredentialStatus.UNKNOWN,
                            message=f"ScrapingDog API returned status {response.status}",
                            health_score=30
                        )
                        
        except asyncio.TimeoutError:
            self.results['scrapingdog'] = CredentialResult(
                name="ScrapingDog API",
                status=CredentialStatus.UNKNOWN,
                message="ScrapingDog API validation timeout - check network connection",
                health_score=0
            )
        except Exception as e:
            self.results['scrapingdog'] = CredentialResult(
                name="ScrapingDog API", 
                status=CredentialStatus.UNKNOWN,
                message=f"ScrapingDog validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_json2video_api(self):
        """Validate JSON2Video API key"""
        try:
            api_key = self.config.get('json2video_api_key', '')
            
            if not api_key or api_key == 'YOUR-KEY-HERE':
                self.results['json2video'] = CredentialResult(
                    name="JSON2Video API",
                    status=CredentialStatus.MISSING,
                    message="JSON2Video API key not configured", 
                    health_score=0
                )
                return
            
            # Test API call - get projects with explicit timeout
            headers = {'X-API-KEY': api_key}
            
            # Add explicit timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get('https://api.json2video.com/v2/projects', headers=headers) as response:
                    if response.status == 200:
                        # Get usage information
                        usage_info = await self._get_json2video_usage_info(session, headers)
                        
                        self.results['json2video'] = CredentialResult(
                            name="JSON2Video API",
                            status=CredentialStatus.VALID,
                            message="JSON2Video API key valid and active",
                            health_score=100,
                            usage_info=usage_info
                        )
                    elif response.status == 401:
                        self.results['json2video'] = CredentialResult(
                            name="JSON2Video API",
                            status=CredentialStatus.INVALID,
                            message="JSON2Video API key invalid or unauthorized",
                            health_score=0
                        )
                    else:
                        self.results['json2video'] = CredentialResult(
                            name="JSON2Video API",
                            status=CredentialStatus.UNKNOWN,
                            message=f"JSON2Video API returned status {response.status}",
                            health_score=30
                        )
                        
        except asyncio.TimeoutError:
            self.results['json2video'] = CredentialResult(
                name="JSON2Video API",
                status=CredentialStatus.UNKNOWN,
                message="JSON2Video API validation timeout - check network connection",
                health_score=0
            )
        except Exception as e:
            self.results['json2video'] = CredentialResult(
                name="JSON2Video API",
                status=CredentialStatus.UNKNOWN,
                message=f"JSON2Video validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_airtable_api(self):
        """Validate Airtable API key and base access"""
        try:
            api_key = self.config.get('airtable_api_key', '')
            base_id = self.config.get('airtable_base_id', '')
            table_name = self.config.get('airtable_table_name', '')
            
            if not api_key or api_key.startswith('patYOUR-KEY'):
                self.results['airtable'] = CredentialResult(
                    name="Airtable API",
                    status=CredentialStatus.MISSING,
                    message="Airtable API key not configured",
                    health_score=0
                )
                return
            
            if not base_id or not table_name:
                self.results['airtable'] = CredentialResult(
                    name="Airtable API",
                    status=CredentialStatus.MISSING,
                    message="Airtable base ID or table name not configured",
                    health_score=0
                )
                return
            
            # Test API call - get base schema with explicit timeout
            headers = {'Authorization': f'Bearer {api_key}'}
            url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
            
            # Add explicit timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        tables = data.get('tables', [])
                        table_names = [t.get('name') for t in tables]
                        
                        if table_name in table_names:
                            self.results['airtable'] = CredentialResult(
                                name="Airtable API",
                                status=CredentialStatus.VALID,
                                message=f"Airtable API valid. Table '{table_name}' found.",
                                health_score=100
                            )
                        else:
                            self.results['airtable'] = CredentialResult(
                                name="Airtable API",
                                status=CredentialStatus.INVALID,
                                message=f"Table '{table_name}' not found in base. Available: {table_names}",
                                health_score=50
                            )
                    elif response.status == 401:
                        self.results['airtable'] = CredentialResult(
                            name="Airtable API",
                            status=CredentialStatus.INVALID,
                            message="Airtable API key invalid or unauthorized",
                            health_score=0
                        )
                    elif response.status == 404:
                        self.results['airtable'] = CredentialResult(
                            name="Airtable API", 
                            status=CredentialStatus.INVALID,
                            message="Airtable base ID not found or no access",
                            health_score=0
                        )
                    else:
                        self.results['airtable'] = CredentialResult(
                            name="Airtable API",
                            status=CredentialStatus.UNKNOWN,
                            message=f"Airtable API returned status {response.status}",
                            health_score=30
                        )
                        
        except asyncio.TimeoutError:
            self.results['airtable'] = CredentialResult(
                name="Airtable API",
                status=CredentialStatus.UNKNOWN,
                message="Airtable API validation timeout - check network connection",
                health_score=0
            )
        except Exception as e:
            self.results['airtable'] = CredentialResult(
                name="Airtable API",
                status=CredentialStatus.UNKNOWN,
                message=f"Airtable validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_oauth_tokens(self):
        """Validate OAuth tokens (Google Drive, YouTube)"""
        self.logger.info("🔐 Validating OAuth Tokens...")
        
        # Google Drive Token
        await self._validate_google_drive_token()
        
        # YouTube Token
        await self._validate_youtube_token()
    
    async def _validate_google_drive_token(self):
        """Validate Google Drive OAuth token"""
        try:
            status = self.google_drive_manager.get_token_status()
            
            if not status['exists']:
                self.results['google_drive'] = CredentialResult(
                    name="Google Drive OAuth",
                    status=CredentialStatus.MISSING,
                    message="Google Drive token file not found",
                    health_score=0,
                    can_refresh=False
                )
                return
            
            if status['valid']:
                days_until_expiry = status.get('days_until_expiry', 0)
                self.results['google_drive'] = CredentialResult(
                    name="Google Drive OAuth",
                    status=CredentialStatus.VALID,
                    message=f"Google Drive token valid for {days_until_expiry} days",
                    expires_in_days=days_until_expiry,
                    health_score=100,
                    can_refresh=status['can_refresh']
                )
            elif status['needs_refresh'] and status['can_refresh']:
                # Try automatic refresh
                success, message = self.google_drive_manager.refresh_token()
                if success:
                    self.results['google_drive'] = CredentialResult(
                        name="Google Drive OAuth",
                        status=CredentialStatus.VALID,
                        message=f"Google Drive token refreshed: {message}",
                        health_score=90,
                        can_refresh=True
                    )
                else:
                    self.results['google_drive'] = CredentialResult(
                        name="Google Drive OAuth",
                        status=CredentialStatus.REFRESH_NEEDED,
                        message=f"Refresh failed: {message}",
                        health_score=20,
                        can_refresh=True
                    )
            elif status['expired']:
                self.results['google_drive'] = CredentialResult(
                    name="Google Drive OAuth",
                    status=CredentialStatus.EXPIRED,
                    message="Google Drive token expired and cannot be refreshed",
                    health_score=0,
                    can_refresh=status['can_refresh']
                )
            else:
                self.results['google_drive'] = CredentialResult(
                    name="Google Drive OAuth",
                    status=CredentialStatus.INVALID,
                    message="Google Drive token is invalid",
                    health_score=0,
                    can_refresh=status['can_refresh']
                )
                
        except Exception as e:
            self.results['google_drive'] = CredentialResult(
                name="Google Drive OAuth",
                status=CredentialStatus.UNKNOWN,
                message=f"Google Drive validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_youtube_token(self):
        """Validate YouTube OAuth token"""
        try:
            youtube_token_path = self.config.get('youtube_token', '/home/claude-workflow/config/youtube_token.json')
            youtube_creds_path = self.config.get('youtube_credentials', '/home/claude-workflow/config/youtube_credentials.json')
            
            if not os.path.exists(youtube_creds_path):
                self.results['youtube'] = CredentialResult(
                    name="YouTube OAuth",
                    status=CredentialStatus.MISSING,
                    message="YouTube credentials file not found",
                    health_score=0
                )
                return
            
            if not os.path.exists(youtube_token_path):
                self.results['youtube'] = CredentialResult(
                    name="YouTube OAuth",
                    status=CredentialStatus.MISSING,
                    message="YouTube token file not found - authorization needed",
                    health_score=0
                )
                return
            
            # Try to validate with YouTubeAuthManager
            try:
                auth_manager = YouTubeAuthManager(self.config)
                success = auth_manager.test_authentication()
                
                if success:
                    self.results['youtube'] = CredentialResult(
                        name="YouTube OAuth",
                        status=CredentialStatus.VALID,
                        message="YouTube token valid and authenticated",
                        health_score=100,
                        can_refresh=True
                    )
                else:
                    self.results['youtube'] = CredentialResult(
                        name="YouTube OAuth",
                        status=CredentialStatus.INVALID,
                        message="YouTube token authentication failed",
                        health_score=0,
                        can_refresh=True
                    )
                    
            except Exception as auth_error:
                self.results['youtube'] = CredentialResult(
                    name="YouTube OAuth",
                    status=CredentialStatus.UNKNOWN,
                    message=f"YouTube authentication test failed: {str(auth_error)}",
                    health_score=0
                )
                
        except Exception as e:
            self.results['youtube'] = CredentialResult(
                name="YouTube OAuth",
                status=CredentialStatus.UNKNOWN,
                message=f"YouTube validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_service_credentials(self):
        """Validate service credentials (WordPress, Instagram, Amazon)"""
        self.logger.info("🌐 Validating Service Credentials...")
        
        # WordPress credentials
        await self._validate_wordpress_credentials()
        
        # Instagram credentials
        await self._validate_instagram_credentials()
        
        # Amazon Associate ID
        await self._validate_amazon_credentials()
    
    async def _validate_wordpress_credentials(self):
        """Validate WordPress API credentials"""
        try:
            wp_url = self.config.get('wordpress_url', '')
            wp_user = self.config.get('wordpress_user', '')
            wp_password = self.config.get('wordpress_password', '')
            wp_enabled = self.config.get('wordpress_enabled', False)
            
            if not wp_enabled:
                self.results['wordpress'] = CredentialResult(
                    name="WordPress",
                    status=CredentialStatus.VALID,
                    message="WordPress publishing disabled - skipping validation",
                    health_score=100
                )
                return
            
            if not wp_url or not wp_user or not wp_password:
                self.results['wordpress'] = CredentialResult(
                    name="WordPress",
                    status=CredentialStatus.MISSING,
                    message="WordPress credentials incomplete",
                    health_score=0
                )
                return
            
            if wp_password == 'YOUR_APPLICATION_PASSWORD':
                self.results['wordpress'] = CredentialResult(
                    name="WordPress",
                    status=CredentialStatus.MISSING,
                    message="WordPress password not configured (still placeholder)",
                    health_score=0
                )
                return
            
            # Test WordPress REST API with explicit timeout
            auth = aiohttp.BasicAuth(wp_user, wp_password)
            test_url = f"{wp_url.rstrip('/')}/wp-json/wp/v2/users/me"
            
            # Add explicit timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, auth=auth) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        username = user_data.get('name', 'Unknown')
                        self.results['wordpress'] = CredentialResult(
                            name="WordPress",
                            status=CredentialStatus.VALID,
                            message=f"WordPress API valid. Connected as: {username}",
                            health_score=100
                        )
                    elif response.status == 401:
                        self.results['wordpress'] = CredentialResult(
                            name="WordPress",
                            status=CredentialStatus.INVALID,
                            message="WordPress credentials invalid or unauthorized",
                            health_score=0
                        )
                    else:
                        self.results['wordpress'] = CredentialResult(
                            name="WordPress", 
                            status=CredentialStatus.UNKNOWN,
                            message=f"WordPress API returned status {response.status}",
                            health_score=30
                        )
                        
        except asyncio.TimeoutError:
            self.results['wordpress'] = CredentialResult(
                name="WordPress",
                status=CredentialStatus.UNKNOWN,
                message="WordPress API validation timeout - check network connection",
                health_score=0
            )
        except Exception as e:
            self.results['wordpress'] = CredentialResult(
                name="WordPress",
                status=CredentialStatus.UNKNOWN,
                message=f"WordPress validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_instagram_credentials(self):
        """Validate Instagram Graph API token"""
        try:
            access_token = self.config.get('instagram_access_token', '')
            
            if not access_token or access_token == 'IGAAYQQB3AYg1BZAE1NX2xwME95R1ZA1V0lBaXBXQ044Y3RmMTd1RnRsclpnMU5rYXBnSGdiLTN3WjVLcGE3cXhQdkhoazNWZAm5kRnZAHOW9YclprLS1RZAEVSM1VGbDZAMUmpTWlRUY0pZAVldQcERQZAXN0Vlhn':
                self.results['instagram'] = CredentialResult(
                    name="Instagram",
                    status=CredentialStatus.MISSING,
                    message="Instagram access token not configured or placeholder",
                    health_score=0
                )
                return
            
            # Test Instagram Graph API with explicit timeout
            test_url = f'https://graph.instagram.com/me?fields=id,username&access_token={access_token}'
            
            # Add explicit timeout to prevent hanging
            timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        username = data.get('username', 'Unknown')
                        self.results['instagram'] = CredentialResult(
                            name="Instagram",
                            status=CredentialStatus.VALID,
                            message=f"Instagram API valid. Connected as: @{username}",
                            health_score=100
                        )
                    elif response.status == 401:
                        self.results['instagram'] = CredentialResult(
                            name="Instagram",
                            status=CredentialStatus.INVALID,
                            message="Instagram access token invalid or expired",
                            health_score=0
                        )
                    else:
                        error_data = await response.json() if response.content else {}
                        error_msg = error_data.get('error', {}).get('message', f'Status {response.status}')
                        self.results['instagram'] = CredentialResult(
                            name="Instagram",
                            status=CredentialStatus.UNKNOWN,
                            message=f"Instagram API error: {error_msg}",
                            health_score=30
                        )
                        
        except asyncio.TimeoutError:
            self.results['instagram'] = CredentialResult(
                name="Instagram",
                status=CredentialStatus.UNKNOWN,
                message="Instagram API validation timeout - check network connection",
                health_score=0
            )
        except Exception as e:
            self.results['instagram'] = CredentialResult(
                name="Instagram",
                status=CredentialStatus.UNKNOWN,
                message=f"Instagram validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_amazon_credentials(self):
        """Validate Amazon Associate credentials"""
        try:
            associate_id = self.config.get('amazon_associate_id', '')
            
            if not associate_id or associate_id == 'your-associate-id-20':
                self.results['amazon'] = CredentialResult(
                    name="Amazon Associate",
                    status=CredentialStatus.MISSING,
                    message="Amazon Associate ID not configured",
                    health_score=0
                )
                return
            
            # Basic validation - check format
            if associate_id.endswith('-20') and len(associate_id) > 5:
                self.results['amazon'] = CredentialResult(
                    name="Amazon Associate",
                    status=CredentialStatus.VALID,
                    message=f"Amazon Associate ID configured: {associate_id}",
                    health_score=80  # Can't fully validate without actual API call
                )
            else:
                self.results['amazon'] = CredentialResult(
                    name="Amazon Associate",
                    status=CredentialStatus.INVALID,
                    message="Amazon Associate ID format appears invalid",
                    health_score=20
                )
                
        except Exception as e:
            self.results['amazon'] = CredentialResult(
                name="Amazon Associate",
                status=CredentialStatus.UNKNOWN,
                message=f"Amazon validation error: {str(e)}",
                health_score=0
            )
    
    async def _validate_file_credentials(self):
        """Validate file-based credentials"""
        self.logger.info("📁 Validating File Credentials...")
        
        # Google Drive credentials file
        self._validate_google_drive_credentials_file()
        
        # YouTube credentials file  
        self._validate_youtube_credentials_file()
    
    def _validate_google_drive_credentials_file(self):
        """Validate Google Drive credentials JSON file"""
        try:
            creds_path = self.config.get('google_drive_oauth_credentials', '')
            
            if not creds_path:
                self.results['google_drive_file'] = CredentialResult(
                    name="Google Drive Credentials File",
                    status=CredentialStatus.MISSING,
                    message="Google Drive credentials path not configured",
                    health_score=0
                )
                return
            
            if not os.path.exists(creds_path):
                self.results['google_drive_file'] = CredentialResult(
                    name="Google Drive Credentials File",
                    status=CredentialStatus.MISSING,
                    message=f"Google Drive credentials file not found: {creds_path}",
                    health_score=0
                )
                return
            
            # Try to load and validate JSON structure
            try:
                with open(creds_path, 'r') as f:
                    creds_data = json.load(f)
                
                # Check for required OAuth fields
                if 'web' in creds_data or 'installed' in creds_data:
                    client_info = creds_data.get('web') or creds_data.get('installed')
                    if client_info and 'client_id' in client_info and 'client_secret' in client_info:
                        self.results['google_drive_file'] = CredentialResult(
                            name="Google Drive Credentials File",
                            status=CredentialStatus.VALID,
                            message="Google Drive credentials file valid",
                            health_score=100
                        )
                    else:
                        self.results['google_drive_file'] = CredentialResult(
                            name="Google Drive Credentials File",
                            status=CredentialStatus.INVALID,
                            message="Google Drive credentials file missing required fields",
                            health_score=20
                        )
                else:
                    self.results['google_drive_file'] = CredentialResult(
                        name="Google Drive Credentials File",
                        status=CredentialStatus.INVALID,
                        message="Google Drive credentials file invalid structure",
                        health_score=20
                    )
                    
            except json.JSONDecodeError:
                self.results['google_drive_file'] = CredentialResult(
                    name="Google Drive Credentials File",
                    status=CredentialStatus.INVALID,
                    message="Google Drive credentials file invalid JSON",
                    health_score=0
                )
                
        except Exception as e:
            self.results['google_drive_file'] = CredentialResult(
                name="Google Drive Credentials File",
                status=CredentialStatus.UNKNOWN,
                message=f"Google Drive credentials validation error: {str(e)}",
                health_score=0
            )
    
    def _validate_youtube_credentials_file(self):
        """Validate YouTube credentials JSON file"""
        try:
            creds_path = self.config.get('youtube_credentials', '')
            
            if not creds_path:
                self.results['youtube_file'] = CredentialResult(
                    name="YouTube Credentials File",
                    status=CredentialStatus.MISSING,
                    message="YouTube credentials path not configured",
                    health_score=0
                )
                return
            
            if not os.path.exists(creds_path):
                self.results['youtube_file'] = CredentialResult(
                    name="YouTube Credentials File", 
                    status=CredentialStatus.MISSING,
                    message=f"YouTube credentials file not found: {creds_path}",
                    health_score=0
                )
                return
            
            # Try to load and validate JSON structure
            try:
                with open(creds_path, 'r') as f:
                    creds_data = json.load(f)
                
                # Check for required OAuth fields
                if 'web' in creds_data or 'installed' in creds_data:
                    client_info = creds_data.get('web') or creds_data.get('installed')
                    if client_info and 'client_id' in client_info and 'client_secret' in client_info:
                        self.results['youtube_file'] = CredentialResult(
                            name="YouTube Credentials File",
                            status=CredentialStatus.VALID,
                            message="YouTube credentials file valid",
                            health_score=100
                        )
                    else:
                        self.results['youtube_file'] = CredentialResult(
                            name="YouTube Credentials File",
                            status=CredentialStatus.INVALID,
                            message="YouTube credentials file missing required fields",
                            health_score=20
                        )
                else:
                    self.results['youtube_file'] = CredentialResult(
                        name="YouTube Credentials File",
                        status=CredentialStatus.INVALID,
                        message="YouTube credentials file invalid structure",
                        health_score=20
                    )
                    
            except json.JSONDecodeError:
                self.results['youtube_file'] = CredentialResult(
                    name="YouTube Credentials File",
                    status=CredentialStatus.INVALID,
                    message="YouTube credentials file invalid JSON",
                    health_score=0
                )
                
        except Exception as e:
            self.results['youtube_file'] = CredentialResult(
                name="YouTube Credentials File",
                status=CredentialStatus.UNKNOWN,
                message=f"YouTube credentials validation error: {str(e)}",
                health_score=0
            )
    
    def _calculate_health_scores(self):
        """Calculate overall health scores and identify critical issues"""
        if not self.results:
            self.overall_health_score = 0
            return
        
        # Calculate weighted average health score
        total_score = sum(result.health_score for result in self.results.values())
        self.overall_health_score = int(total_score / len(self.results))
        
        # Identify critical failures and warnings
        for name, result in self.results.items():
            if result.health_score == 0:
                self.critical_failures.append(f"{result.name}: {result.message}")
            elif result.health_score < 50:
                self.warnings.append(f"{result.name}: {result.message}")
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        # Determine overall status
        if self.overall_health_score >= 90:
            overall_status = "ready"
            can_proceed = True
        elif self.overall_health_score >= 70:
            overall_status = "warning" 
            can_proceed = True
        else:
            overall_status = "failed"
            can_proceed = False
        
        # Format results for report
        formatted_results = {}
        for name, result in self.results.items():
            formatted_results[name] = {
                'name': result.name,
                'status': result.status.value,
                'message': result.message,
                'health_score': result.health_score,
                'expires_in_days': result.expires_in_days,
                'can_refresh': result.can_refresh,
                'usage_info': result.usage_info
            }
        
        return {
            'overall_status': overall_status,
            'health_score': self.overall_health_score,
            'results': formatted_results,
            'critical_failures': self.critical_failures,
            'warnings': self.warnings,
            'can_proceed': can_proceed,
            'validation_timestamp': datetime.utcnow().isoformat()
        }
    
    def print_validation_report(self, report: Dict[str, Any]):
        """Print a formatted validation report to console"""
        
        print("\n" + "="*80)
        print("🔍 CREDENTIAL VALIDATION REPORT")
        print("="*80)
        
        # Overall status
        status_emoji = {
            'ready': '✅',
            'warning': '⚠️', 
            'failed': '❌'
        }
        
        print(f"\n📊 OVERALL STATUS: {status_emoji.get(report['overall_status'], '❓')} {report['overall_status'].upper()}")
        print(f"🏥 HEALTH SCORE: {report['health_score']}/100")
        print(f"🚀 CAN PROCEED: {'YES' if report['can_proceed'] else 'NO'}")
        
        # Individual results
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 80)
        
        for name, result in report['results'].items():
            status_icon = {
                'valid': '✅',
                'expired': '⏰',
                'invalid': '❌', 
                'missing': '❓',
                'refresh_needed': '🔄',
                'unknown': '⚡'
            }
            
            icon = status_icon.get(result['status'], '❓')
            score = result['health_score']
            
            print(f"{icon} {result['name']:<25} [{score:3d}/100] - {result['message']}")
            
            # Show expiry information
            if result.get('expires_in_days') is not None:
                days = result['expires_in_days']
                if days > 0:
                    print(f"   └── Expires in {days} days")
                else:
                    print(f"   └── Expired {abs(days)} days ago")
            
            # Show usage information
            usage = result.get('usage_info')
            if usage:
                if usage.get('type') == 'character_usage':
                    used = usage.get('used', 0)
                    limit = usage.get('limit', 0)
                    remaining = usage.get('remaining', 0)
                    tier = usage.get('tier', 'Unknown')
                    percent = usage.get('usage_percent', 0)
                    
                    status_color = '🟢' if percent < 50 else '🟡' if percent < 80 else '🔴'
                    print(f"   └── {status_color} Usage: {used:,}/{limit:,} chars ({percent}%) | {remaining:,} remaining | {tier} tier")
                    
                elif usage.get('type') == 'credit_usage':
                    used = usage.get('used', 0)
                    remaining = usage.get('remaining', 0)
                    limit = usage.get('limit', 0)
                    percent = usage.get('usage_percent', 0)
                    plan = usage.get('plan', '')
                    validity = usage.get('validity_days', 0)
                    
                    status_color = '🟢' if percent < 50 else '🟡' if percent < 80 else '🔴'
                    
                    if plan and validity:
                        print(f"   └── {status_color} Usage: {used:,}/{limit:,} credits ({percent}%) | {remaining:,} remaining")
                        print(f"   └── 📦 Plan: {plan} | ⏰ {validity} days remaining")
                    else:
                        print(f"   └── {status_color} Usage: {used:,}/{limit:,} credits ({percent}%) | {remaining:,} remaining")
                    
                elif usage.get('type') == 'video_credits':
                    plan = usage.get('plan', 'Unknown')
                    videos = usage.get('videos_rendered', 0)
                    credits_used = usage.get('credits_used', 0)
                    credits_limit = usage.get('credits_limit', 0)
                    
                    print(f"   └── 🎬 Plan: {plan} | Videos: {videos} | Credits: {credits_used}/{credits_limit}")
                    
                elif usage.get('type') == 'token_usage':
                    total_requests = usage.get('total_requests', 0)
                    total_tokens = usage.get('total_tokens', 0)
                    dalle_requests = usage.get('dalle_requests', 0)
                    tts_requests = usage.get('tts_requests', 0)
                    models = usage.get('models_used', [])
                    time_period = usage.get('time_period', '48h')
                    
                    print(f"   └── 📊 Usage ({time_period}): {total_requests} requests | {total_tokens:,} tokens")
                    if dalle_requests > 0 or tts_requests > 0 or len(models) > 0:
                        details = []
                        if dalle_requests > 0:
                            details.append(f"DALL-E: {dalle_requests}")
                        if tts_requests > 0:
                            details.append(f"TTS: {tts_requests}")
                        if models:
                            details.append(f"Models: {', '.join(models[:2])}")
                        print(f"   └── 🎨 {' | '.join(details)}")
                
                elif usage.get('type') == 'usage_info':
                    org = usage.get('organization', 'Personal')
                    print(f"   └── 📊 Organization: {org} | Check usage at platform.openai.com")
                    
                elif usage.get('type') == 'basic':
                    note = usage.get('note', '')
                    if note:
                        print(f"   └── ℹ️  {note}")
        
        # Critical failures
        if report['critical_failures']:
            print(f"\n🚨 CRITICAL FAILURES:")
            print("-" * 80)
            for failure in report['critical_failures']:
                print(f"❌ {failure}")
        
        # Warnings
        if report['warnings']:
            print(f"\n⚠️  WARNINGS:")
            print("-" * 80)
            for warning in report['warnings']:
                print(f"⚠️  {warning}")
        
        # Usage Warnings
        usage_warnings = self._get_usage_warnings(report)
        if usage_warnings:
            print(f"\n💰 USAGE WARNINGS:")
            print("-" * 80)
            for warning in usage_warnings:
                print(f"💰 {warning}")
        
        # Recommendations
        print(f"\n📝 RECOMMENDATIONS:")
        print("-" * 80)
        
        if report['overall_status'] == 'ready':
            print("✅ All credentials validated. Workflow can proceed safely.")
        elif report['overall_status'] == 'warning':
            print("⚠️  Some credentials have issues but workflow can proceed.")
            print("   Consider fixing warnings to improve reliability.")
        else:
            print("❌ Critical credential failures detected. Fix before proceeding:")
            for failure in report['critical_failures'][:3]:  # Show top 3
                print(f"   • {failure}")
        
        if usage_warnings:
            print("\n💡 COST OPTIMIZATION:")
            for warning in usage_warnings:
                if 'ElevenLabs' in warning:
                    print("   • Consider upgrading ElevenLabs plan or monitoring character usage")
                elif 'ScrapingDog' in warning:
                    print("   • Consider purchasing more ScrapingDog credits")
                elif 'JSON2Video' in warning:
                    print("   • Check JSON2Video account and plan limits")
        
        print("\n" + "="*80)


# Convenience functions for direct usage
async def validate_all_production_credentials() -> Dict[str, Any]:
    """Validate all production credentials and return report"""
    validator = ProductionCredentialValidationServer()
    return await validator.validate_all_credentials()

async def validate_and_print_report():
    """Validate credentials and print formatted report"""
    validator = ProductionCredentialValidationServer()
    report = await validator.validate_all_credentials()
    validator.print_validation_report(report)
    return report

def main():
    """Main function for standalone execution"""
    print("🔍 Production Credential Validation Starting...")
    report = asyncio.run(validate_and_print_report())
    
    if not report['can_proceed']:
        print(f"\n❌ VALIDATION FAILED - Cannot proceed with workflow")
        exit(1)
    elif report['warnings']:
        print(f"\n⚠️  VALIDATION COMPLETED WITH WARNINGS")
        exit(0)  
    else:
        print(f"\n✅ VALIDATION SUCCESSFUL - Ready to proceed")
        exit(0)

if __name__ == "__main__":
    main()