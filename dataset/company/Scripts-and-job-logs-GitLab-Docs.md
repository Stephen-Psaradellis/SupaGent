# Scripts and job logs | GitLab Docs

Source: https://docs.gitlab.com/ci/yaml/script/#use-special-characters-with-script

Scripts and job logs | GitLab Docs
Scripts and job logs
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
You can use special syntax in
script
sections to:
Split long commands
into multiline commands.
Use color codes
to make job logs easier to review.
Create custom collapsible sections
to simplify job log output.
Use special characters with
script
Sometimes,
script
commands must be wrapped in single or double quotes.
For example, commands that contain a colon (
:
) must be wrapped in single quotes (
'
).
The YAML parser needs to interpret the text as a string rather than
a “key: value” pair.
For example, this script uses a colon:
job
:
script
:
-
curl --request POST --header 'Content-Type
:
application/json' "https://gitlab.example.com/api/v4/projects"
To be considered valid YAML, you must wrap the entire command in single quotes. If
the command already uses single quotes, you should change them to double quotes (
"
)
if possible:
job
:
script
:
-
'curl --request POST --header "Content-Type: application/json" "https://gitlab.example.com/api/v4/projects"'
You can verify the syntax is valid with the
CI Lint
tool.
Be careful when using these characters as well:
{
,
}
,
[
,
]
,
,
,
&
,
*
,
#
,
?
,
|
,
-
,
<
,
>
,
=
,
!
,
%
,
@
,
`
.
Ignore non-zero exit codes
When script commands return an exit code other than zero, the job fails and further
commands do not execute.
Store the exit code in a variable to avoid this behavior:
job
:
script
:
-
exit_code=0
-
false
|| exit_code=$?
-
if [ $exit_code -ne 0 ]; then echo "Previous command failed"; fi;
Set a default
before_script
or
after_script
for all jobs
You can use
before_script
and
after_script
with
default
:
Use
before_script
with
default
to define a default array of commands that
should run before the
script
commands in all jobs.
Use
after_script
with default to define a default array of commands
that should run after any job completes or is canceled.
You can overwrite a default by defining a different one in a job. To ignore the default
use
before_script: []
or
after_script: []
:
default
:
before_script
:
-
echo "Execute this `before_script` in all jobs by default."
after_script
:
-
echo "Execute this `after_script` in all jobs by default."
job1
:
script
:
-
echo "These script commands execute after the default `before_script`,"
-
echo "and before the default `after_script`."
job2
:
before_script
:
-
echo "Execute this script instead of the default `before_script`."
script
:
-
echo "This script executes after the job's `before_script`,"
-
echo "but the job does not use the default `after_script`."
after_script
:
[]
Skip
after_script
commands if a job is canceled
History
Introduced
in GitLab 17.0
with a flag
named
ci_canceling_status
. Enabled by default. Requires GitLab Runner version 16.11.1.
Generally available
in GitLab 17.3. Feature flag
ci_canceling_status
removed.
after_script
commands run if a job is canceled while the
before_script
or
script
section of that job are running.
The job’s status in the UI is
canceling
while the
after_script
are executing,
and changes to
canceled
after the
after_script
commands complete. The
$CI_JOB_STATUS
predefined variable has a value of
canceled
while the
after_script
commands are running.
To prevent
after_script
commands running after canceling a job, configure the
after_script
section to:
Check the
$CI_JOB_STATUS
predefined variable at the start of the
after_script
section.
End execution early if the value is
canceled
.
For example:
job1
:
script
:
-
my-script.sh
after_script
:
-
if [ "$CI_JOB_STATUS" == "canceled" ]; then exit 0; fi
-
my-after-script.sh
Split long commands
You can split long commands into multiline commands to improve readability with
|
(literal) and
>
(folded)
YAML multiline block scalar indicators
.
If multiple commands are combined into one command string, only the last command’s
failure or success is reported.
Failures from earlier commands are ignored due to a bug
.
To work around this, run each command as a separate
script
item, or add an
exit 1
command to each command string.
You can use the
|
(literal) YAML multiline block scalar indicator to write
commands over multiple lines in the
script
section of a job description.
Each line is treated as a separate command.
Only the first command is repeated in the job log, but additional
commands are still executed:
job
:
script
:
-
|
echo "First command line."
echo "Second command line."
echo "Third command line."
The previous example renders in the job log as:
$
echo
First
command
line
# collapsed multiline command
First
command
line
Second
command
line.
Third
command
line.
The
>
(folded) YAML multiline block scalar indicator treats empty lines between
sections as the start of a new command:
job
:
script
:
-
>
echo "First command line
is split over two lines."
echo "Second command line."
This behaves similarly to multiline commands without the
>
or
|
block
scalar indicators:
job
:
script
:
-
echo "First command line
is split over two lines."
echo "Second command line."
The previous two examples render in the job log as:
$
echo
First
command
line is split over two lines.
# collapsed multiline command
First
command
line is split over two lines.
Second
command
line.
When you omit the
>
or
|
block scalar indicators, GitLab concatenates non-empty
lines to form the command. Make sure the lines can run when concatenated.
Shell here documents
work with the
|
and
>
operators as well. The following example transliterates lowercase letters
to upper case:
job
:
script
:
-
|
tr a-z A-Z << END_TEXT
one two three
four five six
END_TEXT
Results in:
$ tr a-z A-Z
<< END_TE
XT
# collapsed multiline command
ONE TWO THREE
FOUR FIVE SIX
Add color codes to script output
Script output can be colored using
ANSI escape codes
,
or by running commands or programs that output ANSI escape codes.
For example, using
Bash with color codes
:
job
:
script
:
-
echo -e "\e[31mThis text is red,\e[0m but this text isn't\e[31m however this text is red again."
You can define the color codes in Shell environment variables, or even
CI/CD variables
,
which makes the commands easier to read and reusable.
For example, using the previous example and environment variables defined in a
before_script
:
job
:
before_script
:
-
TXT_RED="\e[31m" && TXT_CLEAR="\e[0m"
script
:
-
echo -e "${TXT_RED}This text is red,${TXT_CLEAR} but this part isn't${TXT_RED} however this part is again."
-
echo "This text is not colored"
Or with
PowerShell color codes
:
job
:
before_script
:
-
$esc="$([char]27)"; $TXT_RED="$esc[31m"; $TXT_CLEAR="$esc[0m"
script
:
-
Write-Host $TXT_RED"This text is red,"$TXT_CLEAR" but this text isn't"$TXT_RED" however this text is red again."
-
Write-Host "This text is not colored"
