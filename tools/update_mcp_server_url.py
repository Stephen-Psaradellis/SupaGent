"""
Update MCP server URL to use Railway production URL.

This script updates the existing MCP server configuration in ElevenLabs
to use the production Railway URL instead of localhost.
"""
from __future__ import annotations

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Update MCP server URL to production."""
    try:
        from core.config import get_config
        from core.secrets import get_elevenlabs_api_key
        from elevenlabs.client import ElevenLabs
        
        config = get_config()
        api_key = get_elevenlabs_api_key()
        mcp_server_id = config.elevenlabs_mcp_server_id
        
        if not api_key:
            print("Error: ELEVENLABS_API_KEY not set in Doppler", file=sys.stderr)
            sys.exit(1)
        
        if not mcp_server_id:
            print("Error: ELEVENLABS_MCP_SERVER_ID not set", file=sys.stderr)
            sys.exit(1)
        
        # Use Railway production URL
        production_url = "https://supagent-production.up.railway.app"
        
        print(f"Updating MCP server {mcp_server_id} to use production URL: {production_url}", file=sys.stderr)
        
        client = ElevenLabs(api_key=api_key)
        
        # Check if we can update the MCP server
        if not hasattr(client, 'conversational_ai') or not hasattr(client.conversational_ai, 'mcp_servers'):
            print("Error: ElevenLabs SDK does not support MCP server updates", file=sys.stderr)
            sys.exit(1)
        
        # Try to get the existing server first
        try:
            mcp_servers = client.conversational_ai.mcp_servers.list()
            existing_server = None
            for server in getattr(mcp_servers, 'servers', []):
                if getattr(server, 'id', None) == mcp_server_id:
                    existing_server = server
                    break
            
            if not existing_server:
                print(f"Warning: MCP server {mcp_server_id} not found. Creating new one...", file=sys.stderr)
                # Create new server with production URL
                mcp_config = {
                    "url": f"{production_url}/mcp",
                    "name": config.mcp_server_name,
                    "description": "SupaGent Knowledge Base MCP Server - Provides access to customer support documentation via vector store search",
                    "transport": "SSE",
                    "approval_policy": "auto_approve_all",
                }
                result = client.conversational_ai.mcp_servers.create(config=mcp_config)
                new_server_id = getattr(result, 'id', None)
                if new_server_id:
                    print(f"✓ Created new MCP server with production URL: {new_server_id}", file=sys.stderr)
                    print(f"Update ELEVENLABS_MCP_SERVER_ID={new_server_id} in your .env file", file=sys.stderr)
                    return 0
                else:
                    print("Error: Failed to create new MCP server", file=sys.stderr)
                    sys.exit(1)
        except Exception as e:
            print(f"Error checking existing server: {e}", file=sys.stderr)
            # Try to create a new one anyway
            pass
        
        # Try to update the server (if the API supports it)
        # Note: The ElevenLabs SDK might not have an update method, so we may need to delete and recreate
        print("Note: ElevenLabs API may not support updating MCP servers directly.", file=sys.stderr)
        print("You may need to:", file=sys.stderr)
        print("1. Delete the old MCP server in ElevenLabs dashboard", file=sys.stderr)
        print("2. Run this script again to create a new one with the production URL", file=sys.stderr)
        print(f"3. Or manually update the MCP server URL in ElevenLabs dashboard to: {production_url}/mcp", file=sys.stderr)
        
        # Try to create a new server with a different name to avoid conflicts
        try:
            mcp_config = {
                "url": f"{production_url}/mcp",
                "name": f"{config.mcp_server_name} (Production)",
                "description": "SupaGent Knowledge Base MCP Server - Production",
                "transport": "SSE",
                "approval_policy": "auto_approve_all",
            }
            result = client.conversational_ai.mcp_servers.create(config=mcp_config)
            new_server_id = getattr(result, 'id', None)
            if new_server_id:
                print(f"\n✓ Created new MCP server with production URL: {new_server_id}", file=sys.stderr)
                print(f"New server URL: {production_url}/mcp", file=sys.stderr)
                print(f"\nNext steps:", file=sys.stderr)
                print(f"1. Update ELEVENLABS_MCP_SERVER_ID={new_server_id} in your .env file", file=sys.stderr)
                print(f"2. Run: python -m tools.update_agent_mcp", file=sys.stderr)
                return 0
        except Exception as e:
            print(f"Error creating new server: {e}", file=sys.stderr)
            print(f"\nPlease manually update the MCP server URL in ElevenLabs dashboard to: {production_url}/mcp", file=sys.stderr)
            sys.exit(1)
        
        return 0
    except Exception as e:
        print(f"Error: Failed to update MCP server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())

