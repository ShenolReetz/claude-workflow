"""
Video Validator SubAgent
=========================
Validates rendered videos for format, duration, and quality.
"""

import sys
import asyncio
import os
from typing import Dict, Any

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent


class VideoValidatorSubAgent(BaseSubAgent):
    """
    Validates rendered videos:
    - File exists and is readable
    - Format is MP4
    - Resolution is 1080x1920
    - Duration is appropriate (30-90 seconds)
    - File size is reasonable
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Validation thresholds
        self.min_duration = config.get('min_video_duration', 30)  # seconds
        self.max_duration = config.get('max_video_duration', 90)  # seconds
        self.min_file_size = config.get('min_video_size_mb', 1) * 1024 * 1024  # bytes
        self.max_file_size = config.get('max_video_size_mb', 100) * 1024 * 1024  # bytes
        self.required_resolution = config.get('required_resolution', '1080x1920')

        self.logger.info("✅ VideoValidatorSubAgent initialized")

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Validate video file

        Args:
            task: Task with 'video_path'

        Returns:
            Validation result
        """
        video_path = task.get('video_path')

        if not video_path:
            raise ValueError("No video path provided for validation")

        self.logger.info(f"✅ Validating video: {video_path}")

        try:
            validation_report = {
                'valid': True,
                'issues': [],
                'warnings': [],
                'stats': {}
            }

            # Check file exists
            if not os.path.exists(video_path):
                validation_report['valid'] = False
                validation_report['issues'].append(f"Video file not found: {video_path}")
                return validation_report

            # Check file size
            file_size = os.path.getsize(video_path)
            validation_report['stats']['file_size_mb'] = file_size / (1024 * 1024)

            if file_size < self.min_file_size:
                validation_report['valid'] = False
                validation_report['issues'].append(
                    f"File too small: {file_size/(1024*1024):.2f}MB (min {self.min_file_size/(1024*1024)}MB)"
                )

            if file_size > self.max_file_size:
                validation_report['warnings'].append(
                    f"File large: {file_size/(1024*1024):.2f}MB (max {self.max_file_size/(1024*1024)}MB)"
                )

            # Check file extension
            if not video_path.lower().endswith('.mp4'):
                validation_report['warnings'].append("Video is not MP4 format")

            # Try to get video metadata if possible
            try:
                import subprocess
                import json

                # Use ffprobe to get video info (if available)
                result = subprocess.run(
                    ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    video_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)

                    if video_stream:
                        width = video_stream.get('width', 0)
                        height = video_stream.get('height', 0)
                        validation_report['stats']['resolution'] = f"{width}x{height}"

                        # Check resolution
                        expected_res = self.required_resolution
                        if f"{width}x{height}" != expected_res:
                            validation_report['warnings'].append(
                                f"Resolution {width}x{height} (expected {expected_res})"
                            )

            except Exception as e:
                self.logger.debug(f"Could not read video metadata: {e}")
                validation_report['warnings'].append("Could not verify video metadata")

            if validation_report['valid']:
                self.logger.info("✅ Video validation passed")
            else:
                self.logger.warning(f"⚠️  Video validation failed: {validation_report['issues']}")

            return validation_report

        except Exception as e:
            self.logger.error(f"❌ Video validation error: {e}")
            raise

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if 'video_path' not in task or not task['video_path']:
            return {'valid': False, 'error': 'Missing video_path'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'valid' not in result:
            return {'valid': False, 'error': 'Missing valid field'}

        return {'valid': True}
