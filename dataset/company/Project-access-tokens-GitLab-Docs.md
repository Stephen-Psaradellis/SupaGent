# Project access tokens | GitLab Docs

Source: https://docs.gitlab.com/user/project/settings/project_access_tokens/

Project access tokens | GitLab Docs
Project access tokens
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
for trial subscriptions in GitLab 16.1.
Project access tokens are similar to passwords, except you can limit access to resources,
select a limited role, and provide an expiry date.
Access to a specific project is controlled by a combination of
roles and permissions
and token scopes.
Use a project access token to authenticate:
With the GitLab API.
With Git, when using HTTP Basic Authentication, use:
Any non-blank value as a username.
The project access token as the password.
On GitLab SaaS, you can use project access tokens with a Premium or Ultimate subscription. With a
trial license
you can also create one project access token.
On GitLab Self-Managed instances, you can use project access tokens with any subscription. If
you have the Free tier, you can
restrict the creation of project access tokens
to limit potential abuse.
Project access tokens are similar to group access tokens and personal access tokens, but are
scoped only to the associated project. You cannot use project access tokens to access resources
that belong to other projects.
On GitLab Self-Managed instances, project access tokens are subject to the same maximum lifetime limits as personal access tokens if the limit is set.
You cannot use project access tokens to create other group, project, or personal access tokens.
Project access tokens inherit the
default prefix setting
configured for personal access tokens.
Create a project access token
History
Introduced
in GitLab 15.1, Owners can select Owner role for project access tokens.
Introduced
in GitLab 15.3, default expiration of 30 days and default role of Guest is populated in the UI.
Ability to create non-expiring project access tokens
removed
in GitLab 16.0.
Maximum allowable lifetime limit
extended to 400 days
in GitLab 17.6
with a flag
named
buffered_token_expiration_limit
. Disabled by default.
Project access token description
introduced
in GitLab 17.7.
The availability of the extended maximum allowable lifetime limit is controlled by a feature flag.
For more information, see the history.
The ability to create project access tokens without an expiry date was
deprecated
in GitLab 15.4 and
removed
in GitLab 16.0. For more information on expiry dates added to existing tokens, see the documentation on
access token expiration
.
To create a project access token:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Access tokens
.
Select
Add new token
.
In
Token name
, enter a name. The token name is visible to any user with permissions to view the project.
Optional. In
Token description
, enter a description for the token.
In
Expiration date
, enter an expiry date for the token.
The token expires on that date at midnight UTC. A token with the expiration date of 2024-01-01 expires at 00:00:00 UTC on 2024-01-01.
If you do not enter an expiry date, the expiry date is automatically set to 30 days later than the current date.
By default, this date can be a maximum of 365 days later than the current date. In GitLab 17.6 or later, you can extend this limit to 400 days.
An instance-wide maximum lifetime setting can limit the maximum allowable lifetime in GitLab Self-Managed instances.
Select a role for the token.
Select the desired scopes.
Select
Create project access token
.
A project access token is displayed. Save the project access token somewhere safe. After you leave or refresh the page, you can’t view it again.
Project access tokens are treated as internal users.
If an internal user creates a project access token, that token is able to access
all projects that have visibility level set to Internal.
Revoke or rotate a project access token
History
Ability to view expired and revoked tokens
introduced
in GitLab 17.3
with a flag
named
retain_resource_access_token_user_after_revoke
. Disabled by default.
Ability to view expired and revoked tokens until they are automatically deleted and
generally available
in GitLab 17.9. Feature flag
retain_resource_access_token_user_after_revoke
removed.
In GitLab 17.9 and later, you can view both active and inactive project
access tokens on the access tokens page.
The inactive project access tokens table displays revoked and expired tokens until they are
automatically deleted
.
To revoke or rotate a project access token:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Access tokens
.
For the relevant token, select
Revoke
(
remove
) or
Rotate
(
retry
).
On the confirmation dialog, select
Revoke
or
Rotate
.
Scopes for a project access token
History
k8s_proxy
introduced
in GitLab 16.4
with a flag
named
k8s_proxy_pat
. Enabled by default.
Feature flag
k8s_proxy_pat
removed
in GitLab 16.5.
self_rotate
introduced
in GitLab 17.9. Enabled by default.
The scope determines the actions you can perform when you authenticate with a project access token.
See the warning in
create a project access token
regarding internal projects.
Scope
Description
api
Grants complete read and write access to the scoped project API, including the
container registry
, the
dependency proxy
, and the
package registry
.
read_api
Grants read access to the scoped project API, including the
package registry
.
read_registry
Grants read access (pull) to the
container registry
images if a project is private and authorization is required.
write_registry
Grants write access (push) to the
container registry
. You need both read and write access to push images.
read_repository
Grants read access (pull) to the repository.
write_repository
Grants read and write access (pull and push) to the repository.
create_runner
Grants permission to create runners in the project.
manage_runner
Grants permission to manage runners in the project.
ai_features
Grants permission to perform API actions for GitLab Duo. This scope is designed to work with the GitLab Duo Plugin for JetBrains. For all other extensions, see scope requirements.
k8s_proxy
Grants permission to perform Kubernetes API calls using the agent for Kubernetes in the project.
self_rotate
Grants permission to rotate this token using the
personal access token API
. Does not allow rotation of other tokens.
Restrict the creation of project access tokens
To limit potential abuse, you can restrict users from creating tokens for a group hierarchy. This setting is only configurable for a top-level group and applies to every downstream project and subgroup. Any existing project access tokens remain valid until their expiration date or until manually revoked.
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
This group must be at the top level.
Select
Settings
>
General
.
Expand
Permissions and group features
.
In
Permissions
, clear the
Users can create project access tokens and group access tokens in this group
checkbox.
Access token expiration
Whether your existing project access tokens have expiry dates automatically applied
depends on what GitLab offering you have, and when you upgraded to GitLab 16.0 or later:
On GitLab.com, during the 16.0 milestone, existing project access tokens without
an expiry date were automatically given an expiry date of 365 days later than the current date.
On GitLab Self-Managed, if you upgraded from GitLab 15.11 or earlier to GitLab 16.0 or later:
On or before July 23, 2024, existing project access tokens without an expiry
date were automatically given an expiry date of 365 days later than the current date.
This change is a breaking change.
On or after July 24, 2024, existing project access tokens without an expiry
date did not have an expiry date set.
On GitLab Self-Managed, if you do a new install of one of the following GitLab
versions, your existing project access tokens do not have expiry dates
automatically applied:
16.0.9
16.1.7
16.2.10
16.3.8
16.4.6
16.5.9
16.6.9
16.7.9
16.8.9
16.9.10
16.10.9
16.11.7
17.0.5
17.1.3
17.2.1
Project access token expiry emails
History
60 and 30 day expiry notifications
introduced
in GitLab 17.6
with a flag
named
expiring_pats_30d_60d_notifications
. Disabled by default.
60 and 30 day notifications
generally available
in GitLab 17.7. Feature flag
expiring_pats_30d_60d_notifications
removed.
Notifications to inherited group members
introduced
in GitLab 17.7
with a flag
named
pat_expiry_inherited_members_notification
. Disabled by default.
Feature flag
pat_expiry_inherited_members_notification
enabled by default in GitLab 17.10
.
Feature flag
pat_expiry_inherited_members_notification
removed in GitLab
17.11
GitLab runs a check every day at 1:00 AM UTC to identify project access tokens that are expiring in the near future. Members of the project with at least the Maintainer role are notified by email when these tokens expire in a certain number of days. The number of days differs depending on the version of GitLab:
In GitLab 17.6 and later, project maintainers and owners are notified by email when the check identifies their project access tokens as expiring in the next 60 days. An additional email is sent when the check identifies their project access tokens as expiring in the next 30 days.
Project maintainers and owners are notified by email when the check identifies their project access tokens as expiring in the next seven days.
In GitLab 17.7 and later, project members who have inherited the Owner or Maintainer role due to the project belonging to a group can also receive notification emails. You can enable this by changing:
The
group setting
in any of the parent groups of the project.
On GitLab Self-Managed, the
instance setting
.
Your expired access tokens are listed in the
inactive project access tokens table
until they are
automatically deleted
.
Bot users for projects
History
Changed
in GitLab 17.2
with a flag
named
retain_resource_access_token_user_after_revoke
. Disabled by default. When enabled new bot users are made members with no expiry date and, when the token is later revoked or expires, the bot user is retained for 30 days.
Inactive bot users retention is
generally available
in GitLab 17.9. Feature flag
retain_resource_access_token_user_after_revoke
removed.
Bot users for projects are
GitLab-created non-billable users
.
Each time you create a project access token, a bot user is created and added to the project.
This user is not a billable user, so it does not count toward the license limit.
The bot users for projects have
permissions
that correspond with the
selected role and
scope
of the project access token.
The name is set to the name of the token.
The username is set to
project_{project_id}_bot_{random_string}
. For example,
project_123_bot_4ffca233d8298ea1
.
The email is set to
project_{project_id}_bot_{random_string}@noreply.{Gitlab.config.gitlab.host}
. For example,
project_123_bot_4ffca233d8298ea1@noreply.example.com
.
API calls made with a project access token are associated with the corresponding bot user.
Bot users for projects:
Are included in a project’s member list but cannot be modified.
Cannot be added to any other project.
Can have a maximum role of Owner for a project. For more information, see
Create a project access token
.
When the project access token is
revoked
:
The bot user is retained as per
inactive token retention setting
.
After 30 days the bot user is deleted. All records are moved to a system-wide user with the username
Ghost User
.
For more information, see
bot users for groups
.
Inactive token retention
By default, GitLab deletes group and project access tokens and their
token family
30 days after the last active token from the token family becomes inactive. This removes all tokens in the token family and the associated bot user and migrates the bot user contributions to a system-wide “Ghost User”.
To modify the retention period for inactive tokens:
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
Account and limit
.
In the
Inactive project and group access token retention period
text box, modify the retention period.
If a number is defined, all group and project access tokens are deleted after they are inactive for the specified number of days.
If the field is blank, inactive tokens are never deleted.
Select
Save changes
.
You can also use the
application settings API
to modify the
inactive_resource_access_tokens_delete_after_days
attribute.
Token availability
More than one project access token is only available in paid subscriptions. In Premium and Ultimate trial subscriptions, only one project access token is included. For more information, see the
“What is included” section of the GitLab Trial FAQ
.
Related topics
Personal access tokens
Group access tokens
Project access tokens API
