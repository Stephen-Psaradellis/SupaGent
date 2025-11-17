#!/usr/bin/env python3
"""
Test script to verify the encryption validation fix.

This script tests that empty tokens are properly rejected and don't cause IntegrityError.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import GoogleTokens


def test_empty_token_validation():
    """Test that empty tokens are properly rejected."""
    print("🔍 Testing empty token validation...")

    # Create a GoogleTokens instance
    token_record = GoogleTokens(service_name="test")

    # Test empty string
    try:
        token_record.set_access_token("")
        print("❌ FAILED: Empty string should be rejected")
        return False
    except ValueError as e:
        print(f"✅ PASS: Empty string rejected - {e}")

    # Test None
    try:
        token_record.set_access_token(None)
        print("❌ FAILED: None should be rejected")
        return False
    except (ValueError, TypeError) as e:
        print(f"✅ PASS: None rejected - {e}")

    # Test valid token
    try:
        token_record.set_access_token("valid_token_123")
        print("✅ PASS: Valid token accepted")
    except Exception as e:
        print(f"❌ FAILED: Valid token rejected - {e}")
        return False

    return True


def test_refresh_token_handling():
    """Test that refresh tokens handle empty values correctly."""
    print("\n🔍 Testing refresh token handling...")

    token_record = GoogleTokens(service_name="test")

    # Test setting None refresh token (should be allowed)
    try:
        token_record.set_refresh_token(None)
        print("✅ PASS: None refresh token accepted")
    except Exception as e:
        print(f"❌ FAILED: None refresh token rejected - {e}")
        return False

    # Test setting empty string refresh token (should be allowed)
    try:
        token_record.set_refresh_token("")
        print("✅ PASS: Empty string refresh token accepted")
    except Exception as e:
        print(f"❌ FAILED: Empty string refresh token rejected - {e}")
        return False

    # Test setting valid refresh token
    try:
        token_record.set_refresh_token("valid_refresh_token_456")
        print("✅ PASS: Valid refresh token accepted")
    except Exception as e:
        print(f"❌ FAILED: Valid refresh token rejected - {e}")
        return False

    return True


def test_encrypt_decrypt_cycle():
    """Test that valid tokens encrypt/decrypt correctly."""
    print("\n🔍 Testing encrypt/decrypt cycle...")

    token_record = GoogleTokens(service_name="test")

    test_token = "test_access_token_789"

    # Set and get should work
    try:
        token_record.set_access_token(test_token)
        retrieved_token = token_record.get_access_token()

        if retrieved_token == test_token:
            print("✅ PASS: Encrypt/decrypt cycle works correctly")
            return True
        else:
            print(f"❌ FAILED: Token mismatch - expected '{test_token}', got '{retrieved_token}'")
            return False
    except Exception as e:
        print(f"❌ FAILED: Encrypt/decrypt cycle failed - {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Testing Encryption Validation Fix\n")

    # Run all tests
    test1 = test_empty_token_validation()
    test2 = test_refresh_token_handling()
    test3 = test_encrypt_decrypt_cycle()

    print("\n📊 Test Results:")
    print(f"  Empty Token Validation: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Refresh Token Handling: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Encrypt/Decrypt Cycle: {'✅ PASS' if test3 else '❌ FAIL'}")

    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! The encryption validation bug has been fixed.")
        return 0
    else:
        print("\n❌ Some tests failed. The encryption validation bug still exists.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
