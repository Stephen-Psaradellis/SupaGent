# Project settings | GitLab Docs

Source: https://docs.gitlab.com/user/project/settings/

Project settings | GitLab Docs
Project settings
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Configure project features and permissions
To configure features and permissions for a project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand
Visibility, project features, permissions
.
To allow users to request access to the project, select the
Users can request access
checkbox.
To turn features on or off in the project, use the feature toggles.
Select
Save changes
.
Feature dependencies
When you turn off a feature, the following additional features are also unavailable:
If you turn off the
Issues
feature, project users cannot use:
Issue Boards
Service Desk
Project users can still access
Milestones
from merge requests.
If you turn off
Issues
and
Merge Requests
, project users cannot use:
Labels
Milestones
If you turn off
Repository
, project users cannot access:
Merge requests
CI/CD
Git Large File Storage
Packages
The metrics dashboard requires read access to project environments and deployments.
Users with access to the metrics dashboard can also access environments and deployments.
Toggle project features
Available project features are visible and accessible to project members.
You can turn off specific project features, so that they are not visible
and accessible to project members, regardless of their role.
To toggle the availability of individual features in a project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand
Visibility, project features, permissions
.
To change the availability of a feature, turn the toggle on or off.
Select
Save changes
.
Turn off project analytics
Turning off project analytics only removes the
Analyze
navigation item, but data is still being computed and available through the respective API endpoints.
By default, project analytics are displayed under the
Analyze
item in the left sidebar.
To turn this feature off and remove the
Analyze
item from the left sidebar:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand
Visibility, project features, permissions
.
Turn off the
Analytics
toggle.
Select
Save changes
.
Turn off CVE identifier request in issues
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com
History
Introduced
in GitLab 13.4, only for public projects on GitLab.com.
In some environments, users can submit a
CVE identifier request
in an issue.
To turn off the CVE identifier request option in issues in your project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand
Visibility, project features, permissions
.
Under
Issues
, turn off the
CVE ID requests in the issue sidebar
toggle.
Select
Save changes
.
Turn off project email notifications
Prerequisites:
You must have the Owner role for the project.
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand the
Visibility, project features, permissions
section.
Clear the
Enable email notifications
checkbox.
Turn off diff previews in project email notifications
History
Introduced
in GitLab 15.6
with a flag
named
diff_preview_in_email
. Disabled by default.
Generally available
in GitLab 17.1. Feature flag
diff_preview_in_email
removed.
When you review code in a merge request and comment on a line of code, GitLab
includes a few lines of the diff in the email notification to participants.
Some organizational policies treat email as a less secure system, or might not
control their own infrastructure for email. This can present risks to IP or
access control of source code.
Prerequisites:
You must have the Owner role for the project.
To turn off diff previews for a project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand the
Visibility, project features, permissions
section.
Clear
Include diff previews
.
Select
Save changes
.
Configure merge request settings for a project
Configure your project’s merge request settings:
Set up the
merge request method
(merge commit, fast-forward merge).
Add merge request
description templates
.
Turn on:
Merge request approvals
.
Status checks
.
Merge only if pipeline succeeds
.
Merge only when all threads are resolved
.
Required associated issue from Jira
.
Delete source branch when merge request is accepted
option by default
.
Configure:
Suggested changes commit messages
.
Merge and squash commit message templates
.
Default target project
for merge requests coming from forks.
Delete the source branch on merge by default
In merge requests, you can change the default behavior so that the
Delete the source branch
checkbox is always selected.
To set this default:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Merge requests
.
Select
Enable “Delete source branch” option by default
.
Select
Save changes
.
Add additional webhook triggers for project access token expiration
History
Introduced
60- and 30-day triggers to project and group access token webhooks in GitLab 17.9
with a flag
named
extended_expiry_webhook_execution_setting
. Disabled by default.
Generally available
in GitLab 17.10. Feature flag
extended_expiry_webhook_execution_setting
removed.
The availability of this feature is controlled by a feature flag. For more information, see the history.
GitLab sends multiple
expiry emails
and triggers a related
webhook
before a project token expires. By default, GitLab only triggers these webhooks 7 days before the token expires. When this feature is enabled, GitLab also triggers these webhooks 60 days and 30 days before the token expires.
To enable additional triggers for these webhooks:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand the
Visibility, project features, permissions
section.
Select the
Extended Group Access Tokens Expiry Webhook execution
checkbox.
Select
Save changes
.
