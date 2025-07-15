#!/usr/bin/env python3
"""
Check available titles in Airtable
"""

import asyncio
import json
import sys
sys.path.append('/home/claude-workflow')

from mcp_servers.airtable_server import AirtableMCPServer

async def check_titles():
    """Check available titles in Airtable"""
    
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize Airtable
    airtable = AirtableMCPServer(
        config['airtable_api_key'],
        config['airtable_base_id'],
        config['airtable_table_name']
    )
    
    print("📋 Checking available titles in Airtable...")
    
    # Get all records
    records = await airtable.get_all_records()
    
    print(f"Found {len(records)} records:")
    
    for i, record in enumerate(records, 1):
        fields = record.get('fields', {})
        title = fields.get('VideoTitle', 'No title')
        status = fields.get('Status', 'No status')
        
        print(f"{i}. {title}")
        print(f"   Status: {status}")
        print(f"   Record ID: {record.get('id')}")
        print()
    
    # Show titles that might work better
    print("🎯 Recommended titles for testing:")
    good_titles = []
    
    for record in records:
        fields = record.get('fields', {})
        title = fields.get('VideoTitle', '').lower()
        
        # Look for titles with common product categories
        if any(keyword in title for keyword in ['gaming', 'tech', 'headphones', 'laptop', 'car', 'phone', 'wireless']):
            good_titles.append((record.get('id'), fields.get('VideoTitle', '')))
    
    for record_id, title in good_titles[:5]:
        print(f"   ✅ {title} (ID: {record_id})")

if __name__ == "__main__":
    asyncio.run(check_titles())