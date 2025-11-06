# Authenticate with the container registry | GitLab Docs

Source: https://docs.gitlab.com/user/packages/container_registry/authenticate_with_container_registry/

Authenticate with the container registry | GitLab Docs
Authenticate with the container registry
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
To authenticate with the container registry, you can use:
GitLab username and password (not available if 2FA is enabled)
Personal access token
Deploy token
Project access token
Group access token
The
GitLab CLI
For token-based authentication methods, the minimum required scope:
For read (pull) access, must be
read_registry
For write (push) access, must be
write_registry
and
read_registry
Admin Mode does not apply during authentication with the container registry. If you are an administrator
with Admin Mode enabled, and you create a personal access token without the
admin_mode
scope,
that token works even though Admin Mode is enabled. For more information, see
Admin Mode
.
Authenticate with username and password
You can authenticate with the container registry using
your GitLab username and password:
docker login registry.example.com -u <username> -p <password>
For security reasons, it’s recommended to use the
--password-stdin
flag instead of
-p
:
echo
"<password>"
|
docker login registry.example.com -u <username> --password-stdin
Username and password authentication is not available if you have two-factor authentication (2FA) enabled.
In this case, you must use a token-based authentication method.
Authenticate with a token
To authenticate with a token, run the
docker login
command:
TOKEN
=
<token>
echo
"
$TOKEN
"
|
docker login registry.example.com -u <username> --password-stdin
After authentication, the client caches the credentials. Later operations make authorization
requests that return JWT tokens, authorized to do only the specified operation.
Tokens remain valid:
For
5 minutes by default
on GitLab Self-Managed
For
15 minutes
on GitLab.com
Use GitLab CI/CD to authenticate
To use CI/CD to authenticate with the container registry, you can use:
The
CI_REGISTRY_USER
CI/CD variable.
This variable holds a per-job user with read-write access to the container registry.
Its password is also automatically created and available in
CI_REGISTRY_PASSWORD
.
echo
"
$CI_REGISTRY_PASSWORD
"
|
docker login
$CI_REGISTRY
-u
$CI_REGISTRY_USER
--password-stdin
A
CI job token
.
This token can only be used for read (pull) access. It has the
read_registry
scope but not the
write_registry
scope needed for push operations.
echo
"
$CI_JOB_TOKEN
"
|
docker login
$CI_REGISTRY
-u
$CI_REGISTRY_USER
--password-stdin
You can also use the
gitlab-ci-token
scheme:
echo
"
$CI_JOB_TOKEN
"
|
docker login
$CI_REGISTRY
-u gitlab-ci-token --password-stdin
A
GitLab deploy token
with the minimum scope of:
For read (pull) access,
read_registry
.
For write (push) access,
read_registry
and
write_registry
.
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
A personal access token with the minimum scope of:
For read (pull) access,
read_registry
.
For write (push) access,
read_registry
and
write_registry
.
echo
"<access_token>"
|
docker login
$CI_REGISTRY
-u <username> --password-stdin
Troubleshooting
docker login
command fails with
access forbidden
The container registry returns the GitLab API URL to the Docker client
to validate credentials. The Docker client uses basic auth, so the request contains
the
Authorization
header. If the
Authorization
header is missing in the request to the
/jwt/auth
endpoint configured in the
token_realm
for the registry configuration,
you receive an
access forbidden
error message.
For example:
> docker login gitlab.example.com:4567
Username: user
Password:
Error response from daemon: Get "https://gitlab.company.com:4567/v2/": denied: access forbidden
To avoid this error, ensure the
Authorization
header is not stripped from the request.
For example, a proxy in front of GitLab might be redirecting to the
/jwt/auth
endpoint.
For more information about credential validation with Docker clients, see
Container registry architecture
.
unauthorized: authentication required
when pushing large images
When pushing large images, you may see an authentication error like the following:
docker push gitlab.example.com/myproject/docs:latest
The push refers to a repository
[
gitlab.example.com/myproject/docs
]
630816f32edb: Preparing
530d5553aec8: Preparing
...
4b0bab9ff599: Waiting
d1c800db26c7: Waiting
42755cf4ee95: Waiting
unauthorized: authentication required
This error happens when your authentication token expires before the image push is complete.
By default, tokens for the container registry on GitLab Self-Managed instances expire after five minutes.
On GitLab.com, the token expiration time is 15 minutes.
