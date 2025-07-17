#!/usr/bin/env python3
"""
Voice Timing Optimizer
Calibrates text length for optimal voice narration timing
"""

import asyncio
import json
import logging
from typing import Dict, Tuple, List
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceTimingOptimizer:
    """Optimizes text length for voice narration timing"""
    
    def __init__(self):
        # ElevenLabs average speaking rates (words per minute)
        self.wpm_rates = {
            "slow": 140,      # Slower, more dramatic
            "normal": 160,    # Normal conversational pace
            "fast": 180       # Faster, energetic pace
        }
        
        # Target durations in seconds
        self.target_durations = {
            "intro": 5,
            "product": 10,
            "outro": 5
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
        """Get constraints for intro text generation"""
        target_words = self.calculate_word_count(self.target_durations["intro"])
        
        return {
            "target_duration": self.target_durations["intro"],
            "word_count": target_words,
            "word_range": (target_words - 2, target_words + 2),
            "guidelines": [
                f"Must be exactly {target_words-2} to {target_words+2} words",
                "Start with an attention-grabbing hook",
                "Mention the video topic clearly",
                "Create excitement for the countdown",
                "Avoid filler words"
            ],
            "example_structure": "Welcome! Today we're counting down [topic]. Let's discover the best!"
        }
    
    def generate_product_constraints(self) -> Dict:
        """Get constraints for product description generation"""
        target_words = self.calculate_word_count(self.target_durations["product"])
        
        # Product format: "Number X. [Product Name]. [Description]"
        # Reserve ~5 words for number and product name, leaving rest for description
        description_words = target_words - 5
        
        return {
            "target_duration": self.target_durations["product"],
            "total_word_count": target_words,
            "word_range": (target_words - 3, target_words + 3),
            "description_word_count": description_words,
            "guidelines": [
                f"Total narration must be {target_words-3} to {target_words+3} words",
                f"Product description should be ~{description_words} words",
                "Include key features and benefits",
                "Mention what makes it special",
                "Use active, engaging language",
                "Include the ranking number naturally"
            ],
            "example_structure": "Number 5. [Product Name]. [15-20 word description highlighting key features]"
        }
    
    def generate_outro_constraints(self) -> Dict:
        """Get constraints for outro text generation"""
        target_words = self.calculate_word_count(self.target_durations["outro"])
        
        return {
            "target_duration": self.target_durations["outro"],
            "word_count": target_words,
            "word_range": (target_words - 2, target_words + 2),
            "guidelines": [
                f"Must be exactly {target_words-2} to {target_words+2} words",
                "Thank viewers for watching",
                "Include clear call-to-action",
                "Encourage engagement (like, subscribe, comment)",
                "End on a positive note"
            ],
            "example_structure": "Thanks for watching! Subscribe for more reviews and comment your favorite below!"
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