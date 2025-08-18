#!/usr/bin/env python3
"""
Run Production Workflow with Local Storage Only
===============================================
This is the main entry point for the local storage workflow.
All media files are saved locally, WordPress uploads them during publishing.
"""

import asyncio
import sys
import logging
from datetime import datetime

# Add project to path
sys.path.append('/home/claude-workflow')

# Import the production flow
from src.production_flow import LocalStorageWorkflowRunner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    try:
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🚀 PRODUCTION WORKFLOW - LOCAL STORAGE VERSION 🚀     ║
║                                                            ║
║     • All media saved locally (no Google Drive)           ║
║     • WordPress uploads media during publishing           ║
║     • Remotion uses local files (100% reliable)           ║
║     • Faster workflow execution                           ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
        
        # Initialize and run workflow
        runner = LocalStorageWorkflowRunner()
        success = await runner.run()
        
        if success:
            print("""
╔════════════════════════════════════════════════════════════╗
║     ✅ WORKFLOW COMPLETED SUCCESSFULLY!                   ║
╚════════════════════════════════════════════════════════════╝
""")
            # Run cleanup for files older than 7 days
            print("\n🧹 Running cleanup for old files...")
            import subprocess
            subprocess.run([
                "python3", 
                "/home/claude-workflow/cleanup_local_storage.py",
                "--days", "7"
            ])
        else:
            print("""
╔════════════════════════════════════════════════════════════╗
║     ❌ WORKFLOW FAILED - CHECK LOGS                       ║
╚════════════════════════════════════════════════════════════╝
""")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Workflow interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)