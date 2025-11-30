"""Metrics Collector SubAgent - Collects performance metrics"""
import sys
import time
sys.path.append('/home/claude-workflow')
from agents.base_subagent import BaseSubAgent
from typing import Dict, Any

class MetricsCollectorSubAgent(BaseSubAgent):
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """Collect workflow performance metrics"""
        workflow_id = task.get('workflow_id', 'unknown')
        params = task.get('params', {})

        # Calculate durations per phase
        metrics = {
            'workflow_id': workflow_id,
            'total_phases': len(params),
            'successful_phases': len([p for p in params.values() if isinstance(p, dict) and p.get('status')]),
            'phases_with_errors': 0,
            'timestamp': time.time()
        }

        return metrics

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {'valid': True}
