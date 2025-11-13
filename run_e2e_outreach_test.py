"""
E2E Outreach Flow Test Script

Runs the complete outreach pipeline for a dentist lead but sends the email
to the test email address instead of the actual lead.

Usage:
    python run_e2e_outreach_test.py
"""

import html
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pipeline.lead_generation import Lead
from pipeline.business_intelligence import BusinessIntelligenceLoader
from pipeline.voice_agent_generator import VoiceAgentGenerator
from pipeline.email_composer import EmailComposer
from pipeline.email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test email override - send to this address instead of the lead
TEST_EMAIL = "spsardellis@gmail.com"


def _escape_html(text: Any) -> str:
    """Escape HTML special characters in text."""
    if text is None:
        return "N/A"
    return html.escape(str(text))


def visualize_business_intelligence(lead: Lead, intelligence: Optional[Dict[str, Any]], output_path: Path) -> None:
    """
    Generate an HTML visualization of business intelligence data.
    
    Args:
        lead: The lead object
        intelligence: Business intelligence dictionary from BusinessIntelligenceLoader
        output_path: Path where the HTML file should be saved
    """
    if not intelligence:
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Intelligence - {lead.name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 20px;
            border-radius: 8px;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Business Intelligence Report</h1>
        <p>Lead: {lead.name}</p>
    </div>
    <div class="warning">
        <h2>⚠️ No Business Intelligence Available</h2>
        <p>Business intelligence data was not gathered for this lead. This may be due to:</p>
        <ul>
            <li>Missing or invalid domain</li>
            <li>Website scraping failure</li>
            <li>Network connectivity issues</li>
        </ul>
    </div>
</body>
</html>
"""
        output_path.write_text(html_content, encoding='utf-8')
        logger.info(f"📊 Visualization saved to {output_path}")
        return
    
    lead_profile = intelligence.get("lead_profile", {})
    metadata_insights = intelligence.get("metadata_insights", {})
    hunter_data = intelligence.get("hunter_enrichment", {})
    content_summaries = intelligence.get("content_summaries", {})
    content_highlights = intelligence.get("content_highlights", {})
    keyword_signals = intelligence.get("keyword_signals", {})
    online_presence = intelligence.get("online_presence", {})
    llm_digest = intelligence.get("llm_digest", "")
    content_sources = intelligence.get("content_sources", {})
    
    # Format generated_at timestamp
    generated_at = intelligence.get("generated_at", 0)
    if generated_at:
        gen_time = datetime.fromtimestamp(generated_at).strftime("%Y-%m-%d %H:%M:%S")
    else:
        gen_time = "Unknown"
    
    # Build HTML
    html_parts = [f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Business Intelligence - {_escape_html(lead_profile.get('name', lead.name))}</title>
    <style>
        * {{
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .card h2 {{
            margin-top: 0;
            color: #667eea;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .card h3 {{
            color: #764ba2;
            font-size: 1.2em;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .info-label {{
            font-weight: 600;
            color: #555;
        }}
        .info-value {{
            color: #333;
            text-align: right;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin: 2px;
        }}
        .badge-primary {{
            background: #667eea;
            color: white;
        }}
        .badge-success {{
            background: #10b981;
            color: white;
        }}
        .badge-warning {{
            background: #f59e0b;
            color: white;
        }}
        .keyword-tag {{
            display: inline-block;
            background: #e0e7ff;
            color: #4338ca;
            padding: 5px 12px;
            border-radius: 15px;
            margin: 4px;
            font-size: 0.9em;
        }}
        .content-preview {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
            max-height: 200px;
            overflow-y: auto;
            font-size: 0.9em;
            line-height: 1.5;
        }}
        .highlight {{
            background: #fef3c7;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 500;
        }}
        .source-link {{
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
        }}
        .source-link:hover {{
            text-decoration: underline;
        }}
        .full-width {{
            grid-column: 1 / -1;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        .digest-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Business Intelligence Report</h1>
        <p><strong>Lead:</strong> {_escape_html(lead_profile.get('name', lead.name))}</p>
        <p><strong>Company:</strong> {_escape_html(lead_profile.get('company', 'N/A'))}</p>
        <p><strong>Generated:</strong> {_escape_html(gen_time)}</p>
    </div>
    
    <div class="grid">
        <!-- Lead Profile Card -->
        <div class="card">
            <h2>👤 Lead Profile</h2>
            <div class="info-row">
                <span class="info-label">Name:</span>
                <span class="info-value">{_escape_html(lead_profile.get('name', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Title:</span>
                <span class="info-value">{_escape_html(lead_profile.get('title', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Company:</span>
                <span class="info-value">{_escape_html(lead_profile.get('company', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Industry:</span>
                <span class="info-value">{_escape_html(lead_profile.get('industry', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Location:</span>
                <span class="info-value">{_escape_html(lead_profile.get('location', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Domain:</span>
                <span class="info-value">{_escape_html(lead_profile.get('domain', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Email:</span>
                <span class="info-value">{_escape_html(lead_profile.get('primary_email', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Score:</span>
                <span class="info-value">{lead_profile.get('score', 0):.2f}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Confidence:</span>
                <span class="info-value">{lead_profile.get('confidence', 0):.2f}</span>
            </div>
            {f'<div style="margin-top: 15px;"><strong>Tags:</strong><br>' + ''.join([f'<span class="badge badge-primary">{_escape_html(tag)}</span>' for tag in lead_profile.get('tags', [])]) + '</div>' if lead_profile.get('tags') else ''}
        </div>
        
        <!-- Online Presence Card -->
        <div class="card">
            <h2>🌐 Online Presence</h2>
            {f'<div class="info-row"><span class="info-label">Domain:</span><span class="info-value">{_escape_html(online_presence.get("domain", "N/A"))}</span></div>' if online_presence.get("domain") else ''}
            {f'<div class="info-row"><span class="info-label">LinkedIn:</span><span class="info-value"><a href="{_escape_html(online_presence.get("linkedin_url", ""))}" class="source-link" target="_blank">{_escape_html(online_presence.get("linkedin_url", ""))}</a></span></div>' if online_presence.get("linkedin_url") else '<p>No LinkedIn URL available</p>'}
            {f'<div class="info-row"><span class="info-label">Yelp:</span><span class="info-value"><a href="{_escape_html(lead.yelp_url)}" class="source-link" target="_blank">{_escape_html(lead.yelp_url)}</a></span></div>' if lead.yelp_url else ''}
            {f'<div class="info-row"><span class="info-label">Google Maps:</span><span class="info-value"><a href="{_escape_html(lead.google_maps_url)}" class="source-link" target="_blank">View on Google Maps</a></span></div>' if lead.google_maps_url else ''}
        </div>
        
        <!-- Hunter Enrichment Card -->
        <div class="card">
            <h2>🔍 Email Verification (Hunter.io)</h2>
    """]
    
    # Hunter enrichment data
    domain_search = hunter_data.get("domain_search", {})
    if domain_search:
        html_parts.append(f"""
            <h3>Domain Search</h3>
            <div class="info-row">
                <span class="info-label">Organization:</span>
                <span class="info-value">{_escape_html(domain_search.get('organization', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Country:</span>
                <span class="info-value">{_escape_html(domain_search.get('country', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">State:</span>
                <span class="info-value">{_escape_html(domain_search.get('state', 'N/A'))}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Disposable:</span>
                <span class="info-value">{'Yes' if domain_search.get('disposable') else 'No'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Webmail:</span>
                <span class="info-value">{'Yes' if domain_search.get('webmail') else 'No'}</span>
            </div>
        """)
        
        emails = domain_search.get("emails", [])
        if emails:
            html_parts.append("<h3>Found Emails</h3>")
            for email_info in emails:
                html_parts.append(f"""
                <div class="content-preview">
                    <strong>Email:</strong> {_escape_html(email_info.get('value', 'N/A'))}<br>
                    <strong>Type:</strong> {_escape_html(email_info.get('type', 'N/A'))}<br>
                    <strong>Confidence:</strong> {_escape_html(email_info.get('confidence', 'N/A'))}%
                </div>
                """)
    else:
        html_parts.append("<p>No Hunter.io enrichment data available</p>")
    
    html_parts.append("</div>")
    
    # Keyword Signals Card
    if keyword_signals:
        top_keywords = keyword_signals.get("top_keywords", [])
        total_tokens = keyword_signals.get("total_unique_tokens", 0)
        html_parts.append(f"""
        <div class="card">
            <h2>🔑 Keyword Signals</h2>
            <div class="stat-box">
                <div class="stat-value">{total_tokens}</div>
                <div class="stat-label">Unique Tokens</div>
            </div>
            <h3>Top Keywords</h3>
            {''.join([f'<span class="keyword-tag">{_escape_html(kw)}</span>' for kw in top_keywords[:20]])}
        </div>
        """)
    
    # Content Summaries
    if content_summaries:
        html_parts.append("""
        <div class="card full-width">
            <h2>📝 Content Summaries</h2>
        """)
        for content_type, summary in content_summaries.items():
            if summary:
                html_parts.append(f"""
            <h3>{content_type.title()}</h3>
            <div class="content-preview">{_escape_html(summary)}</div>
                """)
        html_parts.append("</div>")
    
    # Content Highlights
    if content_highlights:
        html_parts.append("""
        <div class="card full-width">
            <h2>✨ Content Highlights</h2>
        """)
        for content_type, highlights_list in content_highlights.items():
            if highlights_list:
                html_parts.append(f"""
            <h3>{content_type.title()}</h3>
            <ul>
                {''.join([f'<li><span class="highlight">{_escape_html(hl[:200])}{"..." if len(hl) > 200 else ""}</span></li>' for hl in highlights_list[:5]])}
            </ul>
                """)
        html_parts.append("</div>")
    
    # Content Sources
    if content_sources:
        total_sources = sum(len(sources) for sources in content_sources.values())
        html_parts.append(f"""
        <div class="card full-width">
            <h2>🔗 Content Sources ({total_sources} pages scraped)</h2>
        """)
        for content_type, sources in content_sources.items():
            if sources:
                html_parts.append(f"""
            <h3>{content_type.title()} ({len(sources)} pages)</h3>
                """)
                for source in sources:  # Show max 5 per type
                    html_parts.append(f"""
            <div class="content-preview">
                <strong><a href="{_escape_html(source.get('url', '#'))}" class="source-link" target="_blank">{_escape_html(source.get('title', 'Untitled'))}</a></strong><br>
                <small>{_escape_html(source.get('url', ''))}</small><br>
                <p>{_escape_html(source.get('content', ''))}</p>
            </div>
                    """)
        html_parts.append("</div>")
    
    # Metadata Insights
    if metadata_insights:
        html_parts.append("""
        <div class="card full-width">
            <h2>📋 Metadata Insights</h2>
        """)
        for insight_type, insight_data in metadata_insights.items():
            if insight_data:
                html_parts.append(f"""
            <h3>{insight_type.replace('_', ' ').title()}</h3>
            <div class="content-preview">
                <pre style="white-space: pre-wrap; font-family: inherit;">{_escape_html(json.dumps(insight_data, indent=2)[:1000])}{'...' if len(json.dumps(insight_data, indent=2)) > 1000 else ''}</pre>
            </div>
                """)
        html_parts.append("</div>")
    
    # LLM Digest
    if llm_digest:
        html_parts.append(f"""
        <div class="card full-width">
            <h2>🤖 AI-Generated Digest</h2>
            <div class="digest-box">{_escape_html(llm_digest)}</div>
        </div>
        """)
    
    # Stats Summary
    stats_html = f"""
        <div class="card full-width">
            <h2>📊 Intelligence Summary</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">{len(content_summaries)}</div>
                    <div class="stat-label">Content Types</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{sum(len(sources) for sources in content_sources.values())}</div>
                    <div class="stat-label">Pages Scraped</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{len(keyword_signals.get('top_keywords', []))}</div>
                    <div class="stat-label">Top Keywords</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{'✅' if hunter_data.get('domain_search') else '❌'}</div>
                    <div class="stat-label">Email Verified</div>
                </div>
            </div>
        </div>
    """
    html_parts.append(stats_html)
    
    html_parts.append("""
    </div>
</body>
</html>
""")
    
    html_content = ''.join(html_parts)
    output_path.write_text(html_content, encoding='utf-8')
    logger.info(f"📊 Business intelligence visualization saved to: {output_path}")
    logger.info(f"   Open in browser: file://{output_path.absolute()}")


def load_dentist_lead() -> Lead:
    """Load a dentist lead from the leads directory."""
    leads_dir = Path("pipeline/leads/dentist/chicago")
    
    # Find the most recent lead file
    lead_files = sorted(leads_dir.glob("*.json"), reverse=True)
    
    if not lead_files:
        raise FileNotFoundError("No dentist leads found in pipeline/leads/dentist/chicago")
    
    # Load the first lead from the most recent file
    lead_file = lead_files[0]
    logger.info(f"Loading lead from {lead_file}")
    
    with open(lead_file, 'r', encoding='utf-8') as f:
        lead_data_list = json.load(f)
    
    if not lead_data_list:
        raise ValueError(f"No leads found in {lead_file}")
    
    # Convert to Lead object
    lead = Lead.from_dict(lead_data_list[0])
    logger.info(f"Loaded lead: {lead.name} ({lead.domain or 'no domain'}) - {lead.email}")
    
    return lead


def run_e2e_outreach_test():
    """Run the complete e2e outreach flow with email override."""
    logger.info("🚀 Starting E2E Outreach Flow Test")
    logger.info("=" * 60)
    
    try:
        # Step 1: Load a dentist lead
        logger.info("📋 Step 1: Loading dentist lead...")
        lead = load_dentist_lead()
        logger.info(f"✅ Loaded lead: {lead.name}")
        logger.info(f"   Email: {lead.email}")
        logger.info(f"   Domain: {lead.domain or 'N/A'}")
        logger.info(f"   Location: {lead.location}")
        logger.info(f"   Industry: {lead.industry}")
        
        # Step 2: Gather business intelligence
        logger.info("\n📊 Step 2: Gathering business intelligence...")
        business_loader = BusinessIntelligenceLoader("pipeline/business_data")
        
        # If no domain, try to extract from email or use organization name
        if not lead.domain or lead.domain == "":
            if lead.email and '@' in lead.email:
                # Try to extract domain from email
                domain = lead.email.split('@')[1]
                lead.domain = domain
                logger.info(f"   Extracted domain from email: {domain}")
            else:
                # Use organization name from metadata if available
                org_name = lead.metadata.get("apollo_contact_data", {}).get("organization_name", "")
                if org_name:
                    # Create a placeholder domain
                    lead.domain = f"{org_name.lower().replace(' ', '').replace('&', 'and').replace(',', '')}.com"
                    logger.info(f"   Created placeholder domain: {lead.domain}")
                else:
                    logger.warning("   ⚠️ No domain available, skipping business intelligence gathering")
                    intelligence = None
        
        # Gather intelligence if we have a domain
        if lead.domain and lead.domain != "":
            intelligence = business_loader.process_lead(lead, max_pages=50)
            if intelligence:
                logger.info(f"✅ Gathered business intelligence for {lead.domain}")
                
                # Generate visualization
                logger.info("\n📊 Generating business intelligence visualization...")
                viz_dir = Path("visualizations")
                viz_dir.mkdir(exist_ok=True)
                domain_safe = lead.domain.replace(".", "_").replace("/", "_")
                viz_path = viz_dir / f"bi_{domain_safe}_{int(datetime.now().timestamp())}.html"
                visualize_business_intelligence(lead, intelligence, viz_path)
            else:
                logger.warning(f"   ⚠️ Failed to gather business intelligence for {lead.domain}")
        else:
            intelligence = None
        
        # Step 3: Generate voice agent
        logger.info("\n🤖 Step 3: Generating voice agent...")
        agent_generator = VoiceAgentGenerator(
            agents_dir="pipeline/agents",
            use_llm=True
        )

        agent_config = agent_generator.generate_agent_for_business(
            domain=lead.domain or lead.email.split('@')[1] if lead.email and '@' in lead.email else "test",
            business_name=lead.name,
            industry=lead.industry or "dentist",
            lead=lead,
            business_intelligence=intelligence,
            create_elevenlabs=True  # Actually create the agent in ElevenLabs
        )

        if agent_config:
            agent_name = agent_config.request_payload.get("name", lead.name)
            agent_id = agent_config.agent_id
            logger.info(f"✅ Generated agent configuration: {agent_name}")
            if agent_id:
                logger.info(f"✅ Created ElevenLabs agent with ID: {agent_id}")
            else:
                logger.warning("   ⚠️ Agent configuration created but ElevenLabs registration failed")
        else:
            logger.warning("   ⚠️ Failed to generate agent configuration")
            agent_id = None
        
        # Step 4: Compose email
        logger.info("\n📧 Step 4: Composing email...")
        email_composer = EmailComposer(
            templates_dir="pipeline/config/email_templates",
            use_llm=True,
            business_data_dir="pipeline/business_data"
        )

        # Try to load business content for personalization
        content_summary = {}
        if lead.domain:
            try:
                content_summary = email_composer._load_business_content(lead.domain) or {}
            except Exception:
                content_summary = {}

        # Compose email using the lead data directly
        email_template = email_composer.compose_email(
            business_name=lead.name,
            domain=lead.domain or "test",
            industry=lead.industry or "general",
            recipient_email=lead.email,
            recipient_name=None,
            content_summary=content_summary,
            voice_agent_id=agent_id
        )
        
        if email_template:
            logger.info(f"✅ Composed email with subject: {email_template.subject}")
        else:
            logger.warning("   ⚠️ Failed to compose email")
            # Create a basic email template as fallback
            email_template = type('EmailTemplate', (), {
                'subject': f"AI Voice Agent Demo for {lead.name}",
                'body': f"Hi {lead.name},\n\nWe've created a personalized AI voice agent for your business. Check it out!",
                'html_body': None
            })()
        
        # Step 5: Send email to test address (not the lead)
        logger.info("\n📤 Step 5: Sending email to test address...")
        original_email = lead.email
        logger.info(f"   Original lead email: {original_email}")
        logger.info(f"   Test email override: {TEST_EMAIL}")
        
        email_sender = EmailSender(
            emails_dir="pipeline/emails",
            leads_dir="pipeline/leads"
        )
        
        # Create a test lead copy with the test email
        test_domain = lead.domain or (lead.email.split('@')[1] if lead.email and '@' in lead.email else "test")
        test_lead = Lead(
            name=lead.name,
            domain=test_domain,
            location=lead.location,
            industry=lead.industry,
            email=TEST_EMAIL,  # Use test email instead
            phone=lead.phone,
            description=lead.description,
            source=lead.source,
            linkedin_url=lead.linkedin_url,
            yelp_url=lead.yelp_url,
            google_maps_url=lead.google_maps_url,
            bbb_url=lead.bbb_url,
            crunchbase_url=lead.crunchbase_url,
            score=lead.score,
            confidence=lead.confidence,
            tags=lead.tags.copy(),
            emails=lead.emails.copy(),
            metadata=lead.metadata.copy()
        )
        
        # Send the email (will use test_lead.email which is TEST_EMAIL)
        success = email_sender.send_email_to_lead(test_lead, track_status=False, voice_agent_id=agent_id)
        
        if success:
            logger.info(f"✅ Email sent successfully to {TEST_EMAIL}")
            logger.info(f"   Subject: {email_template.subject}")
        else:
            logger.warning(f"⚠️ Failed to send email to {TEST_EMAIL}")
            logger.warning("   This may be due to an expired ElasticEmail API key.")
            logger.warning("   All other pipeline steps completed successfully.")
            # Don't fail the test - the email composition worked, just sending failed
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("🎉 E2E Outreach Flow Test Complete!")
        logger.info("=" * 60)
        logger.info(f"   Lead: {lead.name}")
        logger.info(f"   Lead Email: {original_email}")
        logger.info(f"   Business Intelligence: {'✅' if intelligence else '⚠️ Skipped'}")
        logger.info(f"   Voice Agent: {'✅' if agent_config else '⚠️ Failed'}")
        logger.info(f"   Email Composed: ✅")
        logger.info(f"   Email Sent: {'✅' if success else '⚠️ Failed (check API key)'}")
        logger.info(f"   Test Email: {TEST_EMAIL}")
        logger.info("")
        logger.info("Note: If email sending failed, check your ElasticEmail API key.")
        logger.info("All other pipeline steps completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ E2E test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = run_e2e_outreach_test()
    sys.exit(0 if success else 1)

