#!/usr/bin/env python3
"""
Voice Timing Optimizer (TEST MODE)
Calibrates text length for optimal voice narration timing in 2-second scenes
"""

import asyncio
import json
import logging
from typing import Dict, Tuple, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceTimingOptimizer:
    """Optimizes text length for voice narration timing (TEST MODE: 2-second scenes)"""
    
    def __init__(self):
        # ElevenLabs average speaking rates (words per minute)
        self.wpm_rates = {
            "slow": 140,      # Slower, more dramatic
            "normal": 160,    # Normal conversational pace
            "fast": 180       # Faster, energetic pace
        }
        
        # Target durations in seconds (TEST MODE: 2-second scenes)
        self.target_durations = {
            "intro": 2,
            "product": 2,
            "outro": 2
        }
        
        # Use normal pace as default
        self.default_wpm = self.wpm_rates["normal"]
    
    def calculate_word_count(self, duration_seconds: int, pace: str = "normal") -> int:
        """Calculate optimal word count for target duration"""
        wpm = self.wpm_rates.get(pace, self.default_wpm)
        words_per_second = wpm / 60
        return int(duration_seconds * words_per_second)
    
    def analyze_text_timing(self, text: str, target_duration: int, pace: str = "normal") -> Dict:
        """Analyze if text fits target duration"""
        # Count words (simple split on whitespace)
        words = text.split()
        word_count = len(words)
        
        # Calculate estimated duration
        wpm = self.wpm_rates.get(pace, self.default_wpm)
        estimated_duration = (word_count / wpm) * 60
        
        # Calculate optimal word count
        optimal_word_count = self.calculate_word_count(target_duration, pace)
        
        # Determine if text is good fit
        tolerance = 0.1  # 10% tolerance
        min_words = int(optimal_word_count * (1 - tolerance))
        max_words = int(optimal_word_count * (1 + tolerance))
        
        is_good_fit = min_words <= word_count <= max_words
        
        return {
            "text": text,
            "word_count": word_count,
            "estimated_duration": round(estimated_duration, 1),
            "target_duration": target_duration,
            "optimal_word_count": optimal_word_count,
            "word_count_range": (min_words, max_words),
            "is_good_fit": is_good_fit,
            "adjustment_needed": word_count - optimal_word_count,
            "pace": pace
        }
    
    def generate_intro_constraints(self) -> Dict:
        """Get constraints for intro text generation (TEST MODE: 2 words max)"""
        return {
            "target_duration": self.target_durations["intro"],
            "word_count": 2,
            "word_range": (1, 2),
            "guidelines": [
                "EXACTLY 2 words maximum for 2-second scene",
                "Start with attention-grabbing word",
                "Keep it simple and clear"
            ],
            "example_structure": "Welcome! Today",
            "test_mode": True
        }
    
    def generate_product_constraints(self) -> Dict:
        """Get constraints for product description generation (TEST MODE: 2 words max)"""
        return {
            "target_duration": self.target_durations["product"],
            "total_word_count": 2,
            "word_range": (1, 2),
            "description_word_count": 0,
            "guidelines": [
                "EXACTLY 2 words maximum for 2-second scene",
                "Format: 'Number X' where X is the rank",
                "Keep it minimal and clear"
            ],
            "example_structure": "Number 5",
            "test_mode": True
        }
    
    def generate_outro_constraints(self) -> Dict:
        """Get constraints for outro text generation (TEST MODE: 2 words max)"""
        return {
            "target_duration": self.target_durations["outro"],
            "word_count": 2,
            "word_range": (1, 2),
            "guidelines": [
                "EXACTLY 2 words maximum for 2-second scene",
                "Thank viewers briefly",
                "Keep it simple and impactful"
            ],
            "example_structure": "Thanks! Subscribe",
            "test_mode": True
        }
    
    def optimize_text(self, text: str, target_type: str, pace: str = "normal") -> Tuple[str, Dict]:
        """Optimize text for target duration"""
        target_duration = self.target_durations.get(target_type, 10)
        analysis = self.analyze_text_timing(text, target_duration, pace)
        
        if analysis["is_good_fit"]:
            return text, analysis
        
        # Text needs adjustment
        words = text.split()
        current_count = len(words)
        target_count = analysis["optimal_word_count"]
        
        if current_count > target_count:
            # Text is too long - need to trim
            # Remove filler words first
            filler_words = ["very", "really", "actually", "basically", "just", "quite"]
            words = [w for w in words if w.lower() not in filler_words]
            
            # If still too long, truncate
            if len(words) > target_count:
                words = words[:target_count]
            
            optimized_text = " ".join(words)
        else:
            # Text is too short - this is harder to fix automatically
            # Return with warning
            optimized_text = text
            analysis["warning"] = f"Text is {target_count - current_count} words too short"
        
        # Re-analyze optimized text
        new_analysis = self.analyze_text_timing(optimized_text, target_duration, pace)
        
        return optimized_text, new_analysis


# Test the optimizer
if __name__ == "__main__":
    optimizer = VoiceTimingOptimizer()
    
    print("🎯 Voice Timing Optimizer Test")
    print("=" * 50)
    
    # Test intro constraints
    intro_constraints = optimizer.generate_intro_constraints()
    print("\n📝 INTRO CONSTRAINTS:")
    print(f"Target: {intro_constraints['target_duration']} seconds")
    print(f"Words: {intro_constraints['word_count']} ({intro_constraints['word_range'][0]}-{intro_constraints['word_range'][1]})")
    print("Guidelines:")
    for guideline in intro_constraints['guidelines']:
        print(f"  - {guideline}")
    
    # Test product constraints
    product_constraints = optimizer.generate_product_constraints()
    print("\n📦 PRODUCT CONSTRAINTS:")
    print(f"Target: {product_constraints['target_duration']} seconds")
    print(f"Total words: {product_constraints['total_word_count']}")
    print(f"Description words: {product_constraints['description_word_count']}")
    
    # Test outro constraints
    outro_constraints = optimizer.generate_outro_constraints()
    print("\n👋 OUTRO CONSTRAINTS:")
    print(f"Target: {outro_constraints['target_duration']} seconds")
    print(f"Words: {outro_constraints['word_count']} ({outro_constraints['word_range'][0]}-{outro_constraints['word_range'][1]})")
    
    # Test text analysis
    print("\n🔍 TEXT ANALYSIS EXAMPLES:")
    
    test_intro = "Welcome back to our channel! Today we're counting down the top 5 gaming headsets!"
    analysis = optimizer.analyze_text_timing(test_intro, 5)
    print(f"\nIntro: '{test_intro}'")
    print(f"Words: {analysis['word_count']} (optimal: {analysis['optimal_word_count']})")
    print(f"Duration: {analysis['estimated_duration']}s")
    print(f"Good fit: {analysis['is_good_fit']}")