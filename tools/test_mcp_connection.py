"""
Test MCP server connection to debug ElevenLabs integration.

This script tests the MCP endpoint to see what responses we're getting
and helps identify connection issues.
"""
from __future__ import annotations

import sys
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

def test_get_endpoint(base_url: str = "https://supagent-production.up.railway.app"):
    """Test the GET endpoint (SSE)."""
    print(f"\n=== Testing GET /mcp (SSE) ===")
    url = f"{base_url}/mcp"
    
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(url, headers={
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            })
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            # Try to read first few lines of the stream
            if response.status_code == 200:
                print("\nFirst 500 chars of response:")
                content = response.text[:500]
                print(content)
                if len(response.text) > 500:
                    print("... (truncated)")
    except Exception as e:
        print(f"Error: {e}")


def test_post_initialize(base_url: str = "https://supagent-production.up.railway.app"):
    """Test POST with initialize request."""
    print(f"\n=== Testing POST /mcp (initialize) ===")
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
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


def test_post_tools_list(base_url: str = "https://supagent-production.up.railway.app"):
    """Test POST with tools/list request."""
    print(f"\n=== Testing POST /mcp (tools/list) ===")
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
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            if "result" in data and "tools" in data["result"]:
                print(f"Number of tools: {len(data['result']['tools'])}")
                print(f"Tool names: {[t.get('name') for t in data['result']['tools'][:5]]}")
            else:
                print(f"Full response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all tests."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://supagent-production.up.railway.app"
    print(f"Testing MCP server at: {base_url}")
    
    test_get_endpoint(base_url)
    test_post_initialize(base_url)
    test_post_tools_list(base_url)
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()

