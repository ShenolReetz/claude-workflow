"""
Agent Communication Protocol
============================
Message-based communication system for inter-agent communication.
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can send/receive"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    ERROR_REPORT = "error_report"
    COMPLETION = "completion"
    HEARTBEAT = "heartbeat"
    CANCEL_REQUEST = "cancel_request"


@dataclass
class AgentMessage:
    """
    Message structure for agent communication
    """
    sender: str
    receiver: str
    message_type: MessageType
    payload: Dict[str, Any]
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    priority: int = 5  # 1-10, higher is more urgent

    def __str__(self):
        return f"Message({self.message_type.value}: {self.sender} → {self.receiver})"


class AgentMessageBus:
    """
    Central message bus for agent communication
    Supports pub/sub pattern and direct messaging
    """

    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.logger = logging.getLogger(__name__)

    async def start(self):
        """Start the message bus"""
        self.running = True
        self.logger.info("📡 Agent Message Bus started")
        asyncio.create_task(self._process_messages())

    async def stop(self):
        """Stop the message bus"""
        self.running = False
        self.logger.info("📡 Agent Message Bus stopped")

    async def send(self, message: AgentMessage):
        """
        Send message to specific receiver
        """
        self.logger.debug(f"📤 Sending: {message}")
        await self.message_queue.put(message)

    async def broadcast(self, message: AgentMessage):
        """
        Broadcast message to all subscribers of this message type
        """
        self.logger.debug(f"📢 Broadcasting: {message}")
        message.receiver = "*"  # Broadcast marker
        await self.message_queue.put(message)

    def subscribe(self, agent_id: str, message_types: List[MessageType],
                  callback: Callable):
        """
        Subscribe to specific message types

        Args:
            agent_id: ID of subscribing agent
            message_types: List of message types to subscribe to
            callback: Async function to call when message received
        """
        for msg_type in message_types:
            key = f"{agent_id}:{msg_type.value}"
            if key not in self.subscribers:
                self.subscribers[key] = set()
            self.subscribers[key].add(callback)

        self.logger.info(f"🔔 {agent_id} subscribed to {[mt.value for mt in message_types]}")

    def unsubscribe(self, agent_id: str, message_types: Optional[List[MessageType]] = None):
        """Unsubscribe from message types"""
        if message_types is None:
            # Unsubscribe from all
            keys_to_remove = [k for k in self.subscribers.keys() if k.startswith(f"{agent_id}:")]
            for key in keys_to_remove:
                del self.subscribers[key]
        else:
            for msg_type in message_types:
                key = f"{agent_id}:{msg_type.value}"
                if key in self.subscribers:
                    del self.subscribers[key]

    async def _process_messages(self):
        """Process messages from queue"""
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                # Broadcast or direct send
                if message.receiver == "*":
                    await self._broadcast_message(message)
                else:
                    await self._deliver_message(message)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")

    async def _deliver_message(self, message: AgentMessage):
        """Deliver message to specific receiver"""
        key = f"{message.receiver}:{message.message_type.value}"

        if key in self.subscribers:
            # Call all subscribers for this agent + message type
            for callback in self.subscribers[key]:
                try:
                    await callback(message)
                except Exception as e:
                    self.logger.error(f"Error in callback for {key}: {e}")
        else:
            self.logger.warning(f"No subscriber for {key}")

    async def _broadcast_message(self, message: AgentMessage):
        """Broadcast message to all subscribers of this type"""
        # Find all subscribers for this message type
        matching_subscribers = [
            callback
            for key, callbacks in self.subscribers.items()
            if key.endswith(f":{message.message_type.value}")
            for callback in callbacks
        ]

        for callback in matching_subscribers:
            try:
                await callback(message)
            except Exception as e:
                self.logger.error(f"Error in broadcast callback: {e}")


# Global message bus instance
_message_bus: Optional[AgentMessageBus] = None


async def get_message_bus() -> AgentMessageBus:
    """Get or create global message bus"""
    global _message_bus
    if _message_bus is None:
        _message_bus = AgentMessageBus()
        await _message_bus.start()
    return _message_bus
