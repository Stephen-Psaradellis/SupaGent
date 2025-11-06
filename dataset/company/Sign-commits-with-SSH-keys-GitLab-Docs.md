# Sign commits with SSH keys | GitLab Docs

Source: https://docs.gitlab.com/user/project/repository/signed_commits/ssh/#signed-commits-with-removed-ssh-keys

Sign commits with SSH keys | GitLab Docs
Sign commits with SSH keys
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
When you sign commits with SSH keys, GitLab uses the SSH public keys associated
with your GitLab account to cryptographically verify the commit signature.
If successful, GitLab displays a
Verified
label on the commit.
You may use the same SSH keys for
git+ssh
authentication to GitLab
and signing commit signatures as long as their usage type is
Authentication & Signing
.
It can be verified on the page for
adding an SSH key to your GitLab account
.
For more information about managing the SSH keys associated with your GitLab account, see
Use SSH keys to communicate with GitLab
.
Configure Git to sign commits with your SSH key
After you
create an SSH key
and
add it to your GitLab account
configure Git to begin using the key.
Prerequisites:
Git 2.34.0 or later.
OpenSSH 8.1 or later.
OpenSSH 8.7 has broken signing functionality. If you are on OpenSSH 8.7, upgrade to OpenSSH 8.8.
An SSH key with the
Usage type
Authentication & Signing
or
Signing
.
The following SSH key types are supported:
ED25519
RSA
ECDSA
To configure Git to use your key:
Configure Git to use SSH for commit signing:
git config --global gpg.format ssh
Specify which public SSH key to use as the signing key and change the filename (
~/.ssh/examplekey.pub
) to the location of your key. The filename might
differ, depending on how you generated your key:
git config --global user.signingkey ~/.ssh/examplekey.pub
Sign commits with your SSH key
Prerequisites:
You’ve
created an SSH key
.
You’ve
added the key
to your GitLab account.
You’ve
configured Git to sign commits
with your SSH key.
To sign a commit:
Use the
-S
flag when signing your commits:
git commit -S -m
"My commit msg"
Optional. If you don’t want to type the
-S
flag every time you commit, tell
Git to sign your commits automatically:
git config --global commit.gpgsign true
If your SSH key is protected, Git prompts you to enter your passphrase.
Push to GitLab.
Check that your commits
are verified
.
Signature verification uses the
allowed_signers
file to associate emails and SSH keys.
For help configuring this file, read
Verify commits locally
.
Verify commits
You can verify all types of signed commits
in the GitLab UI
. Commits signed
with an SSH key can also be verified locally.
Verify commits locally
To verify commits locally, create an
allowed signers file
for Git to associate SSH public keys with users:
Create an allowed signers file:
touch allowed_signers
Configure the
allowed_signers
file in Git:
git config gpg.ssh.allowedSignersFile
"
$(
pwd
)
/allowed_signers"
Add your entry to the allowed signers file. Use this command to add your
email address and public SSH key to the
allowed_signers
file. Replace
<MY_KEY>
with the name of your key, and
~/.ssh/allowed_signers
with the location of your project’s
allowed_signers
file:
# Modify this line to meet your needs.
# Declaring the `git` namespace helps prevent cross-protocol attacks.
echo
"
$(
git config --get user.email
)
namespaces=\"git\"
$(
cat ~/.ssh/<MY_KEY>.pub
)
"
>> ~/.ssh/allowed_signers
The resulting entry in the
allowed_signers
file contains your email address, key type,
and key contents, like this:
example@gitlab.com namespaces="git" ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAmaTS47vRmsKyLyK1jlIFJn/i8wdGQ3J49LYyIYJ2hv
Repeat the previous step for each user who you want to verify signatures for.
Consider checking this file in to your Git repository if you want to locally
verify signatures for many different contributors.
Use
git log --show-signature
to view the signature status for the commits:
$ git log --show-signature
commit e2406b6cd8ebe146835ceab67ff4a5a116e09154
(
HEAD -> main, origin/main, origin/HEAD
)
Good
"git"
signature
for
johndoe@example.com with ED25519 key SHA256:Ar44iySGgxic+U6Dph4Z9Rp+KDaix5SFGFawovZLAcc
Author: John Doe <johndoe@example.com>
Date: Tue Nov
29
06:54:15
2022
-0600
SSH signed commit
Signed commits with removed SSH keys
You can revoke or delete your SSH keys used to sign commits. For more information see
Remove an SSH key
.
Removing your SSH key can impact any commits signed with the key:
Revoking your SSH key marks your previous commits as
Unverified
. Until you add a new SSH key, any new commits are also marked as
Unverified
.
Deleting your SSH key doesn’t impact your previous commits. Until you add a new SSH key, any new commits are marked as
Unverified
.
Related topics
Sign commits and tags with X.509 certificates
Sign commits with GPG
Commits API
