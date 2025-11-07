# Create agent

**URL:** https://elevenlabs.io/docs/api-reference/agents/create

**Section:** agents
**Endpoint:** create


---

Create an agent from a config object

### Headers

xi-api-keystringRequired

### Request

This endpoint expects an object.

conversation\_configobjectRequired

Conversation configuration for an agent

Show 7 properties

platform\_settingsobject or nullOptional

Platform settings for the agent are all settings that aren't related to the conversation orchestration and content.

Show 10 properties

workflowobjectOptional

Workflow for the agent. This is used to define the flow of the conversation and how the agent interacts with tools.

Show 2 properties

namestring or nullOptional

A name to make the agent easier to find

tagslist of strings or nullOptional

Tags to help classify and filter the agent

### Response

Successful Response

agent\_idstring

ID of the created agent

### Errors

422

Unprocessable Entity Error
