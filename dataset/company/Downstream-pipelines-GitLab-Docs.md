# Downstream pipelines | GitLab Docs

Source: https://docs.gitlab.com/ci/pipelines/downstream_pipelines/#use-a-child-pipeline-configuration-file-in-a-different-project

Downstream pipelines | GitLab Docs
Downstream pipelines
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
A downstream pipeline is any GitLab CI/CD pipeline triggered by another pipeline.
Downstream pipelines run independently and concurrently to the upstream pipeline
that triggered them.
A
parent-child pipeline
is a downstream pipeline
triggered in the same project as the first pipeline.
A
multi-project pipeline
is a downstream pipeline triggered
in a different project than the first pipeline.
You can sometimes use parent-child pipelines and multi-project pipelines for similar purposes,
but there are
key differences
.
A pipeline hierarchy can contain up to 1000 downstream pipelines by default.
For more information about this limit and how to change it, see
Limit pipeline hierarchy size
.
Parent-child pipelines
A parent pipeline is a pipeline that triggers a downstream pipeline in the same project.
The downstream pipeline is called a child pipeline.
Child pipelines:
Run under the same project, ref, and commit SHA as the parent pipeline.
Do not directly affect the overall status of the ref the pipeline runs against. For example,
if a pipeline fails for the main branch, it’s common to say that “main is broken”.
The status of child pipelines only affects the status of the ref if the child
pipeline is triggered with
trigger:strategy
.
Are automatically canceled if the pipeline is configured with
interruptible
when a new pipeline is created for the same ref.
Are not displayed in the project’s pipeline list. You can only view child pipelines on
their parent pipeline’s details page.
Nested child pipelines
Parent and child pipelines have a maximum depth of two levels of child pipelines.
A parent pipeline can trigger many child pipelines, and these child pipelines can trigger
their own child pipelines. You cannot trigger another level of child pipelines.
For an overview, see
Nested Dynamic Pipelines
.
Multi-project pipelines
A pipeline in one project can trigger downstream pipelines in another project,
called multi-project pipelines. The user triggering the upstream pipeline must be able to
start pipelines in the downstream project, otherwise
the downstream pipeline fails to start
.
Multi-project pipelines:
Are triggered from another project’s pipeline, but the upstream (triggering) pipeline does
not have much control over the downstream (triggered) pipeline. However, it can
choose the ref of the downstream pipeline, and pass CI/CD variables to it.
Affect the overall status of the ref of the project it runs in, but does not
affect the status of the triggering pipeline’s ref, unless it was triggered with
trigger:strategy
.
Are not automatically canceled in the downstream project when using
interruptible
if a new pipeline runs for the same ref in the upstream pipeline. They can be
automatically canceled if a new pipeline is triggered for the same ref on the downstream project.
Are visible in the downstream project’s pipeline list.
Are independent, so there are no nesting limits.
If you use a public project to trigger downstream pipelines in a private project,
make sure there are no confidentiality problems. The upstream project’s pipelines page
always displays:
The name of the downstream project.
The status of the pipeline.
Trigger a downstream pipeline from a job in the
.gitlab-ci.yml
file
Use the
trigger
keyword in your
.gitlab-ci.yml
file
to create a job that triggers a downstream pipeline. This job is called a trigger job.
For example:
Parent-child pipeline
trigger_job
:
trigger
:
include
:
-
local
:
path/to/child-pipeline.yml
Multi-project pipeline
trigger_job
:
trigger
:
project
:
project-group/my-downstream-project
After the trigger job starts, the initial status of the job is
pending
while GitLab
attempts to create the downstream pipeline. The trigger job shows
passed
if the
downstream pipeline is created successfully, otherwise it shows
failed
. Alternatively,
you can
set the trigger job to show the downstream pipeline’s status
instead.
Use
rules
to control downstream pipeline jobs
Use CI/CD variables or the
rules
keyword to
control job behavior
in downstream pipelines.
When you trigger a downstream pipeline with the
trigger
keyword,
the value of the
$CI_PIPELINE_SOURCE
predefined variable
for all jobs is:
pipeline
for multi-project pipelines.
parent_pipeline
for parent-child pipelines.
For example, to control jobs in multi-project pipelines in a project that also runs
merge request pipelines:
job1
:
rules
:
-
if
:
$CI_PIPELINE_SOURCE == "pipeline"
script
:
echo "This job runs in multi-project pipelines only"
job2
:
rules
:
-
if
:
$CI_PIPELINE_SOURCE == "merge_request_event"
script
:
echo "This job runs in merge request pipelines only"
job3
:
rules
:
-
if
:
$CI_PIPELINE_SOURCE == "pipeline"
-
if
:
$CI_PIPELINE_SOURCE == "merge_request_event"
script
:
echo "This job runs in both multi-project and merge request pipelines"
Use a child pipeline configuration file in a different project
You can use
include:project
in a trigger job
to trigger child pipelines with a configuration file in a different project:
microservice_a
:
trigger
:
include
:
-
project
:
'my-group/my-pipeline-library'
ref
:
'main'
file
:
'/path/to/child-pipeline.yml'
Combine multiple child pipeline configuration files
You can include up to three configuration files when defining a child pipeline. The child pipeline’s
configuration is composed of all configuration files merged together:
microservice_a
:
trigger
:
include
:
-
local
:
path/to/microservice_a.yml
-
template
:
Jobs/SAST.gitlab-ci.yml
-
project
:
'my-group/my-pipeline-library'
ref
:
'main'
file
:
'/path/to/child-pipeline.yml'
Dynamic child pipelines
You can trigger a child pipeline from a YAML file generated in a job, instead of a
static file saved in your project. This technique can be very powerful for generating pipelines
targeting content that changed or to build a matrix of targets and architectures.
The artifact containing the generated YAML file must be within
instance limits
.
For an overview, see
Create child pipelines using dynamically generated configurations
.
For an example project that generates a dynamic child pipeline, see
Dynamic Child Pipelines with Jsonnet
.
This project shows how to use a data templating language to generate your
.gitlab-ci.yml
at runtime.
You can use a similar process for other templating languages like
Dhall
or
ytt
.
Trigger a dynamic child pipeline
To trigger a child pipeline from a dynamically generated configuration file:
Generate the configuration file in a job and save it as an
artifact
:
generate-config
:
stage
:
build
script
:
generate-ci-config > generated-config.yml
artifacts
:
paths
:
-
generated-config.yml
Configure the trigger job to run after the job that generated the configuration file.
Set
include: artifact
to the generated artifact, and set
include: job
to
the job that created the artifact:
child-pipeline
:
stage
:
test
trigger
:
include
:
-
artifact
:
generated-config.yml
job
:
generate-config
In this example, GitLab retrieves
generated-config.yml
and triggers a child pipeline
with the CI/CD configuration in that file.
The artifact path is parsed by GitLab, not the runner, so the path must match the
syntax for the OS running GitLab. If GitLab is running on Linux but using a Windows
runner for testing, the path separator for the trigger job is
/
. Other CI/CD
configuration for jobs that use the Windows runner, like scripts, use
\
.
You cannot use CI/CD variables in an
include
section in a dynamic child pipeline’s configuration.
Run child pipelines with merge request pipelines
Pipelines, including child pipelines, run as branch pipelines by default when not using
rules
or
workflow:rules
.
To configure child pipelines to run when triggered from a
merge request (parent) pipeline
, use
rules
or
workflow:rules
.
For example, using
rules
:
Set the parent pipeline’s trigger job to run on merge requests:
trigger-child-pipeline-job
:
trigger
:
include
:
path/to/child-pipeline-configuration.yml
rules
:
-
if
:
$CI_PIPELINE_SOURCE == "merge_request_event"
Use
rules
to configure the child pipeline jobs to run when triggered by the parent pipeline:
job1
:
script
:
echo "This child pipeline job runs any time the parent pipeline triggers it."
rules
:
-
if
:
$CI_PIPELINE_SOURCE == "parent_pipeline"
job2
:
script
:
echo "This child pipeline job runs only when the parent pipeline is a merge request pipeline"
rules
:
-
if
:
$CI_MERGE_REQUEST_ID
In child pipelines,
$CI_PIPELINE_SOURCE
always has a value of
parent_pipeline
, so:
You can use
if: $CI_PIPELINE_SOURCE == "parent_pipeline"
to ensure child pipeline jobs always run.
You can’t use
if: $CI_PIPELINE_SOURCE == "merge_request_event"
to configure child pipeline
jobs to run for merge request pipelines. Instead, use
if: $CI_MERGE_REQUEST_ID
to set child pipeline jobs to run only when the parent pipeline is a merge request pipeline. The parent pipeline’s
CI_MERGE_REQUEST_*
predefined variables
are passed to the child pipeline jobs.
Specify a branch for multi-project pipelines
You can specify the branch to use when triggering a multi-project pipeline. GitLab uses
the commit on the head of the branch to create the downstream pipeline. For example:
staging
:
stage
:
deploy
trigger
:
project
:
my/deployment
branch
:
stable-11-2
Use:
The
project
keyword to specify the full path to the downstream project.
In
GitLab 15.3 and later
,
you can use
variable expansion
.
The
branch
keyword to specify the name of a branch or
tag
in the project specified by
project
. You can use variable expansion.
Trigger a multi-project pipeline by using the API
You can use the
CI/CD job token (
CI_JOB_TOKEN
)
with the
pipeline trigger API endpoint
to trigger multi-project pipelines from inside a CI/CD job. GitLab sets pipelines triggered
with a job token as downstream pipelines of the pipeline that contains the job that
made the API call.
For example:
trigger_pipeline
:
stage
:
deploy
script
:
-
curl --request POST --form "token=$CI_JOB_TOKEN" --form ref=main "https://gitlab.example.com/api/v4/projects/9/trigger/pipeline"
rules
:
-
if
:
$CI_COMMIT_TAG
environment
:
production
View a downstream pipeline
In the
pipeline details page
, downstream pipelines display
as a list of cards on the right of the graph. From this view, you can:
Select a trigger job to see the triggered downstream pipeline’s jobs.
Select
Expand jobs
chevron-lg-right
on a pipeline card to expand the view
with the downstream pipeline’s jobs. You can view one downstream pipeline at a time.
Hover over a pipeline card to have the job that triggered the downstream pipeline highlighted.
Retry failed and canceled jobs in a downstream pipeline
History
Retry from graph view
introduced
in GitLab 15.0
with a flag
named
downstream_retry_action
. Disabled by default.
Retry from graph view
generally available and feature flag removed
in GitLab 15.1.
To retry failed and canceled jobs, select
Retry
(
retry
):
From the downstream pipeline’s details page.
On the pipeline’s card in the pipeline graph view.
Recreate a downstream pipeline
History
Retry trigger job from graph view
introduced
in GitLab 15.10
with a flag
named
ci_recreate_downstream_pipeline
. Disabled by default.
Generally available
in GitLab 15.11. Feature flag
ci_recreate_downstream_pipeline
removed.
You can recreate a downstream pipeline by retrying its corresponding trigger job. The newly created downstream pipeline replaces the current downstream pipeline in the pipeline graph.
To recreate a downstream pipeline:
Select
Run again
(
retry
) on the trigger job’s card in the pipeline graph view.
Cancel a downstream pipeline
History
Retry from graph view
introduced
in GitLab 15.0
with a flag
named
downstream_retry_action
. Disabled by default.
Retry from graph view
generally available and feature flag removed
in GitLab 15.1.
To cancel a downstream pipeline that is still running, select
Cancel
(
cancel
):
From the downstream pipeline’s details page.
On the pipeline’s card in the pipeline graph view.
Auto-cancel the parent pipeline from a downstream pipeline
You can configure a child pipeline to
auto-cancel
as soon as one of its jobs fail.
The parent pipeline only auto-cancels when a job in the child pipeline fails if:
The parent pipeline is also set up to auto-cancel on job failure.
The trigger job is configured with
strategy: mirror
.
For example:
Content of
.gitlab-ci.yml
:
workflow
:
auto_cancel
:
on_job_failure
:
all
trigger_job
:
trigger
:
include
:
child-pipeline.yml
strategy
:
mirror
job3
:
script
:
-
sleep 120
Content of
child-pipeline.yml
# Contents of child-pipeline.yml
workflow
:
auto_cancel
:
on_job_failure
:
all
job1
:
script
:
sleep 60
job2
:
script
:
-
sleep 30
-
exit 1
In this example:
The parent pipeline triggers the child pipeline and
job3
at the same time
job2
from the child pipeline fails and the child pipeline is canceled, stopping
job1
as well
The child pipeline has been canceled so the parent pipeline is auto-canceled
Mirror the status of a downstream pipeline in the trigger job
You can mirror the status of the downstream pipeline in the trigger job
by using
strategy: mirror
:
Parent-child pipeline
trigger_job
:
trigger
:
include
:
-
local
:
path/to/child-pipeline.yml
strategy
:
mirror
Multi-project pipeline
trigger_job
:
trigger
:
project
:
my/project
strategy
:
mirror
View multi-project pipelines in pipeline graphs
History
Moved
from GitLab Premium to GitLab Free in 16.8.
After you trigger a multi-project pipeline, the downstream pipeline displays
to the right of the
pipeline graph
.
In
pipeline mini graphs
, the downstream pipeline
displays to the right of the mini graph.
View child pipeline reports in merge requests
History
Introduced
in GitLab 18.6.
You can view reports from child pipelines in merge request widgets. This provides a
unified view of test results and quality checks across your pipeline hierarchy
without manually navigating through multiple pipelines to identify failures.
The following report types from child pipelines are supported:
Unit test reports (Junit)
Code quality reports
Terraform reports
Metric reports
Test results from child pipelines also appear in the parent pipeline’s
Tests
tab.
To ensure complete report information in merge request widgets,
child pipelines that generate
artifacts reports
should use
strategy: depend
or
strategy: mirror
.
For example:
test-backend
:
trigger
:
include
:
backend-tests.yml
strategy
:
depend
test-frontend
:
trigger
:
include
:
frontend-tests.yml
strategy
:
depend
Fetch artifacts from an upstream pipeline
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Parent-child pipeline
Use
needs:pipeline:job
to fetch artifacts from an
upstream pipeline:
In the upstream pipeline, save the artifacts in a job with the
artifacts
keyword, then trigger the downstream pipeline with a trigger job:
build_artifacts
:
stage
:
build
script
:
-
echo "This is a test artifact!" >> artifact.txt
artifacts
:
paths
:
-
artifact.txt
deploy
:
stage
:
deploy
trigger
:
include
:
-
local
:
path/to/child-pipeline.yml
variables
:
PARENT_PIPELINE_ID
:
$CI_PIPELINE_ID
Use
needs:pipeline:job
in a job in the downstream pipeline to fetch the artifacts.
test
:
stage
:
test
script
:
-
cat artifact.txt
needs
:
-
pipeline
:
$PARENT_PIPELINE_ID
job
:
build_artifacts
Set
job
to the job in the upstream pipeline that created the artifacts.
Multi-project pipeline
Use
needs:project
to fetch artifacts from an
upstream pipeline:
In GitLab 15.9 and later,
add the downstream project to the job token scope allowlist
of the upstream project.
In the upstream pipeline, save the artifacts in a job with the
artifacts
keyword, then trigger the downstream pipeline with a trigger job:
build_artifacts
:
stage
:
build
script
:
-
echo "This is a test artifact!" >> artifact.txt
artifacts
:
paths
:
-
artifact.txt
deploy
:
stage
:
deploy
trigger
:
my/downstream_project
# Path to the project to trigger a pipeline in
Use
needs:project
in a job in the downstream pipeline to fetch the artifacts.
test
:
stage
:
test
script
:
-
cat artifact.txt
needs
:
-
project
:
my/upstream_project
job
:
build_artifacts
ref
:
main
artifacts
:
true
Set:
job
to the job in the upstream pipeline that created the artifacts.
ref
to the branch.
artifacts
to
true
.
Fetch artifacts from an upstream merge request pipeline
When you use
needs:project
to
pass artifacts to a downstream pipeline
,
the
ref
value is usually a branch name, like
main
or
development
.
For
merge request pipelines
, the
ref
value is in the form of
refs/merge-requests/<id>/head
,
where
id
is the merge request ID. You can retrieve this ref with the
CI_MERGE_REQUEST_REF_PATH
CI/CD variable. Do not use a branch name as the
ref
with merge request pipelines,
because the downstream pipeline attempts to fetch artifacts from the latest branch pipeline.
To fetch the artifacts from the upstream
merge request
pipeline instead of the
branch
pipeline,
pass
CI_MERGE_REQUEST_REF_PATH
to the downstream pipeline using
variable inheritance
:
In GitLab 15.9 and later,
add the downstream project to the job token scope allowlist
of the upstream project.
In a job in the upstream pipeline, save the artifacts using the
artifacts
keyword.
In the job that triggers the downstream pipeline, pass the
$CI_MERGE_REQUEST_REF_PATH
variable:
build_artifacts
:
rules
:
-
if
:
$CI_PIPELINE_SOURCE == 'merge_request_event'
stage
:
build
script
:
-
echo "This is a test artifact!" >> artifact.txt
artifacts
:
paths
:
-
artifact.txt
upstream_job
:
rules
:
-
if
:
$CI_PIPELINE_SOURCE == 'merge_request_event'
variables
:
UPSTREAM_REF
:
$CI_MERGE_REQUEST_REF_PATH
trigger
:
project
:
my/downstream_project
branch
:
my-branch
In a job in the downstream pipeline, fetch the artifacts from the upstream pipeline
by using
needs:project
and the passed variable as the
ref
:
test
:
stage
:
test
script
:
-
cat artifact.txt
needs
:
-
project
:
my/upstream_project
job
:
build_artifacts
ref
:
$UPSTREAM_REF
artifacts
:
true
You can use this method to fetch artifacts from upstream merge request pipelines,
but not from
merged results pipelines
.
Pass inputs to a downstream pipeline
You can use the
inputs
keyword to pass input values to downstream pipelines.
Inputs provide advantages over variables including type checking, validation through options,
descriptions, and default values.
First, define input parameters in the target configuration file using
spec:inputs
:
# Target pipeline configuration
spec
:
inputs
:
environment
:
description
:
"Deployment environment"
options
:
[
staging, production]
version
:
type
:
string
description
:
"Application version"
Then provide values when triggering the pipeline:
Parent-child pipeline
staging
:
trigger
:
include
:
-
local
:
path/to/child-pipeline.yml
inputs
:
environment
:
staging
version
:
"1.0.0"
Multi-project pipeline
staging
:
trigger
:
project
:
my-group/my-deployment-project
inputs
:
environment
:
staging
version
:
"1.0.0"
Pass CI/CD variables to a downstream pipeline
You can pass
CI/CD variables
to a downstream pipeline with
a few different methods, based on where the variable is created or defined.
Pass YAML-defined CI/CD variables
Inputs are recommended for pipeline configuration instead of variables as they offer improved security and flexibility.
You can use the
variables
keyword to pass CI/CD variables to a downstream pipeline.
These variables are pipeline variables for
variable precedence
.
For example:
Parent-child pipeline
variables
:
VERSION
:
"1.0.0"
staging
:
variables
:
ENVIRONMENT
:
staging
stage
:
deploy
trigger
:
include
:
-
local
:
path/to/child-pipeline.yml
Multi-project pipeline
variables
:
VERSION
:
"1.0.0"
staging
:
variables
:
ENVIRONMENT
:
staging
stage
:
deploy
trigger
:
my-group/my-deployment-project
The
ENVIRONMENT
variable is available in every job defined in the downstream pipeline.
The
VERSION
default variable is also available in the downstream pipeline, because
all jobs in a pipeline, including trigger jobs, inherit
default
variables
.
Prevent default variables from being passed
You can stop default CI/CD variables from reaching the downstream pipeline with
inherit:variables
. You can list specific variables to inherit,
or block all default variables.
For example:
Parent-child pipeline
variables
:
DEFAULT_VAR
:
value
trigger-job
:
inherit
:
variables
:
false
variables
:
JOB_VAR
:
value
trigger
:
include
:
-
local
:
path/to/child-pipeline.yml
Multi-project pipeline
variables
:
DEFAULT_VAR
:
value
trigger-job
:
inherit
:
variables
:
false
variables
:
JOB_VAR
:
value
trigger
:
my-group/my-project
The
DEFAULT_VAR
variable is not available in the triggered pipeline, but
JOB_VAR
is available.
Pass a predefined variable
To pass information about the upstream pipeline using
predefined CI/CD variables
use interpolation. Save the predefined variable as a new job variable in the trigger
job, which is passed to the downstream pipeline. For example:
Parent-child pipeline
trigger-job
:
variables
:
PARENT_BRANCH
:
$CI_COMMIT_REF_NAME
trigger
:
include
:
-
local
:
path/to/child-pipeline.yml
Multi-project pipeline
trigger-job
:
variables
:
UPSTREAM_BRANCH
:
$CI_COMMIT_REF_NAME
trigger
:
my-group/my-project
The
UPSTREAM_BRANCH
variable, which contains the value of the upstream pipeline’s
$CI_COMMIT_REF_NAME
predefined CI/CD variable, is available in the downstream pipeline.
Do not use this method to pass
masked variables
to a multi-project pipeline. The CI/CD masking configuration is not passed to the
downstream pipeline and the variable could be unmasked in job logs in the downstream project.
You cannot use this method to forward
job-only variables
to a downstream pipeline, as they are not available in trigger jobs.
Upstream pipelines take precedence over downstream ones. If there are two
variables with the same name defined in both upstream and downstream projects,
the ones defined in the upstream project take precedence.
Pass dotenv variables created in a job
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
You can pass variables to a downstream pipeline with
dotenv
variable inheritance
.
For example, in a
multi-project pipeline
:
Save the variables in a
.env
file.
Save the
.env
file as a
dotenv
report.
Trigger the downstream pipeline.
build_vars
:
stage
:
build
script
:
-
echo "BUILD_VERSION=hello" >> build.env
artifacts
:
reports
:
dotenv
:
build.env
deploy
:
stage
:
deploy
trigger
:
my/downstream_project
Set the
test
job in the downstream pipeline to inherit the variables from the
build_vars
job in the upstream project with
needs
. The
test
job inherits the variables in the
dotenv
report and it can access
BUILD_VERSION
in the script:
test
:
stage
:
test
script
:
-
echo $BUILD_VERSION
needs
:
-
project
:
my/upstream_project
job
:
build_vars
ref
:
master
artifacts
:
true
Control what type of variables to forward to downstream pipelines
Use the
trigger:forward
keyword
to specify
what type of variables to forward to the downstream pipeline. Forwarded variables
are considered trigger variables, which have the
highest precedence
.
Downstream pipelines for deployments
History
Introduced
in GitLab 16.4.
You can use the
environment
keyword with
trigger
.
You might want to use
environment
from a trigger job if your deployment and application projects are separately managed.
deploy
:
trigger
:
project
:
project-group/my-downstream-project
environment
:
production
A downstream pipeline can provision infrastructure, deploy to a designated environment, and return the deployment status
to the upstream project.
You can
view the environment and deployment
from the upstream project.
Advanced example
This example configuration has the following behaviors:
The upstream project dynamically composes an environment name based on a branch name.
The upstream project passes the context of the deployment to the downstream project with
UPSTREAM_*
variables.
The
.gitlab-ci.yml
in an upstream project:
stages
:
-
deploy
-
cleanup
.downstream-deployment-pipeline
:
variables
:
UPSTREAM_PROJECT_ID
:
$CI_PROJECT_ID
UPSTREAM_ENVIRONMENT_NAME
:
$CI_ENVIRONMENT_NAME
UPSTREAM_ENVIRONMENT_ACTION
:
$CI_ENVIRONMENT_ACTION
trigger
:
project
:
project-group/deployment-project
branch
:
main
strategy
:
mirror
deploy-review
:
stage
:
deploy
extends
:
.downstream-deployment-pipeline
environment
:
name
:
review/$CI_COMMIT_REF_SLUG
on_stop
:
stop-review
stop-review
:
stage
:
cleanup
extends
:
.downstream-deployment-pipeline
environment
:
name
:
review/$CI_COMMIT_REF_SLUG
action
:
stop
when
:
manual
The
.gitlab-ci.yml
in a downstream project:
deploy
:
script
:
echo "Deploy to ${UPSTREAM_ENVIRONMENT_NAME} for ${UPSTREAM_PROJECT_ID}"
rules
:
-
if
:
$CI_PIPELINE_SOURCE == "pipeline" && $UPSTREAM_ENVIRONMENT_ACTION == "start"
stop
:
script
:
echo "Stop ${UPSTREAM_ENVIRONMENT_NAME} for ${UPSTREAM_PROJECT_ID}"
rules
:
-
if
:
$CI_PIPELINE_SOURCE == "pipeline" && $UPSTREAM_ENVIRONMENT_ACTION == "stop"
