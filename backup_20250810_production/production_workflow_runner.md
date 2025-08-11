#!/usr/bin/env python3
"""
Production Workflow Runner
==========================

This script drives the full end‑to‑end content creation pipeline using live
APIs.  It mirrors the structure of the original test workflow but replaces
all hardcoded values with real service calls.  The goal is to take a
pending record from Airtable, generate search‑optimised content and media,
assemble a video via JSON2Video and then publish the results.  All
functionality is asynchronous to maximise throughput while waiting on
network bound operations.

Key integrations:

* **OpenAI GPT‑4** for keyword generation, title optimisation and countdown
  script creation via the `OpenAIContentGenerationServer`.
* **ScrapingDog** for reliable Amazon product search and metadata
  extraction via the `ScrapingDogAmazonServer`.
* **Amazon Affiliate** link generation using the existing
  `AmazonAffiliateAgentMCP` so that products can be monetised.
* **OpenAI DALL‑E** for ultra‑realistic product imagery.  Generated
  pictures are saved back to Airtable along with the product names and
  descriptions.
* **ElevenLabs** for voice synthesis.  Each piece of narration (intro,
  outro and per‑product voiceover) is generated in high quality and stored
  as base64 encoded MP3 in Airtable.
* **JSON2Video** for assembling the final vertical video from the
  generated script, images and audio.
* **Google Drive** for storing the final video file and optionally the
  generated images.  A shareable link is returned and saved to Airtable.
* **WordPress** and **YouTube** publishing hooks.  These remain optional
  and are executed only if configured in `api_keys.json`.

Before running this script you must populate `config/api_keys.json` with
valid credentials for Airtable, OpenAI, ScrapingDog, ElevenLabs,
JSON2Video, Google Drive and, if desired, YouTube and WordPress.

The workflow proceeds in discrete steps.  Each step includes logging for
diagnostics.  Failures in non‑critical steps (for example publishing to
YouTube) will be logged but will not abort the entire pipeline.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

# Ensure project root is on the path so that imports work correctly when
# executed from within docker or a different working directory.
sys.path.append('/home/claude-workflow')

# Airtable integration
from mcp_servers.airtable_server import AirtableMCPServer

# Content generation using OpenAI (GPT‑4)
from mcp_servers.openai_content_server import OpenAIContentGenerationServer

# Amazon search via ScrapingDog
from mcp_servers.scrapingdog_amazon_server import ScrapingDogAmazonServer

# ElevenLabs voice synthesis
from mcp_servers.voice_generation_server import VoiceGenerationMCPServer

# Affiliate link generation agent
from src.mcp.amazon_affiliate_agent_mcp import run_amazon_affiliate_generation

# Text generation quality control and regeneration
from src.mcp.text_generation_control_agent_mcp_v2 import run_text_control_with_regeneration

# Video creation via JSON2Video
from src.mcp.json2video_agent_mcp import run_video_creation

# Google Drive upload
from src.mcp.google_drive_agent_mcp import upload_video_to_google_drive

# WordPress and YouTube publishing
from src.mcp.wordpress_mcp import WordPressMCP
from src.mcp.youtube_mcp import YouTubeMCP

# Use the OpenAI python client for DALL‑E image generation
import openai


class ProductionContentPipelineOrchestrator:
    """Orchestrator coordinating the production workflow using real APIs."""

    def __init__(self) -> None:
        # Load API keys and configuration
        config_path = '/home/claude-workflow/config/api_keys.json'
        with open(config_path, 'r') as f:
            self.config: Dict[str, any] = json.load(f)

        # Set OpenAI API key early for image generation
        openai.api_key = self.config.get('openai_api_key')

        # Initialise MCP/Server wrappers
        self.airtable_server = AirtableMCPServer(
            api_key=self.config['airtable_api_key'],
            base_id=self.config['airtable_base_id'],
            table_name=self.config['airtable_table_name']
        )

        self.content_server = OpenAIContentGenerationServer(
            openai_api_key=self.config['openai_api_key']
        )

        self.scraping_server = ScrapingDogAmazonServer(self.config)
        self.voice_server = VoiceGenerationMCPServer(
            elevenlabs_api_key=self.config['elevenlabs_api_key']
        )

        # Post‑production services
        self.wordpress_service = WordPressMCP(self.config)

        # YouTube MCP will be initialised only when needed
        self.youtube_mcp: Optional[YouTubeMCP] = None


    async def _generate_images(self, products: List[Dict]) -> Dict[int, str]:
        """Generate a DALL‑E image for each product.

        Returns a mapping of product rank to the resulting image URL.  If
        generation fails for a product, that entry will be omitted.
        """
        image_urls: Dict[int, str] = {}
        for product in products:
            rank = product.get('rank')
            name = product.get('name', '')
            description = product.get('description', '')
            if not rank or not name:
                continue
            prompt = (
                f"Create an ultra‑realistic product image of {name}.\n"
                f"Description: {description}\n"
                "Style requirements:\n"
                "- Ultra‑realistic commercial product photography\n"
                "- 9:16 aspect ratio (vertical orientation)\n"
                "- Clean white or subtle gradient background\n"
                "- Professional studio lighting\n"
                "- High detail and clarity\n"
                "- Product should be prominently centered\n"
                "- Commercial advertising quality"
            )
            try:
                # Use DALL‑E 3 via OpenAI's images API
                response = openai.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1792",
                    quality="hd",
                    n=1
                )
                url = response.data[0].url
                image_urls[rank] = url
                print(f"✅ DALL‑E image generated for product #{rank}: {url[:60]}…")
            except Exception as e:
                print(f"❌ Image generation failed for product #{rank}: {e}")
        return image_urls


    async def _generate_voice_data(self, script_data: Dict) -> Dict[str, str]:
        """Generate voice tracks for intro, products and outro via ElevenLabs."""
        voice_data: Dict[str, str] = {}
        # Intro voice
        intro_text = script_data.get('intro', '')
        if intro_text:
            voice = await self.voice_server.generate_intro_voice(intro_text)
            if voice:
                voice_data['intro_voice'] = voice

        # Product voices
        for product in script_data.get('products', []):
            rank = product.get('rank')
            name = product.get('name', '')
            desc = product.get('script', '')
            if not rank:
                continue
            key = f'product_{rank}_voice'
            voice = await self.voice_server.generate_product_voice(name, desc, rank)
            if voice:
                voice_data[key] = voice

        # Outro voice
        outro_text = script_data.get('outro', '')
        if outro_text:
            voice = await self.voice_server.generate_outro_voice(outro_text)
            if voice:
                voice_data['outro_voice'] = voice

        return voice_data


    async def run_complete_workflow(self) -> None:
        """Execute the full production workflow for a single pending Airtable record."""
        print(f"\n🚀 Starting production workflow at {datetime.now()}\n{'='*60}")

        # 1. Acquire a pending record from Airtable
        pending = await self.airtable_server.get_pending_titles()
        if not pending:
            print("❌ No pending records found.  Aborting.")
            return
        record_id = pending['record_id']
        base_title = pending.get('video_title') or pending.get('title')
        print(f"📋 Processing record {record_id}: {base_title}")

        # 2. Generate SEO keywords using GPT‑4
        keywords = await self.content_server.generate_seo_keywords(base_title, "General")
        await self.airtable_server.update_keywords(record_id, keywords)

        # 3. Optimise the title for social media platforms
        optimised_title = await self.content_server.optimize_title(base_title, keywords)

        # 4. Generate the countdown script (intro, product entries and outro)
        script_data = await self.content_server.generate_countdown_script(optimised_title, keywords)
        if not script_data:
            print("❌ Failed to generate script.  Aborting record.")
            return

        # 5. Persist the generated content (keywords, title, script) to Airtable
        await self.airtable_server.save_generated_content(
            record_id,
            {
                'keywords': keywords,
                'optimized_title': optimised_title,
                'script': script_data
            }
        )

        # 6. Validate the generated text and regenerate any invalid products
        control_result = await run_text_control_with_regeneration(self.config, record_id)
        if not control_result.get('success'):
            print(f"⚠️ Text control encountered issues after {control_result.get('attempts', 0)} attempt(s): {control_result.get('error')}")
        elif not control_result.get('all_valid', False):
            print(f"⚠️ Not all products passed validation after regeneration.  Proceeding anyway.")
        else:
            print(f"✅ Text validated after {control_result.get('attempts')} attempt(s)")

        # 7. Generate Amazon affiliate links for each product
        affiliate_result = await run_amazon_affiliate_generation(self.config, record_id)
        if affiliate_result.get('success'):
            print(f"🔗 Affiliate links generated for {affiliate_result.get('products_processed')} products")
        else:
            print(f"⚠️ Affiliate link generation failed: {affiliate_result.get('error')}")

        # 8. Generate images for products using DALL‑E and update Airtable
        image_urls = await self._generate_images(script_data.get('products', []))
        if image_urls:
            await self.airtable_server.save_generated_content(record_id, {'image_urls': image_urls})

        # 9. Generate voice tracks and save them back to Airtable
        voice_data = await self._generate_voice_data(script_data)
        if voice_data:
            await self.airtable_server.save_voice_data(record_id, voice_data)

        # 10. Create the video via JSON2Video
        video_result = await run_video_creation(self.config, record_id)
        if not video_result.get('success'):
            print(f"❌ Video creation failed: {video_result.get('error')}")
            return
        print("🎬 Video creation started successfully")

        video_url = video_result.get('video_url', '')
        project_name = video_result.get('project_name', optimised_title)

        # 11. Upload the video to Google Drive
        if video_url:
            drive_result = await upload_video_to_google_drive(self.config, video_url, project_name, record_id)
            if drive_result.get('success'):
                print(f"☁️ Video uploaded to Google Drive: {drive_result['drive_url']}")
            else:
                print(f"⚠️ Google Drive upload failed: {drive_result.get('error')}")

        # 12. Publish a WordPress blog post
        try:
            wp_result = await self.wordpress_service.create_review_post(pending)
            if wp_result.get('success'):
                print(f"📝 WordPress post created: {wp_result.get('post_url')}")
            else:
                print(f"⚠️ WordPress post failed: {wp_result.get('error')}")
        except Exception as e:
            print(f"❌ WordPress error: {e}")

        # 13. Optionally publish to YouTube Shorts
        if self.config.get('youtube_enabled') and video_url:
            try:
                # Lazy initialisation of YouTube MCP
                self.youtube_mcp = YouTubeMCP(
                    credentials_path=self.config.get('youtube_credentials', '/home/claude-workflow/config/youtube_credentials.json'),
                    token_path=self.config.get('youtube_token', '/home/claude-workflow/config/youtube_token.json')
                )

                # Compose a Shorts title using the optimised title and optional prefixes/suffixes
                prefix = self.config.get('youtube_title_prefix', '')
                suffix = self.config.get('youtube_title_suffix', '')
                raw_title = pending.get('VideoTitle') or pending.get('Title') or optimised_title
                youtube_title = f"{prefix}{raw_title}{suffix}"[:100]

                # Build description: intro + product list + hashtags + disclaimer
                description_lines: List[str] = []
                description_lines.append(raw_title)
                description_lines.append("")
                # Add timestamps for a ~60 second video: intro (0:00), products (0:05…0:50), outro (0:55)
                description_lines.append("⏱️ Timestamps:")
                description_lines.append("0:00 Intro")
                description_lines.append("0:05 Products")
                description_lines.append("0:55 Outro")
                description_lines.append("")
                description_lines.append("🛒 Featured Products:")
                for prod in script_data.get('products', []):
                    description_lines.append(f"#{prod['rank']} {prod['name']}")
                    description_lines.append(prod['script'][:100] + '…')
                    description_lines.append("")
                # Add hashtags from keywords
                hashtags = [f"#{kw.replace(' ', '').replace('-', '')}" for kw in keywords[:10]]
                description_lines.append(' '.join(hashtags))
                # Add Shorts tag and disclaimer
                description_lines.append(self.config.get('youtube_shorts_tag', '#shorts'))
                description_lines.append("")
                description_lines.append("=" * 50)
                description_lines.append("As an Amazon Associate I earn from qualifying purchases.")
                description_lines.append("=" * 50)
                youtube_description = '\n'.join(description_lines)[:5000]

                # Prepare tags list
                tags: List[str] = self.config.get('youtube_tags', []).copy()
                tags.append('shorts')
                tags.extend([kw.lower() for kw in keywords[:10]])
                # Remove duplicates and limit to 30
                tags = list(dict.fromkeys(tags))[:30]

                yt_result = await self.youtube_mcp.upload_video(
                    video_path=video_url,
                    title=youtube_title,
                    description=youtube_description,
                    tags=tags,
                    category_id=self.config.get('youtube_category', '22'),
                    privacy_status=self.config.get('youtube_privacy', 'private')
                )
                if yt_result.get('success'):
                    print(f"📹 YouTube upload successful: {yt_result['video_url']}")
                    # Update Airtable with the YouTube link
                    await self.airtable_server.update_record(record_id, {'YouTubeURL': yt_result['video_url']})
                else:
                    print(f"⚠️ YouTube upload failed: {yt_result.get('error')}")
            except Exception as e:
                print(f"❌ YouTube error: {e}")

        # 14. Mark the record as complete in Airtable
        await self.airtable_server.update_record_status(record_id, "Done")
        print("🎉 Workflow completed successfully!\n")


async def main() -> None:
    orchestrator = ProductionContentPipelineOrchestrator()
    await orchestrator.run_complete_workflow()


if __name__ == '__main__':
    asyncio.run(main())

