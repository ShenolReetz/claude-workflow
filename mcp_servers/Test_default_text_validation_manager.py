#!/usr/bin/env python3
"""
Test Default Text Validation Manager

This manager pre-populates Airtable status columns with "Approved" values
for test environment speed optimization.

Test-only optimization - NOT for production integration.
"""

import json
import asyncio
from typing import Dict, Any, List

class TestDefaultTextValidationManager:
    """Manager for pre-populating text validation status columns in test mode"""
    
    def __init__(self):
        # All text validation status columns that should be pre-populated
        # EXACT COLUMN NAMES FROM ToDo.md - DO NOT CHANGE
        self.validation_status_columns = [
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
        
        # Default approved status
        self.default_status = "Approved"
    
    async def populate_default_validation_status(self, airtable_server, record_id: str) -> Dict[str, Any]:
        """
        Populate all text validation status columns with 'Approved' for test speed optimization
        
        Args:
            airtable_server: Airtable MCP server instance
            record_id: Record ID to update
            
        Returns:
            Dict with success status and populated columns
        """
        
        print(f"📝 TEST MODE: Pre-populating text validation status columns...")
        
        try:
            # Create updates dict with all status columns set to "Approved"
            updates = {}
            for column in self.validation_status_columns:
                updates[column] = self.default_status
            
            # Update the record
            result = await airtable_server.update_record(record_id, updates)
            
            if result:
                print(f"✅ Successfully pre-populated {len(self.validation_status_columns)} text validation status columns")
                print(f"   All columns set to: {self.default_status}")
                return {
                    "success": True,
                    "columns_updated": len(self.validation_status_columns),
                    "status_value": self.default_status,
                    "columns": self.validation_status_columns
                }
            else:
                print(f"❌ Failed to update text validation status columns")
                return {
                    "success": False,
                    "error": "Failed to update Airtable record"
                }
                
        except Exception as e:
            print(f"❌ Error populating text validation status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_validation_status_columns(self) -> List[str]:
        """Get list of all text validation status columns"""
        return self.validation_status_columns.copy()
    
    def get_default_status(self) -> str:
        """Get the default status value"""
        return self.default_status

# Test function
async def test_default_text_validation_manager():
    """Test the default text validation manager"""
    
    print("="*80)
    print("🧪 Testing Default Text Validation Manager")
    print("="*80)
    
    manager = TestDefaultTextValidationManager()
    
    print(f"\n📋 Text Validation Status Columns:")
    for i, column in enumerate(manager.get_validation_status_columns(), 1):
        print(f"   {i:2d}. {column}")
    
    print(f"\n✅ Default Status: {manager.get_default_status()}")
    print(f"📊 Total Columns: {len(manager.get_validation_status_columns())}")
    
    print("\n" + "="*80)
    print("✅ Test Complete")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_default_text_validation_manager())