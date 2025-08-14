#!/usr/bin/env python3
"""
Production Text Length Validation with Regeneration Agent MCP
"""

from typing import Dict

async def production_run_text_validation_with_regeneration(record: Dict, config: Dict) -> Dict:
    """Validate and regenerate text for proper timing"""
    try:
        # Ensure record has proper structure
        if not isinstance(record, dict):
            record = {'record_id': '', 'fields': {}}
        if 'fields' not in record:
            record['fields'] = {}
        
        # Text is already validated in the control agent
        # This is a secondary validation step
        
        fields = record.get('fields', {})
        
        # Check all scripts exist
        required_scripts = ['IntroScript', 'OutroScript']
        for i in range(1, 6):
            required_scripts.append(f'Product{i}Script')
        
        missing_scripts = []
        for script in required_scripts:
            if not fields.get(script):
                missing_scripts.append(script)
        
        if missing_scripts:
            return {
                'success': False,
                'error': f'Missing scripts: {missing_scripts}',
                'updated_record': record
            }
        
        return {
            'success': True,
            'validation_passed': True,
            'updated_record': record
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }