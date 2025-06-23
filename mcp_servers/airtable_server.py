import asyncio
import json
from airtable import Airtable
from typing import Dict, List, Optional

class AirtableMCPServer:
    def __init__(self, api_key: str, base_id: str, table_name: str):
        self.airtable = Airtable(base_id, table_name, api_key)
        
    async def get_pending_titles(self, limit: int = 1) -> Optional[Dict]:
        """Get titles with 'Pending' status from Airtable"""
        try:
            records = self.airtable.search('Status', 'Pending', max_records=limit)
            if records:
                record = records[0]
                return {
                    'record_id': record['id'],
                    'title': record['fields'].get('Title', ''),
                    'video_title': record['fields'].get('VideoTitle', ''),
                    'video_title_status': record['fields'].get('VideoTitleStatus', ''),
                    'status': record['fields'].get('Status', '')
                }
            return None
        except Exception as e:
            print(f"Error fetching pending titles: {e}")
            return None
    
    async def save_voice_data(self, record_id: str, voice_data: Dict) -> bool:
        """Save generated voice data to Airtable Mp3 fields"""
        try:
            update_fields = {}
            
            # Save intro voice
            if 'intro_voice' in voice_data:
                update_fields['IntroMp3'] = voice_data['intro_voice']
            
            # Save outro voice  
            if 'outro_voice' in voice_data:
                update_fields['OutroMp3'] = voice_data['outro_voice']
            
            # Save product voices
            for rank in [5, 4, 3, 2, 1]:
                voice_key = f'product_{rank}_voice'
                if voice_key in voice_data:
                    update_fields[f'Product{rank}Mp3'] = voice_data[voice_key]
            
            print(f"🎵 Saving voice data to fields: {list(update_fields.keys())}")
            self.airtable.update(record_id, update_fields)
            print(f"✅ Saved voice data for record {record_id}")
            
            return True
            
        except Exception as e:
            print(f"Error saving voice data: {e}")
            return False


    async def update_record_status(self, record_id: str, status: str = "Processing") -> bool:
        """Update record status - try different status values"""
        try:
            self.airtable.update(record_id, {'Status': status})
            print(f"✅ Updated record {record_id} status to {status}")
            return True
        except Exception as e:
            print(f"Warning: Could not update status: {e}")
            return False
    
    async def save_generated_content(self, record_id: str, content_data: Dict) -> bool:
        """Save generated content back to Airtable using individual product columns"""
        try:
            update_fields = {}
            
            if 'keywords' in content_data:
                update_fields['KeyWords'] = ', '.join(content_data['keywords'])
            
            if 'optimized_title' in content_data:
                update_fields['VideoTitle'] = content_data['optimized_title']
            
            if 'script' in content_data and isinstance(content_data['script'], dict):
                script_data = content_data['script']
                
                if 'intro' in script_data:
                    update_fields['VideoDescription'] = script_data['intro']
                
                products = script_data.get('products', [])
                sorted_products = sorted(products, key=lambda x: x.get('rank', 0), reverse=True)
                
                for product in sorted_products:
                    rank = product.get('rank')
                    name = product.get('name', '')
                    script = product.get('script', '')
                    
                    if rank == 5:
                        update_fields['ProductNo5Title'] = name
                        update_fields['ProductNo5Description'] = script
                        if 'image_urls' in content_data and 5 in content_data['image_urls']:
                            update_fields['ProductNo5Photo'] = content_data['image_urls'][5]
                    elif rank == 4:
                        update_fields['ProductNo4Title'] = name
                        update_fields['ProductNo4Description'] = script
                        if 'image_urls' in content_data and 4 in content_data['image_urls']:
                            update_fields['ProductNo4Photo'] = content_data['image_urls'][4]
                    elif rank == 3:
                        update_fields['ProductNo3Title'] = name
                        update_fields['ProductNo3Description'] = script
                        if 'image_urls' in content_data and 3 in content_data['image_urls']:
                            update_fields['ProductNo3Photo'] = content_data['image_urls'][3]
                    elif rank == 2:
                        update_fields['ProductNo2Title'] = name
                        update_fields['ProductNo2Description'] = script
                        if 'image_urls' in content_data and 2 in content_data['image_urls']:
                            update_fields['ProductNo2Photo'] = content_data['image_urls'][2]
                    elif rank == 1:
                        update_fields['ProductNo1Title'] = name
                        update_fields['ProductNo1Description'] = script
                        if 'image_urls' in content_data and 1 in content_data['image_urls']:
                            update_fields['ProductNo1Photo'] = content_data['image_urls'][1]

            print(f"📝 Saving to fields: {list(update_fields.keys())}")
            self.airtable.update(record_id, update_fields)
            print(f"✅ Saved generated content for record {record_id}")
            
            product_count = sum(1 for key in update_fields.keys() if 'ProductNo' in key and 'Title' in key)
            print(f"   📊 Saved: Keywords, VideoTitle, VideoDescription, and {product_count} products")
            
            return True
        except Exception as e:
            print(f"Error saving generated content: {e}")
            return False

    async def get_all_records(self) -> List[Dict]:
        """Get all records from Airtable"""
        try:
            records = self.airtable.get_all()
            return records
        except Exception as e:
            print(f"Error fetching all records: {e}")
            return []

    async def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """Get a single record by ID"""
        try:
            record = self.airtable.get(record_id)
            return record
        except Exception as e:
            print(f"Error fetching record {record_id}: {e}")
            return None

    async def update_record(self, record_id: str, fields: Dict) -> bool:
        """Update a record with the given fields"""
        try:
            self.airtable.update(record_id, fields)
            return True
        except Exception as e:
            print(f"Error updating record {record_id}: {e}")
            return False

    async def get_records_by_category(self, category: str, status: str = None) -> List[Dict]:
        """Get records filtered by category and optionally by status"""
        try:
            all_records = self.airtable.get_all()
            filtered_records = []
            
            for record in all_records:
                fields = record.get('fields', {})
                if fields.get('Category') == category:
                    if status is None or fields.get('Status') == status:
                        filtered_records.append(record)
            
            return filtered_records
        except Exception as e:
            print(f"Error fetching records by category: {e}")
            return []

    async def get_next_category(self, current_category: str) -> Optional[str]:
        """Get the next category to process"""
        categories = ["Electronics", "Fashion", "Home & Garden", "Beauty", "Sports & Outdoors", "Toys & Games", "Food & Beverage", "Other"]
        try:
            current_index = categories.index(current_category)
            if current_index < len(categories) - 1:
                return categories[current_index + 1]
        except ValueError:
            pass
        return None

    async def get_pending_records(self, limit: int = 100) -> List[Dict]:
        """Get all pending records"""
        try:
            records = self.airtable.search('Status', 'Pending', max_records=limit)
            return records
        except Exception as e:
            print(f"Error fetching pending records: {e}")
            return []

    async def update_keywords(self, record_id: str, keywords: List[str]) -> bool:
        """Update the SEO Keywords field for a record"""
        try:
            if isinstance(keywords, list):
                keywords_str = ", ".join(keywords)
            else:
                keywords_str = keywords
                
            self.airtable.update(record_id, {'SEO Keywords': keywords_str})
            return True
        except Exception as e:
            print(f"Error updating keywords for record {record_id}: {e}")
            return False


