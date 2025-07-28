#!/usr/bin/env python3
"""
Test API Credit Monitor Server
Test version with simulated monitoring
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCreditMonitorMCPServer:
    def __init__(self, config: Dict = None):
        """Initialize Test Credit Monitor Server"""
        self.config = config or {}
        self.alert_email = "shenolb@live.com"
        
        # Simulated API usage for testing
        self.apis = {
            "openai": {"name": "OpenAI", "current": 250, "limit": 1000, "cost": 5.50},
            "anthropic": {"name": "Anthropic Claude", "current": 180, "limit": 1000, "cost": 3.60},
            "elevenlabs": {"name": "ElevenLabs", "current": 1200, "limit": 10000, "cost": 12.00},
            "json2video": {"name": "JSON2Video", "current": 15, "limit": 100, "cost": 30.00},
            "scrapingdog": {"name": "ScrapingDog", "current": 450, "limit": 1000, "cost": 9.00}
        }
        
        logger.info("🔴 TEST API Credit Monitor initialized - simulating 5 APIs")

    async def check_all_api_credits(self) -> Dict[str, Any]:
        """Check credits for all APIs (TEST MODE)"""
        alerts = []
        total_cost = sum(api["cost"] for api in self.apis.values())
        
        for api_key, api_data in self.apis.items():
            usage_percent = (api_data["current"] / api_data["limit"]) * 100
            
            # Log current usage
            logger.info(f"📊 {api_data['name']}: {api_data['current']}/{api_data['limit']} ({usage_percent:.1f}%) - ${api_data['cost']:.2f}")
            
            # Generate test alerts for demonstration
            if usage_percent > 70:  # Lowered threshold for testing
                alert_type = "critical" if usage_percent > 90 else "urgent" if usage_percent > 80 else "warning"
                
                alerts.append({
                    "api": api_data["name"],
                    "usage_percent": usage_percent,
                    "alert_type": alert_type,
                    "current": api_data["current"],
                    "limit": api_data["limit"],
                    "cost": api_data["cost"]
                })
        
        if alerts:
            logger.warning(f"🚨 TEST MODE: {len(alerts)} API usage alerts generated")
            logger.warning(f"📧 In production, email would be sent to {self.alert_email}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_apis": len(self.apis),
            "alerts": alerts,
            "total_cost": total_cost,
            "status": "critical" if any(a["usage_percent"] > 90 for a in alerts) else "normal"
        }

    async def update_api_usage(self, api_name: str, usage_increment: int, cost_increment: float = 0) -> Dict[str, Any]:
        """Update usage for a specific API (TEST MODE)"""
        if api_name.lower() in self.apis:
            api_data = self.apis[api_name.lower()]
            api_data["current"] += usage_increment
            api_data["cost"] += cost_increment
            
            usage_percent = (api_data["current"] / api_data["limit"]) * 100
            
            logger.info(f"📊 TEST: {api_data['name']} usage updated: {api_data['current']}/{api_data['limit']} ({usage_percent:.1f}%)")
            
            return {
                "api": api_data["name"],
                "current": api_data["current"],
                "limit": api_data["limit"],
                "usage_percent": usage_percent,
                "cost": api_data["cost"]
            }
        
        return {"error": f"API {api_name} not found"}

    async def get_usage_report(self) -> Dict[str, Any]:
        """Generate TEST usage report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "TEST",
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
        
        logger.info(f"📊 TEST Credit Report: ${report['summary']['total_cost']:.2f} total cost")
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

    async def simulate_high_usage(self) -> Dict[str, Any]:
        """Simulate high usage for testing alerts"""
        logger.info("🧪 TEST: Simulating high API usage for alert testing...")
        
        # Simulate high usage on JSON2Video
        await self.update_api_usage("json2video", 80, 160.00)  # Push to 95%
        
        # Check for alerts
        alerts = await self.check_all_api_credits()
        
        logger.warning(f"🚨 TEST: Simulated {len(alerts['alerts'])} critical alerts")
        return alerts

# Testing function
async def test_credit_monitor():
    """Test the credit monitor functionality"""
    monitor = TestCreditMonitorMCPServer()
    
    print("🔴 Testing API Credit Monitor...")
    
    # Initial report
    report = await monitor.get_usage_report()
    print(f"📊 Initial total cost: ${report['summary']['total_cost']:.2f}")
    
    # Simulate high usage
    alerts = await monitor.simulate_high_usage()
    print(f"🚨 Critical alerts generated: {len(alerts['alerts'])}")
    
    return report

if __name__ == "__main__":
    asyncio.run(test_credit_monitor())