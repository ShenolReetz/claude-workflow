"""Monitoring Agent - Manages error recovery, metrics, costs, and reporting"""
import sys
sys.path.append('/home/claude-workflow')
from agents.base_agent import BaseAgent
from .error_recovery_subagent import ErrorRecoverySubAgent
from .metrics_collector_subagent import MetricsCollectorSubAgent
from .cost_tracker_subagent import CostTrackerSubAgent
from .reporting_subagent import ReportingSubAgent
from typing import Dict, Any, List

class MonitoringAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__("monitoring", config)
        self.sub_agents = [
            ErrorRecoverySubAgent("error_recovery", config, self.agent_id),
            MetricsCollectorSubAgent("metrics_collector", config, self.agent_id),
            CostTrackerSubAgent("cost_tracker", config, self.agent_id),
            ReportingSubAgent("reporting", config, self.agent_id),
        ]
        self.logger.info(f"✅ MonitoringAgent initialized with {len(self.sub_agents)} sub-agents")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        phase = task.get('phase', '')
        self.logger.info(f"📊 Executing monitoring phase: {phase}")

        try:
            if phase == 'finalize':
                return await self._finalize_workflow(task)
            else:
                return {'status': 'monitored'}
        except Exception as e:
            self.logger.error(f"❌ Monitoring failed: {e}")
            raise

    async def _finalize_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final workflow report"""
        self.logger.info("📊 Finalizing workflow and generating report...")

        # Collect metrics
        metrics = await self.delegate_to_subagent('MetricsCollectorSubAgent', task)

        # Track costs
        costs = await self.delegate_to_subagent('CostTrackerSubAgent', task)

        # Generate report
        report = await self.delegate_to_subagent('ReportingSubAgent', {
            **task,
            'metrics': metrics['result'],
            'costs': costs['result']
        })

        return {
            'metrics': metrics['result'],
            'costs': costs['result'],
            'report': report['result'],
            'status': 'finalized'
        }

    def get_capabilities(self) -> List[str]:
        return ['error_recovery', 'metrics_collection', 'cost_tracking', 'reporting', 'finalize']