async def test_airtable_server():
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    pending_title = await server.get_pending_titles()
    if pending_title:
        print("✅ Found pending title:", pending_title['title'])
        print("   Video title:", pending_title['video_title'])
        print("   Status:", pending_title['status'])
    else:
        print("❌ No pending titles found")

if __name__ == "__main__":
    asyncio.run(test_airtable_server())
    
    async def update_record_status(self, record_id: str, status: str = "Processing") -> bool:
        """Update record status - try different status values"""
        try:
            self.airtable.update(record_id, {'Status': status})
            print(f"✅ Updated record {record_id} status to {status}")
            return True
        except Exception as e:
            print(f"Warning: Could not update status: {e}")
            return False
    
    async def save_generated_content(self, record_id: str, content_data: Dict) -> bool:
        """Save generated content back to Airtable using individual product columns"""
        try:
            update_fields = {}
            
            if 'keywords' in content_data:
                update_fields['KeyWords'] = ', '.join(content_data['keywords'])
            
            if 'optimized_title' in content_data:
                update_fields['VideoTitle'] = content_data['optimized_title']
            
            if 'script' in content_data and isinstance(content_data['script'], dict):
                script_data = content_data['script']
                
                if 'intro' in script_data:
                    update_fields['VideoDescription'] = script_data['intro']
                
                products = script_data.get('products', [])
                sorted_products = sorted(products, key=lambda x: x.get('rank', 0), reverse=True)
                
                for product in sorted_products:
                    rank = product.get('rank')
                    name = product.get('name', '')
                    script = product.get('script', '')
                    
                    if rank == 5:
                        update_fields['ProductNo5Title'] = name
                        update_fields['ProductNo5Description'] = script
                    elif rank == 4:
                        update_fields['ProductNo4Title'] = name
                        update_fields['ProductNo4Description'] = script
                    elif rank == 3:
                        update_fields['ProductNo3Title'] = name
                        update_fields['ProductNo3Description'] = script
                    elif rank == 2:
                        update_fields['ProductNo2Title'] = name
                        update_fields['ProductNo2Description'] = script
                    elif rank == 1:
                        update_fields['ProductNo1Title'] = name
                        update_fields['ProductNo1Description'] = script
            
            print(f"📝 Saving to fields: {list(update_fields.keys())}")
            self.airtable.update(record_id, update_fields)
            print(f"✅ Saved generated content for record {record_id}")
            
            product_count = sum(1 for key in update_fields.keys() if 'ProductNo' in key and 'Title' in key)
            print(f"   📊 Saved: Keywords, VideoTitle, VideoDescription, and {product_count} products")
            
            return True
        except Exception as e:
            print(f"Error saving generated content: {e}")
            return False

