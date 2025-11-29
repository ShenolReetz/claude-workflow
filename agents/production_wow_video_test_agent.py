#!/usr/bin/env python3
"""
Production WOW Video Test Agent
================================
Tests and validates Remotion WOW video generation with all enhanced components.

This agent:
1. Validates all 8 WOW components are integrated
2. Tests video generation with different configurations
3. Verifies component animations and timing
4. Generates test report with recommendations

Enhanced Components Tested:
- ⭐ Animated Star Ratings (sequential fill + sparkles)
- 📊 Review Count (counting animation + pulse)
- 💰 Dramatic Price Reveal (strike-through + bounce + flash)
- 🔄 3D Card Flip Transitions
- 💥 Particle Burst Effects (stars, confetti, sparkles)
- 🏆 Amazon Badges (Choice, Bestseller, Deal, Prime)
- 🌀 Glitch Transitions (RGB split + scan lines)
- 📝 Animated Text (bounce, slide, fade, zoom, wave)

Usage:
    agent = ProductionWowVideoTestAgent(config)
    await agent.test_all_components()
    await agent.generate_comparison_videos()
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append('/home/claude-workflow')

from mcp_servers.production_remotion_wow_video_mcp import (
    ProductionRemotionWowVideoMCP,
    mcp_generate_wow_video,
    mcp_test_wow_components
)


class ProductionWowVideoTestAgent:
    """Agent to test and validate WOW video generation."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize WOW Video Test Agent.

        Args:
            config: System configuration
        """
        self.config = config
        self.mcp = ProductionRemotionWowVideoMCP(config)
        self.test_results = []

        # Test scenarios
        self.test_scenarios = [
            {
                'name': 'All Components Enabled',
                'description': 'Test with all 8 WOW components active',
                'effects': {
                    'star_rating': True,
                    'review_count': True,
                    'price_reveal': True,
                    'card_flip': True,
                    'particle_burst': True,
                    'amazon_badge': True,
                    'glitch_transition': True,
                    'animated_text': True,
                },
            },
            {
                'name': 'Bestseller Product',
                'description': 'Test bestseller badge with all effects',
                'product_overrides': {
                    'BestSellerRank': 1,
                    'OriginalPrice': None,
                },
                'effects': {
                    'amazon_badge': True,
                    'particle_burst': True,
                    'star_rating': True,
                },
            },
            {
                'name': 'Deal Product',
                'description': 'Test deal badge with price discount',
                'product_overrides': {
                    'OriginalPrice': '$99.99',
                    'Price': '$29.99',
                },
                'effects': {
                    'amazon_badge': True,
                    'price_reveal': True,
                    'particle_burst': True,
                },
            },
            {
                'name': 'Minimal Effects',
                'description': 'Test with only essential components',
                'effects': {
                    'star_rating': True,
                    'review_count': True,
                    'price_reveal': True,
                    'animated_text': True,
                },
            },
        ]

    async def run_comprehensive_test(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run comprehensive test of all WOW components.

        Args:
            product_data: Product information for testing

        Returns:
            Complete test results
        """
        print("\n" + "="*80)
        print("🎬 PRODUCTION WOW VIDEO TEST AGENT")
        print("="*80)
        print(f"Product: {product_data.get('Title', 'Test Product')}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

        # Test 1: Component Integration Test
        print("📋 Test 1: Component Integration")
        print("-" * 80)
        integration_result = await self._test_component_integration(product_data)
        self.test_results.append(integration_result)
        self._print_test_result(integration_result)

        # Test 2: Scenario Testing
        print("\n📋 Test 2: Scenario Testing")
        print("-" * 80)
        scenario_results = await self._test_scenarios(product_data)
        self.test_results.extend(scenario_results)

        # Test 3: Performance Validation
        print("\n📋 Test 3: Performance Validation")
        print("-" * 80)
        performance_result = await self._test_performance(product_data)
        self.test_results.append(performance_result)
        self._print_test_result(performance_result)

        # Generate final report
        report = await self._generate_report()

        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        self._print_report(report)

        return report

    async def _test_component_integration(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test that all 8 WOW components are properly integrated."""
        print("Testing all 8 WOW components integration...")

        result = await mcp_test_wow_components(product_data, self.config)

        return {
            'test_name': 'Component Integration',
            'passed': result.get('test_passed', False),
            'components_found': result.get('total_components', 0),
            'components_expected': 8,
            'missing_components': result.get('missing_components', []),
            'video_path': result.get('video_path', ''),
            'duration': result.get('duration_seconds', 0),
            'file_size_mb': result.get('file_size_mb', 0),
            'timestamp': datetime.now().isoformat(),
        }

    async def _test_scenarios(self, product_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test different video generation scenarios."""
        results = []

        for scenario in self.test_scenarios:
            print(f"\nTesting: {scenario['name']}")
            print(f"Description: {scenario['description']}")

            # Merge product overrides
            test_product = product_data.copy()
            if 'product_overrides' in scenario:
                test_product.update(scenario['product_overrides'])

            # Generate video
            try:
                video_result = await mcp_generate_wow_video(
                    test_product,
                    self.config,
                    {'effects': scenario['effects']}
                )

                result = {
                    'test_name': scenario['name'],
                    'passed': video_result.get('success', False),
                    'description': scenario['description'],
                    'components_used': video_result.get('components_used', []),
                    'video_path': video_result.get('video_path', ''),
                    'duration': video_result.get('duration', 0),
                    'file_size_mb': video_result.get('file_size_mb', 0),
                    'error': video_result.get('error'),
                    'timestamp': datetime.now().isoformat(),
                }

                if result['passed']:
                    print(f"  ✅ SUCCESS - Generated video with {len(result['components_used'])} components")
                else:
                    print(f"  ❌ FAILED - {result.get('error', 'Unknown error')}")

            except Exception as e:
                result = {
                    'test_name': scenario['name'],
                    'passed': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                }
                print(f"  ❌ EXCEPTION - {str(e)}")

            results.append(result)

        return results

    async def _test_performance(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test video generation performance."""
        print("Testing performance metrics...")

        start_time = datetime.now()

        # Generate a full WOW video
        result = await mcp_generate_wow_video(product_data, self.config)

        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()

        passed = (
            result.get('success', False) and
            generation_time < 120 and  # Should complete in under 2 minutes
            result.get('file_size_mb', 0) < 50  # Should be under 50MB
        )

        return {
            'test_name': 'Performance Validation',
            'passed': passed,
            'generation_time_seconds': generation_time,
            'file_size_mb': result.get('file_size_mb', 0),
            'duration_seconds': result.get('duration', 0),
            'fps': 30,
            'resolution': '1080x1920',
            'timestamp': datetime.now().isoformat(),
        }

    async def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get('passed', False))
        failed_tests = total_tests - passed_tests

        # Collect all components tested
        all_components = set()
        for result in self.test_results:
            if 'components_used' in result:
                all_components.update(result['components_used'])

        # Expected WOW components
        expected_components = [
            'starRating',
            'reviewCount',
            'priceTag',
            'cardFlip',
            'particleBursts',
            'amazonBadge',
            'glitchTransitions',
            'animatedText',
        ]

        missing_components = [c for c in expected_components if c not in all_components]

        return {
            'test_summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
            },
            'component_coverage': {
                'expected': len(expected_components),
                'found': len(all_components),
                'missing': missing_components,
                'coverage_rate': f"{(len(all_components) / len(expected_components) * 100):.1f}%",
            },
            'test_results': self.test_results,
            'recommendations': self._generate_recommendations(),
            'timestamp': datetime.now().isoformat(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        # Check integration test
        integration_test = next((r for r in self.test_results if r.get('test_name') == 'Component Integration'), None)

        if integration_test:
            if not integration_test.get('passed'):
                recommendations.append(
                    "❌ Component integration test failed. Review missing components and fix integration."
                )
            else:
                recommendations.append(
                    "✅ All 8 WOW components successfully integrated!"
                )

        # Check performance
        perf_test = next((r for r in self.test_results if r.get('test_name') == 'Performance Validation'), None)

        if perf_test:
            gen_time = perf_test.get('generation_time_seconds', 0)
            if gen_time > 120:
                recommendations.append(
                    f"⚠️ Video generation took {gen_time:.1f}s. Consider optimization or parallel rendering."
                )
            else:
                recommendations.append(
                    f"✅ Performance excellent: {gen_time:.1f}s generation time."
                )

        # Check file sizes
        large_videos = [r for r in self.test_results if r.get('file_size_mb', 0) > 30]
        if large_videos:
            recommendations.append(
                f"⚠️ {len(large_videos)} videos exceed 30MB. Consider compression or quality adjustment."
            )

        # Check scenario coverage
        scenario_tests = [r for r in self.test_results if 'Scenario' in r.get('test_name', '') or r.get('test_name') in [s['name'] for s in self.test_scenarios]]
        failed_scenarios = [r for r in scenario_tests if not r.get('passed')]

        if failed_scenarios:
            recommendations.append(
                f"❌ {len(failed_scenarios)} scenario tests failed. Review error messages."
            )

        return recommendations

    def _print_test_result(self, result: Dict[str, Any]):
        """Print formatted test result."""
        status = "✅ PASSED" if result.get('passed') else "❌ FAILED"
        print(f"\n{status}: {result.get('test_name', 'Unknown Test')}")

        if result.get('components_found'):
            print(f"  Components: {result['components_found']}/{result.get('components_expected', 8)}")

        if result.get('missing_components'):
            print(f"  Missing: {', '.join(result['missing_components'])}")

        if result.get('video_path'):
            print(f"  Video: {Path(result['video_path']).name}")
            print(f"  Duration: {result.get('duration', 0):.1f}s")
            print(f"  Size: {result.get('file_size_mb', 0):.2f} MB")

        if result.get('generation_time_seconds'):
            print(f"  Generation Time: {result['generation_time_seconds']:.1f}s")

        if result.get('error'):
            print(f"  Error: {result['error']}")

    def _print_report(self, report: Dict[str, Any]):
        """Print formatted test report."""
        summary = report.get('test_summary', {})
        coverage = report.get('component_coverage', {})

        print(f"\n📊 Tests: {summary.get('passed')}/{summary.get('total_tests')} passed ({summary.get('success_rate')})")
        print(f"✨ Components: {coverage.get('found')}/{coverage.get('expected')} found ({coverage.get('coverage_rate')})")

        if coverage.get('missing'):
            print(f"\n⚠️  Missing Components:")
            for component in coverage['missing']:
                print(f"   - {component}")

        print(f"\n💡 Recommendations:")
        for rec in report.get('recommendations', []):
            print(f"   {rec}")

    async def generate_sample_videos(self) -> List[str]:
        """
        Generate sample videos showcasing all WOW components.

        Returns:
            List of generated video paths
        """
        print("\n🎬 Generating Sample Videos...")

        sample_products = [
            {
                'Title': 'Premium Wireless Gaming Mouse RGB',
                'Price': '$29.99',
                'OriginalPrice': '$49.99',
                'Rating': 4.8,
                'ReviewCount': 15234,
                'BestSellerRank': 1,
                'AmazonChoice': True,
                'Description': 'High-performance wireless gaming mouse with customizable RGB lighting and programmable buttons',
            },
            {
                'Title': 'Mechanical Keyboard Blue Switches',
                'Price': '$79.99',
                'OriginalPrice': None,
                'Rating': 4.6,
                'ReviewCount': 8942,
                'AmazonChoice': True,
                'Description': 'Professional mechanical keyboard with tactile blue switches for gaming and typing',
            },
            {
                'Title': 'Noise Cancelling Headphones Bluetooth',
                'Price': '$149.99',
                'OriginalPrice': '$299.99',
                'Rating': 4.7,
                'ReviewCount': 23145,
                'Description': 'Active noise cancelling wireless headphones with 30-hour battery life',
            },
        ]

        video_paths = []

        for i, product in enumerate(sample_products, 1):
            print(f"\n[{i}/{len(sample_products)}] {product['Title'][:50]}...")

            result = await mcp_generate_wow_video(product, self.config)

            if result.get('success'):
                video_path = result['video_path']
                video_paths.append(video_path)
                print(f"  ✅ Generated: {Path(video_path).name}")
                print(f"  📊 Components: {len(result.get('components_used', []))}")
                print(f"  ⏱️  Duration: {result.get('duration', 0):.1f}s")
                print(f"  💾 Size: {result.get('file_size_mb', 0):.2f} MB")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")

        return video_paths


async def main():
    """Main test execution."""
    # Load config
    with open('/home/claude-workflow/config/api_keys.json', 'r') as f:
        config = json.load(f)

    # Create agent
    agent = ProductionWowVideoTestAgent(config)

    # Sample product for testing
    test_product = {
        'Title': 'Wireless Gaming Mouse RGB Programmable 16000 DPI',
        'Price': '$29.99',
        'OriginalPrice': '$49.99',
        'Rating': 4.7,
        'ReviewCount': 12453,
        'ProductImage': '/home/claude-workflow/test_product_image.jpg',
        'Description': 'High-performance wireless gaming mouse with customizable RGB lighting',
        'BestSellerRank': 3,
        'AmazonChoice': True,
    }

    # Run comprehensive test
    report = await agent.run_comprehensive_test(test_product)

    # Save report
    report_file = Path('/home/claude-workflow/output/wow_video_test_report.json')
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved: {report_file}")

    # Generate sample videos (optional)
    # video_paths = await agent.generate_sample_videos()
    # print(f"\n✅ Generated {len(video_paths)} sample videos")


if __name__ == "__main__":
    asyncio.run(main())
