# Troubleshooting job artifacts | GitLab Docs

Source: https://docs.gitlab.com/ci/jobs/job_artifacts_troubleshooting/#error-message-this-job-could-not-start-because-it-could-not-retrieve-the-needed-artifacts

Troubleshooting job artifacts | GitLab Docs
Troubleshooting job artifacts
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
When working with
job artifacts
, you might encounter the following issues.
Job does not retrieve certain artifacts
By default, jobs fetch all artifacts from previous stages, but jobs using
dependencies
or
needs
do not fetch artifacts from all jobs by default.
If you use these keywords, artifacts are fetched from only a subset of jobs. Review
the keyword reference for information on how to fetch artifacts with these keywords:
dependencies
needs
needs:artifacts
Job artifacts use too much disk space
If job artifacts are using too much disk space, see the
job artifacts administration documentation
.
Error message
No files to upload
This message appears in job logs when a the runner can’t find the file to upload. Either
the path to the file is incorrect, or the file was not created. You can check the job
log for other errors or warnings that specify the filename and why it wasn’t
generated.
For more detailed job logs, you can
enable CI/CD debug logging
and try the job again. This logging might provide more information about why the file
wasn’t created.
Error message
FATAL: invalid argument
when uploading a dotenv artifact on a Windows runner
The PowerShell
echo
command writes files with UCS-2 LE BOM (Byte Order Mark) encoding,
but only UTF-8 is supported. If you try to create a
dotenv
artifact with
echo
, it causes a
FATAL: invalid argument
error.
Use PowerShell
Add-Content
instead, which uses UTF-8:
test-job
:
stage
:
test
tags
:
-
windows
script
:
-
echo "test job"
-
Add-Content -Path build.env -Value "MY_ENV_VAR=true"
artifacts
:
reports
:
dotenv
:
build.env
Job artifacts do not expire
If some job artifacts are not expiring as expected, check if the
Keep artifacts from most recent successful jobs
setting is enabled.
When this setting is enabled, job artifacts from the latest successful pipeline
of each ref do not expire and are not deleted.
Error message
This job could not start because it could not retrieve the needed artifacts.
A job fails to start and returns this error message if it can’t fetch the artifacts
it expects. This error is returned when:
The job’s dependencies are not found. By default, jobs in later stages fetch artifacts
from jobs in all earlier stages, so the earlier jobs are all considered dependent.
If the job uses the
dependencies
keyword, only
the listed jobs are dependent.
The artifacts are already expired. You can set a longer expiry with
artifacts:expire_in
.
The job cannot access the relevant resources due to insufficient permissions.
See these additional troubleshooting steps if the job uses the
needs:artifacts
:
keyword with:
needs:project
needs:pipeline:job
For a job configured with
needs:project
The
could not retrieve the needed artifacts.
error can happen for a job using
needs:project
with a configuration similar to:
rspec
:
needs
:
-
project
:
my-group/my-project
job
:
dependency-job
ref
:
master
artifacts
:
true
To troubleshoot this error, verify that:
Project
my-group/my-project
is in a group with a Premium subscription plan.
The user running the job can access resources in
my-group/my-project
.
The
project
,
job
, and
ref
combination exists and results in the desired dependency.
Any variables in use evaluate to the correct values.
If you use the
CI_JOB_TOKEN
, add the token to the project’s
allowlist
to pull artifacts from a different project.
For a job configured with
needs:pipeline:job
The
could not retrieve the needed artifacts.
error can happen for a job using
needs:pipeline:job
with a configuration similar to:
rspec
:
needs
:
-
pipeline
:
$UPSTREAM_PIPELINE_ID
job
:
dependency-job
artifacts
:
true
To troubleshoot this error, verify that:
The
$UPSTREAM_PIPELINE_ID
CI/CD variable is available in the current pipeline’s
parent-child pipeline hierarchy.
The
pipeline
and
job
combination exists and resolves to an existing pipeline.
dependency-job
has run and finished successfully.
Jobs show
UnlockPipelinesInQueueWorker
after an upgrade
Jobs might stall and show an error that states
UnlockPipelinesInQueueWorker
.
This issue occurs after an upgrade.
The workaround is to enable the
ci_unlock_pipelines_extra_low
feature flag.
To toggle feature flags, you must be an administrator.
On GitLab SaaS:
Run the following
ChatOps
command:
/chatops run feature set ci_unlock_pipelines_extra_low true
On GitLab Self-Managed:
Enable the feature flag
named
ci_unlock_pipelines_extra_low
.
For more information see the comment in
merge request 140318
.
