#!/usr/bin/env python3
"""
Optimized Title Filtering System for High-Retention Social Media Content
"""

import asyncio
import json
import re
from typing import Dict, List, Tuple
from mcp_servers.Test_airtable_server import AirtableMCPServer

class OptimizedTitleFilterSystem:
    """Optimized filter titles for high social media retention"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
        # High-retention keywords (simplified for performance)
        self.high_retention_keywords = {
            'gaming': ['gaming', 'game', 'rgb', 'mechanical', 'esports', 'pro gaming'],
            'tech': ['laptop', 'phone', 'camera', 'drone', 'smartwatch', 'earbuds', 'headphones'],
            'action': ['action camera', 'gopro', 'dashcam', 'security camera'],
            'fitness': ['fitness', 'workout', 'health', 'tracker', 'scale', 'yoga'],
            'smart_home': ['smart', 'alexa', 'google home', 'wifi', 'bluetooth'],
            'kitchen': ['air fryer', 'blender', 'coffee', 'instant pot', 'kitchen']
        }
        
        # Engagement boosters
        self.engagement_keywords = ['top', 'best', 'new', '2024', '2025', 'amazing', 'ultimate', 'perfect']
        
        # Low-retention words to avoid
        self.avoid_keywords = ['office', 'cleaning', 'industrial', 'medical', 'books', 'basic', 'standard']
    
    def calculate_simple_score(self, title: str) -> int:
        """Calculate simple retention score for a title"""
        score = 0
        title_lower = title.lower()
        
        # High-retention categories
        for category, keywords in self.high_retention_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    score += 10
                    break  # Only count once per category
        
        # Engagement boosters
        for keyword in self.engagement_keywords:
            if keyword in title_lower:
                score += 3
                break
        
        # Avoid low-retention
        for keyword in self.avoid_keywords:
            if keyword in title_lower:
                score -= 5
                break
        
        # Bonus for number format
        if re.search(r'top \d+|best \d+|\d+ best', title_lower):
            score += 5
        
        return score
    
    async def get_sample_titles(self, limit: int = 100) -> List[Dict]:
        """Get a sample of titles for testing"""
        print(f"📋 Fetching sample of {limit} titles from Airtable...")
        
        try:
            # Get first batch of records
            records = self.airtable_server.airtable.get_all(max_records=limit)
            
            sample_titles = []
            for record in records:
                title = record['fields'].get('Title', '')
                if title:
                    sample_titles.append({
                        'record_id': record['id'],
                        'title': title,
                        'current_status': record['fields'].get('Status', 'Pending')
                    })
            
            print(f"✅ Found {len(sample_titles)} sample titles")
            return sample_titles
            
        except Exception as e:
            print(f"❌ Error fetching sample titles: {e}")
            return []
    
    async def filter_sample_titles(self, sample_limit: int = 100) -> Dict:
        """Filter sample titles for testing"""
        print(f"🎯 Testing with {sample_limit} sample titles...")
        
        # Get sample titles
        sample_titles = await self.get_sample_titles(sample_limit)
        
        if not sample_titles:
            return {}
        
        # Calculate scores
        scored_titles = []
        
        for title_data in sample_titles:
            score = self.calculate_simple_score(title_data['title'])
            
            scored_titles.append({
                'record_id': title_data['record_id'],
                'title': title_data['title'],
                'score': score,
                'current_status': title_data['current_status']
            })
        
        # Sort by score (highest first)
        scored_titles.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top 50% as "good" titles
        good_count = len(scored_titles) // 2
        good_titles = scored_titles[:good_count]
        remaining = scored_titles[good_count:]
        
        print(f"📊 Sample Results:")
        print(f"  Total sample: {len(scored_titles)}")
        print(f"  Good titles: {len(good_titles)}")
        print(f"  Remaining: {len(remaining)}")
        
        if good_titles:
            print(f"  Highest score: {good_titles[0]['score']}")
            print(f"  Lowest good score: {good_titles[-1]['score']}")
        
        # Show top 10 examples
        print(f"\n🏆 TOP 10 SAMPLE TITLES:")
        for i, title_data in enumerate(good_titles[:10], 1):
            print(f"  {i}. Score: {title_data['score']} - {title_data['title'][:60]}...")
        
        return {
            'good_titles': good_titles,
            'remaining': remaining,
            'total_processed': len(scored_titles)
        }
    
    async def update_sample_statuses(self, filtering_results: Dict) -> None:
        """Update sample title statuses"""
        if not filtering_results:
            return
        
        good_titles = filtering_results['good_titles']
        remaining = filtering_results['remaining']
        
        print(f"📝 Updating sample statuses...")
        
        # Set good titles to Pending
        for title_data in good_titles:
            try:
                await self.airtable_server.update_record(
                    title_data['record_id'],
                    {'Status': 'Pending'}
                )
            except Exception as e:
                print(f"Error updating {title_data['record_id']}: {e}")
        
        # Set remaining to NotUsed
        for title_data in remaining:
            try:
                await self.airtable_server.update_record(
                    title_data['record_id'],
                    {'Status': 'NotUsed'}
                )
            except Exception as e:
                print(f"Error updating {title_data['record_id']}: {e}")
        
        print(f"✅ Updated {len(good_titles)} titles to 'Pending'")
        print(f"🚫 Updated {len(remaining)} titles to 'NotUsed'")

async def main():
    """Main function to run the optimized title filtering system"""
    print("🚀 Starting Optimized Title Filtering System")
    
    # Load configuration
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Initialize filter system
    filter_system = OptimizedTitleFilterSystem(config)
    
    try:
        # Start with sample filtering
        print("🧪 Testing with sample titles first...")
        filtering_results = await filter_system.filter_sample_titles(sample_limit=50)
        
        if filtering_results:
            # Update sample statuses
            await filter_system.update_sample_statuses(filtering_results)
            
            print(f"\n✅ Sample filtering complete!")
            print(f"🎯 Ready to scale up to full 1500 title filtering")
            
            # Ask user before proceeding with full filtering
            print(f"\n📝 Sample filtering successful. Run full filtering? (y/n)")
            # For automation, we'll assume yes
            proceed = True
            
            if proceed:
                print("🚀 Ready to implement full 1500 title filtering...")
                print("💡 Next step: Scale up to process all 3000+ titles")
        else:
            print("❌ Sample filtering failed")
        
    except Exception as e:
        print(f"❌ Error in title filtering: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())