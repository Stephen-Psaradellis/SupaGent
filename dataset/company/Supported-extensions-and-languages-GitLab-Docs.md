# Supported extensions and languages | GitLab Docs

Source: https://docs.gitlab.com/user/project/repository/code_suggestions/supported_extensions/

Supported extensions and languages | GitLab Docs
Supported extensions and languages
Tier
: Premium, Ultimate
Add-on
: GitLab Duo Core, Pro, or Enterprise, GitLab Duo with Amazon Q
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Changed to require GitLab Duo add-on in GitLab 17.6 and later.
Changed to include GitLab Duo Core in GitLab 18.0.
Code Suggestions is available in the following editor extensions and
for the following languages.
Supported editor extensions
To use Code Suggestions, use one of these editor extensions:
IDE
Extension
Visual Studio Code (VS Code)
GitLab Workflow for VS Code
GitLab Web IDE (VS Code in the Cloud)
No configuration required.
Microsoft Visual Studio (2022 for Windows)
Visual Studio GitLab extension
JetBrains IDEs
GitLab Duo Plugin for JetBrains
Neovim
gitlab.vim
plugin
Eclipse
GitLab for Eclipse
A
GitLab Language Server
is used in VS Code, Visual Studio, Eclipse, and Neovim. The Language Server supports faster iteration across more platforms. You can also configure it to support Code Suggestions in IDEs where GitLab doesn’t provide official support.
You can express interest in other IDE extension support
in this issue
.
Supported languages by IDE
The following table provides more information on the languages Code Suggestions supports by default, and the IDEs.
Code Suggestions also works with other languages, but you must
manually add support
.
Language
Web IDE
VS Code
JetBrains IDEs
Visual Studio 2022 for Windows
Neovim
Eclipse
C
check-circle-filled
Yes
check-circle-filled
Yes
dash-circle
No
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
C++
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
C#
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
CSS
check-circle-filled
Yes
dash-circle
No
dash-circle
No
dash-circle
No
dash-circle
No
dash-circle
No
Go
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Google SQL
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
dash-circle
No
HAML
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
HTML
check-circle-filled
Yes
dash-circle
No
dash-circle
No
dash-circle
No
dash-circle
No
dash-circle
No
Java
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
JavaScript
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Kotlin
dash-circle
No
check-circle-filled
Yes
(Requires third-party extension providing Kotlin support)
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Markdown
check-circle-filled
Yes
dash-circle
No
dash-circle
No
dash-circle
No
dash-circle
No
dash-circle
No
PHP
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Python
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Ruby
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Rust
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Scala
dash-circle
No
check-circle-filled
Yes
(Requires third-party extension providing Scala support)
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Shell scripts (
bash
only)
check-circle-filled
Yes
dash-circle
No
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Svelte
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Swift
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
TypeScript (
.ts
and
.tsx
files)
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Terraform
dash-circle
No
check-circle-filled
Yes
(Requires third-party extension providing Terraform support)
check-circle-filled
Yes
dash-circle
No
check-circle-filled
Yes
(Requires third-party extension providing the
terraform
file type)
check-circle-filled
Yes
Vue
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Some languages are not supported in all JetBrains IDEs, or might require additional
plugin support. Refer to the JetBrains documentation for specifics on your IDE.
Support for Infrastructure-as-Code (IaC)
Code Suggestions works with infrastructure-as-code interfaces, including:
Kubernetes Resource Model (KRM)
Google Cloud CLI
Terraform
Manage languages for Code Suggestions
History
Introduced
in GitLab Workflow for VS Code 4.21.0
You can customize your coding experience in VS Code by enabling or disabling Code Suggestions for specific supported languages.
You can do this by editing your
settings.json
file directly, or from the VS Code user interface:
In VS Code, open the extension settings for
GitLab Workflow
:
On the top bar, go to
Code
>
Settings
>
Extensions
.
Search for
GitLab Workflow
in the list, and select
Manage
(
settings
).
Select
Extension Settings
.
In your
User
settings, find the section titled
AI Assisted Code Suggestions: Enabled Supported Languages
.
To enable Code Suggestions for a language, select its checkbox.
To disable Code Suggestions for a language, clear its checkbox.
Your changes are automatically saved, and take effect immediately.
When you disable Code Suggestions for a language, the Duo icon changes to show that suggestions are disabled
for this language. On hover, it shows
Code Suggestions are disabled for this language
.
Add support for more languages
If your desired language doesn’t have Code Suggestions available by default,
you can add support for your language locally.
However, Code Suggestions might not function as expected.
Visual Studio Code
Prerequisites:
You have installed and enabled the
GitLab Workflow extension for VS Code
.
You have completed the
VS Code extension setup
instructions, and authorized the extension to access your GitLab account.
To do this:
Find your desired language in the list of
language identifiers
.
You need the
Identifier
for your languages in a later step.
In VS Code, open the extension settings for
GitLab Workflow
:
On the top bar, go to
Code
>
Settings
>
Extensions
.
Search for
GitLab Workflow
in the list, and select
Manage
(
settings
).
Select
Extension Settings
.
In your
User
settings, find
GitLab › Ai Assisted Code Suggestions: Additional Languages
and select
Add Item
.
In
Item
, add the identifier for each language you want to support. Identifiers should be
lowercase, like
html
or
powershell
. Don’t add leading periods from file suffixes to each identifier.
Select
OK
.
JetBrains IDEs
Prerequisites:
You have installed and enabled the
GitLab plugin for JetBrains IDEs
.
You have completed the
Jetbrains extension setup
instructions, and authorized the extension to access your GitLab account.
To do this:
Find your desired language in the list of
language identifiers
.
You need the identifier for your languages in a later step.
In your IDE, on the top bar, select your IDE name, then select
Settings
.
On the left sidebar, select
Tools
>
GitLab Duo
.
Under
Code Suggestions Enabled Languages
>
Additional languages
, add the identifier for each language
you want to support. Identifiers should be in lowercase, like
html
. Separate multiple identifiers with commas,
like
html,powershell,latex
, and don’t add leading periods to each identifier.
Select
OK
.
Eclipse
Prerequisites:
You have installed and enabled the
GitLab for Eclipse plugin
.
You have completed the
Eclipse setup
instructions, and authorized the extension to access your GitLab account.
To do this:
In your Eclipse bottom menu, select the GitLab icon.
Select
Show Settings
.
Scroll down to the
Code Suggestions Enabled Languages
section.
In
Additional Languages
, add a comma-separated list of language identifiers. Don’t
add leading periods to the identifiers. For example, use
html
,
md
, and
powershell
.
