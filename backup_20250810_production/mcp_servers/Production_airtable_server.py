#!/usr/bin/env python3
"""
Production Airtable MCP Server - Real API Integration
"""

import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import base64
from urllib.parse import quote

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
        
    async def get_pending_title(self) -> Optional[Dict]:
        """Fetch a pending title from Airtable using real API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Filter for records where Status = "Pending" and sort by smallest ID
                params = {
                    "filterByFormula": "{Status} = 'Pending'",
                    "maxRecords": 1,
                    "sort[0][field]": "ID",
                    "sort[0][direction]": "asc"
                }
                
                async with session.get(self.base_url, headers=self.headers, params=params) as response:
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
                        print(f"❌ Airtable API error: {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Error fetching pending title: {e}")
            return None
    
    async def update_title_status(self, record_id: str, status: str, notes: str = "") -> bool:
        """Update the main Status of a title in Airtable"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {
                    "fields": {
                        "Status": status,
                        "TextControlStatus": notes,
                        "LastOptimizationDate": datetime.now().strftime('%Y-%m-%d')
                    }
                }
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        print(f"✅ Updated record {record_id} status to: {status}")
                        return True
                    else:
                        print(f"❌ Failed to update status: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error updating status: {e}")
            return False

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

    async def update_specific_status(self, record_id: str, fields: Dict) -> bool:
        """Update specific fields in Airtable"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {"fields": fields}
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        field_names = ', '.join(fields.keys())
                        print(f"✅ Updated {field_names} for record {record_id}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to update fields: {response.status}")
                        print(f"   Error details: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Error updating specific status: {e}")
            return False

    async def update_record_field(self, record_id: str, field_name: str, value: any) -> bool:
        """Update a single field in Airtable record"""
        return await self.update_specific_status(record_id, {field_name: value})
    
    async def save_amazon_products(self, record_id: str, products: List[Dict]) -> Dict:
        """Save Amazon products to Airtable record with proper field mapping"""
        try:
            fields = {}
            # Map to the actual Airtable field names
            for i, product in enumerate(products[:5], 1):
                # Use ProductNo{i} format as per Airtable schema
                fields[f'ProductNo{i}Title'] = product.get('name', '')[:100]
                fields[f'ProductNo{i}Description'] = product.get('description', '')[:500]  
                fields[f'ProductNo{i}Photo'] = product.get('image_url', '')
                
                # Handle price conversion
                price_str = product.get('price', '$0').replace('$', '').replace(',', '')
                try:
                    fields[f'ProductNo{i}Price'] = float(price_str)
                except (ValueError, TypeError):
                    fields[f'ProductNo{i}Price'] = 0.0
                
                # Handle rating conversion
                rating_str = product.get('rating', '0')
                try:
                    fields[f'ProductNo{i}Rating'] = float(rating_str)
                except (ValueError, TypeError):
                    fields[f'ProductNo{i}Rating'] = 0.0
                
                # Handle reviews conversion
                reviews_str = product.get('reviews', '0').replace(',', '').replace('+', '')
                try:
                    fields[f'ProductNo{i}Reviews'] = int(reviews_str)
                except (ValueError, TypeError):
                    fields[f'ProductNo{i}Reviews'] = 0
                
                # Set all statuses to Ready since we have the data
                fields[f'ProductNo{i}TitleStatus'] = 'Ready'
                fields[f'ProductNo{i}DescriptionStatus'] = 'Ready'
                fields[f'ProductNo{i}PhotoStatus'] = 'Ready'
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {"fields": fields}
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Saved {len(products)} products to Airtable with Ready status")
                        # Return properly formatted record structure
                        return {
                            'record_id': record_id,
                            'fields': result.get('fields', {})
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to save products: {response.status}")
                        print(f"   Error details: {error_text}")
                        return {'record_id': record_id, 'fields': {}}
        except Exception as e:
            print(f"❌ Error saving products: {e}")
            return {'record_id': record_id, 'fields': {}}
    
    async def save_generated_content(self, record_id: str, content: Dict) -> bool:
        """Save generated content (titles, descriptions, scripts) to Airtable with status updates"""
        try:
            fields = {}
            
            # Save keywords
            if 'keywords' in content:
                fields['KeyWords'] = ', '.join(content['keywords'][:10])
                fields['UniversalKeywords'] = ', '.join(content['keywords'][:10])
            
            # Save platform-specific titles and descriptions with status updates
            if 'youtube_title' in content:
                fields['YouTubeTitle'] = content['youtube_title'][:100]
            if 'youtube_description' in content:
                fields['YouTubeDescription'] = content['youtube_description'][:5000]
            if 'instagram_caption' in content:
                fields['InstagramCaption'] = content['instagram_caption'][:500]
            if 'wordpress_title' in content:
                fields['WordPressTitle'] = content['wordpress_title'][:100]
            if 'tiktok_description' in content:
                fields['TikTokDescription'] = content['tiktok_description'][:500]
                
            # Save video title and description with status
            if 'video_title' in content:
                fields['VideoTitle'] = content['video_title']
                fields['VideoTitleStatus'] = 'Ready'
            if 'video_description' in content:
                fields['VideoDescription'] = content['video_description']
                fields['VideoDescriptionStatus'] = 'Ready'
            
            # Save scripts as structured JSON
            if 'script_data' in content:
                fields['VideoScript'] = json.dumps(content['script_data'])
                fields['IntroHook'] = content['script_data'].get('intro_script', '')
                fields['OutroCallToAction'] = content['script_data'].get('outro_script', '')
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {"fields": fields}
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        print(f"✅ Saved generated content with status updates to Airtable")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to save content: {response.status}")
                        print(f"   Error details: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Error saving content: {e}")
            return False
    
    async def save_voice_data(self, record_id: str, voice_data: Dict) -> bool:
        """Save voice/audio data to Airtable using correct field names"""
        try:
            fields = {}
            
            # Save intro/outro voice (using actual Airtable field names)
            if 'intro_voice' in voice_data:
                fields['IntroMp3'] = voice_data['intro_voice']
            if 'outro_voice' in voice_data:
                fields['OutroMp3'] = voice_data['outro_voice']
            
            # Save product voices (Product1Mp3, Product2Mp3, etc.)
            for i in range(1, 6):
                if f'product{i}_voice' in voice_data:
                    fields[f'Product{i}Mp3'] = voice_data[f'product{i}_voice']
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {"fields": fields}
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        print(f"✅ Saved voice data to Airtable")
                        return True
                    else:
                        print(f"❌ Failed to save voice data: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error saving voice data: {e}")
            return False
    
    async def save_image_urls(self, record_id: str, image_urls: Dict) -> bool:
        """Save generated image URLs to Airtable using correct field names"""
        try:
            fields = {}
            
            # Save intro/outro images (using actual Airtable field names)
            if 'intro_image' in image_urls:
                fields['IntroPhoto'] = image_urls['intro_image']
            if 'outro_image' in image_urls:
                fields['OutroPhoto'] = image_urls['outro_image']
            
            # Save product images - these should update the existing ProductNo{i}Photo fields
            for i in range(1, 6):
                if f'product{i}_image' in image_urls:
                    fields[f'ProductNo{i}Photo'] = image_urls[f'product{i}_image']
                    fields[f'ProductNo{i}PhotoStatus'] = 'Ready'
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {"fields": fields}
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        print(f"✅ Saved image URLs with status updates to Airtable")
                        return True
                    else:
                        print(f"❌ Failed to save image URLs: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error saving image URLs: {e}")
            return False
    
    async def save_video_data(self, record_id: str, video_data: Dict) -> bool:
        """Save video data and URLs to Airtable with status updates"""
        try:
            fields = {}
            
            if 'video_url' in video_data:
                fields['FinalVideo'] = video_data['video_url']
            if 'project_id' in video_data:
                fields['JSON2VideoProjectID'] = video_data['project_id']
            if 'youtube_url' in video_data:
                fields['YouTubeURL'] = video_data['youtube_url']
            if 'tiktok_url' in video_data:
                fields['TikTokURL'] = video_data['tiktok_url']
                
            # Update platform readiness
            platforms_ready = []
            if 'youtube_url' in video_data:
                platforms_ready.append('Youtube')
            if 'tiktok_url' in video_data:
                platforms_ready.append('TikTok')
            if 'wordpress_url' in video_data:
                platforms_ready.append('Website')
                
            if platforms_ready:
                fields['PlatformReadiness'] = platforms_ready
            
            # Set content validation status to validated
            fields['ContentValidationStatus'] = 'Validated'
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {"fields": fields}
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        print(f"✅ Saved video data with platform readiness to Airtable")
                        return True
                    else:
                        print(f"❌ Failed to save video data: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error saving video data: {e}")
            return False
    
    async def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """Get a specific record by ID"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'record_id': data['id'],
                            'fields': data['fields']
                        }
                    else:
                        print(f"❌ Failed to get record: {response.status}")
                        return None
        except Exception as e:
            print(f"❌ Error getting record: {e}")
            return None
    
    async def update_record(self, record_id: str, fields: Dict) -> bool:
        """Update any fields in a record"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/{record_id}"
                data = {"fields": fields}
                
                async with session.patch(url, headers=self.headers, json=data) as response:
                    if response.status == 200:
                        print(f"✅ Updated record {record_id}")
                        return True
                    else:
                        print(f"❌ Failed to update record: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Error updating record: {e}")
            return False