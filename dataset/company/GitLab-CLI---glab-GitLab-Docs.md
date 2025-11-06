# GitLab CLI - `glab` | GitLab Docs

Source: https://docs.gitlab.com/editor_extensions/gitlab_cli/

GitLab CLI - `glab` | GitLab Docs
GitLab CLI -
glab
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
glab
is an open source GitLab CLI tool. It brings GitLab to your terminal:
next to where you are already working with Git and your code, without
switching between windows and browser tabs.
Work with issues.
Work with merge requests.
Watch running pipelines directly from your CLI.
The GitLab CLI uses commands structured like
glab <command> <subcommand> [flags]
to perform many of the actions you usually do from the GitLab user interface:
# Sign in
glab auth login --stdin < token.txt
# View a list of issues
glab issue list
# Create merge request for issue 123
glab mr create
123
# Check out the branch for merge request 243
glab mr checkout
243
# Watch the pipeline in progress
glab pipeline ci view
# View, approve, and merge the merge request
glab mr view
glab mr approve
glab mr merge
Core commands
glab alias
: Create, list, and delete aliases.
glab api
: Make authenticated requests to the GitLab API.
glab auth
: Manage the authentication state of the CLI.
glab changelog
: Interact with the changelog API.
glab check-update
: Check for updates to the CLI.
glab ci
: Work with GitLab CI/CD pipelines and jobs.
glab cluster
: Manage GitLab agents for Kubernetes and their clusters.
glab completion
: Generate shell completion scripts.
glab config
: Set and get CLI settings.
glab deploy-key
: Manage deploy keys.
glab duo
: Generate terminal commands from natural language.
glab incident
: Work with GitLab incidents.
glab issue
: Work with GitLab issues.
glab iteration
: Retrieve iteration information.
glab job
: Work with GitLab CI/CD jobs.
glab label
: Manage labels for your project.
glab mr
: Create, view, and manage merge requests.
glab release
: Manage GitLab releases.
glab repo
: Work with GitLab repositories and projects.
glab schedule
: Work with GitLab CI/CD schedules.
glab securefile
: Manage secure files for a project.
glab snippet
: Create, view and manage snippets.
glab ssh-key
: Manage SSH keys registered with your GitLab account.
glab stack
: Create, manage, and work with stacked diffs.
glab token
: Manage personal, project, or group tokens.
glab user
: Interact with a GitLab user account.
glab variable
: Manage variables for a GitLab project or group.
glab version
: Show version information for the CLI.
GitLab Duo for the CLI
Tier
: Premium, Ultimate
Add-on
: GitLab Duo Enterprise
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Model information
LLM: Anthropic
Claude 3 Haiku
Available on
GitLab Duo with self-hosted models
: Yes
History
Changed to require GitLab Duo add-on in GitLab 17.6 and later.
Changed to include Premium in GitLab 18.0.
The GitLab CLI includes features powered by
GitLab Duo
. These include:
glab duo ask
To ask questions about
git
commands while you work, type:
glab duo ask
The
glab duo ask
command can help you remember a
git
command you forgot,
or provide suggestions on how to run
git
commands to perform other tasks.
Install the CLI
Installation instructions are available in
the
glab
README
.
Authenticate with GitLab
To authenticate with your GitLab account, run
glab auth login
.
glab
respects tokens set using
GITLAB_TOKEN
.
glab
also integrates with the
1Password shell plugin
for secure authentication.
Examples
Run a CI/CD pipeline with variables from a file
The
glab ci run
command, when run with the
-f
(
--variables-from-string
) flag, uses values stored
in an external file. For example, add this code to your
.gitlab-ci.yml
file
to reference two variables:
stages
:
-
build
# $EXAMPLE_VARIABLE_1 and $EXAMPLE_VARIABLE_2 are stored in another file
build-job
:
stage
:
build
script
:
-
echo $EXAMPLE_VARIABLE_1
-
echo $EXAMPLE_VARIABLE_2
-
echo $CI_JOB_ID
Then, create a file named
variables.json
to contain those variables:
[
{
"key"
:
"EXAMPLE_VARIABLE_1"
,
"value"
:
"example value 1"
},
{
"key"
:
"EXAMPLE_VARIABLE_2"
,
"value"
:
"example value 2"
}
]
To start a CI/CD pipeline that includes the contents of
variables.json
, run this command, editing
the path to the file as needed:
$ glab ci run --variables-file /tmp/variables.json
$
echo
$EXAMPLE_VARIABLE_1
example value
1
$
echo
$EXAMPLE_VARIABLE_2
example value
2
$
echo
$CI_JOB_ID
9811701914
Use the CLI as a Docker credential helper
You can use the CLI as a
Docker credential helper
when pulling images from the GitLab
container registry
or the
container image dependency proxy
. To configure the credential helper
do the following:
Run
glab auth login
.
Select the type of GitLab instance to sign in to. If prompted, enter your GitLab hostname.
For sign-in method, select
Web
.
Enter a comma-separated list of domains used for the container registry and container image proxy.
When signing in to GitLab.com, default values are provided.
After authenticating, run
glab auth configure-docker
to initialize the credential helper in
your Docker configuration.
Report issues
Open an issue in the
gitlab-org/cli
repository
to send us feedback.
Related topics
Install the CLI
Documentation
Extension source code in the
cli
project
Troubleshooting
Environment variable changes in
glab
2.0.0
In
glab
version 2.0.0 and later, all
glab
environment variables are prefixed with
GLAB_
.
For more information about this deprecation, see
issue 7999
.
glab completion
commands fail when using the 1Password shell plugin
The
1Password shell plugin
adds the alias
glab='op plugin run -- glab'
, which can interfere with the
glab completion
command. If your
glab completion
commands fail, configure your shell to prevent expanding aliases
before performing completions:
For Zsh, edit your
~/.zshrc
file and add this line:
setopt completealiases
For Bash, edit your
~/.bashrc
file and add this line:
complete -F _functionname glab
For more information, see
issue 122
for the 1Password shell plugin.
Commands use the wrong Git remote
If a Git repository has multiple remotes and you select the wrong one, commands might return empty
results if they query the wrong remote. To fix this problem, change the remote
glab
uses for a repository:
From your terminal, run
git config edit
.
Find the lines that include
glab-resolved = base
, and if incorrect, remove them.
Save your changes to your Git configuration file.
To set the default you’d like to use, run this command. Edit the example and replace
origin
with the name of your preferred remote:
git config
set
--append remote.origin.glab-resolved base
