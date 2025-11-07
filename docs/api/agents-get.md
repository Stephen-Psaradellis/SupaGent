# Get agent

**URL:** https://elevenlabs.io/docs/api-reference/agents/get

**Section:** agents
**Endpoint:** get


---

Retrieve config for an agent

### Path Parameters

agent\_idstringRequired

The id of an agent. This is returned on agent creation.

### Headers

xi-api-keystringRequired

### Response

Successful Response

agent\_idstring

The ID of the agent

namestring

The name of the agent

conversation\_configobject

The conversation configuration of the agent

Show 7 properties

metadataobject

The metadata of the agent

Show 2 properties

platform\_settingsobject or null

The platform settings of the agent

Show 11 properties

phone\_numberslist of objects or null

The phone numbers of the agent

Show 2 variants

workflowobject or null

The workflow of the agent

Show 2 properties

access\_infoobject or null

The access information of the agent for the user

Show 4 properties

tagslist of strings or null

Agent tags used to categorize the agent

### Errors

422

Unprocessable Entity Error
