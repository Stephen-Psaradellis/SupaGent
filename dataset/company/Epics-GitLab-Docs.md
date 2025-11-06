# Epics | GitLab Docs

Source: https://docs.gitlab.com/user/group/epics/

Epics | GitLab Docs
Epics
Tier
: Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Epics in GitLab coordinate and track large initiatives by organizing work items into a work hierarchy.
Epics make complex projects manageable. They:
Break down large features into smaller deliverables that add incremental value.
Track the progress of related work items with scheduled start and end dates.
Organize discussions and decisions about feature scope and requirements.
Create hierarchical structures that connect tasks to strategic goals.
Build visual roadmaps to monitor progress toward objectives.
Teams use epics to coordinate across multiple iterations and track progress toward long-term goals.
In the Ultimate tier,
nested epics
provide additional
structure through work hierarchies that align with agile frameworks.
Break down complex projects into more manageable child epics, which can further contain their own
sets of issues and tasks.
This nested structure helps maintain clarity and ensures all aspects of a project are covered without
losing sight of the overarching goals.
See the video:
GitLab Epics - Setting up your Organization with GitLab
.
Relationships between epics and other items
The possible relationships between epics and other items are:
An epic is the parent of one or more issues.
An epic is the parent of one or more
child epics
. Ultimate only.
An epic is
linked
to one or more task, objective, or key result.
Example set of relationships:
%%{init: { "fontFamily": "GitLab Sans" }}%%
graph TD
accTitle: Epics and issues
accDescr: How issues and child epics relate to parent epics and lateral relationships to work items
%% Main structure %%
Parent_epic -->|contains| Issue1
Parent_epic -->|contains| Child_epic
Child_epic -->|contains| Issue2
%% Additional work items and lateral relationships %%
Issue1 -- contains --> Task1["Task"]
Issue2 -- "blocked by" --> Objective1["Objective"]
Task1 -- blocking --> KeyResult1["Key Result"]
%% Work items linked to epics and issues %%
Parent_epic -. related .- Objective1
Child_epic -. "blocked by" .- KeyResult1
Child issues from different group hierarchies
You can add issues from a different group hierarchy to an epic.
To do it, paste the issue URL when
adding an existing issue
.
Roadmap in epics
Tier
: Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
On the
Child items
section header, select
More actions
(
ellipsis_v
) >
View on a roadmap
.
A roadmap filtered for the parent epic opens.
Epics as work items
History
Introduced
in GitLab 17.2
with a flag
named
work_item_epics
. Disabled by default. Introduced in
beta
.
Enabled on GitLab.com
in GitLab 17.6.
Enabled by default on GitLab Self-Managed and GitLab Dedicated
in GitLab 17.7.
Generally available
in GitLab 18.1. Feature flag
work_item_epics
removed.
We have changed how epics look by migrating them to a unified framework for work items to better
meet the product needs of our Agile Planning offering.
For more information, see
epic 9290
and the
following blog posts:
First look: The new Agile planning experience in GitLab
(June 2024)
Unveiling a new epic experience for improved Agile planning
(July 2024)
If you run into any issues while trying out this change, you can use the
feedback issue
to provide more details.
Work item Markdown reference
History
Introduced
in GitLab 18.1
with a flag
named
extensible_reference_filters
. Disabled by default.
Generally available
in GitLab 18.2. Feature flag
extensible_reference_filters
removed.
You can reference work items in GitLab Flavored Markdown fields with
[work_item:123]
.
For more information, see
GitLab-specific references
.
Related topics
Manage epics
and multi-level child epics.
Link
related epics
based on a type of relationship.
Create workflows with
epic boards
.
Turn on notifications
for about epic events.
Add an emoji reaction
to an epic or its comments.
Collaborate on an epic by posting comments in a
thread
.
Use
health status
to track your progress.
Create epic templates
to standardize epic descriptions.
