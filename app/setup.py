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
    
    Args:
        app: FastAPI application instance.
        config: Application configuration.
    """
    def create_or_get_mcp_server() -> Optional[str]:
        """Create or retrieve MCP server configuration in ElevenLabs."""
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            
            if not config.elevenlabs_api_key:
                return None
            
            client = ElevenLabs(api_key=config.elevenlabs_api_key)
            base_url = config.base_url
            mcp_server_name = config.mcp_server_name
            
            # Check if MCP server already exists
            try:
                if hasattr(client.conversational_ai, 'mcp_servers'):
                    mcp_servers = client.conversational_ai.mcp_servers.list()
                    for server in getattr(mcp_servers, 'servers', []):
                        server_config = getattr(server, 'config', {})
                        server_url = server_config.get('url', '') if isinstance(server_config, dict) else getattr(server_config, 'url', '')
                        if base_url in server_url or getattr(server, 'name', '') == mcp_server_name:
                            server_id = getattr(server, 'id', None)
                            if server_id:
                                app.state._mcp_server_id = server_id
                                return server_id
            except Exception:
                pass
            
            # Create new MCP server
            try:
                mcp_config = {
                    "url": f"{base_url}/mcp",
                    "name": mcp_server_name,
                    "description": "SupaGent Knowledge Base MCP Server - Provides access to customer support documentation via vector store search",
                    "transport": "SSE",
                    "approval_policy": "auto_approve_all",
                }
                
                if hasattr(client, 'conversational_ai') and hasattr(client.conversational_ai, 'mcp_servers'):
                    result = client.conversational_ai.mcp_servers.create(config=mcp_config)
                    server_id = getattr(result, 'id', None)
                    if server_id:
                        app.state._mcp_server_id = server_id
                        # Persist to .env
                        env_path = Path(".env")
                        if env_path.exists():
                            lines = env_path.read_text(encoding="utf-8").splitlines()
                            lines = [l for l in lines if not l.startswith("ELEVENLABS_MCP_SERVER_ID=")]
                            lines.append(f"ELEVENLABS_MCP_SERVER_ID={server_id}")
                            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                        return server_id
            except Exception as e:
                app.state._mcp_server_error = str(e)
                return None
        except Exception as e:
            app.state._mcp_server_error = str(e)
            return None
    
    # Store function for use in routes
    app.state._create_or_get_mcp_server = create_or_get_mcp_server
    
    # Create/register MCP server with ElevenLabs and grant agent access
    if config.elevenlabs_api_key:
        mcp_server_id = create_or_get_mcp_server()
        if mcp_server_id:
            os.environ["ELEVENLABS_MCP_SERVER_ID"] = mcp_server_id
            config.elevenlabs_mcp_server_id = mcp_server_id
            
            # Grant agent access to MCP server and knowledge base
            if config.elevenlabs_agent_id:
                try:
                    from agents.agent_testing import ElevenLabsAgentTester
                    from agents.system_prompt import get_system_prompt
                    tester = ElevenLabsAgentTester(agent_id=config.elevenlabs_agent_id)
                    
                    system_prompt = get_system_prompt()
                    tester.update_agent(
                        mcp_server_ids=[mcp_server_id],
                        prompt=system_prompt
                    )
                except Exception as e:
                    app.state._agent_update_error = str(e)


def setup_elevenlabs_agent(app: FastAPI, config: AppConfig) -> None:
    """Auto-create ElevenLabs Agent if needed.
    
    Args:
        app: FastAPI application instance.
        config: Application configuration.
    """
    if config.elevenlabs_api_key and not config.elevenlabs_agent_id:
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            
            client = ElevenLabs(api_key=config.elevenlabs_api_key)
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
        except Exception as e:
            app.state._agent_error = str(e)

