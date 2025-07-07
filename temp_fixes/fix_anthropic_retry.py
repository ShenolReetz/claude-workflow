#!/usr/bin/env python3
"""
Add retry logic for Anthropic API overload errors
"""

# Read the content generation server
with open('mcp_servers/content_generation_server.py', 'r') as f:
    content = f.read()

# Add retry logic after imports
import_section = '''import json
import asyncio
import time
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic
import logging

logger = logging.getLogger(__name__)'''

retry_decorator = '''
import json
import asyncio
import time
from typing import Dict, List, Optional
from anthropic import AsyncAnthropic
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_on_overload(max_retries=3, base_delay=5):
    """Decorator to retry on Anthropic overload errors"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if "529" in str(e) or "overloaded" in str(e).lower():
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(f"Anthropic API overloaded, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(delay)
                        else:
                            logger.error(f"Max retries reached for Anthropic API")
                            raise
                    else:
                        raise
            return None
        return wrapper
    return decorator'''

# Replace the import section
content = content.replace(import_section, retry_decorator)

# Add @retry_on_overload decorator to each generation method
methods_to_decorate = [
    'async def generate_seo_keywords',
    'async def generate_social_media_title',
    'async def generate_countdown_script',
    'async def generate_blog_post'
]

for method in methods_to_decorate:
    content = content.replace(
        f'    {method}',
        f'    @retry_on_overload(max_retries=3, base_delay=5)\n    {method}'
    )

# Write the updated content
with open('mcp_servers/content_generation_server.py', 'w') as f:
    f.write(content)

print("✅ Added retry logic for Anthropic API overload errors")
print("✅ Will retry up to 3 times with exponential backoff")
