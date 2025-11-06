# Protected tags | GitLab Docs

Source: https://docs.gitlab.com/user/project/protected_tags/#prevent-tag-creation-with-the-same-name-as-branches

Protected tags | GitLab Docs
Protected tags
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Protected
tags
:
Allow control over who has permission to create tags.
Prevent accidental update or deletion once created.
Each rule allows you to match either:
An individual tag name.
Wildcards to control multiple tags at once.
This feature evolved out of
protected branches
.
To create or delete a protected tag, you must be in the
Allowed to create or delete
list for that protected tag.
Configuring protected tags
Prerequisites:
You must have at least the Maintainer role for the project.
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
Protected tags
.
Select
Add new
.
To protect a single tag, select
Tag
, then choose your tag from the dropdown list.
To protect all tags with names matching a string:
Select
Tag
.
Enter the string to use for tag matching. Wildcards (
*
) are supported.
Select
Create wildcard
.
In
Allowed to create
, select roles that may create protected tags.
In GitLab Premium and Ultimate, you can also add groups or individual users
to
Allowed to create
.
Select
Protect
.
The protected tag (or wildcard) displays in the
Protected tags
list.
Add a group to protected tags
To set the members of a group or subgroup as Allowed to create protected tags:
On the left sidebar, select
Search or go
to and find your project.
Select
Settings
>
Repository
.
Expand
Protected tags
.
Add groups to the following field:
# Allow group members to create protected tags
Allowed to create: @group-x
Group inheritance and eligibility
%%{init: { "fontFamily": "GitLab Sans" }}%%
graph TD
accTitle: Diagram of group inheritance for protected tags
accDescr: If a project is shared with a group, the group members inherit permissions for protected tags.
A[Parent group X] -->|owns| B[Project A]
A -->|contains| C[Subgroup Y]
B -->|shared with| C
C -->|members inherit permissions| B
In this example:
Parent group X (
group-x
) owns Project A.
Parent group X also contains a subgroup, Subgroup Y. (
group-x/subgroup-y
)
Project A is shared with Subgroup Y.
The eligible groups for protected tag permissions are:
Project A: Both Group X and Subgroup Y, because Project A is shared with Subgroup Y.
Share projects with groups for protected tag permissions
You can share the project with a group or subgroup so that their members are
eligible for protected tag permissions.
%%{init: { "fontFamily": "GitLab Sans" }}%%
graph LR
accTitle: Diagram of project sharing for protected tag permissions
accDescr: Sharing a project with a group affects whether their members can have protected tag permissions.
A[Parent group X] -->|owns| B[Project A]
A -->|also contains| C[Subgroup Y]
C -.->D{Share Project A<br/>with Subgroup Y?} -.->|yes| E[Members of Subgroup Y<br/>can have protected<br/>tag permissions]
D{Share Project A<br/>with Subgroup Y?} -.->|no| F[Members of Subgroup Y<br />cannot have protected<br/>tag permissions]
E -.->|Add Subgroup Y<br/> to protected tag settings| I[Subgroup Y members<br/>can create tags] -.-> B
F -.-> |Add Subgroup Y<br/> to protected tag settings| J[Settings will not<br/>take effect] -.-> B
To grant access to Subgroup Y members for Project A, you must share the project with the subgroup.
Adding the subgroup directly to the protected tag settings is not effective and isn’t applicable to subgroup members.
For a group to have protected tag permissions, the project must be directly shared with the group.
Inherited project membership from parent groups is not sufficient for protected tag permissions.
Wildcard protected tags
You can specify a wildcard protected tag, which protects all tags
matching the wildcard. For example:
Wildcard Protected Tag
Matching Tags
v*
v1.0.0
,
version-9.1
*-deploy
march-deploy
,
1.0-deploy
*gitlab*
gitlab
,
gitlab/v1
*
v1.0.1rc2
,
accidental-tag
Two different wildcards can potentially match the same tag. For example,
*-stable
and
production-*
would both match a
production-stable
tag.
In that case, if
any
of these protected tags have a setting like
Allowed to create
, then
production-stable
also inherit this setting.
If you select a protected tag’s name, GitLab displays a list of
all matching tags.
Prevent tag creation with the same name as branches
A tag and a branch with identical names can contain different commits. If your
tags and branches use the same names, users running
git checkout
commands might check out the
tag
qa
when they instead meant to check out
the
branch
qa
. As an added security measure, avoid creating tags with the
same name as branches. Confusing the two could lead to potential
security or operational issues.
To prevent this problem:
Identify the branch names you do not want used as tags.
As described in
Configuring protected tags
,
create a protected tag:
For the
Name
, provide a name, such as
stable
. You can also create a wildcard
like
stable-*
to match multiple names, like
stable-v1
and
stable-v2
.
For
Allowed to Create
, select
No one
.
Select
Protect
.
Users can still create branches, but not tags, with the protected names.
Allow deploy keys to create protected tags
You can permit a
deploy key
to create protected tags.
Prerequisites:
The deploy key must be enabled for your project. A project deploy key is enabled by default when
it is created. However, a public deploy key must be
granted
access to the
project.
The deploy key must have
write access
to your project
repository.
The owner of the deploy key must have at least read access to the project.
The owner of the deploy key must also be a member of the project.
To allow a deploy key to create a protected tag:
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
Protected tags
.
From the
Tag
dropdown list, select the tag you want to protect.
From the
Allowed to create
list, select the deploy key.
Select
Protect
.
Run pipelines on protected tags
The permissions to create protected tags define if a user can:
Initiate and run CI/CD pipelines.
Execute actions on jobs associated with these tags.
These permissions ensure that only authorized users can trigger and manage
CI/CD processes for protected tags.
Delete a protected tag
You can manually delete protected tags with the GitLab API, or the
GitLab user interface.
Prerequisites:
You must be in the
Allowed to create or delete
list.
To do this:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Tags
.
Next to the tag you want to delete, select
Delete
(
remove
).
On the confirmation dialog, enter the tag name and select
Yes, delete protected tag
.
Protected tags can only be deleted by using GitLab either from the UI or API.
These protections prevent you from accidentally deleting a tag through local
Git commands or third-party Git clients.
Related topics
Protected Tags API
Tags API
