# Git file blame | GitLab Docs

Source: https://docs.gitlab.com/user/project/repository/files/git_blame/

Git file blame | GitLab Docs
Git file blame
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Git blame
provides more information
about every line in a file, including the last modified time, author, and
commit hash.
View blame for a file
History
Viewing blame directly in the file view
introduced
in GitLab 16.7
with flag
named
inline_blame
. Disabled by default.
Prerequisites:
The file must contain readable text content. The GitLab UI displays
git blame
results for text
files like
.rb
,
.js
,
.md
,
.txt
,
.yml
, and similar formats. Binary files, such as images
and PDFs, are not supported.
To view the blame for a file:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Repository
.
Select the file you want to review.
Either:
To change the view of the current file, in the file header, select
Blame
.
To open the full blame page, in the upper-right corner, select
Blame
.
Go to the line you want to see.
When you select
Blame
, this information is displayed:
To see the precise date and time of the commit, hover over the date. The vertical bar
to the left of the user avatar shows the general age of the commit. The newest
commits have a dark blue bar. As the age of the commit increases, the bar color
changes to light gray.
Blame previous commit
To see earlier revisions of a specific line:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Code
>
Repository
.
Select the file you want to review.
In the upper-right corner, select
Blame
, and go to the line you want to see.
Select
View blame prior to this change
(
doc-versions
)
until you’ve found the changes you’re interested in viewing.
Ignore specific revisions
History
Introduced
in GitLab 17.10
with a flag
named
blame_ignore_revs
. Disabled by default.
Enabled on GitLab.com, GitLab Self-Managed, and GitLab Dedicated
in GitLab 17.10.
Generally available
in GitLab 17.11. Feature flag
blame_ignore_revs
removed.
To configure Git blame to ignore specific revisions:
In the root of your repository, create a
.git-blame-ignore-revs
file.
Add the commit hashes you want to ignore, one per line.
For example:
a24cb33c0e1390b0719e9d9a4a4fc0e4a3a069cc
676c1c7e8b9e2c9c93e4d5266c6f3a50ad602a4c
Open a file in the blame view.
Select the
Blame preferences
dropdown list.
Select
Ignore specific revisions
.
The blame view refreshes and skips the revisions specified in the
.git-blame-ignore-revs
file,
showing the previous meaningful changes instead.
Related topics
Git file blame REST API
Common Git commands
File management with Git
