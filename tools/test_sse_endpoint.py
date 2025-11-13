"""
Test the SSE endpoint to verify it sends tools list correctly.

This simulates what ElevenLabs does when scanning available tools.
"""
from __future__ import annotations

import sys
import json
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx


def test_sse_endpoint(base_url: str = "https://supagent-production.up.railway.app"):
    """
    Test the SSE endpoint to verify it sends initialization and tools.
    
    Args:
        base_url: Base URL of the MCP server
    """
    print(f"\n{'='*60}")
    print("Testing MCP SSE Endpoint")
    print(f"{'='*60}")
    print(f"URL: {base_url}/mcp")
    print(f"Transport: SSE (Server-Sent Events)")
    print()
    
    url = f"{base_url}/mcp"
    
    try:
        with httpx.Client(timeout=30.0) as client:
            print("📡 Opening SSE connection...")
            
            # Open SSE connection
            with client.stream("GET", url, headers={
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            }) as response:
                print(f"✅ Connection established (Status: {response.status_code})")
                print(f"Content-Type: {response.headers.get('content-type')}")
                print()
                
                if response.status_code != 200:
                    print(f"❌ Error: Expected 200, got {response.status_code}")
                    return False
                
                # Read SSE events
                print("📥 Reading SSE events...\n")
                
                events_received = []
                line_buffer = ""
                event_count = 0
                
                # Read for 10 seconds or until we get both initialization and tools
                start_time = time.time()
                max_wait = 10
                
                for chunk in response.iter_text():
                    line_buffer += chunk
                    
                    # Process complete lines
                    while '\n' in line_buffer:
                        line, line_buffer = line_buffer.split('\n', 1)
                        
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            try:
                                event = json.loads(data)
                                event_count += 1
                                events_received.append(event)
                                
                                method = event.get('method', 'unknown')
                                print(f"📨 Event #{event_count}: {method}")
                                
                                # Print event details
                                if method == "notifications/initialized":
                                    params = event.get('params', {})
                                    server_info = params.get('serverInfo', {})
                                    print(f"   Server: {server_info.get('name', 'N/A')}")
                                    print(f"   Version: {server_info.get('version', 'N/A')}")
                                    print(f"   Protocol: {params.get('protocolVersion', 'N/A')}")
                                
                                elif method == "notifications/tools/list_changed":
                                    tools = event.get('params', {}).get('tools', [])
                                    print(f"   Tools count: {len(tools)}")
                                    print(f"   Tools:")
                                    for tool in tools[:5]:
                                        tool_name = tool.get('name', 'N/A')
                                        tool_desc = tool.get('description', 'N/A')[:60]
                                        print(f"     - {tool_name}: {tool_desc}")
                                    if len(tools) > 5:
                                        print(f"     ... and {len(tools) - 5} more")
                                
                                print()
                                
                            except json.JSONDecodeError as e:
                                print(f"⚠️  Failed to parse event: {e}")
                                print(f"   Data: {data[:100]}")
                        
                        elif line.startswith(':'):
                            # Keepalive comment
                            pass
                        elif line.strip() == '':
                            # Empty line (event separator)
                            pass
                    
                    # Check if we have both initialization and tools
                    has_init = any(e.get('method') == 'notifications/initialized' for e in events_received)
                    has_tools = any(e.get('method') == 'notifications/tools/list_changed' for e in events_received)
                    
                    if has_init and has_tools:
                        print("✅ Received both initialization and tools list!")
                        break
                    
                    # Check timeout
                    if time.time() - start_time > max_wait:
                        print(f"⏱️  Timeout after {max_wait} seconds")
                        break
                
                # Summary
                print(f"\n{'='*60}")
                print("Summary")
                print(f"{'='*60}")
                print(f"Events received: {event_count}")
                
                has_init = any(e.get('method') == 'notifications/initialized' for e in events_received)
                has_tools = any(e.get('method') == 'notifications/tools/list_changed' for e in events_received)
                
                print(f"Initialization: {'✅' if has_init else '❌'}")
                print(f"Tools list: {'✅' if has_tools else '❌'}")
                
                if has_tools:
                    tools_event = next((e for e in events_received if e.get('method') == 'notifications/tools/list_changed'), None)
                    if tools_event:
                        tools_count = len(tools_event.get('params', {}).get('tools', []))
                        print(f"Tools count: {tools_count}")
                
                if has_init and has_tools:
                    print(f"\n{'='*60}")
                    print("🎉 SUCCESS! SSE endpoint is working correctly!")
                    print("ElevenLabs should now be able to scan available tools.")
                    print(f"{'='*60}")
                    return True
                else:
                    print(f"\n{'='*60}")
                    print("❌ FAILED! SSE endpoint is not sending required events.")
                    if not has_init:
                        print("  Missing: initialization event")
                    if not has_tools:
                        print("  Missing: tools list event")
                    print(f"{'='*60}")
                    return False
                
    except httpx.TimeoutException:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("MCP SSE Endpoint Test")
    print("=" * 60)
    print("This test simulates what ElevenLabs does when scanning tools.")
    print()
    
    # Test production endpoint
    success = test_sse_endpoint("https://supagent-production.up.railway.app")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())









