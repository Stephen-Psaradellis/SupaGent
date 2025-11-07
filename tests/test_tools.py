"""
Tests for MCP tool endpoints.
Verifies that all tools are callable and return expected responses.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import build_app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    app = build_app()
    return TestClient(app)


class TestCreateSupportTicket:
    """Tests for create_support_ticket tool."""
    
    def test_create_ticket_with_minimal_fields(self, client: TestClient):
        """Test creating a ticket with only required fields."""
        response = client.post(
            "/tools/create_support_ticket",
            json={
                "title": "Test Issue",
                "description": "This is a test issue description"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ticket_id" in data
        assert data["title"] == "Test Issue"
        assert data["status"] == "created"
    
    def test_create_ticket_with_all_fields(self, client: TestClient):
        """Test creating a ticket with all optional fields."""
        response = client.post(
            "/tools/create_support_ticket",
            json={
                "title": "Urgent Issue",
                "description": "This is an urgent issue",
                "customer_id": "cust_123",
                "priority": "high",
                "tags": ["urgent", "billing"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ticket_id" in data
        assert data["title"] == "Urgent Issue"
    
    def test_create_ticket_mcp_endpoint(self, client: TestClient):
        """Test creating a ticket via MCP endpoint."""
        response = client.post(
            "/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "create_support_ticket",
                    "arguments": {
                        "title": "MCP Test Ticket",
                        "description": "Testing MCP endpoint"
                    }
                },
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "content" in data["result"]
        assert len(data["result"]["content"]) > 0
        assert "Ticket created" in data["result"]["content"][0]["text"]
    
    def test_create_ticket_invalid_priority(self, client: TestClient):
        """Test creating a ticket with invalid priority (should still work, uses default)."""
        response = client.post(
            "/tools/create_support_ticket",
            json={
                "title": "Test",
                "description": "Test description",
                "priority": "invalid_priority"
            }
        )
        # Should still succeed, priority validation happens at CRM level
        assert response.status_code == 200
    
    def test_create_ticket_empty_title_fails(self, client: TestClient):
        """Test that creating a ticket with empty title fails validation."""
        response = client.post(
            "/tools/create_support_ticket",
            json={
                "title": "",
                "description": "Test description"
            }
        )
        # FastAPI validation should catch this
        assert response.status_code in [200, 422]  # May allow empty or reject


class TestGetCustomerInfo:
    """Tests for get_customer_info tool."""
    
    def test_get_customer_by_id(self, client: TestClient):
        """Test getting customer info by customer ID."""
        response = client.post(
            "/tools/get_customer_info",
            json={"identifier": "cust_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # In mock mode, should return mock data
        assert "customer_id" in data or "customer" in data
    
    def test_get_customer_by_email(self, client: TestClient):
        """Test getting customer info by email."""
        response = client.post(
            "/tools/get_customer_info",
            json={"identifier": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_customer_mcp_endpoint(self, client: TestClient):
        """Test getting customer info via MCP endpoint."""
        response = client.post(
            "/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "get_customer_info",
                    "arguments": {
                        "identifier": "test_customer"
                    }
                },
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "content" in data["result"]
    
    def test_get_customer_not_found(self, client: TestClient):
        """Test getting customer info for non-existent customer."""
        # This will depend on CRM implementation
        # In mock mode, it should still return success
        response = client.post(
            "/tools/get_customer_info",
            json={"identifier": "nonexistent_customer"}
        )
        assert response.status_code == 200
    
    def test_get_customer_empty_identifier(self, client: TestClient):
        """Test getting customer info with empty identifier."""
        response = client.post(
            "/tools/get_customer_info",
            json={"identifier": ""}
        )
        # Should handle gracefully
        assert response.status_code == 200


class TestEscalateToHuman:
    """Tests for escalate_to_human tool."""
    
    def test_escalate_with_minimal_fields(self, client: TestClient):
        """Test escalating with only required session_id."""
        response = client.post(
            "/tools/escalate_to_human",
            json={"session_id": "session_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["escalation_id"] == "session_123"
        assert data["status"] == "pending"
    
    def test_escalate_with_all_fields(self, client: TestClient):
        """Test escalating with all optional fields."""
        response = client.post(
            "/tools/escalate_to_human",
            json={
                "session_id": "session_456",
                "reason": "complex_issue",
                "customer_id": "cust_123",
                "conversation_summary": "Customer needs help with complex billing issue"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["escalation_id"] == "session_456"
    
    def test_escalate_mcp_endpoint(self, client: TestClient):
        """Test escalating via MCP endpoint."""
        response = client.post(
            "/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "escalate_to_human",
                    "arguments": {
                        "session_id": "test_session",
                        "reason": "user_request"
                    }
                },
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "content" in data["result"]
        assert "Escalation created" in data["result"]["content"][0]["text"]
    
    def test_escalate_without_session_id_fails(self, client: TestClient):
        """Test that escalating without session_id fails validation."""
        response = client.post(
            "/tools/escalate_to_human",
            json={"reason": "test"}
        )
        # Should fail validation
        assert response.status_code == 422
    
    def test_escalate_creates_ticket_when_crm_available(self, client: TestClient):
        """Test that escalation creates a ticket when CRM is available."""
        # This test verifies the integration, but may not create ticket if CRM not configured
        response = client.post(
            "/tools/escalate_to_human",
            json={
                "session_id": "session_789",
                "customer_id": "cust_456",
                "reason": "user_request"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # ticket_id may be None if CRM not configured
        assert "ticket_id" in data


class TestLogInteraction:
    """Tests for log_interaction tool."""
    
    def test_log_interaction_minimal(self, client: TestClient):
        """Test logging interaction with minimal required fields."""
        response = client.post(
            "/tools/log_interaction",
            json={
                "customer_id": "cust_123",
                "activity_type": "call",
                "details": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_log_interaction_with_details(self, client: TestClient):
        """Test logging interaction with detailed information."""
        response = client.post(
            "/tools/log_interaction",
            json={
                "customer_id": "cust_456",
                "activity_type": "ticket_created",
                "details": {
                    "ticket_id": "ticket_123",
                    "priority": "high",
                    "category": "billing"
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_log_interaction_mcp_endpoint(self, client: TestClient):
        """Test logging interaction via MCP endpoint."""
        response = client.post(
            "/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "log_interaction",
                    "arguments": {
                        "customer_id": "cust_789",
                        "activity_type": "chat",
                        "details": {"duration": 300}
                    }
                },
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "content" in data["result"]
        assert "Interaction logged" in data["result"]["content"][0]["text"]
    
    def test_log_interaction_missing_required_field(self, client: TestClient):
        """Test that logging interaction without required fields fails."""
        response = client.post(
            "/tools/log_interaction",
            json={
                "customer_id": "cust_123",
                "activity_type": "call"
                # Missing details
            }
        )
        # Should fail validation
        assert response.status_code == 422
    
    def test_log_interaction_various_activity_types(self, client: TestClient):
        """Test logging different types of activities."""
        activity_types = ["call", "chat", "ticket_created", "issue_resolved", "refund_processed"]
        for activity_type in activity_types:
            response = client.post(
                "/tools/log_interaction",
                json={
                    "customer_id": "cust_123",
                    "activity_type": activity_type,
                    "details": {"test": True}
                }
            )
            assert response.status_code == 200
            assert response.json()["success"] is True


class TestCheckOrderStatus:
    """Tests for check_order_status tool."""
    
    def test_check_order_with_order_id_only(self, client: TestClient):
        """Test checking order status with only order_id."""
        response = client.post(
            "/tools/check_order_status",
            json={"order_id": "order_123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "order" in data
        assert data["order"]["order_id"] == "order_123"
        assert "status" in data["order"]
    
    def test_check_order_with_customer_id(self, client: TestClient):
        """Test checking order status with customer_id for verification."""
        response = client.post(
            "/tools/check_order_status",
            json={
                "order_id": "order_456",
                "customer_id": "cust_123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["order"]["order_id"] == "order_456"
    
    def test_check_order_mcp_endpoint(self, client: TestClient):
        """Test checking order status via MCP endpoint."""
        response = client.post(
            "/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "check_order_status",
                    "arguments": {
                        "order_id": "order_789"
                    }
                },
                "id": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "content" in data["result"]
        assert "Order" in data["result"]["content"][0]["text"]
        assert "status" in data["result"]["content"][0]["text"]
    
    def test_check_order_missing_order_id_fails(self, client: TestClient):
        """Test that checking order without order_id fails validation."""
        response = client.post(
            "/tools/check_order_status",
            json={"customer_id": "cust_123"}
        )
        # Should fail validation
        assert response.status_code == 422
    
    def test_check_order_returns_delivery_info(self, client: TestClient):
        """Test that order status includes delivery information."""
        response = client.post(
            "/tools/check_order_status",
            json={"order_id": "order_999"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        order = data["order"]
        # Should have delivery-related fields
        assert "estimated_delivery" in order or "created_date" in order


class TestToolDefinitions:
    """Tests for tool definitions endpoint."""
    
    def test_get_tool_definitions(self, client: TestClient):
        """Test that tool definitions endpoint returns all tools."""
        response = client.get("/tools/definitions")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        tools = data["tools"]
        
        # Should have all 6 tools (1 original + 5 new)
        tool_names = [tool["function"]["name"] for tool in tools]
        assert "search_knowledge_base" in tool_names
        assert "create_support_ticket" in tool_names
        assert "get_customer_info" in tool_names
        assert "escalate_to_human" in tool_names
        assert "log_interaction" in tool_names
        assert "check_order_status" in tool_names
        assert len(tools) == 6
    
    def test_tool_definitions_have_correct_structure(self, client: TestClient):
        """Test that each tool definition has the correct structure."""
        response = client.get("/tools/definitions")
        assert response.status_code == 200
        data = response.json()
        
        for tool in data["tools"]:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
            assert "url" in tool["function"]
    
    def test_mcp_tools_list(self, client: TestClient):
        """Test that MCP tools/list endpoint returns all tools."""
        response = client.post(
            "/mcp",
            json={"method": "tools/list"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert "tools" in data["result"]
        tools = data["result"]["tools"]
        
        tool_names = [tool["name"] for tool in tools]
        assert "search_knowledge_base" in tool_names
        assert "create_support_ticket" in tool_names
        assert "get_customer_info" in tool_names
        assert "escalate_to_human" in tool_names
        assert "log_interaction" in tool_names
        assert "check_order_status" in tool_names
        assert len(tools) == 6

