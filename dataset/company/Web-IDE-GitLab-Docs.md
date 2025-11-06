# Web IDE | GitLab Docs

Source: https://docs.gitlab.com/user/project/web_ide/

Web IDE | GitLab Docs
Web IDE
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Generally available
in GitLab 18.0. Feature flag
vscode_web_ide
removed.
The Web IDE is an advanced editor where you can edit multiple files, stage changes, and create
commits directly in the GitLab UI. Unlike the
Web Editor
, the Web
IDE provides a full-featured development environment with source control management.
Support for
GitLab Flavored Markdown
preview in the Web IDE is proposed in
epic 15810
.
Open the Web IDE
You can access the Web IDE through several methods.
With a keyboard shortcut
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Use the
.
keyboard shortcut.
From a directory
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Go to your directory.
Select
Code
>
Open in Web IDE
.
From a file
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Go to your file.
Select
Edit
>
Open in Web IDE
.
From a merge request
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Go to your merge request.
In the upper right, select
Code
>
Open in Web IDE
.
The Web IDE opens new and modified files in separate tabs, and displays changes side by side.
To reduce load time, only 10 files with the most lines changed open automatically.
The Web IDE interface displays a merge request icon (
merge-request
) next to
new or modified files in the left sidebar
Explorer
view. To view changes to a file, right-click
the file and select
Compare with merge request base
.
Manage files
You can use the Web IDE to open, edit, and upload multiple files.
Open a file
To open a file by name in the Web IDE:
Press
Command
+
P
.
In the search box, enter the filename.
Search open files
To search across open files in the Web IDE:
Press
Shift
+
Command
+
F
.
In the search box, enter your search term.
Upload a file
To upload a file in the Web IDE:
On the left side of the Web IDE, select
Explorer
(
documents
), or
press
Shift
+
Command
+
E
.
Go to the directory where you want to upload the file.
To create a new directory:
In the
Explorer
view, in the upper right,
select
New Folder
(
folder-new
).
Right-click the directory and select
Upload
.
Select the file you want to upload.
You can upload multiple files at once.
The files are uploaded and automatically added to the repository.
Restore uncommitted changes
You do not have to manually save any file you edit in the Web IDE.
The Web IDE stages the files you modify, so you can
commit the changes
.
Uncommitted changes are saved in your browser’s local storage. They persist
even if you close the browser tab or refresh the Web IDE.
If your uncommitted changes are not available, you can restore the changes from local history.
To restore uncommitted changes in the Web IDE:
Press
Shift
+
Command
+
P
.
In the search box, enter
Local History: Find Entry to Restore
.
Select the file that contains the uncommitted changes.
Use source control
You can use source control to view modified files, create and switch branches,
commit changes, and create merge requests.
View modified files
To view a list of files you modified in the Web IDE:
On the left side of the Web IDE, select
Source Control
(
branch
), or
press
Control
+
Shift
+
G
.
Your
CHANGES
,
STAGED CHANGES
, and
MERGE CHANGES
are displayed.
For more information, see the
VS Code documentation
.
Switch branches
The Web IDE uses the current branch by default.
To switch branches in the Web IDE:
On the bottom status bar, on the left, select the current branch name.
Enter or select an existing branch.
Create a branch
To create a branch from the current branch in the Web IDE:
On the bottom status bar, on the left, select the current branch name.
From the dropdown list, select
Create new branch
.
Enter the new branch name.
The Web IDE creates a branch using the checked out branch as base. Alternatively, you can follow
these steps to create a branch from a different base:
On the left side of the Web IDE, select
Source Control
(
branch
), or
press
Control
+
Shift
+
G
.
Select the ellipsis menu (
ellipsis_h
) in the upper-right side of the
Source Control panel.
From the dropdown list, select
Branch
>
Create branch from…
.
From the dropdown list, select the branch that you want to use as base.
If you do not have write access to the repository,
Create new branch
is not visible.
Delete a branch
On the left side of the Web IDE, select
Source Control
(
branch
), or
press
Control
+
Shift
+
G
.
Select the ellipsis menu (
ellipsis_h
) in the upper-right side of the
Source Control panel.
From the dropdown list, select
Branch
>
Delete branch
.
From the dropdown list, select the branch that you want to delete.
You can’t delete protected branches from the Web IDE.
Commit changes
To commit changes in the Web IDE:
On the left side of the Web IDE, select
Source Control
(
branch
), or
press
Control
+
Shift
+
G
.
Enter your commit message.
Select one of the following commit options:
Commit to current branch
- Commits changes to the current branch
Create a new branch
- Creates a new branch and commits changes
Commit and force push
- Force pushes changes to the remote branch
Amend commit and force push
- Modifies the last commit and force pushes
Commit and force push
To commit and force push your changes:
Select the action button menu or select the ellipsis (
ellipsis_h
).
Select
Commit and Force push
.
This action overwrites the remote history of the current branch. Use with caution.
Amend commit and force push
To amend the last commit and force push:
Select the action button menu or select the ellipsis (
ellipsis_h
).
Select
Amend commit and Force push
.
This updates the last commit and force pushes it to the remote repository. Use this to fix recent commits without creating new ones.
Create a merge request
To create a
merge request
in the Web IDE:
Commit the changes
.
In the notification that appears in the lower right, select
Create MR
.
For more information, see
View missed notifications
.
Customize the Web IDE
Customize the Web IDE to match your preferences for keyboard shortcuts,
themes, settings, and synchronization.
Use the Command Palette
You can use the Command Palette to access many commands.
To open the Command Palette and run a command in the Web IDE:
Press
Shift
+
Command
+
P
.
Enter or select the command.
Edit settings
You can use the settings editor to view and edit your user and workspace settings.
To open the settings editor in the Web IDE:
On the top menu bar, select
File
>
Preferences
>
Settings
,
or press
Command
+
,
.
In the settings editor, you can search for the settings you want to change.
Edit keyboard shortcuts
You can use the keyboard shortcuts editor to view and change
the default keybindings for all available commands.
To open the keyboard shortcuts editor in the Web IDE:
On the top menu bar, select
File
>
Preferences
>
Keyboard Shortcuts
,
or press
Command
+
K
then
Command
+
S
.
In the keyboard shortcuts editor, you can search for:
The keybindings you want to change
The commands you want to add or remove keybindings for
Keybindings are based on your keyboard layout.
If you change your keyboard layout, existing keybindings are updated automatically.
Change the color theme
You can choose between different color themes for the Web IDE.
The default theme is
GitLab Dark
.
To change the color theme in the Web IDE:
On the top menu bar, select
File
>
Preferences
>
Theme
>
Color Theme
,
or press
Command
+
K
then
Command
+
T
.
From the dropdown list, preview the themes with the arrow keys.
Select a theme.
The Web IDE stores your active color theme in your
user settings
.
Configure sync settings
To configure sync settings in the Web IDE:
Press
Shift
+
Command
+
P
.
In the search box, enter
Settings Sync: Configure
.
Select or clear the checkbox for:
Settings
Keyboard shortcuts
User snippets
User tasks
UI state
Extensions
Profiles
These settings sync automatically across multiple Web IDE instances.
You cannot sync user profiles or go back to an earlier version of synced settings.
View missed notifications
When you perform actions in the Web IDE, notifications appear in the lower right.
To view any notification you might have missed:
On the bottom status bar, on the right, select the bell icon (
notifications
)
for a list of notifications.
Select the notification you want to view.
Manage extensions
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
as a
beta
in GitLab 17.0
with flags
named
web_ide_oauth
and
web_ide_extensions_marketplace
. Disabled by default.
web_ide_oauth
enabled on GitLab.com, GitLab Self-Managed, and GitLab Dedicated
in GitLab 17.4.
web_ide_extensions_marketplace
enabled on GitLab.com
in GitLab 17.4.
web_ide_oauth
removed
in GitLab 17.5.
Introduced
the
vscode_extension_marketplace_settings
feature flag
in GitLab 17.10. Disabled by default.
web_ide_extensions_marketplace
enabled on GitLab Self-Managed
, and
vscode_extension_marketplace_settings
enabled on GitLab.com and GitLab Self-Managed
in GitLab 17.11.
Generally available
in GitLab 18.1. Feature flags
web_ide_extensions_marketplace
and
vscode_extension_marketplace_settings
removed.
The VS Code Extension Marketplace provides access to extensions that enhance the functionality of the
Web IDE. By default, the GitLab Web IDE connects to the
Open VSX Registry
.
To access the VS Code Extension Marketplace, your browser must be able to access the
.cdn.web-ide.gitlab-static.net
assets host.
This security requirement ensures that third-party extensions run in isolation and cannot access your account.
This applies to both GitLab.com and GitLab Self-Managed.
Prerequisites:
You must
integrate the extension marketplace
in your user preferences.
For GitLab Self-Managed and GitLab Dedicated, a GitLab administrator must
enable the extension registry
.
For enterprise users, a group Owner must
enable the Extension Marketplace for enterprise users
.
Install an extension
To install an extension in the Web IDE:
On the top menu bar, select
View
>
Extensions
,
or press
Command
+
Shift
+
X
.
In the search box, enter the extension name.
Select the extension you want to install.
Select
Install
.
Uninstall an extension
To uninstall an extension in the Web IDE:
On the top menu bar, select
View
>
Extensions
,
or press
Command
+
Shift
+
X
.
From the list of installed extensions, select the extension you want to uninstall.
Select
Uninstall
.
Extension setup
Web IDE extensions may require additional configuration to work with your projects.
Use Vim keybindings
Use Vim keybindings to navigate and edit text using keyboard shortcuts from the Vim text editor.
With the Extensions Marketplace, you can add Vim keybindings to the Web IDE.
To enable Vim keybindings, install the
Vim
extension. For more information, see
install an extension
.
AsciiDoc Support
The
AsciiDoc
extension provides live preview, syntax highlighting, and snippets for AsciiDoc files in the Web IDE. To use AsciiDoc markup preview in the Web IDE, you must install the AsciiDoc extension. For more information, see
install an extension
.
Related topics
GitLab Duo Chat in the Web IDE
Troubleshooting
When working with the Web IDE, you might encounter the following issues.
Character offset when typing
When you type in the Web IDE, you might get a four-character offset.
As a workaround:
On the top menu bar, select
File
>
Preferences
>
Settings
,
or press
Command
+
,
.
In the upper-right corner, select
Open Settings (JSON)
.
In the
settings.json
file, add
"editor.disableMonospaceOptimizations": true
or change the
"editor.fontFamily"
setting.
For more information, see
VS Code issue 80170
.
Update the OAuth callback URL
Offering
: GitLab Self-Managed
Prerequisites:
You must have administrator access to the instance.
The Web IDE uses an
instance-wide OAuth application
for authentication.
If the OAuth callback URL is misconfigured, you might encounter a
Cannot open Web IDE
error page with the following message:
The URL you're using to access the Web IDE and the configured OAuth callback URL do not match. This issue often occurs when you're using a proxy.
To resolve this issue, you must update the OAuth callback URL to match the URL used to access the GitLab instance.
To update the OAuth callback URL:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Applications
.
For
GitLab Web IDE
, select
Edit
.
Enter the OAuth callback URL.
You can enter multiple URLs separated by newlines.
Access token lifetime cannot be less than 5 minutes
Offering
: GitLab Self-Managed
You might encounter an error message stating that the access token lifetime cannot be less
than 5 minutes.
This error occurs when your GitLab instance is configured with an access token expiry time of
less than 5 minutes. The Web IDE requires access tokens with a minimum lifetime of
5 minutes to function properly.
To resolve this issue, increase the access token lifetime to at least 5 minutes in your
instance configuration. For more information about configuring access token expiration,
see
access token expiration
.
Workhorse dependency
Offering
: GitLab Self-Managed
On GitLab Self-Managed, Workhorse must be installed and running in front of the GitLab Rails
server. If it is not, you might encounter issues when you open the Web IDE or use certain
features like Markdown preview.
For security, some parts of the Web IDE must run in a separate origin. To support this
approach, the Web IDE uses Workhorse to route requests appropriately to and from Web IDE
assets. The Web IDE assets are static frontend assets, so it’s unnecessary overhead to rely
on Rails for this effort.
CORS issues
The Web IDE requires specific Cross-Origin Resource Sharing (CORS) configuration to function properly on GitLab Self-Managed instances.
GitLab API endpoints (
/api/*
) must include the following HTTP response headers to support the Web IDE:
Header
Value
Description
Access-Control-Allow-Origin
https://[subdomain].cdn.web-ide.gitlab-static.net
Allows requests from the Web IDE origin. The
[subdomain]
is a dynamically generated alphanumeric string (max 52 characters).
Access-Control-Allow-Headers
Authorization
Permits the Authorization header in cross-origin requests.
Access-Control-Allow-Methods
GET, POST, PUT, DELETE, OPTIONS
Specifies allowed HTTP methods (recommended).
Access-Control-Allow-Credentials
false
The Web IDE does not need to include credentials controlled by this
header
in HTTP requests.
Access-Control-Expose-Headers
Link, X-Total, X-Total-Pages, X-Per-Page, X-Page, X-Next-Page, X-Prev-Page, X-Gitlab-Blob-Id, X-Gitlab-Commit-Id, X-Gitlab-Content-Sha256, X-Gitlab-Encoding, X-Gitlab-File-Name, X-Gitlab-File-Path, X-Gitlab-Last-Commit-Id X-Gitlab-Ref, X-Gitlab-Size, X-Request-Id, ETag
Headers used by GitLab Rest and GraphQL APIs.
Vary
Origin
Ensures proper caching behavior for CORS responses.
Since the subdomain portion of the Web IDE origin is dynamically generated, your CORS configuration must:
Pattern matching
: Accept origins matching the pattern
https://*.cdn.web-ide.gitlab-static.net
.
Validation
: Ensure the subdomain contains only alphanumeric characters and is ≤52 characters.
Security
: Never use wildcard (*) for Access-Control-Allow-Origin as this poses security risks.
A GitLab instance default CORS configuration satisfies these requirements. You might find issues when the GitLab Self-Managed
instance is behind an HTTP reverse proxy server or it uses a custom CORS policy configuration.
If these headers are not provided, the Web IDE will still work on GitLab Self-Managed although
features such as Extension Marketplace will be disabled for security reasons. The Web IDE uses
the
https://*.cdn.web-ide.gitlab-static.net
origin to run third-party extensions in a sandboxed
environment.
Air-gapped or offline environments
The Web IDE disables the Extension Marketplace and Web Views in air-gapped or offline environments where a
user’s web browser can’t connect to the
https://*.cdn.web-ide.gitlab-static.net
external assets host.
The Web IDE uses the external assets host to run third-party code coming from VSCode Extensions and Web Views
in a sandboxed environment to secure user data.
The Web IDE engineering team will provide better support for air-gapped environments in the future.
You can keep track of the latest developments in this
epic
.
Report a problem
To report a problem,
create a new issue
with the following information:
The error message
The full error details
How often the problem occurs
Steps to reproduce the problem
If you’re on a paid tier, you can also
contact Support
for help.
