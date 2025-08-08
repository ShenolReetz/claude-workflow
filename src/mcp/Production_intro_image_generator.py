#!/usr/bin/env python3
"""
Production Intro Image Generator
"""

from typing import Dict
import openai

async def production_generate_intro_image_for_workflow(record: Dict, config: Dict) -> Dict:
    """Generate intro image using OpenAI DALL-E"""
    try:
        openai.api_key = config.get('openai_api_key')
        
        # Ensure record has proper structure
        if not isinstance(record, dict):
            record = {'record_id': '', 'fields': {}}
        if 'fields' not in record:
            record['fields'] = {}
        
        title = record.get('fields', {}).get('VideoTitle', 'Top Products')
        
        prompt = f"Create a professional intro image for a video titled '{title}'. Style: modern, clean, 9:16 aspect ratio, vibrant colors."
        
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        record['fields']['IntroImageURL'] = image_url
        
        return {
            'success': True,
            'image_url': image_url,
            'updated_record': record
        }
        
    except Exception as e:
        print(f"❌ Error generating intro image: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }