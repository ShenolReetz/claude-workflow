#!/usr/bin/env python3
"""
Production Outro Image Generator
"""

from typing import Dict
import openai

async def production_generate_outro_image_for_workflow(record: Dict, config: Dict) -> Dict:
    """Generate outro image using OpenAI DALL-E"""
    try:
        openai.api_key = config.get('openai_api_key')
        
        prompt = "Create a professional outro image for a product review video. Text: 'Thanks for Watching!' Style: modern, clean, 9:16 aspect ratio, call-to-action feel."
        
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792",
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        record['fields']['OutroImageURL'] = image_url
        
        return {
            'success': True,
            'image_url': image_url,
            'updated_record': record
        }
        
    except Exception as e:
        print(f"❌ Error generating outro image: {e}")
        return {
            'success': False,
            'error': str(e),
            'updated_record': record
        }