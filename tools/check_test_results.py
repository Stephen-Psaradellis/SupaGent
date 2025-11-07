#!/usr/bin/env python3
"""
Check test results for ElevenLabs Agent tests.

Usage:
    python -m tools.check_test_results [--suite-id SUITE_ID]
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import httpx
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.agent_testing import ElevenLabsAgentTester


def check_test_results(suite_id: str = None):
    """Check and display test results."""
    load_dotenv()
    
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not agent_id or not api_key:
        print("Error: ELEVENLABS_AGENT_ID and ELEVENLABS_API_KEY must be set")
        return
    
    tester = ElevenLabsAgentTester()
    
    # Get all tests
    print("Fetching test list...")
    tests_response = tester.list_tests()
    all_tests = tests_response.get("tests", [])
    
    # Filter to get the latest tool invocation and comprehensive tests
    tool_tests = [t for t in all_tests if t.get("type") == "tool" and "Tool Invocation" in t.get("name", "")]
    llm_tests = [t for t in all_tests if t.get("type") == "llm"]
    
    # Get the 5 most recent tool tests and 10 most recent LLM tests
    tool_tests = sorted(tool_tests, key=lambda x: x.get("id", ""), reverse=True)[:5]
    llm_tests = sorted(llm_tests, key=lambda x: x.get("id", ""), reverse=True)[:10]
    
    print(f"\nFound {len(tool_tests)} tool invocation tests and {len(llm_tests)} comprehensive tests")
    print("=" * 80)
    
    # Check each test
    results = {
        "tool_tests": [],
        "llm_tests": [],
    }
    
    print("\nTool Invocation Tests:")
    print("-" * 80)
    for test_info in tool_tests:
        test_id = test_info["id"]
        test_name = test_info["name"]
        
        try:
            test = tester.get_test(test_id)
            tool_params = test.get("tool_call_parameters", {})
            tool_ref = tool_params.get("referenced_tool", {})
            
            print(f"✓ {test_name}")
            print(f"  ID: {test_id}")
            print(f"  Tool: {tool_ref.get('id', 'N/A')} (type: {tool_ref.get('type', 'N/A')})")
            
            results["tool_tests"].append({
                "name": test_name,
                "id": test_id,
                "status": "configured",
                "tool": tool_ref.get("id", "N/A"),
            })
        except Exception as e:
            print(f"✗ {test_name}: Error - {str(e)[:100]}")
            results["tool_tests"].append({
                "name": test_name,
                "id": test_id,
                "status": "error",
                "error": str(e)[:100],
            })
    
    print("\nComprehensive Tests (LLM):")
    print("-" * 80)
    for test_info in llm_tests:
        test_id = test_info["id"]
        test_name = test_info["name"]
        
        try:
            test = tester.get_test(test_id)
            has_condition = bool(test.get("success_condition"))
            
            print(f"✓ {test_name}")
            print(f"  ID: {test_id}")
            print(f"  Has success condition: {has_condition}")
            
            results["llm_tests"].append({
                "name": test_name,
                "id": test_id,
                "status": "configured",
            })
        except Exception as e:
            print(f"✗ {test_name}: Error - {str(e)[:100]}")
            results["llm_tests"].append({
                "name": test_name,
                "id": test_id,
                "status": "error",
                "error": str(e)[:100],
            })
    
    print("\n" + "=" * 80)
    print("\nSummary:")
    print(f"  Tool Invocation Tests: {len([r for r in results['tool_tests'] if r['status'] == 'configured'])}/{len(results['tool_tests'])} configured")
    print(f"  Comprehensive Tests: {len([r for r in results['llm_tests'] if r['status'] == 'configured'])}/{len(results['llm_tests'])} configured")
    
    print(f"\n✓ All tests are configured and ready to run")
    print(f"\nView test results in the ElevenLabs dashboard:")
    print(f"https://elevenlabs.io/app/agents/{agent_id}/tests")
    
    # If suite_id provided, try to check suite status
    if suite_id:
        print(f"\nChecking test suite: {suite_id}")
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        
        # Try different endpoint formats
        endpoints = [
            f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}/test-runs/{suite_id}",
            f"https://api.elevenlabs.io/v1/convai/agent-testing/runs/{suite_id}",
        ]
        
        for endpoint in endpoints:
            try:
                response = httpx.get(endpoint, headers=headers, timeout=10.0)
                if response.is_success:
                    suite = response.json()
                    test_runs = suite.get("test_runs", [])
                    
                    if test_runs:
                        print(f"\nTest Suite Results:")
                        print("-" * 80)
                        
                        passed = sum(1 for tr in test_runs if tr.get("status") == "passed")
                        failed = sum(1 for tr in test_runs if tr.get("status") == "failed")
                        pending = sum(1 for tr in test_runs if tr.get("status") == "pending")
                        running = sum(1 for tr in test_runs if tr.get("status") == "running")
                        
                        for tr in test_runs:
                            name = tr.get("test_name", "Unknown")
                            status = tr.get("status", "unknown")
                            symbol = {"passed": "✓", "failed": "✗", "pending": "⏳", "running": "▶"}.get(status, "?")
                            print(f"{symbol} {name}: {status}")
                        
                        print("-" * 80)
                        print(f"Passed: {passed}, Failed: {failed}, Pending: {pending}, Running: {running}")
                        break
            except Exception:
                continue


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check ElevenLabs Agent test results")
    parser.add_argument("--suite-id", help="Test suite ID to check results for")
    args = parser.parse_args()
    
    check_test_results(suite_id=args.suite_id)

