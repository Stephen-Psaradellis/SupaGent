"""
Update ElevenLabs agent to grant access to MCP server.

This script directly calls the ElevenLabs API to update the agent configuration
and grant it access to the configured MCP server.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Update the ElevenLabs agent with MCP server access."""
    try:
        from core.config import get_config
        from core.secrets import get_elevenlabs_api_key
        from agents.agent_testing import ElevenLabsAgentTester
        from agents.system_prompt import get_system_prompt
        
        config = get_config()
        api_key = get_elevenlabs_api_key()
        agent_id = config.elevenlabs_agent_id
        mcp_server_id = config.elevenlabs_mcp_server_id
        
        if not api_key:
            print("Error: ELEVENLABS_API_KEY not set in Doppler", file=sys.stderr)
            sys.exit(1)
        
        if not agent_id:
            print("Error: ELEVENLABS_AGENT_ID not set", file=sys.stderr)
            sys.exit(1)
        
        if not mcp_server_id:
            print("Error: ELEVENLABS_MCP_SERVER_ID not set. Please configure MCP server first.", file=sys.stderr)
            sys.exit(1)
        
        print(f"Updating agent {agent_id} with MCP server {mcp_server_id}...", file=sys.stderr)
        
        tester = ElevenLabsAgentTester(agent_id=agent_id, api_key=api_key)
        system_prompt = get_system_prompt()
        
        # Print what we're sending
        print(f"\nPayload being sent:", file=sys.stderr)
        print(f"  mcp_server_ids: [{mcp_server_id}]", file=sys.stderr)
        print(f"  prompt: (length {len(system_prompt)} chars)", file=sys.stderr)
        
        result = tester.update_agent(
            mcp_server_ids=[mcp_server_id],
            prompt=system_prompt
        )
        
        # Print the API response
        print(f"\nAPI Response:", file=sys.stderr)
        import json
        print(json.dumps(result, indent=2), file=sys.stderr)
        
        # Check if MCP server IDs are in the response (nested in conversation_config.agent.prompt)
        if isinstance(result, dict):
            prompt_config = result.get("conversation_config", {}).get("agent", {}).get("prompt", {})
            mcp_ids = prompt_config.get("mcp_server_ids", [])
            if mcp_ids:
                print(f"\n✓ MCP server IDs successfully set in agent config: {mcp_ids}", file=sys.stderr)
            else:
                print(f"\n⚠ Warning: 'mcp_server_ids' not found in prompt config", file=sys.stderr)
                print(f"Prompt config keys: {list(prompt_config.keys())}", file=sys.stderr)
        
        print("\n✓ Agent update API call completed", file=sys.stderr)
        print(f"Agent ID: {agent_id}", file=sys.stderr)
        print(f"MCP Server ID: {mcp_server_id}", file=sys.stderr)
        
        return 0
    except Exception as e:
        print(f"Error: Failed to update agent: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())

