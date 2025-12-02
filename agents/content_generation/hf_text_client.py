"""
Hugging Face Text Generation Client
====================================
Generates content using Qwen2.5-72B-Instruct via HF Inference API.
"""

import aiohttp
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class HuggingFaceTextClient:
    """
    Client for HF Qwen2.5-72B text generation
    Replaces GPT-4o to save costs
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_token = config.get('hf_api_token')
        self.model_id = config.get('hf_text_model', 'meta-llama/Llama-3.1-8B-Instruct')

        # Use Inference API endpoint
        self.base_url = f"https://api-inference.huggingface.co/models/{self.model_id}"

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"📝 HF Text Client initialized: {self.model_id}")

    async def generate_text(self, prompt: str, max_tokens: int = 300,
                           temperature: float = 0.7, top_p: float = 0.9) -> Dict[str, Any]:
        """
        Generate text from prompt

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter

        Returns:
            {'success': bool, 'text': str}
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "return_full_text": False
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload,
                                       timeout=aiohttp.ClientTimeout(total=60)) as response:

                    if response.status == 200:
                        result = await response.json()
                        generated_text = result[0]['generated_text']

                        self.logger.info(f"✅ Text generated: {len(generated_text)} chars")

                        return {
                            'success': True,
                            'text': generated_text,
                            'length': len(generated_text)
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(f"❌ Text generation failed: {response.status} - {error_text}")

                        return {
                            'success': False,
                            'error': error_text,
                            'status': response.status
                        }

        except Exception as e:
            self.logger.error(f"❌ Text generation exception: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def generate_script(self, product_data: Dict[str, Any],
                             section: str = 'intro') -> Dict[str, Any]:
        """
        Generate voice script for product section

        Args:
            product_data: Product information
            section: 'intro', 'product1'-'product5', or 'outro'

        Returns:
            {'success': bool, 'script': str}
        """
        # Build prompt based on section
        if section == 'intro':
            prompt = f"""Generate an engaging 10-second intro script for a product review video about:
{product_data.get('Title', '')}

Make it exciting and attention-grabbing. Keep it under 40 words."""

        elif section.startswith('product'):
            product_num = int(section.replace('product', ''))
            product = product_data.get(f'Product{product_num}', {})

            prompt = f"""Generate a 7-second product highlight script for:
Product: {product.get('title', '')}
Price: {product.get('price', '')}
Features: {product.get('description', '')}

Make it concise and compelling. Focus on value. Keep it under 30 words."""

        elif section == 'outro':
            prompt = f"""Generate a 5-second outro script for a product review video.
Include a call to action to check the link in the description.
Keep it under 20 words."""

        else:
            return {'success': False, 'error': f'Unknown section: {section}'}

        # Generate
        result = await self.generate_text(prompt, max_tokens=100, temperature=0.7)

        if result['success']:
            return {
                'success': True,
                'script': result['text'].strip(),
                'section': section
            }
        else:
            return result

    async def generate_platform_content(self, title: str, products: List[Dict],
                                       platform: str = 'youtube') -> Dict[str, Any]:
        """
        Generate platform-specific content

        Args:
            title: Video title
            products: List of product dictionaries
            platform: 'youtube', 'wordpress', or 'instagram'

        Returns:
            {'success': bool, 'content': dict}
        """
        if platform == 'youtube':
            prompt = f"""Generate YouTube video metadata for:
Title: {title}

Create:
1. SEO-optimized description (200 words)
2. 10 relevant tags
3. Engaging call-to-action

Products featured: {len(products)} items"""

        elif platform == 'wordpress':
            prompt = f"""Generate WordPress blog post content for:
Title: {title}

Create:
1. Introduction (50 words)
2. Product comparison section
3. Conclusion with CTA (30 words)

Make it SEO-friendly and engaging."""

        elif platform == 'instagram':
            prompt = f"""Generate Instagram Reels caption for:
{title}

Include:
1. Hook line
2. Brief product mention
3. 30 relevant hashtags
4. CTA

Keep caption under 150 words."""

        else:
            return {'success': False, 'error': f'Unknown platform: {platform}'}

        result = await self.generate_text(prompt, max_tokens=500, temperature=0.7)

        if result['success']:
            return {
                'success': True,
                'content': self._parse_platform_content(result['text'], platform),
                'platform': platform
            }
        else:
            return result

    def _parse_platform_content(self, text: str, platform: str) -> Dict[str, Any]:
        """Parse generated content into structured format"""
        # Simple parsing (can be improved with better prompts)
        lines = [l.strip() for l in text.split('\n') if l.strip()]

        if platform == 'youtube':
            return {
                'description': '\n'.join(lines[:10]) if len(lines) > 10 else text,
                'tags': self._extract_tags(text),
                'raw': text
            }
        elif platform == 'wordpress':
            return {
                'content': text,
                'raw': text
            }
        elif platform == 'instagram':
            return {
                'caption': '\n'.join(lines[:5]) if len(lines) > 5 else text,
                'hashtags': self._extract_hashtags(text),
                'raw': text
            }

        return {'raw': text}

    def _extract_tags(self, text: str) -> List[str]:
        """Extract YouTube tags from text"""
        # Look for lines with tags or keywords
        tags = []
        for line in text.split('\n'):
            if 'tag' in line.lower() or '#' in line:
                # Extract words
                words = line.replace('#', '').split(',')
                tags.extend([w.strip() for w in words if w.strip()])

        return tags[:15]  # Limit to 15 tags

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags[:30]  # Limit to 30 hashtags


# Alias for backward compatibility
HFTextClient = HuggingFaceTextClient
