# Debugging CI/CD pipelines | GitLab Docs

Source: https://docs.gitlab.com/ci/debugging/#config-should-be-an-array-of-hashes-error-message

Debugging CI/CD pipelines | GitLab Docs
Debugging CI/CD pipelines
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
GitLab provides several tools to help make it easier to debug your CI/CD configuration.
If you are unable to resolve pipeline issues, you can get help from:
The
GitLab community forum
GitLab
Support
If you are having issues with a specific CI/CD feature, see the related troubleshooting section
for that feature:
Caching
CI/CD job tokens
Container registry
Docker
Downstream pipelines
Environments
GitLab Runner
ID tokens
Jobs
Job artifacts
Merge request pipelines
merged results pipelines
and
merge trains
Pipeline editor
Variables
YAML
includes
keyword
YAML
script
keyword
Debugging techniques
Verify syntax
An early source of problems can be incorrect syntax. The pipeline shows a
yaml invalid
badge and does not start running if any syntax or formatting problems are found.
Edit
.gitlab-ci.yml
with the pipeline editor
The
pipeline editor
is the recommended editing
experience (rather than the single file editor or the Web IDE). It includes:
Code completion suggestions that ensure you are only using accepted keywords.
Automatic syntax highlighting and validation.
The
CI/CD configuration visualization
,
a graphical representation of your
.gitlab-ci.yml
file.
Edit
.gitlab-ci.yml
locally
If you prefer to edit your pipeline configuration locally, you can use the
GitLab CI/CD schema in your editor to verify basic syntax issues. Any
editor with Schemastore support
uses
the GitLab CI/CD schema by default.
If you need to link to the schema directly, use this URL:
https://gitlab.com/gitlab-org/gitlab/-/blob/master/app/assets/javascripts/editor/schema/ci.json
To see the full list of custom tags covered by the CI/CD schema, check the
latest version of the schema.
Verify syntax with CI Lint tool
You can use the
CI Lint tool
to verify that the syntax of a CI/CD configuration
snippet is correct. Paste in full
.gitlab-ci.yml
files or individual job configurations,
to verify the basic syntax.
When a
.gitlab-ci.yml
file is present in a project, you can also use the CI Lint
tool to
simulate the creation of a full pipeline
.
It does deeper verification of the configuration syntax.
Use pipeline names
Use
workflow:name
to give names to all your pipeline types,
which makes it easier to identify pipelines in the pipelines list. For example:
variables
:
PIPELINE_NAME
:
"Default pipeline name"
workflow
:
name
:
'$PIPELINE_NAME'
rules
:
-
if
:
'$CI_PIPELINE_SOURCE == "merge_request_event"'
variables
:
PIPELINE_NAME
:
"Merge request pipeline"
-
if
:
'$CI_PIPELINE_SOURCE == "schedule" && $PIPELINE_SCHEDULE_TYPE == "hourly_deploy"'
variables
:
PIPELINE_NAME
:
"Hourly deployment pipeline"
-
if
:
'$CI_PIPELINE_SOURCE == "schedule"'
variables
:
PIPELINE_NAME
:
"Other scheduled pipeline"
-
if
:
'$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
variables
:
PIPELINE_NAME
:
"Default branch pipeline"
-
if
:
'$CI_COMMIT_BRANCH =~ /^\d{1,2}\.\d{1,2}-stable$/'
variables
:
PIPELINE_NAME
:
"Stable branch pipeline"
CI/CD variables
Verify variables
A key part of troubleshooting CI/CD is to verify which variables are present in a
pipeline, and what their values are. A lot of pipeline configuration is dependent
on variables, and verifying them is one of the fastest ways to find the source of
a problem.
Export the full list of variables
available in each problematic job. Check if the variables you expect are present,
and check if their values are what you expect.
Use variables to add flags to CLI commands
You can define CI/CD variables that are not used in standard pipeline runs, but can
be used for debugging on demand. If you add a variable like in the following example,
you can add it during manual runs of the
pipeline
or
individual job
to modify the command’s behavior.
For example:
my-flaky-job
:
variables
:
DEBUG_VARS
:
""
script
:
-
my-test-command $DEBUG_VARS /test-dirs
In this example,
DEBUG_VARS
is blank by default in standard pipelines. If you need to
debug the job’s behavior, run the pipeline manually and set
DEBUG_VARS
to
--verbose
for additional output.
Dependencies
Dependency-related issues are another common source of unexpected issues in pipelines.
Verify dependency versions
To validate that the correct versions of dependencies are being used in jobs, you can
output them before running the main script commands. For example:
job
:
before_script
:
-
node --version
-
yarn --version
script
:
-
my-javascript-tests.sh
Pin versions
While you might want to always use the latest version of a dependency or image,
an update could include breaking changes unexpectedly. Consider pinning
key dependencies and images to avoid surprise changes. For example:
variables
:
ALPINE_VERSION
:
'3.18.6'
job1
:
image
:
alpine:$ALPINE_VERSION
# This will never change unexpectedly
script
:
-
my-test-script.sh
job2
:
image
:
alpine:latest
# This might suddenly change
script
:
-
my-test-script.sh
You should still regularly check the dependency and image updates, as there might be
important security updates. Then you can manually update the version as part of a process that
verifies the updated image or dependency still works with your pipeline.
Verify job output
Make output verbose
If you use
--silent
to reduce the amount of output in a job log, it can make it
difficult to identify what went wrong in a job. Additionally, consider using
--verbose
when possible, for additional details.
job1
:
script
:
-
my-test-tool --silent
# If this fails, it might be impossible to identify the issue.
-
my-other-test-tool --verbose
# This command will likely be easier to debug.
Save output and reports as artifacts
Some tools might generate files that are only needed while the job is running,
but the content of these files could be used for debugging. You can save them for
later analysis with
artifacts
:
job1
:
script
:
-
my-tool --json-output my-output.json
artifacts
:
paths
:
-
my-output.json
Reports configured with
artifacts:reports
are not available
for download by default, but could also contain information to help with debugging.
Use the same technique to make these reports available for inspection:
job1
:
script
:
-
rspec --format RspecJunitFormatter --out rspec.xml
artifacts
:
reports
:
junit
:
rspec.xml
paths
:
-
rspec.xmp
Do not save tokens, passwords, or other sensitive information in artifacts,
as they could be viewed by any user with access to the pipelines.
Run the job’s commands locally
You can use a tool like
Rancher Desktop
or similar alternatives
to run the job’s container image on your local machine. Then, run the job’s
script
commands
in the container and verify the behavior.
Troubleshoot a failed job with Root Cause Analysis
You can use GitLab Duo Root Cause Analysis in GitLab Duo Chat to
troubleshoot failed CI/CD jobs
.
Job configuration issues
A lot of common pipeline issues can be fixed by analyzing the behavior of the
rules
or
only/except
configuration used to
control when jobs are added to a pipeline
.
You shouldn’t use these two configurations in the same pipeline, as they behave differently.
It’s hard to predict how a pipeline runs with this mixed behavior.
rules
is the preferred
choice for controlling jobs, as
only
and
except
are no longer being actively developed.
If your
rules
or
only/except
configuration makes use of
predefined variables
like
CI_PIPELINE_SOURCE
,
CI_MERGE_REQUEST_ID
, you should
verify them
as the first troubleshooting step.
Jobs or pipelines don’t run when expected
The
rules
or
only/except
keywords are what determine whether or not a job is
added to a pipeline. If a pipeline runs, but a job is not added to the pipeline,
it’s usually due to
rules
or
only/except
configuration issues.
If a pipeline does not seem to run at all, with no error message, it may also be
due to
rules
or
only/except
configuration, or the
workflow: rules
keyword.
If you are converting from
only/except
to the
rules
keyword, you should check
the
rules
configuration details
carefully. The behavior
of
only/except
and
rules
is different and can cause unexpected behavior when migrating
between the two.
The
common
if
clauses for
rules
can be very helpful for examples of how to write rules that behave the way you expect.
If a pipeline contains only jobs in the
.pre
or
.post
stages, it does not run.
There must be at least one other job in a different stage.
Unexpected behavior when
.gitlab-ci.yml
file contains a byte order mark (BOM)
A
UTF-8 Byte-Order Mark (BOM)
in
the
.gitlab-ci.yml
file or other included configuration files can lead to incorrect
pipeline behavior. The byte order mark affects parsing of the file, causing some configuration
to be ignored - jobs might be missing, and variables could have the wrong values.
Some text editors could insert a BOM character if configured to do so.
If your pipeline has confusing behavior, you can check for the presence of BOM characters
with a tool capable of displaying them. The pipeline editor cannot display the characters,
so you must use an external tool. See
issue 354026
for more details.
A job with the
changes
keyword runs unexpectedly
A common reason a job is added to a pipeline unexpectedly is because the
changes
keyword always evaluates to true in certain cases. For example,
changes
is always
true in certain pipeline types, including scheduled pipelines and pipelines for tags.
The
changes
keyword is used in combination with
only/except
or
rules
. It’s recommended to only use
changes
with
if
sections in
rules
or
only/except
configuration that ensures the job is only added to
branch pipelines or merge request pipelines.
Two pipelines run at the same time
Two pipelines can run when pushing a commit to a branch that has an open merge request
associated with it. Usually one pipeline is a merge request pipeline, and the other
is a branch pipeline.
This situation is usually caused by the
rules
configuration, and there are several ways to
prevent duplicate pipelines
.
No pipeline or the wrong type of pipeline runs
Before a pipeline can run, GitLab evaluates all the jobs in the configuration and tries
to add them to all available pipeline types. A pipeline does not run if no jobs are added
to it at the end of the evaluation.
If a pipeline did not run, it’s likely that all the jobs had
rules
or
only/except
that
blocked them from being added to the pipeline.
If the wrong pipeline type ran, then the
rules
or
only/except
configuration should
be checked to make sure the jobs are added to the correct pipeline type. For
example, if a merge request pipeline did not run, the jobs may have been added to
a branch pipeline instead.
It’s also possible that your
workflow: rules
configuration
blocked the pipeline, or allowed the wrong pipeline type.
If you are using pull mirroring, you can check the
troubleshooting entry for pull mirroring pipelines
.
Pipeline with many jobs fails to start
A Pipeline that has more jobs than the instance’s defined
CI/CD limits
fails to start.
To reduce the number of jobs in a single pipeline, you can split your
.gitlab-ci.yml
configuration into more independent
parent-child pipelines
.
Pipeline warnings
Pipeline configuration warnings are shown when you:
Validate configuration with the CI Lint tool
.
Manually run a pipeline
.
Job may allow multiple pipelines to run for a single action
warning
When you use
rules
with a
when
clause without an
if
clause, multiple pipelines may run. Usually this occurs when you push a commit to
a branch that has an open merge request associated with it.
To
prevent duplicate pipelines
, use
workflow: rules
or rewrite your rules to control
which pipelines can run.
Pipeline errors
A CI/CD pipeline must run and be successful before merge
message
This message is shown if the
Pipelines must succeed
setting is enabled in the project and a pipeline has not yet run successfully.
This also applies if the pipeline has not been created yet, or if you are waiting
for an external CI service.
If you don’t use pipelines for your project, then you should disable
Pipelines must succeed
so you can accept merge requests.
Checking ability to merge automatically
message
If your merge request is stuck with a
Checking ability to merge automatically
message that does not disappear after a few minutes, you can try one of these workarounds:
Refresh the merge request page.
Close & Re-open the merge request.
Rebase the merge request with the
/rebase
quick action
.
If you have already confirmed the merge request is ready to be merged, you can merge
it with the
/merge
quick action.
This issue is
resolved
in GitLab 15.5.
Checking pipeline status
message
This message displays with a spinning status icon (
spinner
) when the merge request
does not yet have a pipeline associated with the latest commit. This might be because:
GitLab hasn’t finished creating the pipeline yet.
You are using an external CI service and GitLab hasn’t heard back from the service yet.
You are not using CI/CD pipelines in your project.
You are using CI/CD pipelines in your project, but your configuration prevented a pipeline from running on the source branch for your merge request.
The latest pipeline was deleted (this is a
known issue
).
The source branch of the merge request is on a private fork.
After the pipeline is created, the message updates with the pipeline status.
In some of these cases, the message might get stuck with the icon spinning endlessly
if the
Pipelines must succeed
setting is enabled. See
issue 334281
for more details.
Project <group/project> not found or access denied
message
This message is shown if configuration is added with
include
and either:
The configuration refers to a project that can’t be found.
The user that is running the pipeline is unable to access any included projects.
To resolve this, check that:
The path of the project is in the format
my-group/my-project
and does not include
any folders in the repository.
The user running the pipeline is a
member of the projects
that contain the included files. Users must also have the
permission
to run CI/CD jobs in the same projects.
The parsed YAML is too big
message
This message displays when the YAML configuration is too large or nested too deeply.
YAML files with a large number of includes, and thousands of lines overall, are
more likely to hit this memory limit. For example, a YAML file that is 200 kb is
likely to hit the default memory limit.
To reduce the configuration size, you can:
Check the length of the expanded CI/CD configuration in the pipeline editor’s
Full configuration
tab. Look for
duplicated configuration that can be removed or simplified.
Move long or repeated
script
sections into standalone scripts in the project.
Use
parent and child pipelines
to move some
work to jobs in an independent child pipeline.
On GitLab Self-Managed, you can
increase the size limits
.
500
error when editing the
.gitlab-ci.yml
file
A loop of included configuration files can cause a
500
error when editing the
.gitlab-ci.yml
file
with the
web editor
.
Ensure that included configuration files do not create a loop of references to each other.
Failed to pull image
messages
History
Allow access to this project with a CI_JOB_TOKEN
setting
renamed to
Limit access to this project
in GitLab 16.3.
A runner might return a
Failed to pull image
message when trying to pull a container image
in a CI/CD job.
The runner authenticates with a
CI/CD job token
when fetching a container image defined with
image
from another project’s container registry.
If the job token settings prevent access to the other project’s container registry,
the runner returns an error message.
For example:
WARNING: Failed to pull image with policy "always": Error response from daemon: pull access denied for registry.example.com/path/to/project, repository does not exist or may require 'docker login': denied: requested access to the resource is denied
WARNING: Failed to pull image with policy "": image pull failed: rpc error: code = Unknown desc = failed to pull and unpack image "registry.example.com/path/to/project/image:v1.2.3": failed to resolve reference "registry.example.com/path/to/project/image:v1.2.3": pull access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
These errors can happen if the following are both true:
The
Limit access to this project
option is enabled in the private project hosting the image.
The job attempting to fetch the image is running in a project that is not listed in
the private project’s allowlist.
To resolve this issue, add any projects with CI/CD jobs that fetch images from the container
registry to the target project’s
job token allowlist
.
These errors might also happen when trying to use a
project access token
to access images in another project. Project access tokens are scoped to one project,
and therefore cannot access images in other projects. You must use
a different token type
with wider scope.
Random or intermittent
Failed to pull image
errors
You might experience intermittent
Failed to pull image
errors in your CI/CD jobs.
This issue can occur when users have different permissions to access images, combined with how runners cache those images.
Bot users are commonly affected because they often have different permissions than other project members.
For example, your pipeline images might be hosted in a container registry in a different project.
If all users can access both projects, this is not a problem. However, if a user (like a bot user)
cannot access the project hosting the images, they can get
Failed to pull image
errors.
The error becomes intermittent when the runner successfully fetches and caches the image
for a user with permission to access the image. This runner now has the image available
and does not need to access the other project to fetch the image. All users, including users
without access to the other project, can run CI/CD jobs with this image. However, if the runner
has never fetched and cached the image, users without permission to access the image project
get the
Failed to pull image
error.
To resolve this issue, make sure all users that run pipelines, including bot users,
can access the project that hosts the pulled images.
Something went wrong on our end
message or
500
error when running a pipeline
You might receive the following pipeline errors:
A
Something went wrong on our end
message when pushing or creating merge requests.
A
500
error when using the API to trigger a pipeline.
These errors can happen if records of internal IDs become out of sync after a project is imported.
To resolve this, see the
workaround in issue 352382
.
config should be an array of hashes
error message
You might see an error similar to the following when using
!reference
tags
with the
parallel:matrix
keyword
:
This GitLab CI configuration is invalid: jobs:my_job_name:parallel:matrix config should be an array of hashes.
The
parallel:matrix
keyword does not support multiple
!reference
tags at the same time.
Try using
YAML anchors
instead.
Issue 439828
proposes improving
!reference
tag support in
parallel:matrix
.
