#!/usr/bin/env python3
"""
Test Text Length Validation Agent MCP

This agent orchestrates the text validation workflow:
1. Fetches content from Airtable
2. Validates all text fields via MCP server
3. Updates Airtable status columns with results

Test version for development and testing.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.Test_airtable_server import AirtableMCPServer
from mcp_servers.Test_text_length_validation_server import TestTextLengthValidationMCPServer

class TestTextLengthValidationAgent:
    """Test agent for orchestrating text length validation workflow"""
    
    def __init__(self):
        # Load API keys
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            self.api_keys = json.load(f)
        
        # Initialize servers
        self.airtable_server = AirtableMCPServer(
            api_key=self.api_keys['airtable_api_key'],
            base_id=self.api_keys['airtable_base_id'],
            table_name=self.api_keys['airtable_table_name']
        )
        
        self.validation_server = TestTextLengthValidationMCPServer()
        
        # Field validation mapping - EXACT COLUMN NAMES FROM ToDo.md
        self.validation_fields = {
            # Video fields (5 second limit)
            'VideoTitle': {
                'status_column': 'VideoTitleStatus',        # → Validates: VideoTitle field
                'scene_type': 'intro',
                'max_seconds': 5
            },
            'VideoDescription': {
                'status_column': 'VideoDescriptionStatus',  # → Validates: VideoDescription field
                'scene_type': 'intro',
                'max_seconds': 5
            },
            
            # Product fields (9 second limit each)
            'ProductNo1Title': {
                'status_column': 'ProductNo1TitleStatus',       # → Validates: ProductNo1Title field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo1Description': {
                'status_column': 'ProductNo1DescriptionStatus', # → Validates: ProductNo1Description field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo2Title': {
                'status_column': 'ProductNo2TitleStatus',       # → Validates: ProductNo2Title field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo2Description': {
                'status_column': 'ProductNo2DescriptionStatus', # → Validates: ProductNo2Description field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo3Title': {
                'status_column': 'ProductNo3TitleStatus',       # → Validates: ProductNo3Title field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo3Description': {
                'status_column': 'ProductNo3DescriptionStatus', # → Validates: ProductNo3Description field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo4Title': {
                'status_column': 'ProductNo4TitleStatus',       # → Validates: ProductNo4Title field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo4Description': {
                'status_column': 'ProductNo4DescriptionStatus', # → Validates: ProductNo4Description field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo5Title': {
                'status_column': 'ProductNo5TitleStatus',       # → Validates: ProductNo5Title field
                'scene_type': 'product',
                'max_seconds': 9
            },
            'ProductNo5Description': {
                'status_column': 'ProductNo5DescriptionStatus', # → Validates: ProductNo5Description field
                'scene_type': 'product',
                'max_seconds': 9
            }
        }
    
    async def validate_record(self, record_id: str, title: str) -> Dict[str, Any]:
        """Validate all text fields for a single record"""
        
        print(f"\n{'='*60}")
        print(f"🔍 Validating text timing for: {title}")
        print(f"Record ID: {record_id}")
        print(f"{'='*60}")
        
        try:
            # Get the full record from Airtable
            record = await self.airtable_server.get_record(record_id)
            
            if not record:
                print(f"❌ Could not fetch record {record_id}")
                return {
                    "success": False,
                    "error": "Could not fetch record",
                    "record_id": record_id
                }
            
            # Prepare batch validation
            validations = []
            for field_name, config in self.validation_fields.items():
                text = record.get('fields', {}).get(field_name, '')
                if text:  # Only validate non-empty fields
                    validations.append({
                        "field_name": field_name,
                        "text": text,
                        "scene_type": config['scene_type']
                    })
            
            # Perform batch validation
            print(f"\n📊 Validating {len(validations)} text fields...")
            validation_results = await self.validation_server.validate_batch(validations)
            
            # Process results and prepare updates
            updates = {}
            validation_summary = []
            
            for result in validation_results['results']:
                field_name = result['field_name']
                status = result['status']
                config = self.validation_fields[field_name]
                status_column = config['status_column']
                
                # Update status column
                updates[status_column] = status
                
                # Log result
                emoji = "✅" if status == "Approved" else "❌"
                message = f"{emoji} {field_name}: {result['word_count']} words, ~{result['estimated_duration']}s (limit: {result['max_seconds']}s)"
                print(message)
                validation_summary.append(message)
            
            # Update Airtable with all status values
            if updates:
                print(f"\n📝 Updating {len(updates)} status columns in Airtable...")
                update_result = await self.airtable_server.update_record(
                    record_id=record_id,
                    fields=updates
                )
                
                if update_result:
                    print(f"✅ Successfully updated status columns")
                else:
                    print(f"❌ Failed to update status columns")
                    return {
                        "success": False,
                        "error": "Failed to update Airtable",
                        "record_id": record_id
                    }
            
            # Summary
            summary = validation_results['summary']
            print(f"\n📊 Validation Summary:")
            print(f"   Total fields: {summary['total']}")
            print(f"   ✅ Approved: {summary['approved']}")
            print(f"   ❌ Rejected: {summary['rejected']}")
            print(f"   ⏳ Pending: {summary['pending']}")
            
            return {
                "success": True,
                "record_id": record_id,
                "title": title,
                "summary": summary,
                "all_approved": validation_results['all_approved'],
                "has_rejections": validation_results['has_rejections'],
                "validation_details": validation_summary,
                "updates_applied": updates
            }
            
        except Exception as e:
            print(f"❌ Error validating record: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id
            }
    
    async def run_validation_workflow(self, limit: int = 5) -> Dict[str, Any]:
        """Run the complete validation workflow"""
        
        print("\n" + "="*80)
        print("🚀 Starting Text Length Validation Workflow")
        print("="*80)
        
        results = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "all_approved": 0,
            "has_rejections": 0,
            "records": []
        }
        
        try:
            # Get records to validate
            print(f"\n📋 Fetching up to {limit} records to validate...")
            
            # For testing, we'll get all records and validate them
            # In production, you might want to filter by specific criteria
            all_records = await self.airtable_server.list_records(max_records=limit)
            
            if not all_records or not all_records.get('records'):
                print("❌ No records found to validate")
                return results
            
            records = all_records['records']
            print(f"✅ Found {len(records)} records to validate")
            
            # Process each record
            for record in records:
                record_id = record['id']
                title = record['fields'].get('Title', 'Unknown')
                
                # Validate the record
                validation_result = await self.validate_record(record_id, title)
                
                results["total_processed"] += 1
                
                if validation_result["success"]:
                    results["successful"] += 1
                    if validation_result.get("all_approved"):
                        results["all_approved"] += 1
                    if validation_result.get("has_rejections"):
                        results["has_rejections"] += 1
                else:
                    results["failed"] += 1
                
                results["records"].append(validation_result)
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            
            # Final summary
            print("\n" + "="*80)
            print("📊 WORKFLOW SUMMARY")
            print("="*80)
            print(f"Total records processed: {results['total_processed']}")
            print(f"✅ Successful validations: {results['successful']}")
            print(f"❌ Failed validations: {results['failed']}")
            print(f"🎯 All fields approved: {results['all_approved']}")
            print(f"⚠️  Has rejections: {results['has_rejections']}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ Workflow error: {str(e)}")
            results["error"] = str(e)
            return results

async def run_text_length_validation(record_id: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
    """Main entry point for text length validation workflow"""
    
    agent = TestTextLengthValidationAgent()
    
    if record_id:
        # Validate a specific record
        # First get the title
        record = await agent.airtable_server.get_record(record_id)
        if record:
            title = record['fields'].get('Title', 'Unknown')
            return await agent.validate_record(record_id, title)
        else:
            return {
                "success": False,
                "error": f"Record {record_id} not found"
            }
    else:
        # Run full workflow
        return await agent.run_validation_workflow(limit=limit)

# For testing
async def main():
    """Test the text length validation workflow"""
    
    # Test with a small batch
    results = await run_text_length_validation(limit=3)
    
    print("\n" + "="*80)
    print("✅ Text Length Validation Test Complete")
    print("="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())