# Calculate expected LLM usage

**URL:** https://elevenlabs.io/docs/api-reference/llm-usage



---

Returns a list of LLM models and the expected cost for using them based on the provided values.

### Headers

xi-api-keystringRequired

### Request

This endpoint expects an object.

prompt\_lengthintegerRequired

Length of the prompt in characters.

number\_of\_pagesintegerRequired

Pages of content in PDF documents or URLs in the agent's knowledge base.

rag\_enabledbooleanRequired

Whether RAG is enabled.

### Response

Successful Response

llm\_priceslist of objects

Show 2 properties

### Errors

422

Unprocessable Entity Error
