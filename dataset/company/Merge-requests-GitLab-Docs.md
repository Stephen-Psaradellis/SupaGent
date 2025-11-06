# Merge requests | GitLab Docs

Source: https://docs.gitlab.com/user/project/merge_requests/

Merge requests | GitLab Docs
Merge requests
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Sidebar actions menu
changed
to also move actions on issues, incidents, and epics in GitLab 16.0.
Generally available
in GitLab 16.9. Feature flag
moved_mr_sidebar
removed.
Merge requests provide a central location for your team to review code, have discussions,
and track code changes.
To help describe why a change was made, link a merge request to an issue and
automatically close the issue when the merge request merges.
Merge requests help ensure subject matter experts review your proposed changes and
your organization’s security requirements are met.
When you create your merge request early in the development process, your team has time to catch bugs and code quality problems.
When viewing a merge request, you see:
A description of the request.
Code changes and inline code reviews.
Information about CI/CD pipelines.
Mergeability reports.
Comments.
The list of commits.
Create a merge request
Learn the various ways to
create a merge request
.
Use merge request templates
When you create a merge request, GitLab checks for the existence of a
description template
to add data to your merge request.
GitLab checks these locations in order from 1 to 5, and applies the first template
found to your merge request:
Name
Project UI
setting
Group
default.md
Instance
default.md
Project
default.md
No template
Standard commit message
1
2
3
4
5
Commit message with an issue closing pattern like
Closes #1234
1
2
3
4
5 *
Branch name
prefixed with an issue ID
, like
1234-example
1 *
2 *
3 *
4 *
5 *
Items marked with an asterisk (*) also append an
issue closing pattern
.
View merge requests
You can view merge requests for your project, group, or yourself.
You’re participating in
To view all merge requests on the homepage, use the
Shift
+
m
keyboard shortcut, or:
On the left sidebar, select the
Merge requests
icon.
or:
On the left sidebar, select
Search or go to
. If you’ve
turned on the new navigation
, this field is on the top bar.
From the dropdown list, select
Merge requests
.
For a project
To view all merge requests for a project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
.
Or, to use a keyboard shortcut, press
g
+
m
.
For all projects in a group
To view merge requests for all projects in a group:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
.
If your group contains subgroups, this view also displays merge requests from the subgroup projects.
For a file
When viewing a file in your repository, GitLab shows a badge with the number of open merge requests
that target the current branch and modify the file. This helps you identify files that have pending changes.
The availability of this feature is controlled by a feature flag.
For more information, see
View open merge requests for a file
.
To view the open merge requests for a file:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Go to the file you want to view.
In the upper right of the screen, next to the filename, look for the green badge with the number
of
merge-request-open
Open
merge requests.
Select the badge to see a list of open merge requests created in the past 30 days.
Select any merge request in the list to go to that merge request.
Filter the list of merge requests
History
Filtering by
source branch
introduced
in GitLab 16.6.
Filtering by
merged by
introduced
in GitLab 16.9. Available only when the feature flag
mr_merge_user_filter
is enabled.
Filtering by
merged by
generally available
in GitLab 17.0. Feature flag
mr_merge_user_filter
removed.
Filtering by
merged before
and
merged after
introduced
in GitLab 18.6.
To filter the list of merge requests:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
.
Above the list of merge requests, select
Search or filter results
.
From the dropdown list, select the attribute you wish to filter by. Some examples:
By environment or deployment date
.
ID
: Enter filter
#30
to return only merge request 30.
User filters: Type (or select from the dropdown list) any of these filters to display a list of users:
Approved by
, for merge requests already approved by a user. Premium and Ultimate only.
Approver
, for merge requests that this user is eligible to approve.
(For more information, read about
Code owners
). Premium and Ultimate only.
Merged by
, for merge requests merged by this user.
Reviewer
, for merge requests reviewed by this user.
Select or type the operator to use for filtering the attribute. The following operators are
available:
=
: Is
!=
: Is not
Enter the text to filter the attribute by.
You can filter some attributes by
None
or
Any
.
Repeat this process to filter by more attributes, joined by a logical
AND
.
Select a
Sort direction
, either
sort-lowest
for descending order,
or
sort-highest
for ascending order.
By environment or deployment date
To filter merge requests by deployment data, such as the environment or a date,
you can type (or select from the dropdown list) the following:
Environment
Deployed before
Deployed after
Projects using a
fast-forward merge method
do not return results, as this method does not create a merge commit.
When filtering by an environment, a dropdown list presents all environments that
you can choose from.
When filtering by
Deployed before
or
Deployed after
:
The date refers to when the deployment to an environment (triggered by the
merge commit) completed successfully.
You must enter the deploy date manually.
Deploy dates use the format
YYYY-MM-DD
. Wrap them in double quotes (
"
)
if you want to specify both a date and time (
"YYYY-MM-DD HH:MM"
).
Add changes to a merge request
If you have permission to add changes to a merge request, you can add your changes
to an existing merge request in several ways. These ways depend on the complexity of your
change, and whether you need access to a development environment:
Edit changes in the Web IDE
in your browser with the
.
keyboard shortcut. Use this
browser-based method to edit multiple files, or if you are not comfortable with Git commands.
You cannot run tests from the Web IDE.
Edit changes in Ona
, if you
need a fully-featured environment to both edit files, and run tests afterward. Ona
supports running the GitLab Development Kit (GDK).
To use Ona, you must enable Ona in your user account.
Push changes from the command line
, if you are
familiar with Git and the command line.
Assign a user to a merge request
To assign the merge request to a user, use the
/assign @user
quick action in a text area in
a merge request, or:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
and find your merge request.
On the right sidebar, expand the right sidebar and locate the
Assignees
section.
Select
Edit
.
Search for the user you want to assign, and select the user. GitLab Free allows one
assignee per merge request, but GitLab Premium and GitLab Ultimate allow multiple assignees:
GitLab adds the merge request to the user’s
Assigned merge requests
page.
Merge a merge request
During the merge request review process, reviewers provide
feedback on your changes. When a reviewer is satisfied with the changes,
they can enable
auto-merge
, even if some merge checks are failing.
After all merge checks pass, the merge request is automatically merged, without further action from you.
Default merge permissions:
The default branch, typically
main
, is protected.
Only Maintainers and higher roles can merge into the default branch.
Developers can merge any merge requests targeting non-protected branches.
To determine if you have permission to merge a specific merge request, GitLab checks:
Your role in the project. For example, Developer, Maintainer, or Owner.
The branch protections of the target branch.
Close a merge request
If you decide to permanently stop work on a merge request, close it rather than
deleting it
.
Prerequisites:
You must be the author or assignees of the merge request, or
You must have the Developer, Maintainer, or Owner role in a project.
To close merge requests in the project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
and find your merge request.
Scroll to the comment box at the bottom of the page.
Following the comment box, select
Close merge request
.
GitLab closes the merge request, but preserves records of the merge request,
its comments, and any associated pipelines.
Delete the source branch on merge
You can delete the source branch for a merge request:
When you create a merge request, by selecting
Delete source branch when merge request accepted
.
When you merge a merge request, if you have the Maintainer role, by selecting
Delete source branch
.
An administrator can make this option the default in the project’s settings.
The delete-branch action is performed by the user who sets auto-merge, or merges the merge request.
If the user lacks the correct role, such as in a forked project, the source branch deletion fails.
Update merge requests when target branch merges
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Merge requests are often chained together, with one merge request depending on
the code added or changed in another merge request. To support keeping individual
merge requests small, GitLab can update up to four open merge requests when their
target branch merges into
main
. For example:
Merge request 1: merge
feature-alpha
into
main
.
Merge request 2: merge
feature-beta
into
feature-alpha
.
If these merge requests are open at the same time, and merge request 1 (
feature-alpha
)
merges into
main
, GitLab updates the destination of merge request 2 from
feature-alpha
to
main
.
Merge requests with interconnected content updates are usually handled in one of these ways:
Merge request 1 merges into
main
first. Merge request 2 is then
retargeted to
main
.
Merge request 2 merges into
feature-alpha
. The updated merge request 1, which
now contains the contents of
feature-alpha
and
feature-beta
, merges into
main
.
This feature works only when a merge request is merged. Selecting
Remove source branch
after merging does not retarget open merge requests. This improvement is
proposed as a follow-up
.
Merge request workflows
For a software developer working in a team:
You check out a new branch, and submit your changes through a merge request.
You gather feedback from your team.
You work on the implementation optimizing code with
Code Quality reports
.
You verify your changes with
Unit test reports
in GitLab CI/CD.
You avoid using dependencies whose license is not compatible with your project with
License approval policies
.
You request the
approval
from your manager.
Your manager:
Pushes a commit with their final review.
Approves the merge request.
Sets it to
auto-merge
(formerly
Merge when pipeline succeeds
).
Your changes get deployed to production with
manual jobs
for GitLab CI/CD.
Your implementations were successfully shipped to your customer.
For a web developer writing a webpage for your company’s website:
You check out a new branch and submit a new page through a merge request.
You gather feedback from your reviewers.
You preview your changes with
review apps
.
You request your web designers for their implementation.
You request the approval from your manager.
After approval, GitLab:
Squashes
the commits.
Merges the commit.
Deployed the changes to staging with GitLab Pages
.
Your production team cherry-picks the merge commit into production.
Filter activity in a merge request
History
Feature flag
mr_activity_filters
enabled on GitLab.com
in GitLab 16.0.
Enabled on GitLab Self-Managed
in GitLab 16.3 by default.
Generally available
in GitLab 16.5. Feature flag
mr_activity_filters
removed.
Filtering bot comments
introduced
in GitLab 16.9.
To understand the history of a merge request, filter its activity feed to show you
only the items that are relevant to you.
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
.
Select a merge request.
Scroll to
Activity
.
On the right side of the page, select
Activity filter
to show the filter options.
If you’ve already selected filter options, this field shows a summary of your
choices, like
Activity + 5 more
.
Select the types of activity you want to see. Options include:
Assignees & Reviewers
Approvals
Comments (from bots)
Comments (from users)
Commits & branches
Edits
Labels
Lock status
Mentions
Merge request status
Tracking
Optional. Select
Sort
(
sort-lowest
) to reverse the sort order.
Your selection persists across all merge requests. You can also change the
sort order by clicking the sort button on the right.
Manage comment threads
Discussions in a merge request include single comments, and threads of comments. Open (unresolved)
threads block the merge of a merge request, but single comments do not. When a thread’s discussion
is finished,
resolve the thread
to collapse its display.
If a comment thread is important but should not block the merge request, move it to an issue to
continue the discussion.
Expand all threads
GitLab shows the number of open threads in the upper-right corner of a
merge request. This merge request has three open threads:
To see all comments in the collapsed threads, expand the threads:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
and find your merge request.
In the merge request, in the upper right, find the
Open threads
dropdown list, and select
Thread options
(
ellipsis_v
).
Select
Show all comments
.
Move open threads to an issue
To move open threads to a new issue, and unblock a merge request:
Move one thread
If you have one specific open thread in a merge request, you can
create an issue to resolve it separately:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
and find your merge request.
In the merge request, find the thread you want to move.
Below the last reply to the thread, next to
Resolve thread
, select
Create issue to resolve thread
(
issue-new
).
Fill out the fields in the new issue, and select
Create issue
.
GitLab marks the thread as resolved, and adds a link from the merge request to
the newly created issue.
Move all open threads
If you have multiple open threads in a merge request, you can
create an issue to resolve them separately:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
and find your merge request.
In the merge request, in the upper right, find the
Open threads
dropdown list, and select
Thread options
(
ellipsis_v
).
Select
Resolve all with new issue
.
Fill out the fields in the new issue, and select
Create issue
.
GitLab marks all threads as resolved, and adds a link from the merge request to
the newly created issue.
Prevent merge unless all threads are resolved
You can prevent merge requests from merging while threads remain open.
When you enable this setting, the
Open threads
counter in a merge request
is shown in orange while at least one thread remains open.
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
In the
Merge checks
section, select the
All threads must be resolved
checkbox.
Select
Save changes
.
Automatically resolve threads in a merge request when they become outdated
You can set merge requests to automatically resolve threads when a new push
changes the lines they describe.
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
In the
Merge options
section, select
Automatically resolve merge request diff threads when they become outdated
.
Select
Save changes
.
Threads are now resolved if a push makes a diff section outdated.
Threads on lines that don’t change and top-level resolvable threads are not resolved.
Move notifications and to-dos
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
History
Introduced
in GitLab 16.5
with a flag
named
notifications_todos_buttons
. Disabled by default.
Issues, incidents
, and
epics
also updated.
The availability of this feature is controlled by a feature flag.
For more information, see the history.
Enabling this feature flag moves the notifications and to-do item buttons to the upper-right corner of the page.
On merge requests, these buttons are shown to the far right of the tabs.
On issues, incidents, and epics, these buttons are shown at the top of the right sidebar.
Related topics
Protect your repository
Review a merge request
Authorization for merge requests
Testing and reports
Comments and threads
Suggest code changes
CI/CD pipelines
Push options
for merge requests
