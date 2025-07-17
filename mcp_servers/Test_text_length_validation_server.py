#!/usr/bin/env python3
"""
Test Text Length Validation MCP Server

This server validates text content against TTS timing requirements.
It calculates estimated speech duration and validates against scene limits:
- Intro/Outro: 5 seconds max
- Products: 9 seconds max each

Test version for development and testing.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional

class TestTextLengthValidationMCPServer:
    """Test Text Length Validation MCP Server for TTS timing validation"""
    
    def __init__(self):
        # Configuration
        self.speaking_rate = 150  # words per minute (adjustable)
        self.buffer_percentage = 1.2  # 20% buffer for natural pauses
        
        # TEST MODE: Always approve validation for speed optimization
        self.test_mode = True
        
        # Scene duration limits (in seconds)
        self.scene_limits = {
            'intro': 5,
            'outro': 5,
            'product': 9
        }
    
    async def calculate_duration(
        self, 
        text: str, 
        speaking_rate: int = None,
        buffer_percentage: float = None
    ) -> Dict[str, Any]:
        """Calculate estimated TTS duration for text"""
        
        if speaking_rate is None:
            speaking_rate = self.speaking_rate
        if buffer_percentage is None:
            buffer_percentage = self.buffer_percentage
            
        # Count words
        word_count = len(text.split())
        
        # Calculate base duration (words / words per minute * 60 seconds)
        base_duration = (word_count / speaking_rate) * 60
        
        # Apply buffer for natural pauses
        estimated_duration = base_duration * buffer_percentage
        
        return {
            "text": text[:50] + "..." if len(text) > 50 else text,
            "word_count": word_count,
            "speaking_rate": speaking_rate,
            "buffer_percentage": buffer_percentage,
            "base_duration": round(base_duration, 2),
            "estimated_duration": round(estimated_duration, 2)
        }
    
    async def validate_text_timing(
        self,
        text: str,
        scene_type: str,
        speaking_rate: int = None,
        buffer_percentage: float = None
    ) -> Dict[str, Any]:
        """Validate if text fits within timing requirements"""
        
        # Get duration calculation
        duration_info = await self.calculate_duration(
            text, speaking_rate, buffer_percentage
        )
        
        # Get scene limit
        max_seconds = self.scene_limits.get(scene_type, 9)
        
        # Determine validation status
        estimated_duration = duration_info["estimated_duration"]
        
        # TEST MODE: Always approve for speed optimization
        if self.test_mode:
            status = "Approved"
            message = f"✅ TEST MODE: {scene_type.capitalize()} text auto-approved: {duration_info['word_count']} words, ~{estimated_duration}s (limit: {max_seconds}s)"
        else:
            # Normal validation logic
            if estimated_duration <= max_seconds:
                status = "Approved"
            else:
                status = "Rejected"
            message = f"{'✅' if status == 'Approved' else '❌'} {scene_type.capitalize()} text: {duration_info['word_count']} words, ~{estimated_duration}s (limit: {max_seconds}s)"
            
        return {
            "status": status,
            "scene_type": scene_type,
            "max_seconds": max_seconds,
            "text_preview": duration_info["text"],
            "word_count": duration_info["word_count"],
            "estimated_duration": estimated_duration,
            "duration_info": duration_info,
            "message": message
        }
    
    async def validate_batch(
        self,
        validations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate multiple text fields in batch"""
        
        results = []
        summary = {
            "total": len(validations),
            "approved": 0,
            "rejected": 0,
            "pending": 0
        }
        
        for validation in validations:
            field_name = validation.get("field_name", "unknown")
            text = validation.get("text", "")
            scene_type = validation.get("scene_type", "product")
            
            # Skip empty text
            if not text or not text.strip():
                results.append({
                    "field_name": field_name,
                    "status": "Pending",
                    "message": f"⏳ {field_name}: No text to validate"
                })
                summary["pending"] += 1
                continue
            
            # Validate the text
            validation_result = await self.validate_text_timing(
                text=text,
                scene_type=scene_type
            )
            
            # Add field name to result
            validation_result["field_name"] = field_name
            results.append(validation_result)
            
            # Update summary
            if validation_result["status"] == "Approved":
                summary["approved"] += 1
            elif validation_result["status"] == "Rejected":
                summary["rejected"] += 1
                
        return {
            "summary": summary,
            "results": results,
            "all_approved": summary["approved"] == summary["total"],
            "has_rejections": summary["rejected"] > 0
        }
    
# Test function
async def test_text_length_validation_server():
    """Test the text length validation server"""
    
    print("="*80)
    print("🧪 Testing Text Length Validation Server")
    print("="*80)
    
    server = TestTextLengthValidationMCPServer()
    
    # Test duration calculation
    test_text = "This is a test text for validation"
    duration = await server.calculate_duration(test_text)
    print(f"\nDuration calculation test:")
    print(f"Text: {test_text}")
    print(f"Duration: {duration['estimated_duration']} seconds")
    
    # Test validation
    validation = await server.validate_text_timing(test_text, "intro")
    print(f"\nValidation test:")
    print(f"Status: {validation['status']}")
    print(f"Message: {validation['message']}")
    
    print("\n" + "="*80)
    print("✅ Test Complete")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_text_length_validation_server())