# Add files to your branch | GitLab Docs

Source: https://docs.gitlab.com/topics/git/add_files/

Add files to your branch | GitLab Docs
Add files to your branch
Use Git to add files to a branch in your local repository.
This action creates a snapshot of the file for your
next commit and starts version control monitoring.
When you add files with Git, you:
Prepare content for version control tracking.
Create a record of file additions and modifications.
Preserve file history for future reference.
Make project files available for team collaboration.
Add files to a Git repository
To add a new file from the command line:
Open a terminal.
Change directories until you are in your project’s folder.
cd
my-project
Choose a Git branch to work in.
To create a branch:
git checkout -b <branchname>
To switch to an existing branch:
git checkout <branchname>
Copy the file you want to add into the directory where you want to add it.
Confirm that your file is in the directory:
Windows:
dir
All other operating systems:
ls
The filename should be displayed.
Check the status of the file:
git status
The filename should be in red. The file is in your file system, but Git isn’t tracking it yet.
Tell Git to track the file:
git add <filename>
Check the status of the file again:
git status
The filename should be green. The file is staged (tracked locally) by Git, but
has not been
committed and pushed
.
Add a file to the last commit
To add changes to a file to the last commit, instead of to a new commit, amend the existing commit:
git add <filename>
git commit --amend
If you do not want to edit the commit message, append
--no-edit
to the
commit
command.
Related topics
Add file from the UI
Add file from the Web IDE
Sign commits
