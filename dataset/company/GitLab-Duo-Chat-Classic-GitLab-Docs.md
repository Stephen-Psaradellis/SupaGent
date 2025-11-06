# GitLab Duo Chat (Classic) | GitLab Docs

Source: https://docs.gitlab.com/user/gitlab_duo_chat/

GitLab Duo Chat (Classic) | GitLab Docs
GitLab Duo Chat (Classic)
Tier
: Premium, Ultimate
Add-on
: GitLab Duo Core, Pro, or Enterprise, GitLab Duo with Amazon Q
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
Model information
LLMs: Anthropic Claude and Vertex AI Search. The LLM depends on the question asked.
LLM for Amazon Q: Amazon Q Developer
Available on
GitLab Duo with self-hosted models
: Yes
History
Introduced
as an
experiment
for SaaS in GitLab 16.0.
Changed to
beta
for SaaS in GitLab 16.6.
Introduced
as a beta for GitLab Self-Managed in GitLab 16.8.
Changed
from Ultimate to Premium tier in GitLab 16.9 while in beta.
Generally available
in GitLab 16.11.
Changed to require GitLab Duo add-on in GitLab 17.6 and later.
Updated naming to GitLab Duo Chat (Classic) in GitLab 18.3.
Added
to GitLab Duo Core in GitLab 18.3.
GitLab Duo Chat (Classic) is an AI assistant that accelerates development with
contextual, conversational AI. Chat:
Explains code and suggests improvements directly in your development environment.
Analyzes code, merge requests, issues, and other GitLab artifacts.
Generates code, tests, and documentation based on your requirements and codebase.
Integrates directly in the GitLab UI, Web IDE, VS Code, JetBrains IDEs, and Visual Studio.
Can include information from your repositories and projects to deliver targeted improvements.
Watch an overview
Learn about the new
GitLab Duo Chat (Agentic)
.
Supported editor extensions
You can use GitLab Duo Chat in:
The GitLab UI
The GitLab Web IDE (VS Code in the cloud)
You can also use GitLab Duo Chat in these IDEs by installing an editor extension:
VS Code
JetBrains
Eclipse
Visual Studio
If you have GitLab Self-Managed: Use GitLab 17.2 and later for the best user experience and results. Earlier versions may continue to work, but the experience might be degraded.
Use GitLab Duo Chat in the GitLab UI
History
Changed
to be available on all pages in the GitLab UI for GitLab.com in GitLab 18.5.
New navigation and GitLab Duo sidebar introduced on GitLab.com in GitLab 18.6 with a
flag
named
paneled_view
. Enabled by default.
The availability of the new navigation and GitLab Duo sidebar is controlled by a feature flag.
For more information, see the history.
Prerequisites:
You must have access to GitLab Duo Chat and GitLab Duo must be turned on.
On GitLab Self-Managed, you must be where Chat is available. It is not available on:
The
Your work
pages, like the To-Do List.
Your
User settings
page.
The
Help
menu.
Instructions are provided for the new navigation and classic navigation.
Select the tab for your navigation type, or
learn how to switch
.
New navigation
On the top bar, select
Search or go to
and find your project.
On the GitLab Duo sidebar, select either
Current GitLab Duo Chat
(
comment
) or
New GitLab Duo Chat
(
plus
).
A Chat conversation opens in the GitLab Duo sidebar on the right side of your screen.
Enter your question in the message box and press
Enter
or select
Send
.
You can provide additional
context
for your chat.
It might take a few seconds for the interactive AI chat to produce an answer.
Optional. You can:
Ask a follow-up question.
Start
another conversation
.
Classic navigation
On the left sidebar, select
Search or go to
and find your project.
In the upper-right corner, select
Open GitLab Duo Chat
(
duo-chat
).
A drawer opens on the right side of your screen.
Enter your question in the message box and press
Enter
or select
Send
.
You can provide additional
context
for your chat.
It might take a few seconds for the interactive AI chat to produce an answer.
Optional. You can:
Ask a follow-up question.
Start
another conversation
.
To ask a new, unrelated question, type
/reset
and select
Send
to clear the context.
View the Chat history
The 25 most recent messages are retained in the chat history.
New navigation
On the GitLab Duo sidebar, select
GitLab Duo Chat history
(
history
).
Classic navigation
In the upper-right corner of the Chat, select
Chat history
(
history
).
Have multiple conversations
History
Introduced
in GitLab 17.10
with a flag
named
duo_chat_multi_thread
. Disabled by default.
Enabled on GitLab Self-Managed
in GitLab 17.11.
Generally available
in GitLab 18.1. Feature flag
duo_chat_multi_thread
removed.
In GitLab 17.10 and later, you can have an unlimited number of simultaneous conversations with Chat.
New navigation
Create a new Chat conversation by doing either of the following:
On the GitLab Duo sidebar, select
New GitLab Duo Chat
(
plus
).
In the message box, type
/new
and press
Enter
or select
Send
.
A new Chat conversation replaces the previous one.
To view all of your conversations, view the
Chat history
.
To switch between conversations, in your Chat history, select the appropriate conversation.
Classic navigation
In the upper-right corner, select
Open GitLab Duo Chat
(
duo-chat
). A drawer opens on the right side of your screen.
Create a new Chat conversation by doing either of the following:
In the upper-right corner of an existing conversation, select
New chat
(
duo-chat-new
).
In the message box, type
/new
and press
Enter
or select
Send
.
A new Chat conversation replaces the previous one.
To view all of your conversations, view the
Chat history
.
To switch between conversations, in your Chat history, select the appropriate conversation.
Every conversation persists an unlimited number of messages. However, only the last 25 messages are sent to the LLM to fit the content in the LLM’s context window.
Conversations created before this feature was enabled are not visible in the Chat history.
Delete a conversation
To delete a conversation:
Select the
Chat history
.
In the history, select
Delete this chat
(
remove
).
By default, individual conversations expire and are automatically deleted after 30 days of inactivity.
However, administrators can
change this expiration period
.
Use GitLab Duo Chat in the Web IDE
History
Introduced in GitLab 16.6 as an
experiment
.
Changed to generally available in GitLab 16.11.
To use GitLab Duo Chat in the Web IDE on GitLab:
Open the Web IDE:
In the GitLab UI, on the left sidebar, select
Search or go to
and find your project.
Select a file. Then in the upper right, select
Edit
>
Open in Web IDE
.
Open Chat by using one of the following methods:
On the left sidebar, select
GitLab Duo Chat
.
In the file that you have open in the editor, select some code.
Right-click and select
GitLab Duo Chat
.
Select
Explain selected snippet
,
Fix
,
Generate tests
,
Open Quick Chat
, or
Refactor
.
Use the keyboard shortcut:
On Windows or Linux:
ALT
+
d
On macOS:
Option
+
d
In the message box, enter your question and press
Enter
or select
Send
.
If you have selected code in the editor, this selection is included with your question to GitLab Duo Chat.
For example, you can select code and ask Chat,
Can you simplify this?
.
Check configuration diagnostics
To check your GitLab Duo configuration diagnostics and system settings, including
system versioning, feature state management, and feature flags:
In the Chat pane, in the upper-right corner, select
Status
.
Use GitLab Duo Chat in VS Code
History
Introduced in GitLab 16.6 as an
experiment
.
Changed to generally available in GitLab 16.11.
Status
added
in the GitLab Workflow extension for VS Code 5.29.0.
Prerequisites:
You’ve
installed and configured the VS Code extension
.
To use GitLab Duo Chat in the GitLab Workflow extension for VS Code:
In VS Code, open a file. The file does not need to be a file in a Git repository.
On the left sidebar, select
GitLab Duo Chat
(
duo-chat
).
In the message box, enter your question and press
Enter
or select
Send
.
If you have selected code in the editor, this selection is included with your question to GitLab Duo Chat.
For example, you can select code and ask Chat,
Can you simplify this?
.
Use Chat while working in the editor window
History
Introduced as
generally available
in the GitLab Workflow extension for VS Code 5.15.0.
Insert Snippet
added
in the GitLab Workflow extension for VS Code 5.25.0.
To open GitLab Duo Chat in the editor window, use any of these methods:
From a keyboard shortcut:
On Windows and Linux:
ALT
+
c
On macOS:
Option
+
c
In the currently open file in your IDE, right-click and select
GitLab Duo Chat
>
Open Quick Chat
.
Select some code to provide additional context.
Open the Command Palette, then select
GitLab Duo Chat: Open Quick Chat
.
After Quick Chat opens:
In the message box, enter your question. You can also:
Type
/
to display all available commands.
Type
/re
to display
/refactor
and
/reset
.
To send your question, select
Send
, or press
Command
+
Enter
.
To interact with the responses, above the code blocks, use the
Copy Snippet
and
Insert Snippet
links.
To exit chat, select the chat icon in the gutter, or press
Escape
while focused on the chat.
Check the status of Chat
To check the health of your GitLab Duo configuration:
In the chat pane, in the upper-right corner, select
Status
.
Close Chat
To close GitLab Duo Chat:
For GitLab Duo Chat on the left sidebar, select
GitLab Duo Chat
(
duo-chat
).
For the quick chat window that’s embedded in your file, in the upper-right corner,
select
Collapse
(
chevron-lg-up
).
Use GitLab Duo Chat in Visual Studio for Windows
Prerequisites:
You’ve
installed and configured the GitLab extension for Visual Studio
.
To use GitLab Duo Chat in the GitLab extension for Visual Studio:
In Visual Studio, open a file. The file does not need to be a file in a Git repository.
Open Chat by using one of the following methods:
In the top menu bar, select
Extensions
, and then select
Open Duo Chat
.
In the file that you have open in the editor, select some code.
Right-click and select
GitLab Duo Chat
.
Select
Explain selected code
or
Generate Tests
.
In the message box, enter your question and press
Enter
or select
Send
.
If you have selected code in the editor, this selection is sent along with your question to the AI. This way you can ask questions about this code selection. For instance,
Could you refactor this?
.
Use GitLab Duo Chat in JetBrains IDEs
History
Introduced as generally available in GitLab 16.11.
Prerequisites:
You’ve
installed and configured the GitLab plugin for JetBrains IDEs
.
To use GitLab Duo Chat in the GitLab plugin for JetBrains IDEs:
In a JetBrains IDE, open a project.
Open GitLab Duo Chat in either a chat window or an editor window.
In a chat window
To open GitLab Duo Chat in a chat window, use any of these methods:
On the right tool window bar, select
GitLab Duo Chat
.
From a keyboard shortcut:
On Windows and Linux:
ALT
+
d
On macOS:
Option
+
d
From an open editor file:
Right-click and select
GitLab Duo Chat
.
Select
Open Chat Window
.
With selected code:
In an editor, select code to include with your command.
Right-click and select
GitLab Duo Chat
.
Select
Explain Code
,
Fix Code
,
Generate Tests
, or
Refactor Code
.
From a highlighted code issue:
Right-click and select
Show Context Actions
.
Select
Fix with Duo
.
With a keyboard or mouse shortcut for a GitLab Duo action, which you can set in
Settings
>
Keymap
.
After GitLab Duo Chat opens:
In the message box, enter your question. You can also:
Type
/
to display all available commands.
Type
/re
to display
/refactor
and
/reset
.
To send your question, press
Enter
or select
Send
.
Use the buttons within code blocks in the responses to interact with them.
In an editor window
History
Introduced as generally available in the
GitLab Duo plugin for JetBrains 3.0.0
and
GitLab Workflow extension for VS Code 5.14.0
.
To open GitLab Duo Chat in the editor window, use any of these methods:
From a keyboard shortcut:
On Windows and Linux:
ALT
+
c
On macOS:
Option
+
c
In an open file in your IDE, select some code,
then, in the floating toolbar, select
GitLab Duo Quick Chat
(
tanuki-ai
).
Right-click and select
GitLab Duo Chat
>
Open Quick Chat
.
After Quick Chat opens:
In the message box, enter your question. You can also:
Type
/
to display all available commands.
Type
/re
to display
/refactor
and
/reset
.
To send your question, press
Enter
.
To interact with the responses, use the buttons around the code blocks.
To exit chat, either select
Escape to close
, or press
Escape
while focused on the chat.
View how to use GitLab Duo Quick Chat
.
Use GitLab Duo Chat in Eclipse
History
Changed
from experiment to beta in GitLab 17.11.
Prerequisites:
You’ve
installed and configured the GitLab for Eclipse plugin
.
To use GitLab Duo Chat in the GitLab for Eclipse plugin:
Open a project in Eclipse.
Select
GitLab Duo Chat
(
duo-chat
), or use the keyboard shortcut:
On Windows and Linux:
ALT
+
d
On macOS:
Option
+
d
In the message box, enter your question and press
Enter
or select
Send
.
Configure Chat conversation expiration
History
Introduced
in GitLab 17.11.
You can configure how long conversations persist before they expire and are automatically deleted.
Prerequisites:
You must be an administrator.
On the left sidebar, at the bottom, select
Admin
. If you’ve
turned on the new navigation
, in the upper-right corner, select your avatar and then select
Admin
.
Select
GitLab Duo
.
In the lower-right corner, select
Change configuration
.
In the
GitLab Duo Chat conversation expiration
section, select either of the following options:
Expire conversation based on time conversation was last updated
.
Expire conversation based on time conversation was created
.
Select
Save changes
.
Available language models
Different language models can be the source for GitLab Duo Chat.
On GitLab.com or GitLab Self-Managed, the default GitLab AI vendor models and
cloud-based AI gateway that is hosted by GitLab.
On GitLab Self-Managed, in GitLab 17.9 and later,
GitLab Duo Self-Hosted with a supported self-hosted model
. Self-hosted models maximize
security and privacy by making sure nothing is sent to an external model. You can use GitLab AI vendor models, other supported language models, or bring your own compatible model.
Input and output length
For each Chat conversation, input and output length is limited:
Input is limited to 200,000 tokens (roughly 680,000 characters). The input tokens
include:
All the
context that Chat is aware of
.
All the previous questions and answers in that conversation.
Output is limited to 8,192 tokens (roughly 28,600 characters).
Give feedback
Your feedback is important to us as we continually enhance the GitLab Duo Chat experience.
Leaving feedback helps us customize the Chat for your needs and improve its performance for everyone.
To give feedback about a specific response, use the feedback buttons in the response message.
Or, you can add a comment in the
feedback issue
.
