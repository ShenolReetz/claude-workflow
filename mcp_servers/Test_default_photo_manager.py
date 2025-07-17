#!/usr/bin/env python3
"""
Test Default Photo Manager
Manages default photos for test workflow to avoid generating new images every run
"""

import json
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDefaultPhotoManager:
    """Manages default photos for test workflow efficiency"""
    
    def __init__(self):
        self.config_path = '/home/claude-workflow/config/test_default_photos.json'
        self.default_photos = self._load_default_photos()
        
    def _load_default_photos(self) -> Dict[str, Any]:
        """Load default photo configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info("✅ Loaded default photo configuration")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Default photo config not found: {self.config_path}")
            return self._create_fallback_config()
        except Exception as e:
            logger.error(f"❌ Error loading default photos: {e}")
            return self._create_fallback_config()
    
    def _create_fallback_config(self) -> Dict[str, Any]:
        """Create minimal fallback configuration"""
        return {
            "test_mode_enabled": True,
            "default_photos": {
                "intro_photo": "https://via.placeholder.com/1080x1920/000000/FFFFFF?text=TEST+INTRO",
                "outro_photo": "https://via.placeholder.com/1080x1920/000000/FFFFFF?text=TEST+OUTRO",
                "product_photos": {
                    "product_1": "https://via.placeholder.com/500x500/FF0000/FFFFFF?text=PRODUCT+1",
                    "product_2": "https://via.placeholder.com/500x500/00FF00/FFFFFF?text=PRODUCT+2",
                    "product_3": "https://via.placeholder.com/500x500/0000FF/FFFFFF?text=PRODUCT+3",
                    "product_4": "https://via.placeholder.com/500x500/FFFF00/000000?text=PRODUCT+4",
                    "product_5": "https://via.placeholder.com/500x500/FF00FF/FFFFFF?text=PRODUCT+5"
                }
            }
        }
    
    def get_default_product_photos(self, category: str = None) -> List[str]:
        """Get default product photos for a category or generic ones"""
        try:
            # Try category-specific photos first
            if category and category in self.default_photos.get('photo_categories', {}):
                photos = self.default_photos['photo_categories'][category]
                logger.info(f"🖼️ Using category-specific photos for: {category}")
                return photos
            
            # Fallback to generic product photos
            product_photos = self.default_photos['default_photos']['product_photos']
            photos = [
                product_photos.get('product_1'),
                product_photos.get('product_2'),
                product_photos.get('product_3'),
                product_photos.get('product_4'),
                product_photos.get('product_5')
            ]
            
            # Filter out None values
            photos = [p for p in photos if p]
            
            logger.info(f"🖼️ Using generic default product photos ({len(photos)} available)")
            return photos
            
        except Exception as e:
            logger.error(f"❌ Error getting default product photos: {e}")
            return self._get_placeholder_photos()
    
    def get_intro_photo(self) -> str:
        """Get default intro photo"""
        try:
            intro_photo = self.default_photos['default_photos']['intro_photo']
            logger.info("🖼️ Using default intro photo")
            return intro_photo
        except Exception as e:
            logger.error(f"❌ Error getting intro photo: {e}")
            return "https://via.placeholder.com/1080x1920/000000/FFFFFF?text=TEST+INTRO"
    
    def get_outro_photo(self) -> str:
        """Get default outro photo"""
        try:
            outro_photo = self.default_photos['default_photos']['outro_photo']
            logger.info("🖼️ Using default outro photo")
            return outro_photo
        except Exception as e:
            logger.error(f"❌ Error getting outro photo: {e}")
            return "https://via.placeholder.com/1080x1920/000000/FFFFFF?text=TEST+OUTRO"
    
    def _get_placeholder_photos(self) -> List[str]:
        """Get placeholder photos as absolute fallback"""
        return [
            "https://via.placeholder.com/500x500/FF0000/FFFFFF?text=PRODUCT+1",
            "https://via.placeholder.com/500x500/00FF00/FFFFFF?text=PRODUCT+2",
            "https://via.placeholder.com/500x500/0000FF/FFFFFF?text=PRODUCT+3",
            "https://via.placeholder.com/500x500/FFFF00/000000?text=PRODUCT+4",
            "https://via.placeholder.com/500x500/FF00FF/FFFFFF?text=PRODUCT+5"
        ]
    
    def populate_airtable_with_default_photos(self, record_data: Dict[str, Any], category: str = None) -> Dict[str, str]:
        """Populate Airtable record with default photos"""
        try:
            updates = {}
            
            # Get product photos
            product_photos = self.get_default_product_photos(category)
            
            # Assign photos to products
            for i in range(1, 6):
                if i <= len(product_photos):
                    updates[f'ProductNo{i}Photo'] = product_photos[i-1]
                else:
                    # Use fallback if not enough photos
                    fallback = self.default_photos.get('default_photos', {}).get('fallback_photos', {}).get('generic_product')
                    updates[f'ProductNo{i}Photo'] = fallback or f"https://via.placeholder.com/500x500/CCCCCC/000000?text=PRODUCT+{i}"
            
            # Add intro and outro photos
            updates['IntroPhoto'] = self.get_intro_photo()
            updates['OutroPhoto'] = self.get_outro_photo()
            
            logger.info(f"✅ TEST MODE: Using default photos instead of generating new ones")
            logger.info(f"📊 Updated {len(updates)} photo fields with default URLs")
            
            return updates
            
        except Exception as e:
            logger.error(f"❌ Error populating default photos: {e}")
            return {}
    
    def detect_category_from_title(self, title: str) -> str:
        """Detect category from title for better photo matching"""
        title_lower = title.lower()
        
        category_keywords = {
            'electronics': ['headset', 'phone', 'laptop', 'tablet', 'speaker', 'camera', 'tv', 'monitor', 'gaming'],
            'home_kitchen': ['kitchen', 'home', 'appliance', 'cookware', 'furniture', 'decor'],
            'sports_outdoors': ['sports', 'outdoor', 'fitness', 'exercise', 'camping', 'hiking'],
            'beauty_personal_care': ['beauty', 'skincare', 'makeup', 'hair', 'personal care'],
            'automotive': ['car', 'auto', 'vehicle', 'tire', 'automotive'],
            'fashion': ['clothing', 'fashion', 'shoes', 'accessories', 'style']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                logger.info(f"🎯 Detected category '{category}' from title: {title}")
                return category
        
        logger.info(f"🔍 No specific category detected for: {title}, using generic photos")
        return 'electronics'  # Default to electronics as most common
    
    def get_test_mode_status(self) -> Dict[str, Any]:
        """Get test mode configuration status"""
        return {
            'test_mode_enabled': self.default_photos.get('test_mode_enabled', False),
            'config_loaded': bool(self.default_photos),
            'available_categories': list(self.default_photos.get('photo_categories', {}).keys()),
            'total_default_photos': len(self.default_photos.get('default_photos', {}).get('product_photos', {})),
            'timestamp': datetime.now().isoformat()
        }

# Test function
if __name__ == "__main__":
    def test_default_photo_manager():
        manager = TestDefaultPhotoManager()
        
        print("🧪 Testing Default Photo Manager")
        print("=" * 50)
        
        # Test status
        status = manager.get_test_mode_status()
        print(f"📊 Test Mode Status: {status}")
        
        # Test category detection
        test_titles = [
            "Best Gaming Headsets 2024",
            "Top Kitchen Appliances",
            "Best Outdoor Camping Gear"
        ]
        
        for title in test_titles:
            category = manager.detect_category_from_title(title)
            photos = manager.get_default_product_photos(category)
            print(f"\n🎯 Title: {title}")
            print(f"   Category: {category}")
            print(f"   Photos available: {len(photos)}")
        
        # Test Airtable population
        test_record = {'Title': 'Test Gaming Products'}
        updates = manager.populate_airtable_with_default_photos(test_record, 'electronics')
        print(f"\n📋 Airtable Updates: {len(updates)} fields")
        for field, url in updates.items():
            print(f"   {field}: {url[:50]}...")
    
    test_default_photo_manager()