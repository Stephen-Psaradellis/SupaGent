# Remove member from user group

**URL:** https://elevenlabs.io/docs/api-reference/workspace/groups/members/remove



---

Removes a member from the specified group. This endpoint may only be called by workspace administrators.

### Path Parameters

group\_idstringRequired

The ID of the target group.

### Headers

xi-api-keystringRequired

### Request

This endpoint expects an object.

emailstringRequired

The email of the target workspace member.

### Response

Successful Response

statusstring

The status of the workspace group member deletion request. If the request was successful, the status will be 'ok'. Otherwise an error message with status 500 will be returned.

### Errors

422

Unprocessable Entity Error
