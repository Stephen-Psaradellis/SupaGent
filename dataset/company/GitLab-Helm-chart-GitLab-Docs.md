# GitLab Helm chart | GitLab Docs

Source: https://docs.gitlab.com/charts/

GitLab Helm chart | GitLab Docs
GitLab Helm chart
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
To install a cloud-native version of GitLab, use the GitLab Helm chart.
This chart contains all the required components to get started and can scale to large deployments.
For OpenShift-based installations, use
GitLab Operator
,
otherwise you must update the
security context constraints
yourself.
The default Helm chart configuration is
not intended for production
.
The default values create an implementation where
all
GitLab services are
deployed in the cluster, which is
not suitable for production workloads
.
For production deployments, you
must
follow the
Cloud Native Hybrid reference architectures
.
For a production deployment, you should have strong working knowledge of Kubernetes.
This method of deployment has different management, observability, and concepts than traditional deployments.
The GitLab Helm chart is made up of multiple
subcharts
,
each of which can be installed separately.
Learn more
Test the GitLab chart on GKE or EKS
Migrate from using the Linux package to the GitLab chart
Prepare to deploy
Deploy
View deployment options
Configure globals
View the subcharts
View advanced configuration options
View architectural decisions
Contribute to development by viewing the
developer documentation
and
contribution guidelines
Create an
issue
Create a
merge request
View
troubleshooting
information
