# Credentials inventory | GitLab Docs

Source: https://docs.gitlab.com/administration/credentials_inventory/#delete-ssh-keys

Credentials inventory | GitLab Docs
Credentials inventory
Tier
: Ultimate
Offering
: GitLab Self-Managed, GitLab Dedicated
History
Group access tokens
added
in GitLab 15.6.
For GitLab.com, see
Credentials inventory for GitLab.com
.
Use the credentials inventory to monitor and control access to your instance.
As an administrator, you can:
Revoke personal, project, or group access tokens.
Delete SSH keys.
Review credential details including:
Ownership.
Access scopes.
Usage patterns.
Expiration dates.
Revocation dates.
Revoke personal access tokens
To revoke a personal access token in your instance:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Credentials
.
Next to the personal access token, select
Revoke
.
If the token was previously expired or revoked, you’ll see the date this happened instead.
The access token is revoked and the user is notified by email.
Revoke project or group access tokens
To revoke a project access token in your instance:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Credentials
.
Select the
Project and group access tokens
tab.
Next to the project access token, select
Revoke
.
The access token is revoked and a background process begins to delete the associated project bot user.
Delete SSH keys
To delete an SSH key in your instance:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Credentials
.
Select the
SSH Keys
tab.
Next to the SSH key, select
Delete
.
The SSH key is deleted and the user is notified.
View GPG keys
You can see details for each GPG key including the owner, ID, and
verification status
.
To view information about GPG keys in your instance:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Credentials
.
Select the
GPG keys
tab.
