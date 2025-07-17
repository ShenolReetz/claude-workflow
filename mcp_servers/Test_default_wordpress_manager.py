#!/usr/bin/env python3
"""
Test Default WordPress Manager
Manages pre-generated WordPress blog content for test workflow to save significant token costs
WordPress content generation typically uses 1000+ tokens per post
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDefaultWordPressManager:
    """Manages default WordPress content for test workflow efficiency"""
    
    def __init__(self):
        self.config_path = '/home/claude-workflow/config/test_default_wordpress_content.json'
        self.default_content = self._load_default_content()
        
    def _load_default_content(self) -> Dict[str, Any]:
        """Load default WordPress content configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info("✅ Loaded default WordPress content configuration")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Default WordPress config not found: {self.config_path}")
            return self._create_fallback_config()
        except Exception as e:
            logger.error(f"❌ Error loading default WordPress content: {e}")
            return self._create_fallback_config()
    
    def _create_fallback_config(self) -> Dict[str, Any]:
        """Create minimal fallback configuration"""
        return {
            "test_mode_enabled": True,
            "default_wordpress_content": {
                "fallback_content": {
                    "title": "Top 5 Best Products for 2025 - Expert Review",
                    "content": "This is a comprehensive review of the top 5 products in this category. Our expert team has carefully evaluated each option based on performance, value, and customer satisfaction. Each product offers unique benefits and has been selected to meet different needs and budgets."
                }
            }
        }
    
    def _detect_category(self, title: str) -> Optional[str]:
        """Detect product category from title for category-specific content"""
        title_lower = title.lower()
        
        # Category mappings
        if any(word in title_lower for word in ['gaming', 'computer', 'tech', 'electronics', 'rgb', 'smart', 'digital']):
            return 'electronics'
        elif any(word in title_lower for word in ['kitchen', 'home', 'house', 'counter', 'living', 'bedroom', 'furniture']):
            return 'home_kitchen'
        elif any(word in title_lower for word in ['car', 'auto', 'vehicle', 'automotive', 'driving', 'truck']):
            return 'automotive'
        elif any(word in title_lower for word in ['sports', 'outdoor', 'fitness', 'exercise', 'hiking', 'camping']):
            return 'sports_outdoors'
        elif any(word in title_lower for word in ['beauty', 'personal', 'care', 'cosmetic', 'skincare', 'makeup']):
            return 'beauty_personal_care'
        elif any(word in title_lower for word in ['fashion', 'clothing', 'style', 'apparel', 'shoes', 'accessories']):
            return 'fashion'
        
        return None  # Use generic template
    
    def _customize_content(self, template: str, title: str, category: str = None) -> str:
        """Customize template content with dynamic values"""
        try:
            # Extract year from title or use current year
            current_year = datetime.now().year
            year = str(current_year)
            
            # Extract category from title if not provided
            if not category:
                category = self._detect_category(title) or "products"
            
            # Replace placeholders
            customized = template.replace('{category}', category)
            customized = customized.replace('{year}', year)
            
            # Add product-specific information if available in title
            if 'power strip' in title.lower():
                customized = customized.replace('{category}', 'power strips and surge protectors')
            elif 'gaming' in title.lower():
                customized = customized.replace('{category}', 'gaming accessories')
            elif 'kitchen' in title.lower():
                customized = customized.replace('{category}', 'kitchen appliances')
            
            return customized
            
        except Exception as e:
            logger.warning(f"Error customizing content: {e}")
            return template
    
    def get_wordpress_content(self, title: str, category: str = None) -> Dict[str, str]:
        """Get default WordPress blog content"""
        try:
            detected_category = category or self._detect_category(title)
            
            # Try category-specific content first
            if detected_category and detected_category in self.default_content['default_wordpress_content'].get('category_specific', {}):
                category_content = self.default_content['default_wordpress_content']['category_specific'][detected_category]
                logger.info(f"📝 Using category-specific WordPress content for: {detected_category}")
                
                return {
                    'title': self._customize_content(category_content['title'], title, detected_category),
                    'content': self._customize_content(category_content['content'], title, detected_category),
                    'category': detected_category,
                    'word_count': len(category_content['content'].split()),
                    'template_used': f'category_{detected_category}'
                }
            
            # Fall back to generic template
            generic_content = self.default_content['default_wordpress_content']['generic_template']
            logger.info(f"📝 Using generic WordPress template")
            
            return {
                'title': self._customize_content(generic_content['title'], title),
                'content': self._customize_content(generic_content['content'], title),
                'category': 'generic',
                'word_count': len(generic_content['content'].split()),
                'template_used': 'generic_template'
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting WordPress content: {e}")
            # Ultimate fallback
            fallback = self.default_content['default_wordpress_content']['fallback_content']
            return {
                'title': fallback['title'],
                'content': fallback['content'],
                'category': 'fallback',
                'word_count': len(fallback['content'].split()),
                'template_used': 'fallback'
            }
    
    def populate_airtable_with_default_wordpress(self, record_data: Dict[str, Any], category: str = None) -> Dict[str, str]:
        """Populate Airtable record with default WordPress content"""
        try:
            # Get the record title for content generation
            title = record_data.get('Title', 'Top 5 Best Products')
            
            # Generate WordPress content
            wordpress_data = self.get_wordpress_content(title, category)
            
            updates = {
                'WordPressTitle': wordpress_data['title'],
                'WordPressDescription': wordpress_data['content']
            }
            
            logger.info(f"✅ TEST MODE: Using default WordPress content (no generation needed)")
            logger.info(f"📊 WordPress content: {wordpress_data['word_count']} words")
            logger.info(f"🎯 Template used: {wordpress_data['template_used']}")
            logger.info(f"💰 Token savings: ~1000+ tokens (typical WordPress generation cost)")
            
            return updates
            
        except Exception as e:
            logger.error(f"❌ Error populating default WordPress content: {e}")
            return {}
    
    def get_test_mode_status(self) -> Dict[str, Any]:
        """Get test mode WordPress configuration status"""
        return {
            'test_mode_enabled': self.default_content.get('test_mode_enabled', False),
            'config_loaded': bool(self.default_content),
            'available_templates': len(self.default_content.get('default_wordpress_content', {}).get('category_specific', {})),
            'categories_supported': list(self.default_content.get('default_wordpress_content', {}).get('category_specific', {}).keys()),
            'token_savings_per_post': '1000+',
            'average_word_count': '500-800',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_content_summary(self) -> Dict[str, Any]:
        """Get summary of all available WordPress content"""
        try:
            category_content = self.default_content.get('default_wordpress_content', {}).get('category_specific', {})
            
            summaries = {}
            for category, content in category_content.items():
                summaries[category] = {
                    'title': content['title'][:100] + '...' if len(content['title']) > 100 else content['title'],
                    'content_preview': content['content'][:200] + '...',
                    'word_count': len(content['content'].split())
                }
            
            return {
                'available_categories': list(summaries.keys()),
                'category_summaries': summaries,
                'total_templates': len(summaries),
                'generic_template_available': bool(self.default_content.get('default_wordpress_content', {}).get('generic_template')),
                'fallback_available': bool(self.default_content.get('default_wordpress_content', {}).get('fallback_content'))
            }
            
        except Exception as e:
            logger.error(f"Error getting content summary: {e}")
            return {
                'available_categories': [],
                'category_summaries': {},
                'total_templates': 0,
                'generic_template_available': False,
                'fallback_available': True
            }

# Test function
if __name__ == "__main__":
    def test_default_wordpress_manager():
        manager = TestDefaultWordPressManager()
        
        print("🧪 Testing Default WordPress Manager")
        print("=" * 50)
        
        # Test status
        status = manager.get_test_mode_status()
        print(f"📊 Test Mode Status: {status}")
        
        # Test content summary
        summary = manager.get_content_summary()
        print(f"\n📝 Content Summary:")
        for category, details in summary['category_summaries'].items():
            print(f"   {category}:")
            print(f"     Title: {details['title']}")
            print(f"     Word Count: {details['word_count']}")
            print(f"     Preview: {details['content_preview']}")
        
        # Test content generation for different categories
        test_titles = [
            'Top 5 Best Power Strips & Surge Protectors 2025',
            'Best Gaming Headsets for PC Gaming',
            'Top Kitchen Appliances for Home Cooking',
            'Best Car Accessories for Road Trips'
        ]
        
        for title in test_titles:
            content = manager.get_wordpress_content(title)
            print(f"\n🎯 Testing: '{title}'")
            print(f"   Generated Title: {content['title'][:100]}...")
            print(f"   Category: {content['category']}")
            print(f"   Word Count: {content['word_count']}")
            print(f"   Template: {content['template_used']}")
        
        # Test Airtable population
        test_record = {'Title': 'Top 5 Best Power Strips & Surge Protectors 2025'}
        updates = manager.populate_airtable_with_default_wordpress(test_record)
        print(f"\n📋 Airtable Updates: {len(updates)} fields")
        for field, value in updates.items():
            print(f"   {field}: {value[:100]}...")
    
    test_default_wordpress_manager()