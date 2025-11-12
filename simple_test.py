#!/usr/bin/env python3
"""
Simple test for HTML template replacement.
"""

import os

def main():
    template_path = 'pipeline/emails/templates/shortforge_email_cta.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print('✅ Template loaded successfully')

        # Test replacements
        replacements = {
            '{{hero_title}}': 'Test Hero Title',
            '{{hero_subtitle}}': 'Test subtitle about AI automation',
            '{{company_name}}': 'Test Dental Clinic',
            '{{voice_agent_url}}': 'https://test.com/agent',
            '{{pricing_title}}': 'Test Pricing',
            '{{pricing_subtitle}}': 'Test pricing subtitle',
            '{{urgency_title}}': 'Test Urgency',
            '{{urgency_text}}': 'Test urgency text'
        }

        test_html = content
        for placeholder, replacement in replacements.items():
            test_html = test_html.replace(placeholder, replacement)

        # Check for remaining placeholders
        import re
        remaining = re.findall(r'\{\{.*?\}\}', test_html)

        if remaining:
            print(f'⚠️  Remaining placeholders: {remaining}')
            return False
        else:
            print('✅ All placeholders replaced successfully')

        # Save test file
        with open('test_replacement.html', 'w', encoding='utf-8') as f:
            f.write(test_html)

        print('✅ Test HTML saved to test_replacement.html')
        print(f'📧 Final HTML length: {len(test_html)} characters')

        return True

    else:
        print('❌ Template file not found')
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print('\n🎉 Test passed!')
    else:
        print('\n❌ Test failed!')
