# Install and set up the GitLab plugin for JetBrains IDEs | GitLab Docs

Source: https://docs.gitlab.com/editor_extensions/jetbrains_ide/setup/

Install and set up the GitLab plugin for JetBrains IDEs | GitLab Docs
Install and set up the GitLab plugin for JetBrains IDEs
Download the plugin from the
JetBrains Plugin Marketplace
and install it.
Prerequisites:
JetBrains IDEs: 2023.2.X and later.
GitLab version 16.8 or later.
If you use an older version of a JetBrains IDE, download a version of the plugin compatible with your IDE:
On the GitLab Duo
plugin page
, select
Versions
.
Select
Compatibility
, then select your JetBrains IDE.
Select a
Channel
to filter for stable releases or alpha releases.
In the compatibility table, find your IDE version and select
Download
.
Enable the plugin
To enable the plugin:
In your IDE, on the top bar, select your IDE’s name, then select
Settings
.
On the left sidebar, select
Plugins
.
Select the
GitLab Duo
plugin, and select
Install
.
Select
OK
or
Save
.
Connect to GitLab
After you install the extension, connect it to your GitLab account.
Create a personal access token
If you are on GitLab Self-Managed, create a personal access token.
In GitLab, on the left sidebar, select your avatar. If you’ve
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
Authenticate with GitLab
After you configure the plugin in your IDE, connect it to your GitLab account:
In your IDE, on the top bar, select your IDE’s name, then select
Settings
.
On the left sidebar, expand
Tools
, then select
GitLab Duo
.
Select an authentication method:
For GitLab.com, use
OAuth
.
For GitLab Self-Managed and GitLab Dedicated, use
Personal access token
.
Provide the
URL to GitLab instance
. For GitLab.com, use
https://gitlab.com
.
For
GitLab Personal Access Token
, paste in the personal access token you created.
The token is not displayed, nor is it accessible to others.
Select
Verify setup
.
Select
OK
or
Save
.
Set the default namespace
The GitLab Duo Agent Platform uses the
Default Namespace
value when the plugin
can’t determine the current GitLab project. To configure this value:
In your IDE, on the top bar, select your IDE’s name, then select
Settings
.
On the left sidebar, expand
Tools
, then select
GitLab Duo
.
Enter a value for
Default Namespace
.
Select
OK
or
Save
.
Install alpha versions of the plugin
GitLab publishes pre-release (alpha) builds of the plugin to the
Alpha
release channel
in the JetBrains Marketplace.
To install a pre-release build, either:
Download the build from JetBrains Marketplace and
install it from disk
.
Add the
alpha
plugin repository
to your IDE. For the repository URL, use
https://plugins.jetbrains.com/plugins/alpha/list
.
To see the alpha release after adding the
alpha
plugin repository, you might need to uninstall and reinstall the GitLab Duo plugin.
For a video tutorial of this process, see
Install alpha releases of the GitLab Duo plugin for JetBrains
.
