#!/usr/bin/env python3
"""
Production Text Generation Control Agent MCP V2 - Text Validation and Regeneration
"""

import openai
from typing import Dict, List, Optional

async def production_run_text_control_with_regeneration(record: Dict, config: Dict) -> Dict:
    """Generate scripts if missing, then validate and regenerate to fit timing constraints"""
    try:
        openai.api_key = config.get('openai_api_key')
        
        # Ensure record has proper structure
        if not isinstance(record, dict):
            record = {'record_id': '', 'fields': {}}
        if 'fields' not in record:
            record['fields'] = {}
        
        # First, generate scripts if they don't exist
        await _generate_missing_scripts(record, config)
        
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
    """Regenerate text to fit word limit using GPT-4o"""
    try:
        prompt = f"""Shorten this {context} text to exactly {max_words} words while keeping the key message:
        
        Original: {text}
        
        Return only the shortened version."""
        
        client = openai.OpenAI(api_key=openai.api_key)
        
        # Use GPT-4o for text regeneration
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at concise writing with advanced understanding of context preservation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_completion_tokens=100
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

async def _generate_missing_scripts(record: Dict, config: Dict):
    """Generate scripts for intro, products, and outro if they don't exist using GPT-4o"""
    fields = record.get('fields', {})
    openai.api_key = config.get('openai_api_key')
    client = openai.OpenAI(api_key=config.get('openai_api_key'))
    
    # Use GPT-4o for content generation
    model = "gpt-4o"  # Production model
    
    # Generate intro script if missing
    if not fields.get('IntroScript'):
        video_title = fields.get('VideoTitle', 'Amazing Products')
        prompt = f"Write a 5-second intro script (max 12 words) for a video titled '{video_title}'. Be engaging and concise."
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=50
        )
        fields['IntroScript'] = response.choices[0].message.content.strip()
    
    # Generate product scripts if missing
    for i in range(1, 6):
        script_field = f'Product{i}Script'
        if not fields.get(script_field):
            product_title = fields.get(f'ProductNo{i}Title', f'Product {i}')
            product_desc = fields.get(f'ProductNo{i}Description', '')
            rating = fields.get(f'ProductNo{i}Rating', 0)
            price = fields.get(f'ProductNo{i}Price', 0)
            
            prompt = f"""Write a 9-second script (max 22 words) for product #{i}:
Title: {product_title}
Rating: {rating} stars
Price: ${price}
Description: {product_desc[:100]}

Make it compelling and highlight key features. Be concise."""
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=60
            )
            fields[script_field] = response.choices[0].message.content.strip()
    
    # Generate outro script if missing
    if not fields.get('OutroScript'):
        prompt = "Write a 5-second outro script (max 12 words) for a product review video. Include a call to action."
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=50
        )
        fields['OutroScript'] = response.choices[0].message.content.strip()
    
    record['fields'] = fields