"""
Base Sub-Agent Class
====================
Foundation for all specialized sub-agents.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class SubAgentStatus(Enum):
    """Sub-agent status"""
    READY = "ready"
    EXECUTING = "executing"
    ERROR = "error"


class BaseSubAgent(ABC):
    """
    Base class for all sub-agents
    Sub-agents are specialized workers that perform specific tasks
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: Optional[str] = None):
        self.name = name
        self.config = config
        self.parent_agent_id = parent_agent_id
        self.status = SubAgentStatus.READY
        self.logger = logging.getLogger(f"SubAgent.{name}")

        # Metrics
        self.executions = 0
        self.failures = 0
        self.total_time = 0.0

        # Retry configuration
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 1.0)

        self.logger.info(f"🔧 Sub-agent initialized: {name}")

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task with retry logic

        Args:
            task: Task parameters

        Returns:
            Result dictionary
        """
        self.status = SubAgentStatus.EXECUTING
        start_time = time.time()

        retry_count = 0
        last_error = None

        while retry_count <= self.max_retries:
            try:
                self.logger.debug(f"🔄 Executing {self.name} (attempt {retry_count + 1})")

                # Validate input
                validation_result = await self.validate_input(task)
                if not validation_result['valid']:
                    raise ValueError(f"Invalid input: {validation_result.get('error')}")

                # Execute main logic
                result = await self.execute_task(task)

                # Validate output
                output_validation = await self.validate_output(result)
                if not output_validation['valid']:
                    raise ValueError(f"Invalid output: {output_validation.get('error')}")

                # Success
                duration = time.time() - start_time
                self.executions += 1
                self.total_time += duration
                self.status = SubAgentStatus.READY

                self.logger.info(f"✅ {self.name} completed in {duration:.2f}s")

                return {
                    'success': True,
                    'result': result,
                    'duration': duration,
                    'retries': retry_count
                }

            except Exception as e:
                last_error = e
                retry_count += 1

                self.logger.warning(f"⚠️  {self.name} failed (attempt {retry_count}): {e}")

                if retry_count <= self.max_retries:
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(self.retry_delay * retry_count)
                else:
                    # Max retries exceeded
                    break

        # All retries failed
        duration = time.time() - start_time
        self.failures += 1
        self.total_time += duration
        self.status = SubAgentStatus.ERROR

        self.logger.error(f"❌ {self.name} failed after {retry_count} attempts: {last_error}")

        return {
            'success': False,
            'error': str(last_error),
            'duration': duration,
            'retries': retry_count
        }

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Execute the main task logic (must be implemented by subclass)

        Args:
            task: Task parameters

        Returns:
            Task result (any type)
        """
        pass

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input parameters (override if needed)

        Args:
            task: Task parameters

        Returns:
            {'valid': bool, 'error': Optional[str]}
        """
        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """
        Validate output result (override if needed)

        Args:
            result: Task result

        Returns:
            {'valid': bool, 'error': Optional[str]}
        """
        return {'valid': True}

    def get_metrics(self) -> Dict[str, Any]:
        """Get sub-agent metrics"""
        avg_time = self.total_time / self.executions if self.executions > 0 else 0
        success_rate = (self.executions / (self.executions + self.failures) * 100
                       if (self.executions + self.failures) > 0 else 0)

        return {
            'name': self.name,
            'status': self.status.value,
            'executions': self.executions,
            'failures': self.failures,
            'total_time': self.total_time,
            'average_time': avg_time,
            'success_rate': success_rate
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name}, status={self.status.value})>"


# Import asyncio for retry delay
import asyncio
