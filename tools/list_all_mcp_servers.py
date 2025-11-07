"""
List all MCP servers to see which ones exist.
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

from core.secrets import get_elevenlabs_api_key
from elevenlabs.client import ElevenLabs


def main():
    """List all MCP servers."""
    api_key = get_elevenlabs_api_key()
    
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not set")
        sys.exit(1)
    
    print("Listing All MCP Servers")
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
    
    print(f"\nFound {len(servers)} MCP server(s):\n")
    
    for i, server in enumerate(servers, 1):
        server_id = getattr(server, 'id', None) or (server.get('id') if isinstance(server, dict) else None)
        
        # Get config
        config_obj = getattr(server, 'config', None) or (server.get('config') if isinstance(server, dict) else None)
        
        if hasattr(config_obj, 'url'):
            url = config_obj.url
        elif isinstance(config_obj, dict):
            url = config_obj.get('url', '')
        else:
            url = ''
        
        # Get metadata
        metadata = getattr(server, 'metadata', None) or (server.get('metadata') if isinstance(server, dict) else None)
        name = ''
        if metadata:
            if hasattr(metadata, 'name'):
                name = metadata.name
            elif isinstance(metadata, dict):
                name = metadata.get('name', '')
        
        # Check dependent agents
        dependent_agents = getattr(server, 'dependent_agents', None) or (server.get('dependent_agents') if isinstance(server, dict) else None)
        agent_count = len(dependent_agents) if dependent_agents else 0
        
        print(f"{i}. Server ID: {server_id}")
        print(f"   Name: {name}")
        print(f"   URL: {url}")
        print(f"   Dependent Agents: {agent_count}")
        if server_id == "oXqU9rXMmQs80UHgQ3RF":
            print(f"   *** THIS IS THE ONE IN THE DASHBOARD ***")
        if server_id == "G1zpU0GHr8MZp3UwIeBR":
            print(f"   *** THIS IS THE ONE IN CONFIG ***")
        print()


if __name__ == "__main__":
    main()

