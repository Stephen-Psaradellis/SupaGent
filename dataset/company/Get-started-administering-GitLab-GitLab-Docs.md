# Get started administering GitLab | GitLab Docs

Source: https://docs.gitlab.com/administration/get_started/

Get started administering GitLab | GitLab Docs
Get started administering GitLab
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
Get started with GitLab administration. Configure your organization and its authentication, then secure, monitor,
and back up GitLab.
Authentication
Authentication is the first step in making your installation secure.
Enforce two-factor authentication (2FA) for all users
. You should use 2FA for GitLab Self-Managed instances.
Ensure users do the following:
Choose a strong, secure password. If possible, store it in a password management system.
If it is not configured for everyone, turn on
two-factor authentication (2FA)
for your account.
This one-time secret code is an additional safeguard that keeps intruders out, even if they have your password.
Add a backup email. If you lose access to your account, the GitLab Support team can help you more quickly.
Save or print your recovery codes. If you can’t access your authentication device, you can use these recovery codes to sign in to your GitLab account.
Add
an SSH key
to your profile. You can generate recovery codes as needed with SSH.
Create
personal access tokens
. When you use 2FA, you can use these tokens to access the GitLab API.
Projects and groups
Organize your environment by configuring your groups and projects.
Projects
: Designate a home for your files and code or track and organize issues in a business category.
Groups
: Organize a collection of users or projects. Use these groups to quickly assign people and projects.
Roles
: Define user access and visibility for your projects and groups.
Watch an overview of
groups and projects
.
Get started:
Create a
project
.
Create a
group
.
Add members
to the group.
Create a
subgroup
.
Add members
to the subgroup.
Turn on
external authorization control
.
More resources
Run multiple Agile teams
.
Sync group memberships by using LDAP
.
Manage user access with inherited permissions. Use up to 20 levels of subgroups to organize both teams and projects.
Inherited membership
.
Example
.
Import projects
You might have to import projects from external sources like GitHub, Bitbucket, or another instance of GitLab. Many external sources can be imported into GitLab.
Review the
GitLab projects documentation
.
Consider
Repository Mirroring
, an
alternative to project migrations
.
Check out our
migration index
for documentation on common migration paths.
Schedule your project exports with our
import/export API
.
Popular project imports
GitHub Enterprise to GitLab Self-Managed
Bitbucket Server
For assistance with these data types, contact your GitLab account manager or GitLab Support about our professional migration services.
GitLab instance security
Security is an important part of the onboarding process. Securing your instance protects your work and your organization.
While this isn’t an exhaustive list, following these steps gives you a solid start for securing your instance.
Use a long root password, stored in a vault.
Install trusted SSL certificate and establish a process for renewal and revocation.
Configure SSH key restrictions
according to your organization’s guidelines.
Turn off new sign-ups
.
Require email confirmation.
Set password length limit, configure SSO or SAML user management.
Limit email domains if allowing sign-up.
Require two-factor authentication (2FA).
Turn off password authentication
for Git over HTTPS.
Set up
email notification for unknown sign-ins
.
Configure
user and IP rate limits
.
Limit
webhooks local access
.
Set
rate limits for protected paths
.
Subscribe to
Security Alerts
from the Communication Preference Center.
Keep track of security best practices on our
blog page
.
Monitor GitLab performance
After you’ve established your basic setup, you’re ready to review the GitLab monitoring services. Prometheus is our core performance monitoring tool.
Unlike other monitoring solutions (for example, Zabbix or New Relic), Prometheus is tightly integrated with GitLab and has extensive community support.
Prometheus
captures
these GitLab metrics
.
Learn more about GitLab
bundled software metrics
.
Prometheus and its exporters are on by default. However, you must
configure the service
.
Find out why
application performance metrics
matter.
Integrate Grafana to
build visual dashboards
based on performance metrics.
Components of monitoring
Web servers
: Handles server requests and facilitates other back-end service transactions.
Monitor CPU, memory, and network IO traffic to track the health of this node.
Workhorse
: Alleviates web traffic congestion from the main server.
Monitor latency spikes to track the health of this node.
Sidekiq
: Handles background operations that allow GitLab to run smoothly.
Monitor for long, unprocessed task queues to track the health of this node.
Back up your GitLab data
GitLab provides backup methods to keep your data safe and recoverable. Whether you use a GitLab Self-Managed or a GitLab.com database, it’s crucial to back up your data regularly.
Decide on a backup strategy.
Consider writing a cron job to make daily backups.
Separately backup the configuration files.
Decide what should be left out of the backup.
Decide where to upload the backups.
Limit backup lifetime.
Run a test backup and restore.
Set up a way to periodically verify the backups.
Back up an instance
The routine differs, depending on whether you deployed with the Linux package or the Helm chart.
To back up a single-node installation that uses the Linux package, you can use a single Rake task.
Learn about
backing up Linux package or Helm variations
.
This process backs up your entire instance, but does not back up the configuration files. Ensure those are backed up separately.
Keep your configuration files and backup archives in a separate location to ensure the encryption keys are not kept with the encrypted data.
Restore a backup
You can restore a backup only to
the exact same version and type
(Community Edition/Enterprise Edition) of GitLab on which it was created.
Review the
Linux package (Omnibus) backup and restore documentation
.
Review the
Helm Chart backup and restore documentation
.
Back up GitLab SaaS
Backups of our production databases are taken hourly through
disk snapshots
and every
24 hours through
wal-g base backups
, with
continuous archiving or WAL transaction log files
streamed into GCS for point-in-time recovery.
All backups are encrypted. After 90 days, backups are deleted.
GitLab SaaS creates backups to ensure your data is secure, but you can’t use these methods to export or back up your data yourself.
Issues are stored in the database. They can’t be stored in Git itself.
You can use the project export option in:
The UI
.
The API
.
Group export by uploading a file export
does
not
export the projects in it, but does export:
Epics
Milestones
Boards
Labels
Additional items
You should not use
direct transfer
or
project export files
to back up your data.
Project export files do not always work for data backups, and not all items are exported.
Alternative backup strategies
In some situations the Rake task for backups might not be the most optimal solution. Here are some
alternatives
to consider if the Rake task does not work for you.
Option 1: File system snapshot
If your GitLab server contains a lot of Git repository data, you might find the GitLab backup script to be too slow. It can be especially slow when backing up to an offsite location.
Slowness typically starts at a Git repository data size of around 200 GB. In this case, you might consider using file system snapshots as part of your backup strategy.
For example, consider a GitLab server with the following components:
Using the Linux package.
Hosted on AWS with an EBS drive containing an ext4 file system mounted at
/var/opt/gitlab
.
The EC2 instance meets the requirements for an application data backup by taking an EBS snapshot. The backup includes all repositories, uploads, and PostgreSQL data.
If you’re running GitLab on a virtualized server, you can create VM snapshots of the entire GitLab server.
It is common for a VM snapshot to require you to power down the server.
Option 2: GitLab Geo
Tier
: Premium, Ultimate
Offering
: GitLab Self-Managed
Geo provides local, read-only instances of your GitLab instances.
While GitLab Geo helps remote teams work more efficiently by using a local GitLab node, it can also be used as a disaster recovery solution.
Learn more about using
Geo as a disaster recovery solution
.
Geo replicates your database, your Git repositories, and a few other assets.
Learn more about the
data types Geo replicates
.
Support for GitLab Self-Managed
GitLab provides support for GitLab Self-Managed through different channels.
Priority support:
Premium and Ultimate
GitLab Self-Managed customers receive priority support with tiered response times.
Learn more about
upgrading to priority support
.
Live upgrade assistance: Get one-on-one expert guidance during a production upgrade. With your
priority support plan
,
you’re eligible for a live, scheduled screen-sharing session with a member of our support team.
To get assistance for GitLab Self-Managed:
Use the GitLab documentation for self-service support.
Join the
GitLab Forum
for community support.
Gather
your subscription information
before submitting a ticket.
Submit a support ticket
.
Support for GitLab SaaS
GitLab SaaS has 24/7 monitoring. Our full team of site reliability and production engineers is always on.
Often, by the time you notice an issue, someone’s already looking into it.
To get assistance for GitLab SaaS:
Access
GitLab Docs
for self-service support.
Join the
GitLab Forum
for community support.
Gather
your subscription information
before submitting a ticket.
Submit a support ticket for:
General assistance
Account or sign-in issues
Subscribe to
the status page
for the latest on GitLab performance or service interruptions.
API and rate limits for GitLab Self-Managed
Rate limits prevent denial-of-service or brute-force attacks. In most cases, you can reduce the load on your application
and infrastructure by limiting the rate of requests from a single IP address.
Rate limits also improve the security of your application.
Configure rate limits for GitLab Self-Managed
You can make changes to your default rate limits from the
Admin
area. For more information about configuration, see the
Admin
area page
.
Define
issues rate limits
to set a maximum number of issue creation requests per minute, per user.
Enforce
user and IP rate limits
for unauthenticated web requests.
Review the
rate limit on raw endpoints
. The default setting is 300 requests per minute for raw file access.
Review the
import/export rate limits
of the six active defaults.
For more information about API and rate limits, see our
API page
.
API and rate limits for GitLab SaaS
Rate limits prevent denial-of-service or brute-force attacks. IP blocks usually happen when GitLab.com receives unusual traffic
from a single IP address. The system views unusual traffic as potentially malicious based on rate limit settings.
Rate limits also improve the security of your application.
Configure rate limits for GitLab SaaS
You can make changes to your default rate limits from the
Admin
area. For more information about configuration, see the
Admin
area page
.
Review the rate limit page.
Read our
API page
for more information about API and rate limiting.
GitLab SaaS-specific block and error responses
403 forbidden error
: If the error occurs for all GitLab SaaS requests, look for an automated process that could have triggered a block. For more assistance, contact GitLab support with your error details, including the affected IP address.
HAProxy API throttle
: GitLab SaaS responds with HTTP status code 429 to API requests that exceed 10 requests per second, per IP address.
Protected paths throttle
: GitLab SaaS responds with HTTP status code 429 to POST requests at protected paths that exceed 10 requests per minute, per IP address.
Git and container registry failed authentication ban
: GitLab SaaS responds with HTTP status code 403 for one hour if it receives 30 failed authentication requests in three minutes from a single IP address.
GitLab training resources
You can learn more about how to administer GitLab.
Get involved in the
GitLab Forum
to trade tips with our talented community.
Check out
our blog
for ongoing updates on:
Releases
Applications
Contributions
News
Events
Paid GitLab training
GitLab education services: Learn more about
GitLab and DevOps best practices
through our specialized training courses. See our full course catalog.
Free GitLab training
GitLab basics: Discover self-service guides on
Git and GitLab basics
.
GitLab University: Learn new GitLab skills in a structured course at
GitLab University
.
Third-party training
Udemy: For a more affordable, guided training option, consider
GitLab CI: Pipelines, CI/CD, and DevOps for Beginners
on Udemy.
LinkedIn Learning: Check out
Continuous Delivery with GitLab
on LinkedIn Learning
for another low-cost, guided training option.
