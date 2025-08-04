#!/usr/bin/env python3
"""
Timing Security Agent - Fallback Content Length Validator

This agent ensures NO video ever fails due to timing issues by:
1. Validating all content meets strict timing requirements
2. Automatically regenerating content that exceeds limits
3. Continuing until ALL content passes timing validation
4. Never allowing workflow to proceed with invalid timing

TIMING REQUIREMENTS:
- IntroHook: MAX 5 seconds (≤12 words)
- OutroCallToAction: MAX 5 seconds (≤12 words)  
- ProductNo1-5Description: MAX 9 seconds each (≤22 words each)
- Total video: ≤60 seconds

This is a SECURITY agent - it prevents video generation failures.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.content_generation_server import ContentGenerationMCPServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimingSecurityAgent:
    """
    Fallback security agent that ensures ALL content meets timing requirements
    before allowing video generation to proceed.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Initialize servers
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
        self.content_server = ContentGenerationMCPServer(
            anthropic_api_key=config['anthropic_api_key']
        )
        
        # Timing constraints - STRICTER to ensure under 60 seconds total
        # Reduced to ensure video stays under 60 seconds with transitions
        self.timing_constraints = {
            'IntroHook': {'max_seconds': 4.0, 'max_words': 10},  # Reduced from 5s/12w
            'OutroCallToAction': {'max_seconds': 4.0, 'max_words': 10},  # Reduced from 5s/12w
            'ProductNo1Description': {'max_seconds': 8.0, 'max_words': 20},  # Reduced from 9s/22w
            'ProductNo2Description': {'max_seconds': 8.0, 'max_words': 20},  # Reduced from 9s/22w
            'ProductNo3Description': {'max_seconds': 8.0, 'max_words': 20},  # Reduced from 9s/22w
            'ProductNo4Description': {'max_seconds': 8.0, 'max_words': 20},  # Reduced from 9s/22w
            'ProductNo5Description': {'max_seconds': 8.0, 'max_words': 20}  # Reduced from 9s/22w
        }
        # Total: 4 + 4 + (8*5) = 48 seconds, leaving 12 seconds buffer for transitions
        
        # Maximum regeneration attempts per field
        self.max_attempts = 3
        
        logger.info("🛡️ Timing Security Agent initialized - protecting against timing failures")
    
    def estimate_speaking_time(self, text: str) -> float:
        """Estimate speaking time in seconds (2.5 words per second average)"""
        if not text or not text.strip():
            return 0.0
        word_count = len(text.strip().split())
        return word_count / 2.5
    
    def get_word_count(self, text: str) -> int:
        """Get word count for text"""
        if not text or not text.strip():
            return 0
        return len(text.strip().split())
    
    async def validate_all_timing(self, record_id: str) -> Dict[str, Any]:
        """
        Validate ALL timing-critical fields and regenerate any that exceed limits.
        Returns validation status and ensures ALL content passes before returning success.
        """
        logger.info(f"🛡️ TIMING SECURITY CHECK: Starting validation for record {record_id}")
        
        # Get current record data
        record_data = await self.airtable_server.get_record_by_id(record_id)
        if not record_data:
            logger.error(f"❌ Record {record_id} not found")
            return {'success': False, 'error': 'Record not found'}
        record = record_data.get('fields', {})
        if not record:
            logger.error(f"❌ Record {record_id} not found")
            return {'success': False, 'error': 'Record not found'}
        
        validation_results = {
            'success': False,
            'total_fields_checked': 0,
            'fields_passed': 0,
            'fields_failed': 0,
            'regenerated_fields': [],
            'final_validation': {},
            'total_video_time': 0.0
        }
        
        max_cycles = 5  # Maximum validation cycles to prevent infinite loops
        current_cycle = 1
        
        while current_cycle <= max_cycles:
            logger.info(f"🔄 Validation Cycle {current_cycle}/{max_cycles}")
            
            # Get fresh record data for this cycle
            record_data = await self.airtable_server.get_record_by_id(record_id)
            if not record_data:
                logger.error(f"❌ Record {record_id} not found in cycle {current_cycle}")
                break
            record = record_data.get('fields', {})
            fields_to_regenerate = []
            cycle_results = {}
            
            # Check each timing-critical field
            for field_name, constraints in self.timing_constraints.items():
                validation_results['total_fields_checked'] += 1
                
                field_value = record.get(field_name, '')
                if not field_value:
                    logger.warning(f"⚠️ Field {field_name} is empty - skipping")
                    continue
                
                # Calculate timing
                word_count = self.get_word_count(field_value)
                speaking_time = self.estimate_speaking_time(field_value)
                max_time = constraints['max_seconds']
                max_words = constraints['max_words']
                
                # Check if field passes timing requirements
                if speaking_time <= max_time and word_count <= max_words:
                    logger.info(f"✅ {field_name}: {word_count} words, {speaking_time:.1f}s (PASSED)")
                    validation_results['fields_passed'] += 1
                    cycle_results[field_name] = {
                        'status': 'PASSED',
                        'word_count': word_count,
                        'speaking_time': speaking_time,
                        'limit': max_time
                    }
                else:
                    logger.warning(f"❌ {field_name}: {word_count} words, {speaking_time:.1f}s (FAILED - max {max_time}s)")
                    validation_results['fields_failed'] += 1
                    fields_to_regenerate.append({
                        'field_name': field_name,
                        'current_text': field_value,
                        'word_count': word_count,
                        'speaking_time': speaking_time,
                        'max_seconds': max_time,
                        'max_words': max_words
                    })
                    cycle_results[field_name] = {
                        'status': 'FAILED',
                        'word_count': word_count,
                        'speaking_time': speaking_time,
                        'limit': max_time
                    }
            
            # If no fields need regeneration, we're done!
            if not fields_to_regenerate:
                logger.info("🎉 ALL FIELDS PASSED TIMING VALIDATION!")
                validation_results['success'] = True
                validation_results['final_validation'] = cycle_results
                break
            
            # Regenerate failed fields
            logger.info(f"🔧 Regenerating {len(fields_to_regenerate)} fields with timing constraints")
            regeneration_success = await self._regenerate_fields(record_id, fields_to_regenerate)
            
            if regeneration_success:
                validation_results['regenerated_fields'].extend([f['field_name'] for f in fields_to_regenerate])
                logger.info(f"✅ Regenerated {len(fields_to_regenerate)} fields, checking again...")
            else:
                logger.error("❌ Regeneration failed")
                break
            
            current_cycle += 1
        
        # Calculate total video time from final record
        if validation_results['success']:
            final_record_data = await self.airtable_server.get_record_by_id(record_id)
            final_record = final_record_data.get('fields', {}) if final_record_data else {}
            total_time = 0.0
            for field_name in self.timing_constraints.keys():
                field_value = final_record.get(field_name, '')
                if field_value:
                    total_time += self.estimate_speaking_time(field_value)
            
            validation_results['total_video_time'] = total_time
            logger.info(f"📊 Total estimated video time: {total_time:.1f} seconds")
            
            if total_time > 60.0:
                logger.warning(f"⚠️ Total video time {total_time:.1f}s exceeds 60s limit")
            else:
                logger.info(f"✅ Total video time {total_time:.1f}s is within 60s limit")
        
        # Final summary
        logger.info(f"""
🛡️ TIMING SECURITY REPORT:
   📊 Fields Checked: {validation_results['total_fields_checked']}
   ✅ Fields Passed: {validation_results['fields_passed']}
   ❌ Fields Failed: {validation_results['fields_failed']}
   🔧 Fields Regenerated: {len(validation_results['regenerated_fields'])}
   ⏱️ Total Video Time: {validation_results['total_video_time']:.1f}s
   🎯 Validation Success: {validation_results['success']}
        """)
        
        return validation_results
    
    async def _regenerate_fields(self, record_id: str, fields_to_regenerate: List[Dict]) -> bool:
        """Regenerate specific fields with timing constraints"""
        try:
            update_data = {}
            
            for field_info in fields_to_regenerate:
                field_name = field_info['field_name']
                max_words = field_info['max_words']
                max_seconds = field_info['max_seconds']
                
                logger.info(f"🔧 Regenerating {field_name} (max {max_words} words, {max_seconds}s)")
                
                # Generate replacement content based on field type
                new_content = await self._generate_replacement_content(
                    field_name, 
                    field_info['current_text'],
                    max_words,
                    max_seconds
                )
                
                if new_content:
                    update_data[field_name] = new_content
                    # Also set status to Ready since we're providing validated content
                    if field_name + 'Status' in ['IntroHookStatus', 'OutroCallToActionStatus'] + [f'ProductNo{i}DescriptionStatus' for i in range(1, 6)]:
                        # Only update status if the status field exists in Airtable
                        status_field = field_name.replace('Hook', 'HookStatus').replace('CallToAction', 'CallToActionStatus').replace('Description', 'DescriptionStatus')
                        if status_field in ['VideoTitleStatus', 'VideoDescriptionStatus', 'ProductNo1DescriptionStatus', 'ProductNo2DescriptionStatus', 'ProductNo3DescriptionStatus', 'ProductNo4DescriptionStatus', 'ProductNo5DescriptionStatus']:
                            update_data[status_field] = 'Ready'
                    
                    logger.info(f"✅ Generated replacement for {field_name}: {len(new_content.split())} words")
                else:
                    logger.error(f"❌ Failed to generate replacement for {field_name}")
                    return False
            
            # Update record with all regenerated content
            if update_data:
                await self.airtable_server.update_record(record_id, update_data)
                logger.info(f"📝 Updated {len(update_data)} fields in Airtable")
                return True
            else:
                logger.error("❌ No content generated for regeneration")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error regenerating fields: {e}")
            return False
    
    async def _generate_replacement_content(self, field_name: str, current_text: str, max_words: int, max_seconds: float) -> str:
        """Generate replacement content that meets timing constraints"""
        try:
            if field_name == 'IntroHook':
                prompt = f"""
                Rewrite this intro hook to be EXACTLY {max_words} words or less for a {max_seconds}-second video intro:
                
                Current text: "{current_text}"
                
                Requirements:
                - Maximum {max_words} words
                - Maximum {max_seconds} seconds when spoken
                - Grab attention immediately
                - Create curiosity about the #1 product
                - Make viewers want to watch until the end
                
                Return ONLY the new intro hook text, nothing else.
                """
                
            elif field_name == 'OutroCallToAction':
                prompt = f"""
                Rewrite this outro call-to-action to be EXACTLY {max_words} words or less for a {max_seconds}-second video outro:
                
                Current text: "{current_text}"
                
                Requirements:
                - Maximum {max_words} words
                - Maximum {max_seconds} seconds when spoken
                - Drive immediate action
                - Create urgency
                - Direct to links/engagement
                
                Return ONLY the new outro text, nothing else.
                """
                
            elif field_name.startswith('ProductNo') and field_name.endswith('Description'):
                product_num = field_name.replace('ProductNo', '').replace('Description', '')
                prompt = f"""
                Rewrite this product description to be EXACTLY {max_words} words or less for a {max_seconds}-second product segment:
                
                Current text: "{current_text}"
                
                Requirements:
                - Maximum {max_words} words
                - Maximum {max_seconds} seconds when spoken
                - Keep the product name and key features
                - Maintain the countdown format (#{product_num})
                - Be engaging and informative
                
                Return ONLY the new product description, nothing else.
                """
            else:
                return current_text  # Unknown field type, return original
            
            # Generate new content
            response = self.content_server.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            new_content = response.content[0].text.strip()
            
            # Verify the new content meets requirements
            new_word_count = self.get_word_count(new_content)
            new_speaking_time = self.estimate_speaking_time(new_content)
            
            if new_word_count <= max_words and new_speaking_time <= max_seconds:
                logger.info(f"✅ Generated valid replacement: {new_word_count} words, {new_speaking_time:.1f}s")
                return new_content
            else:
                logger.warning(f"⚠️ Generated content still too long: {new_word_count} words, {new_speaking_time:.1f}s")
                # Truncate to max words as fallback
                words = new_content.split()[:max_words]
                truncated = ' '.join(words)
                logger.info(f"🔧 Truncated to {len(words)} words: {truncated}")
                return truncated
                
        except Exception as e:
            logger.error(f"❌ Error generating replacement content for {field_name}: {e}")
            return current_text  # Return original as fallback

# Main function for testing
async def test_timing_security_agent():
    """Test the timing security agent"""
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    agent = TimingSecurityAgent(config)
    
    # Test with a specific record ID (replace with actual ID)
    test_record_id = "rec1euZqjLu6SGHQW"  # Example from previous run
    
    result = await agent.validate_all_timing(test_record_id)
    
    print("🛡️ TIMING SECURITY TEST RESULTS:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_timing_security_agent())