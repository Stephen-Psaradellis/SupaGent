"""
Create test suites in ElevenLabs dashboard.
This tool creates the 10 comprehensive tests in your ElevenLabs agent dashboard.

Usage:
  python -m tools.create_elevenlabs_tests
  python -m tools.create_elevenlabs_tests --suite comprehensive
"""
from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    import argparse
    from agents.agent_testing import ElevenLabsAgentTester
    from agents.test_suites import get_comprehensive_test_suite
    
    parser = argparse.ArgumentParser(description="Create test suites in ElevenLabs dashboard")
    parser.add_argument(
        "--suite",
        choices=["comprehensive", "tool-invocation"],
        default="comprehensive",
        help="Test suite to create",
    )
    parser.add_argument(
        "--name",
        default="SupaGent Comprehensive Test Suite",
        help="Name for the test suite",
    )
    parser.add_argument(
        "--description",
        default="Comprehensive test suite with 10 scenarios covering password reset, account recovery, support queries, and more.",
        help="Description for the test suite",
    )
    args = parser.parse_args()
    
    # Check for required environment variables
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("Error: ELEVENLABS_API_KEY not set.", file=sys.stderr)
        sys.exit(1)
    
    if not os.getenv("ELEVENLABS_AGENT_ID"):
        print("Error: ELEVENLABS_AGENT_ID not set.", file=sys.stderr)
        sys.exit(1)
    
    try:
        tester = ElevenLabsAgentTester()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get scenarios
    if args.suite == "comprehensive":
        from agents.test_suites import get_comprehensive_test_suite
        scenarios = get_comprehensive_test_suite()
    elif args.suite == "tool-invocation":
        from agents.test_suites import get_tool_invocation_test_suite
        scenarios = get_tool_invocation_test_suite()
    else:
        print(f"Unknown suite: {args.suite}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Creating {len(scenarios)} tests in ElevenLabs...", file=sys.stderr)
    print(f"Agent ID: {tester.agent_id}", file=sys.stderr)
    
    # Create tests from scenarios
    created_tests = tester.create_tests_from_scenarios(scenarios)
    
    successful = [t for t in created_tests if "test_id" in t]
    failed = [t for t in created_tests if "error" in t]
    
    print(f"\n✓ Successfully created {len(successful)}/{len(scenarios)} tests", file=sys.stderr)
    
    if successful:
        print("\nCreated test IDs:", file=sys.stderr)
        for test in successful:
            print(f"  - {test['scenario_name']}: {test['test_id']}", file=sys.stderr)
    
    if failed:
        print(f"\n✗ Failed to create {len(failed)} tests:", file=sys.stderr)
        for test in failed:
            print(f"  - {test['scenario_name']}: {test.get('error', 'Unknown error')}", file=sys.stderr)
    
    print(f"\nYou should now see the tests in your ElevenLabs dashboard.", file=sys.stderr)
    print(f"Visit: https://elevenlabs.io/app/agents/{tester.agent_id}/tests", file=sys.stderr)
    
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()

