"""
Base Agent Class
================
Foundation for all main agents in the system.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum

from .agent_protocol import AgentMessage, MessageType, get_message_bus
from .agent_state import WorkflowStateManager, WorkflowState


class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


class BaseAgent(ABC):
    """
    Base class for all main agents
    Provides common functionality for lifecycle, communication, and error handling
    """

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"Agent.{agent_id}")

        # Communication
        self.message_bus = None
        self.sub_agents: List['BaseSubAgent'] = []

        # State
        self.current_task = None
        self.task_queue = asyncio.Queue()

        # Metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time = 0.0

        self.logger.info(f"🤖 Agent initialized: {agent_id}")

    async def initialize(self):
        """Initialize agent (override if needed)"""
        self.message_bus = await get_message_bus()

        # Subscribe to messages
        self.message_bus.subscribe(
            self.agent_id,
            [MessageType.TASK_REQUEST, MessageType.CANCEL_REQUEST],
            self._handle_message
        )

        self.logger.info(f"✅ Agent {self.agent_id} initialized")

    async def start(self):
        """Start the agent"""
        self.status = AgentStatus.IDLE
        asyncio.create_task(self._process_task_queue())
        self.logger.info(f"▶️  Agent {self.agent_id} started")

    async def stop(self):
        """Stop the agent"""
        self.status = AgentStatus.STOPPED
        self.logger.info(f"⏸️  Agent {self.agent_id} stopped")

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task (must be implemented by subclass)

        Args:
            task: Task parameters

        Returns:
            Result dictionary
        """
        pass

    async def delegate_to_subagent(self, subagent_class: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate task to a sub-agent

        Args:
            subagent_class: Name of sub-agent class
            task: Task to delegate

        Returns:
            Sub-agent result
        """
        # Find sub-agent by class name
        subagent = next((sa for sa in self.sub_agents if sa.__class__.__name__ == subagent_class), None)

        if not subagent:
            raise ValueError(f"Sub-agent not found: {subagent_class}")

        self.logger.debug(f"📤 Delegating to {subagent_class}")
        result = await subagent.execute(task)
        self.logger.debug(f"📥 Received from {subagent_class}")

        return result

    async def _handle_message(self, message: AgentMessage):
        """Handle incoming messages"""
        self.logger.debug(f"📨 Received message: {message}")

        if message.message_type == MessageType.TASK_REQUEST:
            await self.task_queue.put(message.payload)

        elif message.message_type == MessageType.CANCEL_REQUEST:
            # Cancel current task
            if self.current_task:
                self.logger.warning(f"🚫 Task cancelled: {self.current_task}")
                self.current_task = None

    async def _process_task_queue(self):
        """Process tasks from queue"""
        while self.status != AgentStatus.STOPPED:
            try:
                # Wait for task (with timeout to check status periodically)
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )

                self.status = AgentStatus.BUSY
                self.current_task = task

                start_time = time.time()

                try:
                    # Execute task
                    result = await self.execute_task(task)

                    # Update metrics
                    duration = time.time() - start_time
                    self.total_execution_time += duration
                    self.tasks_completed += 1

                    self.logger.info(f"✅ Task completed in {duration:.2f}s")

                    # Send completion message
                    if self.message_bus:
                        completion_msg = AgentMessage(
                            sender=self.agent_id,
                            receiver=task.get('requester', 'orchestrator'),
                            message_type=MessageType.COMPLETION,
                            payload={'result': result, 'duration': duration},
                            correlation_id=task.get('correlation_id', '')
                        )
                        await self.message_bus.send(completion_msg)

                except Exception as e:
                    # Task failed
                    duration = time.time() - start_time
                    self.tasks_failed += 1

                    self.logger.error(f"❌ Task failed: {e}")

                    # Send error report
                    if self.message_bus:
                        error_msg = AgentMessage(
                            sender=self.agent_id,
                            receiver=task.get('requester', 'orchestrator'),
                            message_type=MessageType.ERROR_REPORT,
                            payload={'error': str(e), 'task': task},
                            correlation_id=task.get('correlation_id', '')
                        )
                        await self.message_bus.send(error_msg)

                finally:
                    self.current_task = None
                    self.status = AgentStatus.IDLE

            except asyncio.TimeoutError:
                # No task in queue, continue waiting
                continue
            except Exception as e:
                self.logger.error(f"Error in task processing: {e}")
                self.status = AgentStatus.ERROR

    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        avg_time = self.total_execution_time / self.tasks_completed if self.tasks_completed > 0 else 0

        return {
            'agent_id': self.agent_id,
            'status': self.status.value,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_execution_time': self.total_execution_time,
            'average_task_time': avg_time,
            'success_rate': (self.tasks_completed / (self.tasks_completed + self.tasks_failed * 100)
                           if (self.tasks_completed + self.tasks_failed) > 0 else 0)
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.agent_id}, status={self.status.value})>"
