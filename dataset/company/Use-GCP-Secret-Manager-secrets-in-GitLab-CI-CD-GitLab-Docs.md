# Use GCP Secret Manager secrets in GitLab CI/CD | GitLab Docs

Source: https://docs.gitlab.com/ci/secrets/gcp_secret_manager/

Use GCP Secret Manager secrets in GitLab CI/CD | GitLab Docs
Use GCP Secret Manager secrets in GitLab CI/CD
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab and GitLab Runner 16.8.
You can use secrets stored in the
Google Cloud (GCP) Secret Manager
in your GitLab CI/CD pipelines.
The flow for using GitLab with GCP Secret Manager is:
GitLab issues an ID token to the CI/CD job.
The runner authenticates to GCP using the ID token.
GCP verifies the ID token with GitLab.
GCP issues a short-lived access token.
The runner accesses the secret data using the access token.
GCP checks IAM secret permission on the access token’s principal.
GCP returns the secret data to the runner.
To use GitLab with GCP Secret Manager, you must:
Have secrets stored in
GCP Secret Manager
.
Configure
GCP Workload Identity Federation
to include GitLab as an identity provider.
Configure
GCP IAM
permissions to grant access to GCP Secret Manager.
Configure
GitLab CI/CD with GCP Secret Manager
.
Configure GCP IAM Workload Identity Federation (WIF)
GCP IAM WIF must be configured to recognize ID tokens issued by GitLab and assign an appropriate principal to them.
The principal is used to authorize access to the Secret Manager resources:
In GCP Console, go to
IAM & Admin > Workload Identity Federation
.
Select
CREATE POOL
and create a new identity pool with a unique name, for example
gitlab-pool
.
Select
ADD PROVIDER
to add a new OIDC Provider to the Identity Pool with a unique name, for example
gitlab-provider
.
Set
Issuer (URL)
to the GitLab URL, for example
https://gitlab.com
.
Select
Default audience
, or select
Allowed audiences
for a custom audience, which is used in the
aud
for the GitLab CI/CD ID token.
Under
Attribute Mapping
, create the following mappings, where:
attribute.X
is the name of the attribute to include as a claim in the Google token.
assertion.X
is the value to extract from the
GitLab claim
.
Attribute (on Google)
Assertion (from GitLab)
google.subject
assertion.sub
attribute.gitlab_project_id
assertion.project_id
Grant access to GCP IAM principal
After setting up WIF, you must grant the WIF principal access to the secrets in Secret Manager.
In GCP Console, go to
Security > Secret Manager
.
Select the name of the secret you wish to grant access to, to view the secret’s details.
From the
PERMISSIONS
tab, select
GRANT ACCESS
to grant access to the principal set created through the WIF provider.
The external identity format is:
principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.gitlab_project_id/GITLAB_PROJECT_ID
In this example:
PROJECT_NUMBER
: Your Google Cloud project number (not ID) which can be found in the
Project’s dashboard
.
POOL_ID
: The ID (not name) of the workload identity pool created in the first section,
for example
gitlab-pool
.
GITLAB_PROJECT_ID
: The GitLab project ID found on the
project overview page
.
Assign the role
Secret Manager Secret Accessor
.
Configure GitLab CI/CD to use GCP Secret Manager secrets
You must
add these CI/CD variables
to provide details about
your GCP Secret Manager:
GCP_PROJECT_NUMBER
: The GCP
Project Number
.
GCP_WORKLOAD_IDENTITY_FEDERATION_POOL_ID
: The WIF Pool ID, for example
gitlab-pool
.
GCP_WORKLOAD_IDENTITY_FEDERATION_PROVIDER_ID
: The WIF Provider ID, for example
gitlab-provider
.
Then you can use secrets stored in GCP Secret Manager in CI/CD jobs by defining them
with the
gcp_secret_manager
keyword:
job_using_gcp_sm
:
id_tokens
:
GCP_ID_TOKEN
:
# `aud` must match the audience defined in the WIF Identity Pool.
aud
:
https://iam.googleapis.com/projects/${GCP_PROJECT_NUMBER}/locations/global/workloadIdentityPools/${GCP_WORKLOAD_IDENTITY_FEDERATION_POOL_ID}/providers/${GCP_WORKLOAD_IDENTITY_FEDERATION_PROVIDER_ID}
secrets
:
DATABASE_PASSWORD
:
gcp_secret_manager
:
name
:
my-project-secret
# This is the name of the secret defined in GCP Secret Manager
version: 1 # optional
:
default to `latest`.
token
:
$GCP_ID_TOKEN
Use secrets from a different GCP project
History
Introduced
in GitLab 17.0.
Secret names in GCP are per-project. By default the secret named in
gcp_secret_manager:name
is read from the project specified in
GCP_PROJECT_NUMBER
.
To read a secret from a different project than the project containing the WIF pool, use the
fully-qualified secret name formatted as
projects/<project-number>/secrets/<secret-name>
.
For example, if
my-project-secret
is in the GCP project number
123456789
,
then you can access the secret with:
job_using_gcp_sm
:
# ... as previously configured ...
secrets
:
DATABASE_PASSWORD
:
gcp_secret_manager
:
name
:
projects/123456789/secrets/my-project-secret
# fully-qualified name of the secret defined in GCP Secret Manager
version: 1 # optional
:
defaults to `latest`.
token
:
$GCP_ID_TOKEN
Troubleshooting
Error: The size of mapped attribute
google.subject
exceeds the 127 bytes limit
Long branch paths can cause a job to fail with this error, because the
assertion.sub
attribute
becomes longer than 127 characters:
ERROR: Job failed (system failure): resolving secrets: failed to exchange sts token: googleapi: got HTTP response code 400 with body:
{"error":"invalid_request","error_description":"The size of mapped attribute google.subject exceeds the 127 bytes limit.
Either modify your attribute mapping or the incoming assertion to produce a mapped attribute that is less than 127 bytes."}
Long branch paths can be caused by:
Deeply nested subgroups.
Long group, repository, or branch names.
For example, for a
gitlab-org/gitlab
branch, the payload is
project_path:gitlab-org/gitlab:ref_type:branch:ref:{branch_name}
.
For the string to remain shorter than 127 characters, the branch name must be 76 characters or fewer.
This limit is imposed by Google Cloud IAM, tracked in
Google issue #264362370
.
The only fix for this issue is to use shorter names
for your branch and repository
.
The secrets provider can not be found. Check your CI/CD variables and try again.
message
You might receive this error when attempting to start a job configured to access GCP Secret Manager:
The secrets provider can not be found. Check your CI/CD variables and try again.
The job can’t be created because one or more of the required variables are not defined:
GCP_PROJECT_NUMBER
GCP_WORKLOAD_IDENTITY_FEDERATION_POOL_ID
GCP_WORKLOAD_IDENTITY_FEDERATION_PROVIDER_ID
WARNING: Not resolved: no resolver that can handle the secret
warning
The Google Cloud Secret Manager integration requires at least GitLab 16.8 and GitLab Runner 16.8.
This warning appears if the job is executed by a runner using a version earlier than 16.8.
On GitLab.com, there is a
known issue
causing SaaS runners to run an older version. As a workaround until this issue is fixed,
you can register your own GitLab Runner with version 16.8 or later.
