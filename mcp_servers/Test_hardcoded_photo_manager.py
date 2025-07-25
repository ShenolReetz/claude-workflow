#!/usr/bin/env python3
"""
Hardcoded Photo Manager for Test Mode
Uses real photos from Power Strips project for all Test workflow projects
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

class TestHardcodedPhotoManager:
    """Provides hardcoded real photo URLs from Power Strips project for all Test projects"""
    
    def __init__(self):
        # Hardcoded real photo URLs from "Top 5 Best Power Strips & Surge Protectors 2025" project
        # These are OpenAI guided images that actually exist in Google Drive
        # Using direct download URLs for JSON2Video compatibility
        self.guided_photos = {
            'product1': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',
            'product2': 'https://drive.google.com/uc?id=10-vElXFcVhVU5FDJUEGdh4I_ZziDN2lJ&export=download',
            'product3': 'https://drive.google.com/uc?id=1wQYvUpZsCLGx8A2o90cTcO88dSsXJnFE&export=download',
            'product4': 'https://drive.google.com/uc?id=13VuwBBsIsv6gLYoiS3q6XfoRvVZGgQpZ&export=download',
            'product5': 'https://drive.google.com/uc?id=1W7eRtz9cxkAOoAOF-5N7oc013YsOvSuX&export=download',
            'intro': 'https://drive.google.com/uc?id=1s5J3T82ISC3P6COkFjenhOT58JACwSfD&export=download',  # Product1
            'outro': 'https://drive.google.com/uc?id=1W7eRtz9cxkAOoAOF-5N7oc013YsOvSuX&export=download'   # Product5
        }
        logger.info("✅ Hardcoded photo manager initialized with Power Strips project photos (direct download URLs)")
    
    def get_airtable_photo_updates(self) -> Dict[str, str]:
        """Get hardcoded photo URLs for updating Airtable"""
        
        airtable_updates = {
            'ProductNo1Photo': self.guided_photos['product1'],
            'ProductNo2Photo': self.guided_photos['product2'], 
            'ProductNo3Photo': self.guided_photos['product3'],
            'ProductNo4Photo': self.guided_photos['product4'],
            'ProductNo5Photo': self.guided_photos['product5'],
            'IntroPhoto': self.guided_photos['intro'],
            'OutroPhoto': self.guided_photos['outro']
        }
        
        logger.info(f"📸 Prepared {len(airtable_updates)} hardcoded photo URLs for Airtable")
        logger.info("🎯 Using OpenAI guided photos from Power Strips project for all Test projects")
        
        return airtable_updates

# Test the manager
def test_hardcoded_photos():
    """Test the hardcoded photo manager"""
    
    manager = TestHardcodedPhotoManager()
    
    print("🧪 Testing hardcoded photo manager...")
    urls = manager.get_airtable_photo_updates()
    
    print(f"\n📸 Hardcoded photo URLs ({len(urls)} total):")
    for field, url in urls.items():
        print(f"  {field}: {url}")
    
    return urls

if __name__ == "__main__":
    test_hardcoded_photos()