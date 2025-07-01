#!/usr/bin/env python3
"""
Control Keywords Agent MCP
Handles keyword checking and generation logic based on your workflow diagram
"""

import asyncio
import json
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

# Add the project root to Python path
sys.path.append('/app')
sys.path.append('/home/claude-workflow')

# Import your existing servers
from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.content_generation_server import ContentGenerationMCPServer

class ControlKeywordsAgentMCP:
    """Controls the keyword generation workflow logic"""
    
    def __init__(self, config: dict):
        self.config = config
        
        # Initialize your existing MCP servers
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
        self.content_server = ContentGenerationMCPServer(
            anthropic_api_key=config['anthropic_api_key']
        )
    
    async def check_and_process_keywords(self, record_id: str) -> Dict:
        """
        Main entry point - checks if keywords exist and processes accordingly
        This implements the green box logic from your diagram
        """
        try:
            print(f"🔍 Checking keywords for record: {record_id}")
            
            # Get record from Airtable
            record = await self.airtable_server.get_record_by_id(record_id)
            
            if not record:
                return {
                    'status': 'error',
                    'error': f'Record {record_id} not found',
                    'next_action': 'skip'
                }
            
            # Check if keywords exist
            existing_keywords = record.get('SEO Keywords', [])
            
            if existing_keywords and len(existing_keywords) > 0:
                print(f"✅ Keywords already exist: {existing_keywords[:3]}...")
                return {
                    'status': 'keywords_exist',
                    'keywords': existing_keywords,
                    'needs_generation': False,
                    'next_action': 'proceed_to_content_generation',
                    'record': record
                }
            
            # No keywords - need to generate
            print(f"❌ No keywords found, generating...")
            
            # Extract title and category
            title = record.get('Title', '')
            category = record.get('Category', 'General')
            
            if not title:
                return {
                    'status': 'error',
                    'error': 'No title found in record',
                    'next_action': 'skip'
                }
            
            # Generate keywords using your existing content server
            keywords = await self.content_server.generate_seo_keywords(title, category)
            
            # Save keywords to Airtable
            print(f"💾 Saving {len(keywords)} keywords to Airtable...")
            await self.airtable_server.update_record(
                record_id,
                {'SEO Keywords': keywords}
            )
            
            # Update record with keywords for return
            record['SEO Keywords'] = keywords
            
            return {
                'status': 'keywords_generated',
                'keywords': keywords,
                'needs_generation': True,
                'next_action': 'proceed_to_content_generation',
                'record': record
            }
            
        except Exception as e:
            print(f"❌ Error in keyword processing: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'next_action': 'retry_or_skip'
            }
    
    async def process_category_batch(self, category: str) -> Dict:
        """
        Process all records in a specific category
        Implements the "Send next Product Category" logic from diagram
        """
        print(f"🔄 Processing category batch: {category}")
        
        try:
            # Get all records for this category
            all_records = await self.airtable_server.get_all_records()
            
            # Filter by category and missing keywords
            records_to_process = [
                r for r in all_records 
                if r.get('Category') == category 
                and not r.get('SEO Keywords')
            ]
            
            results = {
                'category': category,
                'total_records': len(records_to_process),
                'processed': 0,
                'generated': 0,
                'errors': []
            }
            
            print(f"📊 Found {len(records_to_process)} records without keywords in {category}")
            
            for record in records_to_process:
                try:
                    record_id = record.get('id', '')
                    result = await self.check_and_process_keywords(record_id)
                    
                    results['processed'] += 1
                    
                    if result.get('needs_generation'):
                        results['generated'] += 1
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(1)
                        
                except Exception as e:
                    print(f"❌ Error processing record {record.get('id')}: {e}")
                    results['errors'].append({
                        'record_id': record.get('id'),
                        'error': str(e)
                    })
            
            # Determine next category based on your workflow
            next_category = await self._get_next_category(category)
            results['next_category'] = next_category
            
            print(f"✅ Category {category} complete. Generated keywords for {results['generated']} records")
            if next_category:
                print(f"➡️  Next category: {next_category}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing category batch: {e}")
            return {
                'category': category,
                'status': 'error',
                'error': str(e)
            }
    
    async def _get_next_category(self, current_category: str) -> Optional[str]:
        """
        Determine the next category to process
        Based on your specific category order
        """
        # Define your category processing order
        category_order = [
            "Electronics",
            "Fashion",
            "Home & Garden",
            "Beauty",
            "Sports & Outdoors",
            "Toys & Games",
            "Food & Beverage",
            "Other"
        ]
        
        try:
            current_index = category_order.index(current_category)
            if current_index < len(category_order) - 1:
                return category_order[current_index + 1]
        except ValueError:
            # Current category not in list
            pass
        
        return None
    
    async def get_records_without_keywords(self) -> List[Dict]:
        """Get all records that don't have keywords yet"""
        all_records = await self.airtable_server.get_all_records()
        return [
            r for r in all_records 
            if not r.get('SEO Keywords') and r.get('Title')
        ]
    
    async def process_all_pending_keywords(self) -> Dict:
        """Process all records without keywords across all categories"""
        print("🚀 Starting bulk keyword generation for all pending records")
        
        records = await self.get_records_without_keywords()
        
        results = {
            'total_records': len(records),
            'processed': 0,
            'generated': 0,
            'errors': []
        }
        
        print(f"📊 Found {len(records)} records without keywords")
        
        for record in records:
            try:
                record_id = record.get('id', '')
                result = await self.check_and_process_keywords(record_id)
                
                results['processed'] += 1
                
                if result.get('needs_generation'):
                    results['generated'] += 1
                
                # Progress update every 10 records
                if results['processed'] % 10 == 0:
                    print(f"Progress: {results['processed']}/{results['total_records']}")
                
                # Rate limiting
                await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                results['errors'].append({
                    'record_id': record.get('id'),
                    'error': str(e)
                })
        
        print(f"✅ Bulk processing complete!")
        print(f"   - Processed: {results['processed']}")
        print(f"   - Generated: {results['generated']}")
        print(f"   - Errors: {len(results['errors'])}")
        
        return results


# Test function
async def test_keywords_agent():
    """Test the Keywords Agent"""
    # Load configuration
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    agent = ControlKeywordsAgentMCP(config)
    
    # Test 1: Check a single record
    print("\n🧪 Test 1: Checking single record")
    # You'll need to replace with an actual record ID from your Airtable
    # result = await agent.check_and_process_keywords("rec...")
    
    # Test 2: Get records without keywords
    print("\n🧪 Test 2: Finding records without keywords")
    pending = await agent.get_records_without_keywords()
    print(f"Found {len(pending)} records without keywords")
    
    # Test 3: Process a category
    if pending:
        categories = list(set(r.get('Category', 'Other') for r in pending))
        if categories:
            print(f"\n🧪 Test 3: Processing category '{categories[0]}'")
            result = await agent.process_category_batch(categories[0])
            print(f"Results: {result}")


if __name__ == "__main__":
    asyncio.run(test_keywords_agent())
