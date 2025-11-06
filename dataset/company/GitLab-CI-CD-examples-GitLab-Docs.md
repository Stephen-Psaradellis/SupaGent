# GitLab CI/CD examples | GitLab Docs

Source: https://docs.gitlab.com/ci/examples/#cicd-templates

GitLab CI/CD examples | GitLab Docs
GitLab CI/CD examples
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
This page contains links to a variety of examples that can help you understand how to
implement
GitLab CI/CD
for your specific use case.
Examples are available in several forms. As a collection of:
.gitlab-ci.yml
template files
maintained in GitLab, for many
common frameworks and programming languages.
Repositories with
example projects
for various languages. You can fork and adjust them to your own needs. Projects include an example of using
review apps with a static site served by NGINX
.
Examples and
other resources
listed in the following sections.
CI/CD examples
The following table lists examples with step-by-step tutorials that are contained in this section:
Use case
Resource
Deployment with Dpl
Using
dpl
as deployment tool
.
GitLab Pages
See the
GitLab Pages
documentation for a complete example of deploying a static site.
Multi project pipeline
Build, test deploy using multi project pipeline
.
npm with semantic-release
Publish npm packages to the GitLab package registry using semantic-release
.
PHP with npm, SCP
Running Composer and npm scripts with deployment via SCP in GitLab CI/CD
.
PHP with PHPUnit,
atoum
Testing PHP projects
.
Secrets management with Vault
Authenticating and Reading Secrets With HashiCorp Vault
.
Contributed examples
You can help people that use your favorite programming language by submitting a link
to a guide for that language. These contributed guides are hosted externally or in
separate example projects:
Use case
Resource
Clojure
Test a Clojure application with GitLab CI/CD
.
Game development
DevOps and Game Development with GitLab CI/CD
.
Java with Maven
How to deploy Maven projects to Artifactory with GitLab CI/CD
.
Java with Spring Boot
Deploy a Spring Boot application to Cloud Foundry with GitLab CI/CD
.
Parallel testing Ruby & JS
GitLab CI/CD parallel jobs testing for Ruby & JavaScript projects
.
Python on Heroku
Test and deploy a Python application with GitLab CI/CD
.
Ruby on Heroku
Test and deploy a Ruby application with GitLab CI/CD
.
Scala on Heroku
Test and deploy a Scala application to Heroku
.
CI/CD templates
Get started with GitLab CI/CD and your favorite programming language or framework by using a
.gitlab-ci.yml
template
.
When you create a
.gitlab-ci.yml
file in the UI, you can
choose one of these templates:
Android (
Android.gitlab-ci.yml
)
Android with fastlane (
Android-Fastlane.gitlab-ci.yml
)
Bash (
Bash.gitlab-ci.yml
)
C++ (
C++.gitlab-ci.yml
)
Chef (
Chef.gitlab-ci.yml
)
Clojure (
Clojure.gitlab-ci.yml
)
Composer
Composer.gitlab-ci.yml
Crystal (
Crystal.gitlab-ci.yml
)
Dart (
Dart.gitlab-ci.yml
)
Django (
Django.gitlab-ci.yml
)
Docker (
Docker.gitlab-ci.yml
)
dotNET (
dotNET.gitlab-ci.yml
)
dotNET Core (
dotNET-Core.gitlab-ci.yml
)
Elixir (
Elixir.gitlab-ci.yml
)
Flutter (
Flutter.gitlab-ci.yml
)
Go (
Go.gitlab-ci.yml
)
Gradle (
Gradle.gitlab-ci.yml
)
Grails (
Grails.gitlab-ci.yml
)
iOS with fastlane (
iOS-Fastlane.gitlab-ci.yml
)
Julia (
Julia.gitlab-ci.yml
)
Laravel (
Laravel.gitlab-ci.yml
)
LaTeX (
LaTeX.gitlab-ci.yml
)
Maven (
Maven.gitlab-ci.yml
)
Mono (
Mono.gitlab-ci.yml
)
npm (
npm.gitlab-ci.yml
)
Node.js (
Nodejs.gitlab-ci.yml
)
OpenShift (
OpenShift.gitlab-ci.yml
)
Packer (
Packer.gitlab-ci.yml
)
PHP (
PHP.gitlab-ci.yml
)
Python (
Python.gitlab-ci.yml
)
Ruby (
Ruby.gitlab-ci.yml
)
Rust (
Rust.gitlab-ci.yml
)
Scala (
Scala.gitlab-ci.yml
)
Swift (
Swift.gitlab-ci.yml
)
Terraform (
Terraform.gitlab-ci.yml
)
Terraform (
Terraform.latest.gitlab-ci.yml
)
If a programming language or framework template is not in this list, you can contribute
one. To create a template, submit a merge request
to
the templates list
.
Adding templates to your GitLab installation
Tier
: Premium, Ultimate
Offering
: GitLab Self-Managed, GitLab Dedicated
You can add custom examples and templates to your instance.
Your GitLab administrator can
designate an instance template repository
that contains examples and templates specific to your organization.
Other resources
This section provides further resources to help you get familiar with various uses of GitLab CI/CD.
Older articles and videos may not reflect the state of the latest GitLab release.
CI/CD in the cloud
For examples of setting up GitLab CI/CD for cloud-based environments, see:
How to set up multi-account AWS SAM deployments with GitLab CI/CD
Video:
Automating Kubernetes Deployments with GitLab CI/CD
How to autoscale continuous deployment with GitLab Runner on DigitalOcean
How to create a CI/CD pipeline with Auto Deploy to Kubernetes using GitLab and Helm
Video:
Demo - Deploying from GitLab to OpenShift Container Cluster
Tutorial:
Set up a GitLab.com Civo Kubernetes integration with Gitpod
See also the following video overviews:
Video:
Kubernetes, GitLab, and Cloud Native
Video:
Deploying to IBM Cloud with GitLab CI/CD
Customer stories
For some customer experiences with GitLab CI/CD, see:
How Verizon Connect reduced data center deploys from 30 days to under 8 hours with GitLab
How Wag! cut their release process from 40 minutes to just 6
How Jaguar Land Rover embraced CI to speed up their software lifecycle
Getting started
For some examples to help get you started, see:
GitLab CI/CD’s 2018 highlights
A beginner’s guide to continuous integration
Implementing GitLab CI/CD
For examples of others who have implemented GitLab CI/CD, see:
How to streamline interactions between multiple repositories with multi-project pipelines
How we used GitLab CI to build GitLab faster
Test all the things in GitLab CI with Docker by example
A Craftsman looks at continuous integration
Go tools and GitLab: How to do continuous integration like a boss
GitBot - automating boring Git operations with CI
How to use GitLab CI for Vue.js
Video:
GitLab CI/CD Deep Dive
Dockerizing GitLab review apps
Fast and natural continuous integration with GitLab CI
Demo: CI/CD with GitLab in action
Migrating to GitLab from third-party CI tools
Examples of migration to GitLab CI/CD from other tools:
Bamboo
CircleCI
GitHub Actions
Jenkins
TeamCity
Integrating GitLab CI/CD with other systems
To see how you can integrate GitLab CI/CD with third-party systems, see:
Streamline and shorten error remediation with Sentry’s new GitLab integration
How to simplify your smart home configuration with GitLab CI/CD
Demo: GitLab + Jira + Jenkins
Introducing Auto Breakfast from GitLab (sort of)
Mobile development
For help with using GitLab CI/CD for mobile application development, see:
How to publish Android apps to the Google Play Store with GitLab and fastlane
Setting up GitLab CI for Android projects
Working with YAML in GitLab CI from the Android perspective
How to use GitLab CI and MacStadium to build your macOS or iOS projects
Setting up GitLab CI for iOS projects
