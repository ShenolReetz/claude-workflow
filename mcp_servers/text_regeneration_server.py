#!/usr/bin/env python3
"""
Text Regeneration Server

This server handles regeneration of specific text fields that failed TTS timing validation.
It regenerates only the failing fields with specific timing constraints.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
import anthropic

class TextRegenerationServer:
    """Server for regenerating specific text fields with timing constraints"""
    
    def __init__(self, anthropic_api_key: str):
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # Field-specific regeneration templates
        self.regeneration_templates = {
            # Video fields (5 second limit)
            'VideoTitle': {
                'max_seconds': 5,
                'max_words': 10,  # ~5 seconds at 150 WPM with buffer
                'prompt_template': """Generate a short, catchy video title for this Amazon product category: {category}

Requirements:
- Maximum {max_words} words (must fit in {max_seconds} seconds of speech)
- Engaging and click-worthy
- Include trending keywords
- Focus on benefits or excitement

Current title that's too long: {current_text}

Generate a shorter, more impactful title:"""
            },
            
            'VideoDescription': {
                'max_seconds': 5,
                'max_words': 10,
                'prompt_template': """Generate a brief video description for this Amazon product category: {category}

Requirements:
- Maximum {max_words} words (must fit in {max_seconds} seconds of speech)
- Complementary to the title
- Call to action oriented
- Creates urgency or interest

Current description that's too long: {current_text}

Generate a shorter, more compelling description:"""
            },
            
            # Product fields (9 second limit)
            'ProductNo1Title': {
                'max_seconds': 9,
                'max_words': 18,  # ~9 seconds at 150 WPM with buffer
                'prompt_template': """Generate a concise product title for this Amazon product: {product_name}

Requirements:
- Maximum {max_words} words (must fit in {max_seconds} seconds of speech)
- Highlight key features or benefits
- Professional and informative
- Include main keyword

Current title that's too long: {current_text}

Generate a shorter, more focused title:"""
            },
            
            'ProductNo1Description': {
                'max_seconds': 9,
                'max_words': 18,
                'prompt_template': """Generate a brief product description for this Amazon product: {product_name}

Requirements:
- Maximum {max_words} words (must fit in {max_seconds} seconds of speech)
- Focus on primary benefit or feature
- Persuasive and clear
- Creates interest to learn more

Current description that's too long: {current_text}

Generate a shorter, more compelling description:"""
            }
        }
        
        # Apply same template structure to all product numbers
        for i in range(2, 6):  # ProductNo2 through ProductNo5
            self.regeneration_templates[f'ProductNo{i}Title'] = {
                'max_seconds': 9,
                'max_words': 18,
                'prompt_template': self.regeneration_templates['ProductNo1Title']['prompt_template']
            }
            self.regeneration_templates[f'ProductNo{i}Description'] = {
                'max_seconds': 9,
                'max_words': 18,
                'prompt_template': self.regeneration_templates['ProductNo1Description']['prompt_template']
            }
    
    async def regenerate_field(
        self, 
        field_name: str, 
        current_text: str, 
        category: str, 
        product_name: str = "",
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """Regenerate a specific field with timing constraints"""
        
        if field_name not in self.regeneration_templates:
            return {
                "success": False,
                "error": f"No regeneration template for field: {field_name}",
                "field_name": field_name
            }
        
        template_config = self.regeneration_templates[field_name]
        
        print(f"🔄 Regenerating {field_name} (max {template_config['max_words']} words, {template_config['max_seconds']}s)")
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Create the prompt
                prompt = template_config['prompt_template'].format(
                    category=category,
                    product_name=product_name,
                    current_text=current_text,
                    max_words=template_config['max_words'],
                    max_seconds=template_config['max_seconds']
                )
                
                # Generate new text
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model="claude-3-haiku-20240307",
                    max_tokens=100,  # Short response
                    temperature=0.7,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                
                new_text = response.content[0].text.strip()
                
                # Remove quotes if present
                if new_text.startswith('"') and new_text.endswith('"'):
                    new_text = new_text[1:-1]
                
                # Check word count
                word_count = len(new_text.split())
                
                if word_count <= template_config['max_words']:
                    print(f"✅ Successfully regenerated {field_name} in {attempt} attempt(s)")
                    return {
                        "success": True,
                        "field_name": field_name,
                        "new_text": new_text,
                        "word_count": word_count,
                        "max_words": template_config['max_words'],
                        "max_seconds": template_config['max_seconds'],
                        "attempts": attempt,
                        "original_text": current_text
                    }
                else:
                    print(f"⚠️ Attempt {attempt}: {word_count} words > {template_config['max_words']} limit")
                    
            except Exception as e:
                print(f"❌ Attempt {attempt} failed: {str(e)}")
                if attempt == max_attempts:
                    break
                await asyncio.sleep(1)
        
        return {
            "success": False,
            "error": f"Failed to regenerate {field_name} within {max_attempts} attempts",
            "field_name": field_name,
            "original_text": current_text,
            "max_words": template_config['max_words'],
            "max_seconds": template_config['max_seconds'],
            "attempts": max_attempts
        }
    
    async def regenerate_multiple_fields(
        self, 
        failed_fields: List[Dict[str, Any]], 
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """Regenerate multiple failed fields in batch"""
        
        results = []
        successful = 0
        failed = 0
        
        for field_info in failed_fields:
            field_name = field_info.get("field_name")
            current_text = field_info.get("current_text")
            category = field_info.get("category")
            product_name = field_info.get("product_name", "")
            
            result = await self.regenerate_field(
                field_name=field_name,
                current_text=current_text,
                category=category,
                product_name=product_name,
                max_attempts=max_attempts
            )
            
            results.append(result)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
            
            # Small delay between regenerations
            await asyncio.sleep(0.5)
        
        return {
            "summary": {
                "total_fields": len(failed_fields),
                "successful": successful,
                "failed": failed
            },
            "results": results
        }

# Test function
async def test_text_regeneration_server():
    """Test the text regeneration server"""
    
    print("="*80)
    print("🧪 Testing Text Regeneration Server")
    print("="*80)
    
    # This would need actual API key in production
    try:
        server = TextRegenerationServer("dummy_key")
        
        # Test field regeneration
        test_field = "VideoTitle"
        test_text = "This is a very long title that definitely exceeds the maximum word count limit for video titles"
        test_category = "Electronics"
        
        print(f"\nTesting field regeneration:")
        print(f"Field: {test_field}")
        print(f"Original text: {test_text}")
        print(f"Category: {test_category}")
        
        # This would fail with dummy key, but shows the structure
        print("\n(Test would regenerate text with real API key)")
        
    except Exception as e:
        print(f"Expected error with dummy key: {str(e)}")
    
    print("\n" + "="*80)
    print("✅ Test Complete")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_text_regeneration_server())