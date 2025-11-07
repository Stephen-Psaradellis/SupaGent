# List conversations

**URL:** https://elevenlabs.io/docs/api-reference/conversations/list

**Section:** conversations
**Endpoint:** list


---

Get all conversations of agents that user owns. With option to restrict to a specific agent.

### Headers

xi-api-keystringRequired

### Query Parameters

cursorstring or nullOptional

Used for fetching next page. Cursor is returned in the response.

agent\_idstring or nullOptional

The id of the agent you're taking the action on.

call\_successfulenum or nullOptional

The result of the success evaluation

Allowed values:successfailureunknown

call\_start\_before\_unixinteger or nullOptional

Unix timestamp (in seconds) to filter conversations up to this start date.

call\_start\_after\_unixinteger or nullOptional

Unix timestamp (in seconds) to filter conversations after to this start date.

user\_idstring or nullOptional

Filter conversations by the user ID who initiated them.

page\_sizeintegerOptional`1-100`Defaults to `30`

How many conversations to return at maximum. Can not exceed 100, defaults to 30.

summary\_modeenumOptionalDefaults to `exclude`

Whether to include transcript summaries in the response.

Allowed values:excludeinclude

searchstring or nullOptional

Full-text or fuzzy search over transcript messages

### Response

Successful Response

conversationslist of objects

Show 12 properties

has\_moreboolean

next\_cursorstring or null

### Errors

422

Unprocessable Entity Error
