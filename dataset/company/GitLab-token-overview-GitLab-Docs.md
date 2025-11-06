# GitLab token overview | GitLab Docs

Source: https://docs.gitlab.com/security/tokens/#security-considerations

GitLab token overview | GitLab Docs
GitLab token overview
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
This document lists tokens used in GitLab, their purpose and, where
applicable, security guidance.
Security considerations
To keep your tokens secure:
Treat tokens like passwords and keep them secure.
When creating a scoped token, use the most limited scope possible to reduce the impact of an accidentally leaked token.
If separate processes require different scopes (for example,
read
and
write
), consider using separate tokens, one for each scope. If one token leaks, it gives reduced access than a single token with a wide scope like full API access.
When creating a token:
Choose a name that describes the token, e.g.
GITLAB_API_TOKEN-application1
or
GITLAB_READ_API_TOKEN-application2
. Avoid generic names like
GITLAB_API_TOKEN
,
API_TOKEN
or
default
.
Consider setting a token that expires when your task is complete. For example, if you need to perform a one-time import, set the token to expire after a few hours.
Add a description that provides further context including any relevant URLs.
If you set up a demo environment to showcase a project you have been working on, and you record a video or write a blog post describing that project, make sure you don’t accidentally leak a secret.
After the demo is finished, revoke all the secrets created during the demo.
Adding tokens to URLs can be a security risk. Instead, pass the token with a header like
Private-Token
.
When cloning or adding a remote with a token in the URL, Git writes the URL to its
.git/config
file in plaintext.
URLs are often logged by proxies and application servers, which could leak those credentials to system administrators.
You can store tokens using
Git credential storage
.
Review all active access tokens of all types on a regular basis and revoke any you don’t need.
Do not:
Store tokens in plaintext in your projects. If the token is an external secret for GitLab CI/CD,
review how to
use external secrets in CI/CD
recommendations.
Include tokens when pasting code, console commands, or log outputs into an issue, MR description, comment, or any other free text inputs.
Log credentials in the console logs or artifacts. Consider
protecting
and
masking
your credentials.
Tokens in CI/CD
Avoid using personal access tokens as CI/CD variables wherever possible due to their wide scope.
If access to other resources is required from a CI/CD job, use one of the following, ordered by least to most access scope:
Job tokens (lowest access scope)
Project tokens
Group tokens
Additional recommendations for
CI/CD variable security
include:
Use
secrets storage
for any credentials.
CI/CD variable containing sensitive information should be
protected
,
masked
, and
hidden
.
Personal access tokens
You can create
personal access tokens
to authenticate with:
The GitLab API.
GitLab repositories.
The GitLab registry.
You can limit the scope and expiration date of your personal access tokens.
By default, they inherit permissions from the user who created them.
You can use the personal access tokens API to programmatically take action,
such as
rotating a personal access token
.
You
receive an email
when your personal access tokens are expiring soon.
When considering a CI/CD job that requires tokens for permissions, avoid using personal access tokens, especially if stored as a CI/CD variable.
CI/CD job tokens and project access tokens can often achieve the same result with much less risk.
OAuth 2.0 tokens
GitLab can serve as an
OAuth 2.0 provider
to
allow other services to access the GitLab API on a user’s behalf.
You can limit the scope and lifetime of your OAuth 2.0 tokens.
Impersonation tokens
An
impersonation token
is a special type of personal access token. It can be created only by
an administrator for a specific user. Impersonation tokens can help
you build applications or scripts that authenticate with the GitLab
API, repositories, and the GitLab registry as a specific user.
You can limit the scope and set an expiration date for an
impersonation token.
Project access tokens
Project access tokens
are scoped to a project. Like personal access tokens, you can use
them to authenticate with:
The GitLab API.
GitLab repositories.
The GitLab registry.
You can limit the scope and expiration date of project access tokens.
When you create a project access token, GitLab creates a
bot user for projects
.
Bot users for projects are service accounts and do not count as
licensed seats.
You can use the
project access tokens API
to programmatically take
action, such as
rotating a project access token
.
Members of a project with at least the Maintainer role
receive an email
when project access tokens are nearly expired.
Group access tokens
Group access tokens
are scoped to a group. Like personal access tokens, you can use
them to authenticate with:
The GitLab API.
GitLab repositories.
The GitLab registry.
You can limit the scope and expiration date of group access tokens.
When you create a group access token, GitLab creates a
bot user for groups
.
Bot users for groups are service accounts and do not count as licensed seats.
You can use the
group access tokens API
to programmatically take
action, such as
rotating a group access token
.
Members of a group with the Owner role
receive an email
when group access tokens are nearly expired.
Deploy tokens
Deploy tokens
allow you
to clone, push, and pull packages and container registry images of a
project without a user and a password. Deploy tokens cannot be used
with the GitLab API.
To manage deploy tokens, you must be a member of a project with at least
the Maintainer role.
Deploy keys
Deploy keys
allow read-only
or read-write access to your repositories by importing an SSH public key
into your GitLab instance. Deploy keys cannot be used with the
GitLab API or the registry.
You can use deploy keys to clone repositories to your continuous integration
server without setting up a fake user account.
To add or enable a deploy key for a project, you must have at least
the Maintainer role.
Runner authentication tokens
In GitLab 16.0 and later, to register a runner, you can use a runner authentication token
instead of a runner registration token. Runner registration tokens are
deprecated
.
After you create a runner and its configuration, you receive a runner authentication token
that you use to register the runner. The runner authentication token is stored locally in
the
config.toml
file,
which you use to configure the runner.
The runner uses the runner authentication token to authenticate with GitLab when it
picks up jobs from the job queue. After the runner authenticates with GitLab, the runner receives
a
job token
, which it uses to execute the job.
The runner authentication token stays on the runner machine. The execution environments
for the following executors have access to only the job token and not the runner authentication token:
Docker Machine
Kubernetes
VirtualBox
Parallels
SSH
Malicious access to a runner’s file system might expose the
config.toml
file and the runner authentication token. The attacker
could use the runner authentication token to
clone the runner
.
You can use the runners API to
rotate or revoke a runner authentication token
.
Runner registration tokens (legacy)
The option to pass runner registration tokens and support for certain configuration arguments is considered legacy
and is not recommended.
Use the
runner creation workflow
to generate an authentication token to register runners. This process provides full
traceability of runner ownership and enhances your runner fleet’s security.
GitLab has implemented a new
GitLab Runner token architecture
, which introduces
a new method for registering runners and eliminates the
runner registration token.
Runner registration tokens are used to
register
a
runner
with GitLab. Group or
project owners or instance administrators can obtain them through the
GitLab user interface. The registration token is limited to runner
registration and has no further scope.
You can use the runner registration token to add runners that execute
jobs in a project or group. The runner has access to the project’s
code, so be careful when assigning permissions to projects or groups.
CI/CD job tokens
The
CI/CD
job token is a short-lived token valid only for
the duration of a job. It gives a CI/CD job access to a limited number of API endpoints.
API authentication uses the job token by using the authorization of the user triggering the job.
The job token is secured by its short lifetime and limited scope. This token could be leaked if
multiple jobs run on the same machine (for example, with the
shell runner
). You can use the
project allow list
to further limit what the job token can access.
On Docker Machine runners, you should configure
MaxBuilds=1
to ensure runner machines run only one build
and are destroyed afterwards. Provisioning takes time,
so this configuration can affect performance.
GitLab cluster agent tokens
When you
register a GitLab agent for Kubernetes
, GitLab generates an access token to authenticate the cluster agent with GitLab.
To revoke this cluster agent token, you can either:
Revoke the token with the
agents API
.
Reset the token
.
For both methods, you must know the token, agent, and project IDs. To
find this information, use the
Rails console
:
# Find token ID
Clusters
::
AgentToken
.
find_by_token
(
'glagent-xxx'
)
.
id
# Find agent ID
Clusters
::
AgentToken
.
find_by_token
(
'glagent-xxx'
)
.
agent
.
id
=>
1234
# Find project ID
Clusters
::
AgentToken
.
find_by_token
(
'glagent-xxx'
)
.
agent
.
project_id
=>
12345
You can also revoke a token directly in the Rails console:
# Revoke token with RevokeService, including generating an audit event
Clusters
::
AgentTokens
::
RevokeService
.
new
(
token
:
Clusters
::
AgentToken
.
find_by_token
(
'glagent-xxx'
),
current_user
:
User
.
find_by_username
(
'admin-user'
))
.
execute
# Revoke token manually, which does not generate an audit event
Clusters
::
AgentToken
.
find_by_token
(
'glagent-xxx'
)
.
revoke!
Other tokens
Feed token
Each user has a long-lived feed token that does not expire.
Use this token to authenticate with:
RSS readers, to load a personalized RSS feed.
Calendar applications, to load a personalized calendar.
You cannot use this token to access any other data.
You can use the user-scoped feed token for all feeds. However, feed
and calendar URLs are generated with a different token valid for only
one feed.
Anyone who has your token can view your feed activity, including
confidential issues, as if they were you. If you think your token
has leaked,
reset the token
immediately.
Disable a feed token
Prerequisites:
You must be an administrator.
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Settings
>
General
.
Expand
Visibility and access controls
.
Under
Feed token
, select the
Disable feed token
checkbox, then select
Save changes
.
Incoming email token
Each user has an incoming email token that does not expire. The token
is included in email addresses associated with a personal project.
You use this token to
create a new issue by email
.
You cannot use this token to access any other data. Anyone who has
your token can create issues and merge requests as if they were
you. If you think your token has leaked, reset the token immediately.
Workspace token
History
Introduced
in GitLab 18.2.
Each
workspace
has an internal, automatically managed token that
does not expire. It allows HTTP and SSH communication with a workspace. It exists whenever a workspace
is requested to be in the
running
state, and is automatically injected and used by the workspace.
Starting a stopped workspace creates a new workspace token.
Restarting a running workspace deletes the existing token and creates a new token.
You cannot directly view or manage this internal token. You cannot use this token to access any other data.
To revoke a workspace token,
stop
or
terminate
the workspace
.
The token is deleted immediately.
Available scopes
This table shows default scopes per token. For some tokens, you can limit scopes further when you create the token.
Token name
API access
Registry access
Repository access
Personal access token
check-circle
Yes
check-circle
Yes
check-circle
Yes
OAuth 2.0 token
check-circle
Yes
dotted-circle
No
check-circle
Yes
Impersonation token
check-circle
Yes
check-circle
Yes
check-circle
Yes
Project access token
check-circle
Yes
1
check-circle
Yes
1
check-circle
Yes
1
Group access token
check-circle
Yes
2
check-circle
Yes
2
check-circle
Yes
2
Deploy token
dotted-circle
No
check-circle
Yes
check-circle
Yes
Deploy key
dotted-circle
No
dotted-circle
No
check-circle
Yes
Runner registration token
dotted-circle
No
dotted-circle
No
check-circle-dashed
Limited
3
Runner authentication token
dotted-circle
No
dotted-circle
No
check-circle-dashed
Limited
3
Job token
check-circle-dashed
Limited
4
dotted-circle
No
check-circle
Yes
Footnotes
:
Limited to the one project.
Limited to the one group.
Runner registration and authentication tokens don’t provide direct access
to repositories, but can be used to register and authenticate new runners
that can execute jobs which do have access to repositories.
Only
certain endpoints
.
Token prefixes
The following table shows the prefixes for each type of token.
With the exception of Personal Access tokens, these prefixes cannot be configured,
as they are designed to be standard identifications.
Token name
Prefix
Personal access token
glpat-
OAuth Application Secret
gloas-
Impersonation token
glpat-
Project access token
glpat-
Group access token
glpat-
Deploy token
gldt-
(
Added in GitLab 16.7
)
Runner authentication token
glrt-
or
glrtr-
if created via registration token
CI/CD Job token
glcbt-
• (
Introduced
in GitLab 16.8 behind a feature flag named
prefix_ci_build_tokens
. Disabled by default.)
• (
Generally available
in GitLab 16.9. Feature flag
prefix_ci_build_tokens
removed.)
Trigger token
glptt-
Feed token
glft-
Incoming mail token
glimt-
GitLab agent for Kubernetes token
glagent-
Workspace token
glwt-
(Added in GitLab 18.2)
GitLab session cookies
_gitlab_session=
SCIM Tokens
glsoat-
• (
Introduced
in GitLab 16.8 behind a feature flag named
prefix_scim_tokens
. Disabled by default.)
• (
Generally available
in GitLab 16.9. Feature flag
prefix_scim_tokens
removed.)
Feature Flags Client token
glffct-
