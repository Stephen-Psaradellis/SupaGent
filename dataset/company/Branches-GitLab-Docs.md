# Branches | GitLab Docs

Source: https://docs.gitlab.com/user/project/repository/branches/

Branches | GitLab Docs
Branches
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Branches keep your team’s development work organized and separated. When multiple people work
on different features simultaneously, branches prevent changes from conflicting with each other.
Each branch acts as an isolated workspace where you implement new features, fix bugs, or
experiment with ideas.
With branches, your team can:
Work on separate features without disrupting the main codebase.
Review proposed changes before they affect the rest of the project.
Roll back problematic changes without affecting other work.
Deploy changes to production in a controlled, predictable way.
The development workflow for branches is:
Create a branch
and add commits to it.
To streamline this process, you should follow
branch naming patterns
.
When the work is ready for review, create a
merge request
to propose merging the changes in your branch.
Preview the changes with a
review app
.
Request a review
.
After your merge request is approved, merge your branch to the origin branch.
The
merge method
determines how merge requests
are handled in your project.
After the contents of your branch are merged,
delete the merged branch
.
View all branches
To view and manage your branches in the GitLab user interface:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
On the left sidebar, select
Code
>
Branches
.
On this page, you can:
See all branches, or filter to see only active or stale branches.
A branch is considered active if a commit has been made to it in the last three months.
Otherwise it is considered stale.
Create new branches
.
Delete merged branches
.
See merge request links that point to the default branch.
Branches with merge requests that do not point to the default branch display the
merge-request
New
merge request button.
View branch rules
.
See latest pipeline status on the branch.
Create a branch
Prerequisites:
You must have at least the Developer role for the project.
To create a new branch from the GitLab UI:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Branches
.
In the upper-right corner, select
New branch
.
Enter a
Branch name
.
In
Create from
, select the base of your branch: an existing branch, an existing
tag, or a commit SHA.
Select
Create branch
.
In a blank project
A
blank project
does not contain a branch, but
you can add one.
Prerequisites:
You must have at least the Developer role for the project.
If you don’t have the Maintainer or Owner role, the
default branch protection
must be set to
Partially protected
or
Not protected
for you to push a commit
to the default branch.
To add a
default branch
to a blank project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Scroll to
The repository for this project is empty
and select the type of
file you want to add.
In the Web IDE, make any desired changes to this file, then select
Create commit
.
Enter a commit message, and select
Commit
.
GitLab creates a default branch and adds your file to it.
From an issue
When viewing an issue, you can create an associated branch directly from that page.
Branches created this way use the
default pattern for branch names from issues
,
including variables.
Prerequisites:
You must have at least the Developer role for the project.
To create a branch from an issue:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
and find your issue.
Below the issue description, select
Create merge request
chevron-down
to display the dropdown list.
Select
Create branch
.
In the dialog, from the
Source (branch or tag)
dropdown list, select a source branch or tag.
Review the suggested branch name. It’s based on your project’s
default branch name pattern
.
Optional. If you need to use a different branch name, enter it in the
Branch name
text box.
Select
Create branch
.
For information about creating branches in empty repositories,
see
Empty repository behavior
.
If the name of the created branch is
prefixed with the issue number
, GitLab cross-links
the issue and related merge request.
From a task
Prerequisites:
You must have at least the Developer role for the project.
To create a branch directly from a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
.
In the issue list, find your task.
Below the task description, select
Create merge request
chevron-down
to display the dropdown list.
Select
Create branch
.
In the dialog, from the
Source branch or tag
dropdown list, select a source branch or tag.
Review the suggested branch name. It’s based on your project’s
default branch name pattern
.
Optional. If you need to use a different branch name, enter it in the
Branch name
text box.
Select
Create branch
.
For information about creating branches in empty repositories,
see
Empty repository behavior
.
If the name of the created branch is
prefixed with the task number
, GitLab cross-links
the issue and related merge request.
Empty repository behavior
If your Git repository is empty, GitLab:
Creates a default branch.
Commits a blank
README.md
file to it.
Creates and redirects you to a new branch based on the issue title.
If your project is
configured with a deployment service
like Kubernetes,
GitLab prompts you to set up
auto deploy
by helping you create a
.gitlab-ci.yml
file.
Name your branch
Git enforces
branch name rules
to help ensure branch names remain compatible with other tools. GitLab
adds extra requirements for branch names, and provides benefits for well-structured branch names.
GitLab enforces these additional rules on all branches:
No spaces are allowed in branch names.
Branch names with 40 hexadecimal characters are prohibited, because they are similar to Git commit hashes.
Branch names are case-sensitive.
Common software packages, like Docker, can enforce
additional branch naming restrictions
.
For the best compatibility with other software packages, use only:
Numbers
Hyphens (
-
)
Underscores (
_
)
Lowercase letters from the ASCII standard table
You can use forward slashes (
/
) and emoji in branch names, but compatibility with other
software packages cannot be guaranteed.
Branch names with specific formatting offer extra benefits:
Streamline your merge request workflow by
prefixing branch names with issue numbers
.
Automate
branch protections
based on branch name.
Test branch names with
push rules
before branches are pushed up to GitLab.
Define which
CI/CD jobs
to run on merge requests.
Configure default pattern for branch names from issues
By default, GitLab uses the pattern
%{id}-%{title}
when creating a branch from
an issue, but you can change this pattern.
Prerequisites:
You must have at least the Maintainer role for the project.
To change the default pattern for branches created from issues:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Repository
.
Expand
Branch defaults
.
Scroll to
Branch name template
and enter a value. The field supports these variables:
%{id}
: The numeric ID of the issue.
%{title}
: The title of the issue, modified to use only characters acceptable in Git branch names.
Select
Save changes
.
Prefix branch names with a number
To streamline the creation of merge requests, start your Git branch name with the
issue or task number, followed by a hyphen. For example, to link a branch to issue
#123
,
start the branch name with
123-
.
The branch must be in the same project as the issue or task.
GitLab uses this number to import data into the merge request:
The item is marked as related to the merge request, and they display links to each other.
The branch is connected to the issue or task.
If your project is configured with a
default closing pattern
,
merging the merge request
also closes
the related issue.
If the merge request is in the same project, and not a fork, the issue milestone
and labels are copied to the merge request.
Manage and protect branches
GitLab provides multiple methods to protect individual branches. These methods
ensure your branches receive oversight and quality checks from their creation to their deletion. To view and edit branch protections, see
Branch rules
.
Download branch comparisons
History
Introduced
in GitLab 18.3.
You can download the comparison between branches as a diff or patch file for use outside of GitLab.
As a diff
To download the branch comparison as a diff, add
format=diff
to the compare URL:
If the URL has no query parameters, append
?format=diff
:
https://gitlab.example.com/my-group/my-project/-/compare/main...feature-branch?format=diff
If the URL already has query parameters, append
&format=diff
:
https://gitlab.example.com/my-group/my-project/-/compare/main...feature-branch?from_project_id=2&format=diff
To download and apply the diff:
curl
"https://gitlab.example.com/my-group/my-project/-/compare/main...feature-branch?format=diff"
|
git apply
As a patch file
To download the branch comparison as a patch file, add
format=patch
to the compare URL:
If the URL has no query parameters, append
?format=patch
:
https://gitlab.example.com/my-group/my-project/-/compare/main...feature-branch?format=patch
If the URL already has query parameters, append
&format=patch
:
https://gitlab.example.com/my-group/my-project/-/compare/main...feature-branch?from_project_id=2&format=patch
To download and apply the patch using
git am
:
# Download and preview the patch
curl
"https://gitlab.example.com/my-group/my-project/-/compare/main...feature-branch?format=patch"
> changes.patch
git apply --check changes.patch
# Apply the patch
git am changes.patch
You can also download and apply the patch in a single command:
curl
"https://gitlab.example.com/my-group/my-project/-/compare/main...feature-branch?format=patch"
|
git am
Delete merged branches
Merged branches can be deleted in bulk if they meet all of these criteria:
They are not
protected branches
.
They have been merged into the project’s default branch.
Prerequisites:
You must have at least the Developer role for the project.
To do this:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Branches
.
In the upper-right corner of the page, select
More
ellipsis_v
.
Select
Delete merged branches
.
In the dialog, enter the word
delete
to confirm, then select
Delete merged branches
.
Deleting a branch does not completely erase all related data.
Some information persists to maintain project history and to support recovery processes.
For more information, see
Handle sensitive information
.
Configure workflows for target branches
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab 16.4
with a flag
named
target_branch_rules_flag
. Enabled by default.
Feature flag removed
in GitLab 16.7.
Some projects use multiple long-term branches for development, like
develop
and
qa
.
In these projects, you might want to keep
main
as the default branch, but expect
merge requests to target
develop
or
qa
instead. Target branch workflows help ensure
merge requests target the appropriate development branch for your project.
When you create a merge request, the workflow checks the name of the branch. If the
branch name matches the workflow, the merge request targets the branch you specify. If the branch name does not match, the merge request targets the
default branch of the project.
Rules are processed on a “first-match” basis - if two rules match the same branch name, the top-most rule is applied.
Prerequisites:
You must have at least the Maintainer role.
To create a target branch workflow:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Merge requests
.
Scroll down to
Merge request branch workflow
Select
Add branch target
.
For
Branch name pattern
, provide a string or wild card to compare against branch names.
Select the
Target branch
to use when the branch name matches the
Branch name pattern
.
Select
Save
.
Target branch workflow example
You could configure your project to have the following target branch workflows:
Branch name pattern
Target branch
feature/*
develop
bug/*
develop
release/*
main
These target branches simplify the process of creating merge requests for a project that:
Uses
main
to represent the deployed state of your application.
Tracks current, unreleased development work in another long-running branch, like
develop
.
If your workflow initially places new features in
develop
instead of
main
, these target branches
ensure all branches matching either
feature/*
or
bug/*
do not target
main
by mistake.
When you’re ready to release to
main
, create a branch named
release/*
, and
ensure this branch targets
main
.
Delete a target branch workflow
When you remove a target branch workflow, existing merge requests remain unchanged.
Prerequisites:
You must have at least the Maintainer role.
To do this:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
Merge requests
.
Select
Delete
on the branch target you want to delete.
Related topics
Protected branches
Branch rules
Compare revisions
Compare changes in merge requests
Download merge request changes
Branches API
Protected Branches API
Getting started with Git
Branches in a Nutshell
Troubleshooting
Multiple branches containing the same commit
At a deeper technical level, Git branches aren’t separate entities, but labels
attached to a set of commit SHAs. When GitLab determines whether or not a branch has been
merged, it checks the target branch for the existence of those commit SHAs.
This behavior can cause unexpected results when two merge requests contain the same
commits. In this example, branches
B
and
C
both start from the same commit (
3
)
on branch
A
:
%%{init: { "fontFamily": "GitLab Sans" }}%%
gitGraph
accTitle: Diagram of multiple branches with the same commit
accDescr: Branches A and B contain the same commit, but branch B also contains other commits. Merging branch B makes branch A appear as merged, because all its commits are merged.
commit id:"a"
branch "branch A"
commit id:"b"
commit id:"c" type: HIGHLIGHT
branch "branch B"
commit id:"d"
checkout "branch A"
branch "branch C"
commit id:"e"
checkout main
merge "branch B" id:"merges commits b, c, d"
If you merge branch
B
, branch
A
also appears as merged (without any action from you)
because all commits from branch
A
now appear in the target branch
main
. Branch
C
remains unmerged, because commit
5
wasn’t part of branch
A
or
B
.
Merge request
A
remains merged, even if you attempt to push new commits
to its branch. If any changes in merge request
A
remain unmerged (because they
weren’t part of merge request
A
), open a new merge request for them.
Error: ambiguous
HEAD
branch exists
In versions of Git earlier than 2.16.0, you could create a branch named
HEAD
.
This branch named
HEAD
collides with the internal reference (also named
HEAD
)
Git uses to describe the active (checked out) branch. This naming collision can
prevent you from updating the default branch of your repository:
Error: Could not set the default branch. Do you have a branch named 'HEAD' in your repository?
To fix this problem:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Branches
.
Search for a branch named
HEAD
.
Make sure the branch has no uncommitted changes.
Select
Delete branch
, then
Yes, delete branch
.
Git versions
2.16.0 and later
,
prevent you from creating a branch with this name.
Find all branches you’ve authored
To find all branches you’ve authored in a project, run this command in a Git repository:
git
for
-each-ref --format
=
'%(authoremail) %(refname:short)'
|
grep
$(
git config --get user.email
)
To get a total of all branches in a project, sorted by author, run this command
in a Git repository:
git
for
-each-ref --format
=
'%(authoremail)'
|
sort
|
uniq -c
|
sort -g
Error:
Failed to create branch 4:Deadline Exceeded
This error is caused by a timeout in Gitaly. It occurs when creating a branch
take longer to complete than the configured timeout period.
To resolve this issue, choose one of the following:
Disable time-consuming
server hooks
.
Increase
Gitaly timeout
settings.
