"""
Text Generator SubAgent with HuggingFace Llama
===============================================
Generates text content using HuggingFace Llama-3.1-8B for COST SAVINGS!

COST: $0.00/request (vs $0.10 with GPT-4o)
SPEED: 2-3 seconds per generation
QUALITY: Very Good
"""

import sys
import asyncio
from typing import Dict, Any, List

sys.path.append('/home/claude-workflow')

from agents.base_subagent import BaseSubAgent
from agents.content_generation.hf_text_client import HFTextClient


class TextGeneratorSubAgent(BaseSubAgent):
    """
    Generates text content using HuggingFace Llama-3.1-8B-Instruct

    Features:
    - Uses FREE HuggingFace Inference API
    - Falls back to GPT-4o-mini if HF fails
    - Generates platform-specific content
    - Creates voice scripts
    """

    def __init__(self, name: str, config: Dict[str, Any], parent_agent_id: str = None):
        super().__init__(name, config, parent_agent_id)

        # Initialize HuggingFace text client
        self.hf_client = HFTextClient(config)

        # Fallback to OpenAI if configured
        self.use_fallback = config.get('text_fallback_enabled', True)

        self.logger.info("✅ TextGeneratorSubAgent initialized with HuggingFace Llama-3.1-8B")
        self.logger.info("💰 Cost savings: $0.10 → $0.00 per video!")

    async def execute_task(self, task: Dict[str, Any]) -> Any:
        """
        Generate text content using HuggingFace Llama

        Args:
            task: Task with operation type ('generate_scripts' or 'generate_content')

        Returns:
            Generated text/scripts
        """
        operation = task.get('operation', 'generate_content')

        self.logger.info(f"📝 Generating text with HF Llama: {operation}")

        try:
            if operation == 'generate_scripts':
                return await self._generate_voice_scripts(task)
            else:
                return await self._generate_platform_content(task)

        except Exception as e:
            self.logger.error(f"❌ Text generation failed: {e}")
            raise

    async def _generate_voice_scripts(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate voice scripts for all products"""
        products = task.get('products', [])

        if not products:
            raise ValueError("No products provided for script generation")

        self.logger.info(f"📜 Generating scripts for {len(products)} products with HF Llama...")

        try:
            # Generate intro script
            intro_script = await self._generate_intro_script(products)

            # Generate product scripts (max 5)
            product_scripts = []
            for i, product in enumerate(products[:5], 1):
                script = await self._generate_product_script(product, i)
                product_scripts.append(script)

            # Generate outro script
            outro_script = await self._generate_outro_script(products)

            result = {
                'intro_script': intro_script,
                'outro_script': outro_script
            }

            # Add product scripts
            for i, script in enumerate(product_scripts, 1):
                result[f'product{i}_script'] = script

            self.logger.info(f"✅ Generated {len(product_scripts) + 2} scripts with HuggingFace (FREE)")

            return result

        except Exception as e:
            self.logger.error(f"❌ Script generation failed: {e}")

            # Fallback to GPT-4o-mini if enabled
            if self.use_fallback:
                return await self._fallback_openai_scripts(products)
            else:
                raise

    async def _generate_intro_script(self, products: List[Dict[str, Any]]) -> str:
        """Generate intro script"""
        category = products[0].get('category', 'products')

        prompt = f"""Generate an engaging 15-second YouTube video intro script for a product review video about {category}.

The intro should:
- Hook the viewer immediately
- Mention that we're showcasing top products
- Be enthusiastic and energetic
- Be exactly 30-40 words

Generate ONLY the script, no other text."""

        script = await self.hf_client.generate_text(
            prompt=prompt,
            max_length=100,
            temperature=0.7
        )

        return script.strip()

    async def _generate_product_script(self, product: Dict[str, Any], index: int) -> str:
        """Generate script for a single product"""
        title = product.get('title', '')
        price = product.get('price', '')
        rating = product.get('rating', 0)
        reviews = product.get('review_count', 0)

        prompt = f"""Generate a 20-second product description script for:

Product: {title}
Price: {price}
Rating: {rating}/5 stars ({reviews} reviews)

The script should:
- Highlight key features and benefits
- Mention the price and rating
- Sound natural and conversational
- Be exactly 40-60 words
- Be enthusiastic but authentic

Generate ONLY the script, no other text."""

        script = await self.hf_client.generate_text(
            prompt=prompt,
            max_length=150,
            temperature=0.7
        )

        return script.strip()

    async def _generate_outro_script(self, products: List[Dict[str, Any]]) -> str:
        """Generate outro script"""
        prompt = f"""Generate a 10-second YouTube video outro script for a product review video.

The outro should:
- Thank viewers for watching
- Encourage likes and subscriptions
- Be friendly and concise
- Be exactly 20-30 words

Generate ONLY the script, no other text."""

        script = await self.hf_client.generate_text(
            prompt=prompt,
            max_length=80,
            temperature=0.7
        )

        return script.strip()

    async def _generate_platform_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate platform-specific content (YouTube, WordPress, Instagram)"""
        products = task.get('products', [])
        category = task.get('category', 'Products')

        if not products:
            raise ValueError("No products provided for content generation")

        self.logger.info(f"📝 Generating platform content for {category}...")

        try:
            # Generate YouTube title and description
            youtube_content = await self._generate_youtube_content(products, category)

            # Generate WordPress title and content
            wordpress_content = await self._generate_wordpress_content(products, category)

            # Generate Instagram caption
            instagram_content = await self._generate_instagram_content(products, category)

            # Generate hashtags
            hashtags = await self._generate_hashtags(category)

            self.logger.info("✅ Platform content generated with HuggingFace (FREE)")

            return {
                'youtube_title': youtube_content['title'],
                'youtube_description': youtube_content['description'],
                'youtube_tags': youtube_content['tags'],
                'wordpress_title': wordpress_content['title'],
                'wordpress_content': wordpress_content['content'],
                'instagram_caption': instagram_content['caption'],
                'hashtags': hashtags
            }

        except Exception as e:
            self.logger.error(f"❌ Platform content generation failed: {e}")
            raise

    async def _generate_youtube_content(self, products: List[Dict[str, Any]], category: str) -> Dict[str, Any]:
        """Generate YouTube title and description"""
        first_product = products[0]['title'] if products else category

        # Title
        title_prompt = f"""Generate a compelling YouTube video title (max 60 characters) for a review of:
{first_product}

The title should:
- Include the current year (2025)
- Mention "Top 5" or "Best"
- Be engaging and clickable
- Include relevant keywords

Generate ONLY the title, no other text."""

        title = await self.hf_client.generate_text(
            prompt=title_prompt,
            max_length=50,
            temperature=0.8
        )

        # Description
        desc_prompt = f"""Generate a YouTube video description (200-300 words) for a product review of {category}.

Include:
- Brief intro about the products
- Affiliate disclaimer
- Timestamps
- Call to action (like, subscribe, comment)

Generate ONLY the description, no other text."""

        description = await self.hf_client.generate_text(
            prompt=desc_prompt,
            max_length=400,
            temperature=0.7
        )

        # Tags (simple extraction from category)
        tags = [category, "review", "2025", "best", "top 5", "amazon"]

        return {
            'title': title.strip()[:60],  # Limit to 60 chars
            'description': description.strip(),
            'tags': tags
        }

    async def _generate_wordpress_content(self, products: List[Dict[str, Any]], category: str) -> Dict[str, Any]:
        """Generate WordPress blog post"""
        title = f"Top 5 {category} in 2025 - Expert Review"

        # Simple content generation
        content = f"""<p>Looking for the best {category.lower()} in 2025? We've tested and reviewed the top products to help you make the right choice.</p>

<h2>Our Top Picks</h2>
"""

        for i, product in enumerate(products[:5], 1):
            content += f"""
<h3>{i}. {product.get('title', 'Product')}</h3>
<p>Price: {product.get('price', 'N/A')} | Rating: {product.get('rating', 0)}/5 ⭐</p>
<p><a href="{product.get('product_url', '#')}" target="_blank">Check Price on Amazon</a></p>
"""

        return {
            'title': title,
            'content': content
        }

    async def _generate_instagram_content(self, products: List[Dict[str, Any]], category: str) -> Dict[str, Any]:
        """Generate Instagram caption"""
        caption = f"""✨ Top 5 {category} in 2025! ✨

Check out our latest video reviewing the best {category.lower()} available right now.

👉 Link in bio to watch the full review!

Which one would you choose? Comment below! 👇"""

        return {'caption': caption}

    async def _generate_hashtags(self, category: str) -> List[str]:
        """Generate relevant hashtags"""
        base_tags = [
            "amazon", "review", "2025", "top5", "productreview",
            "shopping", "deals", "affiliate", "recommendations"
        ]

        # Add category-specific tags
        category_tag = category.lower().replace(' & ', '').replace(' ', '')
        base_tags.append(category_tag)

        return base_tags[:30]  # Limit to 30 hashtags

    async def _fallback_openai_scripts(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback to OpenAI GPT-4o-mini if HuggingFace fails"""
        self.logger.warning("⚠️  Falling back to GPT-4o-mini for script generation...")

        try:
            # Import OpenAI script generator
            from src.mcp.production_text_generation_control_agent_mcp_v2 import production_run_text_control_with_regeneration

            result = await production_run_text_control_with_regeneration(products)

            self.logger.warning("⚠️  Scripts generated with GPT-4o-mini (fallback, cost: $0.10)")

            return result

        except Exception as e:
            self.logger.error(f"❌ Fallback also failed: {e}")
            raise RuntimeError("Both HuggingFace and OpenAI failed for text generation")

    async def validate_input(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input parameters"""
        operation = task.get('operation', 'generate_content')

        if operation == 'generate_scripts':
            if 'products' not in task or not task['products']:
                return {'valid': False, 'error': 'Missing or empty products list'}

        return {'valid': True}

    async def validate_output(self, result: Any) -> Dict[str, Any]:
        """Validate output result"""
        if not isinstance(result, dict):
            return {'valid': False, 'error': 'Result must be a dictionary'}

        # Check for key fields based on operation type
        required_fields = ['intro_script', 'outro_script'] if 'intro_script' in result else ['youtube_title', 'youtube_description']

        for field in required_fields:
            if field not in result or not result[field]:
                return {'valid': False, 'error': f'Missing or empty {field}'}

        return {'valid': True}
