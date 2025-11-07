# Delete knowledge base document

**URL:** https://elevenlabs.io/docs/api-reference/knowledge-base/delete



---

Delete a document from the knowledge base

### Path Parameters

documentation\_idstringRequired

The id of a document from the knowledge base. This is returned on document addition.

### Headers

xi-api-keystringRequired

### Query Parameters

forcebooleanOptionalDefaults to `false`

If set to true, the document will be deleted regardless of whether it is used by any agents and it will be deleted from the dependent agents.

### Response

Successful Response

### Errors

422

Unprocessable Entity Error
