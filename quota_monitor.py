#!/usr/bin/env python3
"""
API Quota Monitor - Check quota status before running workflows
"""

import asyncio
import json
import sys
from datetime import datetime
import openai
from openai import OpenAI

sys.path.append('/home/claude-workflow')

class QuotaMonitor:
    def __init__(self, config_path='/home/claude-workflow/config/api_keys.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.clients = {
            'openai': OpenAI(api_key=self.config['openai_api_key'])
        }

    async def check_openai_quota(self):
        """Check OpenAI quota and rate limits"""
        try:
            # Test with minimal request
            response = self.clients['openai'].chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=1
            )
            
            return {
                'status': 'available',
                'message': 'OpenAI API accessible',
                'timestamp': datetime.now().isoformat()
            }
            
        except openai.RateLimitError as e:
            if "insufficient_quota" in str(e):
                return {
                    'status': 'quota_exhausted',
                    'message': 'OpenAI quota exhausted - workflow will use fallbacks',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'rate_limited',
                    'message': 'OpenAI rate limited - retry later',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'OpenAI API error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }

    async def check_all_apis(self):
        """Check status of all critical APIs"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'apis': {}
        }
        
        # OpenAI
        results['apis']['openai'] = await self.check_openai_quota()
        
        # JSON2Video (simple connectivity check)
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {"x-api-key": self.config['json2video_api_key']}
                
                # Test endpoint (without creating video)
                async with session.get("https://api.json2video.com/v2/account", headers=headers) as resp:
                    if resp.status == 200:
                        results['apis']['json2video'] = {
                            'status': 'available',
                            'message': 'JSON2Video API accessible'
                        }
                    else:
                        results['apis']['json2video'] = {
                            'status': 'error',
                            'message': f'JSON2Video returned {resp.status}'
                        }
        except Exception as e:
            results['apis']['json2video'] = {
                'status': 'error',
                'message': f'JSON2Video connection failed: {str(e)}'
            }
        
        # Airtable
        try:
            import aiohttp
            headers = {"Authorization": f"Bearer {self.config['airtable_api_key']}"}
            base_id = self.config['airtable_base_id']
            
            async with aiohttp.ClientSession() as session:
                url = f"https://api.airtable.com/v0/{base_id}/Video%20Titles?maxRecords=1"
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        results['apis']['airtable'] = {
                            'status': 'available',
                            'message': 'Airtable API accessible'
                        }
                    else:
                        results['apis']['airtable'] = {
                            'status': 'error',
                            'message': f'Airtable returned {resp.status}'
                        }
        except Exception as e:
            results['apis']['airtable'] = {
                'status': 'error',
                'message': f'Airtable connection failed: {str(e)}'
            }
        
        return results

    def print_status_report(self, results):
        """Print formatted status report"""
        print("\n🔍 API QUOTA & STATUS REPORT")
        print("=" * 50)
        print(f"📅 Timestamp: {results['timestamp']}")
        print()
        
        for api_name, status in results['apis'].items():
            status_emoji = {
                'available': '✅',
                'quota_exhausted': '❌',
                'rate_limited': '⚠️',
                'error': '❌'
            }.get(status['status'], '❓')
            
            print(f"{status_emoji} {api_name.upper()}: {status['status']}")
            print(f"   📝 {status['message']}")
            if 'error' in status:
                print(f"   🚨 Error: {status['error'][:100]}...")
            print()
        
        # Overall recommendation
        critical_apis = ['openai', 'airtable']
        all_critical_ok = all(
            results['apis'].get(api, {}).get('status') in ['available', 'rate_limited'] 
            for api in critical_apis
        )
        
        if all_critical_ok:
            print("🚀 RECOMMENDATION: Workflow can run (may use fallbacks if needed)")
        else:
            print("⚠️ RECOMMENDATION: Fix critical API issues before running workflow")
            
        # Quota specifically
        openai_status = results['apis'].get('openai', {}).get('status')
        if openai_status == 'quota_exhausted':
            print("💡 TIP: Workflow will use content fallbacks due to OpenAI quota")
        
        print("=" * 50)

async def main():
    monitor = QuotaMonitor()
    results = await monitor.check_all_apis()
    monitor.print_status_report(results)
    
    # Save to file for other scripts to check
    with open('/home/claude-workflow/api_status.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())