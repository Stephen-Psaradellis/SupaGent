# Configuring runners | GitLab Docs

Source: https://docs.gitlab.com/ci/runners/configure_runners/#set-the-maximum-job-timeout

Configuring runners | GitLab Docs
Configuring runners
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
This document describes how to configure runners in the GitLab UI.
If you need to configure runners on the machine where you installed GitLab Runner, see
the GitLab Runner documentation
.
Set the maximum job timeout
You can specify a maximum job timeout for each runner to prevent projects
with longer job timeouts from using the runner. The maximum job timeout is
used if it is shorter than the job timeout defined in the project.
To set a runner’s maximum timeout, set the
maximum_timeout
parameter in the REST API endpoint
PUT /runners/:id
.
For an instance runner
Prerequisites:
You must be an administrator.
You can override the job timeout for instance runners on GitLab Self-Managed.
On GitLab.com, you cannot override the job timeout for GitLab hosted instance runners and must use the
project defined timeout
instead.
To set the maximum job timeout:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
CI/CD > Runners
.
To the right of the runner, you want to edit, select
Edit
(
pencil
).
In the
Maximum job timeout
field, enter a value in seconds. The minimum value is 600 seconds (10 minutes).
Select
Save changes
.
For a group runner
Prerequisites:
You must have the Owner role for the group.
To set the maximum job timeout:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Runners
.
To the right of the runner you want to edit, select
Edit
(
pencil
).
In the
Maximum job timeout
field, enter a value in seconds. The minimum value is 600 seconds (10 minutes).
Select
Save changes
.
For a project runner
Prerequisites:
You must have the Owner role for the project.
To set the maximum job timeout:
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
Runners
.
To the right of the runner you want to edit, select
Edit
(
pencil
).
In the
Maximum job timeout
field, enter a value in seconds. The minimum value is 600 seconds (10 minutes). If not defined, the
job timeout for the project
is used instead.
Select
Save changes
.
How maximum job timeout works
Example 1 - Runner timeout bigger than project timeout
You set the
maximum_timeout
parameter for a runner to 24 hours.
You set the
Maximum job timeout
for a project to
2 hours
.
You start a job.
The job, if running longer, times out after
2 hours
.
Example 2 - Runner timeout not configured
You remove the
maximum_timeout
parameter configuration from a runner.
You set the
Maximum job timeout
for a project to
2 hours
.
You start a job.
The job, if running longer, times out after
2 hours
.
Example 3 - Runner timeout smaller than project timeout
You set the
maximum_timeout
parameter for a runner to
30 minutes
.
You set the
Maximum job timeout
for a project to 2 hours.
You start a job.
The job, if running longer, times out after
30 minutes
.
Set
script
and
after_script
timeouts
History
Introduced
in GitLab Runner 16.4.
To control the amount of time
script
and
after_script
runs before it terminates, specify a timeout value in the
.gitlab-ci.yml
file.
For example, you can specify a timeout to terminate a long-running
script
early. This ensures artifacts and caches can still be uploaded
before the
job timeout
is exceeded.
The timeout values for
script
and
after_script
must be less than the job timeout.
To set a timeout for
script
, use the job variable
RUNNER_SCRIPT_TIMEOUT
.
To set a timeout for
after_script
, and override the default of 5 minutes, use the job variable
RUNNER_AFTER_SCRIPT_TIMEOUT
.
Both of these variables accept
Go’s duration format
(for example,
40s
,
1h20m
,
2h
4h30m30s
).
For example:
job-with-script-timeouts
:
variables
:
RUNNER_SCRIPT_TIMEOUT
:
15m
RUNNER_AFTER_SCRIPT_TIMEOUT
:
10m
script
:
-
"I am allowed to run for min(15m, remaining job timeout)."
after_script
:
-
"I am allowed to run for min(10m, remaining job timeout)."
job-artifact-upload-on-timeout
:
timeout
:
1h
# set job timeout to 1 hour
variables
:
RUNNER_SCRIPT_TIMEOUT
:
50m
# only allow script to run for 50 minutes
script
:
-
long-running-process > output.txt
# will be terminated after 50m
artifacts
:
# artifacts will have roughly ~10m to upload
paths
:
-
output.txt
when
:
on_failure
# on_failure because script termination after a timeout is treated as a failure
Ensuring
after_script
execution
For
after_script
to run successfully, the total of
RUNNER_SCRIPT_TIMEOUT
+
RUNNER_AFTER_SCRIPT_TIMEOUT
must not exceed the job’s configured timeout.
The following example shows how to configure timeouts to ensure
after_script
runs even when the main script times out:
job-with-script-timeouts
:
timeout
:
5m
variables
:
RUNNER_SCRIPT_TIMEOUT
:
1m
RUNNER_AFTER_SCRIPT_TIMEOUT
:
1m
script
:
-
echo "Starting build..."
-
sleep 120
# Wait 2 minutes to trigger timeout. Script aborts after 1 minute due to RUNNER_SCRIPT_TIMEOUT.
-
echo "Build finished."
after_script
:
-
echo "Starting Clean-up..."
-
sleep 15
# Wait just a few seconds. Runs successfully because it's within RUNNER_AFTER_SCRIPT_TIMEOUT.
-
echo "Clean-up finished."
The
script
is canceled by
RUNNER_SCRIPT_TIMEOUT
, but the
after_script
runs successfully because it takes 15 seconds,
which is less than both
RUNNER_AFTER_SCRIPT_TIMEOUT
and the job’s
timeout
value.
Protecting sensitive information
The security risks are greater when using instance runners as they are available by default to all groups and projects in a GitLab instance.
The runner executor and file system configuration affects security. Users with access to the runner host environment can view the code that runner executed and the runner authentication.
For example, users with access to the runner authentication token can clone
a runner and submit false jobs in a vector attack. For more information, see
Security Considerations
.
Configuring long polling
To reduce job queueing times and load on your GitLab server, configure
long polling
.
Using instance runners in forked projects
When a project is forked, the job settings related to jobs are copied. If you have instance runners
configured for a project and a user forks that project, the instance runners serve jobs of this project.
Due to a
known issue
, if the runner settings
of the forked project does not match the new project namespace, the following message displays:
An error occurred while forking the project. Please try again.
.
To work around this issue, ensure that the instance runner settings are consistent in the forked project and the new namespace.
If instance runners are
enabled
on the forked project, then this should also be
enabled
on the new namespace.
If instance runners are
disabled
on the forked project, then this should also be
disabled
on the new namespace.
Reset the runner registration token for a project (deprecated)
The option to pass runner registration tokens and support for certain configuration arguments is considered legacy
and is not recommended.
Use the
runner creation workflow
to generate an authentication token to register runners. This process provides full
traceability of runner ownership and enhances your runner fleet’s security.
For more information, see
Migrating to the new runner registration workflow
.
If you think that a registration token for a project was revealed, you should
reset it. A registration token can be used to register another runner for the project.
That new runner may then be used to obtain the values of secret variables or to clone project code.
To reset the registration token:
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
Runners
.
To the right of
New project runner
, select the vertical ellipsis (
ellipsis_v
).
Select
Reset registration token
.
Select
Reset token
.
After you reset the registration token, it is no longer valid and does not register
any new runners to the project. You should also update the registration token in tools
you use to provision and register new values.
Authentication token security
History
Introduced
in GitLab 15.3
with a flag
named
enforce_runner_token_expires_at
. Disabled by default.
Generally available
in GitLab 15.5. Feature flag
enforce_runner_token_expires_at
removed.
Each runner uses a
runner authentication token
to connect to and authenticate with a GitLab instance.
To help prevent the token from being compromised, you can have the
token rotate automatically at specified intervals. When the tokens are rotated,
they are updated for each runner, regardless of the runner’s status (
online
or
offline
).
No manual intervention should be required, and no running jobs should be affected.
For more information about token rotation, see
Runner authentication token does not update when rotated
.
If you need to manually update the runner authentication token, you can run a
command to
reset the token
.
Reset the runner configuration authentication token
If a runner’s authentication token is exposed, an attacker could use it to
clone the runner
.
To reset the runner configuration authentication token:
Delete the runner:
Delete an instance runner
.
Delete a group runner
.
Delete a project runner
.
Create a new runner so that it is assigned a new runner authentication token:
Create an instance runner
.
Create a group runner
.
Create a project runner
.
Optional. To verify that the previous runner authentication token has been revoked, use the
Runners API
.
To reset runner configuration authentication tokens, you can also use the
Runners API
.
Automatically rotate runner authentication tokens
You can specify an interval to rotate runner authentication tokens.
Regularly rotating runner authentication tokens helps minimize the risk of unauthorized access to your GitLab instance through compromised tokens.
Prerequisites:
Runners must use
GitLab Runner 15.3 or later
.
You must be an administrator.
To automatically rotate runner authentication tokens:
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
Continuous Integration and Deployment
.
Set a
Runners expiration
time for runners, leave empty for no expiration.
Select
Save changes
.
Before the interval expires, runners automatically request a new runner authentication token.
For more information about token rotation, see
Runner authentication token does not update when rotated
.
Prevent runners from revealing sensitive information
To ensure runners don’t reveal sensitive information, you can configure them to only run jobs
on
protected branches
, or jobs that have
protected tags
.
Runners configured to run jobs on protected branches can
optionally run jobs in merge request pipelines
.
For an instance runner
Prerequisites:
You must be an administrator.
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
CI/CD > Runners
.
To the right of the runner you want to protect, select
Edit
(
pencil
).
Select the
Protected
checkbox.
Select
Save changes
.
For a group runner
Prerequisites:
You must have the Owner role for the group.
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Runners
.
To the right of the runner you want to protect, select
Edit
(
pencil
).
Select the
Protected
checkbox.
Select
Save changes
.
For a project runner
Prerequisites:
You must have the Owner role for the project.
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
Runners
.
To the right of the runner you want to protect, select
Edit
(
pencil
).
Select the
Protected
checkbox.
Select
Save changes
.
Control jobs that a runner can run
You can use
tags
to control the jobs a runner can run.
For example, you can specify the
rails
tag for runners that have the dependencies to run
Rails test suites.
GitLab CI/CD tags are different to Git tags. GitLab CI/CD tags are associated with runners.
Git tags are associated with commits.
For an instance runner
Prerequisites:
You must be an administrator.
To control the jobs that an instance runner can run:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
CI/CD > Runners
.
To the right of the runner you want to edit, select
Edit
(
pencil
).
Set the runner to run tagged or untagged jobs:
To run tagged jobs, in the
Tags
field, enter the job tags separated with a comma. For example,
macos
,
rails
.
To run untagged jobs, select the
Run untagged jobs
checkbox.
Select
Save changes
.
For a group runner
Prerequisites:
You must have the Owner role for the group.
To control the jobs that a group runner can run:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Runners
.
To the right of the runner you want to edit, select
Edit
(
pencil
).
Set the runner to run tagged or untagged jobs:
To run tagged jobs, in the
Tags
field, enter the job tags separated with a comma. For example,
macos
,
ruby
.
To run untagged jobs, select the
Run untagged jobs
checkbox.
Select
Save changes
.
For a project runner
Prerequisites:
You must have the Owner role for the project.
To control the jobs that a project runner can run:
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
Runners
.
To the right of the runner you want to edit, select
Edit
(
pencil
).
Set the runner to run tagged or untagged jobs:
To run tagged jobs, in the
Tags
field, enter the job tags separated with a comma. For example,
macos
,
ruby
.
To run untagged jobs, select the
Run untagged jobs
checkbox.
Select
Save changes
.
How the runner uses tags
Runner runs only tagged jobs
The following examples illustrate the potential impact of the runner being set
to run only tagged jobs.
Example 1:
The runner is configured to run only tagged jobs and has the
docker
tag.
A job that has a
hello
tag is executed and stuck.
Example 2:
The runner is configured to run only tagged jobs and has the
docker
tag.
A job that has a
docker
tag is executed and run.
Example 3:
The runner is configured to run only tagged jobs and has the
docker
tag.
A job that has no tags defined is executed and stuck.
Runner is allowed to run untagged jobs
The following examples illustrate the potential impact of the runner being set
to run tagged and untagged jobs.
Example 1:
The runner is configured to run untagged jobs and has the
docker
tag.
A job that has no tags defined is executed and run.
A second job that has a
docker
tag defined is executed and run.
Example 2:
The runner is configured to run untagged jobs and has no tags defined.
A job that has no tags defined is executed and run.
A second job that has a
docker
tag defined is stuck.
A runner and a job have multiple tags
The selection logic that matches the job and runner is based on the list of
tags
defined in the job.
The following examples illustrate the impact of a runner and a job having multiple tags. For a runner to be
selected to run a job, it must have all of the tags defined in the job script block.
Example 1:
The runner is configured with the tags
[docker, shell, gpu]
.
The job has the tags
[docker, shell, gpu]
and is executed and run.
Example 2:
The runner is configured with the tags
[docker, shell, gpu]
.
The job has the tags
[docker, shell,]
and is executed and run.
Example 3:
The runner is configured with the tags
[docker, shell]
.
The job has the tags
[docker, shell, gpu]
and is not executed.
Use tags to run jobs on different platforms
You can use tags to run different jobs on different platforms. For
example, if you have an OS X runner with tag
osx
and a Windows runner with tag
windows
, you can run a job on each platform.
Update the
tags
field in the
.gitlab-ci.yml
:
windows job
:
stage
:
build
tags
:
-
windows
script
:
-
echo Hello, %USERNAME%!
osx job
:
stage
:
build
tags
:
-
osx
script
:
-
echo "Hello, $USER!"
Use CI/CD variables in tags
In the
.gitlab-ci.yml
file, use
CI/CD variables
with
tags
for dynamic runner selection:
variables
:
KUBERNETES_RUNNER
:
kubernetes
job
:
tags
:
-
docker
-
$KUBERNETES_RUNNER
script
:
-
echo "Hello runner selector feature"
Configure runner behavior with variables
You can use
CI/CD variables
to configure runner Git behavior
globally or for individual jobs:
GIT_STRATEGY
GIT_SUBMODULE_STRATEGY
GIT_CHECKOUT
GIT_CLEAN_FLAGS
GIT_FETCH_EXTRA_FLAGS
GIT_CLONE_EXTRA_FLAGS
GIT_SUBMODULE_UPDATE_FLAGS
GIT_SUBMODULE_FORCE_HTTPS
GIT_DEPTH
(shallow cloning)
GIT_SUBMODULE_DEPTH
GIT_CLONE_PATH
(custom build directories)
TRANSFER_METER_FREQUENCY
(artifact/cache meter update frequency)
ARTIFACT_COMPRESSION_LEVEL
(artifact archiver compression level)
CACHE_COMPRESSION_LEVEL
(cache archiver compression level)
CACHE_REQUEST_TIMEOUT
(cache request timeout)
RUNNER_SCRIPT_TIMEOUT
RUNNER_AFTER_SCRIPT_TIMEOUT
AFTER_SCRIPT_IGNORE_ERRORS
You can also use variables to configure how many times a runner
attempts certain stages of job execution
.
When using the Kubernetes executor, you can use variables to
override Kubernetes CPU and memory allocations for requests and limits
.
Runner feature flags
are also accepted as
job and pipeline variables
.
Git strategy
The
GIT_STRATEGY
variable configures how the build directory is prepared and
repository content is fetched. You can set this variable globally or per job
in the
variables
section.
variables
:
GIT_STRATEGY
:
clone
Possible values are
clone
,
fetch
,
none
, and
empty
. If you do not specify a value,
jobs use the
project’s pipeline setting
.
clone
is the slowest option. It clones the repository from scratch for every
job, ensuring that the local working copy is always pristine.
If an existing worktree is found, it is removed before cloning.
fetch
is faster as it re-uses the local working copy (falling back to
clone
if it does not exist).
git clean
is used to undo any changes made by the last
job, and
git fetch
is used to retrieve commits made after the last job ran.
However,
fetch
does require access to the previous worktree. This works
well when using the
shell
or
docker
executor because these
try to preserve worktrees and try to re-use them by default.
This has limitations when using the
Docker Machine executor
.
A Git strategy of
none
also re-uses the local working copy, but skips all Git
operations usually done by GitLab. GitLab Runner pre-clone scripts are also skipped,
if present. This strategy could mean you need to add
fetch
and
checkout
commands
to
your
.gitlab-ci.yml
script
.
It can be used for jobs that operate exclusively on artifacts, like a deployment job.
Git repository data may be present, but it’s likely out of date. You should only
rely on files brought into the local working copy from cache or artifacts. Be
aware that cache and artifact files from previous pipelines might still be present.
Unlike
none
, the
empty
Git strategy deletes and then re-creates
a dedicated build directory before downloading cache or artifact files.
With this strategy, the GitLab Runner hook scripts are still run
(if provided) to allow for further behavior customization.
Use the
empty
Git strategy when:
You do not need the repository data to be present.
You want a clean, controlled, or customized starting state every time a job runs.
Git submodule strategy
The
GIT_SUBMODULE_STRATEGY
variable is used to control if / how
Git submodules
are included when fetching the code before a build. You can set them
globally or per-job in the
variables
section.
The three possible values are
none
,
normal
, and
recursive
:
none
means that submodules are not included when fetching the project
code. This setting matches the default behavior in versions before 1.10.
normal
means that only the top-level submodules are included. It’s
equivalent to:
git submodule sync
git submodule update --init
recursive
means that all submodules (including submodules of submodules)
are included. This feature needs Git v1.8.1 and later. When using a
GitLab Runner with an executor not based on Docker, make sure the Git version
meets that requirement. It’s equivalent to:
git submodule sync --recursive
git submodule update --init --recursive
For this feature to work correctly, the submodules must be configured
(in
.gitmodules
) with either:
the HTTP(S) URL of a publicly-accessible repository, or
a relative path to another repository on the same GitLab server. See the
Git submodules
documentation.
You can provide additional flags to control advanced behavior using
GIT_SUBMODULE_UPDATE_FLAGS
.
Git checkout
The
GIT_CHECKOUT
variable can be used when the
GIT_STRATEGY
is set to either
clone
or
fetch
to specify whether a
git checkout
should be run. If not
specified, it defaults to true. You can set them globally or per-job in the
variables
section.
If set to
false
, the runner:
when doing
fetch
- updates the repository and leaves the working copy on
the current revision,
when doing
clone
- clones the repository and leaves the working copy on the
default branch.
If
GIT_CHECKOUT
is set to
true
, both
clone
and
fetch
work the same way.
The runner checks out the working copy of a revision related
to the CI pipeline:
variables
:
GIT_STRATEGY
:
clone
GIT_CHECKOUT
:
"false"
script
:
-
git checkout -B master origin/master
-
git merge $CI_COMMIT_SHA
Git clean flags
The
GIT_CLEAN_FLAGS
variable is used to control the default behavior of
git clean
after checking out the sources. You can set it globally or per-job in the
variables
section.
GIT_CLEAN_FLAGS
accepts all possible options of the
git clean
command.
git clean
is disabled if
GIT_CHECKOUT: "false"
is specified.
If
GIT_CLEAN_FLAGS
is:
Not specified,
git clean
flags default to
-ffdx
.
Given the value
none
,
git clean
is not executed.
For example:
variables
:
GIT_CLEAN_FLAGS
:
-
ffdx -e cache/
script
:
-
ls -al cache/
Git fetch extra flags
Use the
GIT_FETCH_EXTRA_FLAGS
variable to control the behavior of
git fetch
. You can set it globally or per-job in the
variables
section.
GIT_FETCH_EXTRA_FLAGS
accepts all options of the
git fetch
command. However,
GIT_FETCH_EXTRA_FLAGS
flags are appended after the default flags that can’t be modified.
The default flags are:
GIT_DEPTH
.
The list of
refspecs
.
A remote called
origin
.
If
GIT_FETCH_EXTRA_FLAGS
is:
Not specified,
git fetch
flags default to
--prune --quiet
along with the default flags.
Given the value
none
,
git fetch
is executed only with the default flags.
For example, the default flags are
--prune --quiet
, so you can make
git fetch
more verbose by overriding this with just
--prune
:
variables
:
GIT_FETCH_EXTRA_FLAGS
:
--
prune
script
:
-
ls -al cache/
The previous configuration results in
git fetch
being called this way:
git fetch origin
$REFSPECS
--depth
20
--prune
Where
$REFSPECS
is a value provided to the runner internally by GitLab.
Git clone extra flags
Use the
GIT_CLONE_EXTRA_FLAGS
variable to pass extra arguments to the native
git clone
operation.
You can set it globally or per-job in the
variables
section.
To use
GIT_CLONE_EXTRA_FLAGS
:
Set
FF_USE_GIT_NATIVE_CLONE
to
true
to enable the native
git clone
functionality.
Set
GIT_STRATEGY
to
clone
to use the clone strategy instead of fetch.
The Git client must be at least version 2.49. This condition is met automatically if the
helper image
is a Linux-flavored image, version 18.1 or later.
GIT_CLONE_EXTRA_FLAGS
accepts all options of the
git clone
command. The flags are appended to the native
git clone
command to provide flexibility for advanced use cases, including referencing alternate repositories
or optimizing clone performance.
For example, you can optimize clone performance by using a reference repository:
variables
:
FF_USE_GIT_NATIVE_CLONE
:
true
GIT_STRATEGY
:
clone
GIT_CLONE_EXTRA_FLAGS
:
"--reference-if-available /tmp/test"
If
GIT_CLONE_EXTRA_FLAGS
is not specified,
git clone
uses only the default flags.
Sync or exclude specific submodules from CI jobs
Use the
GIT_SUBMODULE_PATHS
variable to control which submodules have to be synced or updated.
You can set it globally or per-job in the
variables
section.
The path syntax is the same as
git submodule
:
To sync and update specific paths:
variables
:
GIT_SUBMODULE_PATHS
:
submoduleA submoduleB
To exclude specific paths:
variables
:
GIT_SUBMODULE_PATHS
:
":(exclude)submoduleA :(exclude)submoduleB"
Git ignores nested paths. To ignore a nested submodule, exclude
the parent submodule and then manually clone it in the job’s scripts. For example,
git clone <repo> --recurse-submodules=':(exclude)nested-submodule'
. Make sure
to wrap the string in single quotes so the YAML can be parsed successfully.
Git submodule update flags
Use the
GIT_SUBMODULE_UPDATE_FLAGS
variable to control the behavior of
git submodule update
when
GIT_SUBMODULE_STRATEGY
is set to either
normal
or
recursive
.
You can set it globally or per-job in the
variables
section.
GIT_SUBMODULE_UPDATE_FLAGS
accepts all options of the
git submodule update
subcommand. However,
GIT_SUBMODULE_UPDATE_FLAGS
flags are appended after a few default flags:
--init
, if
GIT_SUBMODULE_STRATEGY
was set to
normal
or
recursive
.
--recursive
, if
GIT_SUBMODULE_STRATEGY
was set to
recursive
.
GIT_DEPTH
. See the default value in the
shallow cloning
section.
Git honors the last occurrence of a flag in the list of arguments, so manually
providing them in
GIT_SUBMODULE_UPDATE_FLAGS
overrides these default flags.
For example, you can use this variable to:
Fetch the latest remote
HEAD
instead of the tracked commit in the
repository (default) to automatically update all submodules with the
--remote
flag.
Speed up the checkout by fetching submodules in multiple parallel jobs with
the
--jobs 4
flag.
variables
:
GIT_SUBMODULE_STRATEGY
:
recursive
GIT_SUBMODULE_UPDATE_FLAGS
:
--
remote --jobs 4
script
:
-
ls -al .git/modules/
The previous configuration results in
git submodule update
being called this way:
git submodule update --init --depth
20
--recursive --remote --jobs
4
You should be aware of the implications for the security, stability, and
reproducibility of your builds when using the
--remote
flag. In most cases,
it is better to explicitly track submodule commits as designed, and update them
using an auto-remediation/dependency bot.
The
--remote
flag is not required to check out submodules at their committed
revisions. Use this flag only when you want to automatically update submodules
to their latest remote versions.
The behavior of
--remote
depends on your Git version.
If the branch specified in your superproject’s
.gitmodules
file is different from the
default branch of the submodule repository, some Git versions will fail with this error:
fatal: Unable to find refs/remotes/origin/<branch> revision in submodule path '<submodule-path>'
The runner implements a “best effort” fallback that attempts to
pull remote refs when the submodule update fails.
If this fallback does not work with your Git version, try one of the following
workarounds:
Update the submodule repository’s default branch to match the branch set in
.gitmodules
in the superproject.
Set
GIT_SUBMODULE_DEPTH
to
0
.
Update the submodules separately and remove the
--remote
flag from
GIT_SUBMODULE_UPDATE_FLAGS
.
Rewrite submodule URLs to HTTPS
History
Introduced
in GitLab Runner 15.11.
Use the
GIT_SUBMODULE_FORCE_HTTPS
variable to force a rewrite of all Git and SSH submodule URLs to HTTPS.
You can clone submodules that use absolute URLs on the same GitLab instance, even if they were
configured with a Git or SSH protocol.
variables
:
GIT_SUBMODULE_STRATEGY
:
recursive
GIT_SUBMODULE_FORCE_HTTPS
:
"true"
When enabled, GitLab Runner uses a
CI/CD job token
to clone the submodules.
The token uses the permissions of the user executing the job and does not require SSH credentials.
Shallow cloning
You can specify the depth of fetching and cloning using
GIT_DEPTH
.
GIT_DEPTH
does a shallow clone of the repository and can significantly speed up cloning.
It can be helpful for repositories with a large number of commits or old, large binaries. The value is
passed to
git fetch
and
git clone
.
Newly-created projects automatically have a
default
git depth
value of
20
.
If you use a depth of
1
and have a queue of jobs or retry
jobs, jobs may fail.
Git fetching and cloning is based on a ref, such as a branch name, so runners
can’t clone a specific commit SHA. If multiple jobs are in the queue, or
you retry an old job, the commit to be tested must be in the cloned
Git history. Setting too small a value for
GIT_DEPTH
can make
it impossible to run these old commits and
unresolved reference
is displayed in
job logs. You should then reconsider changing
GIT_DEPTH
to a higher value.
Jobs that rely on
git describe
may not work correctly when
GIT_DEPTH
is
set because only part of the Git history is present.
To fetch or clone only the last 3 commits:
variables
:
GIT_DEPTH
:
"3"
You can set it globally or per-job in the
variables
section.
Git submodule depth
History
Introduced
in GitLab Runner 15.5.
Use the
GIT_SUBMODULE_DEPTH
variable to specify the depth of fetching and cloning submodules
when
GIT_SUBMODULE_STRATEGY
is set to either
normal
or
recursive
.
You can set it globally or for a specific job in the
variables
section.
When you set the
GIT_SUBMODULE_DEPTH
variable, it overwrites the
GIT_DEPTH
setting
for the submodules only.
To fetch or clone only the last 3 commits:
variables
:
GIT_SUBMODULE_DEPTH
:
3
Custom build directories
By default, GitLab Runner clones the repository in a unique subpath of the
$CI_BUILDS_DIR
directory. However, your project might require the code in a
specific directory (Go projects, for example). In that case, you can specify
the
GIT_CLONE_PATH
variable to tell the runner the directory to clone the
repository in:
variables
:
GIT_CLONE_PATH
:
$CI_BUILDS_DIR/project-name
test
:
script
:
-
pwd
The
GIT_CLONE_PATH
must always be inside
$CI_BUILDS_DIR
. The directory set in
$CI_BUILDS_DIR
is dependent on executor and configuration of
runners.builds_dir
setting.
This can only be used when
custom_build_dir
is enabled in the
runner’s configuration
.
Handling concurrency
An executor that uses a concurrency greater than
1
might lead
to failures. Multiple jobs might be working on the same directory if the
builds_dir
is shared between jobs.
The runner does not try to prevent this situation. It’s up to the administrator
and developers to comply with the requirements of runner configuration.
To avoid this scenario, you can use a unique path in
$CI_BUILDS_DIR
, because runner
exposes two additional variables that provide a unique
ID
of concurrency:
$CI_CONCURRENT_ID
: Unique ID for all jobs running in the given executor.
$CI_CONCURRENT_PROJECT_ID
: Unique ID for all jobs running in the given executor and project.
The most stable configuration that should work well in any scenario and on any executor
is to use
$CI_CONCURRENT_ID
in the
GIT_CLONE_PATH
. For example:
variables
:
GIT_CLONE_PATH
:
$CI_BUILDS_DIR/$CI_CONCURRENT_ID/project-name
test
:
script
:
-
pwd -P
The
$CI_CONCURRENT_PROJECT_ID
should be used in conjunction with
$CI_PROJECT_PATH
.
$CI_PROJECT_PATH
provides a path of a repository in the
group/subgroup/project
format.
For example:
variables
:
GIT_CLONE_PATH
:
$CI_BUILDS_DIR/$CI_CONCURRENT_ID/$CI_PROJECT_PATH
test
:
script
:
-
pwd -P
Nested paths
The value of
GIT_CLONE_PATH
expands once. You cannot nest variables
in this value.
For example, you define the following variables in your
.gitlab-ci.yml
file:
variables
:
GOPATH
:
$CI_BUILDS_DIR/go
GIT_CLONE_PATH
:
$GOPATH/src/namespace/project
The value of
GIT_CLONE_PATH
is expanded once into
$CI_BUILDS_DIR/go/src/namespace/project
, and results in failure
because
$CI_BUILDS_DIR
is not expanded.
Ignore errors in
after_script
You can use
after_script
in a job to define an array of commands
that should run after the job’s
before_script
and
script
sections. The
after_script
commands
run regardless of the script termination status (failure or success).
By default, GitLab Runner ignores any errors that happen when
after_script
runs.
To set the job to fail immediately on errors when
after_script
runs, set the
AFTER_SCRIPT_IGNORE_ERRORS
CI/CD variable to
false
. For example:
variables
:
AFTER_SCRIPT_IGNORE_ERRORS
:
false
Job stages attempts
You can set the number of attempts that the running job tries to execute
the following stages:
Variable
Description
ARTIFACT_DOWNLOAD_ATTEMPTS
Number of attempts to download artifacts running a job
EXECUTOR_JOB_SECTION_ATTEMPTS
The number of attempts to run a section in a job after a
No Such Container
error (
Docker executor
only).
GET_SOURCES_ATTEMPTS
Number of attempts to fetch sources running a job
RESTORE_CACHE_ATTEMPTS
Number of attempts to restore the cache running a job
The default is one single attempt.
Example:
variables
:
GET_SOURCES_ATTEMPTS
:
3
You can set them globally or per-job in the
variables
section.
System calls not available on GitLab.com instance runners
GitLab.com instance runners run on CoreOS. This means that you cannot use some system calls, like
getlogin
, from the C standard library.
Artifact and cache settings
Artifact and cache settings control the compression ratio of artifacts and caches.
Use these settings to specify the size of the archive produced by a job.
On a slow network, uploads might be faster for smaller archives.
On a fast network where bandwidth and storage are not a concern, uploads might be faster using the fastest compression ratio, despite the archive produced being larger.
For
GitLab Pages
to serve
HTTP Range requests
, artifacts
should use the
ARTIFACT_COMPRESSION_LEVEL: fastest
setting, as only uncompressed zip archives
support this feature.
A meter can be enabled to provide the rate of transfer for uploads and downloads.
You can set a maximum time for cache upload and download with the
CACHE_REQUEST_TIMEOUT
setting.
Use this setting when slow cache uploads substantially increase the duration of your job.
variables
:
# output upload and download progress every 2 seconds
TRANSFER_METER_FREQUENCY
:
"2s"
# Use fast compression for artifacts, resulting in larger archives
ARTIFACT_COMPRESSION_LEVEL
:
"fast"
# Use no compression for caches
CACHE_COMPRESSION_LEVEL
:
"fastest"
# Set maximum duration of cache upload and download
CACHE_REQUEST_TIMEOUT
:
5
Variable
Description
TRANSFER_METER_FREQUENCY
Specify how often to print the meter’s transfer rate. It can be set to a duration (for example,
1s
or
1m30s
). A duration of
0
disables the meter (default). When a value is set, the pipeline shows a progress meter for artifact and cache uploads and downloads.
ARTIFACT_COMPRESSION_LEVEL
To adjust compression ratio, set to
fastest
,
fast
,
default
,
slow
, or
slowest
. This setting works with the Fastzip archiver only, so the GitLab Runner feature flag
FF_USE_FASTZIP
must also be enabled.
CACHE_COMPRESSION_LEVEL
To adjust compression ratio, set to
fastest
,
fast
,
default
,
slow
, or
slowest
. This setting works with the Fastzip archiver only, so the GitLab Runner feature flag
FF_USE_FASTZIP
must also be enabled.
CACHE_REQUEST_TIMEOUT
Configure the maximum duration of cache upload and download operations for a single job in minutes. Default is
10
minutes.
Artifact provenance metadata
History
Introduced
in GitLab Runner 15.1.
Runners can generate an
SLSA Provenance
and produce an
SLSA Statement
that binds the provenance to all build artifacts.
The statement is called artifact provenance metadata.
To enable artifact provenance metadata, set the
RUNNER_GENERATE_ARTIFACTS_METADATA
environment
variable to
true
. You can set the variable globally or for individual jobs:
variables
:
RUNNER_GENERATE_ARTIFACTS_METADATA
:
"true"
job1
:
variables
:
RUNNER_GENERATE_ARTIFACTS_METADATA
:
"true"
The metadata renders in a plain text
.json
file stored with the artifact. The
filename is
{ARTIFACT_NAME}-metadata.json
.
ARTIFACT_NAME
is the
name for the artifact
defined in the
.gitlab-ci.yml
file. If the name is not defined, the default filename is
artifacts-metadata.json
.
Provenance metadata format
The artifact provenance metadata is generated in the
in-toto v0.1 Statement
format.
It contains a provenance predicate generated in the
SLSA 1.0 Provenance
format.
These fields are populated by default:
Field
Value
_type
https://in-toto.io/Statement/v0.1
subject
Set of software artifacts the metadata applies to
subject[].name
The filename of the artifact.
subject[].sha256
The artifact’s
sha256
checksum.
predicateType
https://slsa.dev/provenance/v1
predicate.buildDefinition.buildType
https://gitlab.com/gitlab-org/gitlab-runner/-/blob/{GITLAB_RUNNER_VERSION}/PROVENANCE.md
. For example, v15.0.0
predicate.runDetails.builder.id
A URI pointing to the runner details page, for example,
https://gitlab.com/gitlab-com/www-gitlab-com/-/runners/3785264
.
predicate.buildDefinition.externalParameters
The names of any CI/CD or environment variables available during the build command execution. The value is always represented as an empty string to protect secrets.
predicate.buildDefinition.externalParameters.source
The URL of the project.
predicate.buildDefinition.externalParameters.entryPoint
The name of the CI/CD job that triggered the build.
predicate.buildDefinition.internalParameters.name
The name of the runner.
predicate.buildDefinition.internalParameters.executor
The runner executor.
predicate.buildDefinition.internalParameters.architecture
The architecture on which the CI/CD job is run.
predicate.buildDefinition.internalParameters.job
The ID of the CI/CD job that triggered the build.
predicate.buildDefinition.resolvedDependencies[0].uri
The URL of the project.
predicate.buildDefinition.resolvedDependencies[0].digest.sha256
The commit revision of the project.
predicate.runDetails.metadata.invocationID
The ID of the CI/CD job that triggered the build.
predicate.runDetails.metadata.startedOn
The time when the build was started. This field is
RFC3339
formatted.
predicate.runDetails.metadata.finishedOn
The time when the build ended. Because metadata generation happens during the build, this time is slightly earlier than the one reported in GitLab. This field is
RFC3339
formatted.
A provenance statement should look similar to this example:
{
"_type"
:
"https://in-toto.io/Statement/v0.1"
,
"predicateType"
:
"https://slsa.dev/provenance/v1"
,
"subject"
:
[
{
"name"
:
"x.txt"
,
"digest"
:
{
"sha256"
:
"ac097997b6ec7de591d4f11315e4aa112e515bb5d3c52160d0c571298196ea8b"
}
},
{
"name"
:
"y.txt"
,
"digest"
:
{
"sha256"
:
"9eb634f80da849d828fcf42740d823568c49e8d7b532886134f9086246b1fdf3"
}
}
],
"predicate"
:
{
"buildDefinition"
:
{
"buildType"
:
"https://gitlab.com/gitlab-org/gitlab-runner/-/blob/2147fb44/PROVENANCE.md"
,
"externalParameters"
:
{
"CI"
:
""
,
"CI_API_GRAPHQL_URL"
:
""
,
"CI_API_V4_URL"
:
""
,
"CI_COMMIT_AUTHOR"
:
""
,
"CI_COMMIT_BEFORE_SHA"
:
""
,
"CI_COMMIT_BRANCH"
:
""
,
"CI_COMMIT_DESCRIPTION"
:
""
,
"CI_COMMIT_MESSAGE"
:
""
,
[...
additional
environmental
variables
...]
"entryPoint"
:
"build-job"
,
"source"
:
"https://gitlab.com/my-group/my-project/test-runner-generated-slsa-statement"
},
"internalParameters"
:
{
"architecture"
:
"amd64"
,
"executor"
:
"docker+machine"
,
"job"
:
"10340684631"
,
"name"
:
"green-4.saas-linux-small-amd64.runners-manager.gitlab.com/default"
},
"resolvedDependencies"
:
[
{
"uri"
:
"https://gitlab.com/my-group/my-project/test-runner-generated-slsa-statement"
,
"digest"
:
{
"sha256"
:
"bdd2ecda9ef57b129c88617a0215afc9fb223521"
}
}
]
},
"runDetails"
:
{
"builder"
:
{
"id"
:
"https://gitlab.com/my-group/my-project/test-runner-generated-slsa-statement/-/runners/12270857"
,
"version"
:
{
"gitlab-runner"
:
"2147fb44"
}
},
"metadata"
:
{
"invocationID"
:
"10340684631"
,
"startedOn"
:
"2025-06-13T07:25:13Z"
,
"finishedOn"
:
"2025-06-13T07:25:40Z"
}
}
}
}
Staging directory
History
Introduced
in GitLab Runner 15.0.
If you do not want to archive cache and artifacts in the system’s default temporary directory, you can specify a different directory.
You might need to change the directory if your system’s default temporary path has constraints.
If you use a fast disk for the directory location, it can also improve performance.
To change the directory, set
ARCHIVER_STAGING_DIR
as a variable in your CI job, or use a runner variable when you register the runner (
gitlab register --env ARCHIVER_STAGING_DIR=<dir>
).
The directory you specify is used as the location for downloading artifacts prior to extraction. If the
fastzip
archiver is
used, this location is also used as scratch space when archiving.
Configure
fastzip
to improve performance
History
Introduced
in GitLab Runner 15.0.
To tune
fastzip
, ensure the
FF_USE_FASTZIP
flag is enabled.
Then use any of the following environment variables.
Variable
Description
FASTZIP_ARCHIVER_CONCURRENCY
The number of files to be concurrently compressed. Default is the number of CPUs available.
FASTZIP_ARCHIVER_BUFFER_SIZE
The buffer size allocated per concurrency for each file. Data exceeding this number moves to scratch space. Default is 2 MiB.
FASTZIP_EXTRACTOR_CONCURRENCY
The number of files to be concurrency decompressed. Default is the number of CPUs available.
Files in a zip archive are appended sequentially. This makes concurrent compression challenging.
fastzip
works around
this limitation by compressing files concurrently to disk first, and then copying the result back to zip archive
sequentially.
To avoid writing to disk and reading the contents back for smaller files, a small buffer per concurrency is used. This setting
can be controlled with
FASTZIP_ARCHIVER_BUFFER_SIZE
. The default size for this buffer is 2 MiB, therefore, a
concurrency of 16 allocates 32 MiB. Data that exceeds the buffer size is written to and read back from disk.
Therefore, using no buffer,
FASTZIP_ARCHIVER_BUFFER_SIZE: 0
, and only scratch space is a valid option.
FASTZIP_ARCHIVER_CONCURRENCY
controls how many files are compressed concurrency. As previously mentioned, this setting
therefore can increase how much memory is being used. It can also increase the temporary data written to the scratch space.
The default is the number of CPUs available, but given the memory ramifications, this may not always be the best
setting.
FASTZIP_EXTRACTOR_CONCURRENCY
controls how many files are decompressed at once. Files from a zip archive can natively
be read from concurrency, so no additional memory is allocated in addition to what the extractor requires. This
defaults to the number of CPUs available.
