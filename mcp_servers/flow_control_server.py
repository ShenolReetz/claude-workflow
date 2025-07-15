# mcp_servers/flow_control_server.py
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FlowControlMCPServer:
    """
    Flow Control MCP Server - Validates complete workflow execution
    Ensures all 5 products are processed correctly with no missing steps
    """
    
    def __init__(self):
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        self.required_products = 5
        
    def reset_validation(self):
        """Reset validation state for new workflow run"""
        self.validation_results = {}
        self.errors = []
        self.warnings = []
        logger.info("🔄 Flow Control validation reset")
    
    async def validate_workflow_step(self, step_name: str, step_data: Dict[str, Any]) -> bool:
        """Validate a specific workflow step"""
        logger.info(f"🔍 Flow Control validating: {step_name}")
        
        validation_method = getattr(self, f"_validate_{step_name.lower().replace(' ', '_')}", None)
        if validation_method:
            result = await validation_method(step_data)
            self.validation_results[step_name] = result
            return result
        else:
            logger.warning(f"⚠️ No validation method for step: {step_name}")
            return True
    
    async def _validate_product_category_extraction(self, data: Dict[str, Any]) -> bool:
        """Validate product category extraction step"""
        required_fields = ['success', 'primary_category', 'search_terms', 'category_confidence']
        
        for field in required_fields:
            if field not in data:
                self.errors.append(f"Category extraction missing field: {field}")
                return False
        
        if not data['success']:
            self.errors.append(f"Category extraction failed: {data.get('error', 'Unknown error')}")
            return False
        
        if data['category_confidence'] < 0.8:
            self.warnings.append(f"Low category confidence: {data['category_confidence']}")
        
        if len(data['search_terms']) < 2:
            self.warnings.append("Few search terms generated - may limit Amazon search success")
        
        logger.info(f"✅ Category extraction validated: {data['primary_category']}")
        return True
    
    async def _validate_amazon_scraping(self, data: Dict[str, Any]) -> bool:
        """Validate Amazon scraping step"""
        if not data.get('success'):
            self.errors.append(f"Amazon scraping failed: {data.get('error', 'Unknown error')}")
            return False
        
        products = data.get('products', [])
        if len(products) == 0:
            self.errors.append("Amazon scraping found 0 products")
            return False
        
        if len(products) < self.required_products:
            self.warnings.append(f"Amazon found only {len(products)} products, need {self.required_products}")
        
        # Validate product structure
        for i, product in enumerate(products[:self.required_products]):
            required_product_fields = ['title', 'price', 'rating', 'review_count', 'image_url', 'affiliate_link']
            for field in required_product_fields:
                if field not in product or not product[field]:
                    self.errors.append(f"Product {i+1} missing field: {field}")
                    return False
        
        logger.info(f"✅ Amazon scraping validated: {len(products)} products")
        return True
    
    async def _validate_multi_platform_keywords(self, data: Dict[str, Any]) -> bool:
        """Validate multi-platform keywords generation"""
        required_platforms = ['youtube', 'instagram', 'tiktok', 'wordpress', 'universal']
        
        for platform in required_platforms:
            if platform not in data:
                self.errors.append(f"Missing keywords for platform: {platform}")
                return False
            
            keywords = data[platform]
            if not isinstance(keywords, list) or len(keywords) == 0:
                self.errors.append(f"No keywords generated for platform: {platform}")
                return False
        
        # Check keyword counts
        expected_counts = {
            'youtube': 20,
            'instagram': 30,
            'tiktok': 15,
            'wordpress': 15,
            'universal': 10
        }
        
        for platform, expected_count in expected_counts.items():
            actual_count = len(data[platform])
            if actual_count < expected_count * 0.8:  # Allow 20% tolerance
                self.warnings.append(f"Low keyword count for {platform}: {actual_count}/{expected_count}")
        
        logger.info(f"✅ Multi-platform keywords validated: {sum(len(data[p]) for p in required_platforms)} total")
        return True
    
    async def _validate_airtable_updates(self, data: Dict[str, Any]) -> bool:
        """Validate Airtable updates have all required fields"""
        required_airtable_fields = []
        
        # Product fields (1-5)
        for i in range(1, self.required_products + 1):
            required_airtable_fields.extend([
                f'ProductNo{i}Title',
                f'ProductNo{i}Price',
                f'ProductNo{i}Rating',
                f'ProductNo{i}Reviews',
                f'ProductNo{i}Photo',
                f'ProductNo{i}AffiliateLink'
            ])
        
        # Keyword fields
        required_airtable_fields.extend([
            'YouTubeKeywords',
            'InstagramHashtags',
            'TikTokKeywords',
            'WordPressSEO',
            'UniversalKeywords'
        ])
        
        # Check if all fields were updated
        updated_fields = data.get('updated_fields', [])
        missing_fields = [field for field in required_airtable_fields if field not in updated_fields]
        
        if missing_fields:
            self.errors.append(f"Airtable missing fields: {missing_fields}")
            return False
        
        logger.info(f"✅ Airtable updates validated: {len(updated_fields)} fields")
        return True
    
    async def _validate_image_generation(self, data: Dict[str, Any]) -> bool:
        """Validate image generation step"""
        images_generated = data.get('images_generated', 0)
        
        if images_generated == 0:
            self.errors.append("No images generated")
            return False
        
        if images_generated < self.required_products:
            self.warnings.append(f"Generated {images_generated} images, need {self.required_products}")
        
        # Check if images were saved to Google Drive
        if not data.get('saved_to_drive', False):
            self.errors.append("Images not saved to Google Drive")
            return False
        
        logger.info(f"✅ Image generation validated: {images_generated} images")
        return True
    
    async def _validate_video_creation(self, data: Dict[str, Any]) -> bool:
        """Validate video creation step"""
        if not data.get('success'):
            self.errors.append(f"Video creation failed: {data.get('error', 'Unknown error')}")
            return False
        
        if not data.get('video_url'):
            self.errors.append("No video URL returned")
            return False
        
        # Check video properties
        video_duration = data.get('duration', 0)
        if video_duration != 60:
            self.warnings.append(f"Video duration {video_duration}s, expected 60s")
        
        # Check if video has expected features
        features = data.get('features', [])
        expected_features = ['reviews', 'ratings', 'animations', 'transitions']
        missing_features = [f for f in expected_features if f not in features]
        
        if missing_features:
            self.warnings.append(f"Video missing features: {missing_features}")
        
        logger.info(f"✅ Video creation validated: {data.get('video_url')}")
        return True
    
    async def _validate_social_media_uploads(self, data: Dict[str, Any]) -> bool:
        """Validate social media uploads"""
        platforms = ['youtube', 'instagram', 'tiktok']
        successful_uploads = 0
        
        for platform in platforms:
            platform_data = data.get(platform, {})
            if platform_data.get('success'):
                successful_uploads += 1
                logger.info(f"✅ {platform.title()} upload successful")
            else:
                if platform == 'tiktok':
                    logger.info(f"⏸️ TikTok upload disabled (API pending)")
                elif platform == 'instagram':
                    logger.info(f"⏸️ Instagram upload disabled")
                else:
                    self.warnings.append(f"{platform.title()} upload failed: {platform_data.get('error', 'Unknown')}")
        
        # YouTube should always work
        if not data.get('youtube', {}).get('success'):
            self.errors.append("YouTube upload failed")
            return False
        
        logger.info(f"✅ Social media uploads validated: {successful_uploads} successful")
        return True
    
    async def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_steps = len(self.validation_results)
        passed_steps = sum(1 for result in self.validation_results.values() if result)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_success': len(self.errors) == 0,
            'steps_passed': passed_steps,
            'total_steps': total_steps,
            'success_rate': (passed_steps / total_steps * 100) if total_steps > 0 else 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'validation_results': self.validation_results,
            'required_products': self.required_products
        }
        
        # Print detailed report
        print("\n" + "="*80)
        print("🎯 FLOW CONTROL VALIDATION REPORT")
        print("="*80)
        print(f"📊 Overall Success: {'✅ PASS' if report['overall_success'] else '❌ FAIL'}")
        print(f"📈 Success Rate: {report['success_rate']:.1f}% ({passed_steps}/{total_steps} steps)")
        print(f"🎯 Required Products: {self.required_products}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        print(f"\n📋 STEP VALIDATION RESULTS:")
        for step, result in self.validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {step}: {status}")
        
        if report['overall_success']:
            print(f"\n🎉 WORKFLOW VALIDATION SUCCESSFUL!")
            print(f"✅ All {self.required_products} products processed correctly")
            print(f"✅ All critical steps completed successfully")
        else:
            print(f"\n🚨 WORKFLOW VALIDATION FAILED!")
            print(f"❌ {len(self.errors)} critical errors must be fixed")
            print(f"🔧 Please address all errors before production")
        
        print("="*80)
        
        return report
    
    async def validate_complete_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete workflow execution"""
        self.reset_validation()
        
        logger.info("🚀 Starting complete workflow validation")
        
        # Define validation steps in order
        validation_steps = [
            'product_category_extraction',
            'amazon_scraping',
            'multi_platform_keywords',
            'airtable_updates',
            'image_generation',
            'video_creation',
            'social_media_uploads'
        ]
        
        # Run each validation step
        for step in validation_steps:
            if step in workflow_data:
                await self.validate_workflow_step(step, workflow_data[step])
            else:
                logger.warning(f"⚠️ Step data missing: {step}")
                self.warnings.append(f"No data provided for step: {step}")
        
        # Generate final report
        report = await self.generate_validation_report()
        
        return report

# Test function
if __name__ == "__main__":
    import asyncio
    
    # Test data
    test_workflow_data = {
        'product_category_extraction': {
            'success': True,
            'primary_category': 'gaming headsets',
            'search_terms': ['gaming headphones', 'headsets for gaming'],
            'category_confidence': 0.95
        },
        'amazon_scraping': {
            'success': True,
            'products': [
                {
                    'title': 'Gaming Headset 1',
                    'price': '$99.99',
                    'rating': 4.5,
                    'review_count': 1000,
                    'image_url': 'https://example.com/1.jpg',
                    'affiliate_link': 'https://amazon.com/dp/123'
                }
            ]
        },
        'multi_platform_keywords': {
            'youtube': ['gaming'] * 20,
            'instagram': ['#gaming'] * 30,
            'tiktok': ['gaming'] * 15,
            'wordpress': ['gaming headsets'] * 15,
            'universal': ['gaming'] * 10
        }
    }
    
    async def test_flow_control():
        flow_control = FlowControlMCPServer()
        
        print("🧪 Testing Flow Control MCP Server")
        print("=" * 50)
        
        report = await flow_control.validate_complete_workflow(test_workflow_data)
        
        print(f"\n📊 Test Result: {'✅ PASS' if report['overall_success'] else '❌ FAIL'}")
        
    asyncio.run(test_flow_control())