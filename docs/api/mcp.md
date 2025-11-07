# Create MCP server

**URL:** https://elevenlabs.io/docs/api-reference/mcp



---

Create a new MCP server configuration in the workspace.

### Headers

xi-api-keystringRequired

### Request

This endpoint expects an object.

configobjectRequired

Configuration details for the MCP Server.

Show 14 properties

### Response

Successful Response

idstring

configobject

Show 14 properties

metadataobject

The metadata of the MCP Server

Show 2 properties

access\_infoobject or null

The access information of the MCP Server

Show 4 properties

dependent\_agentslist of objects or null

List of agents that depend on this MCP Server.

Show 2 variants

### Errors

422

Unprocessable Entity Error
