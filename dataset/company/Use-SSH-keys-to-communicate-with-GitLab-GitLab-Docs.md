# Use SSH keys to communicate with GitLab | GitLab Docs

Source: https://docs.gitlab.com/user/ssh/#use-different-keys-for-different-repositories

Use SSH keys to communicate with GitLab | GitLab Docs
Use SSH keys to communicate with GitLab
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Git is a distributed version control system, which means you can work locally,
then share or
push
your changes to a server. In this case, the server you push to is GitLab.
GitLab uses the SSH protocol to securely communicate with Git.
When you use SSH keys to authenticate to the GitLab remote server,
you don’t need to supply your username and password each time.
What are SSH keys
SSH uses two keys, a public key and a private key.
The public key can be distributed.
The private key should be protected.
It is not possible to reveal confidential data by uploading your public key. When you need to copy or upload your SSH public key, make sure you do not accidentally copy or upload your private key instead.
You can use your private key to
sign commits
,
which makes your use of GitLab and your data even more secure.
This signature then can be verified by anyone using your public key.
For details, see
Asymmetric cryptography, also known as public-key cryptography
.
Prerequisites
To use SSH to communicate with GitLab, you need:
The OpenSSH client, which comes pre-installed on GNU/Linux, macOS, and Windows 10.
SSH version 6.5 or later. Earlier versions used an MD5 signature, which is not secure.
To view the version of SSH installed on your system, run
ssh -V
.
Supported SSH key types
To communicate with GitLab, you can use the following SSH key types:
ED25519
ED25519_SK
ECDSA_SK
RSA
ECDSA (As noted in
Practical Cryptography With Go
, the security issues related to DSA also apply to ECDSA.)
Administrators can
restrict which keys are permitted and their minimum lengths
.
ED25519 SSH keys
The book
Practical Cryptography With Go
suggests that
ED25519
keys are more secure and performant than RSA keys.
OpenSSH 6.5 introduced ED25519 SSH keys in 2014, and they should be available on most
operating systems.
ED25519 keys might not be fully supported by all FIPS systems. For more information, see
issue 367429
.
ED25519_SK SSH keys
To use ED25519_SK SSH keys on GitLab, your local client and GitLab server
must have
OpenSSH 8.2
or later installed.
ECDSA_SK SSH keys
To use ECDSA_SK SSH keys on GitLab, your local client and GitLab server
must have
OpenSSH 8.2
or later installed.
RSA SSH keys
History
Maximum RSA key length
changed
in GitLab 16.3.
Available documentation suggests ED25519 is more secure than RSA.
If you use an RSA key, the US National Institute of Standards and Technology in
Publication 800-57 Part 3 (PDF)
recommends a key size of at least 2048 bits. Due to limitations in Go,
RSA keys
cannot exceed 8192 bits
.
The default key size depends on your version of
ssh-keygen
.
Review the
man
page for your installed
ssh-keygen
command for details.
See if you have an existing SSH key pair
Before you create a key pair, see if a key pair already exists.
Go to your home directory.
Go to the
.ssh/
subdirectory. If the
.ssh/
subdirectory doesn’t exist,
you are either not in the home directory, or you haven’t used
ssh
before.
In the latter case, you need to
generate an SSH key pair
.
See if a file with one of the following formats exists:
Algorithm
Public key
Private key
ED25519 (preferred)
id_ed25519.pub
id_ed25519
ED25519_SK
id_ed25519_sk.pub
id_ed25519_sk
ECDSA_SK
id_ecdsa_sk.pub
id_ecdsa_sk
RSA (at least 2048-bit key size)
id_rsa.pub
id_rsa
DSA (deprecated)
id_dsa.pub
id_dsa
ECDSA
id_ecdsa.pub
id_ecdsa
Generate an SSH key pair
If you do not have an existing SSH key pair, generate a new one:
Open a terminal.
Run
ssh-keygen -t
followed by the key type and an optional comment.
This comment is included in the
.pub
file that’s created.
You may want to use an email address for the comment.
For example, for ED25519:
ssh-keygen -t ed25519 -C
"<comment>"
For 2048-bit RSA:
ssh-keygen -t rsa -b
2048
-C
"<comment>"
Press
Enter
. Output similar to the following is displayed:
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/user/.ssh/id_ed25519):
Accept the suggested filename and directory, unless you are generating a
deploy key
or want to save in a specific directory where you store other keys.
You can also dedicate the SSH key pair to a
specific host
.
Specify a
passphrase
:
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
A confirmation is displayed, including information about where your files are stored.
A public and private key are generated.
Add the public SSH key to your GitLab account
and keep the private key secure.
Configure SSH to point to a different directory
If you did not save your SSH key pair in the default directory,
configure your SSH client to point to the directory where the private key is stored.
Open a terminal and run this command:
eval
$(
ssh-agent -s
)
ssh-add <directory to private SSH key>
Save these settings in the
~/.ssh/config
file. For example:
# GitLab.com
Host gitlab.com
PreferredAuthentications publickey
IdentityFile ~/.ssh/gitlab_com_rsa
# Private GitLab instance
Host gitlab.company.com
PreferredAuthentications publickey
IdentityFile ~/.ssh/example_com_rsa
For more information on these settings, see the
man ssh_config
page in the SSH configuration manual.
Public SSH keys must be unique to GitLab because they bind to your account.
Your SSH key is the only identifier you have when you push code with SSH.
It must uniquely map to a single user.
Add an SSH key to your GitLab account
History
Suggested default expiration date for keys
introduced
in GitLab 15.4.
Usage types for SSH keys
added
in GitLab 15.7.
To use SSH with GitLab, copy your public key to your GitLab account:
Copy the contents of your public key file. You can do this manually or use a script.
In these examples, replace
id_ed25519.pub
with your filename. For example, for RSA, use
id_rsa.pub
.
macOS
tr -d
'\n'
< ~/.ssh/id_ed25519.pub
|
pbcopy
Linux (requires the xclip package)
xclip -sel clip < ~/.ssh/id_ed25519.pub
Git Bash on Windows
cat ~/.ssh/id_ed25519.pub
|
clip
Sign in to GitLab.
On the left sidebar, select your avatar. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Edit profile
.
On the left sidebar, select
SSH Keys
.
Select
Add new key
.
In the
Key
box, paste the contents of your public key.
If you manually copied the key, make sure you copy the entire key,
which starts with
ssh-rsa
,
ssh-dss
,
ecdsa-sha2-nistp256
,
ecdsa-sha2-nistp384
,
ecdsa-sha2-nistp521
,
ssh-ed25519
,
sk-ecdsa-sha2-nistp256@openssh.com
, or
sk-ssh-ed25519@openssh.com
, and may end with a comment.
In the
Title
box, type a description, like
Work Laptop
or
Home Workstation
.
Optional. Select the
Usage type
of the key. It can be used either for
Authentication
or
Signing
or both.
Authentication & Signing
is the default value.
Optional. Update
Expiration date
to modify the default expiration date. For more information, see
SSH key expiration
.
Select
Add key
.
Verify that you can connect
Verify that your SSH key was added correctly.
To ensure you connect to the correct server, identify the SSH host key fingerprint. For:
GitLab.com, see the
SSH host keys fingerprints
documentation.
GitLab Self-Managed or GitLab Dedicated, see
https://gitlab.example.com/help/instance_configuration#ssh-host-keys-fingerprints
where
gitlab.example.com
is the GitLab instance URL.
Open a terminal and run this command. Replace
gitlab.example.com
with your
GitLab instance URL:
ssh -T git@gitlab.example.com
By default, connections use the
git
username, but administrators can
change the username
.
On your first connection, you might need to verify the authenticity of the GitLab host.
Follow the on-screen prompts if you see a message like:
The authenticity of host 'gitlab.example.com (35.231.145.151)' can't be established.
ECDSA key fingerprint is SHA256:HbW3g8zUjNSksFbqTiUWPWg2Bq1x8xdGUrliXFzSnUw.
Are you sure you want to continue connecting (yes/no)?
You should receive a welcome message.
Welcome to GitLab, <username>!
If the message doesn’t appear, you might need to
troubleshoot your SSH connection
.
Update your SSH key passphrase
You can update the passphrase for your SSH key:
Open a terminal and run this command:
ssh-keygen -p -f /path/to/ssh_key
At the prompts, enter the passphrase and then press
Enter
.
Upgrade your RSA key pair to a more secure format
If your version of OpenSSH is between 6.5 and 7.8, you can save your private
RSA SSH keys in a more secure OpenSSH format by opening a terminal and running
this command:
ssh-keygen -o -f ~/.ssh/id_rsa
Alternatively, you can generate a new RSA key with the more secure encryption format with
the following command:
ssh-keygen -o -t rsa -b
4096
-C
"<comment>"
Generate an SSH key pair for a FIDO2 hardware security key
To generate ED25519_SK or ECDSA_SK SSH keys, you must use OpenSSH 8.2 or later:
Insert a hardware security key into your computer.
Open a terminal.
Run
ssh-keygen -t
followed by the key type and an optional comment.
This comment is included in the
.pub
file that’s created.
You may want to use an email address for the comment.
For example, for ED25519_SK:
ssh-keygen -t ed25519-sk -C
"<comment>"
For ECDSA_SK:
ssh-keygen -t ecdsa-sk -C
"<comment>"
If your security key supports FIDO2 resident keys, you can enable this when
creating your SSH key:
ssh-keygen -t ed25519-sk -O resident -C
"<comment>"
-O resident
indicates that the key should be stored on the FIDO authenticator itself.
Resident key is easier to import to a new computer because it can be loaded directly
from the security key by
ssh-add -K
or
ssh-keygen -K
.
Press
Enter
. Output similar to the following is displayed:
Generating public/private ed25519-sk key pair.
You may need to touch your authenticator to authorize key generation.
Touch the button on the hardware security key.
Accept the suggested filename and directory:
Enter file in which to save the key (/home/user/.ssh/id_ed25519_sk):
Specify a
passphrase
:
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
A confirmation is displayed, including information about where your files are stored.
A public and private key are generated.
Add the public SSH key to your GitLab account
.
Generate an SSH key pair with 1Password
You can use
1Password
and the
1Password browser extension
to either:
Automatically generate a new SSH key.
Use an existing SSH key in your 1Password vault to authenticate with GitLab.
Sign in to GitLab.
On the left sidebar, select your avatar. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Edit profile
.
On the left sidebar, select
SSH Keys
.
Select
Add new key
.
Select
Key
, and you should see the 1Password helper appear.
Select the 1Password icon and unlock 1Password.
You can then select
Create SSH Key
or select an existing SSH key to fill in the public key.
In the
Title
box, enter a description, like
Work Laptop
or
Home Workstation
.
Optional. Select the
Usage type
of the key. It can be used either for
Authentication
or
Signing
or both.
Authentication & Signing
is the default value.
Optional. Update
Expiration date
to modify the default expiration date.
Select
Add key
.
For more information about using 1Password with SSH keys, see the
1Password documentation
.
Use different keys for different repositories
You can use a different key for each repository.
Open a terminal and run this command:
git config core.sshCommand
"ssh -o IdentitiesOnly=yes -i ~/.ssh/private-key-filename-for-this-repository -F /dev/null"
This command does not use the SSH Agent and requires Git 2.10 or later. For more information
on
ssh
command options, see the
man
pages for both
ssh
and
ssh_config
.
View your SSH keys
To view the SSH keys for your account:
On the left sidebar, select your avatar. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Edit profile
.
On the left sidebar, select
SSH Keys
.
Your existing SSH keys are listed at the bottom of the page. The information includes:
The title for the key
Public fingerprint
Permitted usage types
Creation date
Last used date
Expiry date
Remove an SSH key
You can revoke or delete your SSH key to permanently remove it from your account.
Removing your SSH key has additional implications if you sign your commits with the key. For more information, see
Signed commits with removed SSH keys
.
Revoke an SSH key
History
Introduced
in GitLab 15.9.
If your SSH key becomes compromised, revoke the key.
Prerequisites:
The SSH key must have the
Signing
or
Authentication & Signing
usage type.
To revoke an SSH key:
On the left sidebar, select your avatar. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Edit profile
.
On the left sidebar, select
SSH Keys
.
Next to the SSH key you want to revoke, select
Revoke
.
Select
Revoke
.
Delete an SSH key
To delete an SSH key:
On the left sidebar, select your avatar. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Edit profile
.
On the left sidebar, select
SSH Keys
.
Next to the key you want to delete, select
Remove
(
remove
).
Select
Delete
.
SSH key expiration
You can set an expiration date when you add an SSH key to your account. This optional setting
helps limit the risk of a security breach.
After your SSH key expires, you can no longer use it to authenticate or sign commits. You must
generate a new SSH key
and
add it to your account
.
On GitLab Self-Managed and GitLab Dedicated, administrators can view expiration dates and use them
for guidance when
deleting keys
.
GitLab checks daily for expiring SSH keys and sends notifications:
At 01:00 AM UTC, seven days before expiration.
At 02:00 AM UTC on the expiration date.
Use different accounts on a single GitLab instance
You can use multiple accounts to connect to a single instance of GitLab. You
can do this by using the command in the
previous topic
.
However, even if you set
IdentitiesOnly
to
yes
, you cannot sign in if an
IdentityFile
exists outside of a
Host
block.
Instead, you can assign aliases to hosts in the
~/.ssh/config
file.
For the
Host
, use an alias like
user_1.gitlab.com
and
user_2.gitlab.com
. Advanced configurations
are more difficult to maintain, and these strings are easier to
understand when you use tools like
git remote
.
For the
IdentityFile
, use the path the private key.
# User1 Account Identity
Host <user_1.gitlab.com>
Hostname gitlab.com
PreferredAuthentications publickey
IdentityFile ~/.ssh/<example_ssh_key1>
# User2 Account Identity
Host <user_2.gitlab.com>
Hostname gitlab.com
PreferredAuthentications publickey
IdentityFile ~/.ssh/<example_ssh_key2>
Now, to clone a repository for
user_1
, use
user_1.gitlab.com
in the
git clone
command:
git clone git@<user_1.gitlab.com>:gitlab-org/gitlab.git
To update a previously-cloned repository that is aliased as
origin
:
git remote set-url origin git@<user_1.gitlab.com>:gitlab-org/gitlab.git
Private and public keys contain sensitive data. Ensure the permissions
on the files make them readable to you but not accessible to others.
Configure two-factor authentication (2FA)
You can set up two-factor authentication (2FA) for
Git over SSH
. You should use
ED25519_SK
or
ECDSA_SK
SSH keys.
Use EGit on Eclipse
If you are using
EGit
, you can
add your SSH key to Eclipse
.
Use SSH on Microsoft Windows
If you’re running Windows 10, you can either use the
Windows Subsystem for Linux (WSL)
with
WSL 2
which
has both
git
and
ssh
preinstalled, or install
Git for Windows
to
use SSH through PowerShell.
The SSH key generated in WSL is not directly available for Git for Windows, and vice versa,
as both have a different home directory:
WSL:
/home/<user>
Git for Windows:
C:\Users\<user>
You can either copy over the
.ssh/
directory to use the same key, or generate a key in each environment.
If you’re running Windows 11 and using
OpenSSH for Windows
, ensure the
HOME
environment variable is set correctly. Otherwise, your private SSH key might not be found.
Alternative tools include:
Cygwin
PuTTYgen
0.81 and later (earlier versions are
vulnerable to disclosure attacks
)
Disable SSH Keys for enterprise users
History
Introduced
in GitLab 18.6
with a flag
named
enterprise_disable_ssh_keys
. Disabled by default.
The availability of this feature is controlled by a feature flag.
For more information, see the history.
Prerequisites:
You must have the Owner role for the group that the enterprise user belongs to.
Disabling the SSH Keys of a group’s
enterprise users
:
Stops the enterprise users from adding new SSH Keys. This behavior applies
even if an enterprise user is also an administrator of the group.
Disables the existing SSH Keys of the enterprise users.
Disabling SSH Keys for enterprise users does not disable deployment keys for
service accounts
.
To disable the enterprise users’ SSH Keys:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings > General
.
Expand
Permissions and group features
.
Under
Enterprise users
, select
Disable SSH Keys
.
Select
Save changes
.
When you delete or block an enterprise user account, their personal SSH Keys are automatically revoked.
Overriding SSH settings on the GitLab server
GitLab integrates with the system-installed SSH daemon and designates a user
(typically named
git
) through which all access requests are handled. Users
who connect to the GitLab server over SSH are identified by their SSH key instead
of their username.
SSH
client
operations performed on the GitLab server are executed as this
user. You can modify this SSH configuration. For example, you can specify
a private SSH key for this user to use for authentication requests. However, this practice
is
not supported
and is strongly discouraged as it presents significant
security risks.
GitLab checks for this condition, and directs you
to this section if your server is configured this way. For example:
$ gitlab-rake gitlab:check
Git user has default SSH configuration? ... no
Try fixing it:
mkdir ~/gitlab-check-backup-1504540051
sudo mv /var/lib/git/.ssh/id_rsa ~/gitlab-check-backup-1504540051
sudo mv /var/lib/git/.ssh/id_rsa.pub ~/gitlab-check-backup-1504540051
For more information see:
doc/user/ssh.md#overriding-ssh-settings-on-the-gitlab-server
Please fix the error above and rerun the checks.
Remove the custom configuration as soon as you can. These customizations
are
explicitly not supported
and may stop working at any time.
Verify GitLab SSH ownership and permissions
The GitLab SSH folder and files must have the following permissions:
The folder
/var/opt/gitlab/.ssh/
must be owned by the
git
group and the
git
user, with permissions set to
700
.
The
authorized_keys
file must have permissions set to
600
.
The
authorized_keys.lock
file must have permissions set to
644
.
To verify that these permissions are correct, run the following:
stat -c
"%a %n"
/var/opt/gitlab/.ssh/.
Set permissions
If the permissions are wrong, sign in to the application server and run:
cd
/var/opt/gitlab/
chown git:git /var/opt/gitlab/.ssh/
chmod
700
/var/opt/gitlab/.ssh/
chmod
600
/var/opt/gitlab/.ssh/authorized_keys
chmod
644
/var/opt/gitlab/.ssh/authorized_keys.lock
