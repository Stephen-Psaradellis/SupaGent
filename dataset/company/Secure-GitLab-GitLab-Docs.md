# Secure GitLab | GitLab Docs

Source: https://docs.gitlab.com/security/

Secure GitLab | GitLab Docs
Secure GitLab
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
General information
This section covers general information and recommendations about the platform.
Password and OAuth token storage
Password generation for users created through integrated authentication
CRIME vulnerability management
Secret rotation for third-party integrations
Recommendations
For more information about improving the security posture of your GitLab environment, see the
hardening recommendations
.
Antivirus software
Generally, running an antivirus software on the GitLab host is not recommended.
However, if you must use one, all of the location of GitLab on the system should be excluded from scanning as it could be quarantined as a false positive.
Specifically, you should exclude the following GitLab directories from scanning:
/var/opt/gitlab
/etc/gitlab/
/var/log/gitlab/
/opt/gitlab/
You can find all those directories listed in the
Linux package configuration documentation
.
User accounts
Review authentication options
.
Configure password length limits
.
Restrict SSH key technologies and require minimum key lengths
.
Restrict account creation with sign up restrictions
.
Send email confirmation on sign-up
Enforce two-factor authentication
to require users to
enable two-factor authentication
.
Restrict logins from multiple IPs
.
How to reset a user password
.
How to unlock a locked user
.
Data access
Security considerations for project membership
.
Protecting and removing user file uploads
.
Proxying linked images for user privacy
.
Platform usage and settings
Review GitLab token type and usages
.
How to configure rate limits improve security and availability
.
How to filter outbound webhook requests
.
How to configure import and export limits and timeouts
.
Review Runner security considerations and recommendations
.
Review CI/CD variables security considerations
.
Review pipeline security for usage and protection of secrets in CI/CD Pipelines
.
Instance-wide compliance and security policy management
.
Patching
GitLab Self-Managed customers and administrators are responsible for the security of their underlying hosts, and for keeping GitLab itself up to date. It is important to
regularly patch GitLab
, patch your operating system and its software, and harden your hosts in accordance with vendor guidance.
Monitoring
Logs
Review the log types and contents produced by GitLab
.
Review Runner job logs information
.
How to use correlation ID to trace logs
.
Logging configuration and access
.
How to configure audit event streaming
.
Response
Responding to security incidents
.
Rate limits
For information about rate limits, see
Rate limits
.
