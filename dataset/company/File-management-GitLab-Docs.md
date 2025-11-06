# File management | GitLab Docs

Source: https://docs.gitlab.com/user/project/repository/files/

File management | GitLab Docs
File management
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
The GitLab UI extends the history and tracking capabilities of Git with user-friendly
features in your browser. You can:
Search for files.
Change file handling.
Explore the history of an entire file, or a single line.
Understand how file types render in the UI
When you add files of these types to your project, GitLab renders their output
to improve readability:
GeoJSON
files display as maps.
Jupyter Notebook
files display as rendered HTML.
Files in many markup languages are rendered for display.
Supported markup languages
If your file has one of the these file extensions, GitLab renders the contents of the file’s
markup language
in the UI.
Markup language
Extensions
Plain text
txt
Markdown
mdown
,
mkd
,
mkdn
,
md
,
markdown
reStructuredText
rst
AsciiDoc
adoc
,
ad
,
asciidoc
Textile
textile
Rdoc
rdoc
Org mode
org
creole
creole
MediaWiki
wiki
,
mediawiki
README and index files
History
Support for
_index.md
files was
introduced
in GitLab 18.5.
When a
README
,
index
, or
_index
file is present in a repository, GitLab renders its contents.
These files can either be plain text or have the extension of a
supported markup language.
The priority order for automatic rendering is:
Previewable files:
README.md
,
index.md
,
_index.md
, etc.
Plain text files:
README
,
index
,
_index
, etc.
The first file found in each category (in alphabetical order) is selected, with
previewable files taking precedence over plain text files. For example, if
multiple READMEs are available GitLab renders them in the following order:
README.adoc
README.md
README.rst
README
Render OpenAPI files
GitLab renders OpenAPI specification files if the filename includes
openapi
or
swagger
,
and the extension is
yaml
,
yml
, or
json
. These examples are all correct:
openapi.yml
,
openapi.yaml
,
openapi.json
swagger.yml
,
swagger.yaml
,
swagger.json
OpenAPI.YML
,
openapi.Yaml
,
openapi.JSON
openapi_gitlab.yml
,
openapi.gitlab.yml
gitlab_swagger.yml
gitlab.openapi.yml
To render an OpenAPI file:
Search for
the OpenAPI file in your repository.
Select
Display rendered file
.
To display the
operationId
in the operations list, add
displayOperationId=true
to the query string.
When
displayOperationId
is present in the query string and has any value, it
evaluates to
true
. This behavior matches the default behavior of Swagger.
View Git records for a file
Historical information about files in your repository is available in the GitLab UI:
Git file history
: shows the commit history of an entire file.
Git blame
: shows each line of a text-based file, and the most
recent commit that changed the line.
Create permalinks
Permalinks are permanent URLs that point to specific files, directories, or sections of code
in your repository. They remain valid even when the repository changes, making them ideal for
sharing and referencing code in documentation, issues, or merge requests.
To create a permalink:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Go to the file or directory you want to link to.
Optional. For specific code selections:
Single line
: Select the line number.
Multiple lines
: Select the first line number, then hold
Shift
and select the last line number.
Markdown anchor
: Hover over a heading to reveal the anchor link (
link
), and select it.
Select
Actions
(
ellipsis_v
), then select
Copy Permalink
.
Alternatively, press
y
. For more shortcuts, see
keyboard shortcuts
.
View open merge requests for a file
History
Introduced
in GitLab 17.10
with a flag
named
filter_blob_path
.
Enabled on GitLab.com
in GitLab 17.11.
Enabled on GitLab Self-Managed and GitLab Dedicated
in GitLab 18.0.
Generally available
in GitLab 18.2. Feature flag
filter_blob_path
removed.
The availability of this feature is controlled by a feature flag. For more information, see the history.
When viewing a repository file, GitLab shows a badge with the number of open merge requests that target
the current branch and modify the file. This helps you identify files that have pending changes.
To view the open merge requests for a file:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Go to the file you want to view.
In the upper right of the screen, next to the filename, look for the green badge with the number
of
merge-request-open
Open
merge requests.
Select the badge to see a list of open merge requests created in the past 30 days.
Select any merge request in the list to go to that merge request.
Search for a file
History
Changed
to a dialog in GitLab 16.11.
Use the file finder to search directly from the GitLab UI for a file in your repository.
The file finder uses fuzzy search and highlights results as you type.
To search for a file, press
t
anywhere in your project, or:
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
In the upper right, select
Find file
.
On the dialog, start entering the filename:
Optional. To narrow the search options, press
Command
+
K
or
select
Commands
on the lower right corner of the dialog:
For
Pages or actions
, enter
>
.
For
Users
, enter
@
.
For
Projects
, enter
:
.
For
Files
, enter
~
.
From the dropdown list, select the file to view it in your repository.
To go back to the
Files
page, press
Esc
.
This feature uses the
fuzzaldrin-plus
library.
Change how Git handles a file
To change the default handling of a file or file type, create a
.gitattributes
file
. Use
.gitattributes
files to:
Configure file display in diffs, such as
syntax highlighting
or
collapsing generated files
.
Control file storage and protection, such as
making files read-only
,
or storing large files
with Git LFS
.
Related topics
Repository files API
File management with Git
Troubleshooting
Repository Languages: excessive CPU use
To determine which languages are in a repository’s files, GitLab uses a Ruby gem.
When the gem parses a file to determine its file type,
the process can use excessive CPU
.
The gem contains a
heuristics configuration file
that defines which file extensions to parse. These file types can take excessive CPU:
Files with the
.txt
extension.
XML files with an extension not defined by the gem.
To fix this problem, edit your
.gitattributes
file and assign a language to
specific file extensions. You can also use this approach to fix misidentified file types:
Identify the language to specify. The gem contains a
configuration file for known data types
.
To add an entry for text files, for example:
Text
:
type
:
prose
wrap
:
true
aliases
:
-
fundamental
-
plain text
extensions
:
-
".txt"
Add or edit
.gitattributes
in the root of your repository:
*.txt linguist-language=Text
*.txt
files have an entry in the heuristics file. This example prevents parsing of these files.
