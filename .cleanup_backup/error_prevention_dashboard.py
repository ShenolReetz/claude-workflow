#!/usr/bin/env python3
"""
Error Prevention Dashboard - Comprehensive monitoring and prevention
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import os

sys.path.append('/home/claude-workflow')

from quota_monitor import QuotaMonitor
from restart_workflow import WorkflowRecoveryManager

class ErrorPreventionDashboard:
    def __init__(self):
        self.quota_monitor = QuotaMonitor()
        self.recovery_manager = WorkflowRecoveryManager()
        self.error_log_path = '/home/claude-workflow/error_log.json'

    async def generate_comprehensive_report(self):
        """Generate comprehensive error analysis and recommendations"""
        
        print("🔍 COMPREHENSIVE ERROR ANALYSIS & PREVENTION REPORT")
        print("=" * 70)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # 1. API Health Status
        print("1️⃣ API HEALTH STATUS")
        print("-" * 30)
        api_status = await self.quota_monitor.check_all_apis()
        self._print_api_health(api_status)
        
        # 2. Recent Error Analysis
        print("\n2️⃣ RECENT ERROR PATTERNS")
        print("-" * 30)
        error_analysis = self._analyze_recent_errors()
        self._print_error_analysis(error_analysis)
        
        # 3. Workflow Recovery Opportunities
        print("\n3️⃣ RECOVERY OPPORTUNITIES")
        print("-" * 30)
        recoverable = await self.recovery_manager.find_recoverable_records()
        self._print_recovery_opportunities(recoverable)
        
        # 4. Prevention Recommendations
        print("\n4️⃣ PREVENTION RECOMMENDATIONS")
        print("-" * 30)
        recommendations = self._generate_recommendations(api_status, error_analysis, recoverable)
        self._print_recommendations(recommendations)
        
        # 5. Immediate Actions
        print("\n5️⃣ IMMEDIATE ACTIONS REQUIRED")
        print("-" * 30)
        actions = self._determine_immediate_actions(api_status, error_analysis, recoverable)
        self._print_immediate_actions(actions)
        
        print("\n" + "=" * 70)
        
        return {
            'api_status': api_status,
            'error_analysis': error_analysis,
            'recoverable': recoverable,
            'recommendations': recommendations,
            'immediate_actions': actions
        }

    def _print_api_health(self, api_status: Dict):
        """Print API health status"""
        for api_name, status in api_status['apis'].items():
            status_emoji = {
                'available': '✅',
                'quota_exhausted': '❌',
                'rate_limited': '⚠️',
                'error': '❌'
            }.get(status['status'], '❓')
            
            print(f"  {status_emoji} {api_name.upper()}: {status['status']}")
            if status['status'] != 'available':
                print(f"    📝 {status['message']}")

    def _analyze_recent_errors(self) -> Dict:
        """Analyze recent error patterns"""
        if not os.path.exists(self.error_log_path):
            return {'total_errors': 0, 'error_types': {}, 'patterns': []}
        
        errors = []
        try:
            with open(self.error_log_path, 'r') as f:
                for line in f:
                    try:
                        errors.append(json.loads(line.strip()))
                    except:
                        continue
        except:
            return {'total_errors': 0, 'error_types': {}, 'patterns': []}
        
        # Filter last 24 hours
        now = datetime.now()
        recent_errors = []
        for error in errors:
            try:
                error_time = datetime.fromisoformat(error['timestamp'])
                if (now - error_time).total_seconds() < 86400:  # 24 hours
                    recent_errors.append(error)
            except:
                continue
        
        # Count error types
        error_types = {}
        for error in recent_errors:
            error_type = error.get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Identify patterns
        patterns = []
        if error_types.get('RateLimitError', 0) > 3:
            patterns.append("High rate limit violations detected")
        if error_types.get('APIError', 0) > 5:
            patterns.append("Frequent API errors - service issues possible")
        if 'quota' in str(errors).lower():
            patterns.append("OpenAI quota exhaustion affecting workflows")
        
        return {
            'total_errors': len(recent_errors),
            'error_types': error_types,
            'patterns': patterns,
            'recent_errors': recent_errors[-5:]  # Last 5 errors
        }

    def _print_error_analysis(self, analysis: Dict):
        """Print error analysis"""
        print(f"  📊 Total errors (24h): {analysis['total_errors']}")
        
        if analysis['error_types']:
            print("  🔍 Error breakdown:")
            for error_type, count in analysis['error_types'].items():
                print(f"    • {error_type}: {count}")
        
        if analysis['patterns']:
            print("  ⚠️ Patterns detected:")
            for pattern in analysis['patterns']:
                print(f"    • {pattern}")

    def _print_recovery_opportunities(self, recoverable: List):
        """Print recovery opportunities"""
        if not recoverable:
            print("  ✅ No failed workflows need recovery")
        else:
            print(f"  🔧 {len(recoverable)} workflows can be recovered:")
            for record in recoverable[:5]:  # Show top 5
                print(f"    • {record['title']} - {record['stage']['description']}")

    def _generate_recommendations(self, api_status: Dict, error_analysis: Dict, recoverable: List) -> List[str]:
        """Generate prevention recommendations"""
        recommendations = []
        
        # API-specific recommendations
        openai_status = api_status['apis'].get('openai', {}).get('status')
        if openai_status == 'quota_exhausted':
            recommendations.extend([
                "Implement OpenAI usage optimization (shorter prompts, fewer calls)",
                "Set up alternative content generation methods",
                "Consider upgrading OpenAI plan or add billing alerts"
            ])
        
        if openai_status == 'rate_limited':
            recommendations.append("Implement exponential backoff for OpenAI calls")
        
        # Error pattern recommendations
        if error_analysis['total_errors'] > 10:
            recommendations.append("Review and strengthen error handling in workflow components")
        
        if 'RateLimitError' in error_analysis.get('error_types', {}):
            recommendations.append("Implement comprehensive rate limiting across all API calls")
        
        if recoverable:
            recommendations.append("Set up automated workflow recovery to handle transient failures")
        
        # General recommendations
        recommendations.extend([
            "Enable proactive monitoring with alerts for quota thresholds",
            "Implement circuit breakers for all external API calls",
            "Create fallback content generation for quota exhaustion scenarios",
            "Set up daily health checks before workflow execution"
        ])
        
        return recommendations

    def _print_recommendations(self, recommendations: List[str]):
        """Print recommendations"""
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

    def _determine_immediate_actions(self, api_status: Dict, error_analysis: Dict, recoverable: List) -> List[str]:
        """Determine immediate actions needed"""
        actions = []
        
        # Critical API issues
        openai_status = api_status['apis'].get('openai', {}).get('status')
        if openai_status == 'quota_exhausted':
            actions.append("🚨 CRITICAL: OpenAI quota exhausted - add billing or wait for reset")
        
        # High error rate
        if error_analysis['total_errors'] > 20:
            actions.append("⚠️ HIGH: Review error logs and fix recurring issues")
        
        # Recovery opportunities
        if len(recoverable) > 5:
            actions.append(f"🔧 MODERATE: {len(recoverable)} workflows ready for recovery")
        
        # Preventive measures
        if not os.path.exists('/home/claude-workflow/api_status.json'):
            actions.append("📋 SETUP: Run quota monitoring before each workflow")
        
        return actions

    def _print_immediate_actions(self, actions: List[str]):
        """Print immediate actions"""
        if not actions:
            print("  ✅ No immediate actions required")
        else:
            for action in actions:
                print(f"  {action}")

    async def automated_health_check(self) -> bool:
        """Automated health check - returns True if workflow should run"""
        
        print("🔍 AUTOMATED HEALTH CHECK")
        print("-" * 30)
        
        # Check API status
        api_status = await self.quota_monitor.check_all_apis()
        
        # Critical checks
        openai_ok = api_status['apis'].get('openai', {}).get('status') in ['available', 'rate_limited']
        airtable_ok = api_status['apis'].get('airtable', {}).get('status') == 'available'
        json2video_ok = api_status['apis'].get('json2video', {}).get('status') == 'available'
        
        workflow_ready = openai_ok and airtable_ok and json2video_ok
        
        if workflow_ready:
            print("✅ All systems ready for workflow execution")
            
            # Check for quota exhaustion (can still run with fallbacks)
            if api_status['apis'].get('openai', {}).get('status') == 'quota_exhausted':
                print("⚠️ Note: OpenAI quota exhausted - will use content fallbacks")
                
            return True
        else:
            print("❌ Critical systems not ready:")
            if not openai_ok:
                print("  • OpenAI API issues")
            if not airtable_ok:
                print("  • Airtable API issues") 
            if not json2video_ok:
                print("  • JSON2Video API issues")
            
            return False

async def main():
    dashboard = ErrorPreventionDashboard()
    
    # Show menu
    print("🔧 ERROR PREVENTION DASHBOARD")
    print("=" * 40)
    print("1. Comprehensive analysis report")
    print("2. Quick health check")
    print("3. Recovery opportunities")
    print("4. API status only")
    print("q. Quit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == '1':
        await dashboard.generate_comprehensive_report()
    elif choice == '2':
        ready = await dashboard.automated_health_check()
        if ready:
            print("\n💡 Recommendation: Workflow can proceed")
        else:
            print("\n⚠️ Recommendation: Fix issues before running workflow")
    elif choice == '3':
        await dashboard.recovery_manager.interactive_recovery()
    elif choice == '4':
        await dashboard.quota_monitor.check_all_apis()
        dashboard.quota_monitor.print_status_report(await dashboard.quota_monitor.check_all_apis())
    elif choice.lower() != 'q':
        print("❌ Invalid option")

if __name__ == "__main__":
    asyncio.run(main())