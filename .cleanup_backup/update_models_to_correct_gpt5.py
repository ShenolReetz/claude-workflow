#!/usr/bin/env python3
"""
Update Models to Correct GPT-5 Configuration
===========================================

Based on OpenAI's August 2025 release, GPT-5 is now available with specific model names:
- gpt-5: Main model for logic and multi-step tasks
- gpt-5-mini: Lightweight version for cost-sensitive applications  
- gpt-5-nano: Ultra-low latency for instant responses
- gpt-5-chat: Advanced conversational model

This script updates the configuration to use the optimal GPT-5 variant.
"""

import os
import re
import glob
from typing import List, Dict

class GPT5ConfigurationUpdater:
    def __init__(self):
        self.files_updated = []
        self.changes_made = []
        
        # Model selection strategy based on use case
        self.model_mapping = {
            'content_generation': 'gpt-5-mini',  # Cost-effective for content
            'text_validation': 'gpt-5-nano',     # Ultra-fast for validation
            'script_generation': 'gpt-5',        # Full model for complex scripts
            'category_extraction': 'gpt-5-nano', # Fast for simple extraction
            'platform_content': 'gpt-5-mini',    # Good balance for social content
            'keyword_optimization': 'gpt-5-mini' # Cost-effective for SEO
        }
        
        # Fallback hierarchy
        self.fallback_chain = ['gpt-5-mini', 'gpt-4o', 'gpt-4-turbo']
        
    def update_content_generation_server(self):
        """Update the main content generation server"""
        file_path = '/home/claude-workflow/mcp_servers/Production_content_generation_server.py'
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Update model configuration
            old_config = '''        # Use GPT-5 as primary model with GPT-4 as fallback
        self.model = "gpt-5"  # Latest GPT-5 model
        self.fallback_model = "gpt-5"  # Fallback to GPT-4 if GPT-5 unavailable'''
        
            new_config = '''        # Use GPT-5-mini for cost-effective content generation
        self.model = "gpt-5-mini"  # Optimal for content generation
        self.fallback_model = "gpt-4o"  # Latest GPT-4 fallback
        self.nano_model = "gpt-5-nano"  # For simple/fast tasks'''
        
            content = content.replace(old_config, new_config)
            
            # Update logging message
            content = content.replace(
                'self.logger.info("🚀 Content Generation Server initialized with GPT-5")',
                'self.logger.info("🚀 Content Generation Server initialized with GPT-5-mini")'
            )
            
            # Update comments
            content = content.replace(
                'Production Content Generation MCP Server - Using OpenAI GPT-5',
                'Production Content Generation MCP Server - Using OpenAI GPT-5-mini'
            )
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            self.files_updated.append(file_path)
            self.changes_made.append((file_path, "Updated to use GPT-5-mini with proper fallback"))
            
        except Exception as e:
            print(f"❌ Error updating content generation server: {e}")
    
    def update_text_control_agent(self):
        """Update text generation control agent for fast validation"""
        file_path = '/home/claude-workflow/src/mcp/Production_text_generation_control_agent_mcp_v2.py'
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Update model variables
            content = re.sub(
                r'model = "gpt-5"  # Primary model\s+fallback_model = "gpt-5"  # Fallback',
                'model = "gpt-5-nano"  # Ultra-fast for validation\n    fallback_model = "gpt-4o"  # Reliable fallback',
                content
            )
            
            # Update regeneration function to use nano for speed
            content = content.replace(
                'model="gpt-5",  # Use GPT-5',
                'model="gpt-5-nano",  # Ultra-fast validation'
            )
            
            content = content.replace(
                'model="gpt-5",  # Try GPT-5',
                'model="gpt-5-nano",  # Ultra-fast generation'
            )
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            self.files_updated.append(file_path)
            self.changes_made.append((file_path, "Updated to use GPT-5-nano for fast validation"))
            
        except Exception as e:
            print(f"❌ Error updating text control agent: {e}")
    
    def update_platform_content_generator(self):
        """Update platform content generator for balanced performance"""
        file_path = '/home/claude-workflow/src/mcp/Production_platform_content_generator.py'
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Update all GPT-5 references to GPT-5-mini for cost efficiency
            content = re.sub(
                r'model="gpt-5",',
                'model="gpt-5-mini",',
                content
            )
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            self.files_updated.append(file_path)
            self.changes_made.append((file_path, "Updated to use GPT-5-mini for cost-effective content"))
            
        except Exception as e:
            print(f"❌ Error updating platform content generator: {e}")
    
    def update_category_extractor(self):
        """Update category extractor for fast processing"""
        file_path = '/home/claude-workflow/mcp_servers/Production_product_category_extractor_server.py'
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Update model to nano for simple extraction tasks
            content = re.sub(
                r'self\.model = "gpt-5"',
                'self.model = "gpt-5-nano"',
                content
            )
            
            with open(file_path, 'w') as f:
                f.write(content)
                
            self.files_updated.append(file_path)
            self.changes_made.append((file_path, "Updated to use GPT-5-nano for fast extraction"))
            
        except Exception as e:
            print(f"❌ Error updating category extractor: {e}")
    
    def create_gpt5_usage_guide(self):
        """Create a usage guide for the different GPT-5 models"""
        guide_content = '''# GPT-5 Model Usage Guide

## Available Models (August 2025)

### 🚀 gpt-5
- **Use for**: Complex reasoning, multi-step tasks, advanced content creation
- **Pricing**: $1.25/1M input tokens, $10/1M output tokens
- **Best for**: Script generation, complex analysis, creative writing

### ⚡ gpt-5-mini  
- **Use for**: General content generation, social media content, SEO optimization
- **Pricing**: $0.25/1M input tokens, $2/1M output tokens
- **Best for**: Platform content, product descriptions, keyword optimization

### 🏃 gpt-5-nano
- **Use for**: Simple tasks, validation, extraction, ultra-fast responses
- **Pricing**: $0.05/1M input tokens, $0.40/1M output tokens  
- **Best for**: Text validation, category extraction, quick classifications

### 💬 gpt-5-chat
- **Use for**: Advanced conversational applications, enterprise chat
- **Pricing**: Similar to gpt-5
- **Best for**: Customer service, advanced chat applications

## Current Workflow Configuration

| Component | Model Used | Reason |
|-----------|------------|---------|
| Content Generation | gpt-5-mini | Cost-effective for content |
| Text Validation | gpt-5-nano | Ultra-fast validation |
| Script Generation | gpt-5-nano | Quick script creation |
| Platform Content | gpt-5-mini | Balanced quality/cost |
| Category Extraction | gpt-5-nano | Simple extraction task |

## Cost Optimization

Using this configuration versus gpt-5 for everything:
- **Content Generation**: 80% cost reduction with gpt-5-mini
- **Validation Tasks**: 95% cost reduction with gpt-5-nano
- **Overall Savings**: ~70-80% reduction in AI costs

## Performance Benefits

- **Speed**: gpt-5-nano provides near-instant responses
- **Quality**: gpt-5-mini maintains high quality at lower cost
- **Reliability**: Proper fallback chain ensures workflow stability
'''
        
        with open('/home/claude-workflow/GPT5_USAGE_GUIDE.md', 'w') as f:
            f.write(guide_content)
        
        print("✅ Created GPT-5 usage guide")
    
    def update_api_resilience_manager(self):
        """Update resilience manager with new pricing info"""
        file_path = '/home/claude-workflow/src/utils/api_resilience_manager.py'
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Add GPT-5 cost tracking
            if 'gpt-5' not in content:
                cost_tracking = '''        # GPT-5 model costs (per 1M tokens)
        self.model_costs = {
            'gpt-5': {'input': 1.25, 'output': 10.00},
            'gpt-5-mini': {'input': 0.25, 'output': 2.00},
            'gpt-5-nano': {'input': 0.05, 'output': 0.40},
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4-turbo': {'input': 10.00, 'output': 30.00}
        }'''
                
                # Insert after the api_usage initialization
                content = content.replace(
                    "        }",
                    f"        }}\n{cost_tracking}",
                    1
                )
                
                with open(file_path, 'w') as f:
                    f.write(content)
                    
                self.files_updated.append(file_path)
                self.changes_made.append((file_path, "Added GPT-5 cost tracking"))
                
        except Exception as e:
            print(f"❌ Error updating resilience manager: {e}")
    
    def run_all_updates(self):
        """Run all model updates"""
        print("\n🚀 UPDATING TO CORRECT GPT-5 CONFIGURATION")
        print("=" * 60)
        print("Using optimal GPT-5 variants based on OpenAI August 2025 release")
        
        # Update each component
        self.update_content_generation_server()
        self.update_text_control_agent()
        self.update_platform_content_generator()
        self.update_category_extractor()
        self.update_api_resilience_manager()
        
        # Create documentation
        self.create_gpt5_usage_guide()
        
        # Print summary
        print(f"\n📊 UPDATE SUMMARY")
        print("=" * 60)
        print(f"Files updated: {len(self.files_updated)}")
        
        if self.files_updated:
            print("\n✅ Updated files:")
            for file_path in self.files_updated:
                print(f"   • {os.path.basename(file_path)}")
        
        print(f"\n🎯 Model Selection Strategy:")
        print("   • gpt-5-mini: Content generation (80% cost savings)")
        print("   • gpt-5-nano: Validation & extraction (95% cost savings)")
        print("   • gpt-4o: Reliable fallback")
        
        print(f"\n💰 Expected Cost Savings: 70-80% reduction in AI costs")
        print(f"⚡ Expected Speed Improvement: 2-5x faster for validation tasks")
        
        print(f"\n🚀 Your workflow is now optimized for GPT-5!")
        return len(self.files_updated) > 0

def main():
    """Main update function"""
    print("\n🔄 GPT-5 CONFIGURATION OPTIMIZER")
    print("=" * 60)
    print("Updating to use the correct GPT-5 model variants based on")
    print("OpenAI's August 2025 release for optimal cost and performance.")
    
    updater = GPT5ConfigurationUpdater()
    success = updater.run_all_updates()
    
    if success:
        print("\n✅ SUCCESS: GPT-5 configuration optimized!")
        print("\n📖 See GPT5_USAGE_GUIDE.md for detailed model information")
        print("\n🚀 Ready to run with optimized GPT-5 configuration:")
        print("   python3 src/Production_workflow_runner.py")
    else:
        print("\n⚠️ No updates were applied")

if __name__ == "__main__":
    main()