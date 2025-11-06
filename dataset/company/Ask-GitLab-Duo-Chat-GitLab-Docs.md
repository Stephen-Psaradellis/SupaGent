# Ask GitLab Duo Chat | GitLab Docs

Source: https://docs.gitlab.com/user/gitlab_duo_chat/examples/

Ask GitLab Duo Chat | GitLab Docs
Ask GitLab Duo Chat
Tier
: Premium, Ultimate
Add-on
: GitLab Duo Core, Pro, or Enterprise
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
GitLab Duo Chat helps you:
Get explanations of code, errors, and GitLab features.
Generate or refactor code, write tests, and fix issues.
Create CI/CD configurations and troubleshoot job failures.
Summarize issues, epics, and merge requests.
Resolve security vulnerabilities.
The following examples provide more information on Duo Chat capabilities.
For additional practical examples, see the
GitLab Duo use cases
.
The example questions on this page, including the
slash commands
, are deliberately generic. You might receive more useful responses from Chat by asking questions that are specific to your current goal. For example, “How does the
clean_missing_data
function in
data_cleaning.py
decide which rows to drop?”.
Ask about GitLab
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, and JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
for GitLab.com in GitLab 16.0.
Introduced
ability to ask doc-related questions on GitLab Self-Managed in GitLab 17.0
with a flag
named
ai_gateway_docs_search
. Enabled by default.
Generally available and feature flag removed
in GitLab 17.1.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
You can ask questions about how GitLab works. Things like:
Explain the concept of a 'fork' in a concise manner.
Provide step-by-step instructions on how to reset a user's password.
GitLab Duo Chat uses the GitLab documentation from the
GitLab repository
as source.
To keep Chat up to date with the documentation, its knowledge base is updated daily.
On GitLab.com, the most recent version of the documentation is used.
On GitLab Self-Managed and GitLab Dedicated, the documentation for the version of the instance is used.
Ask about a specific issue
Add-on
: GitLab Duo Enterprise
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
for GitLab.com in GitLab 16.0.
Introduced
for GitLab Self-Managed and GitLab Dedicated in GitLab 16.8.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include Premium in GitLab 18.0.
You can ask about a specific GitLab issue. For example:
Generate a summary for the issue identified via this link: <link to your issue>
When you are viewing an issue in GitLab, you can ask
Generate a concise summary of the current issue.
How can I improve the description of <link to your issue> so that readers understand the value and problems to be solved?
If the issue contains a large amount of text (more than 40,000 words), GitLab Duo Chat might not be able to consider every word. The AI model has a limit to the amount of input it can process at one time.
For tips on how GitLab Duo Chat can improve your productivity with issues and epics, see
Boost your productivity with GitLab Duo Chat
.
Ask about a specific epic
Add-on
: GitLab Duo Enterprise
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
for GitLab.com in GitLab 16.3.
Introduced
for GitLab Self-Managed and GitLab Dedicated in GitLab 16.8.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include Premium in GitLab 18.0.
You can ask about a specific GitLab epic. For example:
Generate a summary for the epic identified via this link: <link to your epic>
When you are viewing an epic in GitLab, you can ask
Generate a concise summary of the opened epic.
What are the unique use cases raised by commenters in <link to your epic>?
If the epic contains a large amount of text (more than 40,000 words), GitLab Duo Chat might not be able to consider every word. The AI model has a limit to the amount of input it can process at one time.
Ask about a specific merge request
Add-on
: GitLab Duo Enterprise
Editor and model information
Editors: GitLab UI
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
in GitLab 17.5.
Changed to require GitLab Duo add-on in GitLab 17.6.
Changed to include Premium in GitLab 18.0.
You can ask GitLab about the merge request you’re viewing. You can ask about:
The title or description.
Comments and threads.
The content on the
Changes
tab.
Metadata, like labels, source branch, author, milestone, and more.
While in the merge request, open Chat and type your question. For example:
Why was the .vue file changed?
What do the reviewers say about this merge request?
How can this merge request be improved?
Which files and changes should I review first?
Ask about a specific commit
Add-on
: GitLab Duo Enterprise
Editor and model information
Editors: GitLab UI
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
in GitLab 17.6.
Changed to include Premium in GitLab 18.0.
You can ask about a specific GitLab commit. For example:
Generate a summary for the commit identified with this link: <link to your commit>
How can I improve the description of this commit?
When you are viewing a commit in GitLab, you can ask
Generate a summary of the current commit.
Ask about a specific pipeline job
Add-on
: GitLab Duo Enterprise
Editor and model information
Editors: GitLab UI
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
in GitLab 17.6.
Changed to include Premium in GitLab 18.0.
You can ask about a specific GitLab pipeline job. For example:
Generate a summary for the pipeline job identified via this link: <link to your pipeline job>
Can you suggest ways to fix this failed pipeline job?
What are the main steps executed in this pipeline job?
When you are viewing a pipeline job in GitLab, you can ask
Generate a summary of the current pipeline job.
Ask about a specific work item
Add-on
: GitLab Duo Enterprise
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
in GitLab 18.2.
You can ask about a specific GitLab work item. For example:
Generate a summary for the work item identified via this link: <link to your work item>
When you are viewing an work item in GitLab, you can ask
Generate a concise summary of the current work item.
How can I improve the description of <link to your work item> so that readers understand the value and problems to be solved?
If the work item contains a large amount of text (more than 40,000 words), GitLab Duo Chat might not be able to consider every word. The AI model has a limit to the amount of input it can process at one time.
Explain selected code
Add-on
: GitLab Duo Core, Pro, or Enterprise, GitLab Duo with Amazon Q
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Introduced
for GitLab.com in GitLab 16.7.
Introduced
for GitLab Self-Managed and GitLab Dedicated in GitLab 16.8.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
You can ask GitLab Duo Chat to explain selected code:
Select some code in your IDE.
In Duo Chat, type
/explain
.
You can also add additional instructions to be considered. For example:
/explain the performance
/explain focus on the algorithm
/explain the performance gains or losses using this code
/explain the object inheritance
(classes, object-oriented)
/explain why a static variable is used here
(C++)
/explain how this function would cause a segmentation fault
(C)
/explain how concurrency works in this context
(Go)
/explain how the request reaches the client
(REST API, database)
For more information, see:
Use GitLab Duo Chat in VS Code
.
Application modernization with GitLab Duo (C++ to Java)
.
In the GitLab UI, you can also explain code in:
A
file
.
A
merge request
.
Ask about or generate code
Add-on
: GitLab Duo Core, Pro, or Enterprise
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
for GitLab.com in GitLab 16.1.
Introduced
for GitLab Self-Managed and GitLab Dedicated in GitLab 16.8.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
You can ask GitLab Duo Chat questions about code by pasting that code into
the Chat window. For example:
Provide a clear explanation of this Ruby code: def sum(a, b) a + b end.
Describe what this code does and how it works.
You can also ask Chat to generate code. For example:
Write a Ruby function that prints 'Hello, World!' when called.
Develop a JavaScript program that simulates a two-player Tic-Tac-Toe game. Provide both game logic and user interface, if applicable.
Create a regular expression for parsing IPv4 and IPv6 addresses in Python.
Generate code for parsing a syslog log file in Java. Use regular expressions when possible, and store the results in a hash map.
Create a product-consumer example with threads and shared memory in C++. Use atomic locks when possible.
Generate Rust code for high performance gRPC calls. Provide a source code example for a server and client.
Ask follow-up questions
Add-on
: GitLab Duo Core, Pro, or Enterprise
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM for GitLab Self-Managed, GitLab Dedicated: Anthropic
Claude 3.5 Sonnet V2
LLM for GitLab.com: Anthropic
Claude 4.0 Sonnet
History
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
You can ask follow-up questions to delve deeper into the topic or task at hand.
This helps you get more detailed and precise responses tailored to your specific needs,
whether it’s for further clarification, elaboration, or additional assistance.
A follow-up to the question
Write a Ruby function that prints 'Hello, World!' when called
could be:
Can you also explain how I can call and execute this Ruby function in a typical Ruby environment, such as the command line?
A follow-up to the question
How to start a C# project?
could be:
Can you also explain how to add a .gitignore and .gitlab-ci.yml file for C#?
Ask about errors
Add-on
: GitLab Duo Core, Pro, or Enterprise
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM for GitLab Self-Managed, GitLab Dedicated: Anthropic
Claude 3.5 Sonnet V2
LLM for GitLab.com: Anthropic
Claude 4.0 Sonnet
History
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
Programming languages that require compiling the source code may throw cryptic error messages. Similarly, a script or a web application could throw a stack trace. You can ask GitLab Duo Chat by prefixing the copied error message with, for example,
Explain this error message:
. Add the specific context, like the programming language.
Explain this error message in Java: Int and system cannot be resolved to a type
Explain when this C function would cause a segmentation fault: sqlite3_prepare_v2()
Explain what would cause this error in Python: ValueError: invalid literal for int()
Why is "this" undefined in VueJS? Provide common error cases, and explain how to avoid them.
How to debug a Ruby on Rails stacktrace? Share common strategies and an example exception.
Ask about specific files in the IDE
Add-on
: GitLab Duo Core, Pro, or Enterprise
Editor and model information
Editors: VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
in GitLab 17.7
with flags
named
duo_additional_context
and
duo_include_context_file
. Disabled by default.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Enabled on GitLab.com and GitLab Self-Managed
in GitLab 17.9.
Generally available
in GitLab 18.0. All feature flags removed.
Changed to include the GitLab Duo Core add-on in GitLab 18.0.
Add repository files to your Duo Chat conversations in VS Code or JetBrains IDEs
by typing
/include
and choosing the files.
Prerequisites:
The files must be part of a repository.
The files must be text-based. Binary files, like PDFs or images, are not supported.
To do this:
In your IDE, in GitLab Duo Chat, type
/include
.
To add files, you can either:
Select the files from the list.
Enter the file path.
For example, if you are developing an e-commerce app, you can add the
cart_service.py
and
checkout_flow.js
files to Chat’s context and ask:
How does checkout_flow.js interact with cart_service.py? Generate a sequence diagram using Mermaid.
Can you extend the checkout process by showing products related to the ones in the user's cart? I want to move the checkout logic to the backend before proceeding. Generate the Python backend code and change the frontend code to work with the new backend.
You cannot use
Quick Chat
to add files or ask questions about files added for Chat’s context.
Refactor code in the IDE
Add-on
: GitLab Duo Core, Pro, or Enterprise, GitLab Duo with Amazon Q
Editor and model information
Editors: Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Introduced
for GitLab.com in GitLab 16.7.
Introduced
for GitLab Self-Managed and GitLab Dedicated in GitLab 16.8.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
You can ask GitLab Duo Chat to refactor selected code:
Select some code in your IDE.
In Duo Chat, type
/refactor
.
You can include additional instructions to be considered. For example:
Use a specific coding pattern, for example
/refactor with ActiveRecord
or
/refactor into a class providing static functions
.
Use a specific library, for example
/refactor using mysql
.
Use a specific function/algorithm, for example
/refactor into a stringstream with multiple lines
in C++.
Refactor to a different programming language, for example
/refactor to TypeScript
.
Focus on performance, for example
/refactor improving performance
.
Focus on potential vulnerabilities, for example
/refactor avoiding memory leaks and exploits
.
/refactor
uses
Repository X-Ray
to deliver more accurate, context-aware suggestions.
For more information, see:
Application modernization with GitLab Duo (C++ to Java)
.
Watch an overview
Fix code in the IDE
Add-on
: GitLab Duo Core, Pro, or Enterprise, GitLab Duo with Amazon Q
Editor and model information
Editors: Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Introduced
for GitLab.com, GitLab Self-Managed and GitLab Dedicated in GitLab 17.3.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
You can ask GitLab Duo Chat to fix selected code:
Select some code in your IDE.
In Duo Chat, type
/fix
.
You can include additional instructions to be considered. For example:
Focus on grammar and typos, for example,
/fix grammar mistakes and typos
.
Focus on a concrete algorithm or problem description, for example,
/fix duplicate database inserts
or
/fix race conditions
.
Focus on potential bugs that are not directly visible, for example,
/fix potential bugs
.
Focus on code performance problems, for example,
/fix performance problems
.
Focus on fixing the build when the code does not compile, for example,
/fix the build
.
/fix
uses
Repository X-Ray
to deliver more accurate, context-aware suggestions.
Write tests in the IDE
Add-on
: GitLab Duo Core, Pro, or Enterprise, GitLab Duo with Amazon Q
Editor and model information
Editors: Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Introduced
for GitLab.com in GitLab 16.7.
Introduced
for GitLab Self-Managed and GitLab Dedicated in GitLab 16.8.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
You can ask GitLab Duo Chat to create tests for the selected code:
Select some code in your IDE.
In Duo Chat, type
/tests
.
You can include additional instructions to be considered. For example:
Use a specific test framework, for example
/tests using the Boost.test framework
(C++) or
/tests using Jest
(JavaScript).
Focus on extreme test cases, for example
/tests focus on extreme cases, force regression testing
.
Focus on performance, for example
/tests focus on performance
.
Focus on regressions and potential exploits, for example
/tests focus on regressions and potential exploits
.
/tests
uses
Repository X-Ray
to deliver more accurate, context-aware suggestions.
For more information, see
Use GitLab Duo Chat in VS Code
.
Watch an overview
Ask about CI/CD
Add-on
: GitLab Duo Pro or Enterprise
Editor and model information
Editors: GitLab UI, Web IDE, VS Code, JetBrains IDEs
LLM: Anthropic
Claude 4.0 Sonnet
History
Introduced
for GitLab.com in GitLab 16.7.
Introduced
for GitLab Self-Managed and GitLab Dedicated in GitLab 16.8.
Updated LLM
from Claude 2.1 to Claude 3 Sonnet in GitLab 17.2.
Updated LLM
from Claude 3 Sonnet to Claude 3.5 Sonnet in GitLab 17.2.
Changed to require GitLab Duo add-on in GitLab 17.6.
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Updated LLM
from Claude 3.5 Sonnet to Claude 4.0 Sonnet in GitLab 17.10.
You can ask GitLab Duo Chat to create a CI/CD configuration:
Create a .gitlab-ci.yml configuration file for testing and building a Ruby on Rails application in a GitLab CI/CD pipeline.
Create a CI/CD configuration for building and linting a Python application.
Create a CI/CD configuration to build and test Rust code.
Create a CI/CD configuration for C++. Use gcc as compiler, and cmake as build tool.
Create a CI/CD configuration for VueJS. Use npm, and add SAST security scanning.
Generate a security scanning pipeline configuration, optimized for Java.
You can also ask to explain specific job errors by copy-pasting the error message, prefixed with
Explain this CI/CD job error message, in the context of <language>:
:
Explain this CI/CD job error message in the context of a Go project: build.sh: line 14: go command not found
Alternatively, you can use GitLab Duo Root Cause Analysis to
troubleshoot failed CI/CD jobs
.
Troubleshoot failed CI/CD jobs with Root Cause Analysis
Add-on
: GitLab Duo Enterprise, GitLab Duo with Amazon Q
Editor and model information
Editors: GitLab UI
LLM: Anthropic
Claude 4.0 Sonnet
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Introduced
in GitLab 16.2 as an
experiment
on GitLab.com.
Generally available
and moved to GitLab Duo Chat in GitLab 17.3.
Changed to require GitLab Duo add-on in GitLab 17.6.
Failed jobs widget for merge requests
introduced
in GitLab 17.7.
Changed to include Premium in GitLab 18.0.
You can use GitLab Duo Root Cause Analysis in GitLab Duo Chat to quickly identify and fix CI/CD job failures.
It analyzes the last 100,000 characters of the job log to determine the cause of failure and provides an example fix.
You can access this feature either from the
Pipelines
tab in merge requests or directly from the job log.
Watch overview
Root Cause Analysis does not support:
Trigger jobs
Downstream pipelines
Provide feedback on this feature in
epic 13872
.
Prerequisites:
You must have permission to view the CI/CD job.
You must have a paid GitLab Duo Enterprise seat.
From a merge request
To troubleshoot a failed CI/CD job from a merge request:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Go to your merge request.
Select the
Pipelines
tab.
From the Failed jobs widget, either:
Select the job ID to go to the job log.
Select
Troubleshoot
to analyze the failure directly.
From the job log
To troubleshoot a failed CI/CD job from the job log:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Build
>
Jobs
.
Select the failed CI/CD job.
Below the job log, either:
Select
Troubleshoot
.
Open GitLab Duo Chat and type
/troubleshoot
.
Explain a vulnerability
Tier
: Ultimate
Add-on
: GitLab Duo Enterprise, GitLab Duo with Amazon Q
Editor and model information
Editors: GitLab UI
LLM: Anthropic
Claude 4.0 Sonnet
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Changed to require GitLab Duo add-on in GitLab 17.6.
You can ask GitLab Duo Chat to explain a vulnerability when you are viewing a SAST vulnerability report.
For more information, see
Explaining a vulnerability
.
Create a new conversation
Add-on
: GitLab Duo Pro or Enterprise
Offering
: GitLab.com
Editors
: GitLab UI
History
Introduced
in GitLab 17.10
with a flag
named
duo_chat_multi_thread
. Disabled by default.
Generally available
in GitLab 18.1. Feature flag
duo_chat_multi_thread
removed.
In GitLab 17.10 and later, you can have multiple simultaneous conversations with Chat.
In the upper-left corner of the Chat drawer, select
New Chat
.
In the text box, type
/new
and press
Enter
or select
Send
.
Delete or start a new conversation
To delete a conversation, use the
chat history
.
To clear the chat window and start a new conversation in the same conversation thread,
type
/reset
and select
Send
.
In both cases, the conversation history will not be considered when you ask new questions.
Starting a new conversation might help improve the answers when you switch contexts,
because Duo Chat will not get confused by the unrelated conversations.
GitLab Duo Chat slash commands
Duo Chat has a list of universal, GitLab UI, and IDE commands, each of which is preceded by a slash (
/
).
Use the commands to quickly accomplish specific tasks.
Universal
Add-on
: GitLab Duo Core, Pro, or Enterprise
Editors
: GitLab UI, Web IDE, VS Code, JetBrains IDEs
History
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
Command
Purpose
/new
Start a new conversation, but keep the previous conversations in the chat history
/reset
Clear the chat window and reset the conversation
/help
Learn more about how Duo Chat works
On GitLab.com, in GitLab 17.10 and later, when having
multiple conversations
, the
/clear
and
/reset
slash commands are replaced by the
/new
slash command
.
GitLab UI
Add-on
: GitLab Duo Enterprise
Editors
: GitLab UI
History
Changed to include Premium in GitLab 18.0.
These commands are dynamic and are available only in the GitLab UI when using Duo Chat:
Command
Purpose
Area
/summarize_comments
Generate a summary of all comments on the current issue
Issues
/troubleshoot
Troubleshoot failed CI/CD jobs with Root Cause Analysis
Jobs
/vulnerability_explain
Explain current vulnerability
Vulnerabilities
IDE
Add-on
: GitLab Duo Core, Pro, or Enterprise
Editors
: Web IDE, VS Code, JetBrains IDEs
History
Enabled
for
self-hosted model configuration
as well as the
default GitLab external AI vendor configuration
in GitLab 17.9.
Changed to include GitLab Duo Core add-on in GitLab 18.0.
These commands work only when using Duo Chat in supported IDEs:
Command
Purpose
/tests
Write tests
/explain
Explain code
/refactor
Refactor the code
/fix
Fix the code
/include
Include file context
