#!/usr/bin/env python3
"""
Production Remotion WOW Video Generator MCP Server
===================================================
Generates videos using Remotion with all enhanced WOW effect components.

Enhanced Components Included:
- Animated Star Ratings with sequential fill and sparkles
- Review Count with counting animation
- Dramatic Price Reveal with strike-through and discount badge
- 3D Card Flip Transitions
- Particle Burst Effects (stars, confetti, sparkles)
- Animated Amazon Badges (Choice, Bestseller, Deal, Prime)
- Glitch Transition Effects
- Enhanced Text Animations (bounce, slide, fade, zoom, wave)

Usage:
    mcp = ProductionRemotionWowVideoMCP(config)
    result = await mcp.generate_wow_video(product_data, options)
"""

import asyncio
import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

class ProductionRemotionWowVideoMCP:
    """Production MCP for Remotion video generation with WOW effects."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Remotion WOW Video MCP.

        Args:
            config: Configuration dictionary with paths and settings
        """
        self.config = config
        self.remotion_dir = Path("/home/claude-workflow/remotion-video-generator")
        self.output_dir = Path(config.get('output_dir', '/home/claude-workflow/output/videos'))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # WOW effect configuration
        self.wow_components = {
            'star_rating': True,
            'review_count': True,
            'price_reveal': True,
            'card_flip': True,
            'particle_burst': True,
            'amazon_badge': True,
            'glitch_transition': True,
            'animated_text': True,
        }

    async def generate_wow_video(
        self,
        product_data: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a WOW video with all enhanced components.

        Args:
            product_data: Product information from Amazon scraper
            options: Optional configuration for video generation
                - composition: Composition name (default: "WowVideoUltra")
                - duration: Video duration in frames (default: 360 = 12s)
                - fps: Frames per second (default: 30)
                - width: Video width (default: 1080)
                - height: Video height (default: 1920)
                - effects: Dict to enable/disable specific effects

        Returns:
            Dict with video_path, metadata, and component usage
        """
        try:
            options = options or {}

            # Prepare video props with enhanced components
            video_props = await self._prepare_video_props(product_data, options)

            # Create temporary props file
            props_file = await self._create_props_file(video_props)

            # Generate video using Remotion
            video_path = await self._render_video(props_file, options)

            # Cleanup temp file
            os.remove(props_file)

            # Collect metadata
            metadata = await self._collect_metadata(product_data, video_props, video_path)

            return {
                'success': True,
                'video_path': str(video_path),
                'video_url': f"file://{video_path}",
                'metadata': metadata,
                'components_used': self._get_components_used(video_props),
                'duration': metadata['duration_seconds'],
                'file_size': metadata['file_size_mb'],
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'product_title': product_data.get('Title', 'Unknown'),
            }

    async def _prepare_video_props(
        self,
        product_data: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare video props with all WOW components.

        Returns:
            Props dictionary for Remotion composition
        """
        effects = options.get('effects', {})

        # Merge with defaults
        for component, enabled in self.wow_components.items():
            if component not in effects:
                effects[component] = enabled

        # Extract product information
        title = product_data.get('Title', 'Amazing Product')
        price = product_data.get('Price', '$29.99')
        original_price = product_data.get('OriginalPrice', None)
        rating = float(product_data.get('Rating', 4.5))
        review_count = int(product_data.get('ReviewCount', 1234))
        image_url = product_data.get('ProductImage', '')

        # Determine badge type
        badge_type = self._determine_badge_type(product_data)

        # Build props with WOW components
        props = {
            # Product basics
            'title': title,
            'price': price,
            'originalPrice': original_price,
            'rating': rating,
            'reviewCount': review_count,
            'productImage': image_url,

            # Enhanced components configuration
            'components': {
                # Animated Star Rating
                'starRating': {
                    'enabled': effects.get('star_rating', True),
                    'rating': rating,
                    'size': 40,
                    'showNumber': True,
                    'startFrame': 125,
                },

                # Review Count Animation
                'reviewCount': {
                    'enabled': effects.get('review_count', True),
                    'count': review_count,
                    'size': 28,
                    'startFrame': 135,
                },

                # Dramatic Price Reveal
                'priceTag': {
                    'enabled': effects.get('price_reveal', True),
                    'price': price,
                    'originalPrice': original_price,
                    'accentColor': '#FF6B6B',
                    'startFrame': 185,
                    'showBadge': original_price is not None,
                },

                # Amazon Badge
                'amazonBadge': {
                    'enabled': effects.get('amazon_badge', True),
                    'type': badge_type,
                    'startFrame': 65,
                    'accentColor': '#FF9900',
                },

                # Particle Bursts
                'particleBursts': {
                    'enabled': effects.get('particle_burst', True),
                    'bursts': [
                        {
                            'type': 'ranking',  # When badge appears
                            'triggerFrame': 70,
                        },
                        {
                            'type': 'price_drop',  # When price reveals
                            'triggerFrame': 200,
                            'x': 50,
                            'y': 60,
                        },
                        {
                            'type': 'celebration',  # End of video
                            'triggerFrame': 300,
                        },
                    ],
                },

                # 3D Card Flip
                'cardFlip': {
                    'enabled': effects.get('card_flip', True),
                    'startFrame': 120,
                    'duration': 30,
                    'direction': 'horizontal',
                },

                # Glitch Transitions
                'glitchTransitions': {
                    'enabled': effects.get('glitch_transition', True),
                    'transitions': [
                        {
                            'startFrame': 60,
                            'duration': 15,
                            'intensity': 1.0,
                        },
                        {
                            'startFrame': 240,
                            'duration': 20,
                            'intensity': 1.2,
                        },
                    ],
                },

                # Animated Text
                'animatedText': {
                    'enabled': effects.get('animated_text', True),
                    'title': {
                        'text': title,
                        'type': 'ProductTitleText',
                        'startFrame': 10,
                    },
                    'callouts': [
                        {
                            'text': 'LIMITED TIME OFFER!' if original_price else 'POPULAR CHOICE!',
                            'type': 'CalloutText',
                            'startFrame': 20,
                            'accentColor': '#FF6B6B',
                        },
                    ],
                    'description': {
                        'text': product_data.get('Description', 'Premium quality product')[:80],
                        'type': 'DescriptionText',
                        'startFrame': 30,
                    },
                },
            },

            # Video settings
            'duration': options.get('duration', 360),  # 12 seconds at 30fps
            'fps': options.get('fps', 30),
            'backgroundColor': '#0a0a0a',
            'accentColor': '#FF6B6B',

            # Branding
            'branding': {
                'showLogo': True,
                'brandName': options.get('brand_name', 'Product Reviews'),
                'logoUrl': options.get('logo_url', ''),
            },
        }

        return props

    def _determine_badge_type(self, product_data: Dict[str, Any]) -> str:
        """
        Determine which Amazon badge to show.

        Priority:
        1. Bestseller (if ranking #1)
        2. Amazon's Choice
        3. Limited Time Deal (if discount > 20%)
        4. Prime
        """
        # Check for bestseller
        if product_data.get('BestSellerRank', 99999) <= 10:
            return 'bestseller'

        # Check for Amazon's Choice
        if product_data.get('AmazonChoice', False):
            return 'choice'

        # Check for big discount
        if product_data.get('OriginalPrice'):
            try:
                original = float(product_data['OriginalPrice'].replace('$', '').replace(',', ''))
                current = float(product_data.get('Price', '0').replace('$', '').replace(',', ''))
                discount_percent = ((original - current) / original) * 100
                if discount_percent >= 20:
                    return 'deal'
            except (ValueError, ZeroDivisionError):
                pass

        # Default to Prime
        return 'prime'

    async def _create_props_file(self, props: Dict[str, Any]) -> str:
        """Create temporary JSON file with video props."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(props, f, indent=2)
            return f.name

    async def _render_video(
        self,
        props_file: str,
        options: Dict[str, Any]
    ) -> Path:
        """
        Render video using Remotion CLI.

        Args:
            props_file: Path to JSON props file
            options: Render options

        Returns:
            Path to rendered video file
        """
        composition = options.get('composition', 'WowVideoUltra')
        fps = options.get('fps', 30)
        width = options.get('width', 1080)
        height = options.get('height', 1920)

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f"wow_video_{timestamp}.mp4"

        # Remotion render command
        cmd = [
            'npx', 'remotion', 'render',
            composition,
            str(output_file),
            '--props', props_file,
            '--codec', 'h264',
            '--fps', str(fps),
            '--width', str(width),
            '--height', str(height),
            '--quality', '90',
            '--concurrency', '4',
        ]

        # Run from Remotion directory
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.remotion_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.wait()

        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown render error"
            raise Exception(f"Remotion render failed: {error_msg}")

        if not output_file.exists():
            raise Exception(f"Video file not created: {output_file}")

        return output_file

    async def _collect_metadata(
        self,
        product_data: Dict[str, Any],
        video_props: Dict[str, Any],
        video_path: Path
    ) -> Dict[str, Any]:
        """Collect video metadata."""
        file_size = video_path.stat().st_size

        return {
            'product_title': product_data.get('Title', 'Unknown'),
            'created_at': datetime.now().isoformat(),
            'duration_frames': video_props['duration'],
            'duration_seconds': video_props['duration'] / video_props['fps'],
            'fps': video_props['fps'],
            'resolution': f"{video_props.get('width', 1080)}x{video_props.get('height', 1920)}",
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'codec': 'h264',
        }

    def _get_components_used(self, video_props: Dict[str, Any]) -> List[str]:
        """Get list of WOW components used in the video."""
        components_used = []

        for component_name, component_config in video_props.get('components', {}).items():
            if isinstance(component_config, dict) and component_config.get('enabled', False):
                components_used.append(component_name)

        return components_used

    async def test_all_components(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test video generation with all WOW components enabled.

        Returns:
            Test results with component verification
        """
        print("\n🧪 Testing All WOW Components...")

        # Generate video with all components
        result = await self.generate_wow_video(product_data, {
            'effects': {
                'star_rating': True,
                'review_count': True,
                'price_reveal': True,
                'card_flip': True,
                'particle_burst': True,
                'amazon_badge': True,
                'glitch_transition': True,
                'animated_text': True,
            }
        })

        if not result.get('success'):
            return {
                'test_passed': False,
                'error': result.get('error'),
            }

        # Verify all components were used
        components_used = result.get('components_used', [])
        expected_components = list(self.wow_components.keys())

        missing_components = [c for c in expected_components if c not in components_used]

        test_passed = len(missing_components) == 0

        return {
            'test_passed': test_passed,
            'video_path': result['video_path'],
            'components_used': components_used,
            'components_expected': expected_components,
            'missing_components': missing_components,
            'total_components': len(components_used),
            'duration_seconds': result['duration'],
            'file_size_mb': result['file_size_mb'],
        }


# MCP Server Interface Functions
async def mcp_generate_wow_video(
    product_data: Dict[str, Any],
    config: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    MCP interface for WOW video generation.

    Args:
        product_data: Product information from scraper
        config: System configuration
        options: Optional video generation options

    Returns:
        Video generation result with path and metadata
    """
    mcp = ProductionRemotionWowVideoMCP(config)
    return await mcp.generate_wow_video(product_data, options)


async def mcp_test_wow_components(
    product_data: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    MCP interface for testing all WOW components.

    Args:
        product_data: Product information for test
        config: System configuration

    Returns:
        Test results
    """
    mcp = ProductionRemotionWowVideoMCP(config)
    return await mcp.test_all_components(product_data)


if __name__ == "__main__":
    # Test the MCP
    import sys
    sys.path.append('/home/claude-workflow')

    async def test():
        # Load config
        with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
            config = json.load(f)

        # Sample product data
        sample_product = {
            'Title': 'Wireless Gaming Mouse RGB Programmable',
            'Price': '$29.99',
            'OriginalPrice': '$49.99',
            'Rating': 4.7,
            'ReviewCount': 12453,
            'ProductImage': '/home/claude-workflow/test_product_image.jpg',
            'Description': 'High-performance wireless gaming mouse with customizable RGB lighting',
            'BestSellerRank': 3,
            'AmazonChoice': True,
        }

        # Test all components
        result = await mcp_test_wow_components(sample_product, config)

        print("\n" + "="*80)
        print("🎬 REMOTION WOW VIDEO MCP - TEST RESULTS")
        print("="*80)

        if result['test_passed']:
            print("✅ TEST PASSED - All WOW components integrated successfully!")
        else:
            print("❌ TEST FAILED - Some components missing")

        print(f"\n📊 Components:")
        print(f"   Total Used: {result['total_components']}")
        print(f"   Expected: {len(result['components_expected'])}")

        if result.get('missing_components'):
            print(f"\n⚠️  Missing Components:")
            for component in result['missing_components']:
                print(f"   - {component}")

        print(f"\n📹 Video Details:")
        print(f"   Path: {result.get('video_path', 'N/A')}")
        print(f"   Duration: {result.get('duration_seconds', 0):.1f}s")
        print(f"   File Size: {result.get('file_size_mb', 0):.2f} MB")

        print(f"\n✨ WOW Components Used:")
        for component in result.get('components_used', []):
            print(f"   ✓ {component}")

        print("\n" + "="*80)

    asyncio.run(test())
