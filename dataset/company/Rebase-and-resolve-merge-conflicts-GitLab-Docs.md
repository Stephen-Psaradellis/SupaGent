# Rebase and resolve merge conflicts | GitLab Docs

Source: https://docs.gitlab.com/topics/git/git_rebase/

Rebase and resolve merge conflicts | GitLab Docs
Rebase and resolve merge conflicts
Git rebase combines changes from one branch into another by moving your commits to the
tip of the target branch. This action:
Updates branches with the latest code from the target branch.
Maintains a clean, linear commit history for easier debugging and code reviews.
Resolves
merge conflicts
at the commit level
for conflict resolution.
Preserves the chronological order of code changes.
When you rebase:
Git imports all the commits submitted to your target branch after you initially created
your branch from it.
Git applies the commits from your branch on top of the imported commits. In this example, after
a branch named
feature
is created (in orange), four commits from
main
(in purple) are
imported into the
feature
branch:
While most rebases are performed against
main
, you can rebase against any other
branch. You can also specify a different remote repository.
For example,
upstream
instead of
origin
.
git rebase
rewrites the commit history. It can cause conflicts in
shared branches and complex merge conflicts.
Instead of rebasing your branch against the default branch,
consider using
git pull origin master
. Pulling has similar
effects with less risk of compromising others’ work.
Rebase
When you use Git to rebase, each commit is applied to your branch.
When merge conflicts occur, you are prompted to address them.
For more advanced options for your commits, use
an interactive rebase
.
Prerequisites:
You must have
permissions
to force push to branches.
To use Git to rebase your branch against the target branch:
Open a terminal and change to your project directory.
Ensure you have the latest contents of the target branch.
In this example, the target branch is
main
:
git fetch origin main
Check out your branch:
git checkout my-branch
Optional. Create a backup of your branch:
git branch my-branch-backup
Changes added to
my-branch
after this point are lost
if you restore from the backup branch.
Rebase against the
main
branch:
git rebase origin/main
If merge conflicts exist:
Resolve the conflicts in your editor.
Stage the changes:
git add .
Continue the rebase:
git rebase --continue
Force push your changes to the target branch, while protecting others’ commits:
git push origin my-branch --force-with-lease
Interactive rebase
Use an interactive rebase to specify how to handle each commit.
The following instructions use the
Vim
text editor to edit commits.
To rebase interactively:
Open a terminal and change to your project directory.
Ensure you have the latest contents of the target branch. In this example, the target branch is
main
:
git fetch origin main
Check out your branch:
git checkout my-branch
Optional. Create a backup of your branch:
git branch my-branch-backup
Changes added to
my-branch
after this point are lost
if you restore from the backup branch.
In the GitLab UI, in your merge request, confirm the number of commits
to rebase in the
Commits
tab.
Open these commits. For example, to edit the last five commits:
git rebase -i HEAD~5
Git opens the commits in your terminal text editor, oldest first.
Each commit shows the action to take, the SHA, and the commit title. For example:
pick
111111111111
Second round of structural revisions
pick
222222222222
Update inbound link to this changed page
pick
333333333333
Shifts from H4 to H3
pick
444444444444
Adds revisions from editorial
pick
555555555555
Revisions
continue
to build the concept part out
# Rebase 111111111111..222222222222 onto zzzzzzzzzzzz (5 commands)
#
# Commands:
# p, pick <commit> = use commit
# r, reword <commit> = use commit, but edit the commit message
# e, edit <commit> = use commit, but stop for amending
# s, squash <commit> = use commit, but meld into previous commit
# f, fixup [-C | -c] <commit> = like "squash" but keep only the previous
Switch to Vim’s edit mode by pressing
i
.
Use the arrow keys to move the cursor to the commit you want to edit.
For each commit, except the first one, change
pick
to
squash
or
fixup
(or
s
or
f
).
Repeat for the remaining commits.
End edit mode, save, and quit:
Press
ESC
.
Type
:wq
.
When squashing, Git prompts you to edit the commit message:
Lines starting with
#
are ignored and not included in the commit
message.
To keep the current message, type
:wq
.
To edit the commit message, switch to
edit mode, make changes, and save.
Push your changes to the target branch.
If you didn’t push your commits to the target branch before rebasing:
git push origin my-branch
If you already pushed the commits:
git push origin my-branch --force-with-lease
Some actions require a force push to make changes to the branch. For more information, see
Force push to a remote branch
.
Resolve conflicts from the command line
To give you the most control over each change, you should fix complex conflicts locally from the command line, instead of in GitLab.
Prerequisites:
You must have
permissions
to force push to branches.
Open the terminal and check out your feature branch:
git switch my-feature-branch
Rebase your branch against the target branch. In this example, the target branch is
main
:
git fetch
git rebase origin/main
Open the conflicting file in your preferred code editor.
Locate and resolve the conflict block:
Choose which version (before or after
=======
) you want to keep.
Delete the version you don’t want to keep.
Delete the conflict markers.
Save the file.
Repeat the process for each file with conflicts.
Stage your changes:
git add .
Commit your changes:
git commit -m
"Resolve merge conflicts"
You can run
git rebase --abort
to stop the process before this point.
Git aborts the rebase and rolls back the branch to the state
before running
git rebase
. After you run
git rebase --continue
, you cannot abort the rebase.
Continue the rebase:
git rebase --continue
Force push the changes to your
remote branch:
git push origin my-feature-branch --force-with-lease
Force push to a remote branch
Complex Git operations like squashing commits, resetting a branch, or rebasing rewrite branch history.
Git requires a forced update for these changes.
Force pushing is not recommended on shared branches, because you risk destroying
others’ changes.
If the branch is
protected
,
you can’t force push unless you:
Unprotect it.
Allow force pushes.
For more information, see
Allow force push on a protected branch
.
Restore your backed up branch
If a rebase or force push fails, restore your branch from its backup:
Ensure you’re on the correct branch:
git checkout my-branch
Reset your branch to the backup:
git reset --hard my-branch-backup
Approving after rebase
If you rebase a branch, you’ve added commits. If your project is configured to
prevent approvals by users who add commits
,
you can’t approve a merge request you’ve rebased. In addition, users who were previously committers,
and could not previously approve, might now be able to approve the changes.
Additionally, users who approved and then performed a rebase might still show as having approved
the merge request. However, the user’s approval does not count toward the required approvals for
the merge request.
Related topics
Revert and undo changes
Git documentation for branches and rebases
Project squash and merge settings
Merge conflicts
Troubleshooting
For CI/CD pipeline troubleshooting information, see
Debugging CI/CD pipelines
.
Unmergeable state
after
/rebase
quick action
The
/rebase
command schedules a background task. The task attempts to rebase
the changes in the source branch on the latest commit of the target branch.
If, after using the
/rebase
quick action
,
you see this error, a rebase cannot be scheduled:
This merge request is currently in an unmergeable state, and cannot be rebased.
This error occurs if any of these conditions are true:
Conflicts exist between the source and target branches.
The source branch contains no commits.
Either the source or target branch does not exist.
An error has occurred, resulting in no diff being generated.
To resolve the
unmergeable state
error:
Resolve any merge conflicts.
Confirm the source branch exists, and has commits.
Confirm the target branch exists.
Confirm the diff has been generated.
/merge
quick action ignored after
/rebase
If
/rebase
is used,
/merge
is ignored to avoid a race condition where the source branch is merged or deleted before it is rebased.
