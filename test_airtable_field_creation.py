#!/usr/bin/env python3
"""
Test script to demonstrate Airtable field creation via API.

The airtable-python-wrapper library does NOT support field creation.
We need to use the Airtable Meta API directly with HTTP requests.
"""

import json
import requests
import os
from typing import Dict, List, Optional

def create_airtable_field(base_id: str, table_id: str, field_config: Dict, access_token: str) -> Optional[Dict]:
    """
    Create a new field in an Airtable table using the Meta API.
    
    Note: This requires a Personal Access Token or OAuth token, NOT an API key.
    
    Args:
        base_id: The Airtable base ID
        table_id: The table ID (not name) - you need to get this from the API
        field_config: Field configuration dict with name, type, and options
        access_token: Personal Access Token with schema:write scope
        
    Returns:
        Response data from Airtable API or None if failed
    """
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=field_config)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating field: {e}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None

def get_base_schema(base_id: str, access_token: str) -> Optional[Dict]:
    """
    Get the base schema including all tables and fields.
    
    Args:
        base_id: The Airtable base ID
        access_token: Personal Access Token with schema:read scope
        
    Returns:
        Base schema data or None if failed
    """
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting base schema: {e}")
        if hasattr(e.response, 'text'):
            print(f"   Response: {e.response.text}")
        return None

def main():
    """
    Demonstrate Airtable field creation capabilities.
    """
    print("=" * 80)
    print("🔍 Airtable Field Creation Test")
    print("=" * 80)
    
    # Load config
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Config file not found. Using example values.")
        config = {
            'airtable_base_id': 'appXXXXXXXXXXXXXX',
            'airtable_api_key': 'keyXXXXXXXXXXXXXX',  # This won't work for schema changes
            'airtable_personal_access_token': None  # You need this for field creation
        }
    
    print("\n📋 Current Airtable Configuration:")
    print(f"   Base ID: {config.get('airtable_base_id', 'Not set')}")
    print(f"   API Key: {'Set' if config.get('airtable_api_key') else 'Not set'}")
    print(f"   Personal Access Token: {'Set' if config.get('airtable_personal_access_token') else 'Not set'}")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("1. Field creation requires a Personal Access Token (PAT) with 'schema:write' scope")
    print("2. Regular API keys CANNOT create fields")
    print("3. You need to create a PAT at: https://airtable.com/create/tokens")
    print("4. The PAT must have these scopes: data.records:read, data.records:write, schema:bases:read, schema:bases:write")
    
    # Check if we have a personal access token
    access_token = config.get('airtable_personal_access_token')
    if not access_token:
        print("\n❌ No Personal Access Token found in config.")
        print("   To enable field creation, add 'airtable_personal_access_token' to your api_keys.json")
        
        print("\n📝 Example field configurations that WOULD work with proper authentication:")
        
        example_fields = [
            {
                "name": "TestControlStatus",
                "type": "singleSelect",
                "options": {
                    "choices": [
                        {"name": "pending", "color": "yellowBright"},
                        {"name": "success", "color": "greenBright"},
                        {"name": "failed", "color": "redBright"}
                    ]
                }
            },
            {
                "name": "TestControlAttempts",
                "type": "number",
                "options": {
                    "precision": 0
                }
            },
            {
                "name": "TestControlLastError",
                "type": "multilineText"
            },
            {
                "name": "ProductNo6Title",
                "type": "singleLineText"
            },
            {
                "name": "ProductNo6Description",
                "type": "multilineText"
            }
        ]
        
        for field in example_fields:
            print(f"\n   Field: {field['name']}")
            print(f"   Type: {field['type']}")
            if field.get('options'):
                print(f"   Options: {json.dumps(field['options'], indent=6)}")
        
        return
    
    # If we have a token, try to get the schema
    base_id = config.get('airtable_base_id')
    print(f"\n🔍 Attempting to get base schema for: {base_id}")
    
    schema = get_base_schema(base_id, access_token)
    if schema:
        print("✅ Successfully retrieved base schema!")
        tables = schema.get('tables', [])
        print(f"   Found {len(tables)} tables")
        
        for table in tables[:3]:  # Show first 3 tables
            print(f"\n   Table: {table.get('name')} (ID: {table.get('id')})")
            fields = table.get('fields', [])
            print(f"   Fields ({len(fields)}):")
            for field in fields[:5]:  # Show first 5 fields
                print(f"      - {field.get('name')} ({field.get('type')})")
    
    print("\n" + "=" * 80)
    print("📚 Summary:")
    print("=" * 80)
    print("1. ✅ Airtable DOES support field creation via API (as of 2024)")
    print("2. ❌ The airtable-python-wrapper library does NOT support this")
    print("3. 🔑 You need a Personal Access Token (not API key) for schema changes")
    print("4. 🛠️  Field creation uses the Meta API: POST /v0/meta/bases/{baseId}/tables/{tableId}/fields")
    print("5. 📖 Official docs: https://airtable.com/developers/web/api/create-field")

if __name__ == "__main__":
    main()