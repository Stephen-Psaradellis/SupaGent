# List knowledge base documents

**URL:** https://elevenlabs.io/docs/api-reference/knowledge-base



---

Get a list of available knowledge base documents

### Headers

xi-api-keystringRequired

### Query Parameters

page\_sizeintegerOptional`1-100`Defaults to `30`

How many documents to return at maximum. Can not exceed 100, defaults to 30.

searchstring or nullOptional

If specified, the endpoint returns only such knowledge base documents whose names start with this string.

show\_only\_owned\_documentsbooleanOptionalDefaults to `false`

If set to true, the endpoint will return only documents owned by you (and not shared from somebody else).

typeslist of enums or nullOptional

If present, the endpoint will return only documents of the given types.

Allowed values:fileurltext

sort\_directionenumOptional

The direction to sort the results

Allowed values:ascdesc

sort\_byenumOptional

The field to sort the results by

Allowed values:namecreated\_atupdated\_atsize

use\_typesensebooleanOptionalDefaults to `false`Deprecated

If set to true, the endpoint will use typesense DB to search for the documents).

cursorstring or nullOptional

Used for fetching next page. Cursor is returned in the response.

### Response

Successful Response

documentslist of objects

Show 3 variants

has\_moreboolean

next\_cursorstring or null

### Errors

422

Unprocessable Entity Error
