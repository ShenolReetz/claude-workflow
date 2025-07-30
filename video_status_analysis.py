#!/usr/bin/env python3
"""
Video Status Analysis Tool - Analyzes failed JSON2Video project ZRKDMhlcMEhAtasZ
Uses actual JSON2Video API endpoint for comprehensive error analysis
"""

import asyncio
import json
import httpx
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoStatusAnalyzer:
    """Analyzes JSON2Video project status using actual API endpoints"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.json2video.com/v2"
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30, headers=self.headers)
    
    async def analyze_failed_project(self, project_id: str) -> Dict[str, Any]:
        """Comprehensive analysis of failed JSON2Video project"""
        
        analysis_report = {
            "project_id": project_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "api_endpoint": f"{self.base_url}/movies?project={project_id}",
            "status": "unknown",
            "raw_api_response": None,
            "error_details": {},
            "root_cause_analysis": {},
            "recovery_recommendations": [],
            "monitoring_suggestions": []
        }
        
        logger.info(f"🔍 Starting comprehensive analysis of project {project_id}")
        logger.info(f"📡 API Endpoint: {analysis_report['api_endpoint']}")
        logger.info(f"🔑 Authentication: x-api-key header configured")
        
        try:
            # Make API call to get project status
            logger.info(f"📞 Calling JSON2Video API for project status...")
            response = await self.client.get(
                f"{self.base_url}/movies?project={project_id}"
            )
            
            # Capture raw response data
            analysis_report["http_status_code"] = response.status_code
            
            if response.status_code == 200:
                result = response.json()
                analysis_report["raw_api_response"] = result
                
                # Extract movie data (nested under 'movie' key)
                movie_data = result.get('movie', {})
                if not movie_data:
                    # Try alternative structure
                    movie_data = result
                
                # Analyze status and error information
                status = movie_data.get('status', '').lower()
                analysis_report["status"] = status
                
                logger.info(f"📊 API Response Status: {response.status_code}")
                logger.info(f"🎬 Project Status: {status}")
                
                # Detailed error analysis
                if status == 'error' or movie_data.get('success') == False:
                    analysis_report["error_details"] = self._extract_error_details(movie_data)
                    analysis_report["root_cause_analysis"] = self._analyze_root_cause(movie_data)
                    analysis_report["recovery_recommendations"] = self._generate_recovery_plan(movie_data)
                
                elif status == 'done':
                    # Check if video URL is available
                    video_url = movie_data.get('url', '')
                    if video_url:
                        analysis_report["video_url"] = video_url
                        logger.info(f"✅ Video completed successfully: {video_url}")
                    else:
                        logger.warning(f"⚠️ Status is 'done' but no video URL provided")
                        analysis_report["error_details"]["issue"] = "Video marked as done but no URL available"
                
                elif status in ['processing', 'queued']:
                    progress = movie_data.get('progress', 0)
                    logger.info(f"🔄 Video still processing: {progress}% complete")
                    analysis_report["progress"] = progress
                    analysis_report["processing_status"] = "ongoing"
                
                else:
                    logger.warning(f"❓ Unknown status: {status}")
                    analysis_report["error_details"]["issue"] = f"Unknown status: {status}"
            
            elif response.status_code == 404:
                logger.error(f"❌ Project {project_id} not found (404)")
                analysis_report["error_details"] = {
                    "error_code": "PROJECT_NOT_FOUND",
                    "description": "Project ID does not exist or has been deleted",
                    "http_status": 404
                }
                analysis_report["root_cause_analysis"] = {
                    "primary_cause": "Invalid or expired project ID",
                    "possible_reasons": [
                        "Project was never created successfully",
                        "Project has been automatically deleted due to age",
                        "Incorrect project ID provided",
                        "API key does not have access to this project"
                    ]
                }
            
            elif response.status_code == 401:
                logger.error(f"❌ Unauthorized (401) - API key issue")
                analysis_report["error_details"] = {
                    "error_code": "UNAUTHORIZED",
                    "description": "API key is invalid or expired",
                    "http_status": 401
                }
            
            else:
                error_text = response.text
                logger.error(f"❌ API Error {response.status_code}: {error_text}")
                analysis_report["error_details"] = {
                    "error_code": f"HTTP_{response.status_code}",
                    "description": error_text,
                    "http_status": response.status_code
                }
            
        except Exception as e:
            logger.error(f"❌ Exception during API call: {str(e)}")
            analysis_report["error_details"] = {
                "error_code": "API_EXCEPTION",
                "description": str(e),
                "error_type": type(e).__name__
            }
        
        # Generate monitoring suggestions
        analysis_report["monitoring_suggestions"] = self._generate_monitoring_suggestions(analysis_report)
        
        return analysis_report
    
    def _extract_error_details(self, movie_data: Dict) -> Dict[str, Any]:
        """Extract detailed error information from API response"""
        error_details = {}
        
        # Extract error message
        error_message = movie_data.get('message', '')
        if error_message:
            error_details["error_message"] = error_message
        
        # Check for success flag
        if movie_data.get('success') == False:
            error_details["success_flag"] = False
        
        # Extract any additional error information
        if 'error' in movie_data:
            error_details["error_object"] = movie_data['error']
        
        # Check for processing issues
        progress = movie_data.get('progress', 0)
        if progress > 0:
            error_details["failed_at_progress"] = f"{progress}%"
        
        return error_details
    
    def _analyze_root_cause(self, movie_data: Dict) -> Dict[str, Any]:
        """Analyze root cause of the failure"""
        root_cause = {
            "primary_cause": "unknown",
            "category": "unknown",
            "technical_details": {},
            "likely_solutions": []
        }
        
        error_message = movie_data.get('message', '').lower()
        
        if 'source url is required' in error_message or 'audio element' in error_message:
            root_cause["primary_cause"] = "Missing or invalid audio source URLs"
            root_cause["category"] = "asset_validation_error"
            root_cause["technical_details"] = {
                "issue": "Empty or invalid audio source URLs in template",
                "affected_elements": "Audio elements in scenes",
                "common_pattern": 'Audio elements with empty src: ""'
            }
            root_cause["likely_solutions"] = [
                "Validate all audio URLs before template submission",
                "Implement fallback audio sources",
                "Check Google Drive audio configuration",
                "Verify ElevenLabs voice generation URLs"
            ]
        
        elif 'template validation' in error_message or 'invalid element' in error_message:
            root_cause["primary_cause"] = "Template validation error"
            root_cause["category"] = "schema_validation_error"
            root_cause["technical_details"] = {
                "issue": "JSON2Video template schema validation failed",
                "validation_stage": "pre_processing"
            }
            root_cause["likely_solutions"] = [
                "Validate JSON schema against JSON2Video API documentation",
                "Check element positioning and sizing",
                "Verify component configurations",
                "Test template with minimal elements first"
            ]
        
        elif 'quota' in error_message or 'limit' in error_message:
            root_cause["primary_cause"] = "API quota or rate limit exceeded"
            root_cause["category"] = "quota_limit_error"
            root_cause["likely_solutions"] = [
                "Check API usage and remaining credits",
                "Implement rate limiting in requests",
                "Upgrade API plan if necessary"
            ]
        
        elif 'timeout' in error_message:
            root_cause["primary_cause"] = "Processing timeout"
            root_cause["category"] = "processing_timeout"
            root_cause["likely_solutions"] = [
                "Reduce template complexity",
                "Optimize image sizes and formats",
                "Simplify transitions and effects"
            ]
        
        return root_cause
    
    def _generate_recovery_plan(self, movie_data: Dict) -> list:
        """Generate specific recovery recommendations"""
        recommendations = []
        
        error_message = movie_data.get('message', '').lower()
        
        if 'source url is required' in error_message:
            recommendations.extend([
                {
                    "priority": "high",
                    "action": "Fix audio URL validation",
                    "steps": [
                        "Check all audio elements in the JSON template",
                        "Ensure no empty src: '' values",
                        "Validate Google Drive audio URLs are accessible",
                        "Test ElevenLabs voice generation endpoints",
                        "Implement fallback audio sources"
                    ],
                    "validation": "Run template through schema validator before submission"
                },
                {
                    "priority": "medium",
                    "action": "Implement audio URL verification",
                    "steps": [
                        "Add pre-flight checks for all audio URLs",
                        "Implement HTTP HEAD requests to verify URL accessibility",
                        "Add retry logic for temporary audio generation failures"
                    ]
                }
            ])
        
        # Always add general recovery steps
        recommendations.extend([
            {
                "priority": "medium",
                "action": "Regenerate video with corrected template",
                "steps": [
                    "Apply identified fixes to template",
                    "Test template with minimal configuration first",
                    "Gradually add complexity after basic version works",
                    "Monitor generation process closely"
                ]
            },
            {
                "priority": "low",
                "action": "Implement enhanced error monitoring",
                "steps": [
                    "Add pre-submission template validation",
                    "Implement automated error recovery workflows",
                    "Create alerting for similar failures"
                ]
            }
        ])
        
        return recommendations
    
    def _generate_monitoring_suggestions(self, analysis_report: Dict) -> list:
        """Generate monitoring protocol suggestions"""
        suggestions = [
            {
                "category": "api_monitoring",
                "recommendation": "Implement 5-minute initial delay before status checks",
                "rationale": "Prevents server overload and allows proper processing time"
            },
            {
                "category": "status_checking",
                "recommendation": "Use 1-minute intervals for status polling",
                "rationale": "Server-friendly timing while maintaining responsiveness"
            },
            {
                "category": "error_detection",
                "recommendation": "Monitor for success: false and status: error patterns",
                "rationale": "Catches both explicit error flags and status-based failures"
            },
            {
                "category": "continuous_monitoring",
                "recommendation": "Continue monitoring even after successful completion",
                "rationale": "Verifies video URL accessibility and final delivery"
            },
            {
                "category": "airtable_integration",
                "recommendation": "Update VideoGenerationStatus with detailed error messages",
                "rationale": "Provides visibility into failure reasons for debugging"
            }
        ]
        
        return suggestions
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main analysis function"""
    # Load API key
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)
    
    api_key = config['json2video_api_key']
    project_id = "ZRKDMhlcMEhAtasZ"
    
    analyzer = VideoStatusAnalyzer(api_key)
    
    try:
        print("=" * 80)
        print("🎬 JSON2Video Project Status Analysis Report")
        print("=" * 80)
        print(f"📋 Project ID: {project_id}")
        print(f"⏰ Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 80)
        
        # Perform comprehensive analysis
        analysis = await analyzer.analyze_failed_project(project_id)
        
        # Display results
        print("\n📊 API RESPONSE ANALYSIS")
        print(f"HTTP Status Code: {analysis.get('http_status_code', 'N/A')}")
        print(f"Project Status: {analysis.get('status', 'unknown')}")
        
        if analysis.get('raw_api_response'):
            print("\n🔍 RAW API RESPONSE:")
            print(json.dumps(analysis['raw_api_response'], indent=2))
        
        if analysis.get('error_details'):
            print("\n❌ ERROR DETAILS:")
            for key, value in analysis['error_details'].items():
                print(f"  {key}: {value}")
        
        if analysis.get('root_cause_analysis'):
            print("\n🔬 ROOT CAUSE ANALYSIS:")
            rca = analysis['root_cause_analysis']
            print(f"  Primary Cause: {rca.get('primary_cause', 'unknown')}")
            print(f"  Category: {rca.get('category', 'unknown')}")
            
            if rca.get('technical_details'):
                print("  Technical Details:")
                for key, value in rca['technical_details'].items():
                    print(f"    {key}: {value}")
        
        if analysis.get('recovery_recommendations'):
            print("\n🛠️ RECOVERY RECOMMENDATIONS:")
            for i, rec in enumerate(analysis['recovery_recommendations'], 1):
                print(f"  {i}. {rec['action']} (Priority: {rec['priority']})")
                if 'steps' in rec:
                    for step in rec['steps']:
                        print(f"     - {step}")
        
        if analysis.get('monitoring_suggestions'):
            print("\n📈 MONITORING PROTOCOL SUGGESTIONS:")
            for suggestion in analysis['monitoring_suggestions']:
                print(f"  • {suggestion['category'].upper()}: {suggestion['recommendation']}")
                print(f"    Rationale: {suggestion['rationale']}")
        
        # Save detailed report
        report_filename = f"/home/claude-workflow/video_status_analysis_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n📄 Detailed analysis saved to: {report_filename}")
        print("=" * 80)
        
    finally:
        await analyzer.close()

if __name__ == "__main__":
    asyncio.run(main())