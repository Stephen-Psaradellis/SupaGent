"""
ElevenLabs Agent Testing Integration
Manages agent tests through the ElevenLabs REST API only (no SDK).
Uses the documented endpoints from https://elevenlabs.io/docs/agents-platform/api-reference/tests/
"""
from __future__ import annotations

import os
import httpx
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class TestScenario:
    """A test scenario for an agent."""
    name: str
    messages: List[Dict[str, str]]  # List of {role: "user"|"assistant", content: str}
    expected_tool_calls: Optional[List[str]] = None  # Expected tool names to be called
    expected_keywords: Optional[List[str]] = None  # Keywords that should appear in response


@dataclass
class TestResult:
    """Result of running a test.
    
    Attributes:
        test_id: Unique identifier for the test run.
        scenario_name: Name of the test scenario that was executed.
        passed: Whether the test passed (True) or failed (False).
        details: Additional test execution details (e.g., sources_count).
        tool_calls: List of tool calls made during test execution.
        response: The agent's response text, if available.
        error: Error message if the test failed, None otherwise.
    """
    test_id: str
    scenario_name: str
    passed: bool
    details: Dict[str, Any]
    tool_calls: List[Dict[str, Any]]
    response: Optional[str] = None
    error: Optional[str] = None


class ElevenLabsAgentTester:
    """Client for managing and running agent tests via ElevenLabs REST API only.
    
    This class provides a REST API-only interface to the ElevenLabs Agent Testing
    platform. It does not require the ElevenLabs SDK and uses httpx for HTTP requests.
    All methods correspond to documented endpoints from the ElevenLabs API reference.
    
    Attributes:
        BASE_URL: Base URL for the ElevenLabs agent testing API.
        agent_id: The ElevenLabs agent ID to test against.
        api_key: The ElevenLabs API key for authentication.
    """

    BASE_URL = "https://api.elevenlabs.io/v1/convai/agent-testing"
    AGENTS_BASE_URL = "https://api.elevenlabs.io/v1/convai/agents"

    def __init__(self, agent_id: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize the ElevenLabs Agent Tester.
        
        Args:
            agent_id: Optional agent ID. If not provided, reads from ELEVENLABS_AGENT_ID env var.
            api_key: Optional API key. If not provided, reads from Doppler.
            
        Raises:
            RuntimeError: If agent_id or api_key is not set (either via args or env vars).
        """
        from core.secrets import get_elevenlabs_api_key
        from dotenv import load_dotenv
        
        load_dotenv()  # Load .env for ELEVENLABS_AGENT_ID
        
        self.agent_id = agent_id or os.getenv("ELEVENLABS_AGENT_ID")
        self.api_key = api_key or get_elevenlabs_api_key()
        
        if not self.agent_id:
            raise RuntimeError("ELEVENLABS_AGENT_ID is not set.")
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is not set in Doppler.")
        
        self._headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        base_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make a REST API request to ElevenLabs.
        
        Internal helper method that handles HTTP requests with authentication
        and error handling. All API methods use this for consistency.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE).
            endpoint: API endpoint path (e.g., "/{test_id}").
            json_data: Optional JSON payload for POST/PATCH requests.
            params: Optional query parameters for GET requests.
            base_url: Optional base URL override (defaults to BASE_URL).
            
        Returns:
            Parsed JSON response as a dictionary.
            
        Raises:
            httpx.HTTPStatusError: If the API request fails (non-2xx status).
        """
        if base_url is None:
            base_url = self.BASE_URL
        url = f"{base_url}{endpoint}"
        
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=self._headers,
            )
            if not response.is_success:
                # Capture error details for debugging
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json
                except:
                    pass
                error_msg = f"Client error '{response.status_code}' for url '{url}'"
                if isinstance(error_detail, dict):
                    error_msg += f": {error_detail}"
                else:
                    error_msg += f": {error_detail[:500]}"
                raise httpx.HTTPStatusError(
                    error_msg,
                    request=response.request,
                    response=response,
                )
            
            # Handle empty responses (common for DELETE requests)
            if not response.text or response.status_code == 204:
                return {"success": True, "status_code": response.status_code}
            
            try:
                return response.json()
            except ValueError:
                # If response is not JSON but is successful, return text
                return {"success": True, "message": response.text, "status_code": response.status_code}

    def list_tests(
        self,
        cursor: Optional[str] = None,
        page_size: int = 30,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all agent response tests.
        
        Retrieves a paginated list of all tests for the configured agent.
        Supports pagination via cursor and optional search filtering.
        
        Args:
            cursor: Optional pagination cursor from a previous response.
            page_size: Number of results per page (max 100, default 30).
            search: Optional search query to filter tests by name or content.
            
        Returns:
            Dictionary containing test list and pagination metadata.
            
        Reference:
            https://elevenlabs.io/docs/agents-platform/api-reference/tests/list
        """
        params = {}
        if cursor:
            params["cursor"] = cursor
        if page_size:
            params["page_size"] = min(page_size, 100)  # Max 100
        if search:
            params["search"] = search
        
        return self._request("GET", "", params=params)

    def get_test(self, test_id: str) -> Dict[str, Any]:
        """Get an agent response test by ID.
        
        Retrieves detailed information about a specific test, including
        its configuration, chat history, and success conditions.
        
        Args:
            test_id: Unique identifier of the test to retrieve.
            
        Returns:
            Dictionary containing full test configuration and metadata.
            
        Reference:
            https://elevenlabs.io/docs/agents-platform/api-reference/tests/get
        """
        return self._request("GET", f"/{test_id}")

    def create_test(
        self,
        name: str,
        chat_history: List[Dict[str, Any]],
        success_condition: str,
        success_examples: List[Dict[str, Any]],
        failure_examples: Optional[List[Dict[str, Any]]] = None,
        tool_call_parameters: Optional[Dict[str, Any]] = None,
        dynamic_variables: Optional[Dict[str, Any]] = None,
        type: str = "llm",  # "llm" or "tool"
        from_conversation_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new agent response test.
        
        Creates a test in the ElevenLabs dashboard that can be run against
        the agent. The test defines a conversation scenario and success criteria.
        
        Args:
            name: Human-readable name for the test.
            chat_history: List of conversation messages in format
                [{"role": "user"|"assistant", "message": str, "type": "client"|"agent"}].
            success_condition: Prompt/condition that evaluates whether the response
                is successful (should return True/False). Can reference tool calls
                and response content.
            success_examples: List of example successful responses for training
                the evaluation model.
            failure_examples: Optional list of example failure responses.
            tool_call_parameters: Optional parameters for evaluating tool calls
                (e.g., expected tool names, argument validation).
            dynamic_variables: Optional variables to inject into agent config
                during test execution.
            type: Test type - "llm" for LLM response evaluation, "tool" for tool call evaluation.
            from_conversation_metadata: Optional metadata if test was created
                from an actual conversation.
                
        Returns:
            Dictionary containing the created test's ID and configuration.
            
        Reference:
            https://elevenlabs.io/docs/agents-platform/api-reference/tests/create
        """
        # Build payload - when tool_call_parameters is present, omit message evaluation fields
        # The API validation rejects them together, so we try omitting them for tool tests
        # All fields are required according to API docs
        # For tool tests: use empty string for success_condition and empty arrays for examples
        payload = {
            "name": name,
            "chat_history": chat_history,
            "success_condition": success_condition,
            "success_examples": success_examples,
            "failure_examples": failure_examples or [],
        }
        
        # Add tool_call_parameters if provided (for tool type tests)
        if tool_call_parameters:
            payload["tool_call_parameters"] = tool_call_parameters
        
        if type:
            payload["type"] = type
        
        if dynamic_variables:
            payload["dynamic_variables"] = dynamic_variables
        if type:
            payload["type"] = type
        if from_conversation_metadata:
            payload["from_conversation_metadata"] = from_conversation_metadata
        
        # Use the correct create endpoint: /v1/convai/agent-testing/create
        return self._request("POST", "/create", json_data=payload)

    def update_test(
        self,
        test_id: str,
        name: Optional[str] = None,
        chat_history: Optional[List[Dict[str, Any]]] = None,
        success_condition: Optional[str] = None,
        success_examples: Optional[List[Dict[str, Any]]] = None,
        failure_examples: Optional[List[Dict[str, Any]]] = None,
        tool_call_parameters: Optional[Dict[str, Any]] = None,
        dynamic_variables: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update an existing test.
        
        Updates one or more fields of an existing test. Only provided fields
        will be updated; others remain unchanged.
        
        Args:
            test_id: Unique identifier of the test to update.
            name: Optional new name for the test.
            chat_history: Optional new chat history.
            success_condition: Optional new success condition prompt.
            success_examples: Optional new list of success examples.
            failure_examples: Optional new list of failure examples.
            tool_call_parameters: Optional new tool call parameters.
            dynamic_variables: Optional new dynamic variables.
            
        Returns:
            Dictionary containing the updated test configuration.
            
        Reference:
            https://elevenlabs.io/docs/agents-platform/api-reference/tests/update
        """
        payload = {}
        if name is not None:
            payload["name"] = name
        if chat_history is not None:
            payload["chat_history"] = chat_history
        if success_condition is not None:
            payload["success_condition"] = success_condition
        if success_examples is not None:
            payload["success_examples"] = success_examples
        if failure_examples is not None:
            payload["failure_examples"] = failure_examples
        if tool_call_parameters is not None:
            payload["tool_call_parameters"] = tool_call_parameters
        if dynamic_variables is not None:
            payload["dynamic_variables"] = dynamic_variables
        
        return self._request("PATCH", f"/{test_id}", json_data=payload)

    def update_agent(
        self,
        mcp_server_ids: Optional[List[str]] = None,
        knowledge_base_ids: Optional[List[str]] = None,
        prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Update agent configuration to grant access to MCP servers and knowledge bases.
        
        Reference: https://elevenlabs.io/docs/agents-platform/api-reference/agents/update
        
        Args:
            mcp_server_ids: List of MCP server IDs to grant access to
            knowledge_base_ids: List of knowledge base IDs to grant access to
            prompt: System prompt to update for the agent
            **kwargs: Additional agent configuration fields to update
            
        Returns:
            Updated agent configuration
        """
        payload = {}
        
        if mcp_server_ids is not None:
            payload["mcp_server_ids"] = mcp_server_ids
        
        if knowledge_base_ids is not None:
            payload["knowledge_base_ids"] = knowledge_base_ids
        
        if prompt is not None:
            # Update the prompt in conversation_config.agent.prompt.prompt
            if "conversation_config" not in payload:
                payload["conversation_config"] = {}
            if "agent" not in payload["conversation_config"]:
                payload["conversation_config"]["agent"] = {}
            if "prompt" not in payload["conversation_config"]["agent"]:
                payload["conversation_config"]["agent"]["prompt"] = {}
            payload["conversation_config"]["agent"]["prompt"]["prompt"] = prompt
        
        # Add any other fields from kwargs
        payload.update(kwargs)
        
        return self._request("PATCH", f"/{self.agent_id}", json_data=payload, base_url=self.AGENTS_BASE_URL)

    def delete_test(self, test_id: str) -> Dict[str, Any]:
        """Delete a test.
        
        Permanently deletes a test from the ElevenLabs dashboard.
        
        Args:
            test_id: Unique identifier of the test to delete.
            
        Returns:
            Dictionary confirming deletion or containing error information.
            
        Reference:
            https://elevenlabs.io/docs/agents-platform/api-reference/tests/delete
        """
        return self._request("DELETE", f"/{test_id}")

    def get_test_summaries(
        self,
        cursor: Optional[str] = None,
        page_size: int = 30,
    ) -> Dict[str, Any]:
        """Get test summaries.
        
        Retrieves summarized test results including pass/fail status and
        execution metadata. More efficient than fetching full test details.
        
        Args:
            cursor: Optional pagination cursor from a previous response.
            page_size: Number of results per page (max 100, default 30).
            
        Returns:
            Dictionary containing test summaries and pagination metadata.
            
        Reference:
            https://elevenlabs.io/docs/agents-platform/api-reference/tests/summaries
        """
        params = {}
        if cursor:
            params["cursor"] = cursor
        if page_size:
            params["page_size"] = min(page_size, 100)
        
        return self._request("GET", "/summaries", params=params)

    def run_tests(
        self,
        test_ids: List[str],
        agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run tests against an agent.
        
        Executes one or more tests against the specified agent and returns
        the results. Tests are run asynchronously on the ElevenLabs platform.
        
        Args:
            test_ids: List of test IDs to execute.
            agent_id: Optional agent ID to test against. Defaults to the
                agent_id configured in the tester instance.
                
        Returns:
            Dictionary containing test execution results and status.
            
        Reference:
            https://elevenlabs.io/docs/agents-platform/api-reference/tests/run-tests
        """
        agent_id = agent_id or self.agent_id
        # The endpoint is /v1/convai/agents/{agent_id}/run-tests, not /agent-testing/run-tests
        payload = {
            "tests": [{"test_id": test_id} for test_id in test_ids],
        }
        
        return self._request("POST", f"/{agent_id}/run-tests", json_data=payload, base_url=self.AGENTS_BASE_URL)

    # Convenience methods for creating tests from scenarios
    def create_test_from_scenario(
        self,
        scenario: TestScenario,
        success_condition: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a test from a TestScenario object.
        
        Converts TestScenario format to ElevenLabs API format.
        Based on actual test structure from API.
        """
        # Convert scenario messages to chat_history format
        # Based on API docs, chat_history for create is simpler - just role and time_in_call_secs
        # The full structure is returned by GET, but create accepts minimal structure
        chat_history = []
        time_in_call = 0
        for i, msg in enumerate(scenario.messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Minimal structure for create endpoint
            turn = {
                "role": role,
                "time_in_call_secs": time_in_call,
            }
            # Add message field if content exists
            if content:
                turn["message"] = content
            chat_history.append(turn)
            time_in_call += 1
        
        # Build success condition and tool_call_parameters
        # NOTE: Due to API limitation, we cannot use tool_call_parameters with message evaluation
        # For tool invocation tests, we'll create them as "tool" type but they may fail to create
        # The API requires success_condition/success_examples/failure_examples but rejects them
        # with tool_call_parameters. This appears to be an API bug.
        
        tool_call_parameters = None
        test_type = "llm"
        
        if not success_condition:
            # Check if this is a tool invocation test (has expected_tool_calls but no keywords)
            if scenario.expected_tool_calls and not scenario.expected_keywords:
                # This is a tool invocation test - use tool evaluation
                test_type = "tool"
                # Use empty string for success_condition (matches existing tool tests)
                # The tool_call_parameters will handle the actual tool verification
                success_condition = ""  # Will be set to empty string in examples section
                
                # Build tool_call_parameters for tool evaluation
                # The API requires referenced_tool with id and type
                # For knowledge base tools, use id "knowledgebase" and type based on the tool
                first_tool = scenario.expected_tool_calls[0] if scenario.expected_tool_calls else None
                if first_tool:
                    # For MCP server tools, the type should be "mcp"
                    # We need the actual tool ID from the MCP server configuration
                    # For now, try using the tool name as ID - the API may resolve it
                    # Or we may need to get the tool ID from the agent's tool configuration
                    tool_call_parameters = {
                        "referenced_tool": {
                            "id": first_tool,  # Tool name - may need actual tool ID
                            "type": "mcp",  # MCP server tool type
                        },
                        "verify_absence": False,
                        "parameters": [],  # Empty parameters array - tool invocation verification only
                    }
                else:
                    tool_call_parameters = None
            elif scenario.expected_keywords:
                # Message evaluation test - check keywords in response
                keyword_checks = [
                    f'"{keyword}" in response.lower()'
                    for keyword in scenario.expected_keywords
                ]
                success_condition = " and ".join(keyword_checks)
            elif scenario.expected_tool_calls:
                # Has tool calls but also keywords - use message evaluation
                success_condition = "len(response) > 0"
            else:
                # Default: test passes if agent responds
                success_condition = "len(response) > 0"
        
        # Create success/failure examples (required by API)
        # For tool type tests: use empty string for success_condition and empty arrays for examples
        # This matches the structure of existing tool tests in the API
        if test_type == "tool":
            # Use empty string and empty arrays - this is what existing tool tests use
            success_condition = ""  # Empty string, not "True"
            success_examples = []
            failure_examples = []
        else:
            success_examples = [
                {
                    "response": "The agent successfully answered the question.",
                    "type": "success"
                }
            ]
            failure_examples = [
                {
                    "response": "The agent failed to answer the question.",
                    "type": "failure"
                }
            ]
        
        return self.create_test(
            name=scenario.name,
            chat_history=chat_history,
            success_condition=success_condition,
            success_examples=success_examples,
            failure_examples=failure_examples,
            tool_call_parameters=tool_call_parameters,
            type=test_type,
        )

    def create_tests_from_scenarios(
        self,
        scenarios: List[TestScenario],
        suite_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Create multiple tests from a list of scenarios.
        
        Batch creates tests from a list of TestScenario objects. Continues
        processing even if individual tests fail, collecting all results.
        
        Args:
            scenarios: List of TestScenario objects to create tests from.
            suite_name: Optional name for the test suite (currently unused,
                reserved for future suite grouping functionality).
                
        Returns:
            List of dictionaries, each containing:
                - "scenario_name": Name of the scenario
                - "test_id": Created test ID (if successful)
                - "result": Full API response (if successful)
                - "error": Error message (if failed)
        """
        created_tests = []
        for scenario in scenarios:
            try:
                result = self.create_test_from_scenario(scenario)
                test_id = result.get("id") or result.get("test_id")
                created_tests.append({
                    "scenario_name": scenario.name,
                    "test_id": test_id,
                    "result": result,
                })
            except Exception as e:
                created_tests.append({
                    "scenario_name": scenario.name,
                    "error": str(e),
                })
        
        return created_tests


def create_default_test_suite() -> List[TestScenario]:
    """Create a default test suite for customer support agent with 10 tests.
    
    Returns a comprehensive set of test scenarios covering common customer
    support queries including password reset, account recovery, troubleshooting,
    and general support questions.
    
    Returns:
        List of TestScenario objects ready to be used with ElevenLabsAgentTester.
    """
    from agents.test_suites import get_comprehensive_test_suite
    return get_comprehensive_test_suite()
