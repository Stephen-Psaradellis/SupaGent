# Deploy tokens | GitLab Docs

Source: https://docs.gitlab.com/user/project/deploy_tokens/

Deploy tokens | GitLab Docs
Deploy tokens
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Deploy tokens provide secure access to GitLab resources without tying permissions to individual user accounts. Use them with Git operations, container registries, and package registries, giving your deployment
automation access to exactly what it needs.
With deploy tokens, you have:
More secure deployments by removing personal credentials from automation systems
Fine-grained access control with specific permissions for each token
Simplified CI/CD pipelines with built-in authentication variables
Reliable deployment processes that won’t break when team members change
Better audit trails by tracking deployments through dedicated token identities
Seamless integration with external build systems and deployment tools
A deploy token is a pair of values:
username
:
username
in the HTTP authentication framework. The default username format is
gitlab+deploy-token-{n}
. You can specify a custom username when you create the deploy token.
token
:
password
in the HTTP authentication framework.
Deploy tokens do not support
SSH authentication
.
You can use a deploy token for
HTTP authentication
to the following endpoints:
GitLab package registry public API.
Git commands
.
GitLab virtual registry package operations
.
You can create deploy tokens at either the project or group level:
Project deploy token
: Permissions apply only to the project.
Group deploy token
: Permissions apply to all projects in the group.
By default, a deploy token does not expire. You can optionally set an expiry date when you create
it. Expiry occurs at midnight UTC on that date.
You cannot use new or existing deploy tokens for Git operations and package registry operations if
external authorization
is enabled.
Scope
A deploy token’s scope determines the actions it can perform.
Scope
Description
read_repository
Read-only access to the repository using
git clone
.
read_registry
Read-only access to the images in the project’s
container registry
.
write_registry
Write access (push) to the project’s
container registry
. You need both read and write access to push images.
read_virtual_registry
If a project is private and authorization is required, grants read-only (pull) access to container images through the
dependency proxy
. Available only when the dependency proxy is enabled.
write_virtual_registry
If a project is private and authorization is required, grants read (pull), write (push), and delete access to container images through the
dependency proxy
. Available only when the dependency proxy is enabled.
read_package_registry
Read-only access to the project’s package registry.
write_package_registry
Write access to the project’s package registry.
GitLab deploy token
History
Support for
gitlab-deploy-token
at the group level
introduced
in GitLab 15.1
with a flag
named
ci_variable_for_group_gitlab_deploy_token
. Enabled by default.
Feature flag
ci_variable_for_group_gitlab_deploy_token
removed in GitLab 15.4.
A GitLab deploy token is a special type of deploy token. If you create a deploy token named
gitlab-deploy-token
, the deploy token is automatically exposed to project CI/CD jobs as variables:
CI_DEPLOY_USER
: Username
CI_DEPLOY_PASSWORD
: Token
For example, to use a GitLab token to sign in to your GitLab container registry:
echo
"
$CI_DEPLOY_PASSWORD
"
|
docker login
$CI_REGISTRY
-u
$CI_DEPLOY_USER
--password-stdin
In GitLab 15.0 and earlier, the special handling for the
gitlab-deploy-token
deploy token does not
work for group deploy tokens. To make a group deploy token available for CI/CD jobs, set the
CI_DEPLOY_USER
and
CI_DEPLOY_PASSWORD
CI/CD variables in
Settings
>
CI/CD
>
Variables
to the
name and token of the group deploy token.
When
gitlab-deploy-token
is defined in a group, the
CI_DEPLOY_USER
and
CI_DEPLOY_PASSWORD
CI/CD variables are available only to immediate child projects of the group.
Deploy token expiration
History
Email notifications for deploy token expiration
introduced
in GitLab 18.3
with a flag
named
project_deploy_token_expiring_notifications
. Disabled by default.
The availability of this feature is controlled by a feature flag.
For more information, see the history.
Deploy tokens expire on the date you define at 00:00 AM UTC.
GitLab checks every day at 01:00 AM UTC for deploy tokens that are about to expire.
Project owners and maintainers are notified by email 60, 30, and 7 days before these tokens expire.
These email notifications are sent only once per interval for active (non-revoked) deploy tokens.
GitLab deploy token security
GitLab deploy tokens are long-lived, making them attractive for attackers.
To prevent leaking the deploy token, you should also configure your
runners
to be secure:
Avoid using Docker
privileged
mode if the machines are re-used.
Avoid using the
shell
executor
when jobs
run on the same machine.
An insecure GitLab Runner configuration increases the risk that someone can steal tokens from other
jobs.
GitLab public API
Deploy tokens can’t be used with the GitLab public API. However, you can use deploy tokens with some
endpoints, such as those from the package registry. You can tell an endpoint belongs to the package registry because the URL has the string
packages/<format>
. For example:
https://gitlab.example.com/api/v4/projects/24/packages/generic/my_package/0.0.1/file.txt
. For more information, see
Authenticate with the registry
.
Create a deploy token
Create a deploy token to automate deployment tasks that can run independently of a user account.
Prerequisites:
To create a group deploy token, you must have the Owner role for the group.
To create a project deploy token, you must have at least the Maintainer role for the project.
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Repository
.
Expand
Deploy tokens
.
Select
Add token
.
Complete the fields, and select the desired
scopes
.
Select
Create deploy token
.
Record the deploy token’s values. After you leave or refresh the page,
you cannot access it
again
.
Revoke a deploy token
Revoke a token when it’s no longer required.
Prerequisites:
To revoke a group deploy token, you must have the Owner role for the group.
To revoke a project deploy token, you must have at least the Maintainer role for the project.
To revoke a deploy token:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Repository
.
Expand
Deploy tokens
.
In the
Active Deploy Tokens
section, by the token you want to revoke, select
Revoke
.
Clone a repository
You can use a deploy token to clone a repository.
Prerequisites:
A deploy token with the
read_repository
scope.
Example of using a deploy token to clone a repository:
git clone https://<username>:<deploy_token>@gitlab.example.com/tanuki/awesome_project.git
Pull images from a container registry
You can use a deploy token to pull images from a container registry.
Prerequisites:
A deploy token with the
read_registry
scope.
Example of using a deploy token to pull images from a container registry:
echo
"
$DEPLOY_TOKEN
"
|
docker login -u <username> --password-stdin registry.example.com
docker pull
$CONTAINER_TEST_IMAGE
Push images to a container registry
You can use a deploy token to push images to a container registry.
Prerequisites:
A deploy token with the
read_registry
and
write_registry
scope.
Example of using a deploy token to push an image to a container registry:
echo
"
$DEPLOY_TOKEN
"
|
docker login -u <username> --password-stdin registry.example.com
docker push
$CONTAINER_TEST_IMAGE
Pull packages from a package registry
You can use a deploy token to pull packages from a package registry.
Prerequisites:
A deploy token with the
read_package_registry
scope.
For the
package type of your choice
, follow the authentication
instructions for deploy tokens.
Example of installing a NuGet package from a GitLab registry:
nuget
source
Add -Name GitLab -Source
"https://gitlab.example.com/api/v4/projects/10/packages/nuget/index.json"
-UserName <username> -Password <deploy_token>
nuget install mypkg.nupkg
Push packages to a package registry
You can use a deploy token to push packages to a GitLab package registry.
Prerequisites:
A deploy token with the
write_package_registry
scope.
For the
package type of your choice
, follow the authentication
instructions for deploy tokens.
Example of publishing a NuGet package to a package registry:
nuget
source
Add -Name GitLab -Source
"https://gitlab.example.com/api/v4/projects/10/packages/nuget/index.json"
-UserName <username> -Password <deploy_token>
nuget push mypkg.nupkg -Source GitLab
Pull images from the dependency proxy
You can use a deploy token to pull images from the dependency proxy.
Prerequisites:
A deploy token with
read_registry
and
write_registry
scopes.
Follow the dependency proxy
authentication instructions
.
