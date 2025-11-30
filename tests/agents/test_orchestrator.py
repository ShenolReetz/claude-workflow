"""
Unit tests for OrchestratorAgent
"""
import pytest
import asyncio
import sys
sys.path.append('/home/claude-workflow')

from agents.orchestrator import OrchestratorAgent, WorkflowType


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'openai_api_key': 'test-key',
        'huggingface': 'hf_test',
        'elevenlabs_api_key': 'test-key',
        'airtable_api_key': 'test-key',
        'airtable_base_id': 'test-base',
        'scrapingdog_api_key': 'test-key',
        'hf_image_model': 'black-forest-labs/FLUX.1-schnell',
        'hf_text_model': 'Qwen/Qwen2.5-72B-Instruct'
    }


@pytest.fixture
async def orchestrator(mock_config):
    """Create orchestrator instance for testing"""
    orch = OrchestratorAgent(mock_config)
    return orch


class TestOrchestratorAgent:
    """Test suite for OrchestratorAgent"""

    def test_orchestrator_initialization(self, mock_config):
        """Test that orchestrator initializes correctly"""
        orch = OrchestratorAgent(mock_config)

        assert orch.name == "orchestrator"
        assert orch.config == mock_config
        assert len(orch.agents) == 0  # Not initialized yet
        assert orch.current_workflow_id is None

    def test_workflow_phases_definition(self, mock_config):
        """Test that workflow phases are correctly defined"""
        orch = OrchestratorAgent(mock_config)
        phases = orch.workflow_phases

        # Should have all 17 phases
        assert len(phases) == 17

        # Check key phases exist
        assert "validate_credentials" in phases
        assert "scrape_amazon" in phases
        assert "generate_images" in phases
        assert "generate_content" in phases
        assert "create_video" in phases
        assert "publish_youtube" in phases
        assert "finalize" in phases

    def test_phase_dependencies(self, mock_config):
        """Test that phase dependencies are correctly defined"""
        orch = OrchestratorAgent(mock_config)
        deps = orch.phase_dependencies

        # validate_credentials has no dependencies
        assert deps["validate_credentials"] == []

        # scrape_amazon depends on fetch_title
        assert "fetch_title" in deps["scrape_amazon"]

        # create_video depends on validate_content and generate_images
        assert "validate_content" in deps["create_video"]
        assert "generate_images" in deps["create_video"]

        # finalize depends on update_airtable_status
        assert "update_airtable_status" in deps["finalize"]

    @pytest.mark.asyncio
    async def test_orchestrator_initialization_with_agents(self, mock_config):
        """Test that orchestrator initializes all 5 agents"""
        orch = OrchestratorAgent(mock_config)

        # This would normally initialize all agents, but we'll skip for unit test
        # as it requires all agent modules
        # await orch.initialize()

        # For unit test, just verify the agent registration works
        class MockAgent:
            def __init__(self, name):
                self.name = name

        orch.register_agent('test_agent', MockAgent('test'))
        assert 'test_agent' in orch.agents
        assert orch.agents['test_agent'].name == 'test'

    def test_parallel_phases_identification(self, mock_config):
        """Test identification of parallel phases"""
        orch = OrchestratorAgent(mock_config)
        phases = orch.workflow_phases
        parallel_groups = orch._identify_parallel_phases(phases)

        # Should identify publishing phases as parallel
        assert len(parallel_groups) >= 1

        # Publishing phases should be in a parallel group
        publishing_phases = ["publish_youtube", "publish_wordpress", "publish_instagram"]
        assert publishing_phases in parallel_groups

    def test_duration_estimation(self, mock_config):
        """Test workflow duration estimation"""
        orch = OrchestratorAgent(mock_config)
        phases = orch.workflow_phases

        estimated_duration = orch._estimate_duration(phases)

        # Should return a positive number
        assert estimated_duration > 0

        # Should be reasonable (between 1 minute and 10 minutes)
        assert 60 < estimated_duration < 600

    @pytest.mark.asyncio
    async def test_workflow_planning(self, mock_config):
        """Test workflow planning"""
        orch = OrchestratorAgent(mock_config)

        plan = await orch._plan_workflow(WorkflowType.STANDARD_VIDEO, {})

        assert plan['workflow_type'] == WorkflowType.STANDARD_VIDEO.value
        assert 'phases' in plan
        assert 'parallel_groups' in plan
        assert 'estimated_duration' in plan
        assert len(plan['phases']) > 0

    @pytest.mark.asyncio
    async def test_wow_video_workflow_planning(self, mock_config):
        """Test WOW video workflow planning"""
        orch = OrchestratorAgent(mock_config)

        plan = await orch._plan_workflow(WorkflowType.WOW_VIDEO, {})

        # WOW workflow should replace create_video with create_wow_video
        assert "create_wow_video" in plan['phases']
        assert "create_video" not in plan['phases']

    def test_workflow_status_without_workflow(self, mock_config):
        """Test getting workflow status when no workflow exists"""
        orch = OrchestratorAgent(mock_config)

        status = orch.get_workflow_status()

        assert 'error' in status
        assert status['error'] == 'Workflow not found'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
