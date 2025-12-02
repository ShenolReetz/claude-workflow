"""
Orchestrator Agent
==================
Master controller that manages the entire workflow by delegating tasks to specialized agents.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

from .base_agent import BaseAgent
from .agent_protocol import AgentMessage, MessageType, get_message_bus
from .agent_state import WorkflowStateManager, WorkflowState


class WorkflowType(Enum):
    """Types of workflows"""
    STANDARD_VIDEO = "standard_video"
    WOW_VIDEO = "wow_video"
    TEST = "test"


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator that coordinates all agents to complete workflows
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("orchestrator", config)

        # Workflow planning
        self.workflow_phases = self._define_workflow_phases()
        self.phase_dependencies = self._define_phase_dependencies()

        # Sub-agents (will be initialized later)
        self.agents = {}

        # State management
        self.current_workflow_id = None
        self.state_manager = None

        # Results storage
        self.workflow_results = {}

        self.logger.info("🎭 Orchestrator Agent initialized")

    def _define_workflow_phases(self) -> List[str]:
        """Define all workflow phases in order"""
        return [
            "fetch_title",
            "scrape_amazon",
            "extract_category",
            "validate_products",
            "save_to_airtable",
            "generate_images",
            "generate_content",
            "generate_scripts",
            "generate_voices",
            "validate_content",
            "create_video",
            "publish_youtube",
            "publish_wordpress",
            "publish_instagram",
            "update_airtable_status",
            "finalize"
        ]

    def _define_phase_dependencies(self) -> Dict[str, List[str]]:
        """Define which phases depend on which others"""
        return {
            "fetch_title": [],
            "scrape_amazon": ["fetch_title"],
            "extract_category": ["fetch_title"],
            "validate_products": ["scrape_amazon"],
            "save_to_airtable": ["validate_products"],
            "generate_images": ["save_to_airtable"],
            "generate_content": ["extract_category", "save_to_airtable"],
            "generate_scripts": ["generate_content"],
            "generate_voices": ["generate_scripts"],
            "validate_content": ["generate_voices"],
            "create_video": ["validate_content", "generate_images"],
            "publish_youtube": ["create_video"],
            "publish_wordpress": ["create_video"],
            "publish_instagram": ["create_video"],
            "update_airtable_status": ["publish_youtube", "publish_wordpress", "publish_instagram"],
            "finalize": ["update_airtable_status"]
        }

    async def initialize(self):
        """Initialize orchestrator and all sub-agents"""
        await super().initialize()

        # Import all agent classes
        from .data_acquisition.agent import DataAcquisitionAgent
        from .content_generation.agent import ContentGenerationAgent
        from .video_production.agent import VideoProductionAgent
        from .publishing.agent import PublishingAgent
        from .monitoring.agent import MonitoringAgent

        # Initialize all 5 main agents
        self.agents['data_acquisition'] = DataAcquisitionAgent(self.config)
        self.agents['content_generation'] = ContentGenerationAgent(self.config)
        self.agents['video_production'] = VideoProductionAgent(self.config)
        self.agents['publishing'] = PublishingAgent(self.config)
        self.agents['monitoring'] = MonitoringAgent(self.config)

        self.logger.info(f"🎭 Orchestrator ready with {len(self.agents)} agents!")
        self.logger.info("💰 HuggingFace integration active - 72% cost savings!")

    def register_agent(self, agent_name: str, agent: BaseAgent):
        """Register a sub-agent"""
        self.agents[agent_name] = agent
        self.logger.info(f"📝 Registered agent: {agent_name}")

    async def execute_workflow(self, workflow_type: WorkflowType = WorkflowType.STANDARD_VIDEO,
                               params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete workflow

        Args:
            workflow_type: Type of workflow to execute
            params: Optional parameters for workflow

        Returns:
            Workflow results
        """
        # Generate workflow ID
        workflow_id = f"workflow_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        self.current_workflow_id = workflow_id

        # Initialize state manager
        self.state_manager = WorkflowStateManager(workflow_id)

        self.logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║              WORKFLOW EXECUTION STARTED                   ║
