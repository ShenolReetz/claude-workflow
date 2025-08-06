#!/usr/bin/env python3
"""
Production Text Generation Control Agent MCP V2 - Text Validation and Regeneration
"""

import openai
from typing import Dict, List, Optional

async def production_run_text_control_with_regeneration(record: Dict, config: Dict) -> Dict:
    """Validate and regenerate text to fit timing constraints"""
    try:
        openai.api_key = config.get('openai_api_key')
        
        all_valid = True
        regeneration_count = 0
        max_attempts = 3
        
        for attempt in range(max_attempts):
            # Validate intro (5 seconds max)
            intro_script = record.get('fields', {}).get('IntroScript', '')
            if len(intro_script.split()) > 12:  # ~2.5 words/sec * 5 sec
                intro_script = await _regenerate_text(intro_script, 12, 'intro')
                record['fields']['IntroScript'] = intro_script
                regeneration_count += 1
            
            # Validate outro (5 seconds max)
            outro_script = record.get('fields', {}).get('OutroScript', '')
            if len(outro_script.split()) > 12:
                outro_script = await _regenerate_text(outro_script, 12, 'outro')
                record['fields']['OutroScript'] = outro_script
                regeneration_count += 1
            
            # Validate product scripts (9 seconds each)
            for i in range(1, 6):
                script_field = f'Product{i}Script'
                product_script = record.get('fields', {}).get(script_field, '')
                if len(product_script.split()) > 22:  # ~2.5 words/sec * 9 sec
                    product_script = await _regenerate_text(product_script, 22, f'product {i}')
                    record['fields'][script_field] = product_script
                    regeneration_count += 1
            
            # Check if all valid now
            all_valid = _validate_all_scripts(record)
            if all_valid:
                break
        
        return {
            'success': True,
            'all_valid': all_valid,
            'attempts': attempt + 1,
            'regenerations': regeneration_count,
            'updated_record': record
        }
        
    except Exception as e:
        print(f"❌ Error in text control: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }

async def _regenerate_text(text: str, max_words: int, context: str) -> str:
    """Regenerate text to fit word limit"""
    try:
        prompt = f"""Shorten this {context} text to exactly {max_words} words while keeping the key message:
        
        Original: {text}
        
        Return only the shortened version."""
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert at concise writing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    except:
        # Fallback: truncate
        words = text.split()[:max_words]
        return ' '.join(words)

def _validate_all_scripts(record: Dict) -> bool:
    """Check if all scripts meet timing requirements"""
    fields = record.get('fields', {})
    
    # Check intro/outro (5 sec = 12 words max)
    if len(fields.get('IntroScript', '').split()) > 12:
        return False
    if len(fields.get('OutroScript', '').split()) > 12:
        return False
    
    # Check products (9 sec = 22 words max)
    for i in range(1, 6):
        script = fields.get(f'Product{i}Script', '')
        if script and len(script.split()) > 22:
            return False
    
    return True