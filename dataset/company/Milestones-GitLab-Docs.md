# Milestones | GitLab Docs

Source: https://docs.gitlab.com/user/project/milestones/

Milestones | GitLab Docs
Milestones
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Milestones help track and organize work in GitLab.
Milestones:
Group related issues, epics, and merge requests to track progress toward a goal.
Support time-based planning with optional start and due dates.
Work alongside iterations to track concurrent timeboxes.
Track releases and generate release evidence.
Apply to projects and groups.
Milestones can belong to a
project
or
group
.
Project milestones apply to issues and merge requests in that project only.
Group milestones apply to any issue, epic or merge request in that group’s projects.
For information about project and group milestones API, see:
Project Milestones API
Group Milestones API
Milestones as releases
Milestones can be used to track releases. To do so:
Set the milestone due date to represent the release date of your release.
If you do not have a defined start date for your release cycle, you can leave the milestone start
date blank.
Set the milestone title to the version of your release, such as
Version 9.4
.
Add issues to your release by selecting the milestone from the issue’s right sidebar.
Additionally, to automatically generate release evidence when you create your release, integrate
milestones with the
Releases feature
.
Project milestones and group milestones
A milestone can belong to
project
or
group
.
You can assign
project milestones
to issues or merge requests in that project only.
You can assign
group milestones
to any issue, epic, or merge request of any project in that group.
For information about project and group milestones API, see:
Project Milestones API
Group Milestones API
View project or group milestones
To view the milestone list:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Milestones
.
In a project, GitLab displays milestones that belong to the project.
In a group, GitLab displays milestones that belong to the group and all projects and subgroups in the group.
View milestones in a project with issues turned off
If a project has issue tracking
turned off
,
to get to the milestones page, enter its URL.
To do so:
Go to your project.
Add:
/-/milestones
to your project URL.
For example
https://gitlab.com/gitlab-org/sample-data-templates/sample-gitlab-project/-/milestones
.
Alternatively, this project’s issues are visible in the group’s milestone page.
Improving this experience is tracked in issue
339009
.
View all milestones
You can view all the milestones you have access to in the entire GitLab namespace.
You might not see some milestones because they’re in projects or groups you’re not a member of.
To do so:
On the left sidebar, select
Search or go to
. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Your work
.
On the left sidebar, select
Milestones
.
View milestone details
To view more information about a milestone,
in the
Milestones
page, select the title of the milestone you want to view.
The milestone view shows the title and description.
The tabs below the title and description show the following:
Work Items
: Shows all work items assigned to the milestone. Work items are displayed in three columns named:
Unstarted Issues (open and unassigned)
Ongoing Issues (open and assigned)
Completed Issues (closed)
Merge Requests
: Shows all merge requests assigned to the milestone. Merge requests are displayed in four columns named:
Work in progress (open and unassigned)
Waiting for merge (open and assigned)
Rejected (closed)
Merged
Participants
: Shows all assignees of issues assigned to the milestone.
Labels
: Shows all labels that are used in issues assigned to the milestone.
Burndown charts
The milestone view contains a
burndown and burnup chart
,
showing the progress of completing a milestone.
Milestone sidebar
The sidebar on the milestone view shows the following:
Percentage complete, which is calculated as number of closed work items divided by total number of work items.
The start date and due date.
The total time spent on all work items and merge requests assigned to the milestone.
The total issue weight of all work items assigned to the milestone.
The count of total, open, closed, and merged merge requests.
Links to associated releases.
The milestone’s reference you can copy to your clipboard.
Create a milestone
History
Changed
the minimum user role from Developer to Reporter in GitLab 15.0.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Introduced
milestones to Epic work items in GitLab 18.2.
You can create a milestone either in a project or a group.
Prerequisites:
You must have at least the Planner role for the project or group the milestone belongs to.
To create a milestone:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Milestones
.
Select
New milestone
.
Enter the title.
Optional. Enter description, start date, and due date.
Select
New milestone
.
Edit a milestone
History
Changed
the minimum user role from Developer to Reporter in GitLab 15.0.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Prerequisites:
You must have at least the Planner role for the project or group the milestone belongs to.
To edit a milestone:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Milestones
.
Select a milestone’s title.
In the upper-right corner, select
Milestone actions
(
ellipsis_v
) and then select
Edit
.
Edit the title, start date, due date, or description.
Select
Save changes
.
Close a milestone
History
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
A milestone closes after its due date.
You can also close a milestone manually.
When a milestone is closed, its open issues remain open.
Prerequisites:
You must have at least the Planner role for the project or group the milestone belongs to.
To close a milestone:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Milestones
.
Either:
Next to the milestone you want to close, select
Milestone actions
(
ellipsis_v
) >
Close
.
Select the milestone title, and then select
Close
.
Delete a milestone
History
Changed
the minimum user role from Developer to Reporter in GitLab 15.0.
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
Prerequisites:
You must have at least the Planner role for the project or group the milestone belongs to.
To delete a milestone:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Milestones
.
Either:
Next to the milestone you want to delete, select
Milestone actions
(
ellipsis_v
) >
Delete
.
Select the milestone title, and then select
Milestone actions
(
ellipsis_v
) >
Delete
.
Select
Delete milestone
.
Promote a project milestone to a group milestone
History
Changed
the minimum user role from Reporter to Planner in GitLab 17.7.
If you are expanding the number of projects in a group, you might want to share the same milestones
among this group’s projects.
You can promote project milestones to the parent group to
make them available to other projects in the same group.
Promoting a milestone merges all project milestones across all projects in this group with the same
name into a single group milestone.
All issues and merge requests that were previously assigned to one of these project
milestones become assigned to the new group milestone.
This action cannot be reversed and the changes are permanent.
Prerequisites:
You must have at least the Planner role for the group.
To promote a project milestone:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Plan
>
Milestones
.
Either:
Next to the milestone you want to promote, select
Milestone actions
(
ellipsis_v
) >
Promote
.
Select the milestone title, and then select
Milestone actions
(
ellipsis_v
) >
Promote
.
Select
Promote Milestone
.
Assign a milestone to an item
History
Ability to assign milestones to epics
introduced
in GitLab 18.2.
Every issue, epic, or merge request can be assigned one milestone.
The milestones are visible on every issue and merge request page, on the right sidebar.
They are also visible in the work item board.
To assign or unassign a milestone:
View an issue, an epic, or a merge request.
On the right sidebar, next to
Milestones
, select
Edit
.
In the
Assign milestone
list, search for a milestone by typing its name.
You can select from both project and group milestones.
Select the milestone you want to assign.
To assign or unassign a milestone, you can also:
Use the
/milestone
quick action
in a comment or description
Drag an issue to a
milestone list
in a board
Bulk edit issues
from the issues list
Filter issues and merge requests by milestone
Filters in list pages
You can filter by both group and project milestones from the project and group issue/merge request list pages.
Filters in issue boards
From
project issue boards
, you can filter by both group milestones and project
milestones in:
Search and filter bar
Issue board configuration
From
group issue boards
, you can filter by only group milestones in:
Search and filter bar
Issue board configuration
Special milestone filters
History
Logic for
Started
and
Upcoming
filters
changed
in GitLab 18.0.
When filtering by milestone, in addition to choosing a specific project milestone or group milestone, you can choose a special milestone filter.
None
: Show issues or merge requests with no assigned milestone.
Any
: Show issues or merge requests with an assigned milestone.
Upcoming
: Show issues or merge requests with an open assigned milestone starting in the future.
Started
: Show issues or merge requests with an open assigned milestone that overlaps with the current date. The
list excludes milestones without a defined start and due date.
