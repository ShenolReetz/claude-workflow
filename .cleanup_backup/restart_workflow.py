#!/usr/bin/env python3
"""
Intelligent Workflow Restart - Resume failed workflows from optimal checkpoint
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Optional

sys.path.append('/home/claude-workflow')

# Import the main workflow
from src.Production_workflow_runner import ProductionContentPipelineOrchestratorV2

class WorkflowRecoveryManager:
    def __init__(self):
        self.orchestrator = ProductionContentPipelineOrchestratorV2()

    async def find_recoverable_records(self) -> list:
        """Find records that failed due to recoverable errors"""
        
        # Get records with failure status
        failed_records = await self.orchestrator.airtable_server.get_records_by_status([
            'Failed - API Quota Exhausted',
            'Failed - Rate Limited',
            'Failed - Video Creation',
            'Processing'  # May have been interrupted
        ])
        
        recoverable = []
        for record in failed_records:
            fields = record.get('fields', {})
            
            # Check what stage it failed at
            stage_info = self._analyze_completion_stage(fields)
            if stage_info['recoverable']:
                recoverable.append({
                    'record_id': record['id'],
                    'title': fields.get('Title', 'Unknown'),
                    'status': fields.get('Status', 'Unknown'),
                    'stage': stage_info,
                    'fields': fields
                })
        
        return recoverable

    def _analyze_completion_stage(self, fields: Dict) -> Dict:
        """Analyze how far the workflow progressed"""
        
        # Check key completion indicators
        has_products = any(fields.get(f'ProductNo{i}Name') for i in range(1, 6))
        has_scripts = any(fields.get(f'Product{i}Script') for i in range(1, 6))
        has_audio = fields.get('IntroAudioURL') or fields.get('OutroAudioURL')
        has_video = fields.get('VideoURL')
        
        if has_video:
            return {
                'stage': 'completed',
                'recoverable': False,
                'resume_from': 'complete'
            }
        elif has_audio:
            return {
                'stage': 'video_creation',
                'recoverable': True,
                'resume_from': 'video_creation',
                'description': 'Has audio, needs video creation'
            }
        elif has_scripts:
            return {
                'stage': 'audio_generation', 
                'recoverable': True,
                'resume_from': 'audio_generation',
                'description': 'Has scripts, needs audio and video'
            }
        elif has_products:
            return {
                'stage': 'content_generation',
                'recoverable': True, 
                'resume_from': 'content_generation',
                'description': 'Has products, needs scripts, audio, and video'
            }
        else:
            return {
                'stage': 'product_scraping',
                'recoverable': True,
                'resume_from': 'full_workflow',
                'description': 'Needs complete restart'
            }

    async def resume_workflow_from_stage(self, record_data: Dict):
        """Resume workflow from specific stage"""
        
        record_id = record_data['record_id']
        stage = record_data['stage']['resume_from']
        
        print(f"\n🔄 RESUMING WORKFLOW for: {record_data['title']}")
        print(f"📍 Resume from: {stage}")
        print(f"💬 Stage info: {record_data['stage']['description']}")
        
        try:
            # Update status to Processing
            await self.orchestrator.airtable_server.update_record_field(
                record_id, 'Status', 'Processing'
            )
            
            # Create record structure for MCP agents
            record = {
                'record_id': record_id,
                'fields': record_data['fields']
            }
            
            if stage == 'content_generation':
                await self._resume_from_content_generation(record)
            elif stage == 'audio_generation':
                await self._resume_from_audio_generation(record)
            elif stage == 'video_creation':
                await self._resume_from_video_creation(record)
            elif stage == 'full_workflow':
                # Run complete workflow
                await self.orchestrator.run_complete_workflow()
            else:
                print(f"❌ Unknown resume stage: {stage}")
                return
                
            print(f"✅ Workflow resumed successfully for: {record_data['title']}")
            
        except Exception as e:
            print(f"❌ Resume failed: {e}")
            await self.orchestrator.airtable_server.update_record_field(
                record_id, 'Status', f'Failed - Resume Error'
            )

    async def _resume_from_content_generation(self, record: Dict):
        """Resume from content generation stage"""
        print("📝 Generating missing content...")
        
        # Import required agents
        from src.mcp.Production_text_generation_control_agent_mcp_v2 import production_run_text_control_with_regeneration
        from src.mcp.Production_voice_timing_optimizer import ProductionVoiceTimingOptimizer
        from src.mcp.Production_intro_image_generator import production_generate_intro_image_for_workflow
        from src.mcp.Production_outro_image_generator import production_generate_outro_image_for_workflow
        from src.mcp.Production_json2video_agent_mcp import production_run_video_creation
        
        # Generate scripts
        script_result = await production_run_text_control_with_regeneration(record, self.orchestrator.config)
        if not script_result.get('success'):
            raise Exception("Script generation failed")
        
        # Continue with audio generation
        await self._resume_from_audio_generation(script_result['updated_record'])

    async def _resume_from_audio_generation(self, record: Dict):
        """Resume from audio generation stage"""
        print("🎙️ Generating missing audio...")
        
        # Generate voice
        voice_result = await self.orchestrator.voice_server.generate_voice_for_record(record)
        
        # Generate images if missing
        intro_result = await production_generate_intro_image_for_workflow(
            voice_result['updated_record'], self.orchestrator.config
        )
        outro_result = await production_generate_outro_image_for_workflow(
            intro_result['updated_record'], self.orchestrator.config
        )
        
        # Continue with video creation
        await self._resume_from_video_creation(outro_result['updated_record'])

    async def _resume_from_video_creation(self, record: Dict):
        """Resume from video creation stage"""
        print("🎬 Creating video...")
        
        from src.mcp.Production_json2video_agent_mcp import production_run_video_creation
        from src.mcp.Production_enhanced_google_drive_agent_mcp import production_upload_all_assets_to_google_drive
        
        # Create video
        video_result = await production_run_video_creation(record, self.orchestrator.config)
        if not video_result.get('success'):
            raise Exception("Video creation failed")
        
        # Upload to Google Drive
        drive_result = await production_upload_all_assets_to_google_drive(
            video_result['updated_record'], self.orchestrator.config
        )
        
        # Mark as completed
        await self.orchestrator.airtable_server.update_record_field(
            record['record_id'], 'Status', 'Completed'
        )

    async def interactive_recovery(self):
        """Interactive recovery menu"""
        recoverable = await self.find_recoverable_records()
        
        if not recoverable:
            print("✅ No recoverable workflows found")
            return
        
        print(f"\n🔍 Found {len(recoverable)} recoverable workflows:")
        print("=" * 60)
        
        for i, record in enumerate(recoverable, 1):
            print(f"{i}. {record['title']}")
            print(f"   Status: {record['status']}")
            print(f"   Stage: {record['stage']['description']}")
            print()
        
        print("0. Resume all recoverable workflows")
        print("q. Quit")
        
        choice = input("\nSelect workflow to resume (0 for all, q to quit): ").strip()
        
        if choice.lower() == 'q':
            return
        elif choice == '0':
            # Resume all
            for record in recoverable:
                await self.resume_workflow_from_stage(record)
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(recoverable):
                    await self.resume_workflow_from_stage(recoverable[index])
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")

async def main():
    print("🔧 WORKFLOW RECOVERY MANAGER")
    print("=" * 40)
    
    recovery = WorkflowRecoveryManager()
    await recovery.interactive_recovery()

if __name__ == "__main__":
    asyncio.run(main())