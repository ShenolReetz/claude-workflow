"""
Category Extractor SubAgent
============================
Extracts product category and keywords from title.
"""

import sys
import asyncio
from typing import Dict, Any, List
import openai

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent


class CategoryExtractorSubAgent(BaseSubAgent):
    """
    Extracts product category using AI:
    - Identifies main category
    - Extracts relevant keywords
    - Suggests subcategories
    """

    CATEGORIES = [
        'Electronics',
        'Home & Kitchen',
        'Sports & Outdoors',
        'Health & Beauty',
        'Toys & Games',
        'Fashion',
        'Tools & Improvement'
    ]

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Initialize OpenAI client (using GPT-4o-mini for cost efficiency)
        openai.api_key = config.get('openai_api_key')
        self.model = config.get('category_model', 'gpt-4o-mini')

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Extract category from title

        Args:
            task: Task with 'title'

        Returns:
            Category, keywords, and subcategory
        """
        title = task.get('title')

        if not title:
            raise ValueError("No title provided for category extraction")

        self.logger.info(f"🏷️  Extracting category from: {title[:50]}...")

        try:
            # Build prompt
            prompt = self._build_extraction_prompt(title)

            # Call GPT-4o-mini
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product categorization expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )

            result_text = response.choices[0].message.content.strip()

            # Parse response
            category_data = self._parse_response(result_text)

            self.logger.info(f"✅ Category: {category_data['category']}")

            return category_data

        except Exception as e:
            self.logger.error(f"❌ Category extraction failed: {e}")
            # Fallback to simple keyword matching
            return self._fallback_extraction(title)

    def _build_extraction_prompt(self, title: str) -> str:
        """Build prompt for category extraction"""
        categories_str = ", ".join(self.CATEGORIES)

        return f"""Extract the product category and keywords from this Amazon product title:

Title: "{title}"

Available categories: {categories_str}

Respond in this EXACT format:
Category: [one of the available categories]
Keywords: [3-5 relevant keywords, comma-separated]
Subcategory: [more specific category if applicable]"""

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GPT response"""
        lines = response_text.strip().split('\n')

        result = {
            'category': 'Electronics',  # Default
            'keywords': [],
            'subcategory': ''
        }

        for line in lines:
            line = line.strip()
            if line.startswith('Category:'):
                category = line.replace('Category:', '').strip()
                # Validate against known categories
                for cat in self.CATEGORIES:
                    if cat.lower() in category.lower():
                        result['category'] = cat
                        break

            elif line.startswith('Keywords:'):
                keywords_str = line.replace('Keywords:', '').strip()
                result['keywords'] = [k.strip() for k in keywords_str.split(',') if k.strip()]

            elif line.startswith('Subcategory:'):
                result['subcategory'] = line.replace('Subcategory:', '').strip()

        return result

    def _fallback_extraction(self, title: str) -> Dict[str, Any]:
        """Fallback category extraction using keyword matching"""
        title_lower = title.lower()

        # Simple keyword-based categorization
        if any(word in title_lower for word in ['phone', 'laptop', 'camera', 'headphone', 'speaker', 'tv']):
            category = 'Electronics'
        elif any(word in title_lower for word in ['kitchen', 'home', 'furniture', 'decor']):
            category = 'Home & Kitchen'
        elif any(word in title_lower for word in ['sport', 'fitness', 'outdoor', 'camping']):
            category = 'Sports & Outdoors'
        elif any(word in title_lower for word in ['beauty', 'health', 'skincare', 'makeup']):
            category = 'Health & Beauty'
        elif any(word in title_lower for word in ['toy', 'game', 'kids', 'children']):
            category = 'Toys & Games'
        elif any(word in title_lower for word in ['clothing', 'shoes', 'fashion', 'apparel']):
            category = 'Fashion'
        elif any(word in title_lower for word in ['tool', 'drill', 'hammer', 'improvement']):
            category = 'Tools & Improvement'
        else:
            category = 'Electronics'  # Default

        # Extract simple keywords (first 3 words)
        words = title.split()[:3]
        keywords = [w for w in words if len(w) > 3]

        return {
            'category': category,
            'keywords': keywords,
            'subcategory': ''
        }

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        if 'title' not in task or not task['title']:
            return {'valid': False, 'error': 'Missing or empty title'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        if 'category' not in result:
            return {'valid': False, 'error': 'Missing category in result'}

        if result['category'] not in self.CATEGORIES:
            return {'valid': False, 'error': f'Invalid category: {result["category"]}'}

        return {'valid': True}
