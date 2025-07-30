#!/usr/bin/env python3
"""
Test Voice Timing Optimizer
Hardcoded responses for testing - no API usage
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys
import uuid
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestVoiceTimingOptimizer:
    """Test Voice Timing Optimizer with hardcoded responses"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Voice timing constraints (same as production)
        self.timing_constraints = {
            'intro': {'max_seconds': 5, 'target_seconds': 4},
            'outro': {'max_seconds': 5, 'target_seconds': 4},
            'product_title': {'max_seconds': 9, 'target_seconds': 7},
            'product_description': {'max_seconds': 9, 'target_seconds': 7},
            'video_title': {'max_seconds': 5, 'target_seconds': 4},
            'video_description': {'max_seconds': 5, 'target_seconds': 4}
        }
        
        print("🧪 TEST MODE: Voice Timing Optimizer using hardcoded responses")
        logger.info("🧪 Test Voice Timing Optimizer initialized")
    
    async def analyze_text_timing(self, text: str, content_type: str) -> Dict:
        """Analyze text timing with hardcoded results"""
        
        logger.info(f"⏱️ Test: Analyzing timing for {content_type}: {text[:30]}...")
        print(f"🧪 TEST: Analyzing timing for {content_type}")
        print(f"   Text: {text[:50]}...")
        
        try:
            # Simulate analysis processing time
            await asyncio.sleep(0.3)
            
            # Get constraints for this content type
            constraints = self.timing_constraints.get(content_type, {'max_seconds': 10, 'target_seconds': 8})
            
            # Calculate hardcoded timing based on text length
            word_count = len(text.split())
            char_count = len(text)
            
            # Simulate realistic timing calculation
            # Average speaking speed: 150-160 words per minute
            estimated_seconds = (word_count / 150) * 60
            
            # Add some variation for realism but keep it predictable
            if char_count < 50:
                estimated_seconds = max(2.0, estimated_seconds * 0.9)
            elif char_count > 200:
                estimated_seconds = estimated_seconds * 1.1
            
            # Determine if timing is acceptable
            is_within_limits = estimated_seconds <= constraints['max_seconds']
            is_optimal = estimated_seconds <= constraints['target_seconds']
            
            timing_result = {
                'success': True,
                'text': text,
                'content_type': content_type,
                'analysis': {
                    'word_count': word_count,
                    'character_count': char_count,
                    'estimated_seconds': round(estimated_seconds, 1),
                    'speaking_rate': '150 WPM (average)',
                    'pause_factor': 1.0
                },
                'constraints': constraints,
                'validation': {
                    'is_within_limits': is_within_limits,
                    'is_optimal': is_optimal,
                    'seconds_over_limit': max(0, round(estimated_seconds - constraints['max_seconds'], 1)),
                    'seconds_over_target': max(0, round(estimated_seconds - constraints['target_seconds'], 1))
                },
                'recommendations': self._generate_timing_recommendations(estimated_seconds, constraints, word_count),
                'test_mode': True,
                'api_usage': 0  # No API tokens used in test mode
            }
            
            status = "✅ OPTIMAL" if is_optimal else "⚠️ LONG" if is_within_limits else "❌ TOO LONG"
            logger.info(f"✅ Test: Timing analysis complete - {estimated_seconds:.1f}s ({status})")
            print(f"🧪 TEST: Timing analysis - {estimated_seconds:.1f}s ({status})")
            
            return timing_result
            
        except Exception as e:
            logger.error(f"❌ Test timing analysis error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    def _generate_timing_recommendations(self, estimated_seconds: float, constraints: Dict, word_count: int) -> List[str]:
        """Generate hardcoded timing recommendations"""
        
        recommendations = []
        
        if estimated_seconds > constraints['max_seconds']:
            recommendations.append(f"Text is {estimated_seconds - constraints['max_seconds']:.1f}s over limit - requires shortening")
            recommendations.append(f"Remove {max(1, int((word_count * 0.2)))} words to reach time limit")
            recommendations.append("Focus on key benefits and remove filler words")
        elif estimated_seconds > constraints['target_seconds']:
            recommendations.append(f"Text is {estimated_seconds - constraints['target_seconds']:.1f}s over target - consider shortening")
            recommendations.append("Could be more concise for better engagement")
        else:
            recommendations.append("Timing is optimal for voice narration")
            recommendations.append("Text length is perfect for this content type")
        
        # Content-specific recommendations
        if word_count < 5:
            recommendations.append("Text might be too short - consider adding key details")
        elif word_count > 50:
            recommendations.append("Consider breaking into shorter sentences for better flow")
        
        return recommendations
    
    async def optimize_text_for_timing(self, text: str, content_type: str, target_seconds: Optional[float] = None) -> Dict:
        """Optimize text timing with hardcoded improvements"""
        
        logger.info(f"🔧 Test: Optimizing text timing for {content_type}")
        print(f"🧪 TEST: Optimizing text for timing")
        
        try:
            await asyncio.sleep(0.5)
            
            # Get initial analysis
            initial_analysis = await self.analyze_text_timing(text, content_type)
            
            if not initial_analysis['success']:
                return initial_analysis
            
            constraints = self.timing_constraints.get(content_type, {'max_seconds': 10, 'target_seconds': 8})
            target_time = target_seconds or constraints['target_seconds']
            
            # If already optimal, return original
            if initial_analysis['validation']['is_optimal']:
                return {
                    'success': True,
                    'original_text': text,
                    'optimized_text': text,
                    'optimization_needed': False,
                    'initial_analysis': initial_analysis,
                    'final_analysis': initial_analysis,
                    'improvements': ['Text was already optimally timed'],
                    'test_mode': True,
                    'api_usage': 0
                }
            
            # Generate hardcoded optimized version
            optimized_text = self._generate_optimized_text(text, target_time, initial_analysis['analysis']['estimated_seconds'])
            
            # Analyze optimized version
            final_analysis = await self.analyze_text_timing(optimized_text, content_type)
            
            # Calculate improvements
            time_saved = initial_analysis['analysis']['estimated_seconds'] - final_analysis['analysis']['estimated_seconds']
            words_removed = initial_analysis['analysis']['word_count'] - final_analysis['analysis']['word_count']
            
            optimization_result = {
                'success': True,
                'original_text': text,
                'optimized_text': optimized_text,
                'optimization_needed': True,
                'initial_analysis': initial_analysis,
                'final_analysis': final_analysis,
                'improvements': [
                    f"Reduced timing by {time_saved:.1f} seconds",
                    f"Removed {words_removed} words while preserving meaning",
                    f"Now {'within optimal range' if final_analysis['validation']['is_optimal'] else 'within acceptable limits'}",
                    "Improved clarity and conciseness"
                ],
                'statistics': {
                    'time_saved_seconds': round(time_saved, 1),
                    'words_removed': words_removed,
                    'character_reduction': initial_analysis['analysis']['character_count'] - final_analysis['analysis']['character_count'],
                    'efficiency_gain': f"{(time_saved / initial_analysis['analysis']['estimated_seconds'] * 100):.1f}%"
                },
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Text optimized - saved {time_saved:.1f}s, removed {words_removed} words")
            print(f"🧪 TEST: Optimization complete - saved {time_saved:.1f}s")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"❌ Test optimization error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    def _generate_optimized_text(self, original_text: str, target_seconds: float, current_seconds: float) -> str:
        """Generate hardcoded optimized text"""
        
        # Calculate how much to reduce
        reduction_factor = target_seconds / current_seconds
        
        if reduction_factor >= 0.9:
            # Minor optimization - remove filler words
            optimized = original_text.replace(' really ', ' ').replace(' very ', ' ').replace(' quite ', ' ')
            optimized = optimized.replace(' absolutely ', ' ').replace(' extremely ', ' ')
        elif reduction_factor >= 0.7:
            # Moderate optimization - shorten sentences
            words = original_text.split()
            # Remove approximately 20-30% of words, keeping key terms
            keep_ratio = max(0.7, reduction_factor)
            words_to_keep = int(len(words) * keep_ratio)
            optimized = ' '.join(words[:words_to_keep])
        else:
            # Heavy optimization - major restructuring
            words = original_text.split()
            # Keep only the most essential words
            essential_words = []
            skip_words = {'the', 'a', 'an', 'and', 'or', 'but', 'with', 'for', 'to', 'of', 'in', 'on', 'at', 'by'}
            
            for word in words:
                if word.lower() not in skip_words or len(essential_words) < len(words) * 0.5:
                    essential_words.append(word)
            
            optimized = ' '.join(essential_words)
        
        # Clean up any double spaces
        optimized = ' '.join(optimized.split())
        
        # Ensure it's not too short
        if len(optimized) < len(original_text) * 0.3:
            optimized = original_text[:int(len(original_text) * 0.6)]
        
        return optimized.strip()
    
    async def batch_analyze_timing(self, content_batch: List[Dict]) -> Dict:
        """Analyze timing for multiple content pieces"""
        
        logger.info(f"📊 Test: Batch analyzing timing for {len(content_batch)} items")
        print(f"🧪 TEST: Batch timing analysis for {len(content_batch)} items")
        
        try:
            await asyncio.sleep(0.8)
            
            results = []
            total_time = 0
            items_over_limit = 0
            items_optimal = 0
            
            for i, content_item in enumerate(content_batch):
                text = content_item.get('text', '')
                content_type = content_item.get('type', 'unknown')
                
                analysis = await self.analyze_text_timing(text, content_type)
                results.append(analysis)
                
                if analysis['success']:
                    total_time += analysis['analysis']['estimated_seconds']
                    if not analysis['validation']['is_within_limits']:
                        items_over_limit += 1
                    if analysis['validation']['is_optimal']:
                        items_optimal += 1
            
            batch_result = {
                'success': True,
                'total_items': len(content_batch),
                'results': results,
                'summary': {
                    'total_estimated_time': round(total_time, 1),
                    'average_time_per_item': round(total_time / len(content_batch), 1) if content_batch else 0,
                    'items_optimal': items_optimal,
                    'items_over_limit': items_over_limit,
                    'items_acceptable': len(content_batch) - items_over_limit,
                    'optimization_needed': items_over_limit > 0
                },
                'recommendations': [
                    f"{items_optimal} items are optimally timed",
                    f"{items_over_limit} items need optimization" if items_over_limit > 0 else "All items within limits",
                    f"Total content duration: {total_time:.1f} seconds"
                ],
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Batch analysis complete - {items_optimal}/{len(content_batch)} optimal")
            print(f"🧪 TEST: Batch analysis complete - {items_optimal}/{len(content_batch)} optimal")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"❌ Test batch analysis error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    async def generate_timing_report(self, content_analysis: Dict) -> Dict:
        """Generate comprehensive timing report"""
        
        logger.info("📋 Test: Generating timing report")
        print("🧪 TEST: Generating timing report")
        
        try:
            await asyncio.sleep(0.4)
            
            report = {
                'success': True,
                'report_id': f"timing_report_{uuid.uuid4().hex[:8]}",
                'generated_at': datetime.now().isoformat(),
                'content_summary': content_analysis.get('summary', {}),
                'timing_analysis': {
                    'total_content_duration': content_analysis.get('summary', {}).get('total_estimated_time', 0),
                    'content_pieces': content_analysis.get('total_items', 0),
                    'optimal_pieces': content_analysis.get('summary', {}).get('items_optimal', 0),
                    'over_limit_pieces': content_analysis.get('summary', {}).get('items_over_limit', 0),
                    'average_duration': content_analysis.get('summary', {}).get('average_time_per_item', 0)
                },
                'recommendations': content_analysis.get('recommendations', []),
                'next_steps': [
                    "Optimize any content pieces over time limits",
                    "Review content structure for better flow",
                    "Consider voice narration speed adjustments",
                    "Test with actual voice generation to validate timing"
                ],
                'quality_score': {
                    'timing_score': 85,
                    'optimization_score': 92,
                    'overall_score': 88
                },
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"✅ Test: Timing report generated - Score: {report['quality_score']['overall_score']}/100")
            print(f"🧪 TEST: Timing report generated - Overall Score: {report['quality_score']['overall_score']}/100")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Test report generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }

# Test function
if __name__ == "__main__":
    async def test_voice_timing_optimizer():
        config = {}
        
        optimizer = TestVoiceTimingOptimizer(config)
        
        print("🧪 Testing Voice Timing Optimizer")
        print("=" * 50)
        
        # Test content
        test_content = [
            {
                'text': 'Discover the top 5 gaming headsets with incredible audio quality and comfort',
                'type': 'video_title'
            },
            {
                'text': 'Premium Gaming Headset with Crystal Clear Audio and Comfortable Design',
                'type': 'product_title'
            },
            {
                'text': 'Experience immersive gaming with our top-rated headset featuring 7.1 surround sound, noise cancellation, and a comfortable over-ear design perfect for long gaming sessions',
                'type': 'product_description'
            }
        ]
        
        # Test individual analysis
        single_result = await optimizer.analyze_text_timing(test_content[0]['text'], test_content[0]['type'])
        print(f"\n⏱️ Single Analysis: {'✅ SUCCESS' if single_result['success'] else '❌ FAILED'}")
        
        # Test optimization
        if single_result['success'] and not single_result['validation']['is_optimal']:
            opt_result = await optimizer.optimize_text_for_timing(test_content[0]['text'], test_content[0]['type'])
            print(f"🔧 Optimization: {'✅ SUCCESS' if opt_result['success'] else '❌ FAILED'}")
        
        # Test batch analysis
        batch_result = await optimizer.batch_analyze_timing(test_content)
        print(f"📊 Batch Analysis: {'✅ SUCCESS' if batch_result['success'] else '❌ FAILED'}")
        
        # Test report generation
        if batch_result['success']:
            report = await optimizer.generate_timing_report(batch_result)
            print(f"📋 Report Generation: {'✅ SUCCESS' if report['success'] else '❌ FAILED'}")
        
        print(f"\n🧪 Total API Usage: 0 tokens")
        
    asyncio.run(test_voice_timing_optimizer())