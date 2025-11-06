# Install and set up the GitLab extension for Visual Studio | GitLab Docs

Source: https://docs.gitlab.com/editor_extensions/visual_studio/setup/

Install and set up the GitLab extension for Visual Studio | GitLab Docs
Install and set up the GitLab extension for Visual Studio
To get the extension, use any of these methods:
Inside Visual Studio, select
Extensions
from the activity bar, and search for
GitLab
.
From the
Visual Studio Marketplace
.
From GitLab, either from the
list of releases
, or by
downloading the latest version
directly.
The extension requires:
Visual Studio 2022 version 17.6 or later (AMD64 or Arm64).
The
IntelliCode
component for Visual Studio.
GitLab version 16.1 or later.
GitLab Duo Code Suggestions requires GitLab version 16.8 or later.
You are not using Visual Studio for Mac, as it is unsupported.
No new additional data is collected to enable this feature. Private non-public GitLab customer data is not used as training data.
Learn more about
Google Vertex AI Codey APIs Data Governance
.
Connect to GitLab
After you install the extension, connect it to your GitLab account by creating a personal access token and authenticating with GitLab.
Create a personal access token
If you are on GitLab Self-Managed, create a personal access token.
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
and
read_user
scopes.
Select
Create personal access token
.
Authenticate with GitLab
To authenticate with GitLab:
In Visual Studio, on the top bar, go to
Tools
>
Options
>
GitLab
.
In the
Access Token
text box, paste your token. The token is not displayed, nor is it accessible to others.
In the
GitLab URL
text box, enter the URL of your GitLab instance. For GitLab.com, use
https://gitlab.com
.
Enable telemetry
The GitLab extension uses the telemetry settings in Visual Studio to send usage and error
information to GitLab. To enable telemetry in GitLab for Visual Studio:
In Visual Studio, on the top bar, go to
Tools
>
Options
.
In the left sidebar, expand
GitLab
and select
General
.
In the
Enable telemetry
dropdown list, select
True
.
Select
OK
.
Configure the extension
This extension provides custom commands that you can use with GitLab. Most commands don’t have
default keyboard shortcuts to avoid conflicts with your existing Visual Studio configuration.
Command name
Default keyboard shortcut
Description
GitLab.ToggleCodeSuggestions
None
Turn on or turn off Code Suggestions.
GitLab.OpenDuoChat
None
Open GitLab Duo Chat.
GitLab.GitLabDuoNextSuggestions
Control
+
Alt
+
N
Switch to the next code suggestion.
GitLab.GitLabDuoPreviousSuggestions
None
Switch to the previous code suggestion.
GitLab.GitLabExplainTerminalWithDuo
Control
+
Alt
+
E
Explain selected text in the terminal.
GitLabDuoChat.ExplainCode
None
Explain selected code.
GitLabDuoChat.Fix
None
Fix issues for the selected code.
GitLabDuoChat.GenerateTests
None
Generate tests for the selected code.
GitLabDuoChat.Refactor
None
Refactor selected code.
You can access the extension’s custom commands with keyboard shortcuts, which you can customize:
On the top bar, go to
Tools
>
Options
.
Go to
Environment
>
Keyboard
. Search for
GitLab.
.
Select a command, and assign it a keyboard shortcut.
