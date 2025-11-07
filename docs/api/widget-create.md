# Create widget avatar

**URL:** https://elevenlabs.io/docs/api-reference/widget/create



---

Sets the avatar for an agent displayed in the widget

### Path Parameters

agent\_idstringRequired

The id of an agent. This is returned on agent creation.

### Headers

xi-api-keystringRequired

### Request

This endpoint expects a multipart form containing a file.

avatar\_filefileRequired

An image file to be used as the agent's avatar.

### Response

Successful Response

agent\_idstring

avatar\_urlstring or null

### Errors

422

Unprocessable Entity Error
