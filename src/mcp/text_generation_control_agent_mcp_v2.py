#!/usr/bin/env python3
"""
Text Generation Control Agent MCP V2
Controls quality and automatically triggers regeneration until valid
"""

import asyncio
import json
import logging
from typing import Dict, List
from pathlib import Path
import sys
import re

sys.path.append(str(Path(__file__).parent.parent.parent))

from mcp_servers.text_generation_control_server import TextGenerationControlMCPServer
from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.content_generation_server import ContentGenerationMCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextGenerationControlAgentMCP:
    """Agent with automatic regeneration loop"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.control_server = TextGenerationControlMCPServer(config)
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        self.content_server = ContentGenerationMCPServer(
            anthropic_api_key=config['anthropic_api_key']
        )
        
    async def control_validate_and_regenerate(self, record_id: str, max_attempts: int = 3) -> Dict:
        """
        Control, validate, and automatically regenerate until all products are valid
        """
        logger.info(f"🎮 Text Control Agent: Starting validation loop for record {record_id}")
        
        attempt = 0
        all_valid = False
        
        while attempt < max_attempts and not all_valid:
            attempt += 1
            logger.info(f"📝 Attempt {attempt}/{max_attempts}")
            
            # Get current record
            record = await self.airtable_server.get_record_by_id(record_id)
            if not record:
                return {'success': False, 'error': 'Record not found'}
            
            # Extract data for validation
            keywords = record['fields'].get('KeyWords', '').split(',')
            keywords = [k.strip() for k in keywords if k.strip()]
            category = record['fields'].get('Category', 'General')
            title = record['fields'].get('Title', '')
            
            # Extract products
            products = []
            for i in range(1, 6):
                prod_title = record['fields'].get(f'ProductNo{i}Title', '')
                prod_desc = record['fields'].get(f'ProductNo{i}Description', '')
                
                if prod_title and prod_desc:
                    products.append({
                        'number': i,
                        'title': prod_title,
                        'description': prod_desc
                    })
            
            # Validate
            validation_result = await self.control_server.check_countdown_products(
                products, keywords, category
            )
            
            if validation_result['all_valid']:
                all_valid = True
                logger.info("✅ All products passed validation!")
                
                await self.airtable_server.update_record(record_id, {
                    'TextControlStatus': 'Validated',
                    'GenerationAttempts': attempt
                })
                
                return {
                    'success': True,
                    'all_valid': True,
                    'attempts': attempt,
                    'validation_results': validation_result
                }
            
            # If not valid and we have attempts left, regenerate
            if attempt < max_attempts:
                logger.warning(f"❌ {len(validation_result['products_needing_regeneration'])} products need regeneration")
                
                # Regenerate invalid products
                await self._regenerate_invalid_products(
                    record_id,
                    validation_result['products_needing_regeneration'],
                    keywords,
                    category,
                    title
                )
                
                # Wait a bit before next validation
                await asyncio.sleep(2)
        
        # Max attempts reached
        await self.airtable_server.update_record(record_id, {
            'TextControlStatus': 'Failed',
            'GenerationAttempts': attempt,
            'ValidationIssues': json.dumps(validation_result['products_needing_regeneration'])
        })
        
        return {
            'success': False,
            'all_valid': False,
            'attempts': attempt,
            'validation_results': validation_result,
            'error': 'Max regeneration attempts reached'
        }
    
    async def _regenerate_invalid_products(self,
                                         record_id: str,
                                         invalid_products: List[Dict],
                                         keywords: List[str],
                                         category: str,
                                         main_title: str) -> None:
        """
        Actually regenerate the invalid products
        """
        update_fields = {}
        
        for product in invalid_products:
            product_num = product['product_number']
            instructions = product['regeneration_instructions']
            
            logger.info(f"🔄 Regenerating Product #{product_num}")
            
            # Create specific prompt for regeneration
            prompt = f"""Regenerate Product #{product_num} for "{main_title}"

Current issues:
{chr(10).join(product['issues'])}

Requirements:
{chr(10).join(instructions)}

Keywords to use: {', '.join(keywords[:5])}
Category: {category}

Generate a product with:
- Title: 4-8 words, specific brand/model
- Description: 15-18 words
- Must be readable in 9 seconds total
- Use at least 2 keywords naturally

Format:
Title: [Your title]
Description: [Your description]"""
            
            # Call content generation for this specific product
            response = await self.content_server.generate_single_product(prompt)
            
            # Parse response and update fields
            if response:
                title_match = re.search(r'Title:\s*(.+)', response)
                desc_match = re.search(r'Description:\s*(.+)', response)
                
                if title_match and desc_match:
                    update_fields[f'ProductNo{product_num}Title'] = title_match.group(1).strip()
                    update_fields[f'ProductNo{product_num}Description'] = desc_match.group(1).strip()
        
        # Update Airtable with regenerated products
        if update_fields:
            await self.airtable_server.update_record(record_id, update_fields)
            logger.info(f"✅ Updated {len(update_fields)//2} products in Airtable")


# Integration function for workflow
async def run_text_control_with_regeneration(config: Dict, record_id: str) -> Dict:
    """Run text control with automatic regeneration"""
    agent = TextGenerationControlAgentMCP(config)
    return await agent.control_validate_and_regenerate(record_id)


if __name__ == "__main__":
    print("Text Generation Control Agent V2 created")
    print("This agent validates and automatically regenerates invalid products")
