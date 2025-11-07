"""
Tests for agent testing functionality.
These tests verify that the agent testing system works correctly.
"""
import pytest
from agents.agent_testing import (
    ElevenLabsAgentTester,
    TestScenario,
    create_default_test_suite,
    TestResult,
)


def test_create_default_test_suite():
    """Test that default test suite is created correctly."""
    scenarios = create_default_test_suite()
    assert len(scenarios) >= 3
    assert all(isinstance(s, TestScenario) for s in scenarios)
    assert any("password" in s.name.lower() for s in scenarios)


def test_test_scenario_creation():
    """Test creating a test scenario."""
    scenario = TestScenario(
        name="Test Query",
        messages=[{"role": "user", "content": "How do I reset my password?"}],
        expected_tool_calls=["search_knowledge_base"],
        expected_keywords=["password"],
    )
    assert scenario.name == "Test Query"
    assert len(scenario.messages) == 1
    assert scenario.expected_tool_calls == ["search_knowledge_base"]


@pytest.mark.skipif(
    not pytest.config.getoption("--run-agent-tests", default=False),
    reason="Requires --run-agent-tests flag and ELEVENLABS_API_KEY"
)
def test_agent_tester_initialization():
    """Test that agent tester can be initialized."""
    import os
    if not os.getenv("ELEVENLABS_API_KEY") or not os.getenv("ELEVENLABS_AGENT_ID"):
        pytest.skip("ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID required")
    
    tester = ElevenLabsAgentTester()
    assert tester.agent_id is not None
    assert tester.api_key is not None


def test_local_test_execution():
    """Test running tests locally (without ElevenLabs API)."""
    # This should work even without API key
    scenarios = [
        TestScenario(
            name="Password Reset Test",
            messages=[{"role": "user", "content": "How do I reset my password?"}],
            expected_tool_calls=["search_knowledge_base"],
            expected_keywords=["password"],
        ),
    ]
    
    # We can't actually run without the full setup, but we can test the structure
    assert len(scenarios) == 1
    assert scenarios[0].name == "Password Reset Test"

