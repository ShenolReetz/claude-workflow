"""
Video Production Agent
=======================
Main agent that orchestrates video rendering using Remotion.
"""

import asyncio
import logging
from typing import Dict, Any, List
import sys

sys.path.append('/home/claude-workflow')

from agents.base_agent import BaseAgent
from .standard_video_subagent import StandardVideoSubAgent
from .wow_video_subagent import WowVideoSubAgent
from .video_validator_subagent import VideoValidatorSubAgent


class VideoProductionAgent(BaseAgent):
    """
    Manages video production:
    - Standard video rendering (Remotion)
    - WOW video rendering (with effects)
    - Video validation
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("video_production", config)

        # Initialize sub-agents
        self.sub_agents = [
            StandardVideoSubAgent("standard_video", config, self.agent_id),
            WowVideoSubAgent("wow_video", config, self.agent_id),
            VideoValidatorSubAgent("video_validator", config, self.agent_id),
        ]

        # Video type preference
        self.default_video_type = config.get('default_video_type', 'standard')

        self.logger.info(f"✅ VideoProductionAgent initialized with {len(self.sub_agents)} sub-agents")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute video production task

        Args:
            task: Task parameters with 'phase' key

        Returns:
            Video production results
        """
        phase = task.get('phase', '')
        self.logger.info(f"🎬 Executing video production phase: {phase}")

        try:
            if phase == 'create_video':
                return await self._create_standard_video(task)

            elif phase == 'create_wow_video':
                return await self._create_wow_video(task)

            else:
                # Default to standard video
                return await self._create_standard_video(task)

        except Exception as e:
            self.logger.error(f"❌ Video production failed: {e}")
            raise

    async def _create_standard_video(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create standard video using Remotion"""
        self.logger.info("🎬 Creating standard video with Remotion...")

        result = await self.delegate_to_subagent('StandardVideoSubAgent', task)

        if not result['success']:
            raise RuntimeError(f"Failed to create video: {result.get('error')}")

        # Validate video
        validation_result = await self._validate_video(result['result']['video_path'])

        return {
            'video_path': result['result']['video_path'],
            'duration': result['result']['duration'],
            'video_type': 'standard',
            'validation': validation_result,
            'status': 'video_created'
        }

    async def _create_wow_video(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create WOW video with effects"""
        self.logger.info("🎬 Creating WOW video with effects...")

        result = await self.delegate_to_subagent('WowVideoSubAgent', task)

        if not result['success']:
            raise RuntimeError(f"Failed to create WOW video: {result.get('error')}")

        # Validate video
        validation_result = await self._validate_video(result['result']['video_path'])

        return {
            'video_path': result['result']['video_path'],
            'duration': result['result']['duration'],
            'video_type': 'wow',
            'validation': validation_result,
            'status': 'video_created'
        }

    async def _validate_video(self, video_path: str) -> Dict[str, Any]:
        """Validate rendered video"""
        validate_task = {'video_path': video_path}

        result = await self.delegate_to_subagent('VideoValidatorSubAgent', validate_task)

        if not result['success']:
            self.logger.warning(f"⚠️  Video validation failed: {result.get('error')}")

        return result.get('result', {})

    def get_capabilities(self) -> List[str]:
        """Return list of capabilities"""
        return [
            'create_video',
            'create_wow_video'
        ]
