# Install and set up the GitLab Workflow extension for VS Code | GitLab Docs

Source: https://docs.gitlab.com/editor_extensions/visual_studio_code/setup/

Install and set up the GitLab Workflow extension for VS Code | GitLab Docs
Install and set up the GitLab Workflow extension for VS Code
To install the GitLab Workflow extension for VS Code:
Go to the Visual Studio Marketplace
and install and enable the extension.
If you use an unofficial version of VS Code, install the
extension from the
Open VSX Registry
.
Connect to GitLab
After you download and install the extension, connect it to your GitLab account.
Authenticate with GitLab
Open the Command Palette:
For macOS, press
Command
+
Shift
+
P
.
For Windows or Linux, press
Control
+
Shift
+
P
.
Type
GitLab: Authenticate
and press
Enter
.
Select your GitLab instance URL from the options, or enter one manually.
If you enter one manually, in
URL to GitLab instance
, paste the full URL,
including the
http://
or
https://
. Press
Enter
to confirm.
Authenticate with GitLab using:
OAuth login after
configuring authentication
.
A new
personal access token
.
The extension matches your Git repository remote URL with the GitLab instance URL you specified
for your token. If you have multiple accounts or projects, you can choose the one you want to use.
For more details, see
Switch GitLab accounts in VS Code
.
Connect to your repository
To connect to your GitLab repository from VS Code:
In VS Code, on the top menu, select
Terminal
>
New Terminal
.
Clone your repository:
git clone <repository>
.
Change to the directory where your repository was cloned and check out your branch:
git checkout <branch_name>
.
Ensure your project is selected:
On the left sidebar, select
GitLab Workflow
(
tanuki
).
Select the project name. If you have multiple projects, select the one you want to work with.
In the terminal, ensure your repository is configured with a remote:
git remote -v
. The results should look similar to:
origin git@gitlab.com:gitlab-org/gitlab.git (fetch)
origin git@gitlab.com:gitlab-org/gitlab.git (push)
If no remote is defined, or you have multiple remotes:
On the left sidebar, select
Source Control
(
branch
).
On the
Source Control
label, right-click and select
Repositories
.
Next to your repository, select the ellipsis (
ellipsis_h
), then
Remote
>
Add Remote
.
Select
Add remote from GitLab
.
Choose a remote.
The extension shows information in the VS Code status bar if both:
Your project has a pipeline for the last commit.
Your current branch is associated with a merge request.
Configure the extension
To configure settings, go to
Settings
>
Extensions
>
GitLab Workflow
.
Settings can be configured at the user or workspace level.
By default, Code Suggestions and GitLab Duo Chat are enabled, so if you have
the GitLab Duo add-on and a seat assigned, you should have access.
Authentication
Authenticate using a personal access token or logging in through an OAuth application.
Create a personal access token
If you are on GitLab Self-Managed or GitLab Dedicated, create a personal access token.
On the left sidebar, select your avatar. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Edit profile
.
On the left sidebar, select
Personal access tokens
.
Select
Add new token
.
Enter a name, description, and expiration date.
Select the
api
scope.
Select
Create personal access token
.
Use an OAuth application
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab Workflow 6.47.0.
To use OAuth authentication you must know the client ID of either:
An instance-wide OAuth application managed by your instance administrator.
A group-wide OAuth application managed by a group owner.
A user OAuth application managed by yourself.
To configure OAuth application login:
Open the Command Palette:
For macOS, press
Command
+
Shift
+
P
.
For Windows or Linux, press
Control
+
Shift
+
P
.
Type
Preferences: Open User Settings
and press
Enter
.
Select
Settings
>
Extensions
>
GitLab Workflow
>
Authentication
.
Under
OAuth Client IDs
, select
Add Item
.
Select
Key
and enter the GitLab instance URL.
Select
Value
and enter the client ID of the OAuth application.
Code security
To configure the code security settings, go to
Settings
>
Extensions
>
GitLab Workflow
>
Code Security
.
To enable SAST scanning of the active file, select the
Enable Real-time SAST scan
checkbox.
Optional. To enable SAST scanning of the active file when you save it, select the
Enable scanning on file save
checkbox.
Install pre-release versions of the extension
GitLab publishes pre-release builds of the extension to the VS Code Extension Marketplace.
To install a pre-release build:
Open VS Code.
Under
Extensions
>
GitLab Workflow
, select
Switch to Pre-release Version
.
Select
Restart Extensions
.
Alternatively
Reload Window
to refresh any outdated webviews after updating.
