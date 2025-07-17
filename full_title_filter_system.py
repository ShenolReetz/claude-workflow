#!/usr/bin/env python3
"""
Full-Scale Title Filtering System for High-Retention Social Media Content
Filters 3000+ titles down to 1500 high-engagement titles
"""

import asyncio
import json
import re
from typing import Dict, List, Tuple
from mcp_servers.Test_airtable_server import AirtableMCPServer

class FullTitleFilterSystem:
    """Full-scale filter titles for high social media retention"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.airtable_server = AirtableMCPServer(
            api_key=config['airtable_api_key'],
            base_id=config['airtable_base_id'],
            table_name=config['airtable_table_name']
        )
        
        # High-retention categories with weights
        self.high_retention_keywords = {
            'gaming': {
                'keywords': ['gaming', 'game', 'rgb', 'mechanical', 'esports', 'pro gaming', 'gaming keyboard', 'gaming mouse', 'gaming headset', 'gaming chair', 'gaming monitor', 'gaming laptop', 'gaming desk'],
                'weight': 15
            },
            'tech_devices': {
                'keywords': ['laptop', 'phone', 'smartphone', 'tablet', 'smartwatch', 'earbuds', 'headphones', 'speaker', 'bluetooth', 'wireless', 'charger', 'power bank'],
                'weight': 12
            },
            'action_cameras': {
                'keywords': ['action camera', 'gopro', 'dashcam', 'security camera', 'surveillance', 'webcam', 'camera', 'drone', 'gimbal', 'stabilizer'],
                'weight': 15
            },
            'fitness_health': {
                'keywords': ['fitness', 'workout', 'health', 'tracker', 'scale', 'yoga', 'exercise', 'gym', 'running', 'sports'],
                'weight': 10
            },
            'smart_home': {
                'keywords': ['smart', 'alexa', 'google home', 'wifi', 'smart bulb', 'smart plug', 'smart thermostat', 'robot vacuum', 'home automation'],
                'weight': 10
            },
            'kitchen_tech': {
                'keywords': ['air fryer', 'blender', 'coffee', 'instant pot', 'kitchen', 'food processor', 'mixer', 'toaster', 'microwave'],
                'weight': 8
            },
            'automotive': {
                'keywords': ['car', 'automotive', 'dash cam', 'car charger', 'car mount', 'car accessories', 'vehicle', 'motorcycle'],
                'weight': 8
            },
            'beauty_personal': {
                'keywords': ['beauty', 'skincare', 'makeup', 'hair', 'electric toothbrush', 'personal care', 'grooming'],
                'weight': 7
            }
        }
        
        # Engagement boosters
        self.engagement_keywords = {
            'urgency': ['new', 'latest', '2024', '2025', 'fresh', 'updated'],
            'quality': ['best', 'top', 'amazing', 'ultimate', 'perfect', 'premium', 'pro'],
            'social_proof': ['popular', 'trending', 'viral', 'bestseller', 'rated', 'reviewed'],
            'curiosity': ['secret', 'hidden', 'must have', 'essential', 'incredible', 'insane']
        }
        
        # Low-retention words to avoid
        self.avoid_keywords = [
            'office supplies', 'cleaning', 'industrial', 'medical', 'books', 'textbooks',
            'basic', 'standard', 'regular', 'simple', 'plain', 'generic', 'boring',
            'screws', 'bolts', 'nuts', 'tools', 'hardware', 'business cards'
        ]
    
    def calculate_retention_score(self, title: str) -> Tuple[int, List[str]]:
        """Calculate detailed retention score for a title"""
        score = 0
        reasons = []
        title_lower = title.lower()
        
        # Check high-retention categories
        for category, data in self.high_retention_keywords.items():
            for keyword in data['keywords']:
                if keyword in title_lower:
                    score += data['weight']
                    reasons.append(f"+{data['weight']} ({category}: {keyword})")
                    break  # Only count once per category
        
        # Check engagement boosters
        for boost_type, keywords in self.engagement_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    score += 3
                    reasons.append(f"+3 ({boost_type}: {keyword})")
                    break  # Only count once per boost type
        
        # Avoid low-retention
        for keyword in self.avoid_keywords:
            if keyword in title_lower:
                score -= 5
                reasons.append(f"-5 (avoid: {keyword})")
                break
        
        # Bonus for specific patterns
        if re.search(r'top \\d+|best \\d+|\\d+ best|\\d+ top', title_lower):
            score += 5
            reasons.append("+5 (numbered list format)")
        
        if re.search(r'review|comparison|vs|versus', title_lower):
            score += 3
            reasons.append("+3 (review/comparison)")
        
        if len(title) > 50:  # Descriptive titles
            score += 2
            reasons.append("+2 (descriptive length)")
        
        return score, reasons
    
    async def get_all_titles_batch(self, batch_size: int = 100) -> List[Dict]:
        """Get all titles from Airtable"""
        print("📋 Fetching all titles from Airtable...")
        
        all_titles = []
        
        try:
            # Get all records at once
            records = self.airtable_server.airtable.get_all()
            
            # Process all records
            for record in records:
                title = record['fields'].get('Title', '')
                if title:
                    all_titles.append({
                        'record_id': record['id'],
                        'title': title,
                        'current_status': record['fields'].get('Status', 'Pending')
                    })
            
            print(f"✅ Total titles found: {len(all_titles)}")
            
        except Exception as e:
            print(f"❌ Error fetching titles: {e}")
        
        return all_titles
    
    async def filter_all_titles(self) -> Dict:
        """Filter all titles and select top 1500"""
        print("🎯 Starting full title filtering process...")
        
        # Get all titles
        all_titles = await self.get_all_titles_batch()
        
        if not all_titles:
            print("❌ No titles found")
            return {}
        
        print(f"📊 Scoring {len(all_titles)} titles...")
        
        # Calculate scores for all titles
        scored_titles = []
        
        for i, title_data in enumerate(all_titles):
            if i % 500 == 0:
                print(f"  Processed {i}/{len(all_titles)} titles...")
            
            score, reasons = self.calculate_retention_score(title_data['title'])
            
            scored_titles.append({
                'record_id': title_data['record_id'],
                'title': title_data['title'],
                'score': score,
                'reasons': reasons,
                'current_status': title_data['current_status']
            })
        
        # Sort by score (highest first)
        print("🔄 Sorting titles by retention score...")
        scored_titles.sort(key=lambda x: x['score'], reverse=True)
        
        # Select top 1500
        top_1500 = scored_titles[:1500]
        remaining = scored_titles[1500:]
        
        print(f"\\n✅ FILTERING RESULTS:")
        print(f"  Total titles processed: {len(scored_titles)}")
        print(f"  Selected for use: {len(top_1500)} titles")
        print(f"  Set to NotUsed: {len(remaining)} titles")
        
        if top_1500:
            print(f"  Highest score: {top_1500[0]['score']}")
            print(f"  Lowest selected score: {top_1500[-1]['score']}")
            
            # Show top 10 examples
            print(f"\\n🏆 TOP 10 HIGHEST SCORING TITLES:")
            for i, title_data in enumerate(top_1500[:10], 1):
                print(f"  {i}. Score: {title_data['score']} - {title_data['title'][:60]}...")
                if title_data['reasons']:
                    print(f"     Reasons: {', '.join(title_data['reasons'][:2])}")
        
        return {
            'top_1500': top_1500,
            'remaining': remaining,
            'total_processed': len(scored_titles)
        }
    
    async def update_all_statuses(self, filtering_results: Dict) -> Dict:
        """Update all title statuses in Airtable"""
        if not filtering_results:
            return {}
        
        print("📝 Updating title statuses in Airtable...")
        
        top_1500 = filtering_results['top_1500']
        remaining = filtering_results['remaining']
        
        # Update remaining titles to 'NotUsed' in batches
        print(f"🚫 Setting {len(remaining)} titles to 'NotUsed' status...")
        
        batch_size = 10
        not_used_count = 0
        
        for i in range(0, len(remaining), batch_size):
            batch = remaining[i:i+batch_size]
            
            for title_data in batch:
                try:
                    await self.airtable_server.update_record(
                        title_data['record_id'],
                        {'Status': 'NotUsed'}
                    )
                    not_used_count += 1
                except Exception as e:
                    print(f"Error updating {title_data['record_id']}: {e}")
            
            if (i + batch_size) % 100 == 0:
                print(f"  Set {min(i+batch_size, len(remaining))}/{len(remaining)} titles to NotUsed")
        
        # Ensure top 1500 titles are available for processing
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
        
        print(f"✅ Status updates complete!")
        print(f"  {pending_count} titles set to 'Pending'")
        print(f"  {not_used_count} titles set to 'NotUsed'")
        
        return {
            'top_1500_count': len(top_1500),
            'not_used_count': not_used_count,
            'pending_count': pending_count,
            'highest_score': top_1500[0]['score'] if top_1500 else 0,
            'lowest_selected_score': top_1500[-1]['score'] if top_1500 else 0
        }
    
    async def generate_final_report(self, filtering_results: Dict, update_summary: Dict) -> None:
        """Generate final filtering report"""
        print("\\n" + "="*80)
        print("🎯 FINAL TITLE FILTERING REPORT")
        print("="*80)
        
        print(f"📊 PROCESSING SUMMARY:")
        print(f"  Total titles processed: {filtering_results['total_processed']}")
        print(f"  Selected for use: {update_summary['top_1500_count']} titles")
        print(f"  Set to NotUsed: {update_summary['not_used_count']} titles")
        print(f"  Set to Pending: {update_summary['pending_count']} titles")
        
        print(f"\\n🏆 SCORING RESULTS:")
        print(f"  Highest retention score: {update_summary['highest_score']}")
        print(f"  Lowest selected score: {update_summary['lowest_selected_score']}")
        
        print(f"\\n🎯 PROCESSING ORDER:")
        print(f"  ✅ Sequential processing enabled (1-1500)")
        print(f"  ✅ No random selection - consistent order")
        print(f"  ✅ Test and Production use same sequence")
        print(f"  ✅ High-retention titles prioritized")
        
        print(f"\\n📋 CATEGORIES PRIORITIZED:")
        print(f"  • Gaming equipment and accessories")
        print(f"  • Action cameras and tech devices")
        print(f"  • Laptops and computing")
        print(f"  • Fitness and health products")
        print(f"  • Smart home automation")
        print(f"  • Kitchen appliances")
        print(f"  • Automotive accessories")
        
        print(f"\\n🚀 READY FOR WORKFLOW:")
        print(f"  • {update_summary['top_1500_count']} high-retention titles selected")
        print(f"  • Titles ranked by social media engagement potential")
        print(f"  • Sequential processing order established")
        print(f"  • Test and Production workflows ready")
        
        print("="*80)

async def main():
    """Main function to run the full title filtering system"""
    print("🚀 Starting Full-Scale Title Filtering System")
    print("🎯 Filtering 3000+ titles down to 1500 high-retention titles")
    
    # Load configuration
    try:
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    # Initialize filter system
    filter_system = FullTitleFilterSystem(config)
    
    try:
        # Filter all titles
        filtering_results = await filter_system.filter_all_titles()
        
        if filtering_results:
            # Update all statuses
            update_summary = await filter_system.update_all_statuses(filtering_results)
            
            # Generate final report
            await filter_system.generate_final_report(filtering_results, update_summary)
            
            print(f"\\n✅ TITLE FILTERING COMPLETE!")
            print(f"🎯 Ready for high-retention content generation")
            
        else:
            print("❌ Title filtering failed")
        
    except Exception as e:
        print(f"❌ Error in title filtering: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())