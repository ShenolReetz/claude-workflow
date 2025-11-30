"""
Agent Workflow Runner
====================
Main entry point for executing video creation workflows using the agent system.

Usage:
    python run_agent_workflow.py --type standard    # Standard video
    python run_agent_workflow.py --type wow         # WOW video with effects
    python run_agent_workflow.py --test             # Test mode (dry run)

Features:
    - Full agent-based architecture
    - HuggingFace integration (72% cost savings)
    - Parallel publishing to YouTube, WordPress, Instagram
    - Comprehensive error recovery
    - Real-time progress monitoring
"""

import asyncio
import argparse
import sys
import os
import logging
from datetime import datetime

# Add project root to path
sys.path.append('/home/claude-workflow')

from agents.agent_initializer import initialize_agent_system
from agents.orchestrator import WorkflowType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'/home/claude-workflow/logs/agent_workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Run video creation workflow using agent system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agent_workflow.py --type standard
  python run_agent_workflow.py --type wow --preload
  python run_agent_workflow.py --test

Workflow Types:
  standard  - Standard product review video (60 seconds)
  wow       - WOW video with special effects (60-75 seconds, +40%% engagement)
  test      - Test mode (validates system without running full workflow)

Cost Savings:
  Old System: $0.43 per video (GPT-4o + fal.ai)
  New System: $0.12 per video (HuggingFace + optimized stack)
  Savings: $0.31 per video (72%% reduction!)
        """
    )

    parser.add_argument(
        '--type',
        choices=['standard', 'wow', 'test'],
        default='standard',
        help='Type of workflow to execute (default: standard)'
    )

    parser.add_argument(
        '--preload',
        action='store_true',
        help='Preload HuggingFace models for faster execution'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - validate system without full execution'
    )

    parser.add_argument(
        '--config',
        default='/home/claude-workflow/config/api_keys.json',
        help='Path to configuration file'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


async def run_test_workflow(orchestrator):
    """Run a test workflow to validate the system"""
    logger.info("\n" + "=" * 70)
    logger.info("RUNNING TEST WORKFLOW")
    logger.info("=" * 70 + "\n")

    try:
        # Verify all agents are initialized
        logger.info("✓ Verifying agent initialization...")
        expected_agents = ['data_acquisition', 'content_generation', 'video_production', 'publishing', 'monitoring']

        for agent_name in expected_agents:
            if agent_name in orchestrator.agents:
                logger.info(f"  ✓ {agent_name}: initialized")
            else:
                logger.error(f"  ✗ {agent_name}: NOT FOUND")
                return False

        # Verify HuggingFace configuration
        logger.info("\n✓ Verifying HuggingFace integration...")
        config = orchestrator.config

        if 'huggingface' in config or 'hf_api_token' in config:
            logger.info(f"  ✓ HF Token: configured")
            logger.info(f"  ✓ Image Model: {config.get('hf_image_model', 'Not set')}")
            logger.info(f"  ✓ Text Model: {config.get('hf_text_model', 'Not set')}")
        else:
            logger.error("  ✗ HuggingFace token not configured")
            return False

        # Test workflow planning
        logger.info("\n✓ Testing workflow planning...")
        plan = await orchestrator._plan_workflow(WorkflowType.STANDARD_VIDEO, {})
        logger.info(f"  ✓ Workflow plan created: {len(plan['phases'])} phases")
        logger.info(f"  ✓ Estimated duration: {plan['estimated_duration']:.0f} seconds")

        logger.info("\n" + "=" * 70)
        logger.info("✅ TEST WORKFLOW PASSED - System is ready!")
        logger.info("=" * 70 + "\n")

        return True

    except Exception as e:
        logger.error(f"\n❌ TEST WORKFLOW FAILED: {e}")
        logger.exception(e)
        return False


async def run_production_workflow(orchestrator, workflow_type: WorkflowType):
    """Run a full production workflow"""
    logger.info("\n" + "=" * 70)
    logger.info(f"STARTING PRODUCTION WORKFLOW: {workflow_type.value.upper()}")
    logger.info("=" * 70 + "\n")

    try:
        # Execute workflow
        result = await orchestrator.execute_workflow(workflow_type)

        if result['success']:
            logger.info("\n" + "=" * 70)
            logger.info("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            logger.info(f"\nWorkflow ID: {result['workflow_id']}")
            logger.info(f"Duration: {result['duration']:.2f} seconds")
            logger.info(f"Phases Completed: {result['summary']['completed']}/{result['summary']['total_phases']}")

            # Display cost summary
            if 'costs' in result.get('results', {}).get('finalize', {}):
                costs = result['results']['finalize']['costs']
                logger.info(f"\n💰 COST ANALYSIS:")
                logger.info(f"  Total Cost: ${costs['total']:.2f}")
                logger.info(f"  Cost Savings: ${costs['savings_vs_old_system']:.2f} (vs old system)")
                logger.info(f"  Savings Percentage: {costs['savings_percent']}%")

            logger.info("=" * 70 + "\n")

            return True
        else:
            logger.error(f"\n❌ WORKFLOW FAILED: {result.get('error', 'Unknown error')}")
            logger.error(f"Duration: {result.get('duration', 0):.2f} seconds")
            return False

    except Exception as e:
        logger.error(f"\n❌ WORKFLOW EXECUTION FAILED: {e}")
        logger.exception(e)
        return False


async def main():
    """Main execution function"""
    # Parse arguments
    args = parse_arguments()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Display startup banner
    print("""
╔══════════════════════════════════════════════════════════╗
║         AGENT-BASED VIDEO WORKFLOW SYSTEM                ║
║         HuggingFace Integration - 72%% Cost Savings      ║
╚══════════════════════════════════════════════════════════╝
    """)

    try:
        # Initialize agent system
        logger.info("🚀 Initializing agent system...")
        orchestrator = await initialize_agent_system(
            config_path=args.config,
            preload_models=args.preload
        )

        logger.info("✅ Agent system initialized successfully!\n")

        # Determine workflow type
        if args.test:
            # Run test workflow
            success = await run_test_workflow(orchestrator)
        else:
            # Run production workflow
            workflow_type_map = {
                'standard': WorkflowType.STANDARD_VIDEO,
                'wow': WorkflowType.WOW_VIDEO,
                'test': WorkflowType.TEST
            }

            workflow_type = workflow_type_map.get(args.type, WorkflowType.STANDARD_VIDEO)
            success = await run_production_workflow(orchestrator, workflow_type)

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Workflow interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"\n❌ FATAL ERROR: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs('/home/claude-workflow/logs', exist_ok=True)

    # Run main function
    asyncio.run(main())
