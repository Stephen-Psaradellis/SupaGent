"""
Test script for MCP SDK-based implementation.

This script tests the new SDK-based MCP endpoint to ensure it works correctly
before switching from the custom implementation.

Usage:
    python tools/test_mcp_sdk.py [base_url]
    
Example:
    python tools/test_mcp_sdk.py https://supagent-production.up.railway.app
"""
from __future__ import annotations

import sys
import json
import httpx
from dotenv import load_dotenv

load_dotenv()


def test_health_check(base_url: str) -> bool:
    """Test the health check endpoint."""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    url = f"{base_url}/mcp/health"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Server: {data.get('server_name')}")
                print(f"   Tool count: {data.get('tool_count')}")
                print(f"   Tools: {', '.join(data.get('tools', [])[:5])}...")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_initialize(base_url: str) -> bool:
    """Test the initialize endpoint."""
    print("\n" + "=" * 60)
    print("TEST 2: Initialize (Protocol Handshake)")
    print("=" * 60)
    
    url = f"{base_url}/mcp"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Initialize successful")
                print(f"   Protocol: {data.get('result', {}).get('protocolVersion')}")
                print(f"   Server: {data.get('result', {}).get('serverInfo', {}).get('name')}")
                print(f"   Capabilities: {list(data.get('result', {}).get('capabilities', {}).keys())}")
                return True
            else:
                print(f"❌ Initialize failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_tools_list(base_url: str) -> bool:
    """Test the tools/list endpoint."""
    print("\n" + "=" * 60)
    print("TEST 3: List Tools")
    print("=" * 60)
    
    url = f"{base_url}/mcp"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("result", {}).get("tools", [])
                print(f"✅ Tools list successful")
                print(f"   Tool count: {len(tools)}")
                print(f"\n   Available tools:")
                for i, tool in enumerate(tools, 1):
                    print(f"   {i}. {tool.get('name')}")
                    required = tool.get('inputSchema', {}).get('required', [])
                    if required:
                        print(f"      Required params: {', '.join(required)}")
                return True
            else:
                print(f"❌ Tools list failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_tool_call(base_url: str) -> bool:
    """Test calling a tool."""
    print("\n" + "=" * 60)
    print("TEST 4: Call Tool (search_knowledge_base)")
    print("=" * 60)
    
    url = f"{base_url}/mcp"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_knowledge_base",
            "arguments": {
                "query": "test query",
                "k": 2
            }
        }
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    print(f"✅ Tool call successful")
                    content = data.get("result", {}).get("content", [])
                    print(f"   Response items: {len(content)}")
                    if content and len(content) > 0:
                        first_content = content[0]
                        text = first_content.get("text", "")
                        preview = text[:200] + "..." if len(text) > 200 else text
                        print(f"   Preview: {preview}")
                    return True
                else:
                    print(f"⚠️  Tool call returned error: {data.get('error', {}).get('message')}")
                    return False
            else:
                print(f"❌ Tool call failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_sse_connection(base_url: str) -> bool:
    """Test SSE connection (GET endpoint)."""
    print("\n" + "=" * 60)
    print("TEST 5: SSE Connection")
    print("=" * 60)
    
    url = f"{base_url}/mcp"
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                url,
                headers={
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache"
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                if "text/event-stream" in response.headers.get("content-type", ""):
                    print(f"✅ SSE connection established")
                    print(f"   First 300 chars:")
                    content = response.text[:300]
                    print(f"   {content}")
                    return True
                else:
                    print(f"⚠️  Wrong content type: {response.headers.get('content-type')}")
                    return False
            else:
                print(f"❌ SSE connection failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_sdk_version(base_url: str) -> None:
    """Verify the endpoint is using SDK implementation."""
    print("\n" + "=" * 60)
    print("VERIFICATION: SDK Implementation")
    print("=" * 60)
    
    print("\nChecking /mcp endpoint...")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{base_url}/mcp/health")
            if response.status_code == 200:
                data = response.json()
                sdk_version = data.get("sdk_version", "unknown")
                if sdk_version == "official":
                    print(f"   ✅ Using official MCP SDK")
                    print(f"   Server: {data.get('server_name')}")
                    print(f"   Tools: {data.get('tool_count')}")
                else:
                    print(f"   ⚠️  SDK version unclear: {sdk_version}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")


def main():
    """Run all tests."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print("=" * 60)
    print("MCP SDK Implementation Test Suite")
    print("=" * 60)
    print(f"Testing: {base_url}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check(base_url)))
    results.append(("Initialize", test_initialize(base_url)))
    results.append(("Tools List", test_tools_list(base_url)))
    results.append(("Tool Call", test_tool_call(base_url)))
    results.append(("SSE Connection", test_sse_connection(base_url)))
    
    # Verify SDK implementation
    verify_sdk_version(base_url)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! SDK implementation is working correctly.")
        print("\nThe /mcp endpoint is now powered by the official MCP Python SDK.")
        print("No URL changes needed - same endpoint, better implementation!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

