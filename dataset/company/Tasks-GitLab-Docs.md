# Tasks | GitLab Docs

Source: https://docs.gitlab.com/user/tasks/

Tasks | GitLab Docs
Tasks
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab 14.5
with a flag
named
work_items
. Disabled by default.
Creating, editing, and deleting tasks
introduced
in GitLab 15.0.
Enabled on GitLab.com and GitLab Self-Managed
in GitLab 15.3.
The availability of this feature is controlled by a feature flag.
For more information, see the history.
A task in GitLab is a planning item that can be created in an issue.
Use tasks to break down user stories captured in
issues
into
smaller, trackable items.
When planning an issue, you need a way to capture and break down technical
requirements or steps necessary to complete it. An issue with related tasks is better defined,
and so you can provide a more accurate issue weight and completion criteria.
For the latest updates, check the
Tasks roadmap
.
Tasks are a type of work item, a step towards
default issue types
in GitLab.
For the roadmap of migrating issues and
epics
to work items and adding custom work item types, see
epic 6033
or the
Plan direction page
.
View tasks
View tasks in issues, in the
Child items
section.
You can also
filter the list of issues
for
Type = task
.
If you select a task from an issue, it opens in a dialog window.
If you select a task to open in a new browser tab, or select it from the issue list,
the task opens in a full-page view.
Create a task
History
Option to select the project where tasks are created
introduced
in GitLab 17.1.
Prerequisites:
You must have at least the Guest role for the project, or the project must be public.
To create a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select
Add
.
Select
New task
.
Enter the task title.
Select the
project
to create the new task in.
Select
Create task
.
From a task list item
History
Introduced
in GitLab 15.9.
Prerequisites:
You must have at least the Guest role for the project.
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, hover over a task list item and select the options menu (
ellipsis_v
).
Select
Convert to task
.
The task list item is removed from the issue description and a task is created in the tasks widget from its contents.
Any nested task list items are moved up a nested level.
Add existing tasks to an issue
History
Introduced
in GitLab 15.6.
Prerequisites:
You must have at least the Guest role for the project, or the project must be public.
To add a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select
Add
.
Select
Existing task
.
Search tasks by title.
Select one or multiple tasks to add to the issue.
Select
Add task
.
Edit a task
History
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Prerequisites:
You must have at least the Planner role for the project.
To edit a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the task you want to edit.
The task window opens.
Optional. To edit the title, select it and make your changes.
Optional. To edit the description, select the edit icon (
pencil
), make your changes, and
select
Save
.
Select the close icon (
close
).
Using the rich text editor
History
Rich text editing in the dialog view
introduced
in GitLab 15.6
with a flag
named
work_items_mvc
. Disabled by default.
Rich text editing in the full page view
introduced
in GitLab 15.7.
Generally available
in GitLab 16.2. Feature flag
work_items_mvc
removed.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Use a rich text editor to edit a task’s description.
Prerequisites:
You must have at least the Planner role for the project.
To edit the description of a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
Next to
Description
, select the edit icon (
pencil
). The description text box appears.
Above the text box, select
Rich text
.
Make your changes, and select
Save
.
Promote a task to an issue
History
Introduced
in GitLab 16.1.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Prerequisites:
You must have at least the Planner role for the project.
To promote a task to an issue:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the task you want to edit.
The task window opens.
Unlink the parent issue and promote the task: In the task window, use these two
quick actions
in separate comments:
/remove_parent
/promote_to issue
The task is converted to an issue and gets a new URL with
/issues/
.
The previous URL with
/work_items/
still works.
Convert a task into another item type
History
Introduced
in GitLab 17.8
with a flag
named
work_items_beta
. Disabled by default.
Moved
to the flag
named
okrs_mvc
. For current flag state, see the top of this page.
Convert a task into another item type, such as:
Issue
Objective
Key result
Changing the type might result in data loss if the target type does not support all fields from the original type.
Prerequisites:
The task you want to convert must not have a parent item assigned.
To convert a task into another item type:
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
Optional. If the task has a parent issue assigned, remove it.
Add a comment to the task with the
/remove_parent
quick action.
In the upper-right corner, select
More actions
(
ellipsis_v
), then select
Change type
.
Select the desired item type.
If all conditions are met, select
Change type
.
Alternatively, you can use the
/type
quick action
, followed
by
issue
,
objective
or
key result
in a comment.
Remove a task from an issue
History
Minimum required role
changed
from Reporter to Guest in GitLab 17.0.
Prerequisites:
You must have at least the Guest role for the project.
You can remove a task from an issue. The task is not deleted, but the two are no longer connected.
It’s not possible to connect them again.
To remove a task from an issue:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the options menu (
ellipsis_v
)
next to the task you want to remove.
Select
Remove task
.
Delete a task
History
Changed
the minimum user role from Owner to Planner in GitLab 17.7.
Prerequisites:
You must either:
Be the author of the task and have at least the Guest role for the project.
Have the Planner or Owner role for the project.
To delete a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the task you want to edit.
In the task window, in the options menu (
ellipsis_v
), select
Delete task
.
Select
OK
.
Reorder tasks
History
Introduced
in GitLab 16.0.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Prerequisites:
You must have at least the Planner role for the project.
By default, tasks are ordered by creation date.
To reorder them, drag them around.
Change status
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab 18.2
with a flag
named
work_item_status_feature_flag
. Enabled by default.
Generally available
in GitLab 18.4. Feature flag
work_item_status_feature_flag
removed.
You can assign a status to tasks to track their progress through your workflow. Status provides more granular tracking than the basic open/closed states, allowing you to use specific stages like
In progress
,
Done
, or
Won’t do
.
For more information about status, including how to configure custom statuses, see
Status
.
Prerequisites:
You must have at least the Planner role for the project, be the author of the task, or be assigned to the task.
To change the status of a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your task to view it.
On the right sidebar, in the
Status
section, select
Edit
.
From the dropdown list, select the status.
The task’s status updates immediately.
You can also set the status by using the
/status
quick action
.
Assign users to a task
History
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
To show who is responsible for a task, you can assign users to it.
Users on GitLab Free can assign one user per task.
Users on GitLab Premium and Ultimate can assign multiple users to a single task.
See also
multiple assignees for issues
.
Prerequisites:
You must have at least the Planner role for the project.
To change the assignee on a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
Next to
Assignees
, select
Add assignees
.
From the dropdown list, select the users to add as an assignee.
Select any area outside the dropdown list.
Assign labels to a task
History
Introduced
in GitLab 15.5.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Prerequisites:
You must have at least the Planner role for the project.
To add
labels
to a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit. The task window opens.
Next to
Labels
, select
Add labels
.
From the dropdown list, select the labels to add.
Select any area outside the dropdown list.
Set a start and due date
History
Introduced
in GitLab 15.4
with a flag
named
work_items_mvc_2
. Disabled by default.
Generally available
in GitLab 15.5. Feature flag
work_items_mvc_2
removed.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
You can set a
start and due date
on a task.
Prerequisites:
You must have at least the Planner role for the project.
You can set start and due dates on a task to show when work should begin and end.
To set a due date:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
If the task already has a due date next to
Due date
, select it. Otherwise, select
Add due date
.
In the date picker, select the desired due date.
To set a start date:
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
If the task already has a start date next to
Start date
, select it. Otherwise, select
Add start date
.
In the date picker, select the desired due date.
The due date must be the same or later than the start date.
If you select a start date to be later than the due date, the due date is then changed to the same day.
Add a task to a milestone
History
Introduced
in GitLab 15.5
with a flag
named
work_items_mvc_2
. Disabled by default.
Moved
to feature flag named
work_items_mvc
in GitLab 15.7. Disabled by default.
Generally available
in GitLab 15.7. Feature flag
work_items_mvc
removed.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
You can add a task to a
milestone
.
You can see the milestone title when you view a task.
If you create a task for an issue that already belongs to a milestone,
the new task inherits the milestone.
Prerequisites:
You must have at least the Planner role for the project.
To add a task to a milestone:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
Next to
Milestone
, select
Add to milestone
.
If a task already belongs to a milestone, the dropdown list shows the current milestone.
From the dropdown list, select the milestone to be associated with the task.
Set task weight
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab 15.3.
Edit button
introduced
in GitLab 16.7.
Prerequisites:
You must have at least the Reporter role for the project.
You can set weight on each task to show how much work it needs.
This value is visible only when you view a task.
To set issue weight of a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
Next to
Weight
, select
Edit
.
Enter a whole, positive number.
Select
Apply
or press
Enter
.
View count and weight of tasks in the parent issue
History
Introduced
in GitLab 18.3
with a flag
named
use_cached_rolled_up_weights
. Disabled by default.
Enabled on GitLab.com
in GitLab 18.4.
Generally available
in GitLab 18.6. Feature flag
use_cached_rolled_up_weights
removed.
The number of descendant tasks and their total weight is displayed in the issue
description, in the
Child items
section header.
To see the number of open and closed tasks:
In the section header, hover over the total counts.
The numbers reflect all child tasks associated with the issue, including those you might
not have permission to view.
View progress of the parent issue
History
Introduced
in GitLab 18.3
with a flag
named
use_cached_rolled_up_weights
. Disabled by default.
Enabled on GitLab.com
in GitLab 18.4.
Generally available
in GitLab 18.6. Feature flag
use_cached_rolled_up_weights
removed.
The issue progress percentage is displayed in the issue description, in the
Child items
section header.
To see the completed and total weight of child tasks:
In the section header, hover over the percentage.
The weights and progress reflect all tasks associated with the issue, including those you might
not have permission to view.
Add a task to an iteration
Tier
: Premium, Ultimate
History
Introduced
in GitLab 15.5
with a flag
named
work_items_mvc_2
. Disabled by default.
Moved
to feature flag named
work_items_mvc
in GitLab 15.7. Disabled by default.
Generally available
in GitLab 15.7. Feature flag
work_items_mvc
removed.
You can add a task to an
iteration
.
You can see the iteration title and period only when you view a task.
Prerequisites:
You must have at least the Reporter role for the project.
To add a task to an iteration:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
Next to
Iteration
, select
Add to iteration
.
From the dropdown list, select the iteration to be associated with the task.
Estimate and track spent time
History
Introduced
in GitLab 17.0.
You can estimate and track the time you spend on a task.
For more information, see
Time tracking
.
Prevent truncating descriptions with
Read more
History
Introduced
in GitLab 17.10.
If a task description is long, GitLab displays only part of it.
To see the whole description, you must select
Read more
.
This truncation makes it easier to find other elements on the page without scrolling through lengthy text.
To change whether descriptions are truncated:
On a task, in the upper-right corner, select
More actions
(
ellipsis_v
).
Toggle
Truncate descriptions
according to your preference.
This setting is remembered and affects all issues, tasks, epics, objectives, and key results.
Hide the right sidebar
History
Introduced
in GitLab 17.10.
Task attributes are shown in a sidebar to the right of the description when space allows.
To hide the sidebar and increase space for the description:
On a task, in the upper-right corner, select
More actions
(
ellipsis_v
).
Select
Hide sidebar
.
This setting is remembered and affects all issues, tasks, epics, objectives, and key results.
To show the sidebar again:
Repeat the previous steps and select
Show sidebar
.
View task system notes
History
Introduced
in GitLab 15.7
with a flag
named
work_items_mvc_2
. Disabled by default.
Moved
to feature flag named
work_items_mvc
in GitLab 15.8. Disabled by default.
Changing activity sort order
introduced
in GitLab 15.8.
Filtering activity
introduced
in GitLab 15.10.
Generally available
in GitLab 15.10. Feature flag
work_items_mvc
removed.
You can view all the system notes related to the task. By default they are sorted by
Oldest first
.
You can always change the sorting order to
Newest first
, which is remembered across sessions.
You can also filter activity by
Comments only
and
History only
in addition to the default
All activity
which is remembered across sessions.
Comments and threads
You can add
comments
and reply to threads in tasks.
Copy task reference
History
Introduced
in GitLab 16.1.
To refer to a task elsewhere in GitLab, you can use its full URL or a short reference, which looks like
namespace/project-name#123
, where
namespace
is either a group or a username.
To copy the task reference to your clipboard:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select your task.
In the upper-right corner, select the vertical ellipsis (
ellipsis_v
), then select
Copy Reference
.
You can now paste the reference into another description or comment.
For more information about task references, see
GitLab-Flavored Markdown
.
Copy task email address
History
Introduced
in GitLab 16.1.
You can create a comment in a task by sending an email.
Sending an email to this address creates a comment that contains the email body.
For more information about creating comments by sending an email and the necessary configuration, see
Reply to a comment by sending email
.
To copy the task’s email address:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the upper-right corner, select the vertical ellipsis (
ellipsis_v
), then select
Copy task email address
.
Set an issue as a parent
History
Introduced
in GitLab 16.5.
Prerequisites:
You must have at least the Guest role for the project.
The issue and task must belong to the same project.
To set an issue as a parent of a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select the title of the task you want to edit.
The task window opens.
Next to
Parent
, from the dropdown list, select the parent to add.
Select any area outside the dropdown list.
To remove the parent item of the task,
next to
Parent
, select the dropdown list and then select
Unassign
.
Confidential tasks
History
Introduced
in GitLab 15.3.
Confidential tasks are tasks visible only to members of a project with
sufficient permissions
.
You can use confidential tasks to keep security vulnerabilities private or prevent surprises from
leaking out.
Make a task confidential
By default, tasks are public.
You can make a task confidential when you create or edit it.
Prerequisites:
You must have at least the Reporter role for the project.
If the task has a parent issue which is non-confidential, and you want to make the issue confidential,
you must first make all the child tasks confidential.
A
confidential issue
can have only confidential children.
In a new task
When you create a new task, a checkbox right below the text area is available to mark the
task as confidential.
Check that box and select
Create task
.
In an existing task
To change the confidentiality of an existing task:
Open the task
.
In the upper-right corner, select the vertical ellipsis (
ellipsis_v
).
Select
Turn on confidentiality
.
Who can see confidential tasks
When a task is made confidential, only users with at least the Reporter role for the project have
access to the task.
Users with Guest or
Minimal
roles can’t access
the task even if they were actively participating before the change.
However, a user with the
Guest role
can create confidential tasks, but can only view the ones
that they created themselves.
Users with the Guest role or non-members can read the confidential task if they are assigned to the task.
When a Guest user or non-member is unassigned from a confidential task, they can no longer view it.
Confidential tasks are hidden in search results for users without the necessary permissions.
Confidential task indicators
Confidential tasks are visually different from regular tasks in a few ways.
Wherever tasks are listed, you can see the confidential (
eye-slash
) icon
next to the tasks that are marked as confidential.
If you don’t have
enough permissions
,
you cannot see confidential tasks at all.
Likewise, while inside the task, you can see the confidential (
eye-slash
) icon right next to
the breadcrumbs.
Every change from regular to confidential and vice versa, is indicated by a
system note in the task’s comments, for example:
eye-slash
Jo Garcia made the issue confidential 5 minutes ago
eye
Jo Garcia made the issue visible to everyone just now
Lock discussion
History
Introduced
in GitLab 16.9
with a flag
named
work_items_beta
. Disabled by default.
Feature flag
work_items_beta
removed
in GitLab 18.6.
The availability of this feature is controlled by a feature flag.
For more information, see the history.
This feature is available for testing, but not ready for production use.
You can prevent public comments in a task.
When you do, only project members can add and edit comments.
Prerequisites:
You must have at least the Reporter role.
To lock a task:
In the upper-right corner, select the vertical ellipsis (
ellipsis_v
).
Select
Lock discussion
.
A system note is added to the page details.
If a task is closed with a locked discussion, then you cannot reopen it until the discussion is unlocked.
Two-column layout
History
Introduced
in GitLab 16.2
with a flag
named
work_items_mvc_2
. Disabled by default. This feature is in
beta
.
Moved
to feature flag named
work_items_beta
in GitLab 16.10. Disabled by default.
Moved
out of feature flag
work_items_beta
in GitLab 17.0.
Tasks use a two-column layout, similar to issues.
The description and threads are on the left, and attributes, such as labels
or assignees, on the right.
This feature is in
beta
.
If you find a bug,
comment on the feedback issue
.
Linked items in tasks
History
Introduced
in GitLab 16.5
with a flag
named
linked_work_items
. Disabled by default.
Enabled on GitLab.com and GitLab Self-Managed
in GitLab 16.7.
Adding related items by entering their URLs and IDs
introduced
in GitLab 16.8.
Generally available
in GitLab 17.0. Feature flag
linked_work_items
removed.
Changed
minimum required role from Reporter (if true) to Guest in GitLab 17.0.
Linked items are a bi-directional relationship and appear in a block below
the emoji reactions section. You can link an objective, key result, or a task in the same project with each other.
The relationship only shows up in the UI if the user can see both items.
Add a linked item
Prerequisites:
You must have at least the Guest role for the project.
To link an item to a task:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select your task.
In the
Linked items
section of a task,
select
Add
.
Select the relationship between the two items. Either:
relates to
blocks
is blocked by
Enter the search text of the item, URL, or its reference ID.
When you have added all the items to be linked, select
Add
below the search box.
When you have finished adding all linked items, you can see
them categorized so their relationships can be better understood visually.
Remove a linked item
Prerequisites:
You must have at least the Guest role for the project.
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Issues
, then select your issue to view it.
In the issue description, in the
Child items
section, select your task.
In the
Linked items
section of a task, next to each item, select the vertical
ellipsis (
ellipsis_v
) and then select
Remove
.
Due to the bi-directional relationship, the relationship no longer appears in either item.
Add a merge request and automatically close tasks
History
Introduced
in GitLab 17.3.
You can set a task to close when a merge request merges.
Prerequisites:
You must have at least a Developer role for the project containing the merge request.
You must have at least a Reporter role for the project containing the task.
Edit your merge request.
In the
Description
box, find and add the task.
Use the
closing pattern
that you would for adding a merge request to an issue.
If your task is in the same project as your merge request, you can search for your task by typing
#
followed by the task’s ID or title.
If your task is in a different project, with a task open, copy the URL from the browser or
copy the task’s reference by selecting the vertical ellipsis (
ellipsis_v
) in the upper-right corner, then
Copy Reference
.
The merge requests are now visible in the main body, in the
Development
section.
You must use the exact closing pattern to add the merge request to the task. Other text will not work.
If
automatic issue closing
is enabled in your project settings, the task will be automatically closed when either:
The added merge request is merged.
A commit referencing a task with the closing pattern is committed to your project’s default branch.
Related topics
Create a merge request from a task
