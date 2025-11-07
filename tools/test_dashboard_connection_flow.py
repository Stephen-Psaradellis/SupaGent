"""
Simulate the exact connection flow that ElevenLabs dashboard uses.

This script mimics what the dashboard does when testing MCP server connection:
1. Opens SSE connection (GET)
2. Sends initialize POST request
3. Expects initialize response through SSE
4. Sends tools/list POST request
5. Expects tools/list response through SSE
"""
from __future__ import annotations

import sys
import json
import time
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import requests
from queue import Queue


def simulate_dashboard_connection_flow(mcp_url: str):
    """Simulate the exact flow the dashboard uses."""
    print("Simulating ElevenLabs Dashboard Connection Flow")
    print("=" * 60)
    
    sse_messages = Queue()
    connection_ok = False
    
    def read_sse_stream():
        """Read SSE stream in background thread."""
        try:
            response = requests.get(
                mcp_url,
                headers={
                    "Accept": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "User-Agent": "ElevenLabs-Dashboard/1.0"
                },
                stream=True,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"[ERROR] SSE connection failed: {response.status_code}")
                return
            
            print(f"[OK] SSE connection established (Status: {response.status_code})")
            
            # Read SSE messages
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # Remove 'data: ' prefix
                        try:
                            data = json.loads(data_str)
                            sse_messages.put(data)
                            print(f"[SSE] Received: {data.get('method', 'response')} (id: {data.get('id', 'N/A')})")
                        except json.JSONDecodeError:
                            pass
                    elif line_str.startswith(': '):
                        # Keepalive comment
                        pass
        except Exception as e:
            print(f"[ERROR] SSE stream error: {e}")
    
    # Start SSE connection in background
    print("\n1. Opening SSE connection...")
    sse_thread = threading.Thread(target=read_sse_stream, daemon=True)
    sse_thread.start()
    
    # Wait a moment for SSE connection to establish
    time.sleep(2)
    
    # Send initialize request
    print("\n2. Sending initialize POST request...")
    init_response = requests.post(
        mcp_url,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "ElevenLabs-Dashboard",
                    "version": "1.0.0"
                }
            }
        },
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ElevenLabs-Dashboard/1.0"
        },
        timeout=10
    )
    
    print(f"   POST Status: {init_response.status_code}")
    if init_response.status_code == 200:
        post_data = init_response.json()
        print(f"   POST Response: {json.dumps(post_data, indent=2)}")
    
    # Wait for initialize response in SSE
    print("\n3. Waiting for initialize response through SSE...")
    init_received = False
    for _ in range(10):  # Wait up to 5 seconds
        time.sleep(0.5)
        try:
            msg = sse_messages.get_nowait()
            if msg.get("id") == 1 and "result" in msg:
                print(f"[OK] Received initialize response through SSE!")
                print(f"     {json.dumps(msg, indent=2)}")
                init_received = True
                break
        except:
            pass
    
    if not init_received:
        print("[ERROR] Did not receive initialize response through SSE")
        return False
    
    # Send tools/list request
    print("\n4. Sending tools/list POST request...")
    tools_response = requests.post(
        mcp_url,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        headers={
            "Content-Type": "application/json",
            "User-Agent": "ElevenLabs-Dashboard/1.0"
        },
        timeout=10
    )
    
    print(f"   POST Status: {tools_response.status_code}")
    
    # Wait for tools/list response in SSE
    print("\n5. Waiting for tools/list response through SSE...")
    tools_received = False
    for _ in range(10):  # Wait up to 5 seconds
        time.sleep(0.5)
        try:
            msg = sse_messages.get_nowait()
            if msg.get("id") == 2 and "result" in msg:
                tools = msg.get("result", {}).get("tools", [])
                print(f"[OK] Received tools/list response through SSE!")
                print(f"     Found {len(tools)} tools")
                tools_received = True
                break
        except:
            pass
    
    if not tools_received:
        print("[ERROR] Did not receive tools/list response through SSE")
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Dashboard connection flow simulation PASSED!")
    print("All responses were received through SSE stream as expected.")
    return True


def main():
    """Main test function."""
    mcp_url = "https://supagent-production.up.railway.app/mcp"
    
    success = simulate_dashboard_connection_flow(mcp_url)
    
    if success:
        print("\nThe MCP server should work with the ElevenLabs dashboard.")
        return 0
    else:
        print("\nThe MCP server may not work correctly with the dashboard.")
        print("Responses need to come through SSE, not HTTP.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

