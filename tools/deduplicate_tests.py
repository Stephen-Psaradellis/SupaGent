#!/usr/bin/env python3
"""
Deduplicate ElevenLabs Agent tests.

Fetches all tests via the API, identifies duplicates based on name and chat history,
and deletes the duplicate tests, keeping one of each.

Usage:
    python -m tools.deduplicate_tests [--dry-run] [--verbose]
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.agent_testing import ElevenLabsAgentTester


def normalize_chat_history(chat_history: List[Dict[str, Any]]) -> str:
    """Normalize chat history for comparison.
    
    Extracts the message content from chat history and creates a normalized
    string representation for duplicate detection.
    
    Args:
        chat_history: List of chat history entries.
        
    Returns:
        Normalized string representation of chat history.
    """
    messages = []
    for entry in chat_history:
        # Extract message content - could be in 'message' or 'content' field
        message = entry.get("message") or entry.get("content", "")
        role = entry.get("role", "user")
        # Normalize: lowercase and strip whitespace
        messages.append(f"{role}:{message.lower().strip()}")
    return "|".join(messages)


def get_test_signature(test: Dict[str, Any]) -> Tuple[str, str]:
    """Generate a signature for a test to identify duplicates.
    
    Creates a tuple of (name, normalized_chat_history) that can be used
    to identify duplicate tests.
    
    Args:
        test: Test dictionary from API.
        
    Returns:
        Tuple of (normalized_name, normalized_chat_history).
    """
    name = test.get("name", "").lower().strip()
    chat_history = test.get("chat_history", [])
    normalized_history = normalize_chat_history(chat_history)
    return (name, normalized_history)


def fetch_all_tests(tester: ElevenLabsAgentTester) -> List[Dict[str, Any]]:
    """Fetch all tests from the API with pagination support.
    
    Handles pagination by following cursor links until all tests are retrieved.
    
    Args:
        tester: ElevenLabsAgentTester instance.
        
    Returns:
        List of all test dictionaries.
    """
    all_tests = []
    cursor = None
    page_size = 100  # Maximum page size
    
    print("Fetching all tests from API...")
    
    while True:
        try:
            response = tester.list_tests(cursor=cursor, page_size=page_size)
            tests = response.get("tests", [])
            all_tests.extend(tests)
            
            print(f"  Fetched {len(tests)} tests (total: {len(all_tests)})")
            
            # Check for next page
            cursor = response.get("next_cursor")
            if not cursor:
                break
                
        except Exception as e:
            print(f"Error fetching tests: {e}")
            break
    
    print(f"\nTotal tests fetched: {len(all_tests)}")
    return all_tests


def get_full_test_details(tester: ElevenLabsAgentTester, test_id: str) -> Dict[str, Any]:
    """Get full test details including chat history.
    
    The list_tests endpoint may not include full chat history, so we
    fetch the complete test details for duplicate detection.
    
    Args:
        tester: ElevenLabsAgentTester instance.
        test_id: Test ID to fetch.
        
    Returns:
        Full test dictionary with all details.
    """
    try:
        return tester.get_test(test_id)
    except Exception as e:
        print(f"Warning: Could not fetch test {test_id}: {e}")
        return {}


def identify_duplicates(tester: ElevenLabsAgentTester, tests: List[Dict[str, Any]], verbose: bool = False) -> Dict[str, List[str]]:
    """Identify duplicate tests.
    
    Groups tests by their signature (name + chat history) and identifies
    which ones are duplicates.
    
    Args:
        tester: ElevenLabsAgentTester instance.
        tests: List of test dictionaries from list_tests.
        verbose: Whether to print verbose output.
        
    Returns:
        Dictionary mapping test signatures to lists of test IDs (duplicates).
    """
    print("\nIdentifying duplicates...")
    print("Fetching full test details for accurate comparison...")
    
    # Group tests by signature
    signature_to_tests: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    
    for i, test in enumerate(tests):
        test_id = test.get("id")
        if not test_id:
            continue
            
        if verbose:
            print(f"  Processing test {i+1}/{len(tests)}: {test.get('name', 'Unknown')} ({test_id})")
        
        # Get full test details to ensure we have chat_history
        full_test = get_full_test_details(tester, test_id)
        if not full_test:
            continue
        
        # Use the full test data
        signature = get_test_signature(full_test)
        signature_to_tests[signature].append({
            "id": test_id,
            "name": full_test.get("name", "Unknown"),
            "full_test": full_test,
        })
    
    # Find duplicates (signatures with more than one test)
    duplicates: Dict[str, List[str]] = {}
    
    for signature, test_list in signature_to_tests.items():
        if len(test_list) > 1:
            # Multiple tests with same signature - these are duplicates
            test_ids = [t["id"] for t in test_list]
            test_names = [t["name"] for t in test_list]
            
            # Use a readable key for the duplicates dict
            key = f"{signature[0]} ({len(test_list)} duplicates)"
            duplicates[key] = test_ids
            
            if verbose:
                print(f"\n  Found duplicates for '{signature[0]}':")
                for test_id, name in zip(test_ids, test_names):
                    print(f"    - {test_id}: {name}")
    
    return duplicates


def deduplicate_tests(dry_run: bool = False, verbose: bool = False) -> None:
    """Main function to deduplicate tests.
    
    Fetches all tests, identifies duplicates, and deletes them (keeping one of each).
    
    Args:
        dry_run: If True, only show what would be deleted without actually deleting.
        verbose: Whether to print verbose output.
    """
    load_dotenv()
    
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not agent_id or not api_key:
        print("Error: ELEVENLABS_AGENT_ID and ELEVENLABS_API_KEY must be set")
        return
    
    tester = ElevenLabsAgentTester()
    
    # Fetch all tests
    all_tests = fetch_all_tests(tester)
    
    if not all_tests:
        print("No tests found.")
        return
    
    # Identify duplicates
    duplicates = identify_duplicates(tester, all_tests, verbose=verbose)
    
    if not duplicates:
        print("\n✓ No duplicates found. All tests are unique.")
        return
    
    # Summary
    total_duplicates = sum(len(test_ids) - 1 for test_ids in duplicates.values())
    print(f"\n{'='*80}")
    print(f"DUPLICATE DETECTION SUMMARY")
    print(f"{'='*80}")
    print(f"Found {len(duplicates)} groups of duplicates")
    print(f"Total duplicate tests to delete: {total_duplicates}")
    print(f"{'='*80}\n")
    
    # Show duplicates
    for key, test_ids in duplicates.items():
        print(f"\n{key}:")
        for i, test_id in enumerate(test_ids):
            # Keep the first one, delete the rest
            if i == 0:
                print(f"  ✓ KEEP: {test_id}")
            else:
                print(f"  ✗ DELETE: {test_id}")
    
    if dry_run:
        print(f"\n{'='*80}")
        print("DRY RUN MODE - No tests were deleted")
        print(f"{'='*80}")
        return
    
    # Confirm deletion
    print(f"\n{'='*80}")
    response = input(f"Delete {total_duplicates} duplicate test(s)? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("Cancelled.")
        return
    
    # Delete duplicates (keep first, delete rest)
    deleted_count = 0
    failed_count = 0
    
    print(f"\nDeleting duplicates...")
    for key, test_ids in duplicates.items():
        # Keep the first one, delete the rest
        for test_id in test_ids[1:]:
            try:
                tester.delete_test(test_id)
                deleted_count += 1
                if verbose:
                    print(f"  ✓ Deleted: {test_id}")
            except Exception as e:
                failed_count += 1
                print(f"  ✗ Failed to delete {test_id}: {e}")
    
    print(f"\n{'='*80}")
    print(f"DELETION SUMMARY")
    print(f"{'='*80}")
    print(f"Successfully deleted: {deleted_count}")
    if failed_count > 0:
        print(f"Failed to delete: {failed_count}")
    print(f"{'='*80}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deduplicate ElevenLabs Agent tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be deleted
  python -m tools.deduplicate_tests --dry-run
  
  # Actually delete duplicates
  python -m tools.deduplicate_tests
  
  # Verbose output
  python -m tools.deduplicate_tests --verbose
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    
    args = parser.parse_args()
    
    deduplicate_tests(dry_run=args.dry_run, verbose=args.verbose)

