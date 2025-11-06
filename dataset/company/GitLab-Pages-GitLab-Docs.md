# GitLab Pages | GitLab Docs

Source: https://docs.gitlab.com/user/project/pages/#parallel-deployments

GitLab Pages | GitLab Docs
GitLab Pages
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
GitLab Pages publishes static websites directly from a repository in GitLab.
These websites:
Deploy automatically with GitLab CI/CD pipelines.
Support any static site generator (like Hugo, Jekyll, or Gatsby) or plain HTML, CSS, and JavaScript.
Run on GitLab-provided infrastructure at no additional cost.
Connect with custom domains and SSL/TLS certificates.
Control access through built-in authentication.
Scale reliably for personal, business, or project documentation sites.
To publish a website with Pages, use any static site generator like Gatsby, Jekyll, Hugo, Middleman, Harp, Hexo, or Brunch.
Pages also supports websites written directly in plain HTML, CSS, and JavaScript.
Dynamic server-side processing (like
.php
and
.asp
) is not supported.
For more information, see
Static vs dynamic websites
.
Getting started
To create a GitLab Pages website:
Document
Description
Use the GitLab UI to create a simple
.gitlab-ci.yml
Add a Pages site to an existing project. Use the UI to set up a simple
.gitlab-ci.yml
.
Create a
.gitlab-ci.yml
file from scratch
Add a Pages site to an existing project. Learn how to create and configure your own CI file.
Use a
.gitlab-ci.yml
template
Add a Pages site to an existing project. Use a pre-populated CI template file.
Fork a sample project
Create a new project with Pages already configured by forking a sample project.
Use a project template
Create a new project with Pages already configured by using a template.
To update a GitLab Pages website:
Document
Description
GitLab Pages domain names, URLs, and base URLs
Learn about GitLab Pages default domains.
Explore GitLab Pages
Requirements, technical aspects, specific GitLab CI/CD configuration options, Access Control, custom 404 pages, limitations, and FAQ.
Custom domains and SSL/TLS Certificates
Custom domains and subdomains, DNS records, and SSL/TLS certificates.
Let’s Encrypt integration
Secure your Pages sites with Let’s Encrypt certificates, which are automatically obtained and renewed by GitLab.
Redirects
Set up HTTP redirects to forward one page to another.
For more information, see:
Document
Description
Static vs dynamic websites
Static versus dynamic site overview.
Modern static site generators
SSG overview.
Build any SSG site with GitLab Pages
Use SSGs for GitLab Pages.
Using GitLab Pages
To use GitLab Pages, you must create a project in GitLab to upload your website’s
files to. These projects can be either public, internal, or private.
By default, GitLab deploys your website from a specific folder called
public
in your
repository.
You can also
set a custom folder to be deployed with Pages
.
When you create a new project in GitLab, a
repository
becomes available automatically.
To deploy your site, GitLab uses its built-in tool called
GitLab CI/CD
to build your site and publish it to the GitLab Pages server. The sequence of
scripts that GitLab CI/CD runs to accomplish this task is created from a file named
.gitlab-ci.yml
, which you can
create and modify
.
A user-defined
job
with
pages: true
property in the configuration file makes
GitLab aware that you’re deploying a GitLab Pages website.
You can either use the GitLab
default domain for GitLab Pages websites
,
*.gitlab.io
, or your own domain (
example.com
). In that case, you
must be an administrator in your domain’s registrar (or control panel) to set it up with Pages.
Access to your Pages site
If you’re using GitLab Pages default domain (
.gitlab.io
), your website is
automatically secure and available under HTTPS. If you’re using your own custom
domain, you can optionally secure it with SSL/TLS certificates.
If you’re using GitLab.com, your website is publicly available to the internet.
To restrict access to your website, enable
GitLab Pages Access Control
.
If you’re using a GitLab Self-Managed instance, your websites are published on your
own server, according to the
Pages settings
chosen by your sysadmin, who can make them public or internal.
Pages examples
These GitLab Pages website examples can teach you advanced techniques to use
and adapt for your own needs:
Posting to your GitLab Pages blog from iOS
.
GitLab CI: Run jobs sequentially, in parallel, or build a custom pipeline
.
GitLab CI: Deployment & environments
.
Building a new GitLab docs site with Nanoc, GitLab CI, and GitLab Pages
.
Publish code coverage reports with GitLab Pages
.
Administer GitLab Pages for GitLab Self-Managed instances
If you are running a GitLab Self-Managed instance,
follow the administration steps
to configure Pages.
Watch a
video tutorial
about how to get started with GitLab Pages administration.
Configure GitLab Pages in a Helm Chart (Kubernetes) instance
To configure GitLab Pages on instances deployed with Helm chart (Kubernetes), use either:
The
gitlab-pages
subchart
.
An external GitLab Pages instance
.
Security for GitLab Pages
Namespaces that contain
.
If your username is
example
, your GitLab Pages website is located at
example.gitlab.io
.
GitLab allows usernames to contain a
.
, so a user named
bar.example
could create
a GitLab Pages website
bar.example.gitlab.io
that effectively is a subdomain of your
example.gitlab.io
website. Be careful if you use JavaScript to set cookies for your website.
The safe way to manually set cookies with JavaScript is to not specify the
domain
at all:
// Safe: This cookie is only visible to example.gitlab.io
document
.
cookie
=
"key=value"
;
// Unsafe: This cookie is visible to example.gitlab.io and its subdomains,
// regardless of the presence of the leading dot.
document
.
cookie
=
"key=value;domain=.example.gitlab.io"
;
document
.
cookie
=
"key=value;domain=example.gitlab.io"
;
This issue doesn’t affect users with a custom domain, or users who don’t set any
cookies manually with JavaScript.
Shared cookies
By default, every project in a group shares the same domain, for example,
group.gitlab.io
. This means that cookies are also shared for all projects in a group.
To ensure each project uses different cookies, enable the Pages
unique domains
feature for your project.
Unique domains
History
Introduced
in GitLab 15.9
with a flag
named
pages_unique_domain
. Disabled by default.
Enabled by default
in GitLab 15.11.
Feature flag removed
in GitLab 16.3.
Changed
unique domain URLs to be shorter in GitLab 17.4.
By default, every new project uses pages unique domain. This is to avoid projects on the same group
to share cookies.
The project maintainer can disable this feature on:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Deploy
>
Pages
.
Clear the
Use unique domain
checkbox.
Select
Save changes
.
For example URLs, see
GitLab Pages default domain names
.
Primary domain
History
Introduced
in GitLab 17.8.
When you use GitLab Pages with custom domains, you can redirect all requests to GitLab Pages to a primary domain.
When the primary domain is selected, users receive
308 Permanent Redirect
status that redirects the browser to the
selected primary domain. Browsers might cache this redirect.
Prerequisites:
You must have at least the Maintainer role for the project.
A
custom domain
must be set up.
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Deploy
>
Pages
.
From the
Primary domain
dropdown list, select the domain to redirect to.
Select
Save changes
.
Expiring deployments
History
Introduced
in GitLab 17.4.
Support for variables
introduced
in GitLab 17.11.
You can configure your Pages deployments to be automatically deleted after
a period of time has passed by specifying a duration at
pages.expire_in
:
create-pages
:
stage
:
deploy
script
:
-
...
pages
:
# specifies that this is a Pages job and publishes the default public directory
expire_in
:
1
week
Expired deployments are stopped by a cron job that runs every 10 minutes.
Stopped deployments are subsequently deleted by another cron job that also
runs every 10 minutes. To recover it, follow the steps described in
Recover a stopped deployment
.
A stopped or deleted deployment is no longer available on the web. You
see a 404 Not found error page at its URL, until another deployment is created
with the same URL configuration.
The previous YAML example uses
user-defined job names
.
Recover a stopped deployment
Prerequisites:
You must have at least the Maintainer role for the project.
To recover a stopped deployment that has not yet been deleted:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Deploy
>
Pages
.
Near
Deployments
turn on the
Include stopped deployments
toggle.
If your deployment has not been deleted yet, it should be included in the
list.
Expand the deployment you want to recover and select
Restore
.
Delete a Deployment
To delete a deployment:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Deploy
>
Pages
.
Under
Deployments
, select any area on the deployment you wish to delete.
The deployment details expand.
Select
Delete
.
When you select
Delete
, your deployment is stopped immediately.
Stopped deployments are deleted by a cron job running every 10 minutes.
To restore a stopped deployment that has not been deleted yet, see
Recover a stopped deployment
.
User-defined job names
History
Introduced
in GitLab 17.5 with a flag
customizable_pages_job_name
, disabled by default.
Generally available
in GitLab 17.6. Feature flag
customizable_pages_job_name
removed.
To trigger a Pages deployment from any job, include the
pages
property in the
job definition. It can either be a Boolean set to
true
or a hash.
For example, using
true
:
deploy-my-pages-site
:
stage
:
deploy
script
:
-
npm run build
pages
:
true
# specifies that this is a Pages job and publishes the default public directory
For example, using a hash:
deploy-pages-review-app
:
stage
:
deploy
script
:
-
npm run build
pages
:
# specifies that this is a Pages job and publishes the default public directory
path_prefix
:
'_staging'
If the
pages
property of a job named
pages
is set to
false
, no
deployment is triggered:
pages
:
pages
:
false
If you have multiple Pages jobs in your pipeline with the same value for
path_prefix
, the last one to be completed will be deployed with Pages.
Parallel deployments
To create multiple deployments for your project at the same time, for example to
create review apps, view the documentation on
Parallel Deployments
.
