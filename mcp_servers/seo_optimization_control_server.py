#!/usr/bin/env python3
"""
SEO Optimization Control MCP Server
Manages SEO scoring, optimization validation, and platform-specific content quality control
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SEOOptimizationControlServer:
    """SEO optimization control and quality scoring for content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # SEO scoring weights
        self.keyword_density_weight = 0.25
        self.title_optimization_weight = 0.30
        self.content_quality_weight = 0.25
        self.platform_readiness_weight = 0.20
        
        # Platform character limits
        self.platform_limits = {
            'youtube': {'title': 60, 'description': 5000},
            'tiktok': {'title': 50, 'caption': 2200},
            'instagram': {'title': 55, 'caption': 2200},
            'wordpress': {'title': 60, 'meta_description': 160}
        }
    
    async def calculate_seo_score(self, 
                                content_data: Dict,
                                keywords: List[str],
                                platform_metadata: Dict) -> Dict[str, Any]:
        """Calculate comprehensive SEO score for content"""
        try:
            logger.info("🔍 Calculating SEO optimization score")
            
            # Score individual components
            keyword_score = await self._score_keyword_optimization(content_data, keywords)
            title_score = await self._score_title_optimization(content_data, platform_metadata)
            content_score = await self._score_content_quality(content_data)
            platform_score = await self._score_platform_readiness(platform_metadata)
            
            # Calculate weighted overall score
            overall_score = (
                keyword_score * self.keyword_density_weight +
                title_score * self.title_optimization_weight +
                content_score * self.content_quality_weight +
                platform_score * self.platform_readiness_weight
            )
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                keyword_score, title_score, content_score, platform_score
            )
            
            result = {
                'overall_seo_score': round(overall_score, 1),
                'component_scores': {
                    'keyword_optimization': round(keyword_score, 1),
                    'title_optimization': round(title_score, 1),
                    'content_quality': round(content_score, 1),
                    'platform_readiness': round(platform_score, 1)
                },
                'grade': self._get_seo_grade(overall_score),
                'recommendations': recommendations,
                'optimization_status': self._get_optimization_status(overall_score)
            }
            
            logger.info(f"✅ SEO Score: {overall_score:.1f}/100 ({result['grade']})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating SEO score: {e}")
            return {'overall_seo_score': 0, 'error': str(e)}
    
    async def _score_keyword_optimization(self, content_data: Dict, keywords: List[str]) -> float:
        """Score how well keywords are integrated into content"""
        if not keywords:
            return 50.0
        
        total_text = ""
        
        # Collect all text content
        if 'products' in content_data:
            for product in content_data['products']:
                total_text += f" {product.get('optimized_title', '')} {product.get('optimized_description', '')}"
        
        total_text += f" {content_data.get('intro_text', '')} {content_data.get('outro', '')}"
        total_text = total_text.lower()
        
        if not total_text.strip():
            return 0.0
        
        # Count keyword usage
        keyword_matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords[:10]:  # Check top 10 keywords
            if keyword.lower() in total_text:
                keyword_matches += 1
        
        # Calculate keyword density (aim for 2-5%)
        word_count = len(total_text.split())
        keyword_density = (keyword_matches / word_count) * 100 if word_count > 0 else 0
        
        # Score based on keyword usage and density
        usage_score = (keyword_matches / total_keywords) * 100 if total_keywords > 0 else 0
        
        # Optimal density is 2-5%
        if 2 <= keyword_density <= 5:
            density_score = 100
        elif keyword_density < 2:
            density_score = keyword_density * 50  # Penalize under-usage
        else:
            density_score = max(0, 100 - (keyword_density - 5) * 10)  # Penalize over-usage
        
        return (usage_score * 0.7 + density_score * 0.3)
    
    async def _score_title_optimization(self, content_data: Dict, platform_metadata: Dict) -> float:
        """Score title optimization across platforms"""
        scores = []
        
        for platform, metadata in platform_metadata.items():
            if not metadata or 'title' not in metadata:
                scores.append(0)
                continue
            
            title = metadata['title']
            platform_limit = self.platform_limits.get(platform, {}).get('title', 60)
            
            # Check character count
            char_score = 100 if len(title) <= platform_limit else max(0, 100 - (len(title) - platform_limit) * 2)
            
            # Check for engagement elements
            engagement_score = 0
            engagement_elements = ['!', '?', 'INSANE', 'SHOCKING', '🔥', '😱', 'TOP', 'BEST', '#']
            for element in engagement_elements:
                if element in title.upper():
                    engagement_score += 10
            engagement_score = min(100, engagement_score)
            
            # Check for numbers/rankings
            number_score = 50 if re.search(r'\d+', title) else 0
            
            platform_score = (char_score * 0.4 + engagement_score * 0.4 + number_score * 0.2)
            scores.append(platform_score)
        
        return sum(scores) / len(scores) if scores else 0
    
    async def _score_content_quality(self, content_data: Dict) -> float:
        """Score overall content quality"""
        quality_score = 0
        checks = 0
        
        # Check intro quality
        if 'intro_text' in content_data:
            intro = content_data['intro_text']
            intro_words = len(intro.split())
            
            if 10 <= intro_words <= 15:
                quality_score += 25
            elif intro_words > 0:
                quality_score += 15
            checks += 1
        
        # Check product descriptions quality
        if 'products' in content_data:
            product_scores = []
            for product in content_data['products']:
                desc = product.get('optimized_description', '')
                desc_words = len(desc.split())
                
                # Optimal length is 18-22 words
                if 18 <= desc_words <= 22:
                    product_scores.append(100)
                elif 15 <= desc_words <= 25:
                    product_scores.append(80)
                else:
                    product_scores.append(50)
            
            if product_scores:
                quality_score += (sum(product_scores) / len(product_scores)) * 0.5
                checks += 1
        
        # Check for call-to-action
        outro = content_data.get('outro', '')
        if outro and any(cta in outro.lower() for cta in ['comment', 'like', 'subscribe', 'link', 'check']):
            quality_score += 25
            checks += 1
        
        return quality_score / max(1, checks)
    
    async def _score_platform_readiness(self, platform_metadata: Dict) -> float:
        """Score how ready content is for each platform"""
        platform_scores = []
        
        for platform, metadata in platform_metadata.items():
            if not metadata:
                platform_scores.append(0)
                continue
            
            score = 0
            
            # Check required fields exist
            required_fields = {
                'youtube': ['title', 'description', 'tags'],
                'tiktok': ['title', 'caption', 'hashtags'],
                'instagram': ['title', 'caption', 'hashtags'],
                'wordpress': ['title', 'meta_description', 'focus_keywords']
            }
            
            platform_requirements = required_fields.get(platform, [])
            fields_present = sum(1 for field in platform_requirements if field in metadata)
            score += (fields_present / len(platform_requirements)) * 100 if platform_requirements else 100
            
            platform_scores.append(score)
        
        return sum(platform_scores) / len(platform_scores) if platform_scores else 0
    
    async def _generate_optimization_recommendations(self, 
                                                   keyword_score: float,
                                                   title_score: float,
                                                   content_score: float,
                                                   platform_score: float) -> List[str]:
        """Generate specific optimization recommendations"""
        recommendations = []
        
        if keyword_score < 70:
            recommendations.append("Improve keyword integration in product descriptions")
        
        if title_score < 70:
            recommendations.append("Optimize titles with more engaging elements and proper length")
        
        if content_score < 70:
            recommendations.append("Enhance content quality with better intro hooks and CTAs")
        
        if platform_score < 70:
            recommendations.append("Complete missing platform-specific metadata fields")
        
        if not recommendations:
            recommendations.append("Content is well-optimized across all metrics")
        
        return recommendations
    
    def _get_seo_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        else:
            return "F"
    
    def _get_optimization_status(self, score: float) -> str:
        """Get optimization status"""
        if score >= 80:
            return "Fully Optimized"
        elif score >= 60:
            return "Well Optimized"
        elif score >= 40:
            return "Needs Improvement"
        else:
            return "Requires Optimization"
    
    async def validate_platform_requirements(self, platform_metadata: Dict) -> Dict[str, Any]:
        """Validate that all platform requirements are met"""
        validation_results = {}
        
        for platform, metadata in platform_metadata.items():
            platform_validation = {
                'is_valid': True,
                'issues': [],
                'character_counts': {}
            }
            
            # Check character limits
            limits = self.platform_limits.get(platform, {})
            for field, limit in limits.items():
                if field in metadata:
                    content = metadata[field]
                    char_count = len(content)
                    platform_validation['character_counts'][field] = char_count
                    
                    if char_count > limit:
                        platform_validation['is_valid'] = False
                        platform_validation['issues'].append(
                            f"{field} exceeds {limit} character limit ({char_count} chars)"
                        )
            
            # Platform-specific validations
            if platform == 'youtube':
                if 'description' in metadata and len(metadata['description']) < 125:
                    platform_validation['issues'].append("YouTube description too short (min 125 chars)")
            
            elif platform == 'tiktok':
                if 'hashtags' in metadata and len(metadata.get('hashtags', [])) < 3:
                    platform_validation['issues'].append("TikTok needs at least 3 hashtags")
            
            elif platform == 'instagram':
                if 'hashtags' in metadata and len(metadata.get('hashtags', [])) > 30:
                    platform_validation['issues'].append("Instagram allows max 30 hashtags")
            
            validation_results[platform] = platform_validation
        
        return validation_results

# Test function
async def test_seo_optimization():
    config = {}
    server = SEOOptimizationControlServer(config)
    
    # Sample content data
    content_data = {
        'intro_text': 'These 5 gaming keyboards will blow your mind',
        'products': [
            {
                'optimized_title': 'Corsair K95 RGB Platinum',
                'optimized_description': 'Premium mechanical gaming keyboard with RGB lighting and cherry switches for ultimate performance'
            }
        ],
        'outro': 'Check the links in comments for the best deals'
    }
    
    keywords = ['gaming keyboard', 'mechanical', 'RGB', 'gaming', 'keyboard']
    
    platform_metadata = {
        'youtube': {
            'title': 'TOP 5 Gaming Keyboards That Will SHOCK You! 🎮',
            'description': 'Discover the most insane gaming keyboards that will transform your setup...',
            'tags': ['gaming', 'keyboard', 'tech']
        }
    }
    
    result = await server.calculate_seo_score(content_data, keywords, platform_metadata)
    print(f"SEO Score: {result['overall_seo_score']}/100")

if __name__ == "__main__":
    asyncio.run(test_seo_optimization())