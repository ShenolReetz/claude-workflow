"""
Test Runner - Runs all unit and integration tests
"""
import pytest
import sys
import os

# Add project root to path
sys.path.append('/home/claude-workflow')


def run_unit_tests():
    """Run all unit tests"""
    print("\n" + "=" * 70)
    print("RUNNING UNIT TESTS")
    print("=" * 70 + "\n")

    # Run unit tests
    result = pytest.main([
        '/home/claude-workflow/tests/agents',
        '/home/claude-workflow/tests/subagents',
        '-v',
        '--tb=short',
        '--color=yes'
    ])

    return result


def run_integration_tests():
    """Run integration tests"""
    print("\n" + "=" * 70)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 70 + "\n")

    # Check if integration tests exist
    integration_test_file = '/home/claude-workflow/tests/test_integration.py'

    if os.path.exists(integration_test_file):
        result = pytest.main([
            integration_test_file,
            '-v',
            '--tb=short',
            '--color=yes'
        ])
        return result
    else:
        print("⚠️  Integration tests not found")
        return 0


def run_cost_comparison_tests():
    """Run cost comparison tests"""
    print("\n" + "=" * 70)
    print("RUNNING COST COMPARISON TESTS")
    print("=" * 70 + "\n")

    # Check if cost comparison tests exist
    cost_test_file = '/home/claude-workflow/tests/test_cost_comparison.py'

    if os.path.exists(cost_test_file):
        result = pytest.main([
            cost_test_file,
            '-v',
            '--tb=short',
            '--color=yes'
        ])
        return result
    else:
        print("⚠️  Cost comparison tests not found")
        return 0


def display_summary(unit_result, integration_result, cost_result):
    """Display test summary"""
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    # Interpret pytest exit codes
    # 0: All tests passed
    # 1: Tests failed
    # 2: Test execution interrupted
    # 3: Internal error
    # 4: pytest usage error
    # 5: No tests collected

    def get_status(code):
        if code == 0:
            return "✅ PASSED"
        elif code == 5:
            return "⚠️  NO TESTS"
        else:
            return "❌ FAILED"

    print(f"\nUnit Tests:         {get_status(unit_result)}")
    print(f"Integration Tests:  {get_status(integration_result)}")
    print(f"Cost Comparison:    {get_status(cost_result)}")

    total_failed = sum(1 for r in [unit_result, integration_result, cost_result] if r != 0 and r != 5)

    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 70 + "\n")
        return 0
    else:
        print(f"\n❌ {total_failed} test suite(s) failed")
        print("=" * 70 + "\n")
        return 1


if __name__ == "__main__":
    # Run all test suites
    unit_result = run_unit_tests()
    integration_result = run_integration_tests()
    cost_result = run_cost_comparison_tests()

    # Display summary
    exit_code = display_summary(unit_result, integration_result, cost_result)

    sys.exit(exit_code)
