# CI/CD inputs | GitLab Docs

Source: https://docs.gitlab.com/ci/inputs/#array-type

CI/CD inputs | GitLab Docs
CI/CD inputs
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
History
Introduced
in GitLab 15.11 as a beta feature.
Made generally available
in GitLab 17.0.
Use CI/CD inputs to increase the flexibility of CI/CD configuration. Inputs and
CI/CD variables
can be used in similar ways, but have different benefits:
Inputs provide typed parameters for reusable templates with built-in validation at pipeline creation time.
To define specific values when the pipeline runs, use inputs instead of CI/CD variables.
CI/CD variables offer flexible values that can be defined at multiple levels, but can be modified
throughout pipeline execution. Use variables for values that need to be accessible in the job’s runtime environment.
You can also use
predefined variables
with
rules
for dynamic pipeline configuration.
CI/CD Inputs and variables comparison
Inputs:
Purpose
: Defined in CI configurations (templates, components or
.gitlab-ci.yml
) and assigned values
when a pipeline is triggered, allowing consumers to customize reusable CI configurations.
Modification
: Once passed at pipeline initialization, input values are interpolated in the CI/CD
configuration and remain fixed for the entire pipeline run.
Scope
: Available only in the file they are defined, whether in the
.gitlab-ci.yml
or a file
being
include
d. You can pass them explicitly to other files - using
include:inputs
- or pipeline
using
trigger:inputs
.
Validation
: Provide robust validation capabilities including type checking, regex patterns,
predefined option lists, and helpful descriptions for users.
CI/CD Variables:
Purpose
: Values that can be set as environment variables during job execution and in various parts
of the pipeline for passing data between jobs.
Modification
: Can be dynamically generated or modified during pipeline execution through dotenv artifacts,
conditional rules, or directly in job scripts.
Scope
: Can be defined globally (affecting all jobs), at the job level (affecting only specific jobs),
or for the entire project or group through the GitLab UI.
Validation
: Simple key-value pairs with minimal built-in validation, though you can add some controls through
the GitLab UI for project variables.
Define input parameters with
spec:inputs
Use
spec:inputs
in the CI/CD configuration
header
to define input parameters that
can be passed to the configuration file.
Use the
$[[ inputs.input-id ]]
interpolation format outside the header section to declare where to use
the inputs.
For example:
spec
:
inputs
:
job-stage
:
default
:
test
environment
:
default
:
production
---
scan-website
:
stage
:
$[[ inputs.job-stage ]]
script
:
./scan-website $[[ inputs.environment ]]
In this example, the inputs are
job-stage
and
environment
.
With
spec:inputs
:
Inputs are mandatory if
default
is not specified.
Inputs are evaluated and populated when the configuration is fetched during pipeline creation.
A string containing an input must be less than 1 MB.
A string inside an input must be less than 1 KB.
Inputs can use CI/CD variables, but have the same
variable limitations as the
include
keyword
.
If the file that defines
spec:inputs
also contains job definitions, add a YAML document
separator (
---
) after the header.
Then you set the values for the inputs when you:
Trigger a new pipeline
using this configuration file.
You should always set default values when using inputs to configure new pipelines
with any method other than
include
. Otherwise the pipeline could fail to start
if a new pipeline triggers automatically, including in:
Merge request pipelines
Branch pipelines
Tag pipelines
Include the configuration
in your pipeline.
Any inputs that are mandatory must be added to the
include:inputs
section, and are used
every time the configuration is included.
Input configuration
To configure inputs, use:
spec:inputs:default
to define default values for inputs
when not specified. When you specify a default, the inputs are no longer mandatory.
spec:inputs:description
to give a description to
a specific input. The description does not affect the input, but can help people
understand the input details or expected values.
spec:inputs:options
to specify a list of allowed values
for an input.
spec:inputs:regex
to specify a regular expression
that the input must match.
spec:inputs:type
to force a specific input type, which
can be
string
(default when not specified),
array
,
number
, or
boolean
.
You can define multiple inputs per CI/CD configuration file, and each input can have
multiple configuration parameters.
For example, in a file named
scan-website-job.yml
:
spec
:
inputs
:
job-prefix
:
# Mandatory string input
description
:
"Define a prefix for the job name"
job-stage
:
# Optional string input with a default value when not provided
default
:
test
environment
:
# Mandatory input that must match one of the options
options
:
[
'test'
,
'staging'
,
'production'
]
concurrency
:
type
:
number
# Optional numeric input with a default value when not provided
default
:
1
version
:
# Mandatory string input that must match the regular expression
type
:
string
regex
:
^v\d\.\d+(\.\d+)$
export_results
:
# Optional boolean input with a default value when not provided
type
:
boolean
default
:
true
---
"$[[ inputs.job-prefix ]]-scan-website"
:
stage
:
$[[ inputs.job-stage ]]
script
:
-
echo "scanning website -e $[[ inputs.environment ]] -c $[[ inputs.concurrency ]] -v $[[ inputs.version ]]"
-
if $[[ inputs.export_results ]]; then echo "export results"; fi
In this example:
job-prefix
is a mandatory string input and must be defined.
job-stage
is optional. If not defined, the value is
test
.
environment
is a mandatory string input that must match one of the defined options.
concurrency
is an optional numeric input. When not specified, it defaults to
1
.
version
is a mandatory string input that must match the specified regular expression.
export_results
is an optional boolean input. When not specified, it defaults to
true
.
Input types
You can specify that an input must use a specific type with the optional
spec:inputs:type
keyword.
The input types are:
array
boolean
number
string
(default when not specified)
When an input replaces an entire YAML value in the CI/CD configuration, it is interpolated
into the configuration as its specified type. For example:
spec
:
inputs
:
array_input
:
type
:
array
boolean_input
:
type
:
boolean
number_input
:
type
:
number
string_input
:
type
:
string
---
test_job
:
allow_failure
:
$[[ inputs.boolean_input ]]
needs
:
$[[ inputs.array_input ]]
parallel
:
$[[ inputs.number_input ]]
script
:
$[[ inputs.string_input ]]
When an input is inserted into a YAML value as part of a larger string, the input
is always interpolated as a string. For example:
spec
:
inputs
:
port
:
type
:
number
---
test_job
:
script
:
curl "https://gitlab.com:$[[ inputs.port ]]"
Array type
History
Introduced
in GitLab 16.11.
The content of the items in an array type can be any valid YAML map, sequence, or scalar. More complex YAML features
like
!reference
cannot be used. When using the value of an array
input in a string (for example
echo "My rules: $[[ inputs.rules-config ]]"
in your
script:
section), you might
see unexpected results. The array input is converted to its string representation, which might not match your
expectations for complex YAML structures such as maps.
spec
:
inputs
:
rules-config
:
type
:
array
default
:
-
if
:
$CI_PIPELINE_SOURCE == "merge_request_event"
when
:
manual
-
if
:
$CI_PIPELINE_SOURCE == "schedule"
---
test_job
:
rules
:
$[[ inputs.rules-config ]]
script
:
ls
Array inputs must be formatted as JSON, for example
["array-input-1", "array-input-2"]
,
when manually passing inputs for:
Manually triggered pipelines
.
The
pipeline triggers API
.
The
pipelines API
.
Git
push options
Pipeline schedules
Multi-line input string values
Inputs support different value types. You can pass multi-string values using the following format:
spec
:
inputs
:
closed_message
:
description
:
Message to announce when an issue is closed.
default
:
'Hi {{author}} :wave:,
Based on the policy for inactive issues, this is now being closed.
If this issue requires further attention, reopen this issue.'
---
Set input values
For configuration added with
include
History
include:with
renamed to
include:inputs
in GitLab 16.0.
Use
include:inputs
to set the values for inputs
when the included configuration is added to the pipeline, including for:
CI/CD components
Custom CI/CD templates
Any other configuration added with
include
.
For example, to include and set the input values for
scan-website-job.yml
from the
input configuration example
:
include
:
-
local
:
'scan-website-job.yml'
inputs
:
job-prefix
:
'some-service-'
environment
:
'staging'
concurrency
:
2
version
:
'v1.3.2'
export_results
:
false
In this example, the inputs for the included configuration are:
Input
Value
Details
job-prefix
some-service-
Must be explicitly defined.
job-stage
test
Not defined in
include:inputs
, so the value comes from
spec:inputs:default
in the included configuration.
environment
staging
Must be explicitly defined, and must match one of the values in
spec:inputs:options
in the included configuration.
concurrency
2
Must be a numeric value to match the
spec:inputs:type
set to
number
in the included configuration. Overrides the default value.
version
v1.3.2
Must be explicitly defined, and must match the regular expression in the
spec:inputs:regex
in the included configuration.
export_results
false
Must be either
true
or
false
to match the
spec:inputs:type
set to
boolean
in the included configuration. Overrides the default value.
With multiple
include
entries
Inputs must be specified separately for each include entry. For example:
include
:
-
component
:
$CI_SERVER_FQDN/the-namespace/the-project/the-component@1.0
inputs
:
stage
:
my-stage
-
local
:
path/to/file.yml
inputs
:
stage
:
my-stage
For a pipeline
History
Introduced
in GitLab 17.11.
Inputs provide advantages over variables including type checking, validation and a clear contract.
Unexpected inputs are rejected.
Inputs for pipelines must be defined in the
spec:inputs
header
of the main
.gitlab-ci.yml
file. You cannot use inputs defined in included files for pipeline-level configuration.
In
GitLab 17.7
and later, pipeline inputs are recommended over passing
pipeline variables
.
For enhanced security, you should
disable pipeline variables
when using inputs.
You should always set default values when defining inputs for pipelines.
Otherwise the pipeline could fail to start if a new pipeline triggers automatically.
For example, merge request pipelines can trigger for changes to a merge request’s source branch.
You cannot manually set inputs for merge request pipelines, so if any input is missing a default,
the pipeline fails to create. This can also happen for branch pipelines, tag pipelines,
and other automatically triggered pipelines.
You can set input values with:
Downstream pipelines
Manually triggered pipelines
.
The
pipeline triggers API
The
pipelines API
Git
push options
Pipeline schedules
The
trigger
keyword
A pipeline can take up to 20 inputs.
Feedback is welcome on
this issue
.
You can pass inputs to
downstream pipelines
,
if the downstream pipeline’s configuration file uses
spec:inputs
.
For example, with
trigger:inputs
:
Parent-child pipeline
trigger-job
:
trigger
:
strategy
:
mirror
include
:
-
local
:
path/to/child-pipeline.yml
inputs
:
job-name
:
"defined"
rules
:
-
if
:
$CI_PIPELINE_SOURCE == 'merge_request_event'
Multi-project pipeline
trigger-job
:
trigger
:
strategy
:
mirror
project
:
project-group/my-downstream-project
inputs
:
job-name
:
"defined"
rules
:
-
if
:
$CI_PIPELINE_SOURCE == 'merge_request_event'
Specify functions to manipulate input values
History
Introduced
in GitLab 16.3.
You can specify predefined functions in the interpolation block to manipulate the input value.
The format supported is the following:
$[[ input.input-id | <function1> | <function2> | ... <functionN> ]]
With functions:
Only
predefined interpolation functions
are permitted.
A maximum of 3 functions may be specified in a single interpolation block.
The functions are executed in the sequence they are specified.
spec
:
inputs
:
test
:
default
:
'test $MY_VAR'
---
test-job
:
script
:
echo $[[ inputs.test | expand_vars | truncate(5,8) ]]
In this example, assuming the input uses the default value and
$MY_VAR
is an unmasked project variable with value
my value
:
First, the function
expand_vars
expands the value to
test my value
.
Then
truncate
applies to
test my value
with a character offset of
5
and length
8
.
The output of
script
would be
echo my value
.
Predefined interpolation functions
expand_vars
History
Introduced
in GitLab 16.5.
Use
expand_vars
to expand
CI/CD variables
in the input value.
Only variables you can
use with the
include
keyword
and which are
not
masked
can be expanded.
Nested variable expansion
is not supported.
Example:
spec
:
inputs
:
test
:
default
:
'test $MY_VAR'
---
test-job
:
script
:
echo $[[ inputs.test | expand_vars ]]
In this example, if
$MY_VAR
is unmasked (exposed in job logs) with a value of
my value
, then the input
would expand to
test my value
.
truncate
History
Introduced
in GitLab 16.3.
Use
truncate
to shorten the interpolated value. For example:
truncate(<offset>,<length>)
Name
Type
Description
offset
Integer
Number of characters to offset by.
length
Integer
Number of characters to return after the offset.
Example:
$[[ inputs.test | truncate(3,5) ]]
Assuming the value of
inputs.test
is
0123456789
, then the output would be
34567
.
posix_quote
History
Introduced
in GitLab 18.6.
Use
posix_quote
to escape any POSIX
Bourne shell
control or meta characters that might be included in input values.
posix_quote
escapes the characters by inserting
\
before any problematic characters in the input.
Example:
spec
:
inputs
:
test
:
default
:
|
A string with single ' and double " quotes and blanks
---
test-job
:
script
:
printf '%s\n' $[[ inputs.test | posix_quote ]]
In this example,
posix_quote
escapes all the characters that could be shell control or metadata characters:
$
printf
'%s\n'
A
\
string
\
with
\
single
\ \'\
and
\
double
\ \"\
quotes
\
and
\ \ \
blanks
A string with single ' and double " quotes and blanks
The escaped input preserves all special characters and spacing exactly as provided.
Not using
posix_quote
can be a security risk if the input contains untrusted input.
Input values that do not escape shell control or metadata characters have risks:
Shell code included in the string might be executed.
Single or double quotes might be used to escape any surrounding quoting.
Variable references could be used to access protected variables.
Input or output redirection might be used to read or write to local files.
Unescaped spaces are used by shells to split a string into multiple arguments.
Escaping might be unnecessary if:
The
spec:input:type
is
number
or
boolean
, which cannot contain problematic characters.
The input value is validated with
spec:input:regex
to prevent problematic input.
The input value is from a trusted source.
If you combine
posix_quote
with
expand_vars
, you must set
expand_vars
first.
Otherwise
posix_quote
would escape the
$
in the variable, preventing expansion.
For example:
test-job
:
script
:
echo $[[ inputs.test | expand_vars | posix_quote ]]
Troubleshooting
YAML syntax errors when using
inputs
CI/CD variable expressions
in
rules:if
expect a comparison of a CI/CD variable with a string, otherwise
a variety of syntax errors could be returned
.
You must ensure that expressions remain properly formatted after input values are
inserted into the configuration, which might require the use of additional quote characters.
For example:
spec
:
inputs
:
branch
:
default
:
$CI_DEFAULT_BRANCH
---
job-name
:
rules
:
-
if
:
$CI_COMMIT_REF_NAME == $[[ inputs.branch ]]
In this example:
Using
include: inputs: branch: $CI_DEFAULT_BRANCH
is valid. The
if:
clause evaluates to
if: $CI_COMMIT_REF_NAME == $CI_DEFAULT_BRANCH
, which is a valid variable expression.
Using
include: inputs: branch: main
is
invalid
. The
if:
clause evaluates to
if: $CI_COMMIT_REF_NAME == main
, which is invalid because
main
is a string but is not quoted.
Alternatively, add quotes to resolve some variable expression issues. For example:
spec
:
inputs
:
environment
:
default
:
"$ENVIRONMENT"
---
$[[ inputs.environment | expand_vars ]] job
:
script
:
echo
rules
:
-
if
:
'"$[[ inputs.environment | expand_vars ]]" == "production"'
In this example, quoting the input block and also the entire variable expression
ensures valid
if:
syntax after the input is evaluated. The internal and external quotes
in the expression must not be the same character. You can use
"
for the internal quotes
and
'
for the external quotes, or the inverse. On the other hand, the job name does
not require any quoting.
