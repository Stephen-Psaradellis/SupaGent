# List workspace batch calling jobs

**URL:** https://elevenlabs.io/docs/api-reference/batch-calling/list



---

Get all batch calls for the current workspace.

### Headers

xi-api-keystringRequired

### Query Parameters

limitintegerOptionalDefaults to `100`

last\_docstring or nullOptional

### Response

Successful Response

batch\_callslist of objects

Show 13 properties

next\_docstring or null

The next document, used to paginate through the batch calls

has\_moreboolean or nullDefaults to `false`

Whether there are more batch calls to paginate through

### Errors

422

Unprocessable Entity Error
