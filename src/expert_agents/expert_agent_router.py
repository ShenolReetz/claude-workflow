#!/usr/bin/env python3
"""
Expert Agent Router/Dispatcher System v4.1
Routes tasks to 16 specialized expert AI subagents across 6 color-coded categories
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCategory(Enum):
    """6 color-coded expert agent categories"""
    CRITICAL_SECURITY = "🔴"  # Critical/Security Agents
    CONTENT_CREATION = "🟠"  # Content Creation Agents  
    QUALITY_CONTROL = "🟡"  # Quality Control Agents
    ANALYTICS_PERFORMANCE = "🟢"  # Analytics/Performance Agents
    OPERATIONS = "🔵"  # Operations Agents
    SUPPORT = "🟣"  # Support Agents

class TaskType(Enum):
    """Task types that can be routed to expert agents"""
    # Critical/Security Tasks
    API_MONITORING = "api_monitoring"
    ERROR_RECOVERY = "error_recovery"
    
    # Content Creation Tasks
    VIDEO_CREATION = "video_creation"
    SEO_OPTIMIZATION = "seo_optimization"
    PRODUCT_RESEARCH = "product_research"
    
    # Quality Control Tasks
    VISUAL_QUALITY = "visual_quality"
    AUDIO_SYNC = "audio_sync" 
    COMPLIANCE_CHECK = "compliance_check"
    VIDEO_STATUS_MONITORING = "video_status_monitoring"
    
    # Analytics/Performance Tasks
    PERFORMANCE_TRACKING = "performance_tracking"
    TREND_ANALYSIS = "trend_analysis"
    MONETIZATION = "monetization"
    
    # Operations Tasks
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    CROSS_PLATFORM = "cross_platform"
    AI_OPTIMIZATION = "ai_optimization"
    AMAZON_SCRAPING = "amazon_scraping"
    
    # Support Tasks
    DOCUMENTATION = "documentation"
    AIRTABLE_MANAGEMENT = "airtable_management"

class ExpertAgentRouter:
    """
    Central Expert Agent Router/Dispatcher System
    
    Routes tasks to 18 specialized expert AI subagents:
    🔴 Critical/Security (2) | 🟠 Content Creation (3) | 🟡 Quality Control (4)
    🟢 Analytics/Performance (3) | 🔵 Operations (4) | 🟣 Support (2)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_agents = {}
        self.task_history = []
        
        # Initialize expert agent registry
        self.expert_agents = {
            # 🔴 Critical/Security Agents (2)
            "api-credit-monitor": {
                "category": AgentCategory.CRITICAL_SECURITY,
                "specialization": "API usage monitoring and credit alerts",
                "task_types": [TaskType.API_MONITORING],
                "priority": "critical",
                "status": "active"
            },
            "error-recovery-specialist": {
                "category": AgentCategory.CRITICAL_SECURITY,
                "specialization": "System failure handling and workflow resilience",
                "task_types": [TaskType.ERROR_RECOVERY],
                "priority": "critical",
                "status": "active"
            },
            
            # 🟠 Content Creation Agents (3)
            "json2video-engagement-expert": {
                "category": AgentCategory.CONTENT_CREATION,
                "specialization": "Viral-worthy professional 9:16 videos under 60 seconds",
                "task_types": [TaskType.VIDEO_CREATION],
                "priority": "high",
                "status": "active"
            },
            "seo-optimization-expert": {
                "category": AgentCategory.CONTENT_CREATION,
                "specialization": "Search visibility maximization across all platforms",
                "task_types": [TaskType.SEO_OPTIMIZATION],
                "priority": "high",
                "status": "active"
            },
            "product-research-validator": {
                "category": AgentCategory.CONTENT_CREATION,
                "specialization": "High-quality product validation and research",
                "task_types": [TaskType.PRODUCT_RESEARCH],
                "priority": "high",
                "status": "active"
            },
            
            # 🟡 Quality Control Agents (4)
            "visual-quality-controller": {
                "category": AgentCategory.QUALITY_CONTROL,
                "specialization": "Brand consistency and visual excellence",
                "task_types": [TaskType.VISUAL_QUALITY],
                "priority": "high",
                "status": "active"
            },
            "audio-sync-specialist": {
                "category": AgentCategory.QUALITY_CONTROL,
                "specialization": "Perfect audio-video synchronization",
                "task_types": [TaskType.AUDIO_SYNC],
                "priority": "high",
                "status": "active"
            },
            "compliance-safety-monitor": {
                "category": AgentCategory.QUALITY_CONTROL,
                "specialization": "Platform policy compliance maintenance",
                "task_types": [TaskType.COMPLIANCE_CHECK],
                "priority": "medium",
                "status": "active"
            },
            "video-status-specialist": {
                "category": AgentCategory.QUALITY_CONTROL,
                "specialization": "Real-time video generation status monitoring",
                "task_types": [TaskType.VIDEO_STATUS_MONITORING],
                "priority": "high",
                "status": "active"
            },
            
            # 🟢 Analytics/Performance Agents (3)
            "analytics-performance-tracker": {
                "category": AgentCategory.ANALYTICS_PERFORMANCE,
                "specialization": "Performance metrics tracking and insights generation",
                "task_types": [TaskType.PERFORMANCE_TRACKING],
                "priority": "medium",
                "status": "active"
            },
            "trend-analysis-planner": {
                "category": AgentCategory.ANALYTICS_PERFORMANCE,
                "specialization": "Emerging trends and market opportunity identification",
                "task_types": [TaskType.TREND_ANALYSIS],
                "priority": "medium",
                "status": "active"
            },
            "monetization-strategist": {
                "category": AgentCategory.ANALYTICS_PERFORMANCE,
                "specialization": "Revenue generation strategy optimization",
                "task_types": [TaskType.MONETIZATION],
                "priority": "medium",
                "status": "active"
            },
            
            # 🔵 Operations Agents (4) 
            "workflow-efficiency-optimizer": {
                "category": AgentCategory.OPERATIONS,
                "specialization": "Processing efficiency maximization",
                "task_types": [TaskType.WORKFLOW_OPTIMIZATION], 
                "priority": "medium",
                "status": "active"
            },
            "cross-platform-coordinator": {
                "category": AgentCategory.OPERATIONS,
                "specialization": "Multi-platform content distribution management",
                "task_types": [TaskType.CROSS_PLATFORM],
                "priority": "high",
                "status": "active"
            },
            "ai-optimization-specialist": {
                "category": AgentCategory.OPERATIONS,
                "specialization": "AI model usage and cost optimization",
                "task_types": [TaskType.AI_OPTIMIZATION],
                "priority": "medium",
                "status": "active"
            },
            "amazon-scraping-specialist": {
                "category": AgentCategory.OPERATIONS,
                "specialization": "Advanced Amazon product scraping with review-based ranking",
                "task_types": [TaskType.AMAZON_SCRAPING],
                "priority": "high",
                "status": "active"
            },
            
            # 🟣 Support Agents (2)
            "documentation-specialist": {
                "category": AgentCategory.SUPPORT,
                "specialization": "Comprehensive technical documentation maintenance",
                "task_types": [TaskType.DOCUMENTATION],
                "priority": "low",
                "status": "active"
            },
            "airtable-specialist": {
                "category": AgentCategory.SUPPORT,
                "specialization": "Professional Airtable data management and column expertise",
                "task_types": [TaskType.AIRTABLE_MANAGEMENT],
                "priority": "high", 
                "status": "active"
            }
        }
        
        logger.info("🎯 Expert Agent Router initialized with 18 specialized subagents")
        logger.info(f"   🔴 Critical/Security: 2 agents")
        logger.info(f"   🟠 Content Creation: 3 agents") 
        logger.info(f"   🟡 Quality Control: 4 agents")
        logger.info(f"   🟢 Analytics/Performance: 3 agents")
        logger.info(f"   🔵 Operations: 4 agents")
        logger.info(f"   🟣 Support: 2 agents")
    
    async def route_task(self, task_type: TaskType, task_data: Dict[str, Any], 
                        priority: str = "medium") -> Dict[str, Any]:
        """
        Route a task to the appropriate expert agent
        
        Args:
            task_type: Type of task to route
            task_data: Data needed for task execution
            priority: Task priority (critical, high, medium, low)
            
        Returns:
            Task execution result from the expert agent
        """
        logger.info(f"🎯 Routing task: {task_type.value} (priority: {priority})")
        
        # Find the best expert agent for this task
        suitable_agent = self._find_best_agent(task_type, priority)
        
        if not suitable_agent:
            logger.error(f"❌ No suitable expert agent found for task: {task_type.value}")
            return {
                "success": False,
                "error": f"No expert agent available for task type: {task_type.value}",
                "task_type": task_type.value
            }
        
        # Log agent selection
        agent_info = self.expert_agents[suitable_agent]
        category_emoji = agent_info["category"].value
        logger.info(f"   {category_emoji} Selected agent: {suitable_agent}")
        logger.info(f"   🎯 Specialization: {agent_info['specialization']}")
        
        # Execute task with the selected expert agent
        try:
            result = await self._execute_with_agent(suitable_agent, task_type, task_data)
            
            # Record task in history
            self.task_history.append({
                "timestamp": datetime.now().isoformat(),
                "task_type": task_type.value,
                "agent": suitable_agent,
                "priority": priority,
                "success": result.get("success", False),
                "duration": result.get("duration", 0)
            })
            
            logger.info(f"✅ Task completed by {suitable_agent}: {result.get('success', False)}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Task execution failed with {suitable_agent}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": suitable_agent,
                "task_type": task_type.value
            }
    
    def _find_best_agent(self, task_type: TaskType, priority: str) -> Optional[str]:
        """Find the best expert agent for a given task type and priority"""
        
        suitable_agents = []
        
        for agent_id, agent_info in self.expert_agents.items():
            if (task_type in agent_info["task_types"] and 
                agent_info["status"] == "active"):
                suitable_agents.append((agent_id, agent_info))
        
        if not suitable_agents:
            return None
        
        # If multiple agents can handle the task, prefer by priority match
        if len(suitable_agents) == 1:
            return suitable_agents[0][0]
        
        # Multi-agent selection logic (prefer exact priority match)
        for agent_id, agent_info in suitable_agents:
            if agent_info["priority"] == priority:
                return agent_id
        
        # Fallback to first suitable agent
        return suitable_agents[0][0]
    
    async def _execute_with_agent(self, agent_id: str, task_type: TaskType, 
                                 task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with a specific expert agent"""
        
        start_time = datetime.now()
        
        # Import and execute the appropriate agent
        try:
            if agent_id == "api-credit-monitor":
                from src.expert_agents.critical_security.api_credit_monitor import execute_task
            elif agent_id == "error-recovery-specialist":
                from src.expert_agents.critical_security.error_recovery_specialist import execute_task
            elif agent_id == "json2video-engagement-expert":
                from src.expert_agents.content_creation.json2video_engagement_expert import execute_task
            elif agent_id == "seo-optimization-expert":
                from src.expert_agents.content_creation.seo_optimization_expert import execute_task
            elif agent_id == "product-research-validator":
                from src.expert_agents.content_creation.product_research_validator import execute_task
            elif agent_id == "visual-quality-controller":
                from src.expert_agents.quality_control.visual_quality_controller import execute_task
            elif agent_id == "audio-sync-specialist":
                from src.expert_agents.quality_control.audio_sync_specialist import execute_task
            elif agent_id == "compliance-safety-monitor":
                from src.expert_agents.quality_control.compliance_safety_monitor import execute_task
            elif agent_id == "video-status-specialist":
                from src.expert_agents.quality_control.video_status_specialist import execute_task
            elif agent_id == "analytics-performance-tracker":
                from src.expert_agents.analytics_performance.analytics_performance_tracker import execute_task
            elif agent_id == "trend-analysis-planner":
                from src.expert_agents.analytics_performance.trend_analysis_planner import execute_task
            elif agent_id == "monetization-strategist":
                from src.expert_agents.analytics_performance.monetization_strategist import execute_task
            elif agent_id == "workflow-efficiency-optimizer":
                from src.expert_agents.operations.workflow_efficiency_optimizer import execute_task
            elif agent_id == "cross-platform-coordinator":
                from src.expert_agents.operations.cross_platform_coordinator import execute_task
            elif agent_id == "ai-optimization-specialist":
                from src.expert_agents.operations.ai_optimization_specialist import execute_task
            elif agent_id == "documentation-specialist":
                from src.expert_agents.support.documentation_specialist import execute_task
            elif agent_id == "airtable-specialist":
                from src.expert_agents.support.airtable_specialist import execute_task
            elif agent_id == "amazon-scraping-specialist":
                from src.expert_agents.operations.amazon_scraping_specialist import execute_task
            else:
                raise ValueError(f"Unknown expert agent: {agent_id}")
            
            # Execute the task with the expert agent
            result = await execute_task(task_type, task_data, self.config)
            
            # Calculate execution time
            duration = (datetime.now() - start_time).total_seconds()
            result["duration"] = duration
            result["agent"] = agent_id
            
            return result
            
        except ImportError as e:
            logger.error(f"❌ Expert agent {agent_id} not implemented yet: {e}")
            return {
                "success": False,
                "error": f"Expert agent {agent_id} not implemented yet",
                "agent": agent_id,
                "implementation_needed": True
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all expert agents"""
        
        status = {
            "total_agents": len(self.expert_agents),
            "active_agents": len([a for a in self.expert_agents.values() if a["status"] == "active"]),
            "categories": {},
            "recent_tasks": len(self.task_history[-10:]) if self.task_history else 0
        }
        
        # Count agents by category
        for agent_info in self.expert_agents.values():
            category = agent_info["category"].value
            if category not in status["categories"]:
                status["categories"][category] = 0
            status["categories"][category] += 1
        
        return status
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent task execution history"""
        return self.task_history[-limit:] if self.task_history else []

# Singleton instance for global access
_expert_router = None

def get_expert_router(config: Dict[str, Any] = None) -> ExpertAgentRouter:
    """Get or create the global Expert Agent Router instance"""
    global _expert_router
    
    if _expert_router is None and config is not None:
        _expert_router = ExpertAgentRouter(config)
    
    return _expert_router

async def route_to_expert(task_type: TaskType, task_data: Dict[str, Any], 
                         priority: str = "medium") -> Dict[str, Any]:
    """
    Convenience function to route tasks to expert agents
    
    Usage:
        result = await route_to_expert(TaskType.VIDEO_CREATION, {
            "record_data": record_data,
            "project_name": "Test Video"
        }, priority="high")
    """
    router = get_expert_router()
    if router is None:
        raise RuntimeError("Expert Agent Router not initialized. Call get_expert_router(config) first.")
    
    return await router.route_task(task_type, task_data, priority)