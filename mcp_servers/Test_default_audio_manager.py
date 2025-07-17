#!/usr/bin/env python3
"""
Test Default Audio Manager
Manages default audio files for test workflow to avoid generating new audio every run
All audio files are 2-second clips with exactly 2 words
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDefaultAudioManager:
    """Manages default audio files for test workflow efficiency"""
    
    def __init__(self):
        self.config_path = '/home/claude-workflow/config/test_default_audio.json'
        self.default_audio = self._load_default_audio()
        
    def _load_default_audio(self) -> Dict[str, Any]:
        """Load default audio configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info("✅ Loaded default audio configuration")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Default audio config not found: {self.config_path}")
            return self._create_fallback_config()
        except Exception as e:
            logger.error(f"❌ Error loading default audio: {e}")
            return self._create_fallback_config()
    
    def _create_fallback_config(self) -> Dict[str, Any]:
        """Create minimal fallback configuration"""
        return {
            "test_mode_enabled": True,
            "default_audio": {
                "intro_mp3": "https://drive.google.com/file/d/fallback_intro/view",
                "outro_mp3": "https://drive.google.com/file/d/fallback_outro/view",
                "product_mp3s": {
                    "product_1": "https://drive.google.com/file/d/fallback_number_5/view",
                    "product_2": "https://drive.google.com/file/d/fallback_number_4/view",
                    "product_3": "https://drive.google.com/file/d/fallback_number_3/view",
                    "product_4": "https://drive.google.com/file/d/fallback_number_2/view",
                    "product_5": "https://drive.google.com/file/d/fallback_number_1/view"
                }
            }
        }
    
    def get_intro_audio(self, category: str = None) -> Dict[str, str]:
        """Get default intro audio (2-second clip: 'Welcome! Today')"""
        try:
            # Try category-specific intro first
            if category and category in self.default_audio.get('category_specific_intros', {}):
                category_intro = self.default_audio['category_specific_intros'][category]
                logger.info(f"🎵 Using category-specific intro audio for: {category}")
                return {
                    'url': category_intro['intro_mp3'],
                    'text': category_intro['text'],
                    'duration': 2
                }
            
            # Default intro
            intro_url = self.default_audio['default_audio']['intro_mp3']
            intro_text = self.default_audio['audio_content']['intro']['text']
            
            logger.info(f"🎵 Using default intro audio: '{intro_text}'")
            return {
                'url': intro_url,
                'text': intro_text,
                'duration': 2
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting intro audio: {e}")
            return {
                'url': "https://drive.google.com/file/d/fallback_intro/view",
                'text': "Welcome! Today",
                'duration': 2
            }
    
    def get_outro_audio(self) -> Dict[str, str]:
        """Get default outro audio (2-second clip: 'Thanks! Subscribe')"""
        try:
            outro_url = self.default_audio['default_audio']['outro_mp3']
            outro_text = self.default_audio['audio_content']['outro']['text']
            
            logger.info(f"🎵 Using default outro audio: '{outro_text}'")
            return {
                'url': outro_url,
                'text': outro_text,
                'duration': 2
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting outro audio: {e}")
            return {
                'url': "https://drive.google.com/file/d/fallback_outro/view",
                'text': "Thanks! Subscribe",
                'duration': 2
            }
    
    def get_product_audio(self, product_number: int) -> Dict[str, str]:
        """Get default product audio (2-second clips: 'Number X')"""
        try:
            # Map product number to countdown order (1->5, 2->4, etc.)
            countdown_number = 6 - product_number
            
            product_key = f"product_{product_number}"
            product_audio = self.default_audio['default_audio']['product_mp3s'].get(product_key)
            product_content = self.default_audio['audio_content']['products'].get(product_key, {})
            
            if product_audio:
                logger.info(f"🎵 Using default product {product_number} audio: '{product_content.get('text', f'Number {countdown_number}')}'")
                return {
                    'url': product_audio,
                    'text': product_content.get('text', f'Number {countdown_number}'),
                    'duration': 2,
                    'countdown_number': countdown_number
                }
            else:
                # Fallback
                logger.warning(f"⚠️ No default audio for product {product_number}, using fallback")
                return {
                    'url': self.default_audio['default_audio']['fallback_audio']['generic_product'],
                    'text': f"Number {countdown_number}",
                    'duration': 2,
                    'countdown_number': countdown_number
                }
                
        except Exception as e:
            logger.error(f"❌ Error getting product {product_number} audio: {e}")
            countdown_number = 6 - product_number
            return {
                'url': "https://drive.google.com/file/d/fallback_product/view",
                'text': f"Number {countdown_number}",
                'duration': 2,
                'countdown_number': countdown_number
            }
    
    def populate_airtable_with_default_audio(self, record_data: Dict[str, Any], category: str = None) -> Dict[str, str]:
        """Populate Airtable record with default audio URLs"""
        try:
            updates = {}
            
            # Get intro audio
            intro_audio = self.get_intro_audio(category)
            updates['IntroMp3'] = intro_audio['url']
            updates['IntroHook'] = intro_audio['text']
            
            # Get outro audio
            outro_audio = self.get_outro_audio()
            updates['OutroMp3'] = outro_audio['url']
            updates['OutroCallToAction'] = outro_audio['text']
            
            # Get product audio (1-5 products) - only if fields exist in Airtable
            try:
                for i in range(1, 6):
                    product_audio = self.get_product_audio(i)
                    # Try to update MP3 field - skip if field doesn't exist in Airtable
                    updates[f'Product{i}Mp3'] = product_audio['url']
                    # Skip ProductXVoiceText fields as they don't exist in Airtable schema
                    # updates[f'Product{i}VoiceText'] = product_audio['text']  # Commented out - field doesn't exist
            except Exception as e:
                logger.warning(f"⚠️ Some audio fields may not exist in Airtable schema: {e}")
                # Continue without audio fields if they don't exist
            
            # Update VideoScript with combined text
            all_texts = [intro_audio['text']]
            for i in range(1, 6):
                product_audio = self.get_product_audio(i)
                all_texts.append(product_audio['text'])
            all_texts.append(outro_audio['text'])
            
            updates['VideoScript'] = '\n\n'.join(all_texts)
            
            logger.info(f"✅ TEST MODE: Using default audio files (no generation needed)")
            logger.info(f"📊 Updated {len(updates)} audio fields with default URLs")
            logger.info(f"⏱️ All audio clips are 2 seconds with 2 words each")
            
            return updates
            
        except Exception as e:
            logger.error(f"❌ Error populating default audio: {e}")
            return {}
    
    def get_test_mode_status(self) -> Dict[str, Any]:
        """Get test mode audio configuration status"""
        return {
            'test_mode_enabled': self.default_audio.get('test_mode_enabled', False),
            'config_loaded': bool(self.default_audio),
            'total_audio_files': 7,  # intro + 5 products + outro
            'audio_duration': 14,    # 7 files × 2 seconds
            'words_per_clip': 2,
            'available_categories': list(self.default_audio.get('category_specific_intros', {}).keys()),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_audio_content_summary(self) -> Dict[str, Any]:
        """Get summary of all audio content"""
        try:
            content = self.default_audio.get('audio_content', {})
            return {
                'intro': content.get('intro', {}).get('text', 'Welcome! Today'),
                'outro': content.get('outro', {}).get('text', 'Thanks! Subscribe'),
                'products': [
                    content.get('products', {}).get(f'product_{i}', {}).get('text', f'Number {6-i}')
                    for i in range(1, 6)
                ],
                'total_duration': 14,  # 7 × 2 seconds
                'total_words': 14      # 7 × 2 words
            }
        except Exception as e:
            logger.error(f"Error getting audio content summary: {e}")
            return {
                'intro': 'Welcome! Today',
                'outro': 'Thanks! Subscribe',
                'products': ['Number 5', 'Number 4', 'Number 3', 'Number 2', 'Number 1'],
                'total_duration': 14,
                'total_words': 14
            }

# Test function
if __name__ == "__main__":
    def test_default_audio_manager():
        manager = TestDefaultAudioManager()
        
        print("🧪 Testing Default Audio Manager")
        print("=" * 50)
        
        # Test status
        status = manager.get_test_mode_status()
        print(f"📊 Test Mode Status: {status}")
        
        # Test audio content summary
        summary = manager.get_audio_content_summary()
        print(f"\n📝 Audio Content Summary:")
        print(f"   Intro: '{summary['intro']}'")
        print(f"   Products: {summary['products']}")
        print(f"   Outro: '{summary['outro']}'")
        print(f"   Total Duration: {summary['total_duration']} seconds")
        print(f"   Total Words: {summary['total_words']} words")
        
        # Test category-specific intros
        test_categories = ['electronics', 'home_kitchen', 'sports_outdoors']
        for category in test_categories:
            intro = manager.get_intro_audio(category)
            print(f"\n🎯 Category '{category}':")
            print(f"   Intro URL: {intro['url'][:50]}...")
            print(f"   Text: '{intro['text']}'")
        
        # Test Airtable population
        test_record = {'Title': 'Test Gaming Products'}
        updates = manager.populate_airtable_with_default_audio(test_record, 'electronics')
        print(f"\n📋 Airtable Updates: {len(updates)} fields")
        for field, value in updates.items():
            if 'Mp3' in field:
                print(f"   {field}: {value[:50]}...")
            else:
                print(f"   {field}: {value}")
    
    test_default_audio_manager()