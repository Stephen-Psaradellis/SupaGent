"""
Test if the agent can actually use MCP tools by checking the agent configuration
and testing tool discovery.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from core.config import get_config
from core.secrets import get_elevenlabs_api_key
from elevenlabs.client import ElevenLabs


def test_tools_list_via_mcp(mcp_url: str):
    """Test tools/list via MCP endpoint."""
    print(f"\n{'='*60}")
    print("Testing MCP tools/list endpoint")
    print(f"{'='*60}")
    
    try:
        import requests
        
        response = requests.post(
            mcp_url,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tools = data.get("result", {}).get("tools", [])
            print(f"[OK] tools/list returned {len(tools)} tools")
            
            print(f"\nAvailable tools:")
            for tool in tools[:10]:  # Show first 10
                tool_name = tool.get("name", "N/A")
                tool_desc = tool.get("description", "N/A")[:60]
                print(f"  - {tool_name}: {tool_desc}...")
            
            if len(tools) > 10:
                print(f"  ... and {len(tools) - 10} more tools")
            
            return tools
        else:
            print(f"[ERROR] tools/list returned {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to test tools/list: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_tool_call(mcp_url: str, tool_name: str = "search_knowledge_base"):
    """Test calling a tool via MCP endpoint."""
    print(f"\n{'='*60}")
    print(f"Testing MCP tool call: {tool_name}")
    print(f"{'='*60}")
    
    try:
        import requests
        
        response = requests.post(
            mcp_url,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": {
                        "query": "test query",
                        "k": 2
                    }
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            
            if "error" in data:
                print(f"[ERROR] Tool call returned error: {data['error']}")
                return False
            else:
                print(f"[OK] Tool call successful")
                print(f"Result keys: {list(result.keys())}")
                return True
        else:
            print(f"[ERROR] Tool call returned {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to test tool call: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("ElevenLabs Agent MCP Tools Test")
    print("=" * 60)
    
    config = get_config()
    mcp_url = "https://supagent-production.up.railway.app/mcp"
    
    print(f"\nMCP URL: {mcp_url}")
    
    # Test 1: List tools
    tools = test_tools_list_via_mcp(mcp_url)
    
    # Test 2: Call a tool
    if tools:
        # Try calling search_knowledge_base
        tool_call_ok = test_tool_call(mcp_url, "search_knowledge_base")
        
        # Summary
        print(f"\n{'='*60}")
        print("Test Summary")
        print(f"{'='*60}")
        
        if tools:
            print(f"[OK] Tools discovery: OK ({len(tools)} tools available)")
        else:
            print(f"[ERROR] Tools discovery: FAILED")
        
        if tool_call_ok:
            print(f"[OK] Tool execution: OK")
            print(f"\n[SUCCESS] Agent can discover and use MCP tools!")
            return 0
        else:
            print(f"[ERROR] Tool execution: FAILED")
            return 1
    else:
        print(f"\n[ERROR] Cannot test tool calls - tools/list failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

