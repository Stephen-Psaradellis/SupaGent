from __future__ import annotations

import os
import sys
from pathlib import Path

"""
Creates an ElevenLabs Agent and prints the agent ID.
Requires ELEVENLABS_API_KEY in the environment. Optionally writes ELEVENLABS_AGENT_ID to .env.
Optionally configures the agent with MCP/vector store tool.

Usage:
  python -m tools.create_eleven_agent --name "SupaGent Support Agent" --write-env
  python -m tools.create_eleven_agent --name "SupaGent Support Agent" --write-env --configure-tools
"""

def main():
    import argparse
    from dotenv import load_dotenv
    load_dotenv()
    
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="SupaGent Support Agent")
    ap.add_argument("--write-env", action="store_true")
    ap.add_argument("--configure-tools", action="store_true", help="Configure agent with MCP/vector store tool")
    ap.add_argument("--base-url", default=None, help="Base URL for tool endpoint (default: http://localhost:8000)")
    args = ap.parse_args()

    try:
        from elevenlabs.client import ElevenLabs  # type: ignore
    except Exception as e:
        raise SystemExit("elevenlabs SDK not installed. Run: pip install elevenlabs")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise SystemExit("ELEVENLABS_API_KEY not set.")

    client = ElevenLabs(api_key=api_key)

    # Get tool definition if configuring tools
    base_url = args.base_url or os.getenv("SUPAGENT_BASE_URL", "http://localhost:8000")
    tool_definition = None
    if args.configure_tools:
        tool_definition = {
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "Search the customer support knowledge base to find relevant documentation, FAQs, and troubleshooting guides. Use this tool when you need to answer questions about products, services, policies, or procedures.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant information in the knowledge base"
                        },
                        "k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 4, max: 10)",
                            "default": 4,
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["query"]
                },
                "url": f"{base_url}/tools/search_knowledge_base"
            }
        }

    # Create a simple agent with default settings; adjust as needed
    # The actual SDK may differ; handle attribute errors gracefully
    try:
        create_kwargs = {"name": args.name}
        if tool_definition:
            # Try to create with tools if SDK supports it
            try:
                agent = client.agents.create(**create_kwargs, tools=[tool_definition])
                print("Created agent with tool configuration", file=sys.stderr)
            except (TypeError, AttributeError):
                # Fallback: create without tools
                agent = client.agents.create(**create_kwargs)
                print("Created agent (tool configuration will be attempted separately)", file=sys.stderr)
        else:
            agent = client.agents.create(**create_kwargs)
    except AttributeError:
        raise SystemExit("Installed elevenlabs SDK version does not support agents.create. Update SDK.")

    agent_id = getattr(agent, "id", None) or getattr(agent, "agent_id", None)
    if not agent_id:
        raise SystemExit("Could not obtain agent id from response.")

    print(agent_id)

    if args.write_env:
        env_path = Path(".env")
        lines = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
            lines = [l for l in lines if not l.startswith("ELEVENLABS_AGENT_ID=")]
        lines.append(f"ELEVENLABS_AGENT_ID={agent_id}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Wrote ELEVENLABS_AGENT_ID to {env_path}", file=sys.stderr)
    
    # Configure tools if requested and not already done during creation
    if args.configure_tools and tool_definition:
        try:
            # Try various SDK methods to add tools
            if hasattr(client.agents, 'update'):
                client.agents.update(agent_id=agent_id, tools=[tool_definition])
                print("Successfully configured tools via agents.update()", file=sys.stderr)
            elif hasattr(client.agents, 'add_tool'):
                client.agents.add_tool(agent_id=agent_id, tool=tool_definition)
                print("Successfully configured tools via agents.add_tool()", file=sys.stderr)
            else:
                print("Warning: SDK does not support tool configuration via API. Please configure manually in ElevenLabs dashboard.", file=sys.stderr)
                print(f"Tool definition available at: {base_url}/tools/definitions", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not configure tools automatically: {e}", file=sys.stderr)
            print(f"Please configure manually in ElevenLabs dashboard or use: {base_url}/tools/definitions", file=sys.stderr)


if __name__ == "__main__":
    main()
