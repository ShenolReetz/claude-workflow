"""
Content Validator SubAgent
===========================
Validates all generated content for quality and completeness.
"""

import sys
import asyncio
import os
from typing import Dict, Any, List
from pathlib import Path

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent


class ContentValidatorSubAgent(BaseSubAgent):
    """
    Validates generated content:
    - Images exist and have proper size
    - Scripts have proper length
    - Voice files exist and are valid
    - All required content present
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Validation thresholds
        self.min_image_size = config.get('min_image_size_bytes', 10000)  # 10KB
        self.min_script_length = config.get('min_script_length_chars', 20)
        self.max_script_length = config.get('max_script_length_chars', 500)
        self.min_voice_size = config.get('min_voice_size_bytes', 5000)  # 5KB

        self.logger.info("✅ ContentValidatorSubAgent initialized")

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Validate all content

        Args:
            task: Task with 'content_data' containing images, scripts, voices

        Returns:
            Validation result with pass/fail and report
        """
        content_data = task.get('content_data', {})

        if not content_data:
            raise ValueError("No content data provided for validation")

        self.logger.info("✅ Validating generated content...")

        try:
            validation_report = {
                'passed': True,
                'issues': [],
                'warnings': [],
                'stats': {
                    'images_valid': 0,
                    'scripts_valid': 0,
                    'voices_valid': 0
                }
            }

            # Validate images
            images = content_data.get('images', [])
            image_issues = await self._validate_images(images)
            if image_issues:
                validation_report['issues'].extend(image_issues)
                validation_report['passed'] = False
            else:
                validation_report['stats']['images_valid'] = len([i for i in images if i])

            # Validate scripts
            scripts = content_data.get('scripts', {})
            script_issues = await self._validate_scripts(scripts)
            if script_issues:
                validation_report['issues'].extend(script_issues)
                validation_report['passed'] = False
            else:
                validation_report['stats']['scripts_valid'] = len([v for v in scripts.values() if v])

            # Validate voices
            voices = content_data.get('voices', [])
            voice_issues = await self._validate_voices(voices)
            if voice_issues:
                validation_report['issues'].extend(voice_issues)
                validation_report['passed'] = False
            else:
                validation_report['stats']['voices_valid'] = len([v for v in voices if v])

            if validation_report['passed']:
                self.logger.info("✅ All content validated successfully")
            else:
                self.logger.warning(f"⚠️  Validation found {len(validation_report['issues'])} issues")

            return {
                'passed': validation_report['passed'],
                'report': validation_report
            }

        except Exception as e:
            self.logger.error(f"❌ Content validation failed: {e}")
            raise

    async def _validate_images(self, images: List) -> List[str]:
        """Validate image files"""
        issues = []

        if not images or len(images) == 0:
            issues.append("No images provided")
            return issues

        for i, image_data in enumerate(images, 1):
            # Extract path from dict or use string directly
            if isinstance(image_data, dict):
                image_path = image_data.get('local_path') or image_data.get('image_path') or image_data.get('path')
            elif isinstance(image_data, str):
                image_path = image_data
            else:
                issues.append(f"Image {i}: Invalid data type (expected str or dict)")
                continue

            if not image_path:
                issues.append(f"Image {i}: Missing path")
                continue

            # Check if file exists
            if not os.path.exists(image_path):
                issues.append(f"Image {i}: File not found at {image_path}")
                continue

            # Check file size
            file_size = os.path.getsize(image_path)
            if file_size < self.min_image_size:
                issues.append(f"Image {i}: File too small ({file_size} bytes, min {self.min_image_size})")

            # Check file extension
            if not any(image_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp']):
                issues.append(f"Image {i}: Invalid file extension")

        return issues

    async def _validate_scripts(self, scripts: Dict[str, str]) -> List[str]:
        """Validate script text"""
        issues = []

        required_scripts = ['intro_script', 'outro_script']

        for script_name in required_scripts:
            if script_name not in scripts:
                issues.append(f"Script: Missing {script_name}")
                continue

            script_text = scripts[script_name]

            if not script_text or not script_text.strip():
                issues.append(f"Script {script_name}: Empty or whitespace only")
                continue

            # Check length
            length = len(script_text)
            if length < self.min_script_length:
                issues.append(f"Script {script_name}: Too short ({length} chars, min {self.min_script_length})")

            if length > self.max_script_length:
                issues.append(f"Script {script_name}: Too long ({length} chars, max {self.max_script_length})")

        return issues

    async def _validate_voices(self, voices) -> List[str]:
        """Validate voice files"""
        issues = []

        if not voices or len(voices) == 0:
            issues.append("No voice files provided")
            return issues

        # voices might be a dict, convert to list
        if isinstance(voices, dict):
            voices = list(voices.values())

        for i, voice_data in enumerate(voices, 1):
            # Extract path from dict or use string directly
            if isinstance(voice_data, dict):
                voice_path = voice_data.get('local_path') or voice_data.get('voice_path') or voice_data.get('path')
            elif isinstance(voice_data, str):
                voice_path = voice_data
            else:
                issues.append(f"Voice {i}: Invalid data type (expected str or dict)")
                continue

            if not voice_path:
                issues.append(f"Voice {i}: Missing path")
                continue

            # Check if file exists
            if not os.path.exists(voice_path):
                issues.append(f"Voice {i}: File not found at {voice_path}")
                continue

            # Check file size
            file_size = os.path.getsize(voice_path)
            if file_size < self.min_voice_size:
                issues.append(f"Voice {i}: File too small ({file_size} bytes, min {self.min_voice_size})")

            # Check file extension
            if not any(voice_path.lower().endswith(ext) for ext in ['.mp3', '.wav', '.m4a']):
                issues.append(f"Voice {i}: Invalid audio file extension")

        return issues

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if 'content_data' not in task:
            return {'valid': False, 'error': 'Missing content_data'}

        content_data = task['content_data']
        if not isinstance(content_data, dict):
            return {'valid': False, 'error': 'content_data must be a dictionary'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'passed' not in result:
            return {'valid': False, 'error': 'Missing passed field'}

        if 'report' not in result:
            return {'valid': False, 'error': 'Missing report field'}

        return {'valid': True}
