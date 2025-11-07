Feature: CRM/Ticketing System Integration
  As a support operations manager
  I want the voice agent to integrate with our CRM/ticketing system
  So that all customer interactions are tracked, escalated properly, and agents have full context

  Background:
    Given the system is configured with CRM/ticketing system credentials
    And customer data exists in the CRM system
    And the voice agent is processing conversations

  Scenario: Create ticket for escalated conversation
    Given a conversation has been flagged for escalation
    When the system creates an escalation ticket
    Then a ticket should be created in the integrated system with:
      | Field | Source |
      | Title | "Voice Agent Escalation: [Query Summary]" |
      | Description | Full conversation transcript and context |
      | Customer | Linked to CRM customer record if available |
      | Priority | Based on escalation reason and customer tier |
      | Category | "Voice Agent Escalation" or configured category |
      | Attachments | Retrieved documents, conversation metadata |
      | Tags | "voice-agent", escalation reason, query topic |
    And the ticket should be:
      | Requirement | Description |
      | Searchable | Findable by customer, session ID, or query text |
      | Assignable | Can be assigned to specific agent or queue |
      | Trackable | Status updates sync between systems |
      | Auditable | Full history of creation and updates |

  Scenario: Sync customer data from CRM
    Given a user is interacting with the voice agent
    When the system identifies the customer (via phone number, email, or account ID)
    Then the system should:
      | Action | Description |
      | Query CRM | Look up customer record in integrated system |
      | Load customer context | Retrieve account status, past tickets, preferences |
      | Personalize responses | Use customer name, account details in answers |
      | Log interaction | Record voice agent interaction in CRM activity log |
    And customer data should include:
      | Information | Description |
      | Account status | Active, suspended, premium, etc. |
      | Past interactions | Previous tickets and resolutions |
      | Product subscriptions | What products/services customer has |
      | Preferences | Language, communication preferences |
      | Support tier | Standard, premium, enterprise support level |
    And if customer is not found:
      | Action | Description |
      | Create prospect record | If configured, create new CRM record |
      | Use anonymous mode | Continue without customer context |
      | Flag for review | Mark interaction for customer data team |

  Scenario: Log all interactions in CRM
    Given a conversation is occurring with the voice agent
    When the conversation completes or escalates
    Then an activity log entry should be created in CRM with:
      | Field | Description |
      | Activity type | "Voice Agent Interaction" |
      | Customer | Linked customer record |
      | Timestamp | Start and end time of conversation |
      | Duration | Total conversation length |
      | Query summary | Main topics discussed |
      | Resolution status | Resolved, escalated, or unresolved |
      | Transcript | Full conversation transcript (if configured) |
      | Metadata | Session ID, confidence scores, retrieved documents |
    And the log entry should be:
      | Requirement | Description |
      | Visible in customer timeline | Appears in CRM customer activity feed |
      | Searchable | Findable by date, topic, or customer |
      | Exportable | Can be included in reports |
      | Compliant | Follows data retention and privacy policies |

  Scenario: Agent handoff with full context
    Given a conversation has been escalated
    And a ticket has been created in the CRM system
    When a human agent opens the ticket
    Then the agent should see:
      | Information | Description |
      | Voice agent transcript | Full conversation with voice agent |
      | Customer CRM record | Complete customer profile and history |
      | Retrieved documents | Knowledge base articles referenced |
      | Suggested responses | AI-generated response suggestions |
      | Escalation reason | Why conversation was escalated |
      | Customer context | Account status, past tickets, preferences |
    And the agent should be able to:
      | Action | Description |
      | Continue conversation | Respond directly from ticket interface |
      | Update customer record | Add notes or update customer information |
      | Link related tickets | Connect to other customer issues |
      | Resolve and close | Mark ticket resolved with resolution notes |
      | Re-open voice agent | Transfer back to voice agent if appropriate |

  Scenario: Bidirectional sync between systems
    Given the voice agent and CRM are integrated
    When changes occur in either system
    Then updates should sync:
      | Change Type | Sync Direction | Description |
      | Ticket status update | CRM → Voice Agent | Voice agent session status updates |
      | Customer data update | CRM → Voice Agent | Customer context refreshes |
      | Voice agent escalation | Voice Agent → CRM | Ticket created in CRM |
      | Interaction logging | Voice Agent → CRM | Activity logged in CRM |
      | Resolution notes | CRM → Voice Agent | Used to improve future responses |
    And sync should be:
      | Requirement | Description |
      | Real-time | Updates appear within seconds |
      | Reliable | Failed syncs are retried automatically |
      | Auditable | Sync events are logged for troubleshooting |
      | Configurable | Admins can enable/disable specific sync types |

  Scenario: Support multiple CRM/ticketing systems
    Given the system needs to integrate with different platforms
    When configuring CRM integration
    Then the system should support:
      | Platform | Integration Method |
      | Salesforce | REST API, OAuth authentication |
      | Zendesk | REST API, API token authentication |
      | ServiceNow | REST API, OAuth or basic auth |
      | Jira Service Management | REST API, API token |
      | Custom/Generic | REST API with configurable endpoints |
    And configuration should include:
      | Setting | Description |
      | API endpoint | Base URL for CRM API |
      | Authentication | Credentials or OAuth configuration |
      | Field mapping | Map voice agent fields to CRM fields |
      | Webhook URLs | For bidirectional sync |
      | Sync rules | When and what to sync |
    And the system should validate connectivity on save

