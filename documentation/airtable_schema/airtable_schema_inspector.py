#!/usr/bin/env python3
"""
Airtable Schema Inspector - Uses Airtable Metadata API to get complete schema
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Any

class AirtableSchemaInspector:
    def __init__(self, config_path: str = 'config/api_keys.json'):
        """Initialize the Airtable Schema Inspector"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.api_key = config.get('airtable_api_key')
        self.base_id = config.get('airtable_base_id')
        self.table_name = config.get('airtable_table_name', 'Content')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def get_base_schema(self) -> Dict[str, Any]:
        """Get the complete base schema using Airtable Metadata API"""
        # Airtable Metadata API endpoint
        url = f"https://api.airtable.com/v0/meta/bases/{self.base_id}/tables"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 404:
                    print("⚠️ Metadata API not available or base not found")
                    print("Note: Metadata API requires specific permissions")
                    return {}
                else:
                    print(f"❌ Error {response.status}: {await response.text()}")
                    return {}
    
    async def get_table_fields_from_schema(self, table_name: str = None) -> List[Dict]:
        """Extract fields for a specific table from the schema"""
        if not table_name:
            table_name = self.table_name
            
        schema = await self.get_base_schema()
        if not schema:
            return []
        
        # Find the specific table
        for table in schema.get('tables', []):
            if table.get('name') == table_name:
                return table.get('fields', [])
        
        return []
    
    async def get_field_info_via_records(self) -> Dict[str, Any]:
        """Alternative method: Infer field types from actual record data"""
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        
        async with aiohttp.ClientSession() as session:
            # Get a good sample of records to infer types
            async with session.get(url, headers=self.headers, params={'maxRecords': 100}) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._infer_field_types(data.get('records', []))
                return {}
    
    def _infer_field_types(self, records: List[Dict]) -> Dict[str, Dict]:
        """Infer field types from actual data"""
        field_info = {}
        
        for record in records:
            fields = record.get('fields', {})
            for field_name, field_value in fields.items():
                if field_name not in field_info:
                    field_info[field_name] = {
                        'name': field_name,
                        'type': 'unknown',
                        'sample_values': [],
                        'appears_in_records': 0
                    }
                
                # Update count
                field_info[field_name]['appears_in_records'] += 1
                
                # Collect sample values (max 3)
                if len(field_info[field_name]['sample_values']) < 3 and field_value:
                    sample = str(field_value)[:50] if field_value else 'empty'
                    if sample not in field_info[field_name]['sample_values']:
                        field_info[field_name]['sample_values'].append(sample)
                
                # Infer type
                if field_value is not None:
                    current_type = field_info[field_name]['type']
                    inferred_type = self._get_value_type(field_value, field_name)
                    
                    # Update type if we have better information
                    if current_type == 'unknown' or (current_type == 'text' and inferred_type != 'text'):
                        field_info[field_name]['type'] = inferred_type
        
        return field_info
    
    def _get_value_type(self, value: Any, field_name: str) -> str:
        """Determine the type of a value"""
        # Check by field name patterns first
        if 'Status' in field_name:
            return 'singleSelect'
        elif 'Photo' in field_name or 'Image' in field_name:
            return 'attachment/url'
        elif 'Price' in field_name or 'Rating' in field_name or 'Reviews' in field_name or 'ID' in field_name:
            return 'number'
        elif 'Link' in field_name:
            return 'url'
        
        # Check by value type
        if isinstance(value, bool):
            return 'checkbox'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, str):
            # Check if it looks like a URL
            if value.startswith('http://') or value.startswith('https://'):
                return 'url'
            # Check if it's a select option (short string with specific values)
            elif len(value) < 20 and value in ['Pending', 'Ready', 'Completed', 'Processing', 'Failed', 'Validated']:
                return 'singleSelect'
            else:
                return 'text'
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                return 'attachment'
            else:
                return 'multipleSelect'
        elif isinstance(value, dict):
            return 'linkedRecord'
        
        return 'unknown'
    
    async def run_complete_inspection(self):
        """Run complete schema inspection"""
        print("=" * 80)
        print("🔍 AIRTABLE SCHEMA INSPECTOR - Complete Analysis")
        print("=" * 80)
        
        # Try to get schema from Metadata API first
        print("\n📡 Attempting to connect to Airtable Metadata API...")
        schema = await self.get_base_schema()
        
        if schema and schema.get('tables'):
            print("✅ Successfully connected to Metadata API!")
            print(f"\n📊 BASE SCHEMA - {len(schema.get('tables', []))} tables found")
            print("-" * 40)
            
            for table in schema.get('tables', []):
                print(f"\nTable: {table.get('name')}")
                print(f"  ID: {table.get('id')}")
                print(f"  Fields: {len(table.get('fields', []))}")
                
                if table.get('name') == self.table_name:
                    print(f"\n📋 FIELDS IN '{self.table_name}' TABLE:")
                    print("-" * 40)
                    
                    for field in table.get('fields', []):
                        field_type = field.get('type', 'unknown')
                        field_name = field.get('name', 'unnamed')
                        print(f"\n  {field_name}")
                        print(f"    Type: {field_type}")
                        
                        # Show additional config for specific types
                        if field_type == 'singleSelect' and field.get('options'):
                            options = field.get('options', {}).get('choices', [])
                            option_names = [opt.get('name', '') for opt in options]
                            print(f"    Options: {', '.join(option_names)}")
                        elif field_type == 'number' and field.get('options'):
                            precision = field.get('options', {}).get('precision', 'default')
                            print(f"    Precision: {precision}")
        else:
            print("⚠️ Metadata API not accessible, using data inference method...")
            
        # Always also use the inference method for comparison
        print("\n📊 INFERRED SCHEMA FROM ACTUAL DATA:")
        print("-" * 40)
        field_info = await self.get_field_info_via_records()
        
        # Group fields by category
        product_fields = {}
        status_fields = {}
        video_fields = {}
        other_fields = {}
        
        for field_name, info in sorted(field_info.items()):
            if 'ProductNo' in field_name:
                product_num = field_name[9] if len(field_name) > 9 else '?'
                if product_num not in product_fields:
                    product_fields[product_num] = []
                product_fields[product_num].append((field_name, info))
            elif 'Status' in field_name:
                status_fields[field_name] = info
            elif 'Video' in field_name:
                video_fields[field_name] = info
            else:
                other_fields[field_name] = info
        
        # Display Product fields grouped by product number
        print("\n📦 PRODUCT FIELDS (Grouped by Product Number):")
        print("-" * 40)
        for product_num in sorted(product_fields.keys()):
            print(f"\nProduct {product_num}:")
            for field_name, info in product_fields[product_num]:
                field_type = info['type']
                appears = info['appears_in_records']
                print(f"  {field_name:<35} Type: {field_type:<15} Records: {appears}")
                if info['sample_values']:
                    print(f"    Sample: {info['sample_values'][0]}")
        
        # Display Status fields
        print("\n⚡ STATUS FIELDS:")
        print("-" * 40)
        for field_name, info in sorted(status_fields.items()):
            print(f"  {field_name:<35} Type: {info['type']:<15}")
            if info['sample_values']:
                print(f"    Values: {', '.join(info['sample_values'])}")
        
        # Display Video fields
        print("\n🎬 VIDEO FIELDS:")
        print("-" * 40)
        for field_name, info in sorted(video_fields.items()):
            print(f"  {field_name:<35} Type: {info['type']:<15}")
        
        # Display Other fields
        print("\n📋 OTHER FIELDS:")
        print("-" * 40)
        for field_name, info in sorted(other_fields.items()):
            print(f"  {field_name:<35} Type: {info['type']:<15}")
        
        # Summary statistics
        print("\n📊 SUMMARY:")
        print("-" * 40)
        print(f"Total fields: {len(field_info)}")
        print(f"Product-related fields: {sum(len(fields) for fields in product_fields.values())}")
        print(f"Status fields: {len(status_fields)}")
        print(f"Video fields: {len(video_fields)}")
        print(f"Other fields: {len(other_fields)}")
        
        print("\n" + "=" * 80)
        print("✅ Schema Inspection Complete!")
        print("=" * 80)

async def main():
    """Main function to run the schema inspector"""
    inspector = AirtableSchemaInspector()
    await inspector.run_complete_inspection()

if __name__ == "__main__":
    asyncio.run(main())