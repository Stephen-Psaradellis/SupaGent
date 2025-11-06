# Install and set up the GitLab plugin for Neovim | GitLab Docs

Source: https://docs.gitlab.com/editor_extensions/neovim/setup/

Install and set up the GitLab plugin for Neovim | GitLab Docs
Install and set up the GitLab plugin for Neovim
Prerequisites:
For both GitLab.com and GitLab Self-Managed, you have GitLab version 16.1 or later.
While many extension features might work with earlier versions, they are unsupported.
The GitLab Duo Code Suggestions feature requires GitLab version 16.8 or later.
You have
Neovim
version 0.9 or later.
You have
NPM
installed. NPM is required for the Code Suggestions install.
To install the extension, follow the installation steps for your chosen plugin manager:
No plugin manager
Run this command to include this project with
packadd
on startup:
git clone https://gitlab.com/gitlab-org/editor-extensions/gitlab.vim.git ~/.local/share/nvim/site/pack/gitlab/start/gitlab.vim
lazy.nvim
Add this plugin to your
lazy.nvim
configuration:
{
'https://gitlab.com/gitlab-org/editor-extensions/gitlab.vim.git'
,
-- Activate when a file is created/opened
event
=
{
'BufReadPre'
,
'BufNewFile'
},
-- Activate when a supported filetype is open
ft
=
{
'go'
,
'javascript'
,
'python'
,
'ruby'
},
cond
=
function
()
-- Only activate if token is present in environment variable.
-- Remove this line to use the interactive workflow.
return
vim.env
.
GITLAB_TOKEN
~=
nil
and
vim.env
.
GITLAB_TOKEN
~=
''
end
,
opts
=
{
statusline
=
{
-- Hook into the built-in statusline to indicate the status
-- of the GitLab Duo Code Suggestions integration
enabled
=
true
,
},
},
}
packer.nvim
Declare the plugin in your
packer.nvim
configuration:
use
{
"git@gitlab.com:gitlab-org/editor-extensions/gitlab.vim.git"
,
}
Authenticate with GitLab
To connect this extension to your GitLab account, configure your environment variables:
Environment variable
Default
Description
GITLAB_TOKEN
not applicable
The default GitLab personal access token to use for authenticated requests. If provided, skips interactive authentication.
GITLAB_VIM_URL
https://gitlab.com
Override the GitLab instance to connect with. Defaults to
https://gitlab.com
.
A full list of environment variables is available in the extension’s help text at
doc/gitlab.txt
.
Configure the extension
To configure this extension:
Configure your desired file types. For example, because this plugin supports Ruby, it adds a
FileType ruby
auto-command.
To configure this behavior for more file types, add more file types to the
code_suggestions.auto_filetypes
setup option:
require
(
'gitlab'
).
setup
({
statusline
=
{
enabled
=
false
},
code_suggestions
=
{
-- For the full list of default languages, see the 'auto_filetypes' array in
-- https://gitlab.com/gitlab-org/editor-extensions/gitlab.vim/-/blob/main/lua/gitlab/config/defaults.lua
auto_filetypes
=
{
'ruby'
,
'javascript'
},
-- Default is { 'ruby' }
ghost_text
=
{
enabled
=
false
,
-- ghost text is an experimental feature
toggle_enabled
=
"<C-h>"
,
accept_suggestion
=
"<C-l>"
,
clear_suggestions
=
"<C-k>"
,
stream
=
true
,
},
}
})
Configure Omni Completion
to set up the key mapping to trigger Code Suggestions.
Optional.
Configure
<Plug>
key mappings
.
Optional. Set up helptags using
:helptags ALL
for access to
:help gitlab.txt
.
Configure Omni Completion
To enable
Omni Completion
with Code Suggestions:
Create a
personal access token
with the
api
scope.
Add the token to your shell as
GITLAB_TOKEN
environment variable.
Install the Code Suggestions
language server
by running the
:GitLabCodeSuggestionsInstallLanguageServer
vim command.
Start the Language Server by running the
:GitLabCodeSuggestionsStart
vim command. Optionally,
Configure
<Plug>
key mappings
to toggle the language server.
Optional. Consider configuring Omni Completion’s dialog even for a single suggestion:
vim.o
.
completeopt
=
'menu,menuone'
When working in a supported file type, open the Omni Completion menu by pressing
Control
+
x
then
Control
+
o
.
Configure
<Plug>
key mappings
For convenience, this plugin provides
<Plug>
key mappings. To use the
<Plug>(GitLab...)
key mapping,
you must include your own key mapping that references it:
-- Toggle Code Suggestions on/off with Control-G in normal mode:
vim.keymap
.
set
(
'n'
,
'<C-g>'
,
'<Plug>(GitLabToggleCodeSuggestions)'
)
Uninstall the extension
To uninstall the extension, remove this plugin and any language server binaries with these commands:
rm -r ~/.local/share/nvim/site/pack/gitlab/start/gitlab.vim
rm ~/.local/share/nvim/gitlab-code-suggestions-language-server-*