async def test_airtable_server():
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    server = AirtableMCPServer(
        api_key=config['airtable_api_key'],
        base_id=config['airtable_base_id'],
        table_name=config['airtable_table_name']
    )
    
    pending_title = await server.get_pending_titles()
    if pending_title:
        print("✅ Found pending title:", pending_title['title'])
    else:
        print("❌ No pending titles found")

if __name__ == "__main__":
    asyncio.run(test_airtable_server())

    async def get_all_records(self) -> List[Dict]:
        """Get all records from Airtable"""
        try:
            records = self.airtable.get_all()
            return records
        except Exception as e:
            print(f"Error fetching all records: {e}")
            return []

    async def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """Get a single record by ID"""
        try:
            record = self.airtable.get(record_id)
            return record
        except Exception as e:
            print(f"Error fetching record {record_id}: {e}")
            return None

    async def update_record(self, record_id: str, fields: Dict) -> bool:
        """Update a record with the given fields"""
        try:
            self.airtable.update(record_id, fields)
            return True
        except Exception as e:
            print(f"Error updating record {record_id}: {e}")
            return False

    async def get_records_by_category(self, category: str, status: str = None) -> List[Dict]:
        """Get records filtered by category and optionally by status"""
        try:
            all_records = self.airtable.get_all()
            filtered_records = []
            
            for record in all_records:
                fields = record.get('fields', {})
                if fields.get('Category') == category:
                    if status is None or fields.get('Status') == status:
                        filtered_records.append(record)
            
            return filtered_records
        except Exception as e:
            print(f"Error fetching records by category: {e}")
            return []

    async def get_next_category(self, current_category: str) -> Optional[str]:
        """Get the next category to process"""
        # This is a simple implementation - you might want to customize this
        categories = ["Electronics", "Fashion", "Home & Garden", "Beauty", "Sports & Outdoors", "Toys & Games", "Food & Beverage", "Other"]
        try:
            current_index = categories.index(current_category)
            if current_index < len(categories) - 1:
                return categories[current_index + 1]
        except ValueError:
            pass
        return None

    async def get_pending_records(self, limit: int = 100) -> List[Dict]:
        """Get all pending records"""
        try:
            records = self.airtable.search('Status', 'Pending', max_records=limit)
            return records
        except Exception as e:
            print(f"Error fetching pending records: {e}")
            return []

    async def update_keywords(self, record_id: str, keywords: List[str]) -> bool:
        """Update the SEO Keywords field for a record"""
        try:
            # Join keywords into a comma-separated string if they're a list
            if isinstance(keywords, list):
                keywords_str = ", ".join(keywords)
            else:
                keywords_str = keywords
                
            self.airtable.update(record_id, {'SEO Keywords': keywords_str})
            return True
        except Exception as e:
            print(f"Error updating keywords for record {record_id}: {e}")
            return False
