#!/usr/bin/env python3
"""
Credit Monitor MCP Server - Monitors API credits/tokens and sends email alerts
"""

import asyncio
import httpx
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import calendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditMonitorMCPServer:
    """Monitor API credits and send email alerts when low"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
        self.low_credit_threshold_eur = 10.0  # Alert when ≤ 10 EUR remaining
        
        # API pricing (approximate EUR per unit)
        self.pricing = {
            'openai': {
                'gpt4_input': 0.000025,      # EUR per token
                'gpt4_output': 0.000075,     # EUR per token  
                'dalle3_hd': 0.07,           # EUR per image
                'dalle2': 0.018,             # EUR per image
            },
            'anthropic': {
                'claude_input': 0.000008,    # EUR per token
                'claude_output': 0.000024,   # EUR per token
            },
            'elevenlabs': {
                'character': 0.00018,        # EUR per character
            },
            'json2video': {
                'credit': 0.20,              # EUR per credit
            },
            'scrapingdog': {
                'request': 0.001,            # EUR per API call
            }
        }
        
        # Email configuration
        self.email_config = {
            'smtp_server': config.get('email_smtp_server', 'smtp.gmail.com'),
            'smtp_port': config.get('email_smtp_port', 587),
            'sender_email': config.get('email_sender', ''),
            'sender_password': config.get('email_password', ''),
            'recipient_email': config.get('email_recipient', config.get('email_sender', ''))
        }
    
    async def check_all_credits(self) -> Dict[str, Any]:
        """Check credits for all paid APIs"""
        
        logger.info("🔍 Checking credits for all paid APIs...")
        
        results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'services': {},
            'alerts': [],
            'total_value_eur': 0.0,
            'services_below_threshold': []
        }
        
        # Check each service
        services_to_check = [
            ('openai', self._check_openai_credits),
            ('anthropic', self._check_anthropic_credits),
            ('elevenlabs', self._check_elevenlabs_credits),
            ('json2video', self._check_json2video_credits),
            ('scrapingdog', self._check_scrapingdog_credits),
            ('airtable', self._check_airtable_usage)
        ]
        
        for service_name, check_function in services_to_check:
            try:
                service_result = await check_function()
                results['services'][service_name] = service_result
                
                if service_result.get('value_eur', 0) > 0:
                    results['total_value_eur'] += service_result['value_eur']
                
                # Check if below threshold
                if service_result.get('value_eur', float('inf')) <= self.low_credit_threshold_eur:
                    if service_result.get('status') == 'success':
                        results['services_below_threshold'].append(service_name)
                        results['alerts'].append({
                            'service': service_name,
                            'value_eur': service_result.get('value_eur', 0),
                            'message': f"⚠️ {service_name.title()} credits low: €{service_result.get('value_eur', 0):.2f} remaining"
                        })
                        
            except Exception as e:
                logger.error(f"❌ Error checking {service_name}: {e}")
                results['services'][service_name] = {
                    'status': 'error',
                    'error': str(e),
                    'value_eur': 0
                }
        
        # Send email if there are alerts
        if results['alerts']:
            await self._send_email_alert(results)
        
        return results
    
    async def _check_openai_credits(self) -> Dict[str, Any]:
        """Check OpenAI API credits and usage"""
        
        api_key = self.config.get('openai_api_key')
        if not api_key:
            return {'status': 'no_key', 'value_eur': 0}
        
        try:
            # Get current usage for this month
            now = datetime.now()
            start_date = f"{now.year}-{now.month:02d}-01"
            end_date = f"{now.year}-{now.month:02d}-{calendar.monthrange(now.year, now.month)[1]}"
            
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            
            # Check usage
            usage_response = await self.client.get(
                f"https://api.openai.com/v1/usage?start_date={start_date}&end_date={end_date}",
                headers=headers
            )
            
            if usage_response.status_code == 200:
                usage_data = usage_response.json()
                total_usage_cents = usage_data.get('total_usage', 0) / 100  # Convert from cents
                total_usage_eur = total_usage_cents * 0.85  # Approximate USD to EUR
                
                # Estimate remaining credits (assuming $100 monthly limit as example)
                estimated_limit_eur = 85.0  # ~$100 in EUR
                remaining_eur = max(0, estimated_limit_eur - total_usage_eur)
                
                return {
                    'status': 'success',
                    'usage_eur': total_usage_eur,
                    'estimated_remaining_eur': remaining_eur,
                    'value_eur': remaining_eur,
                    'top_up_url': 'https://platform.openai.com/account/billing',
                    'details': f"Used: €{total_usage_eur:.2f} this month"
                }
            else:
                return {
                    'status': 'error',
                    'error': f"API error: {usage_response.status_code}",
                    'value_eur': 0
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'value_eur': 0
            }
    
    async def _check_anthropic_credits(self) -> Dict[str, Any]:
        """Check Anthropic API credits"""
        
        api_key = self.config.get('anthropic_api_key')
        if not api_key:
            return {'status': 'no_key', 'value_eur': 0}
        
        try:
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            }
            
            # Note: Anthropic doesn't have a public usage API yet
            # This is a placeholder for when they add it
            return {
                'status': 'not_available',
                'message': 'Anthropic usage API not yet available',
                'value_eur': float('inf'),  # Don't trigger alerts
                'top_up_url': 'https://console.anthropic.com/settings/billing'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'value_eur': 0
            }
    
    async def _check_elevenlabs_credits(self) -> Dict[str, Any]:
        """Check ElevenLabs API credits"""
        
        api_key = self.config.get('elevenlabs_api_key')
        if not api_key:
            return {'status': 'no_key', 'value_eur': 0}
        
        try:
            headers = {
                'xi-api-key': api_key
            }
            
            # Get subscription info
            response = await self.client.get(
                "https://api.elevenlabs.io/v1/user/subscription",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                character_count = data.get('character_count', 0)
                character_limit = data.get('character_limit', 10000)
                
                remaining_characters = character_limit - character_count
                remaining_eur = remaining_characters * self.pricing['elevenlabs']['character']
                
                return {
                    'status': 'success',
                    'characters_used': character_count,
                    'characters_remaining': remaining_characters,
                    'value_eur': remaining_eur,
                    'top_up_url': 'https://elevenlabs.io/subscription',
                    'details': f"Characters: {remaining_characters:,} remaining"
                }
            else:
                return {
                    'status': 'error',
                    'error': f"API error: {response.status_code}",
                    'value_eur': 0
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'value_eur': 0
            }
    
    async def _check_json2video_credits(self) -> Dict[str, Any]:
        """Check JSON2Video API credits"""
        
        api_key = self.config.get('json2video_api_key')
        if not api_key:
            return {'status': 'no_key', 'value_eur': 0}
        
        try:
            headers = {
                'x-api-key': api_key
            }
            
            # Check account credits
            response = await self.client.get(
                "https://api.json2video.com/v2/account",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # JSON2Video uses "remaining_quota" with "time" in seconds
                remaining_quota = data.get('remaining_quota', {})
                time_seconds = remaining_quota.get('time', 0)
                
                # Convert seconds to videos (assuming 60 seconds per video)
                video_count = time_seconds // 60
                credits_eur = video_count * self.pricing['json2video']['credit']
                
                return {
                    'status': 'success',
                    'time_seconds': time_seconds,
                    'estimated_videos': video_count,
                    'value_eur': credits_eur,
                    'top_up_url': 'https://json2video.com/pricing',
                    'details': f"Time: {time_seconds:,}s (~{video_count} videos)"
                }
            else:
                return {
                    'status': 'error',
                    'error': f"API error: {response.status_code}",
                    'value_eur': 0
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'value_eur': 0
            }
    
    async def _check_scrapingdog_credits(self) -> Dict[str, Any]:
        """Check ScrapingDog API credits"""
        
        api_key = self.config.get('scrapingdog_api_key')
        if not api_key:
            return {'status': 'no_key', 'value_eur': 0}
        
        try:
            # Check account usage
            response = await self.client.get(
                f"https://api.scrapingdog.com/account?api_key={api_key}"
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # ScrapingDog response format: requestLimit, requestUsed
                request_limit = data.get('requestLimit', 0)
                request_used = data.get('requestUsed', 0)
                requests_remaining = request_limit - request_used
                
                requests_eur = requests_remaining * self.pricing['scrapingdog']['request']
                
                return {
                    'status': 'success',
                    'request_limit': request_limit,
                    'request_used': request_used,
                    'requests_remaining': requests_remaining,
                    'value_eur': requests_eur,
                    'top_up_url': 'https://scrapingdog.com/pricing',
                    'details': f"Requests: {requests_remaining:,} remaining ({request_used:,}/{request_limit:,} used)"
                }
            else:
                return {
                    'status': 'error',
                    'error': f"API error: {response.status_code}",
                    'value_eur': 0
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'value_eur': 0
            }
    
    async def _check_airtable_usage(self) -> Dict[str, Any]:
        """Check Airtable API usage (usually free but has limits)"""
        
        api_key = self.config.get('airtable_api_key')
        if not api_key:
            return {'status': 'no_key', 'value_eur': float('inf')}
        
        # Airtable doesn't have a usage API, but has generous free limits
        return {
            'status': 'free_tier',
            'message': 'Airtable usage within free limits',
            'value_eur': float('inf'),  # Don't trigger alerts for free tier
            'top_up_url': 'https://airtable.com/pricing'
        }
    
    async def _send_email_alert(self, results: Dict[str, Any]) -> bool:
        """Send email alert for low credits"""
        
        if not self.email_config.get('sender_email') or not self.email_config.get('sender_password'):
            logger.warning("⚠️ Email credentials not configured - cannot send alert")
            return False
        
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"🚨 API Credits Low Alert - {len(results['alerts'])} Service(s)"
            
            # Create HTML email body
            html_body = self._create_email_html(results)
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Email alert sent to {self.email_config['recipient_email']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")
            return False
    
    def _create_email_html(self, results: Dict[str, Any]) -> str:
        """Create HTML email body for credit alerts"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .alert {{ background: #ff4444; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .service {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .low-credit {{ background: #ffeeee; border-left: 5px solid #ff4444; }}
                .ok-credit {{ background: #eeffee; border-left: 5px solid #44ff44; }}
                .button {{ background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>🚨 API Credits Alert</h1>
            
            <div class="alert">
                <strong>{len(results['alerts'])} service(s) have low credits (≤ €10 remaining)</strong>
            </div>
            
            <h2>📊 Credit Status Summary</h2>
            <table>
                <tr>
                    <th>Service</th>
                    <th>Status</th>
                    <th>Remaining Value</th>
                    <th>Details</th>
                    <th>Action</th>
                </tr>
        """
        
        for service_name, service_data in results['services'].items():
            status = service_data.get('status', 'unknown')
            value_eur = service_data.get('value_eur', 0)
            details = service_data.get('details', '')
            top_up_url = service_data.get('top_up_url', '#')
            
            # Determine row class and status display
            if status == 'success':
                if value_eur <= self.low_credit_threshold_eur:
                    row_class = 'low-credit'
                    status_display = f"🚨 LOW (€{value_eur:.2f})"
                else:
                    row_class = 'ok-credit'
                    status_display = f"✅ OK (€{value_eur:.2f})"
            else:
                row_class = ''
                status_display = f"⚠️ {status.replace('_', ' ').title()}"
            
            html += f"""
                <tr class="{row_class}">
                    <td><strong>{service_name.title()}</strong></td>
                    <td>{status_display}</td>
                    <td>{"€{:.2f}".format(value_eur) if value_eur != float('inf') else 'Unlimited'}</td>
                    <td>{details}</td>
                    <td><a href="{top_up_url}" class="button">Top Up</a></td>
                </tr>
            """
        
        html += f"""
            </table>
            
            <h2>💰 Total Remaining Value</h2>
            <p><strong>€{results['total_value_eur']:.2f}</strong> across all services</p>
            
            <h2>🔧 Recommended Actions</h2>
            <ul>
        """
        
        for alert in results['alerts']:
            service = alert['service']
            value = alert['value_eur']
            top_up_url = results['services'][service].get('top_up_url', '#')
            
            html += f"""
                <li>
                    <strong>{service.title()}</strong>: Only €{value:.2f} remaining
                    <br><a href="{top_up_url}" class="button">Add Credits</a>
                </li>
            """
        
        html += f"""
            </ul>
            
            <h2>📅 Report Details</h2>
            <p><strong>Generated:</strong> {results['timestamp']}</p>
            <p><strong>Workflow:</strong> Video Content Pipeline</p>
            <p><strong>Threshold:</strong> €{self.low_credit_threshold_eur} per service</p>
            
            <hr>
            <p><em>This alert was automatically generated by your Video Content Pipeline workflow.</em></p>
        </body>
        </html>
        """
        
        return html
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Integration function for workflow_runner.py
async def monitor_api_credits(config: Dict) -> Dict[str, Any]:
    """Monitor API credits - integration point for main workflow"""
    
    monitor = CreditMonitorMCPServer(config)
    
    try:
        result = await monitor.check_all_credits()
        
        # Log summary
        logger.info(f"💰 Credit monitoring complete:")
        logger.info(f"   Total value: €{result['total_value_eur']:.2f}")
        logger.info(f"   Services below threshold: {len(result['services_below_threshold'])}")
        
        if result['alerts']:
            logger.warning(f"⚠️ {len(result['alerts'])} service(s) have low credits!")
            for alert in result['alerts']:
                logger.warning(f"   {alert['message']}")
        
        return result
    finally:
        await monitor.close()


# Test function
if __name__ == "__main__":
    async def test_credit_monitor():
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
        
        # Add email config for testing (replace with your email)
        config['email_sender'] = 'your-email@gmail.com'
        config['email_password'] = 'your-app-password'
        config['email_recipient'] = 'your-email@gmail.com'
        
        result = await monitor_api_credits(config)
        print(json.dumps(result, indent=2))
    
    asyncio.run(test_credit_monitor())