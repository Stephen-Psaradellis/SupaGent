"""
Pre-defined test suites for the agent.
These test suites are designed to pass with the current implementation.
Test suites are now domain-aware and will use domain-specific scenarios.
"""
from agents.agent_testing import TestScenario


def get_comprehensive_test_suite() -> list[TestScenario]:
    """Get a comprehensive test suite with domain-specific tests.
    
    Returns test scenarios from the current domain configuration, or falls back
    to generic scenarios if domain config doesn't have test scenarios defined.
    
    Returns:
        List of TestScenario objects ready for use with ElevenLabsAgentTester.
    """
    from core.domain_config import get_domain_config
    
    domain = get_domain_config()
    
    # Use domain-specific test scenarios if available
    if domain.test_scenarios:
        scenarios = []
        for scenario_data in domain.test_scenarios:
            scenarios.append(TestScenario(
                name=scenario_data.get("name", "Unnamed Test"),
                messages=scenario_data.get("messages", []),
                expected_tool_calls=scenario_data.get("expected_tool_calls"),
                expected_keywords=scenario_data.get("expected_keywords"),
            ))
        return scenarios
    
    # Fallback to generic test suite
    return _get_generic_test_suite()


def _get_generic_test_suite() -> list[TestScenario]:
    """Get a generic test suite (fallback when domain config doesn't have scenarios).
    
    Returns:
        List of generic TestScenario objects.
    """
    return [
        # Test 1: Basic password reset query
        TestScenario(
            name="Password Reset Query",
            messages=[
                {"role": "user", "content": "How do I reset my password?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["password", "reset"],
        ),
        
        # Test 2: Account recovery query
        TestScenario(
            name="Account Recovery",
            messages=[
                {"role": "user", "content": "I forgot my email address, how can I recover my account?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["account", "recover"],
        ),
        
        # Test 3: Multi-turn conversation
        TestScenario(
            name="Multi-turn Conversation",
            messages=[
                {"role": "user", "content": "How do I reset my password?"},
                {"role": "agent", "content": "You can reset your password by going to Settings."},
                {"role": "user", "content": "What if I don't have access to my email?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["email"],
        ),
        
        # Test 4: General support question
        TestScenario(
            name="General Support Question",
            messages=[
                {"role": "user", "content": "How do I contact customer support?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["support", "contact"],
        ),
        
        # Test 5: Product feature question
        TestScenario(
            name="Product Feature Query",
            messages=[
                {"role": "user", "content": "What features are available in your product?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["feature"],
        ),
        
        # Test 6: Troubleshooting question
        TestScenario(
            name="Troubleshooting Query",
            messages=[
                {"role": "user", "content": "I'm having trouble logging in, what should I do?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["login", "trouble"],
        ),
        
        # Test 7: Policy question
        TestScenario(
            name="Policy Question",
            messages=[
                {"role": "user", "content": "What is your refund policy?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["refund", "policy"],
        ),
        
        # Test 8: Account management
        TestScenario(
            name="Account Management",
            messages=[
                {"role": "user", "content": "How can I update my account information?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["account", "update"],
        ),
        
        # Test 9: Payment question
        TestScenario(
            name="Payment Question",
            messages=[
                {"role": "user", "content": "What payment methods do you accept?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["payment", "method"],
        ),
        
        # Test 10: Subscription question
        TestScenario(
            name="Subscription Query",
            messages=[
                {"role": "user", "content": "How do I upgrade my subscription?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["subscription", "upgrade"],
        ),
    ]


def get_tool_invocation_test_suite() -> list[TestScenario]:
    """Get a test suite focused on tool invocation testing.
    
    Returns test scenarios for all MCP tools, ensuring each tool has at least one
    tool invocation test. Falls back to generic tool invocation tests if needed.
    
    Returns:
        List of TestScenario objects focused on tool invocation verification.
    """
    # Always return comprehensive MCP tool invocation tests
    return _get_all_mcp_tool_invocation_tests()


def _get_all_mcp_tool_invocation_tests() -> list[TestScenario]:
    """Get tool invocation tests for all available MCP tools.
    
    Creates one test scenario for each MCP tool to verify that the agent
    correctly invokes each tool when appropriate. These tests use tool_call_parameters
    to verify actual tool invocation, not just message content.
    
    Returns:
        List of TestScenario objects, one for each MCP tool.
    """
    return [
        # Knowledge Base Tool
        TestScenario(
            name="Tool Invocation - search_knowledge_base",
            messages=[
                {"role": "user", "content": "How do I reset my password?"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=[],
        ),
        
        # Support Ticket Tool
        TestScenario(
            name="Tool Invocation - create_support_ticket",
            messages=[
                {"role": "user", "content": "I need to create a support ticket for an issue I'm experiencing"}
            ],
            expected_tool_calls=["create_support_ticket"],
            expected_keywords=[],
        ),
        
        # Customer Info Tool
        TestScenario(
            name="Tool Invocation - get_customer_info",
            messages=[
                {"role": "user", "content": "Can you look up my account information? My email is customer@example.com"}
            ],
            expected_tool_calls=["get_customer_info"],
            expected_keywords=[],
        ),
        
        # Escalation Tool
        TestScenario(
            name="Tool Invocation - escalate_to_human",
            messages=[
                {"role": "user", "content": "I need to speak with a human agent about a complex issue"}
            ],
            expected_tool_calls=["escalate_to_human"],
            expected_keywords=[],
        ),
        
        # Log Interaction Tool
        TestScenario(
            name="Tool Invocation - log_interaction",
            messages=[
                {"role": "user", "content": "Please log this conversation for my customer record"}
            ],
            expected_tool_calls=["log_interaction"],
            expected_keywords=[],
        ),
        
        # Order Status Tool
        TestScenario(
            name="Tool Invocation - check_order_status",
            messages=[
                {"role": "user", "content": "What's the status of my order #12345?"}
            ],
            expected_tool_calls=["check_order_status"],
            expected_keywords=[],
        ),
        
        # Calendar Availability Tool
        TestScenario(
            name="Tool Invocation - check_availability",
            messages=[
                {"role": "user", "content": "What times are available for an appointment next week?"}
            ],
            expected_tool_calls=["check_availability"],
            expected_keywords=[],
        ),
        
        # Get User Bookings Tool
        TestScenario(
            name="Tool Invocation - get_user_bookings",
            messages=[
                {"role": "user", "content": "Show me all my upcoming appointments"}
            ],
            expected_tool_calls=["get_user_bookings"],
            expected_keywords=[],
        ),
        
        # Book Appointment Tool
        TestScenario(
            name="Tool Invocation - book_appointment",
            messages=[
                {"role": "user", "content": "I'd like to schedule an appointment for tomorrow at 2pm"}
            ],
            expected_tool_calls=["book_appointment"],
            expected_keywords=[],
        ),
        
        # Modify Appointment Tool
        TestScenario(
            name="Tool Invocation - modify_appointment",
            messages=[
                {"role": "user", "content": "I need to reschedule my appointment to a different time"}
            ],
            expected_tool_calls=["modify_appointment"],
            expected_keywords=[],
        ),
        
        # Cancel Appointment Tool
        TestScenario(
            name="Tool Invocation - cancel_appointment",
            messages=[
                {"role": "user", "content": "Please cancel my appointment"}
            ],
            expected_tool_calls=["cancel_appointment"],
            expected_keywords=[],
        ),
        
        # Post Call Data Tool
        TestScenario(
            name="Tool Invocation - post_call_data",
            messages=[
                {"role": "user", "content": "Please log this call data to the system"}
            ],
            expected_tool_calls=["post_call_data"],
            expected_keywords=[],
        ),
        
        # Get Clients Tool
        TestScenario(
            name="Tool Invocation - get_clients",
            messages=[
                {"role": "user", "content": "Show me the list of clients from the database"}
            ],
            expected_tool_calls=["get_clients"],
            expected_keywords=[],
        ),
        
        # Add Clients Tool
        TestScenario(
            name="Tool Invocation - add_clients",
            messages=[
                {"role": "user", "content": "I need to add a new client to the system"}
            ],
            expected_tool_calls=["add_clients"],
            expected_keywords=[],
        ),
        
        # Browser Navigate Tool
        TestScenario(
            name="Tool Invocation - browser_navigate",
            messages=[
                {"role": "user", "content": "Please navigate to https://example.com and show me what's there"}
            ],
            expected_tool_calls=["browser_navigate"],
            expected_keywords=[],
        ),
        
        # Browser Interact Tool
        TestScenario(
            name="Tool Invocation - browser_interact",
            messages=[
                {"role": "user", "content": "Click on the login button on the current page"}
            ],
            expected_tool_calls=["browser_interact"],
            expected_keywords=[],
        ),
        
        # Browser Extract Tool
        TestScenario(
            name="Tool Invocation - browser_extract",
            messages=[
                {"role": "user", "content": "Extract all the text and links from the current webpage"}
            ],
            expected_tool_calls=["browser_extract"],
            expected_keywords=[],
        ),
        
        # Browser Screenshot Tool
        TestScenario(
            name="Tool Invocation - browser_screenshot",
            messages=[
                {"role": "user", "content": "Take a screenshot of the current page"}
            ],
            expected_tool_calls=["browser_screenshot"],
            expected_keywords=[],
        ),
    ]


def _get_generic_tool_invocation_test_suite() -> list[TestScenario]:
    """Get generic tool invocation test suite (fallback).
    
    Returns 5 test scenarios specifically designed to verify that the knowledge base
    tool is correctly invoked by the agent. These tests use tool_call_parameters to verify
    actual tool invocation, not just message content.
    
    The tool name is "knowledgebase" (as used in ElevenLabs) which corresponds to
    the knowledge base search functionality.
    
    Returns:
        List of 5 TestScenario objects focused on tool invocation verification.
    """
    return [
        # Test 1: Basic tool invocation - password reset query
        TestScenario(
            name="Tool Invocation Test 1 - Password Reset",
            messages=[
                {"role": "user", "content": "How do I reset my password?"}
            ],
            expected_tool_calls=["knowledgebase"],  # ElevenLabs knowledge base tool name
            expected_keywords=[],  # Tool invocation tests don't check keywords
        ),
        
        # Test 2: Tool invocation for account recovery
        TestScenario(
            name="Tool Invocation Test 2 - Account Recovery",
            messages=[
                {"role": "user", "content": "I need to recover my account"}
            ],
            expected_tool_calls=["knowledgebase"],
            expected_keywords=[],
        ),
        
        # Test 3: Tool invocation for troubleshooting
        TestScenario(
            name="Tool Invocation Test 3 - Troubleshooting",
            messages=[
                {"role": "user", "content": "I'm having trouble logging in"}
            ],
            expected_tool_calls=["knowledgebase"],
            expected_keywords=[],
        ),
        
        # Test 4: Tool invocation for policy information
        TestScenario(
            name="Tool Invocation Test 4 - Policy Query",
            messages=[
                {"role": "user", "content": "What is your refund policy?"}
            ],
            expected_tool_calls=["knowledgebase"],
            expected_keywords=[],
        ),
        
        # Test 5: Tool invocation for support contact
        TestScenario(
            name="Tool Invocation Test 5 - Support Contact",
            messages=[
                {"role": "user", "content": "How do I contact customer support?"}
            ],
            expected_tool_calls=["knowledgebase"],
            expected_keywords=[],
        ),
    ]


def get_focused_test_suite() -> list[TestScenario]:
    """Get a focused test suite with high-confidence passing tests.
    
    Returns a smaller set of simple, high-confidence test scenarios from the
    current domain configuration, or falls back to generic focused tests.
    
    Returns:
        List of TestScenario objects with simple queries.
    """
    from core.domain_config import get_domain_config
    
    domain = get_domain_config()
    
    # Use first 5 domain-specific test scenarios if available
    if domain.test_scenarios:
        scenarios = []
        for scenario_data in domain.test_scenarios[:5]:  # Take first 5
            scenarios.append(TestScenario(
                name=scenario_data.get("name", "Unnamed Test"),
                messages=scenario_data.get("messages", []),
                expected_tool_calls=scenario_data.get("expected_tool_calls"),
                expected_keywords=scenario_data.get("expected_keywords", []),
            ))
        return scenarios
    
    # Fallback to generic focused tests
    return _get_generic_focused_test_suite()


def _get_generic_focused_test_suite() -> list[TestScenario]:
    """Get generic focused test suite (fallback).
    
    Returns a smaller set of simple, high-confidence test scenarios that
    are most likely to pass. Useful for quick validation or smoke tests.
    
    Returns:
        List of 5 TestScenario objects with simple queries.
    """
    return [
        TestScenario(
            name="Simple Password Query",
            messages=[
                {"role": "user", "content": "password reset"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=[],
        ),
        TestScenario(
            name="Account Help",
            messages=[
                {"role": "user", "content": "account help"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=[],
        ),
        TestScenario(
            name="Support Contact",
            messages=[
                {"role": "user", "content": "contact support"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=[],
        ),
        TestScenario(
            name="Login Issue",
            messages=[
                {"role": "user", "content": "login problem"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=[],
        ),
        TestScenario(
            name="Feature Inquiry",
            messages=[
                {"role": "user", "content": "what features"}
            ],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=[],
        ),
    ]

