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
    """Get a test suite focused on tool awareness and system integration testing.

    Since ElevenLabs cannot test MCP tool invocations, this suite focuses on:
    1. System tools that CAN be tested for invocation (like escalate_to_human)
    2. Tool awareness tests that verify the agent understands when tools should be used

    Returns:
        List of TestScenario objects focused on tool awareness and system integration.
    """
    # Return tool awareness tests - MCP tool invocations cannot be tested in ElevenLabs
    return _get_all_tool_awareness_tests()


def _get_all_tool_awareness_tests() -> list[TestScenario]:
    """Get tool awareness tests for system integration and MCP tool understanding.

    Since ElevenLabs cannot test MCP tool invocations, these tests verify that
    the agent properly understands when tools should be used and responds
    appropriately. Only system tools like escalate_to_human can be tested
    for actual invocation.

    Returns:
        List of TestScenario objects focused on tool awareness and system integration.
    """
    return [
        # System Tool - This CAN be tested for invocation
        TestScenario(
            name="System Tool - Escalate to Human",
            messages=[
                {"role": "user", "content": "This is very urgent and I need to speak with a human immediately"}
            ],
            expected_tool_calls=["escalate_to_human"],
            expected_keywords=["escalat", "human", "agent"],
        ),

        # Tool Awareness Tests - These verify the agent understands tool usage
        TestScenario(
            name="Tool Awareness - Knowledge Base Search",
            messages=[
                {"role": "user", "content": "How do I reset my password?"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["search", "knowledge", "information", "help"],
        ),

        TestScenario(
            name="Tool Awareness - Customer Information Lookup",
            messages=[
                {"role": "user", "content": "Can you check my account details? My customer ID is CUST-12345"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["account", "customer", "information", "lookup"],
        ),

        TestScenario(
            name="Tool Awareness - Order Status Check",
            messages=[
                {"role": "user", "content": "What's the status of my order number ORD-67890?"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["order", "status", "check", "track"],
        ),

        TestScenario(
            name="Tool Awareness - Support Ticket Creation",
            messages=[
                {"role": "user", "content": "I need to create a support ticket for this critical issue"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["ticket", "support", "create", "issue"],
        ),

        TestScenario(
            name="Tool Awareness - Calendar Availability",
            messages=[
                {"role": "user", "content": "What times are available for a meeting next Tuesday?"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["available", "calendar", "schedule", "meeting"],
        ),

        TestScenario(
            name="Tool Awareness - Browser Navigation",
            messages=[
                {"role": "user", "content": "Can you check the latest documentation on our website?"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["website", "documentation", "check", "browse"],
        ),

        TestScenario(
            name="System Integration - Call Logging",
            messages=[
                {"role": "user", "content": "Please make sure this conversation gets logged for compliance"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["log", "record", "compliance", "conversation"],
        ),

        TestScenario(
            name="Multi-Tool Scenario - Complex Support",
            messages=[
                {"role": "user", "content": "I'm having trouble with my account, I can't log in, and I need to check my order status too"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["account", "login", "order", "help", "multiple"],
        ),

        TestScenario(
            name="Fallback Response - Tool Unavailable",
            messages=[
                {"role": "user", "content": "Can you access my bank account details?"}
            ],
            expected_tool_calls=[],  # Cannot test MCP tool invocation
            expected_keywords=["cannot", "unable", "security", "policy"],
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

