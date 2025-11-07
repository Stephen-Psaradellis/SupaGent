# Get widget

**URL:** https://elevenlabs.io/docs/api-reference/widget



---

Retrieve the widget configuration for an agent

### Path Parameters

agent\_idstringRequired

The id of an agent. This is returned on agent creation.

### Headers

xi-api-keystringRequired

### Query Parameters

conversation\_signaturestring or nullOptional

An expiring token that enables a websocket conversation to start. These can be generated for an agent using the /v1/convai/conversation/get-signed-url endpoint

### Response

Successful Response

agent\_idstring

widget\_configobject

Show 42 properties

### Errors

422

Unprocessable Entity Error
