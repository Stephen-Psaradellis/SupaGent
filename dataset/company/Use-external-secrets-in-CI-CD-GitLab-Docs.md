# Use external secrets in CI/CD | GitLab Docs

Source: https://docs.gitlab.com/ci/secrets/

Use external secrets in CI/CD | GitLab Docs
Use external secrets in CI/CD
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
CI/CD jobs might need sensitive information, called secrets, to complete work.
This sensitive information could be items like API tokens, database credentials, or private keys.
Secrets are sourced from a secrets provider.
Unlike CI/CD variables which are always available in jobs, secrets must be explicitly
requested by a job.
GitLab supports several secret management providers, including:
HashiCorp Vault
Google Cloud Secret Manager
Azure Key Vault
AWS Secrets Manager
These integrations use
ID tokens
for authentication.
You can also use ID tokens to manually authenticate with any secrets provider that supports
OIDC authentication with JSON web tokens (JWT).
