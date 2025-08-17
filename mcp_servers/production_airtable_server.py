#!/usr/bin/env python3
"""
Production Airtable MCP Server - Optimized with Connection Pooling and Retry Logic
"""

import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64
from urllib.parse import quote
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

def with_retry(max_attempts: int = 3, backoff_factor: float = 2.0):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_attempts} attempts failed: {e}")
                        raise
            return None
        return wrapper
    return decorator

class ProductionAirtableMCPServer:
    def __init__(self, api_key: str, base_id: str, table_name: str):
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{quote(table_name)}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Connection pooling session
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.2  # 5 requests per second max
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create a reusable session with connection pooling"""
        if self._session is None or self._session.closed:
            # Create connector with connection pooling
            self._connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool limit
                limit_per_host=30,  # Per-host connection limit
                ttl_dns_cache=300,  # DNS cache timeout
                enable_cleanup_closed=True
            )
            
            # Create session with timeout
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self._session = aiohttp.ClientSession(
                connector=self._connector,
                headers=self.headers,
                timeout=timeout
            )
            logger.info("Created new Airtable session with connection pooling")
        
        return self._session
    
    async def _rate_limit(self):
        """Implement rate limiting to avoid API throttling"""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        
        self._last_request_time = time.time()
    
    @with_retry(max_attempts=3)
    async def get_pending_title(self) -> Optional[Dict]:
        """Fetch a pending title from Airtable using real API with retry logic"""
        try:
            await self._rate_limit()
            session = await self._get_session()
            
            # Filter for records where Status = "Pending" and sort by smallest ID
            params = {
                "filterByFormula": "{Status} = 'Pending'",
                "maxRecords": 1,
                "sort[0][field]": "ID",
                "sort[0][direction]": "asc"
            }
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    records = data.get('records', [])
                    if records:
                        record = records[0]
                        return {
                            'record_id': record['id'],
                            'Title': record['fields'].get('Title', ''),
                            'VideoTitle': record['fields'].get('VideoTitle', ''),
                            'Status': record['fields'].get('Status', 'Pending'),
                            'Category': record['fields'].get('Category', 'General'),
                            'Keywords': record['fields'].get('Keywords', ''),
                            'Created': record['fields'].get('Created', '')
                        }
                else:
                    logger.error(f"Airtable API error: {response.status}")
                    error_text = await response.text()
                    logger.error(f"Error details: {error_text}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching pending title: {e}")
            raise
    
    @with_retry(max_attempts=3)
    async def update_title_status(self, record_id: str, status: str, notes: str = "") -> bool:
        """Update the main Status of a title in Airtable with retry logic"""
        try:
            await self._rate_limit()
            session = await self._get_session()
            
            url = f"{self.base_url}/{record_id}"
            data = {
                "fields": {
                    "Status": status,
                    "TextControlStatus": notes,
                    "LastOptimizationDate": datetime.now().strftime('%Y-%m-%d')
                }
            }
            
            async with session.patch(url, json=data) as response:
                if response.status == 200:
                    logger.info(f"Updated record {record_id} status to: {status}")
                    return True
                else:
                    logger.error(f"Failed to update status: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            raise

    async def update_video_title_status(self, record_id: str, title: str) -> bool:
        """Update VideoTitle and set VideoTitleStatus to Ready"""
        return await self.update_specific_status(record_id, {
            'VideoTitle': title,
            'VideoTitleStatus': 'Ready'
        })

    async def update_video_description_status(self, record_id: str, description: str) -> bool:
        """Update VideoDescription and set VideoDescriptionStatus to Ready"""
        return await self.update_specific_status(record_id, {
            'VideoDescription': description,
            'VideoDescriptionStatus': 'Ready'
        })

    async def update_product_status(self, record_id: str, product_num: int, title: str, description: str, photo_url: str, affiliate_link: str, price: float, rating: float, reviews: int) -> bool:
        """Update product data and set all related statuses to Ready"""
        return await self.update_specific_status(record_id, {
            f'ProductNo{product_num}Title': title,
            f'ProductNo{product_num}TitleStatus': 'Ready',
            f'ProductNo{product_num}Description': description,
            f'ProductNo{product_num}DescriptionStatus': 'Ready',
            f'ProductNo{product_num}Photo': photo_url,
            f'ProductNo{product_num}PhotoStatus': 'Ready',
            f'ProductNo{product_num}AffiliateLink': affiliate_link,
            f'ProductNo{product_num}Price': price,
            f'ProductNo{product_num}Rating': rating,
            f'ProductNo{product_num}Reviews': reviews
        })

    async def update_video_production_ready(self, record_id: str) -> bool:
        """Mark video as ready for production"""
        return await self.update_specific_status(record_id, {
            'VideoProductionRDY': 'Ready'
        })

    async def update_content_validation_status(self, record_id: str, status: str, issues: str = "", regeneration_count: int = 0) -> bool:
        """Update content validation status"""
        return await self.update_specific_status(record_id, {
            'ContentValidationStatus': status,
            'ValidationIssues': issues,
            'RegenerationCount': regeneration_count
        })

    async def update_platform_readiness(self, record_id: str, platforms: list) -> bool:
        """Update which platforms are ready for upload"""
        return await self.update_specific_status(record_id, {
            'PlatformReadiness': platforms
        })

    @with_retry(max_attempts=3)
    async def update_specific_status(self, record_id: str, fields: Dict) -> bool:
        """Update specific fields in Airtable with retry logic and connection pooling"""
        try:
            await self._rate_limit()
            session = await self._get_session()
            
            url = f"{self.base_url}/{record_id}"
            data = {"fields": fields}
            
            async with session.patch(url, json=data) as response:
                if response.status == 200:
                    field_names = ', '.join(fields.keys())
                    logger.info(f"Updated {field_names} for record {record_id}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to update fields: {response.status}")
                    logger.error(f"Error details: {error_text}")
                    # Log the specific fields that failed for debugging
                    logger.error(f"Failed fields: {list(fields.keys())}")
                    logger.error(f"Field values sample: {str(fields)[:500]}")
                    return False
        except Exception as e:
            logger.error(f"Error updating specific status: {e}")
            raise

    async def update_record_field(self, record_id: str, field_name: str, value: any) -> bool:
        """Update a single field in Airtable record"""
        return await self.update_specific_status(record_id, {field_name: value})
    
    @with_retry(max_attempts=3)
    async def update_record_fields_batch(self, record_id: str, fields: Dict) -> bool:
        """
        Batch update multiple fields in a single API call with retry logic
        
        Args:
            record_id: The Airtable record ID
            fields: Dictionary of field names and values to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        return await self.update_specific_status(record_id, fields)
    
    async def save_amazon_products(self, record_id: str, products: List[Dict]) -> Dict:
        """Save Amazon products to Airtable record with proper field mapping and retry logic"""
        try:
            fields = {}
            # Map to the actual Airtable field names
            for i, product in enumerate(products[:5], 1):
                # Use ProductNo{i} format as per Airtable schema
                fields[f'ProductNo{i}Title'] = product.get('title', '')[:100]
                fields[f'ProductNo{i}Description'] = product.get('description', '')[:500]  
                fields[f'ProductNo{i}Photo'] = product.get('image', '')
                fields[f'ProductNo{i}AffiliateLink'] = product.get('link', '')
                
                # Handle price conversion
                price_val = product.get('price', '$0')
                if isinstance(price_val, (int, float)):
                    fields[f'ProductNo{i}Price'] = float(price_val)
                else:
                    price_str = str(price_val).replace('$', '').replace(',', '')
                    try:
                        fields[f'ProductNo{i}Price'] = float(price_str)
                    except (ValueError, TypeError):
                        fields[f'ProductNo{i}Price'] = 0.0
                
                # Handle rating
                rating_val = product.get('rating', 0)
                if isinstance(rating_val, (int, float)):
                    fields[f'ProductNo{i}Rating'] = float(rating_val)
                else:
                    try:
                        fields[f'ProductNo{i}Rating'] = float(str(rating_val))
                    except (ValueError, TypeError):
                        fields[f'ProductNo{i}Rating'] = 0.0
                
                # Handle reviews count
                reviews_val = product.get('total_reviews', '0')
                if isinstance(reviews_val, (int, float)):
                    fields[f'ProductNo{i}Reviews'] = int(reviews_val)
                else:
                    reviews_str = str(reviews_val).replace(',', '').replace('K', '000').replace('M', '000000')
                    try:
                        if '+' in reviews_str:
                            reviews_str = reviews_str.replace('+', '')
                        fields[f'ProductNo{i}Reviews'] = int(float(reviews_str))
                    except (ValueError, TypeError):
                        fields[f'ProductNo{i}Reviews'] = 0
                
                # Set status fields to Ready
                fields[f'ProductNo{i}TitleStatus'] = 'Ready'
                fields[f'ProductNo{i}DescriptionStatus'] = 'Ready'
                fields[f'ProductNo{i}PhotoStatus'] = 'Ready'
            
            # Save to Airtable with retry logic
            success = await self.update_record_fields_batch(record_id, fields)
            
            if success:
                logger.info(f"Successfully saved {len(products)} products to Airtable")
                return {'success': True, 'products_saved': len(products)}
            else:
                return {'success': False, 'error': 'Failed to update Airtable'}
                
        except Exception as e:
            logger.error(f"Error saving Amazon products: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close(self):
        """Close the session and connector properly"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Closed Airtable session")
        
        if self._connector:
            await self._connector.close()
            logger.info("Closed Airtable connector")
    
    def __del__(self):
        """Cleanup on deletion"""
        if self._session and not self._session.closed:
            try:
                asyncio.create_task(self._session.close())
            except RuntimeError:
                # Event loop might be closed
                pass