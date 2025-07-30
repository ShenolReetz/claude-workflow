#!/usr/bin/env python3
"""
JSON2Video Template Validator
Comprehensive validation script to prevent JSON2Video API schema errors
"""

import json
import logging
import sys
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSON2VideoTemplateValidator:
    """Validates JSON2Video templates against known API requirements"""
    
    # Properties that are invalid for subtitle elements
    INVALID_SUBTITLE_PROPERTIES = [
        'vertical-align',
        'vertical_align', 
        'text-align',
        'align',
        'valign',
        'v-align'
    ]
    
    # Properties that are invalid for specific element types
    INVALID_PROPERTIES_BY_TYPE = {
        'subtitles': INVALID_SUBTITLE_PROPERTIES,
        'text': ['vertical-align'],  # text elements may have different restrictions
    }
    
    # Required properties for different element types
    REQUIRED_PROPERTIES = {
        'subtitles': ['type', 'language'],
        'text': ['type', 'text'],
        'image': ['type', 'src'],
        'audio': ['type', 'src'],
        'component': ['type', 'component']
    }
    
    # Valid positioning methods (cannot mix them)
    POSITIONING_METHODS = ['position', 'x', 'y', 'offset-x', 'offset-y']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
    
    def validate_template(self, template: Dict[str, Any], fix_errors: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate a JSON2Video template
        
        Args:
            template: Template dictionary to validate
            fix_errors: Whether to automatically fix errors when possible
            
        Returns:
            Tuple of (is_valid, fixed_template)
        """
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
        
        # Deep copy for fixing
        fixed_template = json.loads(json.dumps(template))
        
        # Validate overall structure
        self._validate_structure(fixed_template)
        
        # Validate scenes
        if 'scenes' in fixed_template:
            for scene_idx, scene in enumerate(fixed_template['scenes']):
                self._validate_scene(scene, scene_idx, fixed_template, fix_errors)
        
        # Apply fixes if requested
        if fix_errors and self.errors:
            logger.info(f"🔧 Attempting to fix {len(self.errors)} validation errors...")
        
        is_valid = len(self.errors) == 0
        
        return is_valid, fixed_template
    
    def _validate_structure(self, template: Dict[str, Any]):
        """Validate overall template structure"""
        required_fields = ['scenes']
        
        for field in required_fields:
            if field not in template:
                self.errors.append(f"Missing required field: '{field}'")
        
        # Check for valid resolution
        if 'resolution' in template:
            valid_resolutions = ['instagram-story', 'youtube-shorts', 'tiktok', 'square', 'landscape']
            if template['resolution'] not in valid_resolutions:
                self.warnings.append(f"Unusual resolution: '{template['resolution']}'. Valid options: {valid_resolutions}")
    
    def _validate_scene(self, scene: Dict[str, Any], scene_idx: int, template: Dict[str, Any], fix_errors: bool):
        """Validate a single scene"""
        scene_prefix = f"scenes[{scene_idx}]"
        
        # Required scene properties
        if 'elements' not in scene:
            self.errors.append(f"{scene_prefix}: Missing 'elements' array")
            return
        
        # Validate each element
        for elem_idx, element in enumerate(scene['elements']):
            self._validate_element(element, f"{scene_prefix}.elements[{elem_idx}]", template, fix_errors)
    
    def _validate_element(self, element: Dict[str, Any], element_prefix: str, template: Dict[str, Any], fix_errors: bool):
        """Validate a single element"""
        
        # Check element type
        if 'type' not in element:
            self.errors.append(f"{element_prefix}: Missing 'type' property")
            return
        
        element_type = element['type']
        
        # Check required properties for this element type  
        if element_type in self.REQUIRED_PROPERTIES:
            for required_prop in self.REQUIRED_PROPERTIES[element_type]:
                if required_prop not in element:
                    self.errors.append(f"{element_prefix}: Missing required property '{required_prop}' for type '{element_type}'")
        
        # Check for invalid properties
        if element_type in self.INVALID_PROPERTIES_BY_TYPE:
            invalid_props = self.INVALID_PROPERTIES_BY_TYPE[element_type]
            
            if 'settings' in element:
                for invalid_prop in invalid_props:
                    if invalid_prop in element['settings']:
                        error_msg = f"{element_prefix}: Invalid property '{invalid_prop}' in settings for type '{element_type}'"
                        
                        if fix_errors:
                            # Remove the invalid property
                            del element['settings'][invalid_prop]
                            self.fixes_applied.append(f"Removed '{invalid_prop}' from {element_prefix}.settings")
                            logger.info(f"🧹 Fixed: {error_msg}")
                            
                            # Add proper positioning if needed
                            if invalid_prop == 'vertical-align' and element_type == 'subtitles':
                                if 'offset-y' not in element['settings']:
                                    element['settings']['offset-y'] = 900
                                    self.fixes_applied.append(f"Added 'offset-y': 900 to {element_prefix}.settings")
                                    logger.info(f"✅ Added offset-y positioning to {element_prefix}")
                        else:
                            self.errors.append(error_msg)
        
        # Check positioning conflicts
        self._validate_positioning(element, element_prefix)
        
        # Type-specific validations
        if element_type == 'subtitles':
            self._validate_subtitle_element(element, element_prefix)
        elif element_type == 'audio':
            self._validate_audio_element(element, element_prefix)
    
    def _validate_positioning(self, element: Dict[str, Any], element_prefix: str):
        """Validate element positioning"""
        positioning_props = []
        
        # Check for positioning properties
        for prop in self.POSITIONING_METHODS:
            if prop in element:
                positioning_props.append(prop)
        
        # Check settings for positioning
        if 'settings' in element:
            for prop in ['offset-x', 'offset-y']:
                if prop in element['settings']:
                    positioning_props.append(f"settings.{prop}")
        
        # Warn about mixed positioning methods
        if len(positioning_props) > 2:  # x, y are OK together
            self.warnings.append(f"{element_prefix}: Multiple positioning methods detected: {positioning_props}")
    
    def _validate_subtitle_element(self, element: Dict[str, Any], element_prefix: str):
        """Validate subtitle-specific properties"""
        
        # Check language
        if 'language' not in element:
            self.warnings.append(f"{element_prefix}: Subtitle element missing 'language' property")
        
        # Check settings
        if 'settings' in element:
            style = element['settings']
            
            # Check for conflicting positioning
            if 'offset-y' in style and 'vertical-align' in style:
                self.warnings.append(
                    f"{element_prefix}: Both 'offset-y' and 'vertical-align' specified. "
                    f"'vertical-align' is not supported and will be ignored."
                )
    
    def _validate_audio_element(self, element: Dict[str, Any], element_prefix: str):
        """Validate audio-specific properties"""
        
        # Check src
        if 'src' not in element:
            self.errors.append(f"{element_prefix}: Audio element missing 'src' property")
        elif not element['src'] or element['src'].strip() == '':
            # This is the specific error that caused the JSON2Video API failure
            self.errors.append(f"{element_prefix}: Audio element has empty 'src' URL")
    
    def generate_report(self) -> str:
        """Generate a validation report"""
        report = ["JSON2Video Template Validation Report", "=" * 50, ""]
        
        if self.errors:
            report.extend(["❌ ERRORS:", ""])
            for error in self.errors:
                report.append(f"  - {error}")
            report.append("")
        
        if self.warnings:
            report.extend(["⚠️  WARNINGS:", ""])
            for warning in self.warnings:
                report.append(f"  - {warning}")
            report.append("")
        
        if self.fixes_applied:
            report.extend(["🔧 FIXES APPLIED:", ""])
            for fix in self.fixes_applied:
                report.append(f"  - {fix}")
            report.append("")
        
        if not self.errors and not self.warnings:
            report.append("✅ Template validation passed - no issues found!")
        
        return "\n".join(report)

def validate_template_file(file_path: str, fix_errors: bool = True, save_fixed: bool = True) -> bool:
    """
    Validate a JSON2Video template file
    
    Args:
        file_path: Path to the template file
        fix_errors: Whether to automatically fix errors
        save_fixed: Whether to save the fixed template
        
    Returns:
        True if validation passed (after fixes if applicable)
    """
    validator = JSON2VideoTemplateValidator()
    
    try:
        # Load template
        with open(file_path, 'r') as f:
            template = json.load(f)
        
        logger.info(f"🔍 Validating template: {file_path}")
        
        # Validate
        is_valid, fixed_template = validator.validate_template(template, fix_errors)
        
        # Generate report
        report = validator.generate_report()
        print(report)
        
        # Save fixed template if requested and fixes were applied
        if fix_errors and validator.fixes_applied and save_fixed:
            backup_path = f"{file_path}.backup"
            fixed_path = file_path
            
            # Create backup
            with open(backup_path, 'w') as f:
                json.dump(template, f, indent=2)
            logger.info(f"📋 Backup saved to: {backup_path}")
            
            # Save fixed version
            with open(fixed_path, 'w') as f:
                json.dump(fixed_template, f, indent=2)
            logger.info(f"🔧 Fixed template saved to: {fixed_path}")
        
        return is_valid or (fix_errors and len(validator.errors) == 0)
        
    except Exception as e:
        logger.error(f"❌ Error validating template {file_path}: {e}")
        return False

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python json2video_template_validator.py <template_file> [--no-fix] [--no-save]")
        print("\nOptions:")
        print("  --no-fix    Don't automatically fix errors")
        print("  --no-save   Don't save the fixed template")
        sys.exit(1)
    
    file_path = sys.argv[1]
    fix_errors = '--no-fix' not in sys.argv
    save_fixed = '--no-save' not in sys.argv
    
    if not Path(file_path).exists():
        logger.error(f"❌ Template file not found: {file_path}")
        sys.exit(1)
    
    success = validate_template_file(file_path, fix_errors, save_fixed)
    
    if success:
        logger.info("✅ Template validation completed successfully")
        sys.exit(0)
    else:
        logger.error("❌ Template validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()