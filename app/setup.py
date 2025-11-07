"""
Application setup and initialization logic.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from core.config import AppConfig
from core.di import ServiceContainer
from fastapi import FastAPI


def setup_elevenlabs_mcp_server(app: FastAPI, config: AppConfig) -> None:
    """Setup and register MCP server with ElevenLabs.
    
    IMPORTANT: This function does NOT create MCP servers or update agents on startup.
    It only validates that the configured MCP server ID exists.
    
    To create/update MCP servers and agents, use:
    - python tools/setup_mcp_server_and_agent.py (for initial setup)
    - python tools/update_agent_mcp.py (to update agent with existing MCP server)
    
    Args:
        app: FastAPI application instance.
        config: Application configuration.
    """
    def verify_mcp_server() -> Optional[str]:
        """Verify that the configured MCP server ID exists in ElevenLabs.
        
        Returns:
            The MCP server ID if valid, None otherwise.
        """
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            
            if not config.elevenlabs_api_key:
                return None
            
            # If MCP server ID is configured, verify it exists
            if config.elevenlabs_mcp_server_id:
                client = ElevenLabs(api_key=config.elevenlabs_api_key)
                
                try:
                    if hasattr(client.conversational_ai, 'mcp_servers'):
                        mcp_servers = client.conversational_ai.mcp_servers.list()
                        
                        # Extract servers list
                        servers = []
                        if hasattr(mcp_servers, 'mcp_servers'):
                            servers = mcp_servers.mcp_servers
                        elif hasattr(mcp_servers, 'servers'):
                            servers = mcp_servers.servers
                        elif isinstance(mcp_servers, list):
                            servers = mcp_servers
                        
                        # Check if configured server ID exists
                        for server in servers:
                            server_id = getattr(server, 'id', None) or (server.get('id') if isinstance(server, dict) else None)
                            if server_id == config.elevenlabs_mcp_server_id:
                                app.state._mcp_server_id = server_id
                                return server_id
                        
                        # Server ID not found
                        app.state._mcp_server_error = f"MCP server {config.elevenlabs_mcp_server_id} not found in ElevenLabs. Please verify the ID or create a new server using tools/setup_mcp_server_and_agent.py"
                        return None
                except Exception as e:
                    app.state._mcp_server_error = f"Failed to verify MCP server: {e}"
                    return None
            
            # No MCP server ID configured - this is okay, just log it
            app.state._mcp_server_id = None
            return None
            
        except Exception as e:
            app.state._mcp_server_error = str(e)
            return None
    
    # Store function for use in routes (if needed for future features)
    app.state._verify_mcp_server = verify_mcp_server
    
    # Only verify the configured MCP server - do NOT create or update anything
    if config.elevenlabs_api_key:
        mcp_server_id = verify_mcp_server()
        if mcp_server_id:
            # Store in app state for reference
            app.state._mcp_server_id = mcp_server_id
        # Note: We do NOT update the agent here - that should be done manually
        # via tools/setup_mcp_server_and_agent.py or tools/update_agent_mcp.py


def setup_elevenlabs_agent(app: FastAPI, config: AppConfig) -> None:
    """Auto-create ElevenLabs Agent if needed.
    
    Args:
        app: FastAPI application instance.
        config: Application configuration.
    """
    # If agent ID is already set, skip auto-creation
    if config.elevenlabs_agent_id:
        return
    
    if config.elevenlabs_api_key:
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            
            client = ElevenLabs(api_key=config.elevenlabs_api_key)
            
            # Check if agents API is available
            if not hasattr(client, 'agents'):
                app.state._agent_error = "Installed elevenlabs SDK version does not support agents API. Update SDK or set ELEVENLABS_AGENT_ID manually."
                return
            
            agent_name = os.getenv("SUPAGENT_AGENT_NAME", "SupaGent Support Agent")
            agent = client.agents.create(name=agent_name)
            
            aid = getattr(agent, "id", None) or getattr(agent, "agent_id", None)
            if aid:
                os.environ["ELEVENLABS_AGENT_ID"] = aid
                config.elevenlabs_agent_id = aid
                # Persist to .env
                env_path = Path(".env")
                lines = []
                if env_path.exists():
                    lines = [
                        l for l in env_path.read_text(encoding="utf-8").splitlines()
                        if not l.startswith("ELEVENLABS_AGENT_ID=")
                    ]
                lines.append(f"ELEVENLABS_AGENT_ID={aid}")
                env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except AttributeError as e:
            app.state._agent_error = f"SDK version does not support agents API: {e}. Update SDK or set ELEVENLABS_AGENT_ID manually."
        except Exception as e:
            app.state._agent_error = str(e)

