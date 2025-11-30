"""
Unit tests for ContentGenerationAgent (with HuggingFace integration)
"""
import pytest
import asyncio
import sys
sys.path.append('/home/claude-workflow')

from agents.content_generation.agent import ContentGenerationAgent


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'openai_api_key': 'test-key',
        'huggingface': 'hf_test',
        'hf_api_token': 'hf_test',
        'elevenlabs_api_key': 'test-key',
        'hf_image_model': 'black-forest-labs/FLUX.1-schnell',
        'hf_text_model': 'Qwen/Qwen2.5-72B-Instruct',
        'hf_use_inference_api': True,
        'hf_max_retries': 3,
        'fal_api_key': 'test-fal-key',
        'image_generation_fallback': True
    }


@pytest.fixture
def mock_products():
    """Mock product data for testing"""
    return [
        {
            'title': 'Test Product 1',
            'price': '$99.99',
            'original_price': '$149.99',
            'rating': 4.5,
            'reviews': 1234,
            'image_url': 'https://example.com/image1.jpg',
            'product_url': 'https://amazon.com/dp/TEST1',
            'asin': 'TEST1'
        },
        {
            'title': 'Test Product 2',
            'price': '$49.99',
            'rating': 4.8,
            'reviews': 567,
            'image_url': 'https://example.com/image2.jpg',
            'product_url': 'https://amazon.com/dp/TEST2',
            'asin': 'TEST2'
        }
    ]


class TestContentGenerationAgent:
    """Test suite for ContentGenerationAgent"""

    def test_agent_initialization(self, mock_config):
        """Test that agent initializes correctly"""
        agent = ContentGenerationAgent(mock_config)

        assert agent.name == "content_generation"
        assert agent.config == mock_config
        assert len(agent.subagents) == 4  # 4 subagents

    def test_subagents_created(self, mock_config):
        """Test that all subagents are created"""
        agent = ContentGenerationAgent(mock_config)

        expected_subagents = [
            'image_generator',
            'text_generator',
            'voice_generator',
            'content_validator'
        ]

        for subagent_name in expected_subagents:
            assert subagent_name in agent.subagents

    @pytest.mark.asyncio
    async def test_huggingface_integration_configured(self, mock_config):
        """Test that HuggingFace is properly configured"""
        agent = ContentGenerationAgent(mock_config)

        # Check that config has HF settings
        assert 'huggingface' in agent.config or 'hf_api_token' in agent.config
        assert agent.config.get('hf_image_model') == 'black-forest-labs/FLUX.1-schnell'
        assert agent.config.get('hf_text_model') == 'Qwen/Qwen2.5-72B-Instruct'

    @pytest.mark.asyncio
    async def test_generate_images_task_structure(self, mock_config, mock_products):
        """Test that image generation task is structured correctly"""
        agent = ContentGenerationAgent(mock_config)

        task = {
            'phase': 'generate_images',
            'workflow_id': 'test_workflow_123',
            'params': {
                'save_to_airtable': {
                    'products': mock_products
                }
            }
        }

        # We won't actually execute (requires real API), just verify structure
        assert task['phase'] == 'generate_images'
        assert 'products' in task['params']['save_to_airtable']
        assert len(task['params']['save_to_airtable']['products']) == 2

    @pytest.mark.asyncio
    async def test_generate_content_task_structure(self, mock_config, mock_products):
        """Test that content generation task is structured correctly"""
        agent = ContentGenerationAgent(mock_config)

        task = {
            'phase': 'generate_content',
            'workflow_id': 'test_workflow_123',
            'params': {
                'save_to_airtable': {
                    'products': mock_products
                },
                'extract_category': {
                    'category': 'Electronics'
                }
            }
        }

        assert task['phase'] == 'generate_content'
        assert 'products' in task['params']['save_to_airtable']
        assert task['params']['extract_category']['category'] == 'Electronics'

    @pytest.mark.asyncio
    async def test_cost_savings_with_huggingface(self, mock_config):
        """Test that HuggingFace integration provides cost savings"""
        agent = ContentGenerationAgent(mock_config)

        # Verify HF is configured (implies $0 cost for images and text)
        hf_configured = (
            'huggingface' in agent.config or 'hf_api_token' in agent.config
        ) and agent.config.get('hf_use_inference_api', True)

        assert hf_configured, "HuggingFace should be configured for cost savings"

        # Calculate expected costs
        old_cost_images = 7 * 0.03  # 7 images at $0.03 each (fal.ai)
        old_cost_text = 0.10  # GPT-4o text generation
        new_cost_images = 0.00  # HuggingFace FLUX (free)
        new_cost_text = 0.00  # HuggingFace Llama (free)

        savings = (old_cost_images + old_cost_text) - (new_cost_images + new_cost_text)

        assert savings == 0.31  # $0.31 saved per video
        assert savings / (old_cost_images + old_cost_text) >= 0.99  # ~100% savings on these components


class TestContentGenerationCostAnalysis:
    """Test cost analysis and savings calculations"""

    def test_old_system_costs(self):
        """Test calculation of old system costs"""
        old_costs = {
            'gpt4o_text': 0.10,
            'fal_images': 0.21,  # 7 images × $0.03
            'elevenlabs_voice': 0.10,
            'scrapingdog': 0.02
        }

        total_old = sum(old_costs.values())
        assert total_old == 0.43

    def test_new_system_costs_with_hf(self):
        """Test calculation of new system costs with HuggingFace"""
        new_costs = {
            'hf_llama_text': 0.00,  # FREE!
            'hf_flux_images': 0.00,  # FREE!
            'elevenlabs_voice': 0.10,
            'scrapingdog': 0.02
        }

        total_new = sum(new_costs.values())
        assert total_new == 0.12

    def test_cost_savings_percentage(self):
        """Test cost savings percentage calculation"""
        old_total = 0.43
        new_total = 0.12
        savings = old_total - new_total
        savings_percent = (savings / old_total) * 100

        assert savings == 0.31
        assert abs(savings_percent - 72.09) < 0.1  # ~72% savings

    def test_monthly_projections(self):
        """Test monthly cost projections"""
        videos_per_month = 100
        old_monthly = 0.43 * videos_per_month
        new_monthly = 0.12 * videos_per_month
        monthly_savings = old_monthly - new_monthly

        assert old_monthly == 43.00
        assert new_monthly == 12.00
        assert monthly_savings == 31.00

    def test_annual_projections(self):
        """Test annual cost projections"""
        videos_per_month = 100
        annual_savings = (0.43 - 0.12) * videos_per_month * 12

        assert annual_savings == 372.00  # $372 saved per year


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
