# Contribute to GitLab development | GitLab Docs

Source: https://docs.gitlab.com/development/contributing/

Contribute to GitLab development | GitLab Docs
Contribute to GitLab development
Thank you for your interest in contributing to GitLab.
You can contribute new features, changes to code or processes, typo fixes,
or updates to language in the interface.
This guide details how to contribute to the development of GitLab.
For a step-by-step guide for first-time contributors, see
Tutorial: Make a GitLab contribution
.
How to contribute
Read the
Code of Conduct
.
Request access to the community forks
.
Choose or create an issue to work on
.
Choose a development environment
.
Make changes and open a merge request.
Your merge request is triaged, reviewed, and can then be incorporated into the product.
All contributions must be submitted in English. GitLab engineering work is done in English,
and merge requests and issues in other languages cannot be reviewed or accepted.
GitLab technologies
GitLab
is a
Ruby on Rails
application.
It uses
Haml
and a JavaScript-based frontend with
Vue.js
.
Some satellite projects use
Go
.
For example:
GitLab Runner
Gitaly
GLab
GitLab Terraform Provider
We have
development style guides for each technology
to help you align with our coding standards.
If you want to contribute to the
website
or the
handbook
,
go to the footer of any page and select
View page source
to open the page in the repository.
Choose or create an issue
If you’re not sure what to work on, you can use the
issue finder
on the
contributor platform
to find and assign yourself.
It is recommended to start with an issue with the label
quick win::first-time contributor
.
If you know what you’re going to work on, see if an issue already exists.
If it doesn’t, open a
new issue
.
Select the appropriate template and add all the necessary information about the work you plan to do.
Tag a
merge request coach
with
@gitlab-bot help
on the issue or through the contributors platform to help
validate the issue
.
You do not need to be assigned to the issue to get started.
If the issue already has an assignee, ask if they are still working on the issue or if they would like to collaborate.
For details, see
the issues workflow
.
Join the community
Request access to the community forks
,
a set of forks mirrored from GitLab repositories in order to improve the contributor experience.
When you request access to the community forks you will receive an onboarding issue in the
community onboarding project
.
For more information, read about the community forks in the
Meta repository README
.
Additionally, we recommend you join the
GitLab Discord server
,
where GitLab team members and the wider community are ready and waiting to answer your questions
and offer support for making contributions.
Choose a development environment
To write and test your code locally, choose a local development environment.
GitLab Development Kit (GDK)
, is a local
development environment that includes an installation of GitLab Self-Managed, sample projects,
and administrator access with which you can test functionality.
GDK-in-a-box
,
packages GDK into a pre-configured container image that you can connect to with VS Code.
Follow
Configure GDK-in-a-box
to set up GDK-in-a-box.
To install GDK and its dependencies, follow the steps in
Install the GDK development environment
.
Open a merge request
Go to
the community fork on GitLab.com
.
If you don’t see this message, on the left sidebar, select
Code > Merge requests > New merge request
.
Take a look at the branch names. You should be merging from your branch
in the community fork to the
master
branch in the GitLab repository.
Fill out the information and then select
Save changes
.
Don’t worry if your merge request is not complete.
If you don’t want anyone from GitLab to review it, you can select the
Mark as draft
checkbox.
If you’re not happy with the merge request after you create it, you can close it, no harm done.
If you’re happy with this merge request and want to start the review process, type
@gitlab-bot ready
in a comment and then select
Comment
.
Someone from GitLab will look at your request and let you know what the next steps are.
For details, see the
merge request workflow
.
Have questions?
Use
@gitlab-bot help
to ping a GitLab Merge Request coach. For more information on MR coaches, visit
How GitLab Merge Request Coaches Can Help You
.
How community merge requests are triaged
When you create a merge request, a merge request coach will assign relevant reviewers or
guide you through the review themselves if possible.
The goal is to have a merge request reviewed within a week after a reviewer is assigned.
At times this may take longer due to high workload, holidays, or other reasons.
If you need to, find a
merge request coach
who specializes in the type of code you have written and mention them in the merge request.
For example, if you have written some frontend code, you should mention the frontend merge request coach.
If your code has multiple disciplines, you can mention multiple merge request coaches.
For details about timelines and how you can request help or escalate a merge request,
see the
Wider Community Merge Request guide
.
After your merge request is reviewed and merged, your changes will be deployed to GitLab.com and included in the next release!
Review process
When you submit code to GitLab, we really want it to get merged!
However, we review submissions carefully, and this takes time.
Code submissions are usually reviewed by two
domain experts
before being merged:
A
reviewer
.
A
maintainer
.
After review, the reviewer could ask the author to update the merge request.
In that case, the reviewer will set the
~"workflow::in dev"
label.
Once you have updated the merge request with the requested changes, comment on it with
@gitlab-bot ready
to signal that it is ready for review again.
This process may repeat several times before merge.
Read our
merge request guidelines for contributors before you start for the first time
.
Make sure to follow our commit message guidelines
.
Write a great description that includes steps to reproduce your implementation.
Automated testing is required. Take your time to understand the different
testing levels
and apply them accordingly.
Contributing to Premium/Ultimate features with an Enterprise Edition license
If you would like to work on GitLab features that are within a paid tier, the code that lives in the
EE directory
, it requires a GitLab Enterprise Edition license.
Request an Enterprise Edition Developers License according to the
documented process
.
Get help
How to find help contributing to GitLab:
Type
@gitlab-bot help
in a comment on a merge request or issue to tag a MR coach.
See
How GitLab Merge Request Coaches Can Help You
for more information.
Join the
GitLab Community Discord
and ask for help in the
#contribute
channel.
Email the Contributor Success team at
contributors@gitlab.com
.
