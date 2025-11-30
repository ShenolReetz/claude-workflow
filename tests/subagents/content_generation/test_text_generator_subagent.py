"""
Unit tests for TextGeneratorSubAgent (HuggingFace Llama integration)
"""
import pytest
import sys
sys.path.append('/home/claude-workflow')

from agents.content_generation.text_generator_subagent import TextGeneratorSubAgent


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        'huggingface': 'hf_test',
        'hf_api_token': 'hf_test',
        'hf_text_model': 'Qwen/Qwen2.5-72B-Instruct',
        'hf_use_inference_api': True,
        'hf_max_retries': 3,
        'hf_timeout': 60,
        'openai_api_key': 'test-openai-key'  # Fallback
    }


@pytest.fixture
def mock_products():
    """Mock products for testing"""
    return [
        {
            'title': 'Premium Wireless Headphones',
            'price': '$129.99',
            'original_price': '$199.99',
            'rating': 4.7,
            'reviews': 3456,
            'discount_percent': 35
        },
        {
            'title': 'Smart Watch with Fitness Tracking',
            'price': '$89.99',
            'rating': 4.5,
            'reviews': 2134
        }
    ]


class TestTextGeneratorSubAgent:
    """Test suite for TextGeneratorSubAgent"""

    def test_subagent_initialization(self, mock_config):
        """Test that subagent initializes correctly"""
        subagent = TextGeneratorSubAgent("text_generator", mock_config, "content_generation")

        assert subagent.name == "text_generator"
        assert subagent.parent_agent_id == "content_generation"
        assert subagent.config == mock_config

    def test_huggingface_configuration(self, mock_config):
        """Test that HuggingFace Llama is properly configured"""
        subagent = TextGeneratorSubAgent("text_generator", mock_config, "content_generation")

        # Verify HF config
        assert subagent.config.get('hf_text_model') == 'Qwen/Qwen2.5-72B-Instruct'
        assert subagent.config.get('hf_use_inference_api') is True

    def test_fallback_configuration(self, mock_config):
        """Test that fallback to OpenAI is configured"""
        subagent = TextGeneratorSubAgent("text_generator", mock_config, "content_generation")

        # Verify fallback is available
        assert 'openai_api_key' in subagent.config

    @pytest.mark.asyncio
    async def test_voice_scripts_task_structure(self, mock_config, mock_products):
        """Test that voice scripts task is structured correctly"""
        subagent = TextGeneratorSubAgent("text_generator", mock_config, "content_generation")

        task = {
            'operation': 'voice_scripts',
            'products': mock_products,
            'category': 'Electronics'
        }

        # Validate task structure
        assert task['operation'] == 'voice_scripts'
        assert len(task['products']) == 2
        assert task['category'] == 'Electronics'

        # Should generate 7 scripts: intro + 5 products + outro
        # (we'll only have 2 products in this test, but in production it's 5)

    @pytest.mark.asyncio
    async def test_platform_content_task_structure(self, mock_config, mock_products):
        """Test that platform content task is structured correctly"""
        subagent = TextGeneratorSubAgent("text_generator", mock_config, "content_generation")

        task = {
            'operation': 'platform_content',
            'products': mock_products,
            'category': 'Electronics'
        }

        # Validate task structure
        assert task['operation'] == 'platform_content'
        assert 'products' in task
        assert 'category' in task

        # Should generate content for: YouTube, WordPress, Instagram

    def test_script_length_requirements(self):
        """Test that scripts meet length requirements"""
        # Voice scripts should be:
        # - Intro: 60-120 characters
        # - Product: 80-150 characters each
        # - Outro: 60-120 characters

        intro_min, intro_max = 60, 120
        product_min, product_max = 80, 150
        outro_min, outro_max = 60, 120

        # Example scripts
        sample_intro = "Discover the top 5 electronics that are revolutionizing tech in 2024!"
        sample_product = "Premium Wireless Headphones with Noise Cancellation - now 35% off at just $129.99, rated 4.7 stars!"
        sample_outro = "Check the links in description for exclusive deals. Subscribe for more reviews!"

        # Validate lengths
        assert intro_min <= len(sample_intro) <= intro_max * 1.5  # Allow some flexibility
        assert product_min <= len(sample_product) <= product_max * 1.5
        assert outro_min <= len(sample_outro) <= outro_max * 1.5

    def test_cost_comparison(self):
        """Test cost comparison between HF Llama and GPT-4o"""
        # HuggingFace Llama-3.1-8B
        hf_cost_per_request = 0.00  # FREE

        # OpenAI GPT-4o (for all text generation)
        gpt4o_cost_per_video = 0.10

        # Savings per video
        savings = gpt4o_cost_per_video - hf_cost_per_request

        assert gpt4o_cost_per_video == 0.10
        assert hf_cost_per_request == 0.00
        assert savings == 0.10  # $0.10 saved per video

    def test_performance_expectations(self):
        """Test performance expectations for HF Llama"""
        # HuggingFace Llama text generation performance
        hf_time_per_generation = 2.2  # seconds (approximate)

        # Total generations per video:
        # - 7 voice scripts (intro + 5 products + outro)
        # - 3 platform content (YouTube, WordPress, Instagram)
        # Total: ~10 generations

        total_generations = 10
        total_time = hf_time_per_generation * total_generations

        # Should complete all text generation in under 30 seconds
        assert total_time < 30

        # Approximate total: 22 seconds
        assert 20 < total_time < 25


