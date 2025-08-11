#!/usr/bin/env python3
"""
Production Scraping Variant Generator
====================================

Generates multiple search variants from a main title to improve Amazon product discovery.
Uses OpenAI to create intelligent variations that maintain search intent while exploring different keyword combinations.
"""

import json
import re
from typing import List, Dict
import openai

class ProductionScrapingVariantGenerator:
    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
    
    async def generate_search_variants(self, title: str, max_variants: int = 5) -> List[str]:
        """
        Generate search variants from a main title for Amazon product scraping.
        
        Args:
            title: Original title like "Top 5 Webcam Stands Most Popular on Amazon 2025"
            max_variants: Maximum number of variants to generate
            
        Returns:
            List of search variants like ["Webcam Stands", "Stands for Webcams", "Camera Stands"]
        """
        
        # Extract the core product from title using regex patterns
        core_product = self._extract_core_product(title)
        
        # Generate variants using OpenAI
        prompt = f"""
        Generate {max_variants} different search variants for finding "{core_product}" products on Amazon.
        
        Original title: "{title}"
        Core product: "{core_product}"
        
        Create variants that:
        1. Use different keyword orders
        2. Include synonyms and related terms
        3. Use both specific and general terms
        4. Maintain the same product category intent
        
        Return only the search terms, one per line, no numbering or formatting.
        Each variant should be 1-4 words maximum, suitable for Amazon search.
        
        Examples for "Webcam Stands":
        Webcam Stands
        Stands for Webcams
        Camera Stands
        Desktop Camera Mounts
        Webcam Holders
        """
        
        try:
            # Try GPT-5 first, fallback to GPT-5-mini
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating Amazon search variations for product discovery."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
            except Exception:
                # Fallback to GPT-5-mini
                response = self.client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating Amazon search variations for product discovery."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=200
                )
            
            variants_text = response.choices[0].message.content.strip()
            variants = [v.strip() for v in variants_text.split('\n') if v.strip()]
            
            # Add the original core product as first variant if not already included
            if core_product not in variants:
                variants.insert(0, core_product)
            
            # Limit to max_variants
            return variants[:max_variants]
            
        except Exception as e:
            print(f"❌ Error generating search variants: {e}")
            # Fallback to simple extraction
            return [core_product] if core_product else [title]
    
    def _extract_core_product(self, title: str) -> str:
        """
        Extract the core product name from titles like 'Top 5 Webcam Stands Most Popular on Amazon 2025'
        """
        
        # Common patterns to remove
        patterns_to_remove = [
            r'^top\s+\d+\s+',  # "Top 5 "
            r'^best\s+\d+\s+',  # "Best 10 "
            r'^most\s+popular\s+',  # "Most Popular "
            r'\s+most\s+popular.*$',  # " Most Popular on Amazon 2025"
            r'\s+on\s+amazon.*$',  # " on Amazon 2025"
            r'\s+\d{4}$',  # " 2025"
            r'\s+reviews?$',  # " review" or " reviews"
            r'^the\s+',  # "The "
        ]
        
        core_product = title.lower()
        
        # Apply removal patterns
        for pattern in patterns_to_remove:
            core_product = re.sub(pattern, '', core_product, flags=re.IGNORECASE)
        
        # Clean up extra spaces and capitalize properly
        core_product = ' '.join(core_product.split())
        core_product = core_product.title()
        
        return core_product if core_product else title

if __name__ == "__main__":
    # Test the variant generator
    import asyncio
    
    async def test_variants():
        generator = ProductionScrapingVariantGenerator("test-key")
        
        test_titles = [
            "Top 5 Webcam Stands Most Popular on Amazon 2025",
            "Best Phone Holders for Car Dashboard",
            "Most Popular Bluetooth Speakers Under $50"
        ]
        
        for title in test_titles:
            print(f"\nTitle: {title}")
            variants = await generator.generate_search_variants(title)
            for i, variant in enumerate(variants, 1):
                print(f"  {i}. {variant}")
    
    # asyncio.run(test_variants())