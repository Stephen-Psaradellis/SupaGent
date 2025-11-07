# Outbound call via twilio

**URL:** https://elevenlabs.io/docs/api-reference/twilio/outbound-call



---

Handle an outbound call via Twilio

### Headers

xi-api-keystringRequired

### Request

This endpoint expects an object.

agent\_idstringRequired

agent\_phone\_number\_idstringRequired

to\_numberstringRequired

conversation\_initiation\_client\_dataobject or nullOptional

Show 5 properties

### Response

Successful Response

successboolean

messagestring

conversation\_idstring or null

callSidstring or null

### Errors

422

Unprocessable Entity Error
