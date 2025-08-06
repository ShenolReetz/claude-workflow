#!/usr/bin/env python3
"""
Production WordPress MCP - Publish to WordPress
"""

import aiohttp
import base64
from typing import Dict, List, Optional

class ProductionWordPressMCP:
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config.get('wordpress_url', 'https://reviewch3kr.com')
        self.username = config.get('wordpress_user', '')
        self.password = config.get('wordpress_password', '')
        
        # Create basic auth header
        credentials = f"{self.username}:{self.password}"
        self.auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"
    
    async def create_post(self, title: str, content: str, excerpt: str, tags: List[str]) -> Dict:
        """Create a WordPress post"""
        try:
            url = f"{self.base_url}/wp-json/wp/v2/posts"
            
            headers = {
                "Authorization": self.auth_header,
                "Content-Type": "application/json"
            }
            
            # Build post data
            post_data = {
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "status": "publish",
                "tags": tags,
                "categories": [1]  # Default category
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=post_data) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        return {
                            'success': True,
                            'post_id': data.get('id'),
                            'post_url': data.get('link', '')
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ WordPress API error: {response.status} - {error_text}")
                        return {
                            'success': False,
                            'error': f'API error: {response.status}'
                        }
                        
        except Exception as e:
            print(f"❌ Error creating WordPress post: {e}")
            return {
                'success': False,
                'error': str(e)
            }