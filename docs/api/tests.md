# List tests

**URL:** https://elevenlabs.io/docs/api-reference/tests



---

Lists all agent response tests with pagination support and optional search filtering.

### Headers

xi-api-keystringRequired

### Query Parameters

cursorstring or nullOptional

Used for fetching next page. Cursor is returned in the response.

page\_sizeintegerOptional`1-100`Defaults to `30`

How many Tests to return at maximum. Can not exceed 100, defaults to 30.

searchstring or nullOptional

Search query to filter tests by name.

### Response

Successful Response

testslist of objects

Show 6 properties

has\_moreboolean

next\_cursorstring or null

### Errors

422

Unprocessable Entity Error
