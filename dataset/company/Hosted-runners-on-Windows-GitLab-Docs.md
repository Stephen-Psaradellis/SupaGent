# Hosted runners on Windows | GitLab Docs

Source: https://docs.gitlab.com/ci/runners/hosted_runners/windows/

Hosted runners on Windows | GitLab Docs
Hosted runners on Windows
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com
Status
: Beta
Hosted runners on Windows autoscale by launching virtual machines on
the Google Cloud Platform. This solution uses an
autoscaling driver
developed by GitLab for the
custom executor
.
Hosted runners on Windows are in
beta
.
GitLab keeps iterating to get Windows runners in a stable state and
generally available
.
You can follow the work towards this goal in the
related epic
.
Machine types available for Windows
GitLab offers the following machine type for hosted runners on Windows.
Runner Tag
vCPUs
Memory
Storage
saas-windows-medium-amd64
2
7.5 GB
75 GB
Supported Windows versions
The Windows runner virtual machine instances do not use the GitLab Docker executor. This means that you can’t specify
image
or
services
in your pipeline configuration.
You can execute your job in one of the following Windows versions:
Version
Status
Windows 2022
GA
You can find a full list of available pre-installed software in
the
pre-installed software documentation
.
Supported shell
Hosted runners on Windows have PowerShell configured as the shell.
The
script
section of your
.gitlab-ci.yml
file therefore requires PowerShell commands.
Example
.gitlab-ci.yml
file
Use this example
.gitlab-ci.yml
file to get started with hosted runners on Windows:
.windows_job
:
tags
:
-
saas-windows-medium-amd64
before_script
:
-
Set-Variable -Name "time" -Value (date -Format "%H:%m")
-
echo ${time}
-
echo "started by ${GITLAB_USER_NAME} / @${GITLAB_USER_LOGIN}"
build
:
extends
:
-
.windows_job
stage
:
build
script
:
-
echo "running scripts in the build job"
test
:
extends
:
-
.windows_job
stage
:
test
script
:
-
echo "running scripts in the test job"
Known issues
For more information about support for beta features, see
beta
.
The average provisioning time for a new Windows virtual machine (VM) is five minutes, so
you might notice slower start times for builds on the Windows runner
fleet during the beta. Updating the autoscaler to enable the pre-provisioning
of virtual machines is proposed in a future release. This update is intended to
significantly reduce the time it takes to provision a VM on the Windows fleet.
For more information, see
issue 32
.
The Windows runner fleet may be unavailable occasionally
for maintenance or updates.
The job may stay in a pending state for longer than the
Linux runners.
There is the possibility that we introduce breaking changes which will
require updates to pipelines that are using the Windows runner
fleet.
