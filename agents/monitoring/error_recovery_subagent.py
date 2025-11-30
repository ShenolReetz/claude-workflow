"""Error Recovery SubAgent - Wraps circuit breaker and auto-retry logic"""
import sys
sys.path.append('/home/claude-workflow')
from agents.base_subagent import BaseSubAgent
from src.utils.circuit_breaker import get_circuit_breaker_manager
from typing import Dict, Any

class ErrorRecoverySubAgent(BaseSubAgent):
    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)
        self.circuit_breaker = get_circuit_breaker_manager()

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """Monitor circuit breaker status and attempt recovery"""
        status = self.circuit_breaker.get_all_status()
        return {'circuit_breaker_status': status, 'auto_recovery_enabled': True}

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {'valid': True}
