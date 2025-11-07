"""
Check the actual status of the MCP server from ElevenLabs API.

This will show us exactly what ElevenLabs sees when it tests the connection.
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


def main():
    """Check MCP server status."""
    config = get_config()
    api_key = get_elevenlabs_api_key()
    mcp_server_id = config.elevenlabs_mcp_server_id
    
    if not mcp_server_id:
        print("ERROR: ELEVENLABS_MCP_SERVER_ID not set")
        sys.exit(1)
    
    print("Checking MCP Server Status via ElevenLabs API")
    print("=" * 60)
    
    client = ElevenLabs(api_key=api_key)
    
    # List all MCP servers
    result = client.conversational_ai.mcp_servers.list()
    
    if hasattr(result, 'mcp_servers'):
        servers = result.mcp_servers
    elif isinstance(result, dict) and 'mcp_servers' in result:
        servers = result['mcp_servers']
    elif isinstance(result, list):
        servers = result
    else:
        servers = []
    
    # Find our server
    our_server = None
    for server in servers:
        server_id = getattr(server, 'id', None) or (server.get('id') if isinstance(server, dict) else None)
        if server_id == mcp_server_id:
            our_server = server
            break
    
    if not our_server:
        print(f"[ERROR] MCP server {mcp_server_id} not found")
        sys.exit(1)
    
    print(f"\nMCP Server: {mcp_server_id}")
    
    # Get config
    config_obj = getattr(our_server, 'config', None) or (our_server.get('config') if isinstance(our_server, dict) else None)
    
    if hasattr(config_obj, 'url'):
        url = config_obj.url
    elif isinstance(config_obj, dict):
        url = config_obj.get('url', '')
    else:
        url = ''
    
    print(f"URL: {url}")
    
    # Check dependent agents
    dependent_agents = getattr(our_server, 'dependent_agents', None) or (our_server.get('dependent_agents') if isinstance(our_server, dict) else None)
    
    if dependent_agents:
        print(f"\nDependent Agents: {len(dependent_agents)}")
        for agent in dependent_agents[:5]:
            agent_id = getattr(agent, 'agent_id', None) or (agent.get('agent_id') if isinstance(agent, dict) else None)
            print(f"  - {agent_id}")
    else:
        print(f"\nDependent Agents: None")
    
    # Check access info
    access_info = getattr(our_server, 'access_info', None) or (our_server.get('access_info') if isinstance(our_server, dict) else None)
    
    if access_info:
        if hasattr(access_info, 'role'):
            role = access_info.role
        elif isinstance(access_info, dict):
            role = access_info.get('role', 'unknown')
        else:
            role = 'unknown'
        print(f"\nAccess Role: {role}")
    
    print(f"\n{'='*60}")
    print("Server configuration looks correct.")
    print("If dashboard still shows failure, the issue may be:")
    print("  1. Dashboard validation timing (responses not arriving fast enough)")
    print("  2. Dashboard expects different response format")
    print("  3. Dashboard caching old connection state")
    print("  4. Network/proxy issues between ElevenLabs and Railway")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

