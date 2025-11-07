"""
Test MCP POST endpoint to verify it returns proper HTTP responses.
"""
from __future__ import annotations

import sys
import json
import requests
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_initialize(base_url: str = "https://supagent-production.up.railway.app"):
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
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Check if it's a proper MCP response
        if "result" in data and "protocolVersion" in data["result"]:
            print("\n[OK] Received proper MCP initialize response")
            return True
        elif "status" in data and data["status"] == "sent_via_sse":
            print("\n[ERROR] Response indicates SSE, but should return HTTP for validation")
            return False
        else:
            print("\n[ERROR] Unexpected response format")
            return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools_list(base_url: str = "https://supagent-production.up.railway.app"):
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
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        
        # Check if it's a proper MCP response
        if "result" in data and "tools" in data["result"]:
            tools = data["result"]["tools"]
            print(f"[OK] Received proper MCP tools/list response with {len(tools)} tools")
            print(f"First 3 tools: {[t.get('name') for t in tools[:3]]}")
            return True
        elif "status" in data and data["status"] == "sent_via_sse":
            print("\n[ERROR] Response indicates SSE, but should return HTTP for validation")
            return False
        else:
            print(f"\n[ERROR] Unexpected response format: {json.dumps(data, indent=2)}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://supagent-production.up.railway.app"
    print(f"Testing MCP POST endpoint at: {base_url}")
    
    init_ok = test_initialize(base_url)
    tools_ok = test_tools_list(base_url)
    
    print("\n=== Test Summary ===")
    print(f"Initialize: {'PASS' if init_ok else 'FAIL'}")
    print(f"Tools/List: {'PASS' if tools_ok else 'FAIL'}")
    
    if init_ok and tools_ok:
        print("\n[SUCCESS] All tests passed! MCP endpoint should work with ElevenLabs dashboard.")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Fix issues before testing in dashboard.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

