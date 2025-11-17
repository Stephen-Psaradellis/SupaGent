#!/usr/bin/env python3
"""
Test script for Google Workspace integrations.
This script tests both Calendar and Sheets integration with your credentials.
"""

import os
import sys
from datetime import datetime, timedelta

def test_calendar_integration():
    """Test Google Calendar integration."""
    print("\n🔍 Testing Google Calendar Integration...")

    try:
        from integrations.google_calendar import GoogleCalendarClient

        # Set environment variables
        os.environ["GOOGLE_CALENDAR_CREDENTIALS_PATH"] = "credentials.json"
        os.environ["GOOGLE_CALENDAR_TOKEN_PATH"] = "calendar_token.json"

        print("📅 Initializing Google Calendar client...")
        client = GoogleCalendarClient()

        print("📅 Testing availability check...")
        # Test availability for next 7 days
        result = client.check_availability(
            time_min=datetime.now(),
            time_max=datetime.now() + timedelta(days=7),
            duration_minutes=30
        )

        print("✅ Calendar integration working!")
        print(f"   Found {result.get('summary', 'unknown')} available slots")

        return True

    except Exception as e:
        print(f"❌ Calendar test failed: {e}")
        return False

def test_sheets_integration():
    """Test Google Sheets integration."""
    print("\n📊 Testing Google Sheets Integration...")

    try:
        from integrations.google_sheets import GoogleSheetsClient

        # Set environment variables
        os.environ["GOOGLE_SHEETS_CREDENTIALS_PATH"] = "credentials.json"
        os.environ["GOOGLE_SHEETS_TOKEN_PATH"] = "sheets_token.json"
        # Note: You'll need to set GOOGLE_SHEETS_SPREADSHEET_ID for full functionality

        print("📊 Initializing Google Sheets client...")
        client = GoogleSheetsClient()

        print("✅ Sheets integration initialized!")
        print("   Note: Full functionality requires GOOGLE_SHEETS_SPREADSHEET_ID")

        return True

    except Exception as e:
        print(f"❌ Sheets test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Google Workspace Integration")
    print("=" * 50)

    # Check if credentials file exists
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found!")
        print("   Please ensure you have the OAuth credentials file.")
        return False

    print("✅ Found credentials.json")

    calendar_ok = test_calendar_integration()
    sheets_ok = test_sheets_integration()

    print("\n" + "=" * 50)
    print("📋 Test Results:")

    if calendar_ok:
        print("✅ Google Calendar: Ready")
    else:
        print("❌ Google Calendar: Failed")

    if sheets_ok:
        print("✅ Google Sheets: Ready")
    else:
        print("❌ Google Sheets: Failed")

    if calendar_ok and sheets_ok:
        print("\n🎉 All integrations are working!")
        print("\nNext steps:")
        print("1. Set these environment variables in your .env file:")
        print("   GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json")
        print("   GOOGLE_CALENDAR_TOKEN_PATH=calendar_token.json")
        print("   GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json")
        print("   GOOGLE_SHEETS_TOKEN_PATH=sheets_token.json")
        print("   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here")
        print("\n2. First run will open browser for OAuth authorization")
        print("3. Tokens will be saved automatically for future use")
    else:
        print("\n⚠️  Some integrations failed. Check the errors above.")

    return calendar_ok and sheets_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
