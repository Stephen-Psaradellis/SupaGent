#!/usr/bin/env python3
"""
Test script to verify the encryption key caching fix.

This script tests that encryption/decryption works correctly with the cached key.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.models import GoogleTokens


def test_encryption_consistency():
    """Test that encryption/decryption works consistently."""
    print("🔍 Testing encryption key caching fix...")

    # Clear any cached key from previous runs
    GoogleTokens._cached_encryption_key = None
    if hasattr(GoogleTokens, '_warned_about_key_generation'):
        delattr(GoogleTokens, '_warned_about_key_generation')

    # Create a GoogleTokens instance
    token_record = GoogleTokens(service_name="test")

    # Test data
    test_token = "test_access_token_12345"
    test_refresh_token = "test_refresh_token_67890"

    print("📝 Testing token encryption/decryption...")

    # Encrypt tokens
    encrypted_access = token_record.encrypt_token(test_token)
    encrypted_refresh = token_record.encrypt_token(test_refresh_token)

    print(f"✅ Encrypted access token: {encrypted_access[:20]}...")
    print(f"✅ Encrypted refresh token: {encrypted_refresh[:20]}...")

    # Decrypt tokens
    decrypted_access = token_record.decrypt_token(encrypted_access)
    decrypted_refresh = token_record.decrypt_token(encrypted_refresh)

    print(f"✅ Decrypted access token: {decrypted_access}")
    print(f"✅ Decrypted refresh token: {decrypted_refresh}")

    # Verify they match
    access_match = decrypted_access == test_token
    refresh_match = decrypted_refresh == test_refresh_token

    print(f"🔍 Access token match: {access_match}")
    print(f"🔍 Refresh token match: {refresh_match}")

    if access_match and refresh_match:
        print("🎉 SUCCESS: Encryption/decryption cycle works correctly!")
        return True
    else:
        print("❌ FAILURE: Encryption/decryption cycle broken!")
        return False


def test_key_caching():
    """Test that the same key is reused across multiple calls."""
    print("\n🔍 Testing key caching across multiple calls...")

    # Clear any cached key
    GoogleTokens._cached_encryption_key = None

    # Create multiple instances
    token_record1 = GoogleTokens(service_name="test1")
    token_record2 = GoogleTokens(service_name="test2")

    # Get keys from different instances
    key1 = GoogleTokens._get_encryption_key()
    key2 = GoogleTokens._get_encryption_key()

    keys_match = key1 == key2
    print(f"🔍 Keys are identical: {keys_match}")

    if keys_match:
        print("🎉 SUCCESS: Key caching works correctly!")
        return True
    else:
        print("❌ FAILURE: Key caching not working!")
        return False


def test_env_var_priority():
    """Test that environment variable takes priority over cached key."""
    print("\n🔍 Testing environment variable priority...")

    # Set environment variable
    test_key = "test_environment_key_12345"
    os.environ["GOOGLE_TOKEN_ENCRYPTION_KEY"] = test_key

    try:
        # Clear cached key to ensure env var is used
        GoogleTokens._cached_encryption_key = None

        # Get key - should use environment variable
        key = GoogleTokens._get_encryption_key()
        expected_key = test_key.encode()

        env_priority = key == expected_key
        print(f"🔍 Environment variable used: {env_priority}")

        if env_priority:
            print("🎉 SUCCESS: Environment variable takes priority!")
            return True
        else:
            print("❌ FAILURE: Environment variable not prioritized!")
            return False
    finally:
        # Clean up
        del os.environ["GOOGLE_TOKEN_ENCRYPTION_KEY"]


def main():
    """Main test function."""
    print("🚀 Testing Google OAuth Token Encryption Fix\n")

    # Run all tests
    test1 = test_encryption_consistency()
    test2 = test_key_caching()
    test3 = test_env_var_priority()

    print("\n📊 Test Results:")
    print(f"  Encryption Consistency: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Key Caching: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Environment Priority: {'✅ PASS' if test3 else '❌ FAIL'}")

    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! The encryption bug has been fixed.")
        return 0
    else:
        print("\n❌ Some tests failed. The encryption bug still exists.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
