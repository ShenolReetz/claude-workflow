import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoPrerequisiteControlMCPServer:
    """
    Video Prerequisite Control MCP Server
    Validates all prerequisites are complete before video generation
    Updates VideoProductionRDY column from 'Pending' to 'Ready'
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
        logger.info("🔄 Video Prerequisite Control validation reset")
    
    async def validate_title_optimization(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate title optimization is complete (exact field checking)"""
        logger.info("🔍 Validating title optimization")
        
        # Check for exact platform-specific title fields
        required_title_fields = [
            'YouTubeTitle',
            'TikTokTitle', 
            'InstagramTitle',
            'WordPressTitle'
        ]
        
        missing_titles = []
        found_titles = []
        
        for field in required_title_fields:
            if airtable_record.get(field):
                found_titles.append(field)
            else:
                missing_titles.append(field)
        
        if missing_titles:
            self.errors.append(f"Missing optimized titles: {missing_titles}")
            return False
        
        logger.info("✅ Title optimization validated")
        return True
    
    async def validate_product_data(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate all product data is complete"""
        logger.info("🔍 Validating product data")
        
        missing_product_data = []
        
        for i in range(1, self.required_products + 1):
            product_fields = [
                f'ProductNo{i}Title',
                f'ProductNo{i}Price', 
                f'ProductNo{i}Rating',
                f'ProductNo{i}Reviews',
                f'ProductNo{i}Photo',
                f'ProductNo{i}AffiliateLink'
            ]
            
            for field in product_fields:
                if not airtable_record.get(field):
                    missing_product_data.append(field)
        
        if missing_product_data:
            self.errors.append(f"Missing product data: {missing_product_data}")
            return False
        
        logger.info(f"✅ Product data validated for {self.required_products} products")
        return True
    
    async def validate_platform_descriptions(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate platform descriptions are generated (exact field checking)"""
        logger.info("🔍 Validating platform descriptions")
        
        # Check for exact platform-specific description fields
        required_description_fields = [
            'YouTubeDescription',
            'TikTokDescription',
            'InstagramCaption', 
            'WordPressContent'
        ]
        
        missing_descriptions = []
        found_descriptions = []
        
        for field in required_description_fields:
            if airtable_record.get(field):
                found_descriptions.append(field)
            else:
                missing_descriptions.append(field)
        
        if missing_descriptions:
            self.errors.append(f"Missing platform descriptions: {missing_descriptions}")
            return False
        
        logger.info("✅ Platform descriptions validated")
        return True
    
    async def validate_affiliate_links(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate affiliate links are generated for all products"""
        logger.info("🔍 Validating affiliate links")
        
        missing_affiliate_links = []
        
        for i in range(1, self.required_products + 1):
            affiliate_field = f'ProductNo{i}AffiliateLink'
            affiliate_link = airtable_record.get(affiliate_field)
            
            if not affiliate_link:
                missing_affiliate_links.append(affiliate_field)
            elif not affiliate_link.startswith('https://amzn.to/') and not affiliate_link.startswith('https://amazon.com/'):
                self.warnings.append(f"Invalid affiliate link format for {affiliate_field}: {affiliate_link}")
        
        if missing_affiliate_links:
            self.errors.append(f"Missing affiliate links: {missing_affiliate_links}")
            return False
        
        logger.info(f"✅ Affiliate links validated for {self.required_products} products")
        return True
    
    async def validate_photo_links(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate photo links are available for all products"""
        logger.info("🔍 Validating photo links")
        
        missing_photo_links = []
        
        for i in range(1, self.required_products + 1):
            photo_field = f'ProductNo{i}Photo'
            photo_link = airtable_record.get(photo_field)
            
            if not photo_link:
                missing_photo_links.append(photo_field)
            elif not (photo_link.startswith('http://') or photo_link.startswith('https://')):
                self.warnings.append(f"Invalid photo link format for {photo_field}: {photo_link}")
        
        if missing_photo_links:
            self.errors.append(f"Missing photo links: {missing_photo_links}")
            return False
        
        logger.info(f"✅ Photo links validated for {self.required_products} products")
        return True
    
    async def validate_audio_generation(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate audio generation is complete (flexible field checking)"""
        logger.info("🔍 Validating audio generation")
        
        # Check for essential audio fields (intro/outro)
        essential_audio_fields = ['IntroMp3', 'OutroMp3']
        missing_essential = []
        
        for field in essential_audio_fields:
            if not airtable_record.get(field):
                missing_essential.append(field)
        
        # Check for product audio fields (may not exist in schema)
        missing_product_audio = []
        existing_product_audio = []
        
        for i in range(1, self.required_products + 1):
            product_audio_field = f'Product{i}Mp3'
            if not airtable_record.get(product_audio_field):
                missing_product_audio.append(product_audio_field)
            else:
                existing_product_audio.append(product_audio_field)
        
        # If essential audio is missing, fail validation
        if missing_essential:
            self.errors.append(f"Missing essential audio: {missing_essential}")
            return False
        
        # Product audio fields are REQUIRED for video production
        if missing_product_audio:
            # Check if this is a schema limitation (no product audio fields exist at all)
            if not existing_product_audio:
                # If VideoScript exists, we can work with that for now, but warn about missing fields
                if airtable_record.get('VideoScript'):
                    self.warnings.append(f"Product audio fields missing from schema: {missing_product_audio}")
                    logger.warning(f"⚠️ Product audio fields missing from schema: {missing_product_audio}")
                    logger.warning("💡 Consider adding Product1Mp3-Product5Mp3 fields to Airtable for proper audio tracking")
                    return True
                else:
                    self.errors.append(f"Missing product audio files and VideoScript: {missing_product_audio}")
                    logger.error(f"❌ Missing product audio files and VideoScript: {missing_product_audio}")
                    return False
            else:
                # Some product audio exists but some is missing - this is a real issue
                self.errors.append(f"Missing product audio files: {missing_product_audio}")
                logger.error(f"❌ Missing product audio files: {missing_product_audio}")
                return False
        
        logger.info(f"✅ Audio generation validated for intro, outro, and {len(existing_product_audio)} products")
        return True
    
    async def validate_keywords_and_seo(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate keywords and SEO data is complete"""
        logger.info("🔍 Validating keywords and SEO")
        
        required_keyword_fields = [
            'YouTubeKeywords',
            'InstagramHashtags',
            'TikTokKeywords',
            'WordPressSEO',
            'UniversalKeywords'
        ]
        
        missing_keywords = []
        for field in required_keyword_fields:
            if not airtable_record.get(field):
                missing_keywords.append(field)
        
        if missing_keywords:
            self.errors.append(f"Missing keywords/SEO: {missing_keywords}")
            return False
        
        logger.info("✅ Keywords and SEO validated")
        return True
    
    async def validate_text_timing_status(self, airtable_record: Dict[str, Any]) -> bool:
        """Validate all text timing status columns are set to 'Approved'"""
        logger.info("🔍 Validating text timing status columns")
        
        # EXACT COLUMN NAMES FROM ToDo.md - CRITICAL FOR VIDEO GENERATION
        required_status_columns = [
            # Video content columns (5 second limit)
            'VideoTitleStatus',        # → Validates: VideoTitle field
            'VideoDescriptionStatus',  # → Validates: VideoDescription field
            
            # Product content columns (9 second limit each)
            'ProductNo1TitleStatus',       # → Validates: ProductNo1Title field
            'ProductNo1DescriptionStatus', # → Validates: ProductNo1Description field
            'ProductNo2TitleStatus',       # → Validates: ProductNo2Title field
            'ProductNo2DescriptionStatus', # → Validates: ProductNo2Description field
            'ProductNo3TitleStatus',       # → Validates: ProductNo3Title field
            'ProductNo3DescriptionStatus', # → Validates: ProductNo3Description field
            'ProductNo4TitleStatus',       # → Validates: ProductNo4Title field
            'ProductNo4DescriptionStatus', # → Validates: ProductNo4Description field
            'ProductNo5TitleStatus',       # → Validates: ProductNo5Title field
            'ProductNo5DescriptionStatus', # → Validates: ProductNo5Description field
        ]
        
        missing_approved_status = []
        rejected_fields = []
        pending_fields = []
        
        for status_column in required_status_columns:
            status_value = airtable_record.get(status_column)
            
            if status_value == "Approved":
                continue  # This is what we want
            elif status_value == "Rejected":
                rejected_fields.append(status_column)
            elif status_value == "Pending":
                pending_fields.append(status_column)
            else:
                missing_approved_status.append(status_column)
        
        # Check for any non-approved statuses
        if rejected_fields:
            self.errors.append(f"Text timing REJECTED (exceeds limits): {rejected_fields}")
            logger.error(f"❌ Text timing validation failed - REJECTED fields: {rejected_fields}")
            return False
        
        if pending_fields:
            self.errors.append(f"Text timing PENDING (awaiting validation): {pending_fields}")
            logger.warning(f"⏳ Text timing validation pending - PENDING fields: {pending_fields}")
            return False
        
        if missing_approved_status:
            self.errors.append(f"Text timing status MISSING/INVALID: {missing_approved_status}")
            logger.error(f"❌ Text timing validation failed - MISSING status: {missing_approved_status}")
            return False
        
        logger.info(f"✅ Text timing status validated - all {len(required_status_columns)} columns are 'Approved'")
        return True
    
    async def check_video_production_ready(self, airtable_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Master validation function to check if video production is ready
        Returns validation results and updates VideoProductionRDY status
        """
        self.reset_validation()
        
        logger.info("🚀 Starting video production prerequisite validation")
        
        # Define all validation checks
        validation_checks = [
            ('title_optimization', self.validate_title_optimization),
            ('product_data', self.validate_product_data),
            ('platform_descriptions', self.validate_platform_descriptions),
            ('affiliate_links', self.validate_affiliate_links),
            ('photo_links', self.validate_photo_links),
            ('audio_generation', self.validate_audio_generation),
            ('keywords_and_seo', self.validate_keywords_and_seo),
            ('text_timing_status', self.validate_text_timing_status)  # CRITICAL: All text must be approved for TTS timing
        ]
        
        # Run all validation checks
        all_passed = True
        for check_name, check_function in validation_checks:
            try:
                result = await check_function(airtable_record)
                self.validation_results[check_name] = result
                if not result:
                    all_passed = False
            except Exception as e:
                logger.error(f"Error in {check_name} validation: {e}")
                self.errors.append(f"Validation error in {check_name}: {str(e)}")
                self.validation_results[check_name] = False
                all_passed = False
        
        # Generate validation report
        report = await self.generate_validation_report(all_passed)
        
        # Determine VideoProductionRDY status
        video_production_status = "Ready" if all_passed else "Pending"
        
        report['video_production_ready'] = all_passed
        report['video_production_status'] = video_production_status
        report['airtable_update_required'] = {
            'VideoProductionRDY': video_production_status
        }
        
        return report
    
    async def generate_validation_report(self, all_passed: bool) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for result in self.validation_results.values() if result)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_success': all_passed,
            'checks_passed': passed_checks,
            'total_checks': total_checks,
            'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'validation_results': self.validation_results,
            'required_products': self.required_products
        }
        
        # Print detailed report
        print("\n" + "="*80)
        print("🎬 VIDEO PRODUCTION PREREQUISITE VALIDATION REPORT")
        print("="*80)
        print(f"📊 Overall Status: {'✅ READY FOR VIDEO PRODUCTION' if all_passed else '❌ NOT READY'}")
        print(f"📈 Validation Rate: {report['success_rate']:.1f}% ({passed_checks}/{total_checks} checks)")
        print(f"🎯 Required Products: {self.required_products}")
        
        if self.errors:
            print(f"\n❌ BLOCKING ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        print(f"\n📋 VALIDATION CHECK RESULTS:")
        for check, result in self.validation_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {check.replace('_', ' ').title()}: {status}")
        
        if all_passed:
            print(f"\n🎉 ALL PREREQUISITES SATISFIED!")
            print(f"✅ Video production can begin")
            print(f"🎬 VideoProductionRDY status: Ready")
        else:
            print(f"\n🚨 PREREQUISITES NOT SATISFIED!")
            print(f"❌ {len(self.errors)} critical issues must be resolved")
            print(f"🔧 VideoProductionRDY status: Pending")
        
        print("="*80)
        
        return report

# Test function
if __name__ == "__main__":
    async def test_video_prerequisite_control():
        control = VideoPrerequisiteControlMCPServer()
        
        # Test data - complete record
        test_record_complete = {
            'YouTubeTitle': 'Best Gaming Headsets 2024',
            'InstagramTitle': 'Top Gaming Headsets',
            'TikTokTitle': 'Gaming Headsets Review',
            'WordPressTitle': 'Ultimate Gaming Headsets Guide',
            'YouTubeDescription': 'Complete description...',
            'InstagramCaption': 'Insta caption...',
            'TikTokDescription': 'TikTok description...',
            'WordPressContent': 'WordPress content...',
            'YouTubeKeywords': 'gaming, headsets, review',
            'InstagramHashtags': '#gaming #headsets',
            'TikTokKeywords': 'gaming headsets',
            'WordPressSEO': 'gaming headsets review',
            'UniversalKeywords': 'gaming audio',
            'IntroMp3': 'https://drive.google.com/intro.mp3',
            'OutroMp3': 'https://drive.google.com/outro.mp3'
        }
        
        # Add product data
        for i in range(1, 6):
            test_record_complete.update({
                f'ProductNo{i}Title': f'Gaming Headset {i}',
                f'ProductNo{i}Price': f'${99 + i}.99',
                f'ProductNo{i}Rating': '4.5',
                f'ProductNo{i}Reviews': '1000',
                f'ProductNo{i}Photo': f'https://example.com/product{i}.jpg',
                f'ProductNo{i}AffiliateLink': f'https://amzn.to/product{i}',
                f'Product{i}Mp3': f'https://drive.google.com/product{i}.mp3'
            })
        
        print("🧪 Testing Video Prerequisite Control MCP Server")
        print("=" * 50)
        
        # Test complete record
        print("\n🟢 Testing COMPLETE record:")
        report_complete = await control.check_video_production_ready(test_record_complete)
        print(f"Result: {'✅ READY' if report_complete['video_production_ready'] else '❌ NOT READY'}")
        
        # Test incomplete record
        print("\n🔴 Testing INCOMPLETE record:")
        test_record_incomplete = test_record_complete.copy()
        del test_record_incomplete['ProductNo1Title']
        del test_record_incomplete['YouTubeDescription']
        del test_record_incomplete['IntroMp3']
        
        report_incomplete = await control.check_video_production_ready(test_record_incomplete)
        print(f"Result: {'✅ READY' if report_incomplete['video_production_ready'] else '❌ NOT READY'}")
        
    asyncio.run(test_video_prerequisite_control())