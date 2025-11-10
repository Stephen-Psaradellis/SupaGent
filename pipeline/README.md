# Growth Automation Pipeline

A complete lead generation flywheel that transforms your voice assistant technology into a growth engine. This pipeline generates qualified leads, scrapes business data, creates personalized voice agents, and sends targeted cold outreach emails.

## 🚀 Quick Start

```bash
# Generate leads only (safe)
python pipeline/auto_outreach.py --industry "dentists" --location "Chicago, IL" --leads-only

# Full pipeline (scraping, agents, emails - no sending)
python pipeline/auto_outreach.py --industry "dentists" --location "Chicago, IL"

# Full pipeline with email sending (CAUTION!)
python pipeline/auto_outreach.py --industry "dentists" --location "Chicago, IL" --send-emails
```

## 📁 Pipeline Architecture

```
pipeline/
├── auto_outreach.py          # Main pipeline orchestrator
├── lead_generation.py        # Multi-source lead discovery
├── business_intelligence.py  # Website scraping & vectorization
├── voice_agent_generator.py  # ElevenLabs agent creation
├── email_composer.py         # Personalized email templates
├── email_sender.py           # Transactional email sending
├── config/
│   ├── pipeline_config.json     # Pipeline settings
│   ├── email_templates/         # Email template configurations
│   └── agent_templates.json     # Voice agent configurations
├── leads/                    # Generated business leads
├── business_data/            # Scraped website content
├── agents/                   # Voice agent configurations
└── emails/                   # Composed email templates
```

## ⚙️ Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# ElevenLabs (for agent creation)
ELEVENLABS_API_KEY=your_api_key
ELEVENLABS_AGENT_ID=your_agent_id

# Email Provider (choose one)
RESEND_API_KEY=your_resend_key
MAILGUN_API_KEY=your_mailgun_key
BREVO_API_KEY=your_brevo_key

# Email Settings
FROM_EMAIL=noreply@yourdomain.com
FROM_NAME="AI Solutions"

# Sender Information
SENDER_NAME="Alex Johnson"
SENDER_TITLE="AI Solutions Specialist"
SENDER_COMPANY="VoiceGenius AI"
SENDER_EMAIL="alex@voicegenius.ai"
SENDER_PHONE="(555) 123-4567"
```

### Pipeline Configuration

Edit `pipeline/config/pipeline_config.json`:

```json
{
  "email_provider": "resend",
  "max_leads": 10,
  "max_pages_per_business": 50,
  "create_elevenlabs_agents": true,
  "send_emails": false,
  "use_llm_email_generation": true,
  "use_llm_agent_prompts": true,
  "batch_size": 10,
  "delay_seconds": 60
}
```

### LLM Configuration (Optional)

For AI-powered email generation, configure OpenRouter API:

**OpenRouter Config** (`pipeline/config/openrouter_config.json`):


### ElevenLabs System Prompt Configuration

The pipeline includes official ElevenLabs documentation that guides LLM system prompt generation:

**Key Documentation Areas:**
- **Voice Agent Best Practices**: Response structure, empathy, and natural conversation
- **System Prompt Structure**: Role definition, boundaries, and communication guidelines
- **Response Optimization**: Length limits, clarity, and spoken delivery optimization
- **Professional Standards**: Escalation paths, accuracy requirements, and brand consistency

**Automatic Integration:**
- Documentation is automatically included in LLM prompts for system prompt generation
- Ensures all generated prompts follow ElevenLabs official guidelines
- Fallback to template-based prompts if LLM generation fails

## 🎯 Supported Industries

Currently optimized for:
- **Dentists** - Patient scheduling, service information
- **Law Firms** - Client intake, consultation booking
- **HVAC** - Service scheduling, emergency response
- **Plumbers** - Emergency calls, service dispatch
- **Restaurants** - Reservations, menu information

Add new industries by editing `pipeline/config/agent_templates.json` and `pipeline/config/email_templates/templates.json`.

## 📊 Pipeline Stages

### 1. Lead Generation
Searches multiple sources:
- Google Maps
- Yelp
- LinkedIn
- Better Business Bureau

**Output:** `pipeline/leads/{industry}/{location}/*.json`

### 2. Business Intelligence
- Website scraping with sitemap discovery
- Content categorization (About, Services, Team, Blog)
- Vectorization into isolated namespaces (`kb:{domain}`)

**Output:** `pipeline/business_data/{domain}/`

### 3. Voice Agent Creation (ElevenLabs-Optimized)
- **Official Documentation Integration**: Uses comprehensive ElevenLabs documentation for system prompt creation
- **LLM-Generated Prompts**: Mistral Medium creates prompts following ElevenLabs best practices
- **Business-Specific Personalization**: Agents trained on scraped website content and services
- **Voice-First Design**: Prompts optimized for spoken delivery, not just text

**ElevenLabs Documentation Integration:**
- **Role Definition**: Clear, specific roles with business context
- **Communication Guidelines**: Personality, tone, and interaction styles
- **Response Best Practices**: Voice-optimized structure and empathy
- **Boundaries & Escalation**: Professional limitations and human handoff
- **Response Format**: Spoken delivery optimization (under 2 minutes)

**Features:**
- Real-time content analysis from business websites
- Industry-specific personality and tone optimization
- Automatic escalation path configuration
- Voice response length optimization
- Brand voice consistency enforcement

**Output:** `pipeline/agents/{domain}/agent.json` with LLM-generated system prompts

### 4. Email Composition (LLM-Powered)
- **AI-Generated Content**: Uses Mistral Medium via OpenRouter for intelligent email composition
- **Business Intelligence Integration**: Accesses scraped website data and agent configurations via MCP server
- **Contextual Personalization**: Deep understanding of business needs and industry pain points
- **Dynamic Value Propositions**: LLM generates tailored benefits based on business content
- **Fallback Templates**: Automatic fallback to static templates if LLM unavailable

**Features:**
- Real-time business intelligence search via MCP tools
- Industry-specific pain point identification
- Personalized value proposition generation
- Confidence scoring for email quality
- Professional formatting and compliance

**Output:** `pipeline/emails/{domain}.md` and `{domain}.json` with LLM metadata

### 5. Email Sending (Optional)
- Transactional API integration
- Open/click tracking
- Rate limiting and deliverability

**Output:** `pipeline/emails/status/email_status.jsonl`

## 🤖 MCP Server Integration

The pipeline integrates with your SupaGent MCP server to provide AI-powered business intelligence:

### New MCP Tools Added:
- **`search_business_intelligence`**: Search vectorized business data by domain and content type
- **`get_business_profile`**: Get comprehensive business intelligence summaries

### LLM Email Generation Flow:
1. **Business Intelligence Gathering**: LLM calls MCP tools to search business data
2. **Context Analysis**: Analyzes services, about content, team info, and industry insights
3. **Personalization**: Generates tailored value propositions based on business content
4. **Agent Awareness**: Understands voice agent personality, tone, and capabilities
5. **Email Composition**: Creates compelling, personalized cold outreach emails

### Benefits:
- **Real-time Intelligence**: Access to latest scraped business data
- **Contextual Understanding**: Deep comprehension of business needs
- **Dynamic Personalization**: Unique emails for each business
- **Industry Expertise**: Specialized knowledge of business pain points

## 🧪 Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/test_pipeline.py -v
```

Tests cover:
- Lead deduplication
- Content scraping and categorization
- Vector store namespace isolation
- Email template generation
- API integration mocking

## 📈 Usage Examples

### Generate Leads Only
```bash
python pipeline/auto_outreach.py \
  --industry "dentists" \
  --location "Chicago, IL" \
  --leads-only
```

### Process Existing Domains
```bash
echo -e "example1.com\nexample2.com" > domains.txt
python pipeline/auto_outreach.py \
  --domains-file domains.txt \
  --process-only
```

### Full Growth Flywheel
```bash
python pipeline/auto_outreach.py \
  --industry "hvac" \
  --location "Austin, TX" \
  --max-leads 25 \
  --send-emails
```

## 🔒 Safety Features

- **Email sending is disabled by default** - requires explicit `--send-emails` flag
- **Rate limiting** built into all API calls
- **Deduplication** prevents duplicate processing
- **Error handling** with graceful failures
- **Configuration validation** before execution

## 📊 Monitoring & Analytics

Track pipeline performance:
- Lead generation success rates
- Business processing completion
- Agent creation success
- Email delivery/open rates

Status tracking in `pipeline/emails/status/email_status.jsonl`

## 🚨 Important Notes

1. **Legal Compliance**: Ensure compliance with email regulations (CAN-SPAM, GDPR, etc.)
2. **Rate Limits**: Respect API limits and website terms of service
3. **Data Quality**: Review generated leads and content for accuracy
4. **Cost Management**: Monitor API usage costs for email and voice agents
5. **Backup**: Regular backups of generated data and configurations

## 🔧 Customization

### Adding New Industries
1. Add industry configuration to `agent_templates.json`
2. Add email templates to `email_templates/templates.json`
3. Test with small batches

### Custom Email Templates
Edit templates in `pipeline/config/email_templates/templates.json`

### Voice Agent Personalities
Modify personalities in `pipeline/config/agent_templates.json`

## 🐛 Troubleshooting

### Common Issues
- **No leads found**: Check location format and industry spelling
- **Scraping failures**: Verify website accessibility and robots.txt
- **Agent creation fails**: Check ElevenLabs API key and quota
- **Email sending fails**: Verify email provider configuration

### Debug Mode
```bash
python pipeline/auto_outreach.py --verbose [other args]
```

## 📚 API Reference

See individual module docstrings for detailed API documentation:
- `pipeline.lead_generation.LeadGenerator`
- `pipeline.business_intelligence.BusinessIntelligenceLoader`
- `pipeline.voice_agent_generator.VoiceAgentGenerator`
- `pipeline.email_composer.EmailComposer`
- `pipeline.email_sender.EmailSender`

---

**Built on SupaGent MCP + ElevenLabs Voice Agent technology** - transforming voice AI into a complete growth automation platform.
