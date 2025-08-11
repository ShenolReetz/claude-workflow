#!/usr/bin/env python3
"""
Run Production Workflow with Token Refresh
==========================================
This script refreshes Google Drive token before running the workflow
"""

import sys
import asyncio
sys.path.append('/home/claude-workflow')

from src.utils.google_drive_token_manager import GoogleDriveTokenManager
from src.Production_workflow_runner import ProductionContentPipelineOrchestratorV2

async def main():
    print("=" * 60)
    print("🚀 PRODUCTION WORKFLOW RUNNER WITH TOKEN REFRESH")
    print("=" * 60)
    
    # Step 1: Refresh Google Drive Token
    print("\n🔄 Step 1: Refreshing Google Drive token...")
    token_manager = GoogleDriveTokenManager()
    token_status = token_manager.get_token_status()
    
    print(f"   Token status: {token_status['status']}")
    print(f"   Needs refresh: {token_status['needs_refresh']}")
    
    if token_status['needs_refresh']:
        success, message = token_manager.refresh_token()
        if success:
            print(f"   ✅ Token refreshed successfully: {message}")
        else:
            print(f"   ⚠️ Token refresh failed: {message}")
            print("   Note: Google Drive upload may fail")
    else:
        print("   ✅ Token is still valid")
    
    # Step 2: Run the workflow
    print("\n🎬 Step 2: Starting Production Workflow...")
    print("-" * 60)
    
    orchestrator = ProductionContentPipelineOrchestratorV2()
    await orchestrator.run_complete_workflow()

if __name__ == "__main__":
    asyncio.run(main())