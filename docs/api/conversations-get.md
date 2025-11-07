# Get conversation details

**URL:** https://elevenlabs.io/docs/api-reference/conversations/get

**Section:** conversations
**Endpoint:** get


---

Get the details of a particular conversation

### Path Parameters

conversation\_idstringRequired

The id of the conversation you're taking the action on.

### Headers

xi-api-keystringRequired

### Response

Successful Response

agent\_idstring

conversation\_idstring

statusenum

Allowed values:initiatedin-progressprocessingdonefailed

transcriptlist of objects

Show 15 properties

metadataobject

Show 26 properties

has\_audioboolean

has\_user\_audioboolean

has\_response\_audioboolean

user\_idstring or null

branch\_idstring or null

analysisobject or null

Show 5 properties

conversation\_initiation\_client\_dataobject or null

Show 5 properties

### Errors

422

Unprocessable Entity Error
