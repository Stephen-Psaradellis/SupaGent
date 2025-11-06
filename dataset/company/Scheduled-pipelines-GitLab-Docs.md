# Scheduled pipelines | GitLab Docs

Source: https://docs.gitlab.com/ci/pipelines/schedules/#create-a-pipeline-schedule

Scheduled pipelines | GitLab Docs
Scheduled pipelines
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Create pipeline schedules to run pipelines at regular intervals based on cron patterns.
Use pipeline schedules for tasks that need to run on a time-based schedule rather than triggered by code changes.
Unlike pipelines triggered by commits or merge requests, scheduled pipelines run independently of code changes.
This makes them suitable for tasks that need to happen regardless of development activity,
such as keeping deployments current or running periodic maintenance.
Create a pipeline schedule
History
Inputs option
introduced
in GitLab 17.11.
When you create a pipeline schedule, you become the schedule owner.
The pipeline runs with your permissions and can access
protected environments
and use the
CI/CD job token
based on your access level.
Prerequisites:
You must have at least the Developer role for the project.
For schedules that target
protected branches
,
you must have merge permissions for the target branch.
Your
.gitlab-ci.yml
file must have valid syntax. You can
validate your configuration
before scheduling.
To create a pipeline schedule:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Pipeline schedules
.
Select
New schedule
.
Complete the fields.
Interval Pattern
: Select one of the preconfigured intervals, or enter a custom
interval in
cron notation
. You can use any cron value,
but scheduled pipelines cannot run more frequently than the instance’s
maximum scheduled pipeline frequency
.
Target branch or tag
: Select the branch or tag for the pipeline.
Inputs
: Set values for any
inputs
defined in your pipeline’s
spec:inputs
section.
These input values are used every time the scheduled pipeline runs. A schedule can have a maximum of 20 inputs.
Variables
: Add any number of
CI/CD variables
to the schedule.
These variables are available only when the scheduled pipeline runs,
and not in any other pipeline run. Inputs are recommended for pipeline configuration instead of variables
because they offer improved security and flexibility.
If the project has reached the
maximum number of pipeline schedules
,
delete unused schedules before adding another.
Edit a pipeline schedule
Prerequisites:
You must be the schedule owner or take ownership of the schedule.
You must have at least the Developer role for the project.
For schedules that target
protected branches
,
you must have merge permissions for the target branch.
For schedules that run on
protected tags
,
you must be allowed to create protected tags.
To edit a pipeline schedule:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Pipeline schedules
.
Next to the schedule, select
Edit
(
pencil
).
Make your changes, then select
Save changes
.
Run manually
You can manually run scheduled pipelines once per minute.
When you run a scheduled pipeline manually, it uses your permissions instead of the schedule owner’s permissions.
To trigger a pipeline schedule immediately instead of waiting for the next scheduled time:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Pipeline schedules
.
Next to the schedule, select
Run
(
play
).
Take ownership
If a pipeline schedule becomes inactive because the original owner is unavailable, you can take ownership.
Scheduled pipelines execute with the permissions of the user who owns the schedule.
Prerequisites:
You must have at least the Maintainer role for the project.
To take ownership of a schedule:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Pipeline schedules
.
Next to the schedule, select
Take ownership
.
View your scheduled pipelines
History
Introduced
in GitLab 18.4.
To view the active pipeline schedules that you own across all your projects:
On the left sidebar, select your avatar. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Edit profile
.
Select
Account
.
Scroll to
Scheduled pipelines you own
.
Related topics
CI/CD pipelines
Run jobs for scheduled pipelines
Pipeline schedules API
Pipeline efficiency
Troubleshooting
When working with pipeline schedules, you might encounter the following issues.
Scheduled pipeline becomes inactive
If a scheduled pipeline status changes to
Inactive
unexpectedly,
the schedule owner might have been blocked or removed from the project.
Take ownership of the schedule to reactivate it.
Distribute pipeline schedules to prevent system load
To prevent excessive load from too many pipelines starting simultaneously,
review and distribute your pipeline schedules:
Run this command to extract and format schedule data:
outfile
=
/tmp/gitlab_ci_schedules.tsv
sudo gitlab-psql --command
"
COPY (SELECT
ci_pipeline_schedules.cron,
projects.path AS project,
users.email
FROM ci_pipeline_schedules
JOIN projects ON projects.id = ci_pipeline_schedules.project_id
JOIN users ON users.id = ci_pipeline_schedules.owner_id
) TO '
$outfile
' CSV HEADER DELIMITER E'\t' ;"
sort
"
$outfile
"
|
uniq -c
|
sort -n
Review the output to identify popular
cron
patterns.
For example, many schedules might run at the start of every hour (
0 * * * *
).
Adjust the schedules to create a staggered
cron
pattern
, especially for large repositories.
For example, instead of multiple schedules running at the start of every hour,
distribute them throughout the hour (
5 * * * *
,
15 * * * *
,
25 * * * *
).
