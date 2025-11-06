# Hosted runners on macOS | GitLab Docs

Source: https://docs.gitlab.com/ci/runners/hosted_runners/macos/

Hosted runners on macOS | GitLab Docs
Hosted runners on macOS
Tier
: Premium, Ultimate
Offering
: GitLab.com
Status
: Beta
Hosted runners on macOS provide an on-demand macOS environment, fully integrated with GitLab
CI/CD
.
You can use these runners to build, test, and deploy apps for the Apple ecosystem (macOS, iOS, watchOS, tvOS).
Our
Mobile DevOps section
provides features, documentation, and guidance on building and deploying mobile applications for iOS.
Hosted runners on macOS are in
beta
and available for open source programs and customers in Premium and Ultimate plans.
General availability
of Hosted runners on macOS is proposed in
epic 8267
.
Review the list of
known issues and usage constraints
that affect hosted runners on macOS before you use them.
Machine types available for macOS
GitLab offers the following machine type for hosted runners on macOS. To build for an x86-64 target, you can use Rosetta 2 to emulate an Intel x86-64 environment.
Runner Tag
vCPUS
Memory
Storage
saas-macos-medium-m1
4
8 GB
50 GB
saas-macos-large-m2pro
6
16 GB
50 GB
Supported macOS images
In comparison to our hosted runners on Linux, where you can run any Docker image,
GitLab provides a set of VM images for macOS.
You can execute your build in one of the following images, which you specify
in your
.gitlab-ci.yml
file. Each image runs a specific version of macOS and Xcode.
VM image
Status
macos-14-xcode-15
GA
Preinstalled Software
macos-15-xcode-16
GA
Preinstalled Software
If no image is specified, the macOS runner uses
macos-15-xcode-16
.
Image update policy for macOS
The images and installed components are updated with each GitLab release, to keep the preinstalled software up-to-date. GitLab typically supports multiple versions of preinstalled software. For more information, see the
full list of preinstalled software
.
Major and minor releases of macOS and Xcode are made available in the milestone subsequent to the Apple release.
A new major release image is initially made available as beta, and becomes generally available with the release of the first minor release.
Because only two generally available images are supported at a time, the oldest image becomes deprecated and will be removed after three months according to the
supported image lifecycle
.
When a new major release is generally available, it becomes the default image for all macOS jobs.
Example
.gitlab-ci.yml
file
The following sample
.gitlab-ci.yml
file shows how to start using the hosted runners on macOS:
.macos_saas_runners
:
tags
:
-
saas-macos-medium-m1
image
:
macos-14-xcode-15
before_script
:
-
echo "started by ${GITLAB_USER_NAME} / @${GITLAB_USER_LOGIN}"
build
:
extends
:
-
.macos_saas_runners
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
.macos_saas_runners
stage
:
test
script
:
-
echo "running scripts in the test job"
Code signing iOS Projects with fastlane
Before you can integrate GitLab with Apple services, install to a device, or deploy to the Apple App Store, you must
code sign
your application.
Included in each runner on macOS VM image is
fastlane
,
an open-source solution aimed at simplifying mobile app deployment.
For information about how to set up code signing for your application, see the instructions in the
Mobile DevOps documentation
.
Related topics:
Apple Developer Support - Code Signing
Code Signing Best Practice Guide
fastlane authentication with Apple Services guide
Optimizing Homebrew
By default, Homebrew checks for updates at the start of any operation. Homebrew has a
release cycle that may be more frequent than the GitLab macOS image release cycle. This
difference in release cycles may cause steps that call
brew
to take extra time to complete
while Homebrew makes updates.
To reduce build time due to unintended Homebrew updates, set the
HOMEBREW_NO_AUTO_UPDATE
variable in
.gitlab-ci.yml
:
variables
:
HOMEBREW_NO_AUTO_UPDATE
:
1
Optimizing Cocoapods
If you use Cocoapods in a project, you should consider the following optimizations to improve CI performance.
Cocoapods CDN
You can use content delivery network (CDN) access to download packages from the CDN instead of having to clone an entire
project repository. CDN access is available in Cocoapods 1.8 or later and is supported by all GitLab hosted runners on macOS.
To enable CDN access, ensure your Podfile starts with:
source
'https://cdn.cocoapods.org/'
Use GitLab caching
Use caching in Cocoapods packages in GitLab to only run
pod install
when pods change, which can improve build performance.
To
configure caching
for your project:
Add the
cache
configuration to your
.gitlab-ci.yml
file:
cache
:
key
:
files
:
-
Podfile.lock
paths
:
-
Pods
Add the
cocoapods-check
plugin to your project.
Update the job script to check for installed dependencies before it calls
pod install
:
bundle
exec
pod check
||
bundle
exec
pod install
Include pods in source control
You can also
include the pods directory in source control
. This eliminates the need to install pods as part of the CI job,
but it does increase the overall size of your project’s repository.
Known issues and usage constraints
If the VM image does not include the specific software version you need for your job, the required software must be fetched and installed. This causes an increase in job execution time.
It is not possible to bring your own OS image.
The keychain for user
gitlab
is not publicly available. You must create a keychain instead.
Hosted runners on macOS run in headless mode.
Any workloads that require UI interactions such as
testmanagerd
are not supported.
Job performance might vary between job executions as Apple silicon chips have efficiency and
performance cores. You can’t control core allocation or scheduling, which might lead to inconsistencies.
The availability of AWS bare metal macOS machines used for hosted runners on macOS is limited. Jobs might experience extended queuing times when no machines are available.
Hosted runner instances on macOS sometimes do not respond to requests, which results in jobs hanging until the maximum job duration is reached.
macOS uses a case-insensitive file system by default.
This behavior can result in unexpected errors if you have duplicate file paths that are equal except case.
These duplicate paths could be in the Git working tree or Git refs where branches and tags are stored.
