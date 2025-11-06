# Visual Studio troubleshooting | GitLab Docs

Source: https://docs.gitlab.com/editor_extensions/visual_studio/visual_studio_troubleshooting/

Visual Studio troubleshooting | GitLab Docs
Visual Studio troubleshooting
If the steps on this page don’t solve your problem, check the
list of open issues
in the Visual Studio plugin’s project. If an issue matches your problem, update the issue.
If no issues match your problem,
create a new issue
.
For troubleshooting the extension for GitLab Duo Code Suggestions,
see
Troubleshooting Code Suggestions
..
View more logs
More logs are available in the
GitLab Extension Output
window:
In Visual Studio, on the top bar, go to the
Tools
>
Options
menu.
Find the
GitLab
option, and set
Log Level
to
Debug
.
Go to
View
>
Output
to open the extension log. In the dropdown list, select
GitLab Extension
as the log filter.
Verify that the debug log contains similar output:
GetProposalManagerAsync: Code suggestions enabled. ContentType
(
csharp
)
or file extension
(
cs
)
is supported.
GitlabProposalSourceProvider.GetProposalSourceAsync
View activity log
If your extension does not load or crashes, check the activity log for errors.
Your activity log is available in this location:
C:\Users\WINDOWS_USERNAME\AppData\Roaming\Microsoft\VisualStudio\VS_VERSION\ActivityLog.xml
Replace these values in the directory path:
WINDOWS_USERNAME
: Your Windows username.
VS_VERSION
: The version of your Visual Studio installation.
Required Information for Support
Before contacting Support, make sure the latest GitLab extension is installed. Visual Studio should automatically update to the latest version of the extension.
Gather this information from affected users, and provide it in your bug report:
The error message shown to the user.
Workflow and Language Server logs:
Enable debug logs
.
Retrieve log files
.
Diagnostics output:
With Visual Studio open, on the top banner, select
Help
>
About Microsoft Visual Studio
.
On the dialog, select
Copy Info
to copy all the required information for this section to your clipboard.
System details:
With Visual Studio open, on the top banner, select
Help
>
About Microsoft Visual Studio
.
On the dialog, select
System Info
to see more detailed information.
For
OS type and version
: Copy the
OS Name
and
Version
.
For
Machine specifications (CPU, RAM)
: copy the
Processor
and
Installed Physical Memory (RAM)
sections.
Describe the scope of impact. How many users are affected?
Describe how to reproduce the error Include a screen recording, if possible.
Describe how other GitLab Duo features are affected:
Is Code Suggestions working?
Does Web IDE Duo Chat return responses?
Perform extension isolation testing. Try disabling (or uninstalling) all other extensions to determine
if another extension is causing the issue. This helps determine if the problem is with our extension,
or from an external source.
