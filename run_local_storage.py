#!/usr/bin/env python3
"""
Run Production Workflow with Local Storage Only
===============================================
This is the main entry point for the local storage workflow.
All media files are saved locally, WordPress uploads them during publishing.

UPDATED: Now supports both legacy workflow and new agent-based system!

Usage:
    python run_local_storage.py                    # Use NEW agent system (default)
    python run_local_storage.py --legacy           # Use legacy workflow
    python run_local_storage.py --agent-system     # Explicitly use agent system
    python run_local_storage.py --type wow         # Use agent system with WOW video
"""

import asyncio
import sys
import argparse
import logging
from datetime import datetime

# Add project to path
sys.path.append('/home/claude-workflow')

# Import both workflows
from src.production_flow import LocalStorageWorkflowRunner  # Legacy
from agents.agent_initializer import initialize_agent_system  # New agent system
from agents.orchestrator import WorkflowType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run production workflow')

    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Use legacy workflow system (old production_flow.py)'
    )

    parser.add_argument(
        '--agent-system',
        action='store_true',
        help='Use new agent-based system (default)'
    )

    parser.add_argument(
        '--type',
        choices=['standard', 'wow'],
        default='standard',
        help='Workflow type for agent system (standard or wow)'
    )

    return parser.parse_args()


async def run_legacy_workflow():
    """Run the legacy workflow system"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🚀 LEGACY WORKFLOW - LOCAL STORAGE VERSION 🚀         ║
║                                                            ║
║     • All media saved locally (no Google Drive)           ║
║     • WordPress uploads media during publishing           ║
║     • Remotion uses local files (100% reliable)           ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

    # Initialize and run legacy workflow
    runner = LocalStorageWorkflowRunner()
    success = await runner.run()

    if success:
        print("""
╔════════════════════════════════════════════════════════════╗
║     ✅ WORKFLOW COMPLETED SUCCESSFULLY!                   ║
╚════════════════════════════════════════════════════════════╝
""")
        print("\n🧹 Note: Complete cleanup runs every Sunday at 07:00 via cron")
        print("   To run cleanup manually: python3 cleanup_all_storage.py")
    else:
        print("""
╔════════════════════════════════════════════════════════════╗
║     ❌ WORKFLOW FAILED - CHECK LOGS                       ║
╚════════════════════════════════════════════════════════════╝
""")

    return success


async def run_agent_workflow(workflow_type: str = 'standard'):
    """Run the new agent-based workflow system"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🚀 AGENT WORKFLOW - LOCAL STORAGE + 72% SAVINGS 🚀    ║
║                                                            ║
║     • Agent-based architecture (5 agents, 19 subagents)   ║
║     • HuggingFace integration (FREE image + text gen)     ║
║     • All media saved locally (no Google Drive)           ║
║     • WordPress uploads media during publishing           ║
║     • Cost: $0.12/video (vs $0.43 old = 72% savings!)     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

    # Initialize agent system
    logger.info("🎭 Initializing agent system...")
    orchestrator = await initialize_agent_system(
        config_path='/home/claude-workflow/config/api_keys.json',
        preload_models=False
    )

    logger.info("✅ Agent system initialized!\n")

    # Determine workflow type
    workflow_type_map = {
        'standard': WorkflowType.STANDARD_VIDEO,
        'wow': WorkflowType.WOW_VIDEO
    }

    wf_type = workflow_type_map.get(workflow_type, WorkflowType.STANDARD_VIDEO)

    # Execute workflow
    result = await orchestrator.execute_workflow(wf_type)

    if result['success']:
        print("""
╔════════════════════════════════════════════════════════════╗
║     ✅ WORKFLOW COMPLETED SUCCESSFULLY!                   ║
╚════════════════════════════════════════════════════════════╝
""")
        print(f"\nWorkflow ID: {result['workflow_id']}")
        print(f"Duration: {result['duration']:.2f} seconds")
        print(f"Phases: {result['summary']['completed']}/{result['summary']['total_phases']}")

        print("\n🧹 Note: Complete cleanup runs every Sunday at 07:00 via cron")
        print("   To run cleanup manually: python3 cleanup_all_storage.py")

        return True
    else:
        print("""
╔════════════════════════════════════════════════════════════╗
║     ❌ WORKFLOW FAILED - CHECK LOGS                       ║
╚════════════════════════════════════════════════════════════╝
""")
        print(f"\nError: {result.get('error', 'Unknown error')}")
        return False


async def main():
    """Main entry point"""
    try:
        # Parse arguments
        args = parse_arguments()

        # Determine which workflow system to use
        use_legacy = args.legacy
        use_agent = args.agent_system or not args.legacy  # Default to agent system

        if use_legacy:
            logger.info("Using LEGACY workflow system")
            success = await run_legacy_workflow()
        else:
            logger.info(f"Using NEW AGENT workflow system (type: {args.type})")
            success = await run_agent_workflow(workflow_type=args.type)

        return 0 if success else 1

    except KeyboardInterrupt:
        logger.info("\n⚠️ Workflow interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        logger.exception(e)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)