# Subgroups | GitLab Docs

Source: https://docs.gitlab.com/user/group/subgroups/

Subgroups | GitLab Docs
Subgroups
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
You can organize GitLab
groups
into subgroups. You can use subgroups to:
Separate internal and external content. Because every subgroup can have its own
visibility level
, you can host groups for different
purposes under the same parent group.
Organize large projects. You can use subgroups to manage who can access parts of
the source code.
Manage permissions. Give a user a different
role
for each group they’re
a member of
.
Subgroups can:
Belong to one immediate parent group.
Have many subgroups.
Be nested up to 20 levels.
Use
runners
registered to parent groups:
Secrets configured for the parent group are available to subgroup jobs.
Users with at least the Maintainer role in projects that belong to subgroups can see the details of runners registered to
parent groups.
For example:
%%{init: { "fontFamily": "GitLab Sans" }}%%
graph TD
accTitle: Parent and subgroup nesting
accDescr: How parent groups, subgroups, and projects nest.
subgraph "Parent group"
subgraph "Subgroup A"
subgraph "Subgroup A1"
G["Project E"]
end
C["Project A"]
D["Project B"]
E["Project C"]
end
subgraph "Subgroup B"
F["Project D"]
end
end
View subgroups of a group
Prerequisites:
To view private nested subgroups, you must be a direct or inherited member of
the private subgroup.
To view the subgroups of a group:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select the
Subgroups and projects
tab.
Select the subgroup you want to view.
To view nested subgroups, expand (
chevron-down
) a subgroup.
Private subgroups in public parent groups
In the hierarchy list, public groups with private subgroups have an expand option (
chevron-down
),
which indicates the group has nested subgroups. All users can view the expand option (
chevron-down
), but only direct or inherited members of the private subgroup can view the private group.
If you prefer to keep information about the presence of nested subgroups private,
you should add private subgroups only to private parent groups.
Create a subgroup
Prerequisites:
You must have either:
At least the Maintainer role for a group.
The
role determined by a setting
. These users can create
subgroups even if group creation is
disabled by an Administrator
in the user’s settings.
You cannot host a GitLab Pages subgroup website with a top-level domain name. For example,
subgroupname.example.io
.
To create a subgroup:
On the left sidebar, select
Search or go to
and find the group you want to create the subgroup in. If you’ve
turned on the new navigation
, this field is on the top bar.
On the parent group’s overview page, in the upper-right corner, select
New subgroup
.
Fill in the fields. View a list of
reserved names
that cannot be used as group names.
Select
Create subgroup
.
Change who can create subgroups
Prerequisites:
You must have at least the Maintainer role on the group, depending on the group’s setting.
To change who can create subgroups on a group:
As a user with the Owner role on the group:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand
Permissions and group features
.
From
Roles allowed to create subgroups
, select an option.
Select
Save changes
.
As an administrator:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
On the left sidebar, select
Overview
>
Groups
and find your group.
In the group’s row, select
Edit
.
From the
Allowed to create subgroups
dropdown list, select an option.
Select
Save changes
.
For more information, view the
permissions table
.
Subgroup membership
History
Changed
to display invited group members on the Members tab of the Members page in GitLab 16.10
with a flag
named
webui_members_inherited_users
. Disabled by default.
Enabled on GitLab.com and GitLab Self-Managed
in GitLab 17.0.
Feature flag
webui_members_inherited_users
removed
in GitLab 17.4. Members of invited groups displayed by default.
When you add a member to a group, that member is also added to all subgroups of that group.
The member’s permissions are inherited from the group into all subgroups.
Subgroup members can be:
Direct members
of the subgroup.
Inherited members
of the subgroup from the subgroup’s parent group.
Members of a group that was
shared with the subgroup’s top-level group
.
Indirect members
include inherited members and members of a group that was
invited to the subgroup or its ancestors
.
%%{init: { "fontFamily": "GitLab Sans" }}%%
flowchart RL
accTitle: Subgroup membership
accDescr: How users become members of a subgroup - through direct, indirect, or inherited membership.
subgraph Group A
A(Direct member)
B{{Shared member}}
subgraph Subgroup A
H(1#46; Direct member)
C{{2#46; Inherited member}}
D{{Inherited member}}
E{{3#46; Shared member}}
end
A-->|Direct membership of Group A\nInherited membership of Subgroup A|C
end
subgraph Group C
G(Direct member)
end
subgraph Group B
F(Direct member)
end
F-->|Group B\nshared with\nGroup A|B
B-->|Inherited membership of Subgroup A|D
G-->|Group C shared with Subgroup A|E
Group permissions for a member can be changed only by:
Users with the Owner role on the group.
Changing the configuration of the group the member was added to.
Determine membership inheritance
To see if a member has inherited the permissions from a parent group:
On the left sidebar, select
Search or go to
and find your group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Manage
>
Members
.
The member’s inheritance is displayed in the
Source
column.
Members list for an example subgroup
Four
:
In the previous screenshot:
Five members have access to group
Four
.
User 0 has the Reporter role on group
Four
, and has inherited their permissions from group
One
:
User 0 is a direct member of group
One
.
Group
One
is above group
Four
in the hierarchy.
User 1 has the Developer role on group
Four
and inherited their permissions from group
Two
:
User 0 is a direct member of group
Two
, which is a subgroup of group
One
.
Groups
One
/
Two
are above group
Four
in the hierarchy.
User 2 has the Developer role on group
Four
and has inherited their permissions from group
Three
:
User 0 is a direct member of group
Three
, which is a subgroup of group
Two
. Group
Two
is a subgroup of group
One
.
Groups
One
/
Two
/
Three
are above group
Four
the hierarchy.
User 3 is a direct member of group
Four
. This means they get their Maintainer role directly from group
Four
.
Administrator has the Owner role on group
Four
and is a member of all subgroups. For that reason, as with User 3,
the
Source
column indicates they are a direct member.
Members can be
filtered by inherited or direct membership
.
Override ancestor group membership
Users with the Owner role in a subgroup can add members to it.
You can’t give a user a role in a subgroup that is lower than the roles the user has in parent groups.
To override a user’s role in a parent group, add the user to the subgroup again with a higher role.
For example:
If User 1 is added to group
Two
with the Developer role, User 1 inherits that role in every subgroup of group
Two
.
To give User 1 the Maintainer role in group
Four
(under
One / Two / Three
), add User 1 again to group
Four
with
the Maintainer role.
If User 1 is removed from group
Four
, the user’s role falls back to their role in group
Two
. User 1 has the Developer
role in group
Four
again.
Mention subgroups
Mentioning subgroups (
@<subgroup_name>
) in epics, issues, commits, and merge requests
notifies all direct members of that group. Inherited members of a subgroup are not notified by mentions.
Mentioning works the same as for projects and groups, and you can choose the group of members to be notified.
