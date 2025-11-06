# Analyze GitLab usage | GitLab Docs

Source: https://docs.gitlab.com/user/analytics/

Analyze GitLab usage | GitLab Docs
Analyze GitLab usage
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Group-level analytics moved to GitLab Premium in 13.9.
GitLab provides different types of analytics insights for instances, groups, and
projects
.
Analytics features require different
roles and permissions
for projects and groups.
Analytics features
End-to-end insight & visibility analytics
Use these features to gain insights into your overall software development lifecycle.
Feature
Description
Project-level
Group-level
Instance-level
Value Streams Dashboard
Insights into DevSecOps trends, patterns, and opportunities for digital transformation improvements.
check-circle
Yes
check-circle
Yes
dotted-circle
No
Value Stream Management Analytics
Insights into time-to-value through customizable stages.
check-circle
Yes
check-circle
Yes
dotted-circle
No
DevOps adoption
by group
and
by instance
Organization’s maturity in DevOps adoption, with feature adoption over time and feature distribution by group.
dotted-circle
No
check-circle
Yes
check-circle
Yes
Usage trends
Overview of instance data and changes in data volume over time.
dotted-circle
No
dotted-circle
No
check-circle
Yes
Insights
Customizable reports to explore issues, merged merge requests, and triage hygiene.
check-circle
Yes
check-circle
Yes
dotted-circle
No
Analytics dashboards
Built-in and customizable dashboards to visualize collected data.
check-circle
Yes
check-circle
Yes
dotted-circle
No
Productivity analytics
Use these features to gain insights into the productivity of your team on issues and merge requests.
Feature
Description
Project-level
Group-level
Instance-level
Issue analytics
Visualization of issues created each month.
check-circle
Yes
check-circle
Yes
dotted-circle
No
Merge request analytics
Overview of merge requests, with mean time to merge, throughput, and activity details.
check-circle
Yes
dotted-circle
No
dotted-circle
No
Productivity analytics
Merge request lifecycle, filterable down to author level.
dotted-circle
No
check-circle
Yes
dotted-circle
No
Code review analytics
Open merge requests with information about merge request activity.
check-circle
Yes
dotted-circle
No
dotted-circle
No
Developer analytics
Use these features to gain insights into developer productivity and code coverage.
Feature
Description
Project-level
Group-level
Instance-level
Contribution analytics
Overview of
contribution events
made by group members, with bar chart of push events, merge requests, and issues.
dotted-circle
No
check-circle
Yes
dotted-circle
No
Contributor analytics
Overview of commits made by project members, with line chart of number of commits.
check-circle
Yes
dotted-circle
No
dotted-circle
No
Repository analytics
Programming languages used in the repository and code coverage statistics.
check-circle
Yes
check-circle
Yes
dotted-circle
No
CI/CD analytics
Use these features to gain insights into CI/CD performance.
Feature
Description
Project-level
Group-level
Instance-level
CI/CD analytics
Pipeline duration and successes or failures.
check-circle
Yes
check-circle
Yes
dotted-circle
No
DORA metrics
DORA metrics over time.
check-circle
Yes
check-circle
Yes
dotted-circle
No
Security analytics
Use these features to gain insights into security vulnerabilities and metrics.
Feature
Description
Project-level
Group-level
Instance-level
Security Dashboards
Collection of metrics, ratings, and charts for vulnerabilities detected by security scanners.
check-circle
Yes
check-circle
Yes
dotted-circle
No
Metric glossary
The following glossary provides definitions for common development metrics used in analytics features,
and explains how they are measured in GitLab.
Metric
Definition
Measurement in GitLab
Mean Time to Change (MTTC)
The average duration between idea and delivery.
From when an issue is created until its related merge request is deployed to production.
Mean Time to Detect (MTTD)
The average duration that a bug goes undetected in production.
From when a bug is deployed to production until an issue is created to report it.
Mean Time to Merge (MTTM)
The average lifespan of a merge request.
From when a merge request is created until it is merged. Excludes merge requests that are closed or unmerged. For more information, see
merge request analytics
.
Mean Time to Recover / Repair / Resolution / Resolve / Restore (MTTR)
The average duration that a bug is not fixed in production.
From when a bug is deployed to production until the bug fix is deployed.
Velocity
The total issue burden completed in a specific period of time. The burden is usually measured in points or weight, often per sprint.
Total points or weight of issues closed in a specific period of time. For example, “30 points per sprint”.
For more definitions, see also the
Value Streams Dashboard metrics and drill-down reports
.
