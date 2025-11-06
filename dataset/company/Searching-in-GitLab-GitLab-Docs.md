# Searching in GitLab | GitLab Docs

Source: https://docs.gitlab.com/user/search/

Searching in GitLab | GitLab Docs
Searching in GitLab
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Find what you need in a growing codebase or expanding organization.
Save time by looking up specific code, issues, merge requests, and other content across your projects.
Choose from three types of search to match your needs:
basic search
,
advanced search
, and
exact code search
.
For code search, GitLab uses these types in this order:
Exact code search
: where you can use exact match and regular expression modes.
Advanced search
: when exact code search is not available.
Basic search
: when exact code search and advanced search are not available
or when you search against a non-default branch.
This type does not support group or global search.
Available scopes
Scopes describe the type of data you’re searching.
The following scopes are available for basic search:
Scope
Global
1
Group
Project
Code
dash-circle
No
dash-circle
No
check-circle-filled
Yes
Comments
dash-circle
No
dash-circle
No
check-circle-filled
Yes
Commits
dash-circle
No
dash-circle
No
check-circle-filled
Yes
Epics
dash-circle
No
check-circle-filled
Yes
dash-circle
No
Issues
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Merge requests
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Milestones
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Projects
check-circle-filled
Yes
check-circle-filled
Yes
dash-circle
No
Users
check-circle-filled
Yes
check-circle-filled
Yes
check-circle-filled
Yes
Wikis
dash-circle
No
dash-circle
No
check-circle-filled
Yes
Footnotes
:
An administrator can
disable global search scopes
.
Specify a search type
History
Introduced
in GitLab 17.4.
To specify a search type, set the
search_type
URL parameter as follows:
search_type=zoekt
for
exact code search
search_type=advanced
for
advanced search
search_type=basic
for basic search
search_type
replaces the deprecated
basic_search
parameter.
For more information, see
issue 477333
.
Restrict search access
Offering
: GitLab Self-Managed
History
Restricting global search to authenticated users
introduced
in GitLab 13.4
with a flag
named
block_anonymous_global_searches
. Disabled by default.
Allowing search for unauthenticated users
introduced
in GitLab 16.7
with a flag
named
allow_anonymous_searches
. Enabled by default.
Restricting global search to authenticated users
generally available
in GitLab 17.11. Feature flag
block_anonymous_global_searches
removed.
Allowing search for unauthenticated users
generally available
in GitLab 18.0. Feature flag
allow_anonymous_searches
removed.
Prerequisites:
You must have administrator access to the instance.
By default, requests to
/search
and global search are available for unauthenticated users.
To restrict
/search
to authenticated users only, do one of the following:
Restrict visibility levels
for the project or group.
Restrict access in the
Admin
area:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Settings
>
Search
.
Expand
Advanced search
.
Clear the
Allow unauthenticated users to use search
checkbox.
Select
Save changes
.
To restrict global search to authenticated users only:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Settings
>
Search
.
Expand
Visibility and access controls
Select the
Restrict global search to authenticated users only
checkbox.
Select
Save changes
.
Disable global search scopes
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
History
Introduced
in GitLab 17.9.
Prerequisites:
You must have administrator access to the instance.
To improve the performance of your instance’s global search,
you can disable one or more search scopes.
All global search scopes are enabled by default on GitLab Self-Managed instances.
To disable one or more global search scopes:
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
Settings
>
Search
.
Expand
Visibility and access controls
.
Clear the checkboxes for the scopes you want to disable.
Select
Save changes
.
Global search validation
History
Support for partial matches in issue search
removed
in GitLab 14.9
with a flag
named
issues_full_text_search
. Disabled by default.
Generally available
in GitLab 16.2. Feature flag
issues_full_text_search
removed.
Global search ignores and logs as abusive any search that includes:
Fewer than two characters
A term longer than 100 characters (URL search terms must not exceed 200 characters)
A stop word only (for example,
the
,
and
, or
if
)
An unknown
scope
group_id
or
project_id
that is not completely numeric
repository_ref
or
project_ref
with special characters not allowed by
Git refname
Global search only flags with an error any search that includes more than:
4096 characters
64 terms
Partial matches are not supported in issue search.
For example, when you search issues for
play
, the query does not return issues that contain
display
.
However, the query matches all possible variations of the string (for example,
plays
).
Autocomplete suggestions
History
Showing only users from authorized projects and groups
introduced
in GitLab 17.10
with flags
named
users_search_scoped_to_authorized_namespaces_advanced_search
,
users_search_scoped_to_authorized_namespaces_basic_search
, and
users_search_scoped_to_authorized_namespaces_basic_search_by_ids
. Disabled by default.
Generally available
in GitLab 17.11. Feature flags
users_search_scoped_to_authorized_namespaces_advanced_search
,
users_search_scoped_to_authorized_namespaces_basic_search
, and
users_search_scoped_to_authorized_namespaces_basic_search_by_ids
removed.
The availability of this feature is controlled by feature flags.
For more information, see the history.
As you type in the search box, autocomplete suggestions are displayed for:
Projects
and groups
Users from authorized projects and groups
Help pages
Project features (for example, milestones)
Settings (for example, user settings)
Recently viewed merge requests
Recently viewed issues and epics
GitLab Flavored Markdown references
for issues in a project
Search in all GitLab
To search in all GitLab:
On the left sidebar, select
Search or go to
. If you’ve
turned on the new navigation
, this field is on the top bar.
Type your search query. You must type at least two characters.
Press
Enter
to search, or select from the list.
The results are displayed. To filter the results, on the left sidebar, select a filter.
Search in a project
To search in a project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Search or go to
again and type the string you want to search for.
Press
Enter
to search, or select from the list.
The results are displayed. To filter the results, on the left sidebar, select a filter.
Search for a project by full path
History
Introduced
in GitLab 15.9
with a flag
named
full_path_project_search
. Disabled by default.
Generally available
in GitLab 15.11. Feature flag
full_path_project_search
removed.
You can search for a project by entering its full path (including the namespace it belongs to) in the search box.
As you type the project path,
autocomplete suggestions
are displayed.
For example:
gitlab-org/gitlab
searches for the
gitlab
project in the
gitlab-org
namespace.
gitlab-org/
displays autocomplete suggestions for projects that belong to the
gitlab-org
namespace.
Include archived projects in search results
History
Introduced
in GitLab 16.1
with a flag
named
search_projects_hide_archived
for project search. Disabled by default.
Generally available
in GitLab 16.6 for all search scopes.
By default, archived projects are excluded from search results.
To include archived projects in search results:
On the search page, on the left sidebar, select the
Include archived
checkbox.
On the left sidebar, select
Apply
.
Search for code
To search for code in a project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Search or go to
again and type the code you want to search for.
Press
Enter
to search, or select from the list.
Code search shows only the first result in the file.
To search for code in all GitLab, ask your administrator to enable
advanced search
.
View Git blame from code search
History
Introduced
in GitLab 14.7.
After you find search results, you can view who made the last change to the line
where the results were found.
From the code search result, hover over the line number.
On the left, select
View blame
.
Filter code search results by language
History
Introduced
in GitLab 15.10.
To filter code search results by one or more languages:
On the code search page, on the left sidebar, select one or more languages.
On the left sidebar, select
Apply
.
Search for a commit SHA
To search for a commit SHA:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Search or go to
again and type the commit SHA you want to search for.
Press
Enter
to search, or select from the list.
If a single result is returned, GitLab redirects to the commit result
and gives you the option to return to the search results page.
Syntax
Basic search uses exact substring matching with the following options:
Syntax
Description
Example
filename:
Filename
filename:*spec.rb
path:
Repository location (full or partial matches)
path:spec/workers/
extension:
File extension without
.
(exact matches only)
extension:js
Examples
Query
Description
rails -filename:gemfile.lock
Returns
rails
in all files except the
gemfile.lock
file.
helper -extension:yml -extension:js
Returns
helper
in all files except files with a
.yml
or
.js
extension.
helper path:lib/git
Returns
helper
in all files with a
lib/git*
path (for example,
spec/lib/gitlab
).
