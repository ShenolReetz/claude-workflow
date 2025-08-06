#!/usr/bin/env python3
import json
import os
import sys

def load_config():
    """Load configuration from api_keys.json"""
    config_path = "/home/claude-workflow/config/api_keys.json"
    with open(config_path, 'r') as f:
        return json.load(f)

# Load config for environment variables
config_path = "/home/claude-workflow/config/api_keys.json"
with open(config_path, 'r') as f:
    config = json.load(f)

# Set environment variables
os.environ["OPENAI_API_KEY"] = config.get("openai_api_key", "")
os.environ["AIRTABLE_API_TOKEN"] = config.get("airtable_api_key", "")
os.environ["AIRTABLE_BASE_ID"] = config.get("airtable_base_id", "")
os.environ["AIRTABLE_TABLE_NAME"] = config.get("airtable_table_name", "")
os.environ["ELEVENLABS_API_KEY"] = config.get("elevenlabs_api_key", "")
os.environ["JSON2VIDEO_API_KEY"] = config.get("json2video_api_key", "")
os.environ["ANTHROPIC_API_KEY"] = config.get("anthropic_api_key", "")

# Run the command if provided
if len(sys.argv) > 1:
    os.execvp(sys.argv[1], sys.argv[1:])
