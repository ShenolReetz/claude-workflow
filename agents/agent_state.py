"""
Agent State Management
======================
Manages workflow state with checkpointing and recovery capabilities.
"""

import asyncio
import json
import time
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class PhaseState:
    """State of a single workflow phase"""
    phase_name: str
    state: WorkflowState
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    retry_count: int = 0

    @property
    def duration(self) -> float:
        """Calculate phase duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            **asdict(self),
            'state': self.state.value,
            'duration': self.duration
        }


class WorkflowStateManager:
    """
    Manages workflow state across all agents
    Provides checkpointing and recovery
    """

    def __init__(self, workflow_id: str, storage_path: str = "/home/claude-workflow/.workflow_state"):
        self.workflow_id = workflow_id
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.state_file = self.storage_path / f"{workflow_id}.json"
        self.checkpoint_dir = self.storage_path / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)

        # State storage
        self.phases: Dict[str, PhaseState] = {}
        self.metadata: Dict[str, Any] = {
            'workflow_id': workflow_id,
            'created_at': time.time(),
            'updated_at': time.time()
        }

        # Recovery data
        self.checkpoints: List[Dict] = []
        self.max_checkpoints = 10

        self.logger = logging.getLogger(__name__)

        # Load existing state if available
        self._load_state()

    def start_phase(self, phase_name: str):
        """Mark phase as started"""
        self.phases[phase_name] = PhaseState(
            phase_name=phase_name,
            state=WorkflowState.RUNNING,
            start_time=time.time()
        )

        self.metadata['updated_at'] = time.time()
        self.logger.info(f"🔵 Phase started: {phase_name}")

        asyncio.create_task(self._persist_state())

    def complete_phase(self, phase_name: str, result: Optional[Dict[str, Any]] = None):
        """Mark phase as completed"""
        if phase_name in self.phases:
            self.phases[phase_name].state = WorkflowState.COMPLETED
            self.phases[phase_name].result = result
            self.phases[phase_name].end_time = time.time()

            self.metadata['updated_at'] = time.time()
            self.logger.info(f"✅ Phase completed: {phase_name} ({self.phases[phase_name].duration:.2f}s)")

            asyncio.create_task(self.checkpoint())

    def fail_phase(self, phase_name: str, error: str):
        """Mark phase as failed"""
        if phase_name in self.phases:
            self.phases[phase_name].state = WorkflowState.FAILED
            self.phases[phase_name].error = error
            self.phases[phase_name].end_time = time.time()

            self.metadata['updated_at'] = time.time()
            self.logger.error(f"❌ Phase failed: {phase_name} - {error}")

            asyncio.create_task(self._persist_state())

    def retry_phase(self, phase_name: str):
        """Increment retry count for phase"""
        if phase_name in self.phases:
            self.phases[phase_name].retry_count += 1
            self.phases[phase_name].state = WorkflowState.PENDING
            self.phases[phase_name].error = None

            self.logger.info(f"🔄 Phase retry #{self.phases[phase_name].retry_count}: {phase_name}")

    def get_phase_state(self, phase_name: str) -> Optional[PhaseState]:
        """Get state of specific phase"""
        return self.phases.get(phase_name)

    def get_all_phases(self) -> Dict[str, PhaseState]:
        """Get all phase states"""
        return self.phases

    def get_failed_phases(self) -> List[PhaseState]:
        """Get list of failed phases"""
        return [p for p in self.phases.values() if p.state == WorkflowState.FAILED]

    def get_completed_phases(self) -> List[PhaseState]:
        """Get list of completed phases"""
        return [p for p in self.phases.values() if p.state == WorkflowState.COMPLETED]

    def is_phase_completed(self, phase_name: str) -> bool:
        """Check if phase is completed"""
        phase = self.phases.get(phase_name)
        return phase is not None and phase.state == WorkflowState.COMPLETED

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of entire workflow"""
        total_phases = len(self.phases)
        completed = len(self.get_completed_phases())
        failed = len(self.get_failed_phases())
        running = len([p for p in self.phases.values() if p.state == WorkflowState.RUNNING])

        total_duration = sum(p.duration for p in self.phases.values())

        return {
            'workflow_id': self.workflow_id,
            'total_phases': total_phases,
            'completed': completed,
            'failed': failed,
            'running': running,
            'pending': total_phases - completed - failed - running,
            'total_duration': total_duration,
            'created_at': self.metadata['created_at'],
            'updated_at': self.metadata['updated_at']
        }

    async def checkpoint(self):
        """Create a checkpoint for recovery"""
        checkpoint = {
            'timestamp': time.time(),
            'phases': {name: phase.to_dict() for name, phase in self.phases.items()},
            'metadata': dict(self.metadata)
        }

        self.checkpoints.append(checkpoint)

        # Keep only last N checkpoints
        if len(self.checkpoints) > self.max_checkpoints:
            self.checkpoints = self.checkpoints[-self.max_checkpoints:]

        # Save checkpoint to disk
        checkpoint_file = self.checkpoint_dir / f"{self.workflow_id}_{int(time.time())}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        self.logger.debug(f"💾 Checkpoint saved: {checkpoint_file.name}")

        # Also persist current state
        await self._persist_state()

    async def restore_from_checkpoint(self, checkpoint_index: int = -1):
        """
        Restore workflow from checkpoint

        Args:
            checkpoint_index: Index of checkpoint to restore (-1 for latest)
        """
        if not self.checkpoints:
            self.logger.warning("No checkpoints available for restore")
            return False

        checkpoint = self.checkpoints[checkpoint_index]

        # Restore phase states
        self.phases = {}
        for phase_name, phase_data in checkpoint['phases'].items():
            self.phases[phase_name] = PhaseState(
                phase_name=phase_data['phase_name'],
                state=WorkflowState(phase_data['state']),
                result=phase_data.get('result'),
                error=phase_data.get('error'),
                start_time=phase_data.get('start_time'),
                end_time=phase_data.get('end_time'),
                retry_count=phase_data.get('retry_count', 0)
            )

        self.metadata = checkpoint['metadata']

        self.logger.info(f"🔄 Restored from checkpoint: {checkpoint['timestamp']}")
        return True

    async def _persist_state(self):
        """Save current state to disk"""
        state_data = {
            'workflow_id': self.workflow_id,
            'metadata': self.metadata,
            'phases': {name: phase.to_dict() for name, phase in self.phases.items()},
            'checkpoints_count': len(self.checkpoints)
        }

        with open(self.state_file, 'w') as f:
            json.dump(state_data, f, indent=2)

    def _load_state(self):
        """Load state from disk if exists"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state_data = json.load(f)

                self.metadata = state_data.get('metadata', self.metadata)

                # Restore phases
                for phase_name, phase_data in state_data.get('phases', {}).items():
                    self.phases[phase_name] = PhaseState(
                        phase_name=phase_data['phase_name'],
                        state=WorkflowState(phase_data['state']),
                        result=phase_data.get('result'),
                        error=phase_data.get('error'),
                        start_time=phase_data.get('start_time'),
                        end_time=phase_data.get('end_time'),
                        retry_count=phase_data.get('retry_count', 0)
                    )

                self.logger.info(f"📂 Loaded existing state for {self.workflow_id}")
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")

    def cleanup(self):
        """Clean up old state files and checkpoints"""
        # Remove old checkpoints (keep only max_checkpoints)
        checkpoint_files = sorted(self.checkpoint_dir.glob(f"{self.workflow_id}_*.json"))
        if len(checkpoint_files) > self.max_checkpoints:
            for old_file in checkpoint_files[:-self.max_checkpoints]:
                old_file.unlink()
                self.logger.debug(f"🗑️  Removed old checkpoint: {old_file.name}")
