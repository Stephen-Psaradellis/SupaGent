"""
Test ElevenLabs Agent connectivity to MCP server and tools.

This script uses the ElevenLabs API to verify:
1. Agent configuration includes MCP server access
2. MCP server is properly configured
3. Tools are accessible
4. Connection is working
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


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")


def test_mcp_servers(client: ElevenLabs) -> dict | None:
    """Test listing MCP servers."""
    print_section("Testing MCP Servers List")
    
    try:
        result = client.conversational_ai.mcp_servers.list()
        
        # Handle different response formats
        if hasattr(result, 'mcp_servers'):
            servers = result.mcp_servers
        elif isinstance(result, dict) and 'mcp_servers' in result:
            servers = result['mcp_servers']
        elif isinstance(result, list):
            servers = result
        else:
            servers = []
        
        print(f"Found {len(servers)} MCP server(s):")
        
        for server in servers:
            server_id = getattr(server, 'id', None) or (server.get('id') if isinstance(server, dict) else None)
            server_name = getattr(server, 'name', None) or (server.get('name') if isinstance(server, dict) else None)
            config = getattr(server, 'config', None) or (server.get('config') if isinstance(server, dict) else None)
            
            if isinstance(config, dict):
                url = config.get('url', 'N/A')
                transport = config.get('transport', 'N/A')
            else:
                url = getattr(config, 'url', 'N/A') if config else 'N/A'
                transport = getattr(config, 'transport', 'N/A') if config else 'N/A'
            
            print(f"  - ID: {server_id}")
            print(f"    Name: {server_name}")
            print(f"    URL: {url}")
            print(f"    Transport: {transport}")
            print()
        
        return {"servers": servers, "count": len(servers)}
        
    except Exception as e:
        print(f"ERROR: Failed to list MCP servers: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_agent_config(client: ElevenLabs, agent_id: str) -> dict | None:
    """Test getting agent configuration."""
    print_section(f"Testing Agent Configuration (ID: {agent_id})")
    
    try:
        agent = client.conversational_ai.agents.get(agent_id=agent_id)
        
        # Get agent name and ID directly from object
        agent_name = getattr(agent, 'name', 'N/A')
        agent_id_actual = getattr(agent, 'agent_id', agent_id)
        print(f"Agent Name: {agent_name}")
        print(f"Agent ID: {agent_id_actual}")
        
        # Get conversation config directly from object
        conv_config_obj = getattr(agent, 'conversation_config', None)
        
        # Access nested config using attributes
        mcp_server_ids = []
        knowledge_base = []
        tools = []
        
        if conv_config_obj:
            # Try to access agent config
            agent_config = getattr(conv_config_obj, 'agent', None)
            if agent_config:
                prompt_config = getattr(agent_config, 'prompt', None)
                if prompt_config:
                    mcp_server_ids = getattr(prompt_config, 'mcp_server_ids', []) or []
                    knowledge_base = getattr(prompt_config, 'knowledge_base', []) or []
            
            # Get tools
            tools = getattr(conv_config_obj, 'tools', []) or []
        
        print(f"\nConversation Config:")
        print(f"  Has agent config: {agent_config is not None}")
        print(f"  Has prompt config: {prompt_config is not None if 'prompt_config' in locals() else False}")
        
        print(f"\nMCP Server IDs: {mcp_server_ids}")
        print(f"Knowledge Base IDs: {knowledge_base}")
        
        if mcp_server_ids:
            print(f"[OK] Agent has {len(mcp_server_ids)} MCP server(s) configured")
        else:
            print(f"[ERROR] Agent has NO MCP servers configured")
        
        # Check tools
        tools = conv_config.get('tools', [])
        print(f"\nTools configured: {len(tools)}")
        if tools:
            for tool in tools[:5]:  # Show first 5
                if isinstance(tool, dict):
                    tool_id = tool.get('tool_id', 'N/A')
                else:
                    tool_id = getattr(tool, 'tool_id', 'N/A')
                print(f"  - Tool ID: {tool_id}")
        
        return {
            "agent": agent_dict,
            "mcp_server_ids": mcp_server_ids,
            "knowledge_base": knowledge_base,
            "tools": tools
        }
        
    except Exception as e:
        print(f"ERROR: Failed to get agent config: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_mcp_server_details(client: ElevenLabs, mcp_server_id: str) -> dict | None:
    """Test getting specific MCP server details."""
    print_section(f"Testing MCP Server Details (ID: {mcp_server_id})")
    
    try:
        # Try to get server details - this might not be available in all API versions
        # So we'll try to find it in the list
        result = client.conversational_ai.mcp_servers.list()
        
        if hasattr(result, 'mcp_servers'):
            servers = result.mcp_servers
        elif isinstance(result, dict) and 'mcp_servers' in result:
            servers = result['mcp_servers']
        elif isinstance(result, list):
            servers = result
        else:
            servers = []
        
        for server in servers:
            server_id = getattr(server, 'id', None) or (server.get('id') if isinstance(server, dict) else None)
            
            if server_id == mcp_server_id:
                print(f"Found MCP server: {server_id}")
                
                config = getattr(server, 'config', None) or (server.get('config') if isinstance(server, dict) else None)
                metadata = getattr(server, 'metadata', None) or (server.get('metadata') if isinstance(server, dict) else None)
                access_info = getattr(server, 'access_info', None) or (server.get('access_info') if isinstance(server, dict) else None)
                
                # Convert Pydantic models to dicts if needed
                if config and hasattr(config, 'model_dump'):
                    config = config.model_dump()
                elif config and hasattr(config, 'dict'):
                    config = config.dict()
                if metadata and hasattr(metadata, 'model_dump'):
                    metadata = metadata.model_dump()
                elif metadata and hasattr(metadata, 'dict'):
                    metadata = metadata.dict()
                if access_info and hasattr(access_info, 'model_dump'):
                    access_info = access_info.model_dump()
                elif access_info and hasattr(access_info, 'dict'):
                    access_info = access_info.dict()
                
                print(f"\nConfiguration:")
                if isinstance(config, dict):
                    for key, value in config.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"  {config}")
                
                print(f"\nMetadata:")
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"  {metadata}")
                
                print(f"\nAccess Info:")
                if isinstance(access_info, dict):
                    for key, value in access_info.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"  {access_info}")
                
                return {
                    "server": server,
                    "config": config,
                    "metadata": metadata,
                    "access_info": access_info
                }
        
        print(f"[ERROR] MCP server {mcp_server_id} not found in list")
        return None
        
    except Exception as e:
        print(f"ERROR: Failed to get MCP server details: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_mcp_endpoint_connectivity(mcp_url: str) -> bool:
    """Test if MCP endpoint is reachable."""
    print_section(f"Testing MCP Endpoint Connectivity: {mcp_url}")
    
    try:
        import requests
        
        # Test GET (SSE connection)
        print(f"Testing GET request (SSE)...")
        response = requests.get(mcp_url, timeout=10, stream=True)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print(f"  [OK] GET endpoint is accessible")
        else:
            print(f"  [ERROR] GET endpoint returned {response.status_code}")
            return False
        
        # Test POST (MCP protocol)
        print(f"\nTesting POST request (MCP protocol)...")
        post_response = requests.post(
            mcp_url,
            json={
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
            },
            timeout=10
        )
        print(f"  Status: {post_response.status_code}")
        
        if post_response.status_code == 200:
            try:
                data = post_response.json()
                print(f"  Response: {json.dumps(data, indent=2)}")
                print(f"  [OK] POST endpoint is working")
                return True
            except:
                print(f"  [ERROR] POST endpoint returned non-JSON response")
                return False
        else:
            print(f"  [ERROR] POST endpoint returned {post_response.status_code}")
            return False
        
    except Exception as e:
        print(f"ERROR: Failed to test MCP endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("ElevenLabs Agent MCP Connectivity Test")
    print("=" * 60)
    
    # Get configuration
    config = get_config()
    api_key = get_elevenlabs_api_key()
    agent_id = config.elevenlabs_agent_id
    mcp_server_id = config.elevenlabs_mcp_server_id
    
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not set")
        sys.exit(1)
    
    if not agent_id:
        print("ERROR: ELEVENLABS_AGENT_ID not set")
        sys.exit(1)
    
    if not mcp_server_id:
        print("ERROR: ELEVENLABS_MCP_SERVER_ID not set")
        sys.exit(1)
    
    print(f"\nConfiguration:")
    print(f"  Agent ID: {agent_id}")
    print(f"  MCP Server ID: {mcp_server_id}")
    print(f"  Base URL: {config.base_url}")
    
    # Initialize client
    client = ElevenLabs(api_key=api_key)
    
    # Test 1: List MCP servers
    mcp_servers_result = test_mcp_servers(client)
    
    # Test 2: Get agent configuration
    agent_result = test_agent_config(client, agent_id)
    
    # Test 3: Get MCP server details
    mcp_server_result = test_mcp_server_details(client, mcp_server_id)
    
    # Test 4: Test MCP endpoint connectivity
    # Use production URL from MCP server config, not localhost
    if mcp_server_result and mcp_server_result.get('config'):
        config_obj = mcp_server_result['config']
        if isinstance(config_obj, dict):
            mcp_url = config_obj.get('url', config.get_mcp_endpoint())
        else:
            mcp_url = getattr(config_obj, 'url', config.get_mcp_endpoint())
    else:
        mcp_url = config.get_mcp_endpoint()
    
    # If it's localhost, try production URL instead
    if 'localhost' in mcp_url or '127.0.0.1' in mcp_url:
        mcp_url = "https://supagent-production.up.railway.app/mcp"
        print(f"\nNote: Using production URL for connectivity test: {mcp_url}")
    
    endpoint_ok = test_mcp_endpoint_connectivity(mcp_url)
    
    # Summary
    print_section("Test Summary")
    
    all_ok = True
    
    if mcp_servers_result:
        print(f"[OK] MCP servers list: OK ({mcp_servers_result['count']} servers)")
    else:
        print(f"[ERROR] MCP servers list: FAILED")
        all_ok = False
    
    if agent_result:
        mcp_ids = agent_result.get('mcp_server_ids', [])
        if mcp_server_id in mcp_ids:
            print(f"[OK] Agent MCP configuration: OK (server {mcp_server_id} is configured)")
        else:
            print(f"[ERROR] Agent MCP configuration: FAILED (server {mcp_server_id} not in agent config)")
            print(f"  Agent has: {mcp_ids}")
            all_ok = False
    else:
        print(f"[ERROR] Agent configuration: FAILED")
        all_ok = False
    
    if mcp_server_result:
        print(f"[OK] MCP server details: OK")
    else:
        print(f"[ERROR] MCP server details: FAILED (server not found)")
        all_ok = False
    
    if endpoint_ok:
        print(f"[OK] MCP endpoint connectivity: OK")
    else:
        print(f"[ERROR] MCP endpoint connectivity: FAILED")
        all_ok = False
    
    print(f"\n{'='*60}")
    if all_ok:
        print("[SUCCESS] ALL TESTS PASSED - Agent is properly configured and connected!")
        return 0
    else:
        print("[FAILED] SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

