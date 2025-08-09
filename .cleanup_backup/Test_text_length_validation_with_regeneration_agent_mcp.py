#!/usr/bin/env python3
"""
Test Text Length Validation with Regeneration Agent MCP
Hardcoded responses for testing - no API usage
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import sys
import uuid
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTextLengthValidationWithRegenerationAgentMCP:
    """Test Text Length Validation Agent with hardcoded responses"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Text validation constraints (same as production)
        self.validation_constraints = {
            'VideoTitle': {'max_length': 100, 'optimal_length': 70, 'min_length': 20},
            'VideoDescription': {'max_length': 200, 'optimal_length': 150, 'min_length': 50},
            'ProductNo1Title': {'max_length': 60, 'optimal_length': 45, 'min_length': 15},
            'ProductNo1Description': {'max_length': 100, 'optimal_length': 80, 'min_length': 30},
            'ProductNo2Title': {'max_length': 60, 'optimal_length': 45, 'min_length': 15},
            'ProductNo2Description': {'max_length': 100, 'optimal_length': 80, 'min_length': 30},
            'ProductNo3Title': {'max_length': 60, 'optimal_length': 45, 'min_length': 15},
            'ProductNo3Description': {'max_length': 100, 'optimal_length': 80, 'min_length': 30},
            'ProductNo4Title': {'max_length': 60, 'optimal_length': 45, 'min_length': 15},
            'ProductNo4Description': {'max_length': 100, 'optimal_length': 80, 'min_length': 30},
            'ProductNo5Title': {'max_length': 60, 'optimal_length': 45, 'min_length': 15},
            'ProductNo5Description': {'max_length': 100, 'optimal_length': 80, 'min_length': 30}
        }
        
        print("🧪 TEST MODE: Text Length Validation Agent using hardcoded responses")
        logger.info("🧪 Test Text Length Validation Agent initialized")
    
    async def validate_text_lengths(self, record_data: Dict) -> Dict:
        """Validate text lengths with hardcoded results"""
        
        logger.info(f"📏 Test: Validating text lengths for record")
        print(f"🧪 TEST: Validating text lengths")
        print(f"   Fields to validate: {len(self.validation_constraints)}")
        
        try:
            await asyncio.sleep(1.0)
            
            validation_results = {}
            valid_fields = 0
            invalid_fields = []
            
            for field_name, constraints in self.validation_constraints.items():
                # Get text from record data or generate sample text
                text = record_data.get(field_name, self._generate_sample_text(field_name))
                text_length = len(text)
                
                # Determine validation status based on constraints
                is_valid = constraints['min_length'] <= text_length <= constraints['max_length']
                is_optimal = text_length <= constraints['optimal_length']
                
                if is_valid:
                    valid_fields += 1
                else:
                    invalid_fields.append(field_name)
                
                validation_results[field_name] = {
                    'text': text,
                    'length': text_length,
                    'constraints': constraints,
                    'is_valid': is_valid,
                    'is_optimal': is_optimal,
                    'status': 'valid' if is_valid else 'invalid',
                    'severity': 'optimal' if is_optimal else 'acceptable' if is_valid else 'requires_fix',
                    'characters_over': max(0, text_length - constraints['max_length']),
                    'characters_under': max(0, constraints['min_length'] - text_length),
                    'recommendations': self._generate_recommendations(text_length, constraints)
                }
            
            # Overall validation summary
            total_fields = len(self.validation_constraints)
            validation_summary = {
                'success': True,
                'total_fields': total_fields,
                'valid_fields': valid_fields,
                'invalid_fields': len(invalid_fields),
                'validation_rate': f"{(valid_fields/total_fields*100):.1f}%",
                'fields_requiring_regeneration': invalid_fields,
                'overall_status': 'all_valid' if valid_fields == total_fields else 'needs_regeneration',
                'validation_results': validation_results,
                'processing_time': '1.0s',
                'validation_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Test: Text validation complete - {valid_fields}/{total_fields} valid")
            print(f"🧪 TEST: Text validation SUCCESS")
            print(f"   Valid Fields: {valid_fields}/{total_fields}")
            print(f"   Invalid Fields: {len(invalid_fields)}")
            
            return validation_summary
            
        except Exception as e:
            logger.error(f"❌ Test text validation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    def _generate_sample_text(self, field_name: str) -> str:
        """Generate sample text for testing"""
        if 'Title' in field_name:
            if 'Video' in field_name:
                return "Top 5 Gaming Headsets with THOUSANDS of 5-Star Reviews (2025 Amazon Finds)"
            else:
                return "Premium Gaming Headset with Crystal Clear Audio"
        else:
            if 'Video' in field_name:
                return "Discover the best gaming headsets on Amazon with real customer reviews, ratings, and honest recommendations from our expert team."
            else:
                return "Experience immersive gaming with 7.1 surround sound, noise cancellation, and comfortable design."
    
    def _generate_recommendations(self, text_length: int, constraints: Dict) -> List[str]:
        """Generate recommendations based on text length"""
        recommendations = []
        
        if text_length > constraints['max_length']:
            over_by = text_length - constraints['max_length']
            recommendations.append(f"Text is {over_by} characters too long - needs shortening")
            recommendations.append(f"Remove approximately {over_by} characters to meet requirements")
            recommendations.append("Focus on key benefits and remove filler words")
        elif text_length < constraints['min_length']:
            under_by = constraints['min_length'] - text_length
            recommendations.append(f"Text is {under_by} characters too short - needs expansion")
            recommendations.append("Add more descriptive details or key features")
            recommendations.append("Include relevant keywords for better SEO")
        elif text_length > constraints['optimal_length']:
            over_optimal = text_length - constraints['optimal_length']
            recommendations.append(f"Text is {over_optimal} characters over optimal length")
            recommendations.append("Consider shortening for better readability")
        else:
            recommendations.append("Text length is optimal")
            recommendations.append("No changes needed")
        
        return recommendations
    
    async def regenerate_invalid_texts(self, 
                                     invalid_fields: List[str], 
                                     original_data: Dict,
                                     context_data: Dict = {}) -> Dict:
        """Regenerate invalid texts with hardcoded improvements"""
        
        logger.info(f"🔄 Test: Regenerating {len(invalid_fields)} invalid text fields")
        print(f"🧪 TEST: Regenerating invalid texts")
        print(f"   Fields to regenerate: {', '.join(invalid_fields[:3])}{'...' if len(invalid_fields) > 3 else ''}")
        
        try:
            # Simulate regeneration processing time
            processing_time = 2.0 + (len(invalid_fields) * 0.5)
            await asyncio.sleep(processing_time)
            
            regenerated_texts = {}
            regeneration_details = {}
            
            for field_name in invalid_fields:
                original_text = original_data.get(field_name, '')
                constraints = self.validation_constraints.get(field_name, {})
                
                # Generate improved text based on field type and constraints
                regenerated_text = self._generate_improved_text(
                    field_name, 
                    original_text, 
                    constraints,
                    context_data
                )
                
                regenerated_texts[field_name] = regenerated_text
                
                # Track regeneration details
                regeneration_details[field_name] = {
                    'original_text': original_text,
                    'original_length': len(original_text),
                    'regenerated_text': regenerated_text,
                    'regenerated_length': len(regenerated_text),
                    'improvement_type': self._determine_improvement_type(original_text, regenerated_text, constraints),
                    'constraints_met': self._check_constraints_met(regenerated_text, constraints),
                    'quality_improvements': [
                        'Better keyword optimization',
                        'Improved readability',
                        'Enhanced engagement potential',
                        'Optimal length achieved'
                    ]
                }
            
            regeneration_result = {
                'success': True,
                'fields_regenerated': len(invalid_fields),
                'regenerated_texts': regenerated_texts,
                'regeneration_details': regeneration_details,
                'processing_summary': {
                    'processing_time': f"{processing_time:.1f}s",
                    'improvement_rate': '100%',
                    'average_quality_score': 92,
                    'constraints_compliance': '100%',
                    'seo_optimization': 'Enhanced'
                },
                'quality_metrics': {
                    'readability_improvement': '23%',
                    'engagement_potential': 'High',
                    'keyword_density': 'Optimized',
                    'length_optimization': 'Perfect',
                    'brand_consistency': 'Maintained'
                },
                'validation_status': {
                    'all_fields_valid': True,
                    'constraints_met': True,
                    'ready_for_production': True,
                    'quality_assured': True
                },
                'test_mode': True,
                'api_usage': 0  # No API tokens used in test mode
            }
            
            logger.info(f"✅ Test: Regenerated {len(invalid_fields)} texts successfully")
            print(f"🧪 TEST: Text regeneration SUCCESS")
            print(f"   Fields regenerated: {len(invalid_fields)}")
            print(f"   Processing time: {processing_time:.1f}s")
            print(f"   Quality score: {regeneration_result['processing_summary']['average_quality_score']}/100")
            
            return regeneration_result
            
        except Exception as e:
            logger.error(f"❌ Test text regeneration error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }
    
    def _generate_improved_text(self, field_name: str, original_text: str, constraints: Dict, context: Dict) -> str:
        """Generate improved text that meets constraints"""
        target_length = constraints.get('optimal_length', constraints.get('max_length', 50))
        
        if 'VideoTitle' in field_name:
            return "⭐ Top 5 Gaming Headsets with THOUSANDS of 5-Star Reviews (2025 Amazon)"[:target_length]
        elif 'VideoDescription' in field_name:
            return "Discover the top-rated gaming headsets on Amazon with real customer reviews, expert analysis, and direct purchase links. Updated for 2025."[:target_length]
        elif 'Title' in field_name:
            product_num = field_name.replace('ProductNo', '').replace('Title', '')
            return f"Premium Gaming Headset #{product_num} - Crystal Clear Audio & Comfort"[:target_length]
        else:  # Description fields
            product_num = field_name.replace('ProductNo', '').replace('Description', '')
            return f"Experience immersive gaming with Product #{product_num} featuring advanced audio technology and ergonomic design for extended use."[:target_length]
    
    def _determine_improvement_type(self, original: str, regenerated: str, constraints: Dict) -> str:
        """Determine the type of improvement made"""
        original_len = len(original)
        regenerated_len = len(regenerated)
        
        if original_len > constraints.get('max_length', 100):
            return 'length_reduction'
        elif original_len < constraints.get('min_length', 10):
            return 'length_expansion'
        else:
            return 'quality_enhancement'
    
    def _check_constraints_met(self, text: str, constraints: Dict) -> bool:
        """Check if regenerated text meets all constraints"""
        text_length = len(text)
        return (constraints.get('min_length', 0) <= text_length <= constraints.get('max_length', 1000))
    
    async def complete_validation_and_regeneration_workflow(self, record_data: Dict) -> Dict:
        """Complete validation and regeneration workflow"""
        
        logger.info("🚀 Test: Starting complete validation and regeneration workflow")
        print("🧪 TEST: Complete validation and regeneration workflow starting")
        
        try:
            workflow_start = datetime.now()
            
            # Step 1: Validate all text lengths
            print("   Step 1: Validating text lengths...")
            validation_result = await self.validate_text_lengths(record_data)
            
            # Step 2: Regenerate invalid texts if needed
            regeneration_result = {'success': True, 'fields_regenerated': 0}
            if not validation_result.get('overall_status') == 'all_valid':
                invalid_fields = validation_result.get('fields_requiring_regeneration', [])
                if invalid_fields:
                    print(f"   Step 2: Regenerating {len(invalid_fields)} invalid texts...")
                    regeneration_result = await self.regenerate_invalid_texts(
                        invalid_fields, record_data, {'category': 'Gaming', 'target_audience': 'Gamers'}
                    )
                else:
                    print("   Step 2: No regeneration needed - all texts valid")
            else:
                print("   Step 2: Skipping regeneration - all texts already valid")
            
            # Step 3: Final validation of regenerated texts
            final_validation = {'success': True, 'all_valid': True}
            if regeneration_result.get('fields_regenerated', 0) > 0:
                print("   Step 3: Final validation of regenerated texts...")
                # Simulate final validation
                await asyncio.sleep(0.5)
                final_validation = {
                    'success': True,
                    'all_valid': True,
                    'validation_passed': True,
                    'ready_for_production': True
                }
            else:
                print("   Step 3: Using original validation results")
                final_validation = validation_result
            
            workflow_end = datetime.now()
            total_time = (workflow_end - workflow_start).total_seconds()
            
            # Compile complete workflow result
            complete_result = {
                'success': True,
                'workflow_id': f'text_validation_{uuid.uuid4().hex[:8]}',
                'workflow_steps': {
                    'initial_validation': validation_result,
                    'text_regeneration': regeneration_result,
                    'final_validation': final_validation
                },
                'workflow_summary': {
                    'total_time': f'{total_time:.1f}s',
                    'steps_completed': 3,
                    'initial_valid_fields': validation_result.get('valid_fields', 0),
                    'fields_regenerated': regeneration_result.get('fields_regenerated', 0),
                    'final_valid_fields': validation_result.get('total_fields', 12),
                    'success_rate': '100%'
                },
                'final_status': {
                    'all_texts_valid': True,
                    'ready_for_video_generation': True,
                    'quality_score': 94,
                    'seo_optimized': True,
                    'constraints_compliant': True
                },
                'performance_metrics': {
                    'validation_speed': f"{validation_result.get('total_fields', 12) / total_time:.1f} fields/second",
                    'regeneration_efficiency': '100%',
                    'quality_improvement': '18%',
                    'automation_level': 'Full'
                },
                'recommendations': [
                    'All texts are now optimally sized for video generation',
                    'Regenerated texts maintain brand consistency',
                    'SEO optimization has been enhanced',
                    'Ready to proceed with video creation workflow'
                ],
                'test_mode': True,
                'api_usage': 0
            }
            
            logger.info(f"🎉 Test: Complete workflow finished successfully in {total_time:.1f}s")
            print(f"🧪 TEST: Complete workflow SUCCESS")
            print(f"   Total Time: {total_time:.1f}s")
            print(f"   Fields Regenerated: {regeneration_result.get('fields_regenerated', 0)}")
            print(f"   Final Quality Score: {complete_result['final_status']['quality_score']}/100")
            
            return complete_result
            
        except Exception as e:
            logger.error(f"❌ Test complete workflow error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'test_mode': True
            }

async def test_run_text_validation_with_regeneration(record_data: Dict, config: Dict) -> Dict:
    """Test function expected by Test_workflow_runner.py"""
    print("🧪 TEST: test_run_text_validation_with_regeneration called")
    
    # Initialize test agent
    config = {
        'anthropic_api_key': 'test-api-key'
    }
    agent = TestTextLengthValidationWithRegenerationAgentMCP(config)
    
    # Run complete validation and regeneration workflow
    result = await agent.complete_validation_and_regeneration_workflow(record_data)
    
    # Return success response with updated_record
    updated_record = record_data.copy()
    updated_record['text_validation_completed'] = True
    updated_record['all_texts_valid'] = result['final_status']['all_texts_valid']
    updated_record['quality_score'] = result['final_status']['quality_score']
    
    # Mark all status fields as "Ready" since this is test mode
    status_fields = [
        'VideoTitleStatus', 'VideoDescriptionStatus',
        'ProductNo1TitleStatus', 'ProductNo1DescriptionStatus',
        'ProductNo2TitleStatus', 'ProductNo2DescriptionStatus',
        'ProductNo3TitleStatus', 'ProductNo3DescriptionStatus',
        'ProductNo4TitleStatus', 'ProductNo4DescriptionStatus',
        'ProductNo5TitleStatus', 'ProductNo5DescriptionStatus'
    ]
    
    for status_field in status_fields:
        updated_record[status_field] = 'Ready'
    
    return {
        'success': True,
        'updated_record': updated_record,
        'fields_processed': 12,
        'fields_regenerated': result['workflow_summary']['fields_regenerated'],
        'quality_score': result['final_status']['quality_score'],
        'ready_for_video': result['final_status']['ready_for_video_generation'],
        'test_mode': True,
        'api_usage': 0
    }

# Test function
if __name__ == "__main__":
    async def test_text_validation_agent():
        config = {
            'anthropic_api_key': 'test-api-key'
        }
        
        agent = TestTextLengthValidationWithRegenerationAgentMCP(config)
        
        # Test record data with some invalid lengths
        test_record_data = {
            'VideoTitle': 'This is an extremely long video title that definitely exceeds the maximum character limit for video titles and needs to be shortened significantly to meet the requirements',  # Too long
            'VideoDescription': 'Short desc',  # Too short
            'ProductNo1Title': 'Perfect Length Gaming Headset Title',  # Good length
            'ProductNo1Description': 'This gaming headset description is perfectly sized and meets all the length requirements for optimal display.',  # Good length
            'ProductNo2Title': 'Way too long product title that exceeds the maximum character limit',  # Too long
            'ProductNo2Description': 'Short',  # Too short
        }
        
        print("🧪 Testing Text Length Validation Agent")
        print("=" * 50)
        
        # Test complete workflow
        result = await agent.complete_validation_and_regeneration_workflow(test_record_data)
        
        print(f"\n🚀 Complete Workflow: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        
        if result['success']:
            print(f"   Total Time: {result['workflow_summary']['total_time']}")
            print(f"   Fields Regenerated: {result['workflow_summary']['fields_regenerated']}")
            print(f"   Final Quality Score: {result['final_status']['quality_score']}/100")
            print(f"   Ready for Video: {result['final_status']['ready_for_video_generation']}")
        
        print(f"\n🧪 Total API Usage: 0 tokens")
        
    asyncio.run(test_text_validation_agent())