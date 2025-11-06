# GitLab Operator | GitLab Docs

Source: https://docs.gitlab.com/operator/

GitLab Operator | GitLab Docs
GitLab Operator
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
The
GitLab Operator
is an installation and management method that follows the
Kubernetes Operator pattern
.
Use the GitLab Operator to run GitLab in
OpenShift
or on
another Kubernetes-compatible platform.
The GitLab Operator has
known limitations
and is only suitable for specific scenarios in production use.
The default values of the GitLab custom resource are
not intended for production use
.
With these values, GitLab Operator creates a GitLab instance where all services, including the persistent data,
are deployed in a Kubernetes cluster, which is
not suitable for production workloads
.
For production deployments, you
must
follow the
Cloud Native Hybrid reference architectures
.
GitLab does not support any issues related to PostgreSQL, Redis, Gitaly, Praefect, or MinIO deployed inside of a Kubernetes Cluster.
Known issues
GitLab Operator does not support:
Managing existing Helm chart-based instances with GitLab Operator. Support for improvements is proposed in
GitLab Operator issue 1567
.
Git over SSH with
OpenShift routes
.
For more information, see
GitLab Operator documentation on OpenShift Routes
.
GKE workload identity
and
IAM service accounts
to authenticate workloads to other cloud APIs (such as object storage).
For more information, see
GitLab Operator issue 1089
.
GitLab Operator has any other limitation of GitLab Chart. GitLab Operator relies on GitLab Chart to provision Kubernetes resources. Therefore, any limitation
in GitLab Chart impacts GitLab Operator. Removing the GitLab Chart dependency from GitLab Operator is proposed in
Cloud Native epic 64
.
Installation
Instructions on how to install the GitLab Operator can be found in our
installation document
.
We list details of how we use
Security Context Constraints
in their respective document.
You should also be aware of the
considerations for SSH access to Git
, especially
when using OpenShift.
Upgrading
Operator upgrades
documentation demonstrates how to upgrade the GitLab Operator.
GitLab upgrades
documentation demonstrates how to upgrade a GitLab instance, managed by the GitLab Operator.
Backup and restore
Backup and restore
documentation demonstrates how to back up and restore a GitLab instance that is managed by the Operator.
Using RedHat certified images
RedHat certified images
documentation demonstrates how to instruct the GitLab Operator
to deploy images that have been certified by RedHat.
Developer Tooling
Developer guide
: Outlines the project structure and how to contribute.
Versioning and Release Info
: Records notes concerning versioning and releasing the operator.
Design decisions
: This projects makes use of Architecture Decision Records, detailing the structure, functionality, and feature implementation of this Operator.
Merge request reviews
Merge requests (MRs) usually follow our standard practice of requiring 2 reviewers. First, a non-maintainer
review the MR and provides comments to the author to help improve/fix the change being proposed. After
the author makes the necessary updates and the reviewer approves the MR, we request a review from one
of the maintainers.
This approach not only provides learning opportunities for reviewers with less experience,
This approach provides learning opportunities for reviewers with less experience. The
first review addresses most problems with an MR prior to the final review. High
volume projects often experience bottlenecks due to maintainer load and this first pass
helps reduce their load.
One approval only exceptions
In certain cases we allow MRs to be merged with only one approval.
Go modules updates
Note:
This is only relevant to GitLab team members of the group which owns this project.
If you are a team member of the team owning this project, you were given CODEOWNERS approval rights over the
go.mod
and
go.sum
files. If the MR is only changing these files, you should be able to approve the MR
and merge it, even if you’re not a maintainer. This was implemented to reduce the review load from maintainers
and improve dependency update efficiency, given that the team assessed that updates to go modules are very
low risk. So, if you’re comfortable with Go, the change looks good to you, and you have a full green
pipeline on the MR, feel free to approve and merge right away.
Still, if you’re not comfortable with Go code, or for any other reason you would like a second opinion,
you’re also encouraged to pass the MR to a maintainer to run a second review.
