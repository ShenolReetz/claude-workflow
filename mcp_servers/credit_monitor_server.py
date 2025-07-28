#!/usr/bin/env python3
"""
API Credit Monitor Server
Monitors API usage across all services and sends alerts
"""

import json
import smtplib
import asyncio
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CreditMonitorMCPServer:
    def __init__(self, config: Dict = None):
        """Initialize Credit Monitor Server"""
        self.config = config or {}
        self.alert_email = "shenolb@live.com"
        self.thresholds = {
            50: "warning",
            75: "urgent", 
            85: "critical",
            90: "emergency",
            95: "service_protection"
        }
        
        # API endpoints and usage tracking
        self.apis = {
            "openai": {"name": "OpenAI", "current": 0, "limit": 1000, "cost": 0},
            "anthropic": {"name": "Anthropic Claude", "current": 0, "limit": 1000, "cost": 0},
            "elevenlabs": {"name": "ElevenLabs", "current": 0, "limit": 10000, "cost": 0},
            "json2video": {"name": "JSON2Video", "current": 0, "limit": 100, "cost": 0},
            "scrapingdog": {"name": "ScrapingDog", "current": 0, "limit": 1000, "cost": 0}
        }
        
        logger.info("🔴 API Credit Monitor initialized - monitoring 5 APIs")

    async def check_all_api_credits(self) -> Dict[str, Any]:
        """Check credits for all APIs and generate alerts if needed"""
        alerts = []
        total_cost = 0
        
        for api_key, api_data in self.apis.items():
            usage_percent = (api_data["current"] / api_data["limit"]) * 100
            total_cost += api_data["cost"]
            
            # Check if any threshold is crossed
            for threshold, alert_type in self.thresholds.items():
                if usage_percent >= threshold:
                    alert = {
                        "api": api_data["name"],
                        "usage_percent": usage_percent,
                        "alert_type": alert_type,
                        "current": api_data["current"],
                        "limit": api_data["limit"],
                        "cost": api_data["cost"]
                    }
                    alerts.append(alert)
                    
                    # Send email for critical alerts
                    if threshold >= 75:
                        await self._send_email_alert(alert)
                    break
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_apis": len(self.apis),
            "alerts": alerts,
            "total_cost": total_cost,
            "status": "critical" if any(a["alert_type"] in ["critical", "emergency", "service_protection"] for a in alerts) else "normal"
        }

    async def update_api_usage(self, api_name: str, usage_increment: int, cost_increment: float = 0) -> Dict[str, Any]:
        """Update usage for a specific API"""
        if api_name.lower() in self.apis:
            api_data = self.apis[api_name.lower()]
            api_data["current"] += usage_increment
            api_data["cost"] += cost_increment
            
            usage_percent = (api_data["current"] / api_data["limit"]) * 100
            
            logger.info(f"📊 {api_data['name']} usage: {api_data['current']}/{api_data['limit']} ({usage_percent:.1f}%)")
            
            return {
                "api": api_data["name"],
                "current": api_data["current"],
                "limit": api_data["limit"],
                "usage_percent": usage_percent,
                "cost": api_data["cost"]
            }
        
        return {"error": f"API {api_name} not found"}

    async def _send_email_alert(self, alert: Dict) -> bool:
        """Send email alert for API usage threshold"""
        try:
            subject = f"[ALERT] {alert['api']} Credit Warning - {alert['usage_percent']:.1f}% Used"
            
            body = f"""
API Credit Alert - Immediate Action Required

Current Usage:
- API: {alert['api']}
- Credits Used: {alert['current']}/{alert['limit']}
- Percentage: {alert['usage_percent']:.1f}%
- Current Cost: ${alert['cost']:.2f}
- Alert Level: {alert['alert_type'].upper()}

Recommendations:
{self._get_optimization_suggestions(alert)}

Action Required:
{self._get_required_actions(alert)}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated alert from Claude Workflow API Credit Monitor.
"""
            
            # In a real implementation, you would configure SMTP settings
            logger.warning(f"🚨 EMAIL ALERT would be sent to {self.alert_email}")
            logger.warning(f"📧 Subject: {subject}")
            logger.warning(f"📝 Alert Level: {alert['alert_type'].upper()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email alert: {e}")
            return False

    def _get_optimization_suggestions(self, alert: Dict) -> str:
        """Get optimization suggestions based on API and usage"""
        suggestions = {
            "OpenAI": "- Consider using Claude for text generation\n- Implement response caching\n- Reduce image generation frequency",
            "Anthropic Claude": "- Implement intelligent caching\n- Optimize prompt lengths\n- Use batch processing",
            "ElevenLabs": "- Use shorter voice clips\n- Cache generated audio\n- Consider alternative TTS services",
            "JSON2Video": "- Optimize video templates\n- Reduce video generation frequency\n- Use cached video elements",
            "ScrapingDog": "- Implement result caching\n- Reduce scraping frequency\n- Use alternative data sources"
        }
        
        return suggestions.get(alert['api'], "- Review usage patterns\n- Implement caching\n- Consider alternatives")

    def _get_required_actions(self, alert: Dict) -> str:
        """Get required actions based on alert level"""
        actions = {
            "warning": "- Monitor usage closely\n- Review optimization opportunities",
            "urgent": "- Implement usage restrictions\n- Enable caching immediately",
            "critical": "- Pause non-essential operations\n- Review billing limits",
            "emergency": "- Stop all non-critical API calls\n- Contact billing support",
            "service_protection": "- EMERGENCY: Stop all operations\n- Add credits immediately"
        }
        
        return actions.get(alert['alert_type'], "- Review usage and optimize")

    async def get_usage_report(self) -> Dict[str, Any]:
        """Generate comprehensive usage report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "apis": {},
            "summary": {
                "total_cost": 0,
                "highest_usage_percent": 0,
                "apis_over_50_percent": 0,
                "critical_apis": []
            }
        }
        
        for api_key, api_data in self.apis.items():
            usage_percent = (api_data["current"] / api_data["limit"]) * 100
            
            report["apis"][api_key] = {
                "name": api_data["name"],
                "current": api_data["current"],
                "limit": api_data["limit"],
                "usage_percent": usage_percent,
                "cost": api_data["cost"],
                "status": self._get_usage_status(usage_percent)
            }
            
            report["summary"]["total_cost"] += api_data["cost"]
            
            if usage_percent > report["summary"]["highest_usage_percent"]:
                report["summary"]["highest_usage_percent"] = usage_percent
                
            if usage_percent > 50:
                report["summary"]["apis_over_50_percent"] += 1
                
            if usage_percent > 85:
                report["summary"]["critical_apis"].append(api_data["name"])
        
        return report

    def _get_usage_status(self, usage_percent: float) -> str:
        """Get status based on usage percentage"""
        if usage_percent >= 95:
            return "service_protection"
        elif usage_percent >= 90:
            return "emergency"
        elif usage_percent >= 85:
            return "critical"
        elif usage_percent >= 75:
            return "urgent"
        elif usage_percent >= 50:
            return "warning"
        else:
            return "normal"

    async def reset_api_usage(self, api_name: str) -> Dict[str, Any]:
        """Reset usage for a specific API (for testing or new billing cycle)"""
        if api_name.lower() in self.apis:
            self.apis[api_name.lower()]["current"] = 0
            self.apis[api_name.lower()]["cost"] = 0
            
            return {
                "api": self.apis[api_name.lower()]["name"],
                "status": "reset",
                "message": f"Usage reset for {self.apis[api_name.lower()]['name']}"
            }
        
        return {"error": f"API {api_name} not found"}

# Example usage and testing
async def test_credit_monitor():
    """Test the credit monitor functionality"""
    monitor = CreditMonitorMCPServer()
    
    # Simulate some usage
    await monitor.update_api_usage("openai", 750, 15.50)  # 75% usage
    await monitor.update_api_usage("json2video", 92, 184.00)  # 92% usage
    
    # Check for alerts
    alerts = await monitor.check_all_api_credits()
    print(f"🔴 Alerts generated: {len(alerts['alerts'])}")
    
    # Generate report
    report = await monitor.get_usage_report()
    print(f"📊 Total cost: ${report['summary']['total_cost']:.2f}")
    
    return report

if __name__ == "__main__":
    asyncio.run(test_credit_monitor())