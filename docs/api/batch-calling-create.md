# Submit batch calling job

**URL:** https://elevenlabs.io/docs/api-reference/batch-calling/create



---

Submit a batch call request to schedule calls for multiple recipients.

### Headers

xi-api-keystringRequired

### Request

This endpoint expects an object.

call\_namestringRequired

agent\_idstringRequired

recipientslist of objectsRequired

Show 4 properties

scheduled\_time\_unixinteger or nullOptional

agent\_phone\_number\_idstring or nullOptional

agent\_whatsapp\_business\_account\_idstring or nullOptional

### Response

Successful Response

idstring

namestring

agent\_idstring

created\_at\_unixinteger

scheduled\_time\_unixinteger

total\_calls\_dispatchedinteger

total\_calls\_scheduledinteger

last\_updated\_at\_unixinteger

statusenum

Allowed values:pendingin\_progresscompletedfailedcancelled

agent\_namestring

phone\_number\_idstring or null

phone\_providerenum or null

Allowed values:twiliosip\_trunk

whatsapp\_business\_account\_idstring or null

### Errors

422

Unprocessable Entity Error
