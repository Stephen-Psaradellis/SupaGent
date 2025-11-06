# Stage, commit, and push changes | GitLab Docs

Source: https://docs.gitlab.com/topics/git/commit/

Stage, commit, and push changes | GitLab Docs
Stage, commit, and push changes
When you make changes to files in a repository, Git tracks the changes
against the most recent version of the checked out branch. You can use
Git commands to review and commit your changes to the branch, and push
your work to GitLab.
Add and commit local changes
When you’re ready to write your changes to the branch, you can commit
them. A commit includes a comment that records information about the
changes, and usually becomes the new tip of the branch.
Git doesn’t automatically include any files you move, change, or
delete in a commit. This prevents you from accidentally including a
change or file, like a temporary directory. To include changes in a
commit, stage them with
git add
.
To stage and commit your changes:
From your repository, for each file or directory you want to add, run
git add <file name or path>
.
To stage all files in the current working directory, run
git add .
.
Confirm that the files have been added to staging:
git status
The files are displayed in green.
To commit the staged files:
git commit -m
"<comment that describes the changes>"
The changes are committed to the branch.
Write a good commit message
The guidelines published by Chris Beams in
How to Write a Git Commit Message
help you write a good commit message:
The commit subject and body must be separated by a blank line.
The commit subject must start with a capital letter.
The commit subject must not be longer than 72 characters.
The commit subject must not end with a period.
The commit body must not contain more than 72 characters per line.
The commit subject or body must not contain emoji.
Commits that change 30 or more lines across at least 3 files should
describe these changes in the commit body.
Use the full URLs for issues, milestones, and merge requests instead of short references,
as they are displayed as plain text outside of GitLab.
The merge request should not contain more than 10 commit messages.
The commit subject should contain at least 3 words.
Commit all changes
You can stage all your changes and commit them with one command:
git commit -a -m
"<comment that describes the changes>"
Be careful your commit doesn’t include files you don’t want to record
to the remote repository. As a rule, always check the status of your
local repository before you commit changes.
Send changes to GitLab
To push all local changes to the remote repository:
git push <remote> <name-of-branch>
For example, to push your local commits to the
main
branch of the
origin
remote:
git push origin main
Sometimes Git does not allow you to push to a repository. Instead,
you must
force an update
.
Push options
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
When you push changes to a branch, you can use client-side
Git push options
.
In Git 2.10 and later, use Git push options to:
Skip CI jobs
Push to merge requests
In Git 2.18 and later, you can use either the long format (
--push-option
) or the shorter
-o
:
git push -o <push_option>
In Git 2.10 to 2.17, you must use the long format:
git push --push-option
=
<push_option>
For server-side controls and enforcement of best practices, see
push rules
and
server hooks
.
Push options for GitLab CI/CD
You can use push options to skip a CI/CD pipeline, or pass CI/CD variables.
Push options are not available for merge request pipelines. For more information,
see
issue 373212
.
Push option
Description
Example
ci.input=<name>=<value>
Passes input parameters to the pipeline.
git push -o ci.input='stage=test' -o ci.input='security_scan=false'
. Array input:
git push -o ci.input='my_array=["string", "double", "quotes"]'
ci.skip
Skips the pipeline for this push. Only affects branch pipelines, not
merge request pipelines
. Does not skip CI/CD integrations like Jenkins.
git push -o ci.skip
ci.variable="<name>=<value>"
Sets
CI/CD variables
for the pipeline. Only affects branch pipelines, not
merge request pipelines
.
git push -o ci.variable="MAX_RETRIES=10" -o ci.variable="MAX_TIME=600"
Push options for Integrations
You can use push options to skip integration CI/CD pipelines.
Push option
Description
Example
integrations.skip_ci
Skip push events for CI/CD integrations, such as Atlassian Bamboo, Buildkite, Drone, Jenkins, and JetBrains TeamCity. Introduced in
GitLab 16.2
.
git push -o integrations.skip_ci
Push options for merge requests
Git push options can perform actions for merge requests while pushing changes:
Push option
Description
merge_request.create
Create a new merge request for the pushed branch. When pushing from the default branch, you must specify a target branch using the
merge_request.target
option to create a merge request.
merge_request.target=<branch_name>
Set the target of the merge request to a particular branch, such as:
git push -o merge_request.target=branch_name
. Required when creating a merge request from the default branch.
merge_request.target_project=<project>
Set the target of the merge request to a particular upstream project, such as:
git push -o merge_request.target_project=path/to/project
. Introduced in
GitLab 16.6
.
merge_request.merge_when_pipeline_succeeds
Deprecated
in GitLab 17.11 favor of the
auto_merge
option.
merge_request.auto_merge
Set the merge request to
auto merge
.
merge_request.remove_source_branch
Set the merge request to remove the source branch when it’s merged.
merge_request.squash
Set the merge request to squash all commits into a single commit on merge. Introduced in
GitLab 17.2
.
merge_request.title="<title>"
Set the title of the merge request. For example:
git push -o merge_request.title="The title I want"
.
merge_request.description="<description>"
Set the description of the merge request. For example:
git push -o merge_request.description="The description I want"
.
merge_request.draft
Mark the merge request as a draft. For example:
git push -o merge_request.draft
.
merge_request.milestone="<milestone>"
Set the milestone of the merge request. For example:
git push -o merge_request.milestone="3.0"
.
merge_request.label="<label>"
Add labels to the merge request. If the label does not exist, it is created. For example, for two labels:
git push -o merge_request.label="label1" -o merge_request.label="label2"
.
merge_request.unlabel="<label>"
Remove labels from the merge request. For example, for two labels:
git push -o merge_request.unlabel="label1" -o merge_request.unlabel="label2"
.
merge_request.assign="<user>"
Assign users to the merge request. Accepts username or user ID. For example, for two users:
git push -o merge_request.assign="user1" -o merge_request.assign="user2"
.
merge_request.unassign="<user>"
Remove assigned users from the merge request. Accepts username or user ID. For example, for two users:
git push -o merge_request.unassign="user1" -o merge_request.unassign="user2"
.
Push options for secret push protection
You can use push options to skip
secret push protection
.
Push option
Description
Example
secret_push_protection.skip_all
Do not perform secret push protection for any commit in this push.
git push -o secret_push_protection.skip_all
Push options for security policy
You can use push options to
bypass security policies
.
Push option
Description
Example
security_policy.bypass_reason
Set the bypass reason for the security policy.
git push -o security_policy.bypass_reason="Hot fix"
Push options for GitGuardian integration
You can use the same
push option for Secret push protection
to skip GitGuardian secret detection.
Push option
Description
Example
secret_detection.skip_all
Deprecated in GitLab 17.2. Use
secret_push_protection.skip_all
instead.
git push -o secret_detection.skip_all
secret_push_protection.skip_all
Do not perform GitGuardian secret detection.
git push -o secret_push_protection.skip_all
Formats for push options
If your push option requires text containing spaces, enclose the text in
double quotes (
"
). You can omit the quotes if there are no spaces. Some examples:
git push -o merge_request.label
=
"Label with spaces"
git push -o merge_request.label
=
Label-with-no-spaces
To combine push options to accomplish multiple tasks at once, use
multiple
-o
(or
--push-option
) flags. This command creates a
new merge request, targets a branch (
my-target-branch
), and sets auto-merge:
git push -o merge_request.create -o merge_request.target
=
my-target-branch -o merge_request.auto_merge
To create a new merge request from the default branch targeting a different branch:
git push -o merge_request.create -o merge_request.target
=
feature-branch
Create Git aliases for pushing
Adding push options to Git commands can create very long commands. If
you use the same push options frequently, create Git aliases for them.
Git aliases are command-line shortcuts for longer Git commands.
To create and use a Git alias for the
auto merge Git push option
:
In your terminal window, run this command:
git config --global alias.mwps
"push -o merge_request.create -o merge_request.target=main -o merge_request.auto_merge"
To use the alias to push a local branch that targets the default branch (
main
)
and auto-merges, run this command:
git mwps origin <local-branch-name>
Related topics
Common Git commands
