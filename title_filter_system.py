#!/usr/bin/env python3
"""
Title Filtering System for High-Retention Social Media Content
Filters 3000+ titles down to 1500 high-engagement titles
"""

import asyncio
import json
import re
from typing import Dict, List, Tuple
from mcp_servers.Test_airtable_server import AirtableMCPServer

class TitleFilterSystem:
    """Filter titles for high social media retention"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
        # High-retention categories (excitement + engagement)
        self.high_retention_categories = {
            'tech_gadgets': {
                'keywords': ['action camera', 'gopro', 'drone', 'smartphone', 'tablet', 'smartwatch', 'earbuds', 'headphones', 'speaker', 'ring light', 'webcam'],
                'weight': 10,
                'description': 'Tech gadgets and accessories'
            },
            'gaming': {
                'keywords': ['gaming keyboard', 'gaming mouse', 'gaming headset', 'gaming chair', 'gaming monitor', 'gaming laptop', 'gaming desk', 'gaming gear', 'rgb', 'mechanical keyboard'],
                'weight': 10,
                'description': 'Gaming equipment and accessories'
            },
            'laptops_computers': {
                'keywords': ['laptop', 'computer', 'macbook', 'chromebook', 'ultrabook', 'gaming laptop', 'business laptop', 'laptop stand', 'laptop bag', 'ssd'],
                'weight': 9,
                'description': 'Laptops and computer equipment'
            },
            'fitness_health': {
                'keywords': ['fitness tracker', 'smart scale', 'resistance bands', 'yoga mat', 'protein powder', 'supplements', 'workout gear', 'treadmill', 'dumbbells'],
                'weight': 8,
                'description': 'Fitness and health products'
            },
            'home_automation': {
                'keywords': ['smart home', 'alexa', 'google home', 'smart bulb', 'smart plug', 'security camera', 'doorbell camera', 'smart thermostat', 'robot vacuum'],
                'weight': 8,
                'description': 'Smart home and automation'
            },
            'automotive': {
                'keywords': ['car accessories', 'dash cam', 'car charger', 'car mount', 'car organizer', 'car cover', 'tire pressure', 'car vacuum', 'car tools'],
                'weight': 7,
                'description': 'Car and automotive accessories'
            },
            'phone_accessories': {
                'keywords': ['phone case', 'screen protector', 'phone charger', 'wireless charger', 'phone stand', 'car mount', 'phone holder', 'power bank'],
                'weight': 7,
                'description': 'Phone and mobile accessories'
            },
            'kitchen_appliances': {
                'keywords': ['air fryer', 'blender', 'coffee maker', 'instant pot', 'food processor', 'mixer', 'toaster', 'microwave', 'kitchen gadgets'],
                'weight': 6,
                'description': 'Kitchen appliances and gadgets'
            },
            'beauty_personal': {
                'keywords': ['skincare', 'makeup', 'hair tools', 'electric toothbrush', 'hair dryer', 'straightener', 'curling iron', 'face mask', 'beauty tools'],
                'weight': 6,
                'description': 'Beauty and personal care'
            },
            'outdoor_sports': {
                'keywords': ['camping gear', 'hiking boots', 'backpack', 'water bottle', 'outdoor gear', 'sports equipment', 'bicycle', 'skateboard', 'fishing gear'],
                'weight': 6,
                'description': 'Outdoor and sports equipment'
            }
        }
        
        # Engagement boost keywords (add extra points)
        self.engagement_boosters = {
            'urgency': ['new', 'latest', '2024', '2025', 'must have', 'essential', 'best', 'top'],
            'excitement': ['amazing', 'incredible', 'insane', 'crazy', 'epic', 'ultimate', 'perfect', 'revolutionary'],
            'social_proof': ['viral', 'trending', 'popular', 'bestseller', 'rated', 'reviewed', 'recommended'],
            'curiosity': ['secret', 'hidden', 'unknown', 'surprising', 'shocking', 'mysterious', 'discover'],
            'numbers': ['top 5', 'top 10', 'best 5', 'best 10', '5 best', '10 best']
        }
        
        # Low-retention categories to avoid
        self.low_retention_categories = [
            'office supplies', 'cleaning supplies', 'basic tools', 'screws', 'bolts', 'nuts', 
            'industrial', 'medical', 'books', 'textbooks', 'academic', 'business cards',
            'generic', 'basic', 'standard', 'regular', 'simple', 'plain', 'boring'
        ]
    
    def calculate_retention_score(self, title: str) -> Tuple[int, List[str]]:
        """Calculate retention score for a title"""
        score = 0
        reasons = []
        title_lower = title.lower()
        
        # Check high-retention categories
        for category, data in self.high_retention_categories.items():
            for keyword in data['keywords']:
                if keyword in title_lower:
                    score += data['weight']
                    reasons.append(f"+{data['weight']} ({category}: {keyword})")
                    break  # Only count once per category
        
        # Check engagement boosters
        for boost_type, keywords in self.engagement_boosters.items():
            for keyword in keywords:
                if keyword in title_lower:
                    score += 2
                    reasons.append(f"+2 ({boost_type}: {keyword})")
                    break  # Only count once per boost type
        
        # Penalize low-retention categories
        for low_keyword in self.low_retention_categories:
            if low_keyword in title_lower:
                score -= 3
                reasons.append(f"-3 (low retention: {low_keyword})")
        
        # Bonus for specific high-engagement patterns
        if re.search(r'top \d+', title_lower):
            score += 3
            reasons.append("+3 (top N format)")
        
        if re.search(r'best \d+', title_lower):
            score += 3
            reasons.append("+3 (best N format)")
        
        if re.search(r'review|comparison|vs|versus', title_lower):
            score += 2
            reasons.append("+2 (review/comparison)")
        
        if len(title) > 60:  # Longer titles tend to be more descriptive
            score += 1
            reasons.append("+1 (descriptive length)")
        
        return score, reasons
    
    async def get_all_titles(self) -> List[Dict]:
        """Get all titles from Airtable"""
        print("📋 Fetching all titles from Airtable...")
        
        # Get all records (not just pending ones)
        all_records = []
        offset = None
        
        while True:
            try:
                # Use Airtable API to get all records
                if offset:
                    records = self.airtable_server.airtable.get_all(offset=offset)
                else:
                    records = self.airtable_server.airtable.get_all()
                
                if not records:
                    break
                
                all_records.extend(records)
                
                # Check if there are more records
                if len(records) < 100:  # Airtable returns max 100 records per request
                    break
                    
            except Exception as e:
                print(f"Error fetching records: {e}")
                break
        
        print(f"✅ Found {len(all_records)} total titles")
        return all_records
    
    async def filter_and_rank_titles(self) -> Dict:
        """Filter and rank all titles by retention score"""
        print("🎯 Starting title filtering and ranking process...")
        
        # Get all titles
        all_records = await self.get_all_titles()
        
        # Calculate scores for all titles
        scored_titles = []
        
        for record in all_records:
            title = record['fields'].get('Title', '')
            if not title:
                continue
            
            score, reasons = self.calculate_retention_score(title)
            
            scored_titles.append({
                'record_id': record['id'],
                'title': title,
                'score': score,
                'reasons': reasons,
                'current_status': record['fields'].get('Status', 'Pending')
            })
        
        # Sort by score (highest first)
        scored_titles.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"📊 Scored {len(scored_titles)} titles")
        
        # Take top 1500 titles
        top_1500 = scored_titles[:1500]
        remaining = scored_titles[1500:]
        
        print(f"✅ Selected top 1500 titles (scores: {top_1500[0]['score']} to {top_1500[-1]['score']})")
        print(f"📝 {len(remaining)} titles will be set to 'NotUsed'")
        
        # Show some examples
        print("\n🏆 TOP 10 HIGHEST SCORING TITLES:")
        for i, title_data in enumerate(top_1500[:10], 1):
            print(f"  {i}. Score: {title_data['score']} - {title_data['title'][:60]}...")
            if title_data['reasons']:
                print(f"     Reasons: {', '.join(title_data['reasons'][:3])}")
        
        print("\n⬇️ BOTTOM 10 OF SELECTED TITLES:")
        for i, title_data in enumerate(top_1500[-10:], len(top_1500)-9):
            print(f"  {i}. Score: {title_data['score']} - {title_data['title'][:60]}...")
        
        return {
            'top_1500': top_1500,
            'remaining': remaining,
            'total_processed': len(scored_titles)
        }
    
    async def update_title_statuses(self, filtering_results: Dict) -> None:
        """Update title statuses in Airtable"""
        print("📝 Updating title statuses in Airtable...")
        
        top_1500 = filtering_results['top_1500']
        remaining = filtering_results['remaining']
        
        # Update remaining titles to 'NotUsed'
        batch_size = 10  # Process in small batches to avoid API limits
        
        print(f"🚫 Setting {len(remaining)} titles to 'NotUsed' status...")
        
        for i in range(0, len(remaining), batch_size):
            batch = remaining[i:i+batch_size]
            
            for title_data in batch:
                try:
                    await self.airtable_server.update_record(
                        title_data['record_id'],
                        {'Status': 'NotUsed'}
                    )
                except Exception as e:
                    print(f"Error updating {title_data['record_id']}: {e}")
            
            print(f"  Processed {min(i+batch_size, len(remaining))}/{len(remaining)} titles")
        
        # Ensure top 1500 titles are set to 'Pending' if not already processed
        print(f"✅ Ensuring top 1500 titles are available for processing...")
        
        pending_count = 0
        for title_data in top_1500:
            if title_data['current_status'] not in ['Completed', 'Processing']:
                try:
                    await self.airtable_server.update_record(
                        title_data['record_id'],
                        {'Status': 'Pending'}
                    )
                    pending_count += 1
                except Exception as e:
                    print(f"Error updating {title_data['record_id']}: {e}")
        
        print(f"✅ {pending_count} titles set to 'Pending' status")
        print(f"🎯 Title filtering complete!")
        
        # Create summary report
        return {
            'top_1500_count': len(top_1500),
            'not_used_count': len(remaining),
            'pending_count': pending_count,
            'highest_score': top_1500[0]['score'],
            'lowest_selected_score': top_1500[-1]['score']
        }
    
    async def generate_filtering_report(self, filtering_results: Dict) -> None:
        """Generate a detailed filtering report"""
        print("\n" + "="*80)
        print("🎯 TITLE FILTERING REPORT")
        print("="*80)
        
        top_1500 = filtering_results['top_1500']
        remaining = filtering_results['remaining']
        
        print(f"📊 Total titles processed: {filtering_results['total_processed']}")
        print(f"✅ Selected for use: {len(top_1500)} titles")
        print(f"🚫 Set to NotUsed: {len(remaining)} titles")
        print(f"🏆 Highest score: {top_1500[0]['score']}")
        print(f"📉 Lowest selected score: {top_1500[-1]['score']}")
        
        # Category breakdown
        print(f"\n📋 CATEGORY BREAKDOWN (Top 1500):")
        category_counts = {}
        
        for title_data in top_1500:
            title_lower = title_data['title'].lower()
            for category, data in self.high_retention_categories.items():
                for keyword in data['keywords']:
                    if keyword in title_lower:
                        category_counts[category] = category_counts.get(category, 0) + 1
                        break
        
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} titles")
        
        print(f"\n🎯 SEQUENTIAL PROCESSING ORDER:")
        print(f"  Titles will be processed in rank order (1-1500)")
        print(f"  No random selection - consistent processing order")
        print(f"  Test and Production workflows will use same sequence")
        
        print("="*80)

async def main():
    """Main function to run the title filtering system"""
    print("🚀 Starting Title Filtering System for High-Retention Social Media Content")
    
    # Load configuration
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Initialize filter system
    filter_system = TitleFilterSystem(config)
    
    try:
        # Filter and rank titles
        filtering_results = await filter_system.filter_and_rank_titles()
        
        # Update statuses in Airtable
        summary = await filter_system.update_title_statuses(filtering_results)
        
        # Generate report
        await filter_system.generate_filtering_report(filtering_results)
        
        print(f"\n✅ Title filtering complete!")
        print(f"🎯 Ready for sequential processing of top 1500 high-retention titles")
        
    except Exception as e:
        print(f"❌ Error in title filtering: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())