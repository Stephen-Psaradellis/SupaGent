#!/usr/bin/env python3
"""
Test Google Workspace integrations with read-only scopes.
These scopes don't require verification and should work immediately.
"""

import os
import sys
from datetime import datetime, timedelta

# Use read-only scopes that don't require verification
CALENDAR_READONLY_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
SHEETS_READONLY_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def test_readonly_calendar():
    """Test Google Calendar with read-only scope."""
    print("\n📅 Testing Google Calendar (Read-Only)...")

    try:
        # Temporarily modify the scopes
        import integrations.google_calendar
        original_scopes = integrations.google_calendar.SCOPES
        integrations.google_calendar.SCOPES = CALENDAR_READONLY_SCOPES

        from integrations.google_calendar import GoogleCalendarClient

        # Set environment variables
        os.environ["GOOGLE_CALENDAR_CREDENTIALS_PATH"] = "credentials.json"
        os.environ["GOOGLE_CALENDAR_TOKEN_PATH"] = "calendar_readonly_token.json"

        print("📅 Initializing Google Calendar client (read-only)...")
        client = GoogleCalendarClient()

        print("📅 Testing calendar access...")
        # Test getting bookings (read-only operation)
        result = client.get_user_bookings(
            time_min=datetime.now(),
            time_max=datetime.now() + timedelta(days=7),
            max_results=5
        )

        print("✅ Calendar read-only integration working!")
        print(f"   Found {result.get('count', 0)} recent bookings")

        # Restore original scopes
        integrations.google_calendar.SCOPES = original_scopes

        return True

    except Exception as e:
        print(f"❌ Calendar read-only test failed: {e}")
        return False

def test_readonly_sheets():
    """Test Google Sheets with read-only scope."""
    print("\n📊 Testing Google Sheets (Read-Only)...")

    try:
        # Temporarily modify the scopes
        import integrations.google_sheets
        original_scopes = integrations.google_sheets.SCOPES
        integrations.google_sheets.SCOPES = SHEETS_READONLY_SCOPES

        from integrations.google_sheets import GoogleSheetsClient

        # Set environment variables
        os.environ["GOOGLE_SHEETS_CREDENTIALS_PATH"] = "credentials.json"
        os.environ["GOOGLE_SHEETS_TOKEN_PATH"] = "sheets_readonly_token.json"

        print("📊 Initializing Google Sheets client (read-only)...")
        client = GoogleSheetsClient()

        print("✅ Sheets read-only integration initialized!")
        print("   Note: Full functionality requires GOOGLE_SHEETS_SPREADSHEET_ID and write permissions")

        # Restore original scopes
        integrations.google_sheets.SCOPES = original_scopes

        return True

    except Exception as e:
        print(f"❌ Sheets read-only test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing Google Workspace Integration (Read-Only)")
    print("=" * 60)

    # Check if credentials file exists
    if not os.path.exists("credentials.json"):
        print("❌ credentials.json not found!")
        return False

    print("✅ Found credentials.json")

    calendar_ok = test_readonly_calendar()
    sheets_ok = test_readonly_sheets()

    print("\n" + "=" * 60)
    print("📋 Read-Only Test Results:")

    if calendar_ok:
        print("✅ Google Calendar (Read-Only): Working")
    else:
        print("❌ Google Calendar (Read-Only): Failed")

    if sheets_ok:
        print("✅ Google Sheets (Read-Only): Working")
    else:
        print("❌ Google Sheets (Read-Only): Failed")

    print("\n📝 Next Steps for Full Access:")
    print("1. To use write permissions, you'll need to:")
    print("   - Complete Google's OAuth verification process")
    print("   - Or use read-only operations only")
    print("   - Or create a new project with different scopes")

    print("\n🔗 OAuth Verification Process:")
    print("   https://support.google.com/cloud/answer/9110914")

    return calendar_ok and sheets_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
