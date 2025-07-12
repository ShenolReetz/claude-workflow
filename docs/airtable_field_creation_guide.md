# Airtable Field Creation Guide

## Summary

Based on my analysis of the codebase and Airtable API documentation:

### 1. **Can we create new fields in Airtable via API?**
**YES** - Airtable supports programmatic field creation through their Meta API (as of 2024).

### 2. **Is there existing code that creates Airtable fields?**
**NO** - The current codebase does not have any field creation functionality. The existing code only:
- Updates existing fields with data
- Reads records from Airtable
- Searches and filters records
- Uses the `airtable-python-wrapper` library which does NOT support field creation

### 3. **What's the best approach for adding new fields to an Airtable base?**
Use the Airtable Meta API directly with HTTP requests and a Personal Access Token.

## Current Implementation Analysis

### What We Found in the Codebase:

1. **Test Files** (`mcp_servers/test_field_creation.py`, `mcp_servers/verify_fields.py`):
   - These files test updating EXISTING fields with data
   - They do NOT create new fields
   - They use the standard `airtable-python-wrapper` library

2. **Airtable Server** (`mcp_servers/airtable_server.py`):
   - Uses `airtable-python-wrapper==0.15.3`
   - Only performs CRUD operations on records
   - Cannot modify table schema

3. **Current Capabilities**:
   - ✅ Read records
   - ✅ Update existing fields
   - ✅ Search and filter
   - ❌ Create new fields
   - ❌ Modify field types
   - ❌ Delete fields

## How to Add Field Creation Capability

### Step 1: Get a Personal Access Token

1. Go to https://airtable.com/create/tokens
2. Create a token with these scopes:
   - `data.records:read`
   - `data.records:write`
   - `schema:bases:read`
   - `schema:bases:write`

### Step 2: Add Token to Configuration

Add to `/home/claude-workflow/config/api_keys.json`:
```json
{
  "airtable_personal_access_token": "patXXXXXXXXXXXXXX"
}
```

### Step 3: Use the Meta API

The field creation endpoint:
```
POST https://api.airtable.com/v0/meta/bases/{baseId}/tables/{tableId}/fields
```

### Step 4: Example Implementation

```python
import requests

def create_field(base_id, table_id, field_config, access_token):
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=field_config)
    return response.json()

# Example: Create a text field
field_config = {
    "name": "NewTextField",
    "type": "singleLineText"
}

# Example: Create a select field
field_config = {
    "name": "Status",
    "type": "singleSelect",
    "options": {
        "choices": [
            {"name": "pending", "color": "yellowBright"},
            {"name": "completed", "color": "greenBright"}
        ]
    }
}
```

## Field Types Supported

Common field types you can create:
- `singleLineText`
- `multilineText`
- `number`
- `singleSelect`
- `multipleSelects`
- `date`
- `dateTime`
- `checkbox`
- `url`
- `email`
- `phoneNumber`
- `currency`
- `percent`
- `duration`
- `rating`

## Important Notes

1. **Authentication**: Regular API keys CANNOT create fields. You MUST use a Personal Access Token.

2. **Table ID vs Table Name**: The API requires the table ID, not the table name. You need to first get the schema to find table IDs.

3. **Rate Limits**: Schema changes have different rate limits than regular data operations.

4. **Field Naming**: Field names must be unique within a table.

5. **Limitations**: Some advanced field types (like formulas) cannot be created via API.

## Recommended Approach for This Project

Since the project already has many hardcoded field names (ProductNo1Title, ProductNo2Title, etc.), the best approach would be:

1. **One-time Setup**: Create all needed fields manually in Airtable UI or via a setup script
2. **Document Fields**: Maintain a schema documentation file
3. **Validation**: Add a startup check to verify all required fields exist
4. **Fallback**: Handle missing fields gracefully in the code

This is more practical than adding dynamic field creation to the workflow, unless you specifically need to create fields on-the-fly.