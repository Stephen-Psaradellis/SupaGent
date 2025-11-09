"""
Run comprehensive MCP tool invocation tests.

This script runs all 18 MCP tool tests to ensure they execute successfully
and return expected results. Tests simulate conversations that trigger tool calls
and validate that tools are invoked and executed properly.

Usage:
    python -m tools.run_mcp_tool_tests
    python -m tools.run_mcp_tool_tests --tool search_knowledge_base
    python -m tools.run_mcp_tool_tests --verbose
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from agents.tool_invocation_tester import (
    MCPToolInvocationTester,
    create_mcp_tool_test_scenarios,
    ToolInvocationResult
)


def print_test_header():
    """Print the test header."""
    print("=" * 80)
    print("🛠️  MCP TOOL INVOCATION TESTS")
    print("=" * 80)
    print("Testing all 18 MCP tools for successful execution")
    print()


def print_test_summary(results: List[ToolInvocationResult], execution_time: float):
    """Print a summary of test results."""
    total_tests = len(results)
    passed_tests = len([r for r in results if r.passed])
    failed_tests = total_tests - passed_tests

    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(".1f")
    print(".1f")

    if passed_tests == total_tests:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ {failed_tests} test(s) failed")

    # Show failed tests
    failed_results = [r for r in results if not r.passed]
    if failed_results:
        print("\n❌ Failed Tests:")
        for result in failed_results:
            print(f"  - {result.scenario_name}")
            for error in result.errors:
                print(f"    Error: {error}")


def print_detailed_results(results: List[ToolInvocationResult], verbose: bool = False):
    """Print detailed test results."""
    if not verbose:
        return

    print("\n" + "=" * 80)
    print("📋 DETAILED TEST RESULTS")
    print("=" * 80)

    for result in results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"\n{status}: {result.scenario_name}")
        print(f"   Execution Time: {result.execution_time:.2f}s")

        if result.tool_calls_made:
            print(f"   Tools Called: {len(result.tool_calls_made)}")
            for tool_call in result.tool_calls_made:
                success_status = "✅" if tool_call.get("success", False) else "❌"
                print(f"     {success_status} {tool_call.get('name', 'Unknown')}")

        if result.errors:
            print("   Errors:")
            for error in result.errors:
                print(f"     - {error}")

        if result.details:
            print(f"   Details: {result.details}")


async def run_tool_tests(tool_filter: Optional[str] = None, verbose: bool = False) -> int:
    """Run the MCP tool invocation tests.

    Args:
        tool_filter: Optional tool name to test only specific tool
        verbose: Whether to show detailed output

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print_test_header()

    # Initialize tester
    tester = MCPToolInvocationTester()

    # Get test scenarios
    all_scenarios = create_mcp_tool_test_scenarios()

    # Filter scenarios if requested
    if tool_filter:
        scenarios = [s for s in all_scenarios if tool_filter in s.name]
        if not scenarios:
            print(f"❌ No test scenarios found for tool: {tool_filter}")
            print(f"Available tools: {[s.name.replace('_tool_test', '') for s in all_scenarios]}")
            return 1
    else:
        scenarios = all_scenarios

    print(f"Running {len(scenarios)} test scenario(s)...")
    if tool_filter:
        print(f"Filtered to tool: {tool_filter}")
    print()

    # Run tests
    start_time = time.time()
    results = await tester.run_multiple_tests(scenarios)
    total_execution_time = time.time() - start_time

    # Print results
    print_detailed_results(results, verbose)
    print_test_summary(results, total_execution_time)

    # Save results to file
    summary = tester.get_test_summary(results)
    output_file = "mcp_tool_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n📄 Detailed results saved to: {output_file}")

    # Return appropriate exit code
    failed_tests = len([r for r in results if not r.passed])
    return 0 if failed_tests == 0 else 1


def main():
    """Main entry point for the tool test runner."""
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP tool invocation tests")
    parser.add_argument(
        "--tool",
        help="Run tests for specific tool only (e.g., search_knowledge_base)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed test output"
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all available tools and exit"
    )

    args = parser.parse_args()

    # List tools if requested
    if args.list_tools:
        scenarios = create_mcp_tool_test_scenarios()
        print("Available MCP tools for testing:")
        for scenario in scenarios:
            tool_name = scenario.name.replace("_tool_test", "")
            print(f"  - {tool_name}: {scenario.description}")
        return 0

    # Run tests
    try:
        exit_code = asyncio.run(run_tool_tests(args.tool, args.verbose))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
