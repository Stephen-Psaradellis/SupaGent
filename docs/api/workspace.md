# Search user group

**URL:** https://elevenlabs.io/docs/api-reference/workspace



---

Searches for user groups in the workspace. Multiple or no groups may be returned.

### Headers

xi-api-keystringRequired

### Query Parameters

namestringRequired

Name of the target group.

### Response

Successful Response

namestring

The name of the workspace group.

idstring

The ID of the workspace group.

members\_emailslist of strings

The emails of the members of the workspace group.

### Errors

422

Unprocessable Entity Error
