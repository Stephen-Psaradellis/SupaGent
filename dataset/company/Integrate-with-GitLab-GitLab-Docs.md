# Integrate with GitLab | GitLab Docs

Source: https://docs.gitlab.com/integration/

Integrate with GitLab | GitLab Docs
Integrate with GitLab
You can integrate GitLab with external applications for enhanced functionality.
Project integrations
Applications like Jenkins, Jira, and Slack are available as
project integrations
.
Issue trackers
You can configure an
external issue tracker
and use:
The external issue tracker with the GitLab issue tracker
The external issue tracker only
Authentication providers
You can integrate GitLab with authentication providers like LDAP and SAML.
For more information, see
GitLab authentication and authorization
.
Security improvements
Solutions like Akismet and reCAPTCHA are available for spam protection.
You can also integrate GitLab with the following security partners:
Anchore
Prisma Cloud
Checkmarx
CodeSecure
Deepfactor
Fortify
Indeni
Jscrambler
Mend
Semgrep
StackHawk
Tenable
Venafi
Veracode
GitLab can check your application for security vulnerabilities.
For more information, see
Secure your application
.
Troubleshooting
When working with integrations, you might encounter the following issues.
SSL certificate errors
When you use a self-signed certificate to integrate GitLab with external applications, you might
encounter SSL certificate errors in different parts of GitLab.
As a workaround, do one of the following:
Add the certificate to the OS trusted chain. For more information, see:
Adding trusted root certificates to the server
How do you add a certificate authority (CA) to Ubuntu?
For installations that use the Linux package, add the certificate to the GitLab trusted chain:
Install the self-signed certificate
.
Concatenate the self-signed certificate with the GitLab trusted certificate.
The self-signed certificate might be overwritten during upgrades.
cat jira.pem >> /opt/gitlab/embedded/ssl/certs/cacert.pem
Restart GitLab.
sudo gitlab-ctl restart
Search Sidekiq logs in Kibana
To locate a specific integration in Kibana, use the following KQL search string:
`json.integration_class.keyword : "Integrations::Jira" and json.project_path : "path/to/project"`
You can find information in:
json.exception.backtrace
json.exception.class
json.exception.message
json.message
Error:
Test Failed. Save Anyway
When you configure an integration on an uninitialized repository, the integration might fail with
a
Test Failed. Save Anyway
error. This error occurs because the integration uses push data
to build the test payload when the project does not have push events.
To resolve this issue, initialize the repository by pushing a test file to the project
and configure the integration again.
