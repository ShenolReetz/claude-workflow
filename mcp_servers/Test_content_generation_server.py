import asyncio
import json
import random
from typing import Dict, List, Optional

class ContentGenerationMCPServer:
    def __init__(self, anthropic_api_key: str):
        # TEST MODE: No actual API calls
        self.api_key = anthropic_api_key
        
        # Hardcoded templates for different categories
        self.category_templates = {
            'electronics': {
                'keywords': ['best 2025', 'tech review', 'gadget', 'smart device', 'electronics', 
                            'digital', 'wireless', 'bluetooth', 'USB-C', 'portable',
                            'amazon finds', 'tech deals', 'budget tech', 'must have',
                            'unboxing', 'comparison', 'top rated', 'viral tech', 'trending', 'TikTok'],
                'title_templates': [
                    "🔥 TOP 5 {category} That BROKE The Internet in 2025!",
                    "⚡ These 5 {category} Are FLYING Off Amazon Shelves!", 
                    "🎯 5 VIRAL {category} Everyone's Buying Right Now!",
                    "💸 Best {category} Under $100 You NEED in 2025!"
                ],
                'intro_templates': [
                    "These 5 products are selling out EVERYWHERE!",
                    "I found the 5 most viral products on Amazon!",
                    "You won't believe these insane deals I found!",
                    "Everyone's buying these 5 products right now!"
                ]
            },
            'home': {
                'keywords': ['home gadgets', 'smart home', 'organization', 'cleaning', 'kitchen',
                            'bedroom', 'bathroom', 'decor', 'space saving', 'minimalist',
                            'home improvement', 'DIY', 'amazon home', 'home hacks', 'cozy',
                            'aesthetic', 'room makeover', 'home essentials', 'viral home', 'TikTok home'],
                'title_templates': [
                    "🏠 5 Home Gadgets That Will CHANGE Your Life in 2025!",
                    "✨ Top 5 Viral Home Products Everyone Needs!",
                    "🎁 5 Amazon Home Finds Under $50 You'll LOVE!",
                    "💡 These 5 Home Products Are GENIUS!"
                ],
                'intro_templates': [
                    "Your home will never be the same after these!",
                    "These 5 products transformed my entire home!",
                    "I can't believe I lived without these!",
                    "These home finds are going viral for a reason!"
                ]
            },
            'fashion': {
                'keywords': ['fashion tech', 'wearable', 'accessories', 'style', 'trendy',
                            'fashionable', 'outfit', 'wardrobe', 'designer', 'luxury',
                            'fashion finds', 'style tips', 'fashion haul', 'OOTD', 'lookbook',
                            'fashion trends', 'style guide', 'fashion must haves', 'viral fashion', 'TikTok fashion'],
                'title_templates': [
                    "👗 5 Fashion Tech Items Taking Over 2025!",
                    "💎 Top 5 Trending Accessories Everyone Wants!",
                    "🛍️ 5 Viral Fashion Finds You Need NOW!",
                    "✨ Best Fashion Tech Under $75 on Amazon!"
                ],
                'intro_templates': [
                    "These fashion finds are breaking the internet!",
                    "Everyone's adding these to their wardrobe!",
                    "You need these trending pieces ASAP!",
                    "These accessories are selling out fast!"
                ]
            },
            'marine_speakers': {
                'keywords': ['marine audio', 'boat speakers', 'waterproof', 'marine stereo', 'boat sound',
                            'marine electronics', 'boat audio', 'nautical', 'marine grade', 'salt resistant',
                            'boat accessories', 'marine tech', 'boat upgrade', 'marine sound system', 'boat life',
                            'marine bluetooth', 'boat party', 'marine amplifier', 'boat entertainment', 'marine subwoofer'],
                'title_templates': [
                    "🚤 TOP 5 Marine Speakers That DOMINATE The Water!",
                    "⚓ 5 Boat Speakers With INSANE Sound Quality!",
                    "🌊 Best Marine Audio Systems Under $200!",
                    "🎵 5 Waterproof Speakers Every Boat NEEDS!"
                ],
                'intro_templates': [
                    "These marine speakers will transform your boat!",
                    "Get ready for the best sound on the water!",
                    "Your boat parties will never be the same!",
                    "These speakers are built for the ocean!"
                ]
            },
            'default': {
                'keywords': ['best 2025', 'top rated', 'amazon finds', 'must have', 'viral',
                            'trending', 'popular', 'review', 'comparison', 'budget',
                            'deals', 'sale', 'discount', 'worth it', 'game changer',
                            'life changing', 'essential', 'recommended', 'favorite', 'TikTok'],
                'title_templates': [
                    "🔥 TOP 5 {category} Everyone's Buying in 2025!",
                    "⭐ 5 {category} With THOUSANDS of 5-Star Reviews!",
                    "💯 Best {category} That Are Actually Worth It!",
                    "🎯 5 Viral {category} You Need to See!"
                ],
                'intro_templates': [
                    "These 5 products are taking over social media!",
                    "I tested the most viral products online!",
                    "You won't believe these incredible finds!",
                    "Everyone's talking about these products!"
                ]
            }
        }
    
    def _get_category_key(self, title: str) -> str:
        """Determine category from title"""
        title_lower = title.lower()
        if any(word in title_lower for word in ['camera', 'photo', 'digital', 'tech', 'gadget', 'electronic']):
            return 'electronics'
        elif any(word in title_lower for word in ['home', 'kitchen', 'cleaning', 'power strip']):
            return 'home'
        elif any(word in title_lower for word in ['fashion', 'watch', 'band', 'accessory', 'wearable']):
            return 'fashion'
        elif any(word in title_lower for word in ['marine', 'boat', 'speaker', 'waterproof', 'nautical']):
            return 'marine_speakers'
        else:
            return 'default'
    
    def _extract_category_name(self, title: str) -> str:
        """Extract category name from title"""
        # Common patterns: "Top 5 X", "Best X", etc.
        patterns = [
            r'top \d+ (.+?)(?:\s+releases|\s+of|\s+in|\s+for|$)',
            r'best (.+?)(?:\s+releases|\s+of|\s+in|\s+for|$)',
            r'new (.+?)(?:\s+releases|\s+of|\s+in|\s+for|$)',
            r'\d+ (.+?)(?:\s+that|\s+you|\s+with|$)'
        ]
        
        import re
        for pattern in patterns:
            match = re.search(pattern, title.lower())
            if match:
                return match.group(1).title()
        
        # Fallback - use middle words
        words = title.split()
        if len(words) > 3:
            return ' '.join(words[2:5]).title()
        return 'Amazing Products'
        
    async def generate_seo_keywords(self, title: str, product_category: str) -> List[str]:
        """TEST MODE: Return hardcoded SEO keywords"""
        try:
            # Determine category
            category_key = self._get_category_key(title)
            template = self.category_templates.get(category_key, self.category_templates['default'])
            
            # Base keywords from template
            keywords = template['keywords'].copy()
            
            # Add title-specific keywords
            title_words = title.lower().split()
            for word in title_words:
                if len(word) > 4 and word not in ['these', 'those', 'there', 'where']:
                    keywords.append(word)
            
            # Add year and trending terms
            keywords.extend(['2025', 'amazon prime', 'free shipping', 'best seller'])
            
            # Shuffle and take 20
            random.shuffle(keywords)
            keywords = keywords[:20]
            
            print(f"✅ TEST MODE: Generated {len(keywords)} SEO keywords")
            return keywords
            
        except Exception as e:
            print(f"Error generating keywords: {e}")
            return ['amazon', 'best', '2025', 'top', 'review']
    
    async def optimize_title(self, original_title: str, keywords: List[str]) -> str:
        """TEST MODE: Return hardcoded optimized title"""
        try:
            # Get category and template
            category_key = self._get_category_key(original_title)
            template = self.category_templates.get(category_key, self.category_templates['default'])
            
            # Pick a random title template
            title_template = random.choice(template['title_templates'])
            
            # Extract category from original title
            category_name = self._extract_category_name(original_title)
            
            # Format the title
            optimized_title = title_template.format(category=category_name)
            
            # Ensure it's under 60 characters
            if len(optimized_title) > 60:
                optimized_title = optimized_title[:57] + "..."
            
            print(f"✅ TEST MODE: Optimized title: {optimized_title}")
            return optimized_title
            
        except Exception as e:
            print(f"Error optimizing title: {e}")
            return original_title[:60]
    
    async def generate_countdown_script(self, title: str, keywords: List[str]) -> Dict:
        """TEST MODE: Generate hardcoded countdown script"""
        try:
            # Get category for appropriate intro
            category_key = self._get_category_key(title)
            template = self.category_templates.get(category_key, self.category_templates['default'])
            
            # Hardcoded product examples by category
            category_products = {
                'electronics': [
                    {"name": "Anker PowerCore 10000", "features": ["10000mAh", "Ultra-compact", "Fast charging"], 
                     "script": "At number 5, the Anker PowerCore 10000! This ultra-compact power bank fits in your pocket but packs enough juice to charge your phone three times!"},
                    {"name": "JBL Flip 6 Portable Speaker", "features": ["Waterproof", "12-hour battery", "PartyBoost"],
                     "script": "Number 4 is the JBL Flip 6! Waterproof, dustproof, and with 12 hours of playtime, this speaker brings the party anywhere you go!"},
                    {"name": "Logitech MX Master 3S", "features": ["8K DPI", "Quiet clicks", "Multi-device"],
                     "script": "Coming in at number 3, the Logitech MX Master 3S! With silent clicks and ultra-smooth scrolling, it's the ultimate productivity mouse!"},
                    {"name": "Sony WH-1000XM5", "features": ["Industry-leading ANC", "30-hour battery", "Hi-Res audio"],
                     "script": "Number 2 goes to Sony WH-1000XM5! These headphones have the best noise canceling on the market and crystal-clear call quality!"},
                    {"name": "Apple AirPods Pro 2nd Gen", "features": ["Adaptive Transparency", "Personalized Spatial Audio", "MagSafe"],
                     "script": "And the number 1 spot? Apple AirPods Pro 2nd Gen! With adaptive noise control and the new H2 chip, these are simply unbeatable!"}
                ],
                'home': [
                    {"name": "Bissell Little Green Machine", "features": ["Portable", "Deep clean", "Pet-friendly"],
                     "script": "Starting at 5, the Bissell Little Green! This portable cleaner tackles any spill or stain in seconds. Perfect for pets and kids!"},
                    {"name": "Instant Vortex Plus Air Fryer", "features": ["6-quart", "6-in-1 functions", "EvenCrisp"],
                     "script": "Number 4, the Instant Vortex Plus! Air fry, roast, broil, and more with 95% less oil. Your kitchen game-changer is here!"},
                    {"name": "Shark IQ Robot Vacuum", "features": ["Self-emptying", "Home mapping", "Pet hair pickup"],
                     "script": "At number 3, the Shark IQ Robot! It empties itself for up to 45 days and maps your home for perfect cleaning every time!"},
                    {"name": "Ninja Foodi 11-in-1", "features": ["Pressure cook", "Air fry", "Slow cook"],
                     "script": "Number 2 is the Ninja Foodi 11-in-1! Replace your entire kitchen with this one device that does literally everything!"},
                    {"name": "Dyson V15 Detect", "features": ["Laser detection", "230AW suction", "LCD screen"],
                     "script": "Taking the top spot, the Dyson V15 Detect! Its laser reveals invisible dust and the LCD shows exactly what you're cleaning!"}
                ],
                'marine_speakers': [
                    {"name": "Polk Audio MM652", "features": ["UV resistant", "IP56 rated", "Full-range"],
                     "script": "At number 5, the Polk Audio MM652! These speakers are built for salt, sun, and spray with incredible full-range sound!"},
                    {"name": "BOSS Audio MCK632WB.64", "features": ["500W system", "Bluetooth", "All-weather"],
                     "script": "Number 4 brings the BOSS Audio marine package! Complete 500-watt system with Bluetooth and weatherproof remotes included!"},
                    {"name": "Kenwood KFC-1653MRW", "features": ["Peak power handling", "Water-resistant", "LED lighting"],
                     "script": "Coming in third, Kenwood marine speakers with built-in LED lights! Your boat will sound amazing and look incredible at night!"},
                    {"name": "JBL MS6520 180W", "features": ["Plus One woofers", "Balanced dome tweeters", "Marine-rated"],
                     "script": "Number 2 goes to JBL MS6520! With Plus One cone technology, these deliver concert-quality sound even in rough seas!"},
                    {"name": "Rockford Fosgate M2-65B", "features": ["Color Optix LED", "Element Ready", "Premium sound"],
                     "script": "And number 1? Rockford Fosgate M2-65B! With customizable LED lighting and audiophile-grade sound, these are the ultimate marine speakers!"}
                ],
                'fashion': [
                    {"name": "Fitbit Charge 5", "features": ["EDA sensor", "Built-in GPS", "7-day battery"],
                     "script": "Starting at 5, the Fitbit Charge 5! Track stress, sleep, and workouts with the most advanced fitness tracker available!"},
                    {"name": "Ray-Ban Smart Glasses", "features": ["Built-in camera", "Open-ear audio", "Voice control"],
                     "script": "Number 4, Ray-Ban smart glasses! Take photos, make calls, and listen to music while looking absolutely stylish!"},
                    {"name": "Oura Ring Gen3", "features": ["Sleep tracking", "Heart rate", "Temperature"],
                     "script": "At number 3, the Oura Ring! This tiny ring tracks everything from sleep to readiness with incredible accuracy!"},
                    {"name": "Apple Watch Series 9", "features": ["Double tap gesture", "Precision finding", "Carbon neutral"],
                     "script": "Number 2 is the Apple Watch Series 9! With the new double-tap gesture and brighter display, it's smarter than ever!"},
                    {"name": "Theragun Mini", "features": ["Ultra-portable", "150-min battery", "QuietForce"],
                     "script": "Taking the top spot, Theragun Mini! This pocket-sized massager delivers professional-grade muscle treatment anywhere!"}
                ]
            }
            
            # Get products for this category
            products = category_products.get(category_key, category_products['electronics'])
            
            # Pick intro
            intro = random.choice(template['intro_templates'])
            
            # Format products for script
            script_products = []
            for i, product in enumerate(products):
                script_products.append({
                    "rank": 5 - i,
                    "name": product["name"],
                    "script": product["script"],
                    "key_features": product["features"]
                })
            
            script_data = {
                "intro": intro,
                "products": script_products,
                "outro": "Which one are you getting? All links in the description below!",
                "total_duration": "58",
                "hook_phrases": ["selling out", "viral", "game-changer", "must-have"]
            }
            
            print(f"✅ TEST MODE: Generated countdown script with {len(script_data['products'])} products")
            return script_data
            
        except Exception as e:
            print(f"Error generating script: {e}")
            return {}
    
    async def generate_blog_post(self, title: str, script_data: Dict, keywords: List[str]) -> str:
        """TEST MODE: Generate hardcoded blog post"""
        try:
            # Extract products from script_data
            products_info = ""
            if 'products' in script_data:
                for product in script_data['products']:
                    products_info += f"#{product.get('rank', 'N/A')}: {product.get('name', 'N/A')} - {product.get('script', 'N/A')}\n"
            
            # Generate hardcoded blog post
            blog_post = f"""# {title}

In this comprehensive review, I'll break down the top 5 products that are absolutely worth your money in 2025.

## Product Reviews

{products_info}

## FAQ Section

**Q: Are these products really worth buying?**
A: Yes, all products featured have been carefully selected based on customer reviews and ratings.

**Q: Where can I buy these products?**
A: All products are available on Amazon with fast shipping.

## Conclusion

These products represent the best value and quality in their respective categories. Watch our full video review for detailed analysis!

*This post contains affiliate links. As an Amazon Associate, I earn from qualifying purchases at no extra cost to you.*"""
            
            print(f"✅ TEST MODE: Generated blog post ({len(blog_post)} characters)")
            return blog_post
            
        except Exception as e:
            print(f"Error generating blog post: {e}")
            return "Basic blog post content"
    
    async def generate_seo_keywords_with_products(self, title: str, product_names: List[str]) -> List[str]:
        """TEST MODE: Generate hardcoded SEO keywords using product data"""
        try:
            # Use the existing hardcoded keyword generation
            keywords = await self.generate_seo_keywords(title, 'products')
            
            # Add product-specific keywords
            for product_name in product_names[:3]:
                if product_name:
                    # Extract brand name (usually first word)
                    brand = product_name.split()[0]
                    if len(brand) > 2:
                        keywords.append(brand.lower())
            
            print(f"✅ TEST MODE: Generated {len(keywords)} SEO keywords with product data")
            return keywords[:20]
            
        except Exception as e:
            print(f"Error generating keywords with products: {e}")
            return ['amazon', 'review', '2025', 'best', 'top']
    
    async def generate_countdown_script_with_products(self, title: str, keywords: List[str], products: List[Dict]) -> Dict:
        """TEST MODE: Generate hardcoded countdown script using actual product data"""
        try:
            # Get category for appropriate intro
            category_key = self._get_category_key(title)
            template = self.category_templates.get(category_key, self.category_templates['default'])
            
            # Use actual product data but with hardcoded script structure
            intro = random.choice(template['intro_templates'])
            
            script_data = {
                "intro": intro,
                "products": [],
                "outro": "Which one are you getting? All links in the description below!"
            }
            
            # Generate scripts for actual products
            for i, product in enumerate(products[:5]):
                rank = 5 - i
                product_name = product.get('title', f'Product {rank}')[:50]
                price = product.get('price', 'N/A')
                rating = product.get('rating', '4.5')
                
                script_templates = [
                    f"At number {rank}, the {product_name}! With {rating} stars and amazing features!",
                    f"Coming in at #{rank}, {product_name}! Priced at just ${price} with incredible value!",
                    f"Number {rank} goes to {product_name}! {rating} stars from thousands of happy customers!",
                    f"At #{rank}, we have {product_name}! Outstanding quality at ${price}!",
                    f"#{rank} on our list: {product_name}! {rating}-star rating speaks for itself!"
                ]
                
                script_data["products"].append({
                    "rank": rank,
                    "name": product_name,
                    "script": script_templates[i % len(script_templates)],
                    "price": str(price),
                    "rating": str(rating)
                })
            
            print(f"✅ TEST MODE: Generated countdown script with {len(script_data['products'])} products")
            return script_data
            
        except Exception as e:
            print(f"Error generating countdown script with products: {e}")
            return {}
    
    async def generate_multi_platform_keywords(self, title: str, products: List[Dict]) -> Dict[str, List[str]]:
        """TEST MODE: Generate hardcoded platform-specific keywords"""
        try:
            # Get category
            category_key = self._get_category_key(title)
            base_keywords = self.category_templates[category_key]['keywords']
            
            # Extract product brands if available
            product_brands = []
            for p in products[:5]:
                if p.get('title'):
                    # Extract brand name (usually first word)
                    brand = p['title'].split()[0]
                    if brand not in ['The', 'A', 'An'] and len(brand) > 2:
                        product_brands.append(brand.lower())
            
            # YouTube Keywords (20)
            youtube_keywords = [
                "amazon finds 2025", "best tech 2025", "top 5 review", 
                "viral products", "must have gadgets", "amazon haul",
                "tech review 2025", "unboxing video", "product comparison",
                "best sellers amazon", "budget tech finds", "worth buying"
            ]
            youtube_keywords.extend(base_keywords[:8])
            youtube_keywords.extend(product_brands[:3])
            youtube_keywords = list(set(youtube_keywords))[:20]
            
            # Instagram Hashtags (30)
            instagram_hashtags = [
                "#amazonfinds", "#amazonfinds2025", "#techreview", "#gadgets",
                "#techtok", "#amazonmusthaves", "#techfinds", "#amazonhaul",
                "#viralproducts", "#amazonfavorites", "#techgadgets", "#smarttech",
                "#amazonprime", "#techdeals", "#gadgetlover", "#techcommunity",
                "#amazonbestsellers", "#techlifestyle", "#instatech", "#techgram"
            ]
            category_tags = {
                'electronics': ["#electronics", "#techie", "#gadgetaddict", "#techlove"],
                'home': ["#smarthome", "#hometech", "#homegadgets", "#homeimprovement"],
                'fashion': ["#fashiontech", "#wearabletech", "#techfashion", "#smartwear"],
                'marine_speakers': ["#marineaudio", "#boatlife", "#marinetech", "#boatspeakers"]
            }
            instagram_hashtags.extend(category_tags.get(category_key, []))
            instagram_hashtags = instagram_hashtags[:30]
            
            # TikTok Keywords (15)
            tiktok_keywords = [
                "amazon finds", "tiktokmademebuyit", "viral products",
                "POV shopping", "tech haul", "must have finds",
                "worth the hype", "amazon favorites", "budget finds",
                "life changing products", "game changer", "holy grail products"
            ]
            tiktok_keywords.extend(base_keywords[:3])
            tiktok_keywords = list(set(tiktok_keywords))[:15]
            
            # WordPress SEO (15 long-tail)
            wordpress_seo = [
                f"best {category_key} products on amazon 2025",
                f"top rated {category_key} amazon review",
                f"{category_key} buying guide 2025",
                f"amazon {category_key} comparison chart",
                f"affordable {category_key} under $100",
                f"{category_key} for beginners guide",
                f"how to choose best {category_key}",
                f"{category_key} vs alternatives comparison",
                f"is {category_key} worth buying in 2025",
                f"{category_key} pros and cons review",
                f"where to buy {category_key} online",
                f"{category_key} frequently asked questions",
                f"{category_key} unboxing and setup guide",
                f"{category_key} maintenance tips and tricks",
                f"best {category_key} brands comparison"
            ][:15]
            
            # Universal Keywords (10)
            universal_keywords = [
                "amazon", "review", "2025", "best", "top 5",
                "comparison", "buying guide", "worth it", "tested", "recommended"
            ]
            
            result = {
                'youtube': youtube_keywords,
                'instagram': instagram_hashtags,
                'tiktok': tiktok_keywords,
                'wordpress': wordpress_seo,
                'universal': universal_keywords
            }
            
            print(f"✅ TEST MODE: Generated multi-platform keywords:")
            print(f"   YouTube: {len(result['youtube'])} keywords")
            print(f"   Instagram: {len(result['instagram'])} hashtags")
            print(f"   TikTok: {len(result['tiktok'])} keywords")
            print(f"   WordPress: {len(result['wordpress'])} keywords")
            print(f"   Universal: {len(result['universal'])} keywords")
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating multi-platform keywords: {e}")
            return {
                'youtube': ["amazon", "review", "2025"],
                'instagram': ["#amazonfinds", "#techreview"],
                'tiktok': ["tiktokmademebuyit"],
                'wordpress': ["best products 2025"],
                'universal': ["amazon", "best"]
            }
    
    def _parse_keywords_fallback(self, text: str) -> Dict[str, List[str]]:
        """Fallback parser for keywords if JSON parsing fails"""
        result = {
            'youtube': [],
            'instagram': [],
            'tiktok': [],
            'wordpress': [],
            'universal': []
        }
        
        # Simple text parsing logic
        lines = text.split('\n')
        current_platform = None
        
        for line in lines:
            line_lower = line.lower()
            if 'youtube' in line_lower:
                current_platform = 'youtube'
            elif 'instagram' in line_lower:
                current_platform = 'instagram'
            elif 'tiktok' in line_lower:
                current_platform = 'tiktok'
            elif 'wordpress' in line_lower:
                current_platform = 'wordpress'
            elif 'universal' in line_lower:
                current_platform = 'universal'
            elif current_platform and ',' in line:
                # Parse comma-separated keywords
                keywords = [k.strip() for k in line.split(',') if k.strip()]
                result[current_platform].extend(keywords)
        
        return result
    
    async def generate_single_product(self, prompt: str) -> str:
        """TEST MODE: Generate hardcoded single product"""
        try:
            # Return hardcoded product based on prompt content
            if 'title' in prompt.lower():
                return "Amazing Product Title with Great Features"
            elif 'description' in prompt.lower():
                return "This incredible product delivers outstanding performance with premium quality and unbeatable value for money."
            else:
                return "High-quality product that customers love with excellent reviews and ratings."
        except Exception as e:
            print(f"Error generating single product: {e}")
            return "Default product text"
    
    async def generate_optimized_product_descriptions(self, products: List[Dict], universal_keywords: List[str], title: str) -> List[Dict]:
        """TEST MODE: Generate hardcoded optimized product descriptions"""
        try:
            # Hardcoded description templates
            description_templates = [
                "This {adjective} {product_type} delivers {benefit} with premium quality and unbeatable value for budget-conscious buyers.",
                "Experience {benefit} with this top-rated {product_type} featuring {feature} and earning thousands of five-star reviews.",
                "The perfect {product_type} combining {feature} with {benefit} making it essential for anyone seeking quality.",
                "Revolutionary {product_type} offering {feature} and {benefit} at an incredible price point you won't believe.",
                "This bestselling {product_type} provides {benefit} through innovative {feature} that customers absolutely love today."
            ]
            
            adjectives = ["amazing", "innovative", "premium", "advanced", "professional"]
            benefits = ["exceptional performance", "outstanding results", "incredible value", "superior quality", "maximum efficiency"]
            features = ["cutting-edge technology", "durable construction", "user-friendly design", "versatile functionality", "smart features"]
            
            optimized_products = []
            
            for i, product in enumerate(products[:5]):
                rank = 5 - i
                
                # Extract product type from title
                product_type = product.get('title', 'product').split()[0:2]
                product_type = ' '.join(product_type).lower()
                
                # Generate description
                template = description_templates[i % len(description_templates)]
                description = template.format(
                    adjective=adjectives[i % len(adjectives)],
                    product_type=product_type,
                    benefit=benefits[i % len(benefits)],
                    feature=features[i % len(features)]
                )
                
                # Count words
                word_count = len(description.split())
                
                optimized_product = {
                    "rank": rank,
                    "optimized_title": product.get('title', f'Product {rank}'),
                    "optimized_description": description,
                    "keywords_used": universal_keywords[:3] if universal_keywords else ["best", "2025", "amazon"],
                    "word_count": word_count,
                    "estimated_seconds": word_count / 2.5,  # 2.5 words per second
                    "selling_points": [
                        f"Rated {product.get('rating', '4.5')}/5 stars",
                        f"Over {product.get('review_count', '1000')} reviews",
                        f"Price: {product.get('price', '$29.99')}"
                    ]
                }
                
                optimized_products.append(optimized_product)
            
            # Reverse to get correct ranking order (5 to 1)
            optimized_products.reverse()
            
            print(f"✅ TEST MODE: Generated {len(optimized_products)} optimized product descriptions")
            return optimized_products
                
        except Exception as e:
            print(f"❌ Error generating optimized product descriptions: {e}")
            return []
    
    async def generate_attention_grabbing_intro(self, title: str, keywords: List[str], hook_style: str = "shocking") -> Dict:
        """TEST MODE: Generate hardcoded catchy intro hooks"""
        try:
            # Hardcoded hooks by style
            hook_templates = {
                "shocking": [
                    "These 5 products are breaking the internet right now!",
                    "I can't believe Amazon still sells these this cheap!",
                    "Number 1 will blow your mind completely!",
                    "Everyone's buying these 5 products like crazy!"
                ],
                "question": [
                    "Want to know what's going viral on Amazon?",
                    "Why is everyone obsessed with these products?",
                    "Can these 5 finds really change your life?",
                    "What makes these products sell out daily?"
                ],
                "countdown": [
                    "5 products you need before they're gone!",
                    "Counting down the hottest Amazon finds today!",
                    "From 5 to 1, these are must-haves!",
                    "Get ready for the ultimate product countdown!"
                ],
                "story": [
                    "I bought these 5 products and wow!",
                    "Last week changed when I found these!",
                    "My friends begged me to share these!",
                    "These 5 finds solved all my problems!"
                ],
                "controversy": [
                    "Experts don't want you knowing about these!",
                    "These products shouldn't work but they do!",
                    "I was wrong about these 5 products!",
                    "People said I'm crazy for buying these!"
                ]
            }
            
            # Get appropriate hooks
            hooks = hook_templates.get(hook_style, hook_templates["shocking"])
            intro_text = random.choice(hooks)
            
            # Alternative hooks
            alternative_hooks = random.sample([h for style_hooks in hook_templates.values() for h in style_hooks if h != intro_text], 3)
            
            intro_data = {
                "intro_text": intro_text,
                "hook_type": hook_style,
                "psychological_triggers": ["curiosity gap", "social proof", "urgency"],
                "word_count": len(intro_text.split()),
                "estimated_seconds": len(intro_text.split()) / 2.5,
                "retention_score": random.randint(85, 95),
                "alternative_hooks": alternative_hooks
            }
            
            print(f"✅ TEST MODE: Generated intro hook: {intro_text}")
            return intro_data
                
        except Exception as e:
            print(f"❌ Error generating intro hook: {e}")
            return {}
    
    async def generate_platform_upload_metadata(self, title: str, products: List[Dict], platform_keywords: Dict, affiliate_data: List[Dict] = None) -> Dict:
        """TEST MODE: Generate hardcoded platform-specific metadata"""
        try:
            # Get category for templates
            category_key = self._get_category_key(title)
            template = self.category_templates.get(category_key, self.category_templates['default'])
            
            # Format affiliate links
            affiliate_links_text = ""
            if affiliate_data:
                affiliate_links_text = "🛍️ AMAZON DEALS - CHECK DESCRIPTION:\n\n"
                for i, affiliate in enumerate(affiliate_data[:5], 1):
                    product_name = affiliate.get('title', f'Product #{i}')[:50]
                    affiliate_url = affiliate.get('affiliate_link', '')
                    if affiliate_url:
                        affiliate_links_text += f"➡️ #{i}: {product_name}\n{affiliate_url}\n\n"
                affiliate_links_text += "💡 As an Amazon Associate, I earn from qualifying purchases."
            
            # Get optimized title
            optimized_title = await self.optimize_title(title, [])
            
            results = {}
            
            # YouTube Metadata
            youtube_desc = f"""{optimized_title}

⏰ TIMESTAMPS:
0:00 Intro
0:05 #5 Product
0:15 #4 Product  
0:25 #3 Product
0:35 #2 Product
0:45 #1 Product
0:55 Outro

{affiliate_links_text}

🔔 SUBSCRIBE for more amazing product reviews!
👍 LIKE if this helped you!
💬 COMMENT your favorite product!

#amazonfinds #amazonmusthaves #techreview #viralproducts #amazonhaul #bestof2025"""
            
            results['youtube'] = {
                "title": optimized_title[:60],
                "description": youtube_desc,
                "tags": platform_keywords.get('youtube', [])[:10],
                "character_count": len(optimized_title)
            }
            
            # TikTok Metadata
            tiktok_title = random.choice([
                "Wait for #1 🤯",
                "POV: You need all of these 😭",
                "RUN don't walk to Amazon!",
                "The last one though 👀"
            ])
            
            tiktok_caption = f"{tiktok_title} These {category_key} finds are INSANE! Link in bio for all the Amazon deals 🛍️🔥 #amazonfinds #tiktokmademebuyit #amazonmusthaves #viralproducts #amazonhaul"
            
            results['tiktok'] = {
                "title": tiktok_title,
                "caption": tiktok_caption,
                "hashtags": platform_keywords.get('tiktok', [])[:8],
                "character_count": len(tiktok_title)
            }
            
            # Instagram Metadata  
            instagram_title = random.choice([
                "✨ Amazon Finds That Changed My Life",
                "📱 Tech Gadgets You NEED in 2025",
                "🎁 Gift Ideas Everyone Will Love",
                "🔥 Viral Products Worth The Hype"
            ])
            
            instagram_caption = f"""{instagram_title}

Okay but why is nobody talking about these?! 😱

I tested the most viral {category_key} on Amazon and these 5 are ACTUALLY worth your money!

Save this for later & check my bio for all the links! 🔗

{' '.join(platform_keywords.get('instagram', [])[:20])}

📌 Tag someone who needs to see this!"""
            
            results['instagram'] = {
                "title": instagram_title[:55],
                "caption": instagram_caption,
                "hashtags": platform_keywords.get('instagram', [])[:30],
                "character_count": len(instagram_title)
            }
            
            # WordPress Metadata
            wp_title = f"Best {self._extract_category_name(title)} on Amazon (2025 Review)"
            meta_desc = f"In-depth review of the top 5 {category_key} on Amazon. Honest comparisons, pros/cons, and buyer's guide included."
            
            # Generate blog content
            blog_content = f"""<h1>{wp_title}</h1>

<p>After testing dozens of {category_key} products, I've found the absolute best options available on Amazon in 2025. This comprehensive guide breaks down everything you need to know before making a purchase.</p>

<h2>Quick Summary - Top 5 {self._extract_category_name(title)}</h2>
<ol>
<li><strong>Best Overall:</strong> Product #1 - Perfect balance of features and value</li>
<li><strong>Best Budget:</strong> Product #5 - Incredible performance under $50</li>
<li><strong>Most Features:</strong> Product #2 - Packed with cutting-edge technology</li>
<li><strong>Best Design:</strong> Product #3 - Sleek and modern aesthetics</li>
<li><strong>Best Value:</strong> Product #4 - Premium quality at mid-range price</li>
</ol>

<h2>Detailed Product Reviews</h2>
"""
            
            # Add product reviews if affiliate data available
            if affiliate_data:
                for i, product in enumerate(affiliate_data[:5], 1):
                    blog_content += f"""
<h3>#{i}. {product.get('title', f'Product {i}')}</h3>
<div class="product-box">
<p><strong>Price:</strong> {product.get('price', 'Check Amazon')}<br>
<strong>Rating:</strong> {product.get('rating', '4.5')}/5 stars ({product.get('review_count', '1000+')} reviews)</p>
<p>Key Features:</p>
<ul>
<li>High-quality construction</li>
<li>Excellent performance</li>
<li>Great value for money</li>
</ul>
<p><a href="{product.get('affiliate_link', '#')}" class="button" target="_blank" rel="nofollow">Check Price on Amazon</a></p>
</div>
"""
            
            blog_content += f"""
<h2>Buying Guide - How to Choose the Best {self._extract_category_name(title)}</h2>
<p>When shopping for {category_key}, consider these key factors:</p>
<ul>
<li><strong>Budget:</strong> Determine your price range before shopping</li>
<li><strong>Features:</strong> List must-have vs nice-to-have features</li>
<li><strong>Reviews:</strong> Always check verified purchase reviews</li>
<li><strong>Warranty:</strong> Look for products with solid warranties</li>
</ul>

<h2>Frequently Asked Questions</h2>
<h3>Q: Are these products worth the price?</h3>
<p>A: Yes, all products in this list offer excellent value for their respective price points.</p>

<h3>Q: Do these products come with warranties?</h3>
<p>A: Most come with manufacturer warranties. Check individual product pages for details.</p>

<h3>Q: How often is this list updated?</h3>
<p>A: We update our recommendations monthly based on new releases and user feedback.</p>

<p><em>Disclosure: This post contains affiliate links. As an Amazon Associate, I earn from qualifying purchases at no extra cost to you.</em></p>"""
            
            results['wordpress'] = {
                "title": wp_title[:60],
                "meta_description": meta_desc[:160],
                "content": blog_content,
                "focus_keywords": platform_keywords.get('wordpress', [])[:5],
                "character_count": len(wp_title)
            }
            
            print(f"✅ TEST MODE: Generated platform metadata for all platforms")
            return results
                
        except Exception as e:
            print(f"❌ Error generating platform metadata: {e}")
            return {}

# Test the server
async def test_content_generation():
    # Load config
    with open('/app/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    # Initialize server
    server = ContentGenerationMCPServer(
        anthropic_api_key=config['anthropic_api_key']
    )
    
    # Test with sample data
    title = "Top 5 New Car Mono Amplifiers Releases 2025"
    category = "Car Audio Equipment"
    
    print("🔍 Generating SEO keywords...")
    keywords = await server.generate_seo_keywords(title, category)
    print(f"Keywords: {keywords[:5]}...")  # Show first 5
    
    print("\n🎯 Optimizing title...")
    optimized_title = await server.optimize_title(title, keywords)
    
    print("\n📝 Generating countdown script...")
    script = await server.generate_countdown_script(optimized_title, keywords)
    if script:
        print(f"Script intro: {script.get('intro', 'N/A')[:50]}...")


if __name__ == "__main__":
    asyncio.run(test_content_generation())
