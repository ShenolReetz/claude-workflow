#!/usr/bin/env python3
import json
import requests

# Load config
with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
    config = json.load(f)

# Try both token field names
airtable_token = config.get('airtable_personal_access_token') or config.get('airtable_api_key', '')

print(f'Using token: {airtable_token[:20]}...')

# Get total count using Airtable API
url = 'https://api.airtable.com/v0/appTtNBJ8dAnjvkPP/tblhGDEW6eUbmaYZx'
headers = {'Authorization': f'Bearer {airtable_token}'}

# Count records using pagination
params = {'fields': ['ID'], 'maxRecords': 100}

total_count = 0
offset = None
page = 1

while True:
    if offset:
        params['offset'] = offset
    elif 'offset' in params:
        del params['offset']
        
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f'HTTP Error {response.status_code}: {response.text}')
        break
        
    data = response.json()
    
    if 'records' in data:
        batch_count = len(data['records'])
        total_count += batch_count
        print(f'Page {page}: {batch_count} records (Total: {total_count})')
        
        if 'offset' in data:
            offset = data['offset']
            page += 1
        else:
            break
    else:
        print(f'Error in response: {data}')
        break

print(f'\n🎯 TOTAL TITLES IN AIRTABLE: {total_count}')