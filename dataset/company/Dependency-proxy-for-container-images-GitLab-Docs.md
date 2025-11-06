# Dependency proxy for container images | GitLab Docs

Source: https://docs.gitlab.com/user/packages/dependency_proxy/

Dependency proxy for container images | GitLab Docs
Dependency proxy for container images
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
The GitLab dependency proxy for container images is a local proxy you can use for your frequently-accessed
upstream images.
In the case of CI/CD, the dependency proxy receives a request and returns the
upstream image from a registry, acting as a pull-through cache.
Prerequisites
To use the dependency proxy for container images, it must be enabled for the GitLab instance. It’s enabled by default,
but
administrators can turn it off
.
Supported images and packages
The following images and packages are supported.
Image/Package
GitLab version
Docker
14.0+
For a list of planned additions, view the
direction page
.
Enable or turn off the dependency proxy for a group
History
Required role
changed
from Developer to Maintainer in GitLab 15.0.
Required role
changed
from Maintainer to Owner in GitLab 17.0.
To enable or turn off the dependency proxy for a group:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Packages and registries
.
Expand the
Dependency Proxy
section.
To enable the proxy, turn on
Enable Proxy
. To turn it off, turn the toggle off.
This setting only affects the dependency proxy for a group. Only an administrator can
turn the dependency proxy on or off
for the entire GitLab instance.
View the dependency proxy for container images
To view the dependency proxy for container images:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Operate
>
Dependency Proxy
.
The dependency proxy is not available for projects.
Use the dependency proxy for Docker images
You can use GitLab as a source for your Docker images.
Prerequisites:
Your images must be stored on
Docker Hub
.
Authenticate with the dependency proxy for container images
History
Removed
the feature flag
dependency_proxy_for_private_groups
in GitLab 15.0.
Support for group access tokens
introduced
in GitLab 16.3.
Deploy token scopes
read_virtual_registry
and
write_virtual_registry
introduced
in GitLab 17.11 with a flag named
dependency_proxy_read_write_scopes
. Disabled by default.
Generally available
in GitLab 18.0. Feature flag
dependency_proxy_read_write_scopes
removed.
Because the dependency proxy for container images is storing Docker images in a space associated with your group,
you must authenticate with it.
Follow the
instructions for using images from a private registry
,
but instead of using
registry.example.com:5000
, use your GitLab domain with no port
gitlab.example.com
.
Admin Mode
does not apply during authentication with the dependency proxy for container images. If you are an administrator with Admin Mode enabled, and you create a personal access token without the
admin_mode
scope, that token works even though Admin Mode is enabled.
For example, to manually sign in:
echo
"
$CONTAINER_REGISTRY_PASSWORD
"
|
docker login gitlab.example.com --username my_username --password-stdin
You can authenticate using:
Your GitLab username and password.
The
GitLab CLI
.
A
personal access token
.
A
group deploy token
.
A
group access token
for the group.
The token should have the scope set to one of the following:
api
: Grants full API access.
read_registry
: Grants read-only access to the container registry.
write_registry
: Grants both read and write access to the container registry.
read_virtual_registry
: Grants read-only access (pull) to container images through the dependency proxy.
write_virtual_registry
: Grants read (pull), write (push), and delete access to container images through the dependency proxy.
When authenticating with the dependency proxy for container images:
Tokens with the
read_virtual_registry
scope must also include the
read_registry
scope.
Tokens with the
write_virtual_registry
scope must also include the
write_registry
scope.
Users accessing the dependency proxy for container images with a personal access token or username and password must
have at least the Guest role for the group they pull images from.
The dependency proxy for container images follows the
Docker v2 token authentication flow
,
issuing the client a JWT to use for the pulls. The JWT issued as a result of authenticating
expires after some time. When the token expires, most Docker clients store your credentials and
automatically request a new token without further action.
The token expiration time is a
configurable setting
.
On GitLab.com, the expiration time is 15 minutes.
SAML SSO
When
SSO enforcement
is enabled, users must be signed-in through SSO before they can pull images through the dependency proxy for container images.
SSO enforcement also affects
auto-merge
.
If an SSO session expires before the auto-merge triggers, the merge pipeline fails
to pull images through the dependency proxy.
Authenticate within CI/CD
Runners sign in to the dependency proxy for container images automatically. To pull through
the dependency proxy, use one of the
predefined variables
:
CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX
pulls through the top-level group.
CI_DEPENDENCY_PROXY_DIRECT_GROUP_IMAGE_PREFIX
pulls through the subgroup, or direct group the
project exists in.
Example pulling the latest alpine image:
# .gitlab-ci.yml
image
:
${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/alpine:latest
There are other additional predefined CI/CD variables you can also use:
CI_DEPENDENCY_PROXY_USER
: A CI/CD user for logging in to the dependency proxy.
CI_DEPENDENCY_PROXY_PASSWORD
: A CI/CD password for logging in to the dependency proxy
CI_DEPENDENCY_PROXY_SERVER
: The server for logging in to the dependency proxy.
CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX
: the image prefix for pulling images through the
dependency proxy from the top-level group.
CI_DEPENDENCY_PROXY_DIRECT_GROUP_IMAGE_PREFIX
: the image prefix for pulling images through the
dependency proxy from the direct group or subgroup that the project belongs to.
CI_DEPENDENCY_PROXY_SERVER
,
CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX
, and
CI_DEPENDENCY_PROXY_DIRECT_GROUP_IMAGE_PREFIX
include the server port. If you explicitly include the dependency proxy
path, the port must be included, unless you have logged into the dependency proxy manually without including the port:
docker pull gitlab.example.com:443/my-group/dependency_proxy/containers/alpine:latest
Example when using the dependency proxy to build an image:
# Dockerfile
FROM gitlab.example.com:443/my-group/dependency_proxy/containers/alpine:latest
# .gitlab-ci.yml
image
:
docker:20.10.16
variables
:
DOCKER_HOST
:
tcp://docker:2375
DOCKER_TLS_CERTDIR
:
""
services
:
-
docker:20.10.16-dind
build
:
image
:
docker:20.10.16-cli
before_script
:
-
echo "$CI_DEPENDENCY_PROXY_PASSWORD" | docker login $CI_DEPENDENCY_PROXY_SERVER -u $CI_DEPENDENCY_PROXY_USER --password-stdin
script
:
-
docker build -t test .
You can also use
custom CI/CD variables
to store and access your personal access token or deploy token.
Authenticate with Docker Hub
History
Support for Docker Hub credentials
added
in GitLab 17.10.
UI support
added
in GitLab 17.11.
By default, the Dependency Proxy does not use credentials when pulling images from Docker Hub.
You can configure Docker Hub authentication using your Docker Hub credentials or tokens.
To authenticate with Docker Hub, you can use:
Your Docker Hub username and password.
This method is not compatible with Docker Hub organizations that
enforce Single Sign-On (SSO)
.
A Docker Hub
Personal Access Token
.
A Docker Hub
Organization Access Token
.
Configure credentials
To set Docker Hub credentials for the dependency proxy for a group:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Packages and registries
.
Expand the
Dependency Proxy
section.
Turn on
Enable Proxy
.
Under
Docker Hub authentication
, enter your credentials:
Identity
is your username (for password or Personal Access Token) or organization name (for Organization Access Token).
Secret
is your password, Personal Access Token, or Organization Access Token.
You must either complete both fields or leave both empty. If you leave both fields empty, requests to Docker Hub remain unauthenticated.
Configure credentials using the GraphQL API
To set Docker Hub credentials in the Dependency Proxy settings using the
GraphQL API
:
Go to GraphiQL:
For GitLab.com, use
https://gitlab.com/-/graphql-explorer
.
For GitLab Self-Managed, use
https://gitlab.example.com/-/graphql-explorer
.
In GraphiQL, enter this mutation:
mutation
{
updateDependencyProxySettings
(
input
:
{
enabled
:
true
,
identity
:
"<identity>"
,
secret
:
"<secret>"
,
groupPath
:
"<group path>"
})
{
dependencyProxySetting
{
enabled
identity
}
errors
}
}
Where:
<identity>
is your username (for password or Personal Access Token) or organization name (for Organization Access Token).
<secret>
is your password, Personal Access Token, or Organization Access Token.
<group path>
is the path of the group where the Dependency Proxy is located.
Select
Play
.
Check for any errors in the results pane.
Verify your credentials
After you authenticate with the Dependency Proxy, verify your Docker Hub credentials by pulling a Docker image:
docker pull gitlab.example.com/groupname/dependency_proxy/containers/alpine:latest
If authentication is successful, you’ll see activity in your
Docker Hub Usage dashboard
.
Store a Docker image in dependency proxy cache
To store a Docker image in dependency proxy storage:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Operate
>
Dependency Proxy
.
Copy the
Dependency Proxy image prefix
.
Use one of these commands. In these examples, the image is
alpine:latest
.
You can also pull images by digest to specify exactly which version of an image to pull.
Pull an image by tag by adding the image to your
.gitlab-ci.yml
file:
image: gitlab.example.com/groupname/dependency_proxy/containers/alpine:latest
Pull an image by digest by adding the image to your
.gitlab-ci.yml
file:
image:
${
CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX
}
/alpine@sha256:c9375e662992791e3f39e919b26f510e5254b42792519c180aad254e6b38f4dc
Manually pull the Docker image:
docker pull gitlab.example.com/groupname/dependency_proxy/containers/alpine:latest
Add the URL to a
Dockerfile
:
FROM gitlab.example.com/groupname/dependency_proxy/containers/alpine:latest
GitLab pulls the Docker image from Docker Hub and caches the blobs
on the GitLab server. The next time you pull the same image, GitLab gets the latest
information about the image from Docker Hub, but serves the existing blobs
from the GitLab server.
Reduce storage usage
For information on reducing your storage use on the dependency proxy for container images, see
Reduce dependency proxy storage use
.
Docker Hub rate limits and the dependency proxy
Watch how to
use the dependency proxy to help avoid Docker Hub rate limits
.
Docker Hub enforces
rate limits on pulls
.
If your GitLab
CI/CD configuration
uses
an image from Docker Hub, each time a job runs, it may count as a pull.
To help get around this limit, you can pull your image from the dependency proxy cache instead.
When you pull an image (by using a command like
docker pull
or, in a
.gitlab-ci.yml
file,
image: foo:latest
), the Docker client makes a collection of requests:
The image manifest is requested. The manifest contains information about
how to build the image.
Using the manifest, the Docker client requests a collection of layers, also
known as blobs, one at a time.
The Docker Hub rate limit is based on the number of GET requests for the manifest. The dependency proxy
caches both the manifest and blobs for a given image, so when you request it again,
Docker Hub does not have to be contacted.
How does GitLab know if a cached tagged image is stale?
If you are using an image tag like
alpine:latest
, the image changes
over time. Each time it changes, the manifest contains different information about which
blobs to request. The dependency proxy does not pull a new image each time the
manifest changes; it checks only when the manifest becomes stale.
Docker does not count HEAD requests for the image manifest towards the rate limit.
You can make a HEAD request for
alpine:latest
, view the digest (checksum)
value returned in the header, and determine if a manifest has changed.
The dependency proxy starts all requests with a HEAD request. If the manifest
has become stale, only then is a new image pulled.
For example, if your pipeline pulls
node:latest
every five
minutes, the dependency proxy caches the entire image and only updates it if
node:latest
changes. So instead of having 360 requests for the image in six hours
(which exceeds the Docker Hub rate limit), you only have one pull, unless
the manifest changed during that time.
Check your Docker Hub rate limit
If you are curious about how many requests to Docker Hub you have made and how
many remain, you can run these commands from your runner, or even in a CI/CD
script:
# Note, you must have jq installed to run this command
TOKEN
=
$(
curl
"https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull"
|
jq --raw-output .token
)
&&
curl --head --header
"Authorization: Bearer
$TOKEN
"
"https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest"
2>
&
1
|
grep --ignore-case RateLimit
...
The output is something like:
RateLimit-Limit: 100
;
w
=
21600
RateLimit-Remaining: 98
;
w
=
21600
This example shows the total limit of 100 pulls in six hours, with 98 pulls remaining.
Check the rate limit in a CI/CD job
This example shows a GitLab CI/CD job that uses an image with
jq
and
curl
installed:
hub_docker_quota_check
:
stage
:
build
image
:
alpine:latest
tags
:
-
<optional_runner_tag>
before_script
:
apk add curl jq
script
:
-
|
TOKEN=$(curl "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" | jq --raw-output .token) && curl --head --header "Authorization: Bearer $TOKEN" "https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest" 2>&1
Troubleshooting
Authentication error:
HTTP Basic: Access Denied
If you receive an
HTTP Basic: Access denied
error when authenticating against the dependency proxy, refer to the
two-factor authentication troubleshooting guide
.
Dependency proxy connection failure
If a service alias is not set the
docker:20.10.16
image is unable to find the
dind
service, and an error like the following is thrown:
error during connect: Get http://docker:2376/v1.39/info: dial tcp: lookup docker on 192.168.0.1:53: no such host
This can be resolved by setting a service alias for the Docker service:
services
:
-
name
:
${CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX}/docker:18.09.7-dind
alias
:
docker
Issues when authenticating to the dependency proxy from CI/CD jobs
GitLab Runner authenticates automatically to the dependency proxy. However, the underlying Docker engine is still subject to its
authorization resolving process
.
Misconfigurations in the authentication mechanism may cause
HTTP Basic: Access denied
and
403: Access forbidden
errors.
You can use the job logs to view the authentication mechanism used to authenticate against the dependency proxy:
Authenticating with credentials from $DOCKER_AUTH_CONFIG
Authenticating with credentials from /root/.docker/config.json
Authenticating with credentials from job payload (GitLab Registry)
Make sure you are using the expected authentication mechanism.
Not Found
or
404
error when pulling image
Errors like these might indicate that the user running the job doesn’t have
a minimum of the Guest role for the dependency proxy group:
ERROR: gitlab.example.com:443/group1/dependency_proxy/containers/alpine:latest: not found
failed to solve with frontend dockerfile.v0: failed to create LLB definition: gitlab.example.com:443/group1/dependency_proxy/containers/alpine:latest: not found
ERROR: Job failed: failed to pull image "gitlab.example.com:443/group1/dependency_proxy/containers/alpine:latest" with specified policies [always]:
Error response from daemon: error parsing HTTP 404 response body: unexpected end of JSON input: "" (manager.go:237:1s)
For more information about the work to improve the error messages in similar cases to
Access denied
,
see
issue 354826
.
exec format error
when running images from the dependency proxy
This issue was
resolved
in GitLab 16.3.
For GitLab Self-Managed instances that are 16.2 or earlier, you can update your instance to 16.3
or use the workaround documented below.
This error occurs if you try to use the dependency proxy on an ARM-based Docker install in GitLab 16.2 or earlier.
The dependency proxy only supports the x86_64 architecture when pulling an image with a specific tag.
As a workaround, you can specify the SHA256 of the image to force the dependency proxy
to pull a different architecture:
docker pull
${
CI_DEPENDENCY_PROXY_GROUP_IMAGE_PREFIX
}
/library/docker:20.10.3@sha256:bc9dcf5c8e5908845acc6d34ab8824bca496d6d47d1b08af3baf4b3adb1bd8fe
In this example,
bc9dcf5c8e5908845acc6d34ab8824bca496d6d47d1b08af3baf4b3adb1bd8fe
is the SHA256 of the ARM based image.
MissingFile
errors after restoring a backup
If you encounter
MissingFile
or
Cannot read file
errors, it might be because
backup archives
do not include the contents of
gitlab-rails/shared/dependency_proxy/
.
To resolve this
known issue
,
you can use
rsync
,
scp
, or a similar tool to copy the affected files or the whole
gitlab-rails/shared/dependency_proxy/
folder structure from the GitLab instance
that was the source of the backup.
If the data is not needed, you can delete the database entries with:
gitlab-psql -c
"DELETE FROM dependency_proxy_blobs; DELETE FROM dependency_proxy_blob_states; DELETE FROM dependency_proxy_manifest_states; DELETE FROM dependency_proxy_manifests;"
