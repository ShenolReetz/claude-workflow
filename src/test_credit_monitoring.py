#!/usr/bin/env python3
"""Test API credit monitoring system"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.credit_monitor_server import CreditMonitorMCPServer, monitor_api_credits

async def test_credit_monitoring():
    """Test the credit monitoring system"""
    
    print("💰 Testing API Credit Monitoring System")
    print("=" * 60)
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    print(f"📋 Monitoring Configuration:")
    print(f"   Enabled: {config.get('credit_monitoring_enabled', True)}")
    print(f"   Threshold: €{config.get('credit_threshold_eur', 10.0)}")
    print(f"   Email Configured: {bool(config.get('email_sender'))}")
    print(f"   Services to Monitor: 6 APIs")
    
    # Initialize monitor
    monitor = CreditMonitorMCPServer(config)
    
    try:
        print(f"\n🔍 Checking credits for all services...")
        
        # Check each service individually first
        services = [
            ('OpenAI', monitor._check_openai_credits),
            ('Anthropic', monitor._check_anthropic_credits),
            ('ElevenLabs', monitor._check_elevenlabs_credits),
            ('JSON2Video', monitor._check_json2video_credits),
            ('ScrapingDog', monitor._check_scrapingdog_credits),
            ('Airtable', monitor._check_airtable_usage)
        ]
        
        individual_results = {}
        for service_name, check_func in services:
            print(f"\n🔍 Checking {service_name}...")
            try:
                result = await check_func()
                individual_results[service_name.lower()] = result
                
                status = result.get('status', 'unknown')
                value_eur = result.get('value_eur', 0)
                details = result.get('details', '')
                
                if status == 'success':
                    if value_eur <= 10.0:
                        print(f"   🚨 LOW: €{value_eur:.2f} - {details}")
                    else:
                        print(f"   ✅ OK: €{value_eur:.2f} - {details}")
                elif status == 'not_available':
                    print(f"   ⚠️ API not available: {result.get('message', '')}")
                elif status == 'free_tier':
                    print(f"   💚 Free tier: {result.get('message', '')}")
                elif status == 'no_key':
                    print(f"   🔑 No API key configured")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                individual_results[service_name.lower()] = {'status': 'error', 'error': str(e)}
        
        print(f"\n📊 Running complete monitoring check...")
        
        # Run complete monitoring
        complete_result = await monitor.check_all_credits()
        
        print(f"\n📈 Complete Results:")
        print(f"   Total Services: {len(complete_result['services'])}")
        print(f"   Services Below Threshold: {len(complete_result['services_below_threshold'])}")
        print(f"   Total Estimated Value: €{complete_result['total_value_eur']:.2f}")
        print(f"   Alerts Generated: {len(complete_result['alerts'])}")
        
        # Show detailed results
        print(f"\n📋 Service Details:")
        for service_name, service_data in complete_result['services'].items():
            status = service_data.get('status', 'unknown')
            value_eur = service_data.get('value_eur', 0)
            details = service_data.get('details', '')
            
            status_emoji = {
                'success': '✅' if value_eur > 10 else '🚨',
                'error': '❌',
                'no_key': '🔑',
                'not_available': '⚠️',
                'free_tier': '💚'
            }.get(status, '❓')
            
            print(f"   {service_name.title()}: {status_emoji} {status}")
            if value_eur != float('inf'):
                print(f"      Value: €{value_eur:.2f}")
            if details:
                print(f"      Details: {details}")
            if service_data.get('top_up_url'):
                print(f"      Top-up: {service_data['top_up_url']}")
        
        # Show alerts
        if complete_result['alerts']:
            print(f"\n🚨 ALERTS ({len(complete_result['alerts'])}):")
            for i, alert in enumerate(complete_result['alerts'], 1):
                print(f"   {i}. {alert['message']}")
                print(f"      Service: {alert['service']}")
                print(f"      Remaining: €{alert['value_eur']:.2f}")
        else:
            print(f"\n✅ No alerts - all services have sufficient credits")
        
        # Test email functionality (without actually sending)
        print(f"\n📧 Email Configuration Test:")
        email_config = monitor.email_config
        if email_config.get('sender_email') and email_config['sender_email'] != 'your-email@gmail.com':
            print(f"   Sender: {email_config['sender_email']}")
            print(f"   Recipient: {email_config['recipient_email']}")
            print(f"   SMTP Server: {email_config['smtp_server']}:{email_config['smtp_port']}")
            
            if complete_result['alerts']:
                print(f"   📧 Email would be sent with {len(complete_result['alerts'])} alert(s)")
            else:
                print(f"   📧 No email needed - no alerts")
        else:
            print(f"   ⚠️ Email not configured - update config with real email credentials")
        
        # Show top-up URLs
        print(f"\n🔗 Quick Top-up Links:")
        top_up_urls = {
            'OpenAI': 'https://platform.openai.com/account/billing',
            'ElevenLabs': 'https://elevenlabs.io/subscription',
            'JSON2Video': 'https://json2video.com/pricing',
            'ScrapingDog': 'https://scrapingdog.com/pricing',
            'Anthropic': 'https://console.anthropic.com/settings/billing'
        }
        
        for service, url in top_up_urls.items():
            print(f"   {service}: {url}")
        
        # Test workflow integration
        print(f"\n🔄 Testing Workflow Integration:")
        try:
            workflow_result = await monitor_api_credits(config)
            print(f"   ✅ Workflow integration successful")
            print(f"   Total Value: €{workflow_result['total_value_eur']:.2f}")
            print(f"   Alerts: {len(workflow_result['alerts'])}")
        except Exception as e:
            print(f"   ❌ Workflow integration error: {e}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await monitor.close()
        print(f"\n✅ Credit monitoring test completed")

if __name__ == "__main__":
    asyncio.run(test_credit_monitoring())