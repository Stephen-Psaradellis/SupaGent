# Get test

**URL:** https://elevenlabs.io/docs/api-reference/tests/get



---

Gets an agent response test by ID.

### Path Parameters

test\_idstringRequired

The id of a chat response test. This is returned on test creation.

### Headers

xi-api-keystringRequired

### Response

Successful Response

chat\_historylist of objects

Show 15 properties

success\_conditionstring

A prompt that evaluates whether the agent's response is successful. Should return True or False.

success\_exampleslist of objects

Non-empty list of example responses that should be considered successful

Show 2 properties

failure\_exampleslist of objects

Non-empty list of example responses that should be considered failures

Show 2 properties

idstring

namestring

tool\_call\_parametersobject or null

How to evaluate the agent’s tool call (if any). If empty, the tool call is not evaluated.

Show 3 properties

dynamic\_variablesmap from strings to nullable strings or doubles or integers or booleans or null

Dynamic variables to replace in the agent config during testing

Show 4 variants

typeenum or null

Allowed values:llmtool

from\_conversation\_metadataobject or null

Metadata of a conversation this test was created from (if applicable).

Show 4 properties

### Errors

422

Unprocessable Entity Error
