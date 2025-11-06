# Create a project | GitLab Docs

Source: https://docs.gitlab.com/user/project/

Create a project | GitLab Docs
Create a project
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
You have different options to create a project. You can create a blank project, create a project
from built-in or custom templates, or
create a project with
git push
.
Create a blank project
To create a blank project:
On the left sidebar, at the top, select
Create new
(
plus
) and
New project/repository
. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Create blank project
.
Enter the project details:
Project name
: Enter the name of your project.
For more information, see
naming rules
.
Project slug
: Enter the path to your project. GitLab uses the slug as the URL path.
Project deployment target (optional)
: If you want to deploy your project to specific environment,
select the relevant deployment target.
Visibility Level
: Select the appropriate visibility level.
See the
viewing and access rights
for users.
Initialize repository with a README
: Select this option to initialize the Git repository,
create a default branch, and enable cloning of this project’s repository.
Enable Static Application Security Testing (SAST)
: Select this option to analyze the
source code for known security vulnerabilities.
Enable Secret Detection
: Select this option to analyze the
source code for secrets and credentials to prevent unauthorized access.
Select
Create project
.
Create a project from a built-in template
Built-in templates populate a new project with files to help you get started.
These templates are sourced from the
project-templates
and
pages
groups.
Anyone can contribute to built-in project templates.
To create a project from a built-in template:
On the left sidebar, at the top, select
Create new
(
plus
) and
New project/repository
. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Create from template
.
Select the
Built-in
tab.
From the list of templates:
To preview a template, select
Preview
.
To use a template, select
Use template
.
Enter the project details:
Project name
: Enter the name of your project.
Project slug
: Enter the path to your project. GitLab uses the slug as the URL path.
Project description (optional)
Enter a description for your project.
The character limit is 500.
Visibility Level
: Select the appropriate visibility level.
See the
viewing and access rights
for users.
Select
Create project
.
If a user creates a project from a template, or
imports a project
,
they are shown as the author of the imported items, which retain the original timestamp from the template or import.
This can make items appear as if they were created before the user’s account existed.
Imported objects are labeled as
By <username> on <timestamp>
.
Before GitLab 17.1, the label was suffixed with
(imported from GitLab)
.
Create a project from the HIPAA Audit Protocol template
The HIPAA Audit Protocol template contains issues for audit inquiries in the
HIPAA Audit Protocol published by the U.S Department of Health and Human Services.
To create a project from the HIPAA Audit Protocol template:
On the left sidebar, at the top, select
Create new
(
plus
) and
New project/repository
. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Create from template
.
Select the
Built-in
tab.
Locate the
HIPAA Audit Protocol
template:
To preview the template, select
Preview
.
To use the template, select
Use template
.
Enter the project details:
Project name
: Enter the name of your project.
Project slug
: Enter the path to your project. GitLab uses the slug as the URL path.
Project description (optional)
Enter a description for your project.
The character limit is 500.
Visibility Level
: Select the appropriate visibility level.
See the
viewing and access rights
for users.
Select
Create project
.
Create a project from a custom template
Custom project templates are available for your
instance
and
group
.
To create a project from a custom template:
On the left sidebar, at the top, select
Create new
(
plus
) and
New project/repository
. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Select
Create from template
.
Select the
Instance
or
Group
tab.
From the list of templates:
To preview the template, select
Preview
.
To use a template, select
Use template
.
Enter the project details:
Project name
: Enter the name of your project.
Project slug
: Enter the path to your project. GitLab uses the slug as the URL path.
Project description (optional)
Enter a description for your project. The character limit is 500.
Visibility Level
: Select the appropriate visibility level.
See the
viewing and access rights
for users.
Select
Create project
.
Create a project that uses SHA-256 hashing
Status
: Experiment
History
Introduced
in GitLab 16.7
with a flag
named
support_sha256_repositories
. Disabled by default. This feature is an
experiment
.
The availability of this feature is controlled by a feature flag.
For more information, see the history.
This feature is available for testing, but not ready for production use.
You can select SHA-256 hashing for a project only when you create the project.
Git does not support migrating to SHA-256 later, or migrating back to SHA-1.
To create a project that uses SHA-256 hashing:
On the left sidebar, at the top, select
Create new
(
plus
) and
New project/repository
. If you’ve
turned on the new navigation
, this button is in the upper-right corner.
Enter the project details:
Project name
: Enter the name of your project.
Project slug
: Enter the path to your project. GitLab uses the slug as the URL path.
Project description (optional)
Enter a description for your project. The character limit is 500.
Visibility Level
: Select the appropriate visibility level.
See the
viewing and access rights
for users.
In the
Project Configuration
area, expand the
Experimental settings
.
Select
Use SHA-256 as the repository hashing algorithm
.
Select
Create project
.
Why SHA-256?
By default, Git uses the SHA-1 hashing algorithm
to generate a 40-character
ID for objects such as commits, blobs, trees, and tags. The SHA-1 algorithm was proven to be insecure when
Google was able to produce a hash collision
.
The Git project is not yet impacted by these
kinds of attacks because of the way Git stores objects.
In SHA-256 repositories, the algorithm generates a 64-character ID instead of a 40-character ID.
The Git project determined that the SHA-256 feature is safe to use when they
removed the experimental label
.
Federal regulations, such as NIST and CISA
guidelines
,
which
FedRamp
enforces, have set a due date in 2030 to stop using SHA-1 and
encourage agencies to move away from SHA-1 earlier, if possible.
Related topics
Create a project with
git push
Reserved project and group names
Rules for project and group names
Manage projects
