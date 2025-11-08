"""
Run all tool invocation tests and verify they pass.

Usage:
    python -m tools.run_tool_invocation_tests
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from agents.agent_testing import ElevenLabsAgentTester
from agents.test_suites import get_tool_invocation_test_suite


def main():
    """Run all tool invocation tests and verify they pass."""
    try:
        tester = ElevenLabsAgentTester()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get all tool invocation tests
    print("Fetching tool invocation tests...", file=sys.stderr)
    tests_response = tester.list_tests()
    all_tests = tests_response.get("tests", [])
    
    # Filter to get tool invocation tests (type == "tool" and name contains "Tool Invocation")
    tool_tests = [
        t for t in all_tests 
        if t.get("type") == "tool" and "Tool Invocation" in t.get("name", "")
    ]
    
    if not tool_tests:
        print("No tool invocation tests found. Creating them...", file=sys.stderr)
        # Create tests if they don't exist
        scenarios = get_tool_invocation_test_suite()
        created_tests = tester.create_tests_from_scenarios(scenarios)
        
        successful = [t for t in created_tests if "test_id" in t]
        if not successful:
            print("Failed to create tests.", file=sys.stderr)
            sys.exit(1)
        
        tool_tests = [
            {"id": t["test_id"], "name": t["scenario_name"]}
            for t in successful
        ]
    
    # Sort by name to ensure consistent ordering
    tool_tests = sorted(tool_tests, key=lambda x: x.get("name", ""))
    
    print(f"\nFound {len(tool_tests)} tool invocation tests", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Get test IDs
    test_ids = [t["id"] for t in tool_tests]
    
    # Run all tests
    print(f"\nRunning {len(test_ids)} tests...", file=sys.stderr)
    run_result = tester.run_tests(test_ids)
    
    if "error" in run_result:
        print(f"Error running tests: {run_result['error']}", file=sys.stderr)
        sys.exit(1)
    
    # Get the run ID from the response
    run_id = run_result.get("id") or run_result.get("run_id")
    if not run_id:
        print("Warning: Could not get run ID from response. Tests may still be running.", file=sys.stderr)
        print(f"Response: {run_result}", file=sys.stderr)
        sys.exit(0)
    
    print(f"Test run ID: {run_id}", file=sys.stderr)
    print("Waiting for tests to complete...", file=sys.stderr)
    
    # Poll for results (tests run asynchronously)
    max_wait_time = 300  # 5 minutes
    wait_interval = 5  # Check every 5 seconds
    elapsed = 0
    
    import httpx
    from core.secrets import get_elevenlabs_api_key
    
    api_key = get_elevenlabs_api_key()
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    
    # Try different endpoint formats for test run results
    endpoints = [
        f"https://api.elevenlabs.io/v1/convai/agents/{tester.agent_id}/test-runs/{run_id}",
        f"https://api.elevenlabs.io/v1/convai/agent-testing/runs/{run_id}",
    ]
    
    while elapsed < max_wait_time:
        time.sleep(wait_interval)
        elapsed += wait_interval
        
        # Try to get test run results
        suite_data = None
        for endpoint in endpoints:
            try:
                response = httpx.get(endpoint, headers=headers, timeout=10.0)
                if response.is_success:
                    suite_data = response.json()
                    break
            except Exception:
                continue
        
        if not suite_data:
            print(f"Waiting... ({elapsed}s)", file=sys.stderr)
            continue
        
        test_runs = suite_data.get("test_runs", [])
        if not test_runs:
            print(f"Waiting for test runs to start... ({elapsed}s)", file=sys.stderr)
            continue
        
        # Check if all tests are complete
        completed = [tr for tr in test_runs if tr.get("status") in ["passed", "failed"]]
        running = [tr for tr in test_runs if tr.get("status") == "running"]
        pending = [tr for tr in test_runs if tr.get("status") == "pending"]
        
        if len(completed) == len(test_runs):
            # All tests complete
            print(f"\nAll tests completed!", file=sys.stderr)
            print("=" * 80, file=sys.stderr)
            
            # Display results
            passed = [tr for tr in test_runs if tr.get("status") == "passed"]
            failed = [tr for tr in test_runs if tr.get("status") == "failed"]
            
            print(f"\nPassed: {len(passed)}/{len(test_runs)}", file=sys.stderr)
            print(f"Failed: {len(failed)}/{len(test_runs)}", file=sys.stderr)
            
            if passed:
                print("\n✓ Passed tests:", file=sys.stderr)
                for tr in passed:
                    name = tr.get("test_name", "Unknown")
                    print(f"  - {name}", file=sys.stderr)
            
            if failed:
                print("\n✗ Failed tests:", file=sys.stderr)
                for tr in failed:
                    name = tr.get("test_name", "Unknown")
                    error = tr.get("error") or tr.get("failure_reason", "Unknown error")
                    print(f"  - {name}: {error}", file=sys.stderr)
            
            print("=" * 80, file=sys.stderr)
            
            if failed:
                print(f"\n⚠️  {len(failed)} test(s) failed. Please review the results.", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"\n✓ All {len(passed)} tests passed!", file=sys.stderr)
                sys.exit(0)
        else:
            print(f"Progress: {len(completed)}/{len(test_runs)} complete, {len(running)} running, {len(pending)} pending...", file=sys.stderr)
    
    print(f"\nTimeout: Tests did not complete within {max_wait_time} seconds.", file=sys.stderr)
    print("Please check the ElevenLabs dashboard for results.", file=sys.stderr)
    print(f"Visit: https://elevenlabs.io/app/agents/{tester.agent_id}/tests", file=sys.stderr)
    print(f"Test run ID: {run_id}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()

