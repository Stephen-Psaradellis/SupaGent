# Contribute to GitLab Pages development | GitLab Docs

Source: https://docs.gitlab.com/development/pages/

Contribute to GitLab Pages development | GitLab Docs
Contribute to GitLab Pages development
Learn how to configure GitLab Pages so you can help develop the feature.
Configuring GitLab Pages hostname
GitLab Pages needs a hostname or domain, as each different GitLab Pages site is accessed through a
subdomain. You can set the GitLab Pages hostname:
Without wildcard, editing your hosts file
.
With DNS wildcard alternatives
.
Without wildcard, editing your hosts file
As
/etc/hosts
don’t support wildcard hostnames, you must configure one entry
for GitLab Pages, and then one entry for each page site:
127.0.0.1 gdk.test # If you're using GDK
127.0.0.1 pages.gdk.test # Pages host
# Any namespace/group/user needs to be added
# as a subdomain to the pages host. This is because
# /etc/hosts doesn't accept wildcards
127.0.0.1 root.pages.gdk.test # for the root pages
With DNS wildcard alternatives
If instead of editing your
/etc/hosts
you’d prefer to use a DNS wildcard, you can use:
nip.io
dnsmasq
Configuring GitLab Pages without GDK
Create a
gitlab-pages.conf
in the root of the GitLab Pages site, like:
# Default port is 3010, but you can use any other
listen-http
=
:
3010
# Your local GitLab Pages domain
pages-domain
=
pages
.
gdk
.
test
# Directory where the pages are stored
pages-root
=
shared
/
pages
# Show more information in the logs
log-verbose
=
true
To see more options you can check
internal/config/flags.go
or run
gitlab-pages --help
.
Running GitLab Pages manually
For any changes in the code, you must run
make
to build the app. It’s best to just always run
it before you start the app. It’s quick to build so don’t worry!
make
&&
./gitlab-pages -config
=
gitlab-pages.conf
Configuring GitLab Pages with GDK
In the following steps,
$GDK_ROOT
is the directory where you cloned GDK.
Set up the
GDK hostname
.
Add a
GitLab Pages hostname
to the
gdk.yml
:
gitlab_pages
:
enabled
:
true
# enable GitLab Pages to be managed by gdk
port
:
3010
# default port is 3010
host
:
pages.gdk.test
# the GitLab Pages domain
auto_update
:
true
# if gdk must update GitLab Pages git
verbose
:
true
# show more information in the logs
Running GitLab Pages with GDK
After these configurations are set, GDK manages a GitLab Pages process, giving you access to
it with commands like:
Start:
gdk start gitlab-pages
Stop:
gdk stop gitlab-pages
Restart:
gdk restart gitlab-pages
Tail logs:
gdk tail gitlab-pages
Running GitLab Pages manually
You can also build and start the app independently of GDK processes management.
For any changes in the code, you must run
make
to build the app. It’s best to just always run
it before you start the app. It’s quick to build so don’t worry!
make
&&
./gitlab-pages -config
=
gitlab-pages.conf
Building GitLab Pages in FIPS mode
FIPS_MODE
=
1
make
&&
./gitlab-pages -config
=
gitlab-pages.conf
Creating GitLab Pages site
To build a GitLab Pages site locally you must
configure
gitlab-runner
.
For more information, refer to the
user manual
.
Enabling access control
GitLab Pages support private sites. Private sites can be accessed only by users
who have access to your GitLab project.
GitLab Pages access control is disabled by default. To enable it:
Enable the GitLab Pages access control in GitLab itself. You can do this in two ways:
If you’re not using GDK, edit
gitlab.yml
:
# gitlab/config/gitlab.yml
pages
:
access_control
:
true
If you’re using GDK, edit
gdk.yml
:
# $GDK_ROOT/gdk.yml
gitlab_pages
:
enabled
:
true
access_control
:
true
Restart GitLab (if running through the GDK, run
gdk restart
). Running
gdk reconfigure
overwrites the value of
access_control
in
config/gitlab.yml
.
In your local GitLab instance, in the browser go to
http://gdk.test:3000/admin/applications
.
Create an
Instance-wide OAuth application
with the
api
scope.
Set the value of your
redirect-uri
to the
pages-domain
authorization endpoint
(for example,
http://pages.gdk.test:3010/auth
).
The
redirect-uri
must not contain any GitLab Pages site domain.
Add the auth client configuration:
With GDK, in
gdk.yml
:
gitlab_pages
:
enabled
:
true
access_control
:
true
auth_client_id
:
$CLIENT_ID
# the OAuth application id created in http://gdk.test:3000/admin/applications
auth_client_secret
:
$CLIENT_SECRET
# the OAuth application secret created in http://gdk.test:3000/admin/applications
GDK generates random
auth_secret
and builds the
auth_redirect_uri
based on GitLab Pages
host configuration.
Without GDK, in
gitlab-pages.conf
:
## the following are only needed if you want to test auth for private projects
auth-client-id=$CLIENT_ID # the OAuth application id created in http://gdk.test:3000/admin/applications
auth-client-secret=$CLIENT_SECRET # the OAuth application secret created in http://gdk.test:3000/admin/applications
auth-secret=$SOME_RANDOM_STRING # should be at least 32 bytes long
auth-redirect-uri=http://pages.gdk.test:3010/auth # the authentication callback url for GitLab Pages
If running Pages inside the GDK, you can use GDK
protected_config_files
section under
gdk
in
your
gdk.yml
to avoid getting
gitlab-pages.conf
configuration rewritten:
gdk
:
protected_config_files
:
-
'gitlab-pages/gitlab-pages.conf'
Enabling object storage
GitLab Pages support using object storage for storing artifacts, but object storage
is disabled by default. You can enable it in the GDK:
Edit
gdk.yml
to enable the object storage in GitLab itself:
# $GDK_ROOT/gdk.yml
object_store
:
enabled
:
true
Reconfigure and restart GitLab by running the commands
gdk reconfigure
and
gdk restart
.
For more information, refer to the
GDK documentation
.
Linting
# Run the linter locally
make lint
# Run linter and fix issues (if supported by the linter)
make format
Testing
To run tests, you can use these commands:
# This will run all of the tests in the codebase
make
test
# Run a specific test file
go
test
./internal/serving/disk/
# Run a specific test in a file
go
test
./internal/serving/disk/ -run TestDisk_ServeFileHTTP
# Run all unit tests except acceptance_test.go
go
test
./... -short
# Run acceptance_test.go only
make acceptance
# Run specific acceptance tests
# We add `make` here because acceptance tests use the last binary that was compiled,
# so we want to have the latest changes in the build that is tested
make
&&
go
test
./ -run TestRedirect
Contributing
Feature flags
All newly-introduced feature flags should be
disabled by default
.
Consider adding a
feature flag
for any non-trivial changes.
Feature flags can make the release and rollback of these changes easier, avoiding
incidents and downtime. To add a new feature flag to GitLab Pages:
Create the feature flag in
internal/feature/feature.go
,
which must be
off
by default.
Create an issue to track the feature flag using the
Feature flag
template.
Add the
~"feature flag"
label to any merge requests that handle feature flags.
For GitLab Pages, the feature flags are controlled by environment variables at a global level.
A deployment at the service level is required to change the state of a feature flag.
Example of a merge request enabling a GitLab Pages feature flag:
Enforce GitLab Pages rate limits
Related topics
Feature flags in the development of GitLab
Becoming a GitLab Pages maintainer
This document serves as a guideline for GitLab team members that want to become maintainers for the GitLab Pages project.
Maintainers should have an advanced understanding of the GitLab Pages codebase.
Prior to applying for maintainer of a project, a person should gain a good feel for the codebase, expertise in one or more functionalities,
and deep understanding of our coding standards.
Expectations
The process to
become a maintainer at GitLab is defined in the handbook
,
and it is the baseline for this process. One thing that is expected is a high number of reviews, however;
the rate of change of the GitLab Pages compared to the GitLab Rails project is too little.
To work around that problem, one must be comfortable in the following areas of the codebase:
Main areas:
Namespace/project resolution
ZIP serving and the virtual file system
Authentication
Smaller areas:
Redirects
Artifacts proxying
Handling of TLS certificates
Rate-limiting
Metrics and monitoring
To achieve this, you should try to make relevant contributions in all main areas and 2-3 smaller areas
mentioned above so that you have a better understanding of the functionality. A relevant contribution may be a bug fix,
a performance improvement, a new feature, or a significant refactoring.
Reviewer
Prior to becoming a maintainer, you should first become a reviewer of the project. This should include changes
to any part of the codebase including the documentation.
To become a reviewer follow the steps
outlined in the handbook
.
There is no set timeline of how long you should be a reviewer before becoming a maintainer, but you should
gain enough experience in the areas mentioned in the
expectations section
of this document.
Maintainer
To become a maintainer follow the steps
outlined in the handbook
.
You are probably ready to become a maintainer when these statements feel true:
The MRs you have reviewed consistently make it through maintainer review without significant additionally required changes
The MRs you have created consistently make it through reviewer and maintainer review without significant required changes
You feel comfortable working through operational tasks
If those subjective requirements are satisfied,
open an MR
promoting you to maintainer and tag the existing maintainers.
