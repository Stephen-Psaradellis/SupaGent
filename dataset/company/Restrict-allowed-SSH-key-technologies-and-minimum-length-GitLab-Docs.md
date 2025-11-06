# Restrict allowed SSH key technologies and minimum length | GitLab Docs

Source: https://docs.gitlab.com/security/ssh_keys_restrictions/

Restrict allowed SSH key technologies and minimum length | GitLab Docs
Restrict allowed SSH key technologies and minimum length
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed, GitLab Dedicated
ssh-keygen
allows users to create RSA keys with as few as 768 bits, which
falls well below recommendations from certain standards groups (such as the US
NIST). Some organizations deploying GitLab need to enforce minimum key
strength, either to satisfy internal security policy or for regulatory
compliance.
Similarly, certain standards groups recommend using RSA, ECDSA, ED25519,
ECDSA_SK, or ED25519_SK over the older DSA, and administrators may need to
limit the allowed SSH key algorithms.
GitLab allows you to restrict the allowed SSH key technology as well as specify
the minimum key length for each technology:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Settings
>
General
.
Expand
Visibility and access controls
and set your desired values for each key type:
RSA SSH keys
.
DSA SSH keys
.
ECDSA SSH keys
.
ED25519 SSH keys
.
ECDSA_SK SSH keys
.
ED25519_SK SSH keys
.
Select
Save changes
.
If a restriction is imposed on any key type, users cannot upload new SSH keys that don’t meet the
requirement. Any existing keys that don’t meet it are disabled but not removed and users cannot
pull or push code using them.
If you have a restricted key, a warning icon (
warning
) is visible to you in the
SSH keys
section of your profile.
To learn why that key is restricted, hover over the icon.
Default settings
By default, the GitLab.com and GitLab Self-Managed settings for the
supported key types
are:
DSA SSH keys are forbidden.
RSA SSH keys are allowed.
ECDSA SSH keys are allowed.
ED25519 SSH keys are allowed.
ECDSA_SK SSH keys are allowed.
ED25519_SK SSH keys are allowed.
Block banned or compromised keys
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab 15.1
with a flag
named
ssh_banned_key
. Enabled by default.
Generally available in GitLab 15.2.
Feature flag
ssh_banned_key
removed.
When users attempt to
add a new SSH key
to GitLab accounts, the key is checked against a list of SSH keys which are known
to be compromised. Users can’t add keys from this list to any GitLab account.
This restriction cannot be configured. This restriction exists because the private
keys associated with the key pair are publicly known, and can be used to access
accounts using the key pair.
If your key is disallowed by this restriction,
generate a new SSH key pair
to use instead.
