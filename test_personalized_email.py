#!/usr/bin/env python3
"""
Test script for personalized HTML email generation.
"""

import sys
import os

# Add pipeline to path
sys.path.insert(0, 'pipeline')

def test_basic_functionality():
    """Test basic functionality without complex imports."""

    print("🎨 Testing basic HTML template functionality...")

    # Test template loading
    template_path = "pipeline/emails/templates/shortforge_email_cta.html"
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        print("✅ HTML template loaded successfully")
        print(f"📄 Template length: {len(template_content)} characters")

        # Check for placeholders
        placeholders = ["{{hero_title}}", "{{hero_subtitle}}", "{{company_name}}", "{{voice_agent_url}}"]
        found_placeholders = [p for p in placeholders if p in template_content]

        if found_placeholders:
            print(f"✅ Found placeholders: {found_placeholders}")
        else:
            print("⚠️  No placeholders found in template")
            return False

        # Test basic replacement
        test_replacements = {
            "{{hero_title}}": "Test Hero Title",
            "{{hero_subtitle}}": "Test subtitle",
            "{{company_name}}": "Test Company",
            "{{voice_agent_url}}": "https://test.com/agent"
        }

        test_html = template_content
        for placeholder, replacement in test_replacements.items():
            test_html = test_html.replace(placeholder, replacement)

        # Check if replacements worked
        remaining_placeholders = [p for p in placeholders if p in test_html]
        if remaining_placeholders:
            print(f"⚠️  Some placeholders not replaced: {remaining_placeholders}")
            return False
        else:
            print("✅ All basic replacements successful")

        # Save test output
        with open("test_basic_replacement.html", "w", encoding="utf-8") as f:
            f.write(test_html)

        print("✅ Test HTML saved to test_basic_replacement.html")
        return True

    else:
        print(f"❌ Template file not found: {template_path}")
        return False

if __name__ == "__main__":
    print("🧪 Starting basic email template tests...\n")

    try:
        success = test_basic_functionality()

        if success:
            print("\n🎉 Basic tests passed!")
        else:
            print("\n❌ Basic tests failed.")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)