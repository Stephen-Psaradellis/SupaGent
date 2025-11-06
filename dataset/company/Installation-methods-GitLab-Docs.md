# Installation methods | GitLab Docs

Source: https://docs.gitlab.com/install/install_methods/

Installation methods | GitLab Docs
Installation methods
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
You can install GitLab on several
cloud providers
,
or use one of the following methods.
Linux package
The Linux package includes the official
deb
and
rpm
packages. The package has GitLab and dependent components, including PostgreSQL, Redis, and Sidekiq.
Use if you want the most mature, scalable method. This version is also used on GitLab.com.
For more information, see:
Linux package
Reference architectures
System requirements
Supported Linux operating systems
Helm chart
Use a chart to install a cloud-native version of GitLab and its components on Kubernetes.
Use if your infrastructure is on Kubernetes and you’re familiar with how it works.
Before you use this installation method, consider that:
Management, observability, and some other concepts are different than traditional deployments.
Administration and troubleshooting requires Kubernetes knowledge.
It can be more expensive for smaller installations.
The default installation requires more resources than a single node Linux package deployment, because most services are deployed in a redundant fashion.
For more information, see
Helm charts
.
GitLab Operator
To install a cloud-native version of GitLab and its components in Kubernetes, use GitLab Operator.
This installation and management method follows the
Kubernetes Operator pattern
.
Use if your infrastructure is on Kubernetes or
OpenShift
, and you’re familiar with how Operators work.
This installation method provides additional functionality beyond the Helm chart installation method, including automation of the
GitLab upgrade steps
. The considerations for the Helm chart also apply here.
Consider the Helm chart installation method if you are limited by
GitLab Operator known issues
.
For more information, see
GitLab Operator
.
Docker
Installs the GitLab packages in a Docker container.
Use if you’re familiar with Docker.
For more information, see
Docker
.
Self-compiled
Installs GitLab and its components from scratch.
Use if none of the previous methods are available for your platform. Can use for unsupported systems like *BSD.
For more information, see
self-compiled installation
.
GitLab Environment Toolkit (GET)
GitLab Environment Toolkit (GET)
is a set of opinionated Terraform and Ansible scripts.
Use to deploy a
reference architecture
on selected major cloud providers.
This installation methods has some
limitations
, and requires manual setup for production environments.
Unsupported Linux distributions and Unix-like operating systems
Self-compiled installation
of GitLab on the following operating systems is possible, but not supported:
Arch Linux
FreeBSD
Gentoo
macOS
Microsoft Windows
GitLab is developed for Linux-based operating systems.
It does not run on Microsoft Windows, and there are no plans to support it in the near future. For the latest development status, see
issue 22337
.
Consider using a virtual machine to run GitLab.