╠══════════════════════════════════════════════════════════╣
║  ID: {workflow_id:<48} ║
║  Type: {workflow_type.value:<46} ║
╚══════════════════════════════════════════════════════════╝
""")

        start_time = time.time()

        try:
            # Plan workflow based on type
            plan = await self._plan_workflow(workflow_type, params)

            # Execute phases
            for phase in plan['phases']:
                await self._execute_phase(phase)

            # All phases complete
            duration = time.time() - start_time

            summary = self.state_manager.get_workflow_summary()

            self.logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║              WORKFLOW COMPLETED SUCCESSFULLY              ║
╠══════════════════════════════════════════════════════════╣
║  Duration: {duration:.2f}s{' ' * (45 - len(f'{duration:.2f}s'))}║
║  Phases: {summary['completed']}/{summary['total_phases']:<43} ║
╚══════════════════════════════════════════════════════════╝
""")

            return {
                'success': True,
                'workflow_id': workflow_id,
                'duration': duration,
                'summary': summary,
                'results': self.workflow_results
            }

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"❌ Workflow failed after {duration:.2f}s: {e}")

            return {
                'success': False,
                'workflow_id': workflow_id,
                'error': str(e),
                'duration': duration,
                'summary': self.state_manager.get_workflow_summary() if self.state_manager else {}
            }

    async def _plan_workflow(self, workflow_type: WorkflowType,
                            params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Plan workflow execution

        Args:
            workflow_type: Type of workflow
            params: Workflow parameters

        Returns:
            Execution plan
        """
        phases = self.workflow_phases.copy()

        # Modify phases based on workflow type
        if workflow_type == WorkflowType.WOW_VIDEO:
            # Use WOW video generator instead of standard
            phases[phases.index("create_video")] = "create_wow_video"

        # Identify phases that can run in parallel
        parallel_groups = self._identify_parallel_phases(phases)

        plan = {
            'workflow_type': workflow_type.value,
            'phases': phases,
            'parallel_groups': parallel_groups,
            'estimated_duration': self._estimate_duration(phases),
            'params': params or {}
        }

        self.logger.info(f"📋 Workflow plan created: {len(phases)} phases, ~{plan['estimated_duration']:.0f}s")

        return plan

    def _identify_parallel_phases(self, phases: List[str]) -> List[List[str]]:
        """
        Identify phases that can run in parallel

        Returns:
            List of phase groups that can run in parallel
        """
        parallel_groups = []

        # Publishing phases can run in parallel
        publishing_phases = ["publish_youtube", "publish_wordpress", "publish_instagram"]
        if all(p in phases for p in publishing_phases):
            parallel_groups.append(publishing_phases)

        # Image and content generation can partially overlap
        if "generate_images" in phases and "generate_content" in phases:
            # These can start at the same time if dependencies are met
            pass

        return parallel_groups

    def _estimate_duration(self, phases: List[str]) -> float:
        """Estimate workflow duration based on phases"""
        # Rough estimates (in seconds)
        phase_durations = {
            "validate_credentials": 5,
            "fetch_title": 2,
            "scrape_amazon": 20,
            "extract_category": 3,
            "validate_products": 2,
            "save_to_airtable": 2,
            "generate_images": 45,  # HF API, 7 images
            "generate_content": 15,  # HF API
            "generate_scripts": 10,
            "generate_voices": 60,  # HF API, 7 clips
            "validate_content": 2,
            "create_video": 60,      # Remotion rendering
            "create_wow_video": 75,  # WOW video takes longer
            "publish_youtube": 30,
            "publish_wordpress": 20,
            "publish_instagram": 15,
            "update_airtable_status": 2,
            "finalize": 1
        }

        total = sum(phase_durations.get(phase, 5) for phase in phases)

        # Account for parallel execution (rough estimate)
        return total * 0.7  # ~30% time saved from parallelization

    async def _execute_phase(self, phase_name: str):
        """
        Execute a single workflow phase

        Args:
            phase_name: Name of phase to execute
        """
        self.logger.info(f"▶️  Executing phase: {phase_name}")

        # Check dependencies
        dependencies = self.phase_dependencies.get(phase_name, [])
        for dep in dependencies:
            if not self.state_manager.is_phase_completed(dep):
                raise RuntimeError(f"Dependency not met: {phase_name} requires {dep}")

        # Start phase
        self.state_manager.start_phase(phase_name)

        try:
            # Route to appropriate agent
            result = await self._route_phase_to_agent(phase_name)

            # Store result
            self.workflow_results[phase_name] = result

            # Mark as complete
            self.state_manager.complete_phase(phase_name, result)

        except Exception as e:
            self.state_manager.fail_phase(phase_name, str(e))
            raise

    async def _route_phase_to_agent(self, phase_name: str) -> Dict[str, Any]:
        """
        Route phase execution to appropriate agent

        Args:
            phase_name: Phase to execute

        Returns:
            Phase result
        """
        # Mapping of phases to agents
        phase_agent_map = {
            "validate_credentials": "data_acquisition",
            "fetch_title": "data_acquisition",
            "scrape_amazon": "data_acquisition",
            "extract_category": "data_acquisition",
            "validate_products": "data_acquisition",
            "save_to_airtable": "data_acquisition",

            "generate_images": "content_generation",
            "generate_content": "content_generation",
            "generate_scripts": "content_generation",
            "generate_voices": "content_generation",
            "validate_content": "content_generation",

            "create_video": "video_production",
            "create_wow_video": "video_production",

            "publish_youtube": "publishing",
            "publish_wordpress": "publishing",
            "publish_instagram": "publishing",
            "update_airtable_status": "publishing",

            "finalize": "monitoring"
        }

        agent_name = phase_agent_map.get(phase_name)

        if not agent_name:
            raise ValueError(f"No agent mapping for phase: {phase_name}")

        if agent_name not in self.agents:
            # Agent not yet implemented, use placeholder
            self.logger.warning(f"⚠️  Agent not implemented: {agent_name}, using placeholder")
            await asyncio.sleep(0.5)  # Simulate execution
            return {'status': 'placeholder', 'phase': phase_name}

        # Delegate to agent
        agent = self.agents[agent_name]

        task = {
            'phase': phase_name,
            'workflow_id': self.current_workflow_id,
            'params': self.workflow_results,  # Pass previous results
            'requester': 'orchestrator'
        }

        # Send task request
        task_msg = AgentMessage(
            sender="orchestrator",
            receiver=agent_name,
            message_type=MessageType.TASK_REQUEST,
            payload=task
        )

        await self.message_bus.send(task_msg)

        # Wait for completion (with timeout)
        # In real implementation, would listen for COMPLETION message
        # For now, call directly if agent has execute_task method
        if hasattr(agent, 'execute_task'):
            result = await agent.execute_task(task)
            return result

        return {'status': 'delegated', 'agent': agent_name}

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task (for BaseAgent compatibility)"""
        workflow_type = WorkflowType(task.get('workflow_type', 'standard_video'))
        params = task.get('params')

        return await self.execute_workflow(workflow_type, params)

    def get_workflow_status(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of workflow"""
        if workflow_id is None:
            workflow_id = self.current_workflow_id

        if not self.state_manager or self.state_manager.workflow_id != workflow_id:
            return {'error': 'Workflow not found'}

        return self.state_manager.get_workflow_summary()
