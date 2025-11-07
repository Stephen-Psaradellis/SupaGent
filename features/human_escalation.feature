Feature: Human Escalation with Context Handoff
  As a customer support agent
  I want to receive escalated conversations with full context
  So that I can quickly understand the issue and provide effective support without asking the customer to repeat information

  Background:
    Given a voice agent conversation is in progress
    And the conversation has multiple turns
    And the agent has retrieved relevant documents from the knowledge base

  Scenario: Automatic escalation trigger - unresolved query
    Given a user has asked a question
    And the voice agent has attempted to answer
    When the agent detects:
      | Condition | Description |
      | Low confidence | Retrieved documents have similarity score below 0.5 |
      | No results | Vector store returned empty results |
      | User frustration | User explicitly requests human agent |
      | Multiple failed attempts | 3+ unsuccessful answer attempts in same session |
    Then the system should:
      | Action | Description |
      | Flag conversation for escalation | Mark session as requiring human intervention |
      | Collect full conversation context | Store all turns, retrieved documents, and metadata |
      | Create escalation ticket | Generate ticket in integrated CRM/ticketing system |
      | Notify human agent | Send notification with conversation summary |
      | Provide handoff message | Inform user that human agent will assist |

  Scenario: View escalated conversation context
    Given a conversation has been escalated
    When a human agent opens the escalation ticket
    Then the agent should see:
      | Information | Description |
      | Full conversation transcript | All user queries and agent responses in chronological order |
      | Retrieved documents | All knowledge base documents retrieved during conversation |
      | Confidence scores | Similarity scores for each retrieved document |
      | Suggested responses | Agent's attempted answers with confidence levels |
      | Session metadata | Session ID, start time, duration, language detected |
      | Customer information | If available from CRM integration |
    And the information should be presented in a clear, readable format
    And the agent should be able to expand/collapse sections

  Scenario: Manual escalation by user request
    Given a user is in a conversation with the voice agent
    When the user says phrases like:
      | Phrase | Example |
      | "I want to speak to a human" | Direct request |
      | "This isn't helping" | Frustration indicator |
      | "Can I talk to a real person?" | Explicit escalation request |
    Then the system should:
      | Action | Description |
      | Immediately flag for escalation | Don't attempt further automated responses |
      | Acknowledge the request | "I'll connect you with a human agent right away" |
      | Collect conversation context | Same as automatic escalation |
      | Create escalation ticket | With priority flag for user-requested escalation |
      | Transfer to human agent | If available, or queue for next available agent |

  Scenario: Suggested responses for human agent
    Given a conversation has been escalated
    When a human agent views the escalation context
    Then the system should provide:
      | Suggestion | Description |
      | Suggested response | AI-generated response based on conversation context |
      | Relevant knowledge base articles | Top 3 most relevant documents |
      | Common solutions | Similar resolved cases from past escalations |
      | Escalation reason | Why this conversation was escalated |
    And the agent should be able to:
      | Action | Description |
      | Use suggested response | Copy/paste or edit suggested response |
      | View full knowledge base | Access complete knowledge base search |
      | Add notes | Document resolution for future reference |
      | Mark as resolved | Close escalation ticket with resolution notes |

  Scenario: Escalation workflow integration
    Given the system is integrated with a CRM/ticketing system
    When a conversation is escalated
    Then the system should:
      | Action | Description |
      | Create ticket | Generate ticket with all context attached |
      | Set priority | Based on escalation reason and user profile |
      | Assign to agent | If routing rules are configured |
      | Send notification | Alert assigned agent via configured channels |
      | Update conversation status | Mark voice agent session as "escalated" |
    And the ticket should be accessible from both systems
    And updates in either system should sync bidirectionally

