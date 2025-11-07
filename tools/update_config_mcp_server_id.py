"""
Update the MCP server ID in the environment configuration.

This script updates ELEVENLABS_MCP_SERVER_ID to match the server ID
that the dashboard is actually using.
"""
from __future__ import annotations

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from core.secrets import get_elevenlabs_api_key
from elevenlabs.client import ElevenLabs


def update_env_file(server_id: str):
    """Update .env file with new MCP server ID."""
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print(f"ERROR: .env file not found at {env_file}")
        return False
    
    # Read current .env file
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update or add ELEVENLABS_MCP_SERVER_ID
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("ELEVENLABS_MCP_SERVER_ID="):
            new_lines.append(f"ELEVENLABS_MCP_SERVER_ID={server_id}\n")
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        # Add it if it doesn't exist
        new_lines.append(f"ELEVENLABS_MCP_SERVER_ID={server_id}\n")
    
    # Write back
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Updated .env file with ELEVENLABS_MCP_SERVER_ID={server_id}")
    return True


def main():
    """Update config to use the correct MCP server ID."""
    # The server ID from the dashboard
    dashboard_server_id = "oXqU9rXMmQs80UHgQ3RF"
    
    print("Updating MCP Server ID Configuration")
    print("=" * 60)
    print(f"Dashboard Server ID: {dashboard_server_id}")
    
    # Verify this server exists and has dependent agents
    api_key = get_elevenlabs_api_key()
    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY not set")
        sys.exit(1)
    
    client = ElevenLabs(api_key=api_key)
    
    # Get server details
    try:
        result = client.conversational_ai.mcp_servers.list()
        
        if hasattr(result, 'mcp_servers'):
            servers = result.mcp_servers
        elif isinstance(result, dict) and 'mcp_servers' in result:
            servers = result['mcp_servers']
        elif isinstance(result, list):
            servers = result
        else:
            servers = []
        
        # Find the server
        found_server = None
        for server in servers:
            server_id = getattr(server, 'id', None) or (server.get('id') if isinstance(server, dict) else None)
            if server_id == dashboard_server_id:
                found_server = server
                break
        
        if not found_server:
            print(f"ERROR: Server {dashboard_server_id} not found")
            sys.exit(1)
        
        # Check dependent agents
        dependent_agents = getattr(found_server, 'dependent_agents', None) or (found_server.get('dependent_agents') if isinstance(found_server, dict) else None)
        agent_count = len(dependent_agents) if dependent_agents else 0
        
        # Get URL
        config_obj = getattr(found_server, 'config', None) or (found_server.get('config') if isinstance(found_server, dict) else None)
        if hasattr(config_obj, 'url'):
            url = config_obj.url
        elif isinstance(config_obj, dict):
            url = config_obj.get('url', '')
        else:
            url = ''
        
        print(f"\nServer Details:")
        print(f"  ID: {dashboard_server_id}")
        print(f"  URL: {url}")
        print(f"  Dependent Agents: {agent_count}")
        
        if agent_count > 0:
            print(f"\n[OK] This server has {agent_count} dependent agent(s) - this is the correct one!")
        else:
            print(f"\n[WARNING] This server has no dependent agents")
        
        # Update .env file
        print(f"\nUpdating .env file...")
        if update_env_file(dashboard_server_id):
            print(f"\n[SUCCESS] Configuration updated!")
            print(f"\nNext steps:")
            print(f"  1. Restart your application to load the new config")
            print(f"  2. The dashboard should now show the correct server")
            return 0
        else:
            print(f"\n[ERROR] Failed to update .env file")
            return 1
            
    except Exception as e:
        print(f"[ERROR] Failed to verify server: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

