# Where variables can be used | GitLab Docs

Source: https://docs.gitlab.com/ci/variables/where_variables_can_be_used/#nested-variable-expansion

Where variables can be used | GitLab Docs
Where variables can be used
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
As it’s described in the
CI/CD variables
documentation, you can
define many different variables. Some of them can be used for all GitLab CI/CD
features, but some of them are more or less limited.
This document describes where and how the different types of variables can be used.
Variables usage
There are two places defined variables can be used. On the:
GitLab side, in the
.gitlab-ci.yml
file.
The GitLab Runner side, in
config.toml
.
.gitlab-ci.yml
file
History
Support for
CI_ENVIRONMENT_*
variables except
CI_ENVIRONMENT_SLUG
introduced
in GitLab 16.4.
Definition
Can be expanded?
Expansion place
Description
after_script
yes
Script execution shell
The variable expansion is made by the
execution shell environment
.
artifacts:name
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
artifacts:paths
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
artifacts:exclude
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
before_script
yes
Script execution shell
The variable expansion is made by the
execution shell environment
cache:key
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
cache:paths
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
cache:policy
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
environment:name
yes
GitLab
Similar to
environment:url
, but the variables expansion doesn’t support the following:
-
CI_ENVIRONMENT_*
variables.
-
Persisted variables
.
environment:url
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
Supported are all variables defined for a job (project/group variables, variables from
.gitlab-ci.yml
, variables from triggers, variables from pipeline schedules).
Not supported are variables defined in the GitLab Runner
config.toml
and variables created in the job’s
script
.
environment:deployment_tier
yes
GitLab
Similar to
environment:url
, but the variables expansion doesn’t support the following:
-
CI_ENVIRONMENT_*
variables.
-
Persisted variables
.
environment:auto_stop_in
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
The value of the variable being substituted should be a period of time in a human readable natural language form. See
supported values
for more information.
environment:kubernetes:agent
yes
GitLab
Similar to
environment:url
, but the variables expansion does not support the following:
-
CI_ENVIRONMENT_*
variables.
-
Persisted variables
.
environment:kubernetes:namespace
yes
GitLab
Similar to
environment:url
, but the variables expansion does not support the following:
-
CI_ENVIRONMENT_*
variables.
-
Persisted variables
.
id_tokens:aud
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab. Variable expansion
introduced
in GitLab 16.1.
image
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
include
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
See
Use variables with include
for more information on supported variables.
resource_group
yes
GitLab
Similar to
environment:url
, but the variables expansion doesn’t support the following:
-
CI_ENVIRONMENT_URL
-
Persisted variables
.
rules:changes
no
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
rules:changes:compare_to
no
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
rules:exists
no
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
rules:if
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
script
yes
Script execution shell
The variable expansion is made by the
execution shell environment
.
services:name
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
services
yes
Runner
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
.
tags
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
trigger
and
trigger:project
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab. Variable expansion for
trigger:project
introduced
in GitLab 15.3.
variables
yes
GitLab/Runner
The variable expansion is first made by the
internal variable expansion mechanism
in GitLab, and then any unrecognized or unavailable variables are expanded by GitLab Runner’s
internal variable expansion mechanism
.
workflow:name
yes
GitLab
The variable expansion is made by the
internal variable expansion mechanism
in GitLab.
Supported are all variables available in
workflow
:
- Project/Group variables.
- Global
variables
and
workflow:rules:variables
(when matching the rule).
- Variables inherited from parent pipelines.
- Variables from triggers.
- Variables from pipeline schedules.
Not supported are variables defined in the GitLab Runner
config.toml
, variables defined in jobs, or
Persisted variables
.
config.toml
file
Definition
Can be expanded?
Description
runners.environment
yes
The variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
runners.kubernetes.pod_labels
yes
The Variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
runners.kubernetes.pod_annotations
yes
The Variable expansion is made by GitLab Runner’s
internal variable expansion mechanism
You can read more about
config.toml
in the
GitLab Runner docs
.
Expansion mechanisms
There are three expansion mechanisms:
GitLab
GitLab Runner
Execution shell environment
GitLab internal variable expansion mechanism
The expanded part needs to be in a form of
$variable
, or
${variable}
or
%variable%
.
Each form is handled in the same way, no matter which OS/shell handles the job,
because the expansion is done in GitLab before any runner gets the job.
Nested variable expansion
GitLab expands job variable values recursively before sending them to the runner. For example, in the following scenario:
-
BUILD_ROOT_DIR
:
'${CI_BUILDS_DIR}'
-
OUT_PATH
:
'${BUILD_ROOT_DIR}/out'
-
PACKAGE_PATH
:
'${OUT_PATH}/pkg'
The runner receives a valid, fully-formed path. For example, if
${CI_BUILDS_DIR}
is
/output
, then
PACKAGE_PATH
would be
/output/out/pkg
.
References to unavailable variables are left intact. In this case, the runner
attempts to expand the variable value
at runtime.
For example, a variable like
CI_BUILDS_DIR
is known by the runner only at runtime.
GitLab Runner internal variable expansion mechanism
Supported: project/group variables,
.gitlab-ci.yml
variables,
config.toml
variables, and
variables from triggers, pipeline schedules, and manual pipelines.
Not supported: variables defined inside of scripts (for example,
export MY_VARIABLE="test"
).
The runner uses Go’s
os.Expand()
method for variable expansion. It means that it handles
only variables defined as
$variable
and
${variable}
. What’s also important, is that
the expansion is done only once, so nested variables may or may not work, depending on the
ordering of variables definitions, and whether
nested variable expansion
is enabled in GitLab.
For artifacts and cache uploads, the runner uses
mvdan.cc/sh/v3/expand
for variable
expansion instead of Go’s
os.Expand()
because
mvdan.cc/sh/v3/expand
supports
parameter expansion
.
Execution shell environment
This is an expansion phase that takes place during the
script
execution.
Its behavior depends on the shell used (
bash
,
sh
,
cmd
, PowerShell). For example, if the job’s
script
contains a line
echo $MY_VARIABLE-${MY_VARIABLE_2}
, it should be properly handled
by bash/sh (leaving empty strings or some values depending whether the variables were
defined or not), but don’t work with Windows’
cmd
or PowerShell, because these shells
use a different variables syntax.
Supported:
The
script
may use all available variables that are default for the shell (for example,
$PATH
which
should be present in all bash/sh shells) and all variables defined by GitLab CI/CD (project/group variables,
.gitlab-ci.yml
variables,
config.toml
variables, and variables from triggers and pipeline schedules).
The
script
may also use all variables defined in the lines before. So, for example, if you define
a variable
export MY_VARIABLE="test"
:
In
before_script
, it works in the subsequent lines of
before_script
and
all lines of the related
script
.
In
script
, it works in the subsequent lines of
script
.
In
after_script
, it works in subsequent lines of
after_script
.
In the case of
after_script
scripts, they can:
Only use variables defined before the script within the same
after_script
section.
Not use variables defined in
before_script
and
script
.
These restrictions exist because
after_script
scripts are executed in a
separated shell context
.
Persisted variables
Some predefined variables are called persisted. Persisted variables are:
Supported for definitions where the
expansion place
is:
Runner.
Script execution shell.
Not supported:
For definitions where the
expansion place
is GitLab.
In
rules
variables expressions
.
Pipeline trigger jobs
cannot use job-level persisted variables,
but can use pipeline-level persisted variables.
Some of the persisted variables contain tokens and cannot be used by some definitions
due to security reasons.
Pipeline-level persisted variables:
CI_PIPELINE_ID
CI_PIPELINE_URL
Job-level persisted variables:
CI_DEPLOY_PASSWORD
CI_DEPLOY_USER
CI_JOB_ID
CI_JOB_STARTED_AT
CI_JOB_TOKEN
CI_JOB_URL
CI_PIPELINE_CREATED_AT
CI_REGISTRY_PASSWORD
CI_REGISTRY_USER
CI_REPOSITORY_URL
Variables with an environment scope
Variables defined with an environment scope are supported. Given that
there is a variable
$STAGING_SECRET
defined in a scope of
review/staging/*
, the following job that is using dynamic environments
is created, based on the matching variable expression:
my-job
:
stage
:
staging
environment
:
name
:
review/$CI_JOB_STAGE/deploy
script
:
-
'deploy staging'
rules
:
-
if
:
$STAGING_SECRET == 'something'
