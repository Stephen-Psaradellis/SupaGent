#!/usr/bin/env python3
"""
Railway Google Workspace Setup Script
Helps configure Google OAuth tokens for Railway deployment.
"""

import os
import json
import base64

def encode_token_file(filepath):
    """Encode a token file for Railway environment variable."""
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found")
        return None

    with open(filepath, 'r') as f:
        content = f.read().strip()

    # Base64 encode for safe transport
    encoded = base64.b64encode(content.encode()).decode()
    return encoded

def generate_railway_config():
    """Generate Railway environment variable configuration."""
    print("🚂 Railway Google Workspace Configuration")
    print("=" * 50)

    # Check credentials
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("   Please ensure you have your OAuth credentials file.")
        return

    print("✅ Found credentials.json")

    # Check tokens
    calendar_token = encode_token_file('calendar_token.json')
    sheets_token = encode_token_file('sheets_token.json')

    print("\n📋 Railway Environment Variables to Set:")
    print("-" * 40)

    # Always include credentials path
    print("GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json")
    print("GOOGLE_SHEETS_CREDENTIALS_PATH=credentials.json")

    # Include tokens if they exist
    if calendar_token:
        print(f"GOOGLE_CALENDAR_TOKEN_B64={calendar_token}")
        print("GOOGLE_CALENDAR_TOKEN_PATH=calendar_token.json")

    if sheets_token:
        print(f"GOOGLE_SHEETS_TOKEN_B64={sheets_token}")
        print("GOOGLE_SHEETS_TOKEN_PATH=sheets_token.json")
        print("GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here")

    print("\n📝 Instructions:")
    print("1. Copy the variables above to your Railway environment")
    print("2. For Railway, use the B64 versions of tokens")
    print("3. Add your Google Sheets spreadsheet ID")
    print("4. Upload credentials.json to Railway via the Files tab")

    if not calendar_token or not sheets_token:
        print("\n⚠️  Warning: Token files not found!")
        print("   Generate them locally first by running:")
        print("   python test_google_readonly.py")
        print("   Then run this script again.")

def generate_railway_files():
    """Generate files for Railway upload."""
    print("\n📁 Files to upload to Railway:")
    print("-" * 30)

    files_to_upload = ['credentials.json']

    if os.path.exists('calendar_token.json'):
        files_to_upload.append('calendar_token.json')

    if os.path.exists('sheets_token.json'):
        files_to_upload.append('sheets_token.json')

    for file in files_to_upload:
        print(f"✅ {file}")

    print("\n📤 Upload these files to Railway via:")
    print("   Railway Dashboard → Your Service → Files tab")

if __name__ == "__main__":
    generate_railway_config()
    generate_railway_files()
