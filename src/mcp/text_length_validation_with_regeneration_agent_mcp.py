#!/usr/bin/env python3
"""
Text Length Validation with Regeneration Agent MCP

This agent orchestrates the text validation workflow with intelligent error handling:
1. Validates all text fields for TTS timing compliance
2. For failed fields, triggers regeneration with specific timing constraints
3. Sets status to "Pending" during regeneration
4. Re-validates regenerated content
5. Updates final status based on validation results

Production version with comprehensive error handling.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp_servers.airtable_server import AirtableMCPServer
from mcp_servers.text_length_validation_server import TextLengthValidationMCPServer
from mcp_servers.text_regeneration_server import TextRegenerationServer

class TextLengthValidationWithRegenerationAgent:
    """Agent for text validation with intelligent regeneration of failed fields"""
    
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
        
        self.validation_server = TextLengthValidationMCPServer()
        self.regeneration_server = TextRegenerationServer(
            anthropic_api_key=self.api_keys['anthropic_api_key']
        )
        
        # Field validation mapping with regeneration info - EXACT COLUMN NAMES FROM ToDo.md
        self.validation_fields = {
            # Video fields (5 second limit)
            'VideoTitle': {
                'status_column': 'VideoTitleStatus',        # → Validates: VideoTitle field
                'scene_type': 'intro',
                'max_seconds': 5,
                'regeneration_context': 'video_title'
            },
            'VideoDescription': {
                'status_column': 'VideoDescriptionStatus',  # → Validates: VideoDescription field
                'scene_type': 'intro',
                'max_seconds': 5,
                'regeneration_context': 'video_description'
            },
            
            # Product fields (9 second limit each)
            'ProductNo1Title': {
                'status_column': 'ProductNo1TitleStatus',       # → Validates: ProductNo1Title field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_title'
            },
            'ProductNo1Description': {
                'status_column': 'ProductNo1DescriptionStatus', # → Validates: ProductNo1Description field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_description'
            },
            'ProductNo2Title': {
                'status_column': 'ProductNo2TitleStatus',       # → Validates: ProductNo2Title field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_title'
            },
            'ProductNo2Description': {
                'status_column': 'ProductNo2DescriptionStatus', # → Validates: ProductNo2Description field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_description'
            },
            'ProductNo3Title': {
                'status_column': 'ProductNo3TitleStatus',       # → Validates: ProductNo3Title field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_title'
            },
            'ProductNo3Description': {
                'status_column': 'ProductNo3DescriptionStatus', # → Validates: ProductNo3Description field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_description'
            },
            'ProductNo4Title': {
                'status_column': 'ProductNo4TitleStatus',       # → Validates: ProductNo4Title field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_title'
            },
            'ProductNo4Description': {
                'status_column': 'ProductNo4DescriptionStatus', # → Validates: ProductNo4Description field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_description'
            },
            'ProductNo5Title': {
                'status_column': 'ProductNo5TitleStatus',       # → Validates: ProductNo5Title field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_title'
            },
            'ProductNo5Description': {
                'status_column': 'ProductNo5DescriptionStatus', # → Validates: ProductNo5Description field
                'scene_type': 'product',
                'max_seconds': 9,
                'regeneration_context': 'product_description'
            }
        }
        
        # Maximum regeneration attempts per field
        self.max_regeneration_attempts = 3
        
        # Maximum total regeneration cycles
        self.max_regeneration_cycles = 2
    
    async def validate_and_regenerate_record(self, record_id: str, title: str) -> Dict[str, Any]:
        """Validate all text fields and regenerate failed ones"""
        
        print(f"\n{'='*80}")
        print(f"🔍 Text Validation with Regeneration: {title}")
        print(f"Record ID: {record_id}")
        print(f"{'='*80}")
        
        cycle_count = 0
        
        while cycle_count < self.max_regeneration_cycles:
            cycle_count += 1
            print(f"\n🔄 Validation Cycle {cycle_count}/{self.max_regeneration_cycles}")
            
            # Perform validation
            validation_result = await self.validate_record(record_id, title)
            
            if not validation_result["success"]:
                return validation_result
            
            # Check if we have rejections
            if not validation_result.get("has_rejections", False):
                print(f"✅ All fields validated successfully!")
                return validation_result
            
            # Extract failed fields
            failed_fields = []
            for result in validation_result.get("validation_results", []):
                if result.get("status") == "Rejected" and "word_count" in result:
                    failed_fields.append({
                        "field_name": result["field_name"],
                        "current_text": result.get("text_preview", ""),
                        "word_count": result.get("word_count", 0),
                        "estimated_duration": result.get("estimated_duration", 0),
                        "max_seconds": result.get("max_seconds", 0)
                    })
            
            if not failed_fields:
                break
            
            print(f"\n⚠️ Found {len(failed_fields)} fields that need regeneration")
            
            # Set failed fields to "Pending" status
            await self.set_fields_to_pending(record_id, failed_fields)
            
            # Regenerate failed fields
            regeneration_result = await self.regenerate_failed_fields(
                record_id, failed_fields, title
            )
            
            if not regeneration_result["success"]:
                print(f"❌ Regeneration failed: {regeneration_result.get('error', 'Unknown error')}")
                return regeneration_result
            
            print(f"✅ Regenerated {regeneration_result['successful_regenerations']} fields")
            
            # Small delay before next validation cycle
            await asyncio.sleep(1)
        
        # Final validation to get the ultimate status
        print(f"\n📊 Final validation after {cycle_count} cycles...")
        final_validation = await self.validate_record(record_id, title)
        
        if final_validation.get("has_rejections", False):
            print(f"⚠️ Some fields still exceed timing limits after {cycle_count} regeneration cycles")
        
        return final_validation
    
    async def validate_record(self, record_id: str, title: str) -> Dict[str, Any]:
        """Validate all text fields for a single record"""
        
        try:
            # Get the full record from Airtable
            record = await self.airtable_server.get_record_by_id(record_id)
            
            if not record:
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
            validation_results = await self.validation_server.validate_batch(validations)
            
            # Process results and prepare updates
            updates = {}
            validation_details = []
            
            for result in validation_results['results']:
                field_name = result['field_name']
                status = result['status']
                config = self.validation_fields[field_name]
                status_column = config['status_column']
                
                # Update status column
                updates[status_column] = status
                
                # Log result
                emoji = "✅" if status == "Approved" else "❌"
                if 'word_count' in result:
                    message = f"{emoji} {field_name}: {result['word_count']} words, ~{result['estimated_duration']}s (limit: {result['max_seconds']}s)"
                else:
                    # Handle case where text was empty/pending
                    message = result.get('message', f"{emoji} {field_name}: {status}")
                print(message)
                validation_details.append(result)
            
            # Update Airtable with all status values
            if updates:
                update_result = await self.airtable_server.update_record(
                    record_id=record_id,
                    fields=updates
                )
                
                if not update_result:
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
                "validation_results": validation_details,
                "updates_applied": updates
            }
            
        except Exception as e:
            print(f"❌ Error validating record: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "record_id": record_id
            }
    
    async def set_fields_to_pending(self, record_id: str, failed_fields: List[Dict[str, Any]]) -> bool:
        """Set failed fields' status columns to 'Pending' during regeneration"""
        
        print(f"\n📝 Setting {len(failed_fields)} fields to 'Pending' status...")
        
        try:
            updates = {}
            for field_info in failed_fields:
                field_name = field_info["field_name"]
                config = self.validation_fields[field_name]
                status_column = config['status_column']
                updates[status_column] = "Pending"
            
            result = await self.airtable_server.update_record(record_id, updates)
            
            if result:
                print(f"✅ Set {len(updates)} status columns to 'Pending'")
                return True
            else:
                print(f"❌ Failed to update status columns to 'Pending'")
                return False
                
        except Exception as e:
            print(f"❌ Error setting fields to pending: {str(e)}")
            return False
    
    async def regenerate_failed_fields(
        self, 
        record_id: str, 
        failed_fields: List[Dict[str, Any]], 
        title: str
    ) -> Dict[str, Any]:
        """Regenerate failed fields with timing constraints"""
        
        print(f"\n🔄 Regenerating {len(failed_fields)} failed fields...")
        
        try:
            # Get the record to extract context information
            record = await self.airtable_server.get_record_by_id(record_id)
            if not record:
                return {
                    "success": False,
                    "error": "Could not fetch record for regeneration context"
                }
            
            # Extract category for context
            category = record.get('fields', {}).get('Category', title)
            
            # Prepare regeneration requests
            regeneration_requests = []
            for field_info in failed_fields:
                field_name = field_info["field_name"]
                current_text = field_info["current_text"]
                
                # Get product name for product fields
                product_name = ""
                if field_name.startswith("ProductNo"):
                    product_num = field_name[9:10]  # Extract number
                    product_name = record.get('fields', {}).get(f'ProductNo{product_num}Name', '')
                
                regeneration_requests.append({
                    "field_name": field_name,
                    "current_text": current_text,
                    "category": category,
                    "product_name": product_name
                })
            
            # Perform batch regeneration
            regeneration_results = await self.regeneration_server.regenerate_multiple_fields(
                failed_fields=regeneration_requests,
                max_attempts=self.max_regeneration_attempts
            )
            
            # Process results and update Airtable
            updates = {}
            successful_regenerations = 0
            
            for result in regeneration_results['results']:
                if result["success"]:
                    field_name = result["field_name"]
                    new_text = result["new_text"]
                    
                    # Update the field with new text
                    updates[field_name] = new_text
                    successful_regenerations += 1
                    
                    if 'word_count' in result:
                        print(f"✅ {field_name}: {result['word_count']} words (was {result['original_text'][:30]}...)")
                    else:
                        print(f"✅ {field_name}: Regenerated successfully")
                else:
                    field_name = result["field_name"]
                    print(f"❌ {field_name}: {result.get('error', 'Unknown error')}")
            
            # Update Airtable with regenerated content
            if updates:
                update_result = await self.airtable_server.update_record(record_id, updates)
                
                if not update_result:
                    return {
                        "success": False,
                        "error": "Failed to update Airtable with regenerated content"
                    }
            
            return {
                "success": True,
                "total_fields": len(failed_fields),
                "successful_regenerations": successful_regenerations,
                "failed_regenerations": len(failed_fields) - successful_regenerations,
                "regeneration_results": regeneration_results['results'],
                "updates_applied": updates
            }
            
        except Exception as e:
            print(f"❌ Error during regeneration: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def run_validation_workflow(self, limit: int = 5) -> Dict[str, Any]:
        """Run the complete validation and regeneration workflow"""
        
        print("\n" + "="*80)
        print("🚀 Starting Text Validation with Regeneration Workflow")
        print("="*80)
        
        results = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "fully_approved": 0,
            "partially_approved": 0,
            "records": []
        }
        
        try:
            # Get records to validate
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
                
                # Validate and regenerate the record
                validation_result = await self.validate_and_regenerate_record(record_id, title)
                
                results["total_processed"] += 1
                
                if validation_result["success"]:
                    results["successful"] += 1
                    if validation_result.get("all_approved"):
                        results["fully_approved"] += 1
                    elif validation_result.get("has_rejections"):
                        results["partially_approved"] += 1
                else:
                    results["failed"] += 1
                
                results["records"].append(validation_result)
                
                # Delay between records
                await asyncio.sleep(1)
            
            # Final summary
            print("\n" + "="*80)
            print("📊 WORKFLOW SUMMARY")
            print("="*80)
            print(f"Total records processed: {results['total_processed']}")
            print(f"✅ Successful validations: {results['successful']}")
            print(f"❌ Failed validations: {results['failed']}")
            print(f"🎯 Fully approved: {results['fully_approved']}")
            print(f"⚠️  Partially approved: {results['partially_approved']}")
            
            return results
            
        except Exception as e:
            print(f"\n❌ Workflow error: {str(e)}")
            results["error"] = str(e)
            return results

async def run_text_validation_with_regeneration(record_id: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
    """Main entry point for text validation with regeneration workflow"""
    
    agent = TextLengthValidationWithRegenerationAgent()
    
    if record_id:
        # Validate a specific record
        record = await agent.airtable_server.get_record_by_id(record_id)
        if record:
            title = record['fields'].get('Title', 'Unknown')
            return await agent.validate_and_regenerate_record(record_id, title)
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
    """Test the text validation with regeneration workflow"""
    
    # Test with a small batch
    results = await run_text_validation_with_regeneration(limit=1)
    
    print("\n" + "="*80)
    print("✅ Text Validation with Regeneration Test Complete")
    print("="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())