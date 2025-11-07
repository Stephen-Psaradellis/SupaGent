Feature: Conversation Analytics and Performance Dashboard
  As a support manager
  I want to view analytics and performance metrics for voice agent interactions
  So that I can measure ROI, identify improvement opportunities, and optimize support operations

  Background:
    Given the voice agent has processed multiple conversations
    And conversations include resolved, escalated, and unresolved interactions
    And feedback has been collected from some interactions

  Scenario: View overall performance metrics
    Given I am a support manager
    When I access the analytics dashboard
    Then I should see the following metrics:
      | Metric | Description |
      | Resolution Rate | Percentage of conversations resolved without escalation |
      | Average Handling Time | Mean time from query start to resolution |
      | Escalation Rate | Percentage of conversations escalated to human agents |
      | Customer Satisfaction (CSAT) | Average rating from feedback collection |
      | Cost Per Resolution | Total cost divided by number of resolved queries |
      | Knowledge Gap Count | Number of queries with low confidence or no results |
    And all metrics should be calculated for the selected time period
    And metrics should be filterable by date range, session ID, and query type

  Scenario: View knowledge gap analysis
    Given conversations have been processed
    When I view the knowledge gaps section
    Then I should see a list of queries that:
      | Condition | Description |
      | Returned no results | Vector store returned empty results |
      | Low confidence score | Retrieved documents had similarity score below threshold |
      | Resulted in escalation | Query was escalated to human agent |
      | Received negative feedback | User provided thumbs down or low rating |
    And each knowledge gap should show:
      | Field | Description |
      | Query text | The original user question |
      | Timestamp | When the query occurred |
      | Session ID | Associated conversation session |
      | Suggested action | Recommendation to add content to knowledge base |

  Scenario: View conversation trends over time
    Given historical conversation data exists
    When I select a time period (daily, weekly, monthly)
    Then I should see trend charts showing:
      | Metric | Visualization |
      | Resolution rate | Line chart over time |
      | Average handling time | Line chart over time |
      | Escalation rate | Line chart over time |
      | Query volume | Bar chart by day/week/month |
      | CSAT scores | Line chart with average and distribution |
    And I should be able to compare periods (e.g., this week vs last week)

  Scenario: Export analytics data
    Given I am viewing analytics data
    When I click the export button
    Then I should be able to export data in formats:
      | Format | Use Case |
      | CSV | Spreadsheet analysis |
      | JSON | API integration |
      | PDF | Executive reports |
    And the export should include all visible metrics and filters
    And the export should be downloadable immediately

  Scenario: View cost analysis
    Given conversations have associated costs (API calls, compute time)
    When I view the cost analysis section
    Then I should see:
      | Metric | Description |
      | Total cost | Sum of all costs for selected period |
      | Cost per resolution | Average cost per resolved query |
      | Cost per escalation | Average cost per escalated query |
      | Cost breakdown | Costs by component (ElevenLabs API, vector store, compute) |
      | ROI estimate | Savings vs human agent costs |
    And costs should be filterable by date range and query type

