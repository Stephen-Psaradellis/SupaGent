# Outbound call via SIP trunk

**URL:** https://elevenlabs.io/docs/api-reference/sip-trunk/outbound-call



---

Handle an outbound call via SIP trunk

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

sip\_call\_idstring or null

### Errors

422

Unprocessable Entity Error
