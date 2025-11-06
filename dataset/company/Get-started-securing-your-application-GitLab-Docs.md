# Get started securing your application | GitLab Docs

Source: https://docs.gitlab.com/user/application_security/get-started-security/

Get started securing your application | GitLab Docs
Get started securing your application
Identify and remediate vulnerabilities in your application’s source code.
Integrate security testing into the software development lifecycle
by automatically scanning your code for potential security issues.
You can scan various programming languages and frameworks,
and detect vulnerabilities like SQL injection, cross-site scripting (XSS),
and insecure dependencies. The results of the security scans are displayed in the GitLab UI,
where you can review and address them.
These features can also be integrated with other GitLab features like merge requests
and pipelines to ensure that security is a priority throughout the development process.
For an overview, see
Adopting GitLab application security
View an interactive reading and how-to demo playlist
This process is part of a larger workflow:
Step 1: Learn about scanning
Secret detection scans your repository to help prevent your secrets from being exposed.
It works with all programming languages.
Dependency scanning analyzes your application’s dependencies for known vulnerabilities.
It works with certain languages and package managers.
For more information, see:
Secret detection
Dependency scanning
Step 2: Choose a project to test
If it’s your first time setting up GitLab security scanning, you should start with a single project.
The project should:
Use your organization’s typical programming languages and technologies,
because some scanning features work differently for different languages.
Allow you to try new settings, like required approvals, without interrupting your team’s daily work.
You can create a copy of a high-traffic project, or select a project that’s not as busy.
Step 3: Enable scanning
To identify leaked secrets and vulnerable packages in the project,
create a merge request that enables secret detection and dependency scanning.
This merge request updates your
.gitlab-ci.yml
file, so that the scans
run as part of your project’s CI/CD pipeline.
As part of this MR, you can change settings to accommodate your project’s layout or configuration.
For example, you might exclude a directory of third-party code.
After you merge this MR to your default branch, the system creates a baseline scan.
This scan identifies which vulnerabilities already exist on the default branch.
Then, merge requests will highlight any newly introduced problems.
Without a baseline scan, merge requests display every vulnerability in the branch,
even if the vulnerability already exists on the default branch.
For more information, see:
Enable secret detection
Secret detection settings
Enable dependency scanning
Dependency scanning settings
Step 4: Review scan results
Let your team get comfortable with viewing security findings in merge requests
and the vulnerability report.
Establish a vulnerability triage workflow. Consider creating labels and issue boards
to help manage issues created from vulnerabilities. With issue boards, all stakeholders
have a common view of all issues and can track remediation progress.
Monitor the Security Dashboard trends to gauge success in remediating existing vulnerabilities
and preventing the introduction of new ones.
For more information, see:
View the vulnerability report
View security findings in merge requests
View the security dashboard
Labels
Issue boards
Step 5: Schedule future scanning jobs
Enforce scheduled security scanning jobs by using a scan execution policy.
These scheduled jobs run independently from any other security scans you
might have defined in a compliance framework pipeline or in the project’s
.gitlab-ci.yml
file.
Scheduled scans are most useful for projects or important branches with
low development activity and where pipeline scans are infrequent.
For more information, see:
Scan execution policy
Container scans
Operational container scanning
Step 6: Limit new vulnerabilities
To enforce required scan types and ensure separation of duties between security and engineering,
use scan execution policies.
To limit new vulnerabilities from being merged into your default branch,
create a merge request approval policy.
After you’ve gotten familiar with how scanning works, you can then choose to:
Follow the same steps to enable scanning in more projects.
Enforce scanning across more of your projects at once.
For more information, see:
Scan execution policies
Merge request approval policy
Step 7: Continue scanning for new vulnerabilities
Over time, you want to ensure new vulnerabilities are not introduced.
To surface newly discovered vulnerabilities that already exist in your repository,
run regular dependency and container scans.
To scan container images in your production cluster for security vulnerabilities,
enable operational container scanning.
Enable other scan types, like SAST, DAST, or fuzz testing.
To allow for DAST and Web API fuzzing on ephemeral test environments,
consider enabling review apps.
For more information, see:
SAST
DAST
Fuzz testing
Web API fuzzing
Review apps
