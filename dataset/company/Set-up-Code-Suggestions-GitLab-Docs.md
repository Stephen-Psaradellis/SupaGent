# Set up Code Suggestions | GitLab Docs

Source: https://docs.gitlab.com/user/project/repository/code_suggestions/set_up/#turn-on-code-suggestions

Set up Code Suggestions | GitLab Docs
Set up Code Suggestions
History
Changed to include GitLab Duo Core in GitLab 18.0.
You can use Code Suggestions in several different IDEs.
To set up Code Suggestions, follow the instructions for your IDE.
Prerequisites
To use Code Suggestions, you need:
A GitLab Duo Core, Pro, or Enterprise add-on.
A Premium or Ultimate subscription.
If you have GitLab Duo Pro or Enterprise, an assigned seat.
If you have GitLab Duo Core,
IDE features turned on
.
To confirm that Code Suggestions
supports your preferred language
.
Different IDEs support different languages.
Configure editor extension
Code Suggestions is part of an editor extension. To use Code Suggestions:
Install the extension in your IDE.
Authenticate with GitLab from the IDE. You can use either OAuth or a personal access token.
Configure the extension.
Follow these steps for your IDE:
Visual Studio Code
Visual Studio
GitLab Duo plugin for JetBrains IDEs
gitlab.vim
plugin for Neovim
GitLab for Eclipse
Turn on Code Suggestions
Code Suggestions is turned on
if you meet the prerequisites
.
To confirm, open your IDE and verify if Code Suggestions works.
VS Code
To verify that Code Suggestions is turned on in VS Code:
In VS Code, go to
Settings
>
Extensions
>
GitLab Workflow
.
Select
Manage
(
settings
).
Ensure that
GitLab › Duo Code Suggestions: Enabled
is selected.
Optional. For
GitLab › Duo Code Suggestions: Enabled Supported Languages
,
select the languages you want to suggest or generate code for.
Optional. For
GitLab › Duo Code Suggestions: Additional Languages
, add other languages you’d like to use.
Visual Studio
To verify that Code Suggestions is turned on in Visual Studio:
In Visual Studio, on the bottom status bar, point to the GitLab icon.
When Code Suggestions is enabled, the icon tooltip shows
GitLab code suggestions are enabled.
If Code Suggestions are not enabled, on the top bar select
Extensions
>
GitLab
>
Toggle Code Suggestions
to enable it.
JetBrains IDEs
To verify that Code Suggestions is turned on in JetBrains IDEs:
In your IDE, on the top bar, select your IDE’s name, then select
Settings
.
On the left sidebar, expand
Tools
, then select
GitLab Duo
.
In the
Features
section, ensure that
Enable Code Suggestions
and
Enable GitLab Duo Chat
are selected.
Select
OK
or
Save
.
Add a custom certificate for Code Suggestions
History
Introduced
in GitLab Duo 2.10.0.
GitLab Duo attempts to detect
trusted root certificates
without configuration on your part. If needed, configure your JetBrains IDE to allow the GitLab Duo plugin
to use a custom SSL certificate when connecting to your GitLab instance.
To use a custom SSL certificate with GitLab Duo:
In your IDE, on the top bar, select your IDE name, then select
Settings
.
On the left sidebar, expand
Tools
, then select
GitLab Duo
.
Under
Connection
, enter the
URL to GitLab instance
.
To verify your connection, select
Verify setup
.
Select
OK
or
Save
.
If your IDE detects a non-trusted SSL certificate:
The GitLab Duo plugin displays a confirmation dialog.
Review the SSL certificate details shown.
Confirm the certificate details match the certificate shown when you connect to GitLab in your browser.
If the certificate matches your expectations, select
Accept
.
To review certificates you’ve already accepted:
In your IDE, on the top bar, select your IDE name, then select
Settings
.
On the left sidebar, select
Tools
>
Server Certificates
.
Select
Server Certificates
.
Select a certificate to view it.
Eclipse
To enable GitLab Duo Code Suggestions, open an Eclipse project. If you open a single file, Code Suggestions is disabled for all file types.
To verify that Code Suggestions is turned on in Eclipse:
In Eclipse, open your GitLab project.
In the Eclipse bottom toolbar, select the GitLab icon.
Code Suggestions
displays as “Enabled”.
Neovim
Code Suggestions provides a LSP (Language Server Protocol) server, to support the built-in
Control
+
x
,
Control
+
o
Omni Completion key mapping:
Mode
Key mappings
Type
Description
INSERT
Control
+
x
,
Control
+
o
Built-in
Requests completions from GitLab Duo Code Suggestions through the language server.
NORMAL
<Plug>(GitLabToggleCodeSuggestions)
<Plug>
Toggles Code Suggestions on or off for the current buffer. Requires
configuration
.
Verify that Code Suggestions is on
All editor extensions from GitLab, except Neovim, add an icon to your IDE’s status bar.
For example, in Visual Studio:
Icon
Status
Meaning
tanuki-ai
Ready
You’ve configured and enabled GitLab Duo, and you’re using a language that supports Code Suggestions.
tanuki-ai-off
Not configured
You haven’t entered a personal access token, or you’re using a language that Code Suggestions doesn’t support.
Loading suggestion
GitLab Duo is fetching Code Suggestions for you.
Error
GitLab Duo has encountered an error.
Turn off Code Suggestions
The process for turning off Code Suggestions is different for each IDE.
You cannot turn off code generation and code completion separately.
VS Code
To turn off Code Suggestions in VS Code:
Go to
Code
>
Settings
>
Extensions
.
Select
Manage
(
settings
) >
Settings
.
Clear the
GitLab Duo Code Suggestions
checkbox.
Instead, you can
set
gitlab.duoCodeSuggestions.enabled
to
false
in the VS Code
settings.json
file
.
Visual Studio
To turn Code Suggestions on or off without uninstalling the extension,
assign a keyboard shortcut to the
GitLab.ToggleCodeSuggestions
custom command
.
To disable or uninstall the extension, see the
Microsoft Visual Studio documentation on uninstalling or disabling the extension
.
JetBrains IDEs
The process to disable GitLab Duo, including Code Suggestions, is the same
regardless of which JetBrains IDE you use.
In your JetBrains IDE, go to settings and select the plugins menu.
Under the installed plugins, find the GitLab Duo plugin.
Disable the plugin.
For more information, see the
JetBrains product documentation
.
Eclipse
To disable Eclipse Code Suggestions for a project:
In the Eclipse bottom toolbar, select the GitLab icon.
Select
Disable Code Suggestions
to disable Code Suggestions for the current project.
To disable Eclipse Code Suggestions for a specific language:
In the Eclipse bottom toolbar, select the GitLab icon.
Select
Show Settings
.
Scroll down to the
Code Suggestions Enabled Languages
section and clear the checkbox for the language you wish to disable.
Neovim
Go to the
Neovim
defaults.lua
settings file
.
Under
code_suggestions
, change the
enabled =
flag to
false
:
code_suggestions
=
{
...
enabled
=
false
,
Turn off GitLab Duo
Alternatively, you can
turn off GitLab Duo
(which includes Code Suggestions) completely for a group, project, or instance.