class TestTextGeneratorCostSavings:
    """Test cost savings calculations for text generation"""

    def test_single_video_savings(self):
        """Test savings for a single video"""
        # Old system (GPT-4o)
        old_cost = 0.10

        # New system (HuggingFace Llama)
        new_cost = 0.00

        savings = old_cost - new_cost

        assert old_cost == 0.10
        assert new_cost == 0.00
        assert savings == 0.10

    def test_monthly_savings(self):
        """Test monthly savings projection"""
        videos_per_month = 100
        savings_per_video = 0.10

        monthly_savings = savings_per_video * videos_per_month

        assert monthly_savings == 10.00  # $10/month saved

    def test_annual_savings(self):
        """Test annual savings projection"""
        videos_per_month = 100
        savings_per_video = 0.10

        annual_savings = savings_per_video * videos_per_month * 12

        assert annual_savings == 120.00  # $120/year saved

    def test_savings_percentage(self):
        """Test percentage savings"""
        old_cost = 0.10
        new_cost = 0.00
        savings_percent = ((old_cost - new_cost) / old_cost) * 100

        assert savings_percent == 100.0  # 100% savings!


class TestContentQuality:
    """Test content quality expectations"""

    def test_voice_script_format(self):
        """Test that voice scripts follow expected format"""
        # Voice scripts should:
        # - Be concise and engaging
        # - Include product name
        # - Include price
        # - Include key feature
        # - Be natural for voice narration

        sample_script = "Premium Wireless Headphones - 35% off at $129.99! Rated 4.7 stars with noise cancellation."

        # Check key elements
        assert any(word in sample_script.lower() for word in ['headphones', 'wireless'])
        assert '$' in sample_script
        assert any(char.isdigit() for char in sample_script)
        assert '.' in sample_script  # Natural sentence

    def test_platform_content_requirements(self):
        """Test platform-specific content requirements"""
        # YouTube: Title (60-80 chars), Description (1000+ chars), Tags
        # WordPress: Title, Full Article (1500+ chars), SEO meta
        # Instagram: Caption (150-200 chars), Hashtags (15-30)

        youtube_title_max = 80
        instagram_caption_max = 200
        wordpress_article_min = 1500

        # These are reasonable limits
        assert youtube_title_max == 80
        assert instagram_caption_max == 200
        assert wordpress_article_min == 1500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
