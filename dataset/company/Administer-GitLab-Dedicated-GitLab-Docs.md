# Administer GitLab Dedicated | GitLab Docs

Source: https://docs.gitlab.com/administration/dedicated/

Administer GitLab Dedicated | GitLab Docs
Administer GitLab Dedicated
Tier
: Ultimate
Offering
: GitLab Dedicated
Use GitLab Dedicated to run GitLab on a fully-managed, single-tenant instance hosted on AWS. You maintain control over your instance configuration through Switchboard, the GitLab Dedicated management portal, while GitLab manages the underlying infrastructure.
For more information about this offering, see the
subscription page
.
Architecture overview
GitLab Dedicated runs on a secure infrastructure that provides:
A fully isolated tenant environment in AWS
High availability with automated failover
Geo-based disaster recovery
Regular updates and maintenance
Enterprise-grade security controls
To learn more, see
GitLab Dedicated architecture
.
Configure infrastructure
Feature
Description
Set up with
Instance sizing
You select an instance size based on your user count. GitLab provisions and maintains the infrastructure.
Onboarding
AWS data regions
You choose regions for primary operations, disaster recovery, and backup. GitLab replicates your data across these regions.
Onboarding
Maintenance windows
You select a weekly 4-hour maintenance window. GitLab performs updates, configuration changes, and security patches during this time.
Onboarding
Release management
GitLab updates your instance monthly with new features and security patches.
Available by
default
Geo disaster recovery
You choose the secondary region during onboarding. GitLab maintains a replicated secondary site in your chosen region using Geo.
Onboarding
Automated backups
GitLab backs up your data to your chosen AWS region.
Available by
default
Secure your instance
Feature
Description
Set up with
Data encryption
GitLab encrypts your data both at rest and in transit through infrastructure provided by AWS.
Available by
default
Bring your own key (BYOK)
You can provide your own AWS KMS keys for encryption instead of using GitLab-managed AWS KMS keys. GitLab integrates these keys with your instance to encrypt data at rest.
Onboarding
SAML SSO
You configure the connection to your SAML identity providers. GitLab handles the authentication flow.
Switchboard
IP allowlists
You specify approved IP addresses. GitLab blocks unauthorized access attempts.
Switchboard
Custom certificates
You import your SSL certificates. GitLab maintains secure connections to your private services.
Switchboard
Compliance frameworks
GitLab maintains compliance with SOC 2, ISO 27001, and other frameworks. You can access reports through the
Trust Center
.
Available by
default
Emergency access protocols
GitLab provides controlled break-glass procedures for urgent situations.
Available by
default
Set up networking
Feature
Description
Set up with
Custom hostname (BYOD)
You provide a domain name and configure DNS records. GitLab manages SSL certificates through Let’s Encrypt.
Support ticket
Inbound private link
GitLab creates an endpoint service. You create VPC endpoints in your AWS account to connect to your GitLab instance.
Switchboard
Outbound private link
You create an endpoint service in your AWS account. GitLab creates VPC endpoints to connect to your services.
Switchboard
Private hosted zones
You define internal DNS requirements. GitLab configures DNS resolution in your instance network.
Switchboard
Use platform tools
Feature
Description
Set up with
GitLab Pages
GitLab hosts your static websites on a dedicated domain. You can publish sites from your repositories.
Available by
default
Advanced search
GitLab maintains the search infrastructure. You can search across your code, issues, and merge requests.
Available by
default
Hosted runners (beta)
You purchase a subscription and configure your hosted runners. GitLab manages the auto-scaling CI/CD infrastructure.
Switchboard
ClickHouse
GitLab maintains the ClickHouse infrastructure and integration. You can access all advanced analytical features such as
GitLab Duo and SDLC trends
and
CI analytics
.
Available by
default for
eligible customers
Manage daily operations
Feature
Description
Set up with
Application logs
GitLab delivers logs to your AWS S3 bucket. You can request access to monitor instance activity through these logs.
Support ticket
Email service
GitLab provides AWS SES by default to send emails from your GitLab Dedicated instance. You can also configure your own SMTP email service.
Support ticket for
custom service
Switchboard access and
notifications
You manage Switchboard permissions and notification settings. GitLab maintains the Switchboard infrastructure.
Switchboard
Switchboard SSO
You configure your organization’s identity provider and supply GitLab with the necessary details. GitLab configures single-sign-on (SSO) for Switchboard.
Support ticket
Get started
To get started with GitLab Dedicated:
Create your GitLab Dedicated instance
.
Configure your GitLab Dedicated instance
.
Create a hosted runner
.
