# Comments and threads | GitLab Docs

Source: https://docs.gitlab.com/user/discussions/

Comments and threads | GitLab Docs
Comments and threads
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Comments and threads on Wiki pages
introduced
in GitLab 17.7
with a flag
named
wiki_comments
. Disabled by default.
Comments and threads on Wiki pages
generally available
in GitLab 17.9. Feature flag
wiki_comments
removed.
GitLab encourages communication through comments, threads, and
suggesting changes for code
.
Comments support
Markdown
and
quick actions
.
Two types of comments are available:
A standard comment.
A comment in a thread, which you can
resolve
.
You can
suggest code changes
in your commit diff comment,
which the user can accept through the user interface.
Places you can add comments
You can create comments in places like:
Commit diffs.
Commits.
Designs.
Epics.
Issues.
Merge requests.
Snippets.
Tasks.
OKRs.
Wiki pages.
Each object can have as many as 5,000 comments.
Mentions
You can mention a user or a group (including
subgroups
) in your GitLab
instance with
@username
or
@groupname
. GitLab notifies all mentioned users with to-do items and emails.
Users can change this setting for themselves in the
notification settings
.
You can quickly see which comments involve you, because GitLab highlights
mentions for yourself (the current, authenticated user) in a different color.
Mentioning all members
History
Flag
named
disable_all_mention
introduced
in GitLab 16.1. Disabled by default.
Enabled on GitLab.com
.
The availability of this feature is controlled by a feature flag.
For more information, see the history.
Avoid mentioning
@all
in comments and descriptions.
@all
mentions more than
just the participants of the project, issue, or merge request, but all members
of that project’s parent group. All these users receive an email notification
and a to-do item, and might interpret it as spam.
When you enable this feature flag, typing
@all
in comments and descriptions
results in plain text instead of mentioning all users.
When you disable this feature, existing
@all
mentions in the Markdown texts are unchanged,
and remain as links. Only future
@all
mentions appear as plain text.
Notifications and mentions can be disabled in
a group’s settings
.
Mention a group in an issue or merge request
When you mention a group in a comment, every member of the group gets a to-do item
added to their to-do list.
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
For merge requests, select
Code
>
Merge requests
, and find your merge request.
For issues, select
Plan
>
Issues
, and find your issue.
In a comment, type
@
followed by the user, group, or subgroup namespace.
For example,
@alex
,
@alex-team
, or
@alex-team/marketing
.
Select
Comment
.
GitLab creates a to-do item for all the group and subgroup members.
For more information on mentioning subgroups, see
Mention subgroups
.
Add a comment to a merge request diff
When you add comments to a merge request diff, these comments persist, even when you:
Force-push after a rebase.
Amend a commit.
To add a commit diff comment:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Merge requests
, and find your merge request.
Select the
Commits
tab, then select the commit message.
Start a comment:
To comment on an entire file, find the file you want to comment on and,
in the file header, select
Comment on this file
(
comment
).
To comment on specific lines, find the line number you want to comment on. Hover over the line number,
then select
Comment
(
comment
). To select more lines, drag the
Comment
(
comment
) icon.
Enter your comment.
Submit your comment:
To add your comment immediately, select
Add comment now
, or use the keyboard shortcut:
macOS:
Shift
+
Command
+
Enter
All other OSes:
Shift
+
Control
+
Enter
To leave your comment unpublished until you finish a review, select
Start a review
, or use the keyboard shortcut:
macOS:
Command
+
Enter
All other OSes:
Control
+
Enter
The comment displays on the merge request’s
Overview
tab.
The comment is not displayed on your project’s
Code
>
Commits
page.
When your comment contains a reference to a commit included in the merge request,
it’s converted to a link in the context of the merge request.
For example,
28719b171a056960dfdc0012b625d0b47b123196
becomes
28719b17
that links to
https://gitlab.example.com/example-group/example-project/-/merge_requests/12345/diffs?commit_id=28719b171a056960dfdc0012b625d0b47b123196
.
Reply to a comment by sending email
If you have
“reply by email”
configured,
you can reply to comments by sending an email.
When you reply to a standard comment, it creates another standard comment.
When you reply to a threaded comment, it creates a reply in the thread.
When you
send an email to an issue email address
,
it creates a standard comment.
You can use
Markdown
and
quick actions
in your email replies.
Edit a comment
You can edit your own comment at any time.
Anyone with at least the Maintainer role can also edit a comment made by someone else.
To edit a comment:
On the comment, select
Edit comment
(
pencil
).
Make your edits.
Select
Save changes
.
Edit a comment to add a mention
By default, when you mention a user, GitLab
creates a to-do item
for them, and sends them a
notification email
.
If you edit an existing comment to add a user mention that wasn’t there before, GitLab:
Creates a to-do item for the mentioned user.
Does not send a notification email.
Prevent comments by locking the discussion
You can prevent public comments in an issue or merge request.
When you do, only project members can add and edit comments.
Prerequisites:
In merge requests, you must have at least the Developer role.
In issues, you must have at least the Planner role.
To lock an issue or merge request:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
For merge requests, select
Code
>
Merge requests
, and find your merge request.
For issues, select
Plan
>
Issues
, and find your issue.
In the upper-right corner, select
Merge request actions
or
Issue actions
(
ellipsis_v
), then select
Lock discussion
.
GitLab adds a system note to the page details.
You must unlock all locked discussions in closed issues or merge requests before you can
reopen the issue or merge request.
Comments on confidential items
Only users with permission to access a confidential item receive notifications for comments on the item.
If the item was not previously confidential, users without access may appear as participants. These users do not receive notifications while the item is confidential.
Who can be notified:
Users assigned to the item, regardless of role.
Users who authored the item, if they have at least the Guest role.
Users with at least a Planner role in the group or project the item belongs to.
Add an internal note
History
Introduced
for merge requests in GitLab 16.9.
Introduced
for GitLab Wiki in GitLab 18.2.
Use internal notes to protect information added to a public issue, epic, wiki page, or merge request.
Internal notes differ from public comments:
Only project members with least the Reporter role can view the internal note.
You can’t convert internal notes to regular comments.
All replies to internal notes are also internal.
Internal notes display an
Internal note
badge and are shown in a different
color than public comments:
Prerequisites:
You must have at least the Reporter role for the project.
To add an internal note:
On the issue, epic, wiki page, or merge request, in the
Comment
text box, enter a comment.
Below the comment, select
Make this an internal note
.
Select
Add internal note
.
You can also mark an entire
issue as confidential
,
or create
confidential merge requests
.
Show only comments
In discussions with many comments, filter the discussion to show only comments or history of
changes (
system notes
). System notes include changes to the description, mentions in other GitLab
objects, or changes to labels, assignees, and the milestone.
GitLab saves your preference, and applies it to every issue, merge request, or epic you view.
On a merge request, issue, or epic, select the
Overview
tab.
On the right side of the page, from the
Sort or filter
dropdown list, select a filter:
Show all activity
: Display all user comments and system notes.
Show comments only
: Display only user comments.
Show history only
: Display only activity notes.
Change activity sort order
Reverse the default order and interact with the activity feed sorted by most recent items
at the top. GitLab saves your preference in local storage and applies it to every issue,
merge request, or epic you view. Issues and epics share the same sorting preference, while merge requests maintain their own separate preference.
To change the activity sort order:
Open an issue, or open the
Overview
tab in a merge request or epic.
Scroll down to the
Activity
heading.
On the right side of the page, change the sort order:
Issues and epics
: From the
Sort or filter
dropdown list, select
Newest first
or
Oldest first
(default).
Merge requests
: Use the sort direction arrow button to toggle between
Sort direction: Ascending
(oldest first, default) or
Sort direction: Descending
(newest first).
View description change history
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
You can see changes to the description listed in the history.
To compare the changes, select
Compare with previous version
.
Assign an issue to the commenting user
You can assign an issue to a user who made a comment.
In the comment, select the
More Actions
(
ellipsis_v
) menu.
Select
Assign to comment author
.
To unassign the commenter, select the button again.
Create a thread by replying to a standard comment
When you reply to a standard comment, you create a thread.
Prerequisites:
You must have at least the Guest role.
You must be in an issue, merge request, or epic. Threads in commits and snippets are not supported.
To create a thread by replying to a comment:
In the upper-right corner of the comment, select
Reply to comment
(
reply
)
to display the reply section.
Enter your reply.
Select
Reply
or
Add comment now
(depending on where in the UI you are replying).
GitLab converts the top comment to a thread.
Create a thread without replying to a comment
You can create a thread without replying to a standard comment.
Prerequisites:
You must have at least the Guest role.
You must be in an issue, merge request, commit, or snippet.
To create a thread:
Enter a comment.
Below the comment, to the right of
Comment
, select the down arrow (
chevron-down
).
From the list, select
Start thread
.
Select
Start thread
again.
Resolve a thread
History
Resolvable threads for issues
introduced
in GitLab 16.3
with a flag
named
resolvable_issue_threads
. Disabled by default.
Resolvable threads for issues
enabled on GitLab.com and GitLab Self-Managed
in GitLab 16.4.
Resolvable threads for issues
generally available
in GitLab 16.7. Feature flag
resolvable_issue_threads
removed.
Resolvable threads for tasks, objectives, and key results
generally available
in GitLab 17.3.
Resolvable threads for epics
introduced
in GitLab 17.5.
The new look for epics
must be enabled.
Resolvable threads for epics
generally available
in GitLab 18.1.
When a conversation is complete, you can resolve the thread. Resolved threads are collapsed, but users can still add comments.
Resolved threads can be reopened later by any user who has permission to resolve threads. To reopen a resolved thread, expand the thread and select
Reopen thread
.
Prerequisites:
You must be in an epic, issue, task, objective, key result, or merge request.
You must have at least the Developer role or be the author of the issue or merge request.
To resolve a thread:
Go to the thread.
Do one of the following:
In the upper-right corner of the original comment, select
Resolve thread
(
check-circle
).
Below the last reply, in the
Reply
field, select
Resolve thread
.
Below the last reply, in the
Reply
field, enter text, select the
Resolve thread
checkbox, and select
Add comment now
.
The same actions can be performed to reopen a thread.
Merge requests provide more flexible
thread management options
,
such as:
Move open threads to a new issue.
Prevent merging until all threads are resolved.
Summarize issue discussions with Duo Chat
Tier
: Premium, Ultimate
Add-on
: GitLab Duo Enterprise, GitLab Duo with Amazon Q
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Model information
LLM for GitLab Self-Managed, GitLab Dedicated: Anthropic
Claude 3.5 Sonnet
LLM for GitLab.com: Anthropic
Claude 3.7 Sonnet
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Introduced
in GitLab 16.0 as an
experiment
.
Moved
to GitLab Duo and promoted to
beta
in GitLab 17.3
with a flag
named
summarize_notes_with_duo
. Disabled by default.
Enabled by default
in GitLab 17.4.
Changed to require GitLab Duo add-on in GitLab 17.6 and later.
Changed to include Premium in GitLab 18.0.
Generate a summary of discussions on an issue.
Watch an overview
Prerequisites:
You must have permission to view the issue.
To generate a summary of issue discussions:
In an issue, scroll to the
Activity
section.
Select
View summary
.
The comments in the issue are summarized in as many as 10 list items.
You can ask follow up questions based on the response.
Data usage: When you use this feature, the text of all comments on the issue are sent to
the large language model.
