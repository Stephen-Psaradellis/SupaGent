"""
Export test scenarios in a format that can be easily imported into ElevenLabs dashboard.
This creates a JSON file with all test scenarios that you can use to manually create tests.

Usage:
  python -m tools.export_tests_for_dashboard
  python -m tools.export_tests_for_dashboard --format json --output tests.json
"""
from __future__ import annotations

import json
import sys
import argparse
from pathlib import Path

from agents.test_suites import get_comprehensive_test_suite


def main():
    parser = argparse.ArgumentParser(description="Export tests for ElevenLabs dashboard")
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--output",
        default="test_scenarios.json",
        help="Output file path",
    )
    parser.add_argument(
        "--suite",
        choices=["comprehensive"],
        default="comprehensive",
        help="Test suite to export",
    )
    args = parser.parse_args()
    
    # Get scenarios
    if args.suite == "comprehensive":
        scenarios = get_comprehensive_test_suite()
    else:
        print(f"Unknown suite: {args.suite}", file=sys.stderr)
        sys.exit(1)
    
    if args.format == "json":
        # Export as JSON
        test_suite = {
            "name": "SupaGent Comprehensive Test Suite",
            "description": "Comprehensive test suite with 10 scenarios covering password reset, account recovery, support queries, and more.",
            "scenarios": [
                {
                    "name": s.name,
                    "messages": s.messages,
                    "expected_tool_calls": s.expected_tool_calls or [],
                    "expected_keywords": s.expected_keywords or [],
                }
                for s in scenarios
            ]
        }
        
        output_path = Path(args.output)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(test_suite, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported {len(scenarios)} test scenarios to {output_path}", file=sys.stderr)
        print(f"\nTo import into ElevenLabs:", file=sys.stderr)
        print(f"1. Go to your agent's test page in the ElevenLabs dashboard", file=sys.stderr)
        print(f"2. Use the 'Import' or 'Create from JSON' option if available", file=sys.stderr)
        print(f"3. Or manually create each test using the scenarios in the JSON file", file=sys.stderr)
        print(f"\nFile location: {output_path.absolute()}", file=sys.stderr)
        
    else:
        # Export as Markdown for easy reading
        output_path = Path(args.output)
        with output_path.open("w", encoding="utf-8") as f:
            f.write("# SupaGent Comprehensive Test Suite\n\n")
            f.write("Comprehensive test suite with 10 scenarios.\n\n")
            
            for i, scenario in enumerate(scenarios, 1):
                f.write(f"## Test {i}: {scenario.name}\n\n")
                f.write("### Messages:\n\n")
                for msg in scenario.messages:
                    f.write(f"- **{msg.get('role', 'user')}**: {msg.get('content', '')}\n")
                f.write("\n")
                
                if scenario.expected_tool_calls:
                    f.write("### Expected Tool Calls:\n\n")
                    for tool in scenario.expected_tool_calls:
                        f.write(f"- `{tool}`\n")
                    f.write("\n")
                
                if scenario.expected_keywords:
                    f.write("### Expected Keywords:\n\n")
                    for keyword in scenario.expected_keywords:
                        f.write(f"- `{keyword}`\n")
                    f.write("\n")
                f.write("---\n\n")
        
        print(f"✓ Exported {len(scenarios)} test scenarios to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

