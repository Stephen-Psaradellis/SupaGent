# DAST profiles | GitLab Docs

Source: https://docs.gitlab.com/user/application_security/dast/profiles/#scanner-profile

DAST profiles | GitLab Docs
DAST profiles
Tier
: Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
DAST site and scanner profiles save information related to your applications and the scanners you use to evaluate them.
Once you define a profile, you can use it for pipeline and on-demand DAST jobs.
The creation, updating, and deletion of DAST profiles, DAST scanner profiles,
and DAST site profiles are included in the
audit log
.
Site profile
History
Site profile features, scan method and file URL, were
enabled on GitLab.com and GitLab Self-Managed
in GitLab 15.6.
GraphQL endpoint path feature was
introduced
in GitLab 15.7.
Additional variables
introduced
in GitLab 17.9.
A site profile defines the attributes and configuration details of the deployed application,
website, or API to be scanned by DAST.
A site profile contains:
Profile name
: A name you assign to the site to be scanned. While a site profile is referenced
in either
.gitlab-ci.yml
or an on-demand scan, it
cannot
be renamed.
Site type
: The type of target to be scanned, either website or API scan.
Target URL
: The URL that DAST runs against.
Excluded URLs
: A comma-separated list of URLs to exclude from the scan.
You can use
RE2-style regex
. The regex can’t include the question mark (
?
) character, because it is a valid URL character.
Request headers
: A comma-separated list of HTTP request headers, including names and values. These headers are added to every request made by DAST.
Authentication
:
Authenticated URL
: The URL of the page containing the sign-in HTML form on the target website. The username and password are submitted with the login form to create an authenticated scan.
Username
: The username used to authenticate to the website.
Password
: The password used to authenticate to the website.
Username form field
: The name of username field at the sign-in HTML form.
Password form field
: The name of password field at the sign-in HTML form.
Submit form field
: The
id
or
name
of the element that when selected submits the sign-in HTML form.
Scan method
: A type of method to perform API testing. The supported methods are OpenAPI, Postman Collections, HTTP Archive (HAR), or GraphQL.
GraphQL endpoint path
: The path to the GraphQL endpoint. This path is concatenated with the target URL to provide the URI for the scan to test. The GraphQL endpoint must support introspection queries.
File URL
: The URL of the OpenAPI, Postman Collection, or HTTP Archive file.
Additional variables
: A list of environment variables to configure specific scan behaviors. These variables provide the same configuration options as pipeline-based DAST scans, such as setting timeouts, adding an authentication success URL, or enabling advanced scan features.
When an API site type is selected, a host override is used to ensure the API being scanned is on the same host as the target. This is done to reduce the risk of running an active scan against the wrong API.
When configured, request headers and password fields are encrypted using
aes-256-gcm
before being stored in the database.
This data can only be read and decrypted with a valid secrets file.
You can reference a site profile in
.gitlab-ci.yml
and
on-demand scans.
stages
:
-
dast
include
:
-
template
:
DAST.gitlab-ci.yml
dast
:
stage
:
dast
dast_configuration
:
site_profile
:
"<profile name>"
Site profile validation
Site profile validation reduces the risk of running an active scan against the wrong website. You must validate a site to run an on-demand scan against it.
Site profile validation is not a security feature. If necessary, you can run DAST against an unvalidated site with a
pipeline scan
.
Each of the site validation methods are equivalent in functionality, so use whichever is most suitable:
Text file validation
: Requires a text file be uploaded to the target site. The text file is
allocated a name and content that is unique to the project. The validation process checks the
file’s content.
Header validation
: Requires the header
Gitlab-On-Demand-DAST
be added to the target site,
with a value unique to the project. The validation process checks that the header is present, and
checks its value.
Meta tag validation
: Requires the meta tag named
gitlab-dast-validation
be added to the
target site, with a value unique to the project. Make sure it’s added to the
<head>
section of
the page. The validation process checks that the meta tag is present, and checks its value.
Create a site profile
To create a site profile:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select
New
>
Site profile
.
Complete the fields then select
Save profile
.
The site profile is saved, for use in an on-demand scan.
Edit a site profile
Edit a site profile to change its settings before a scan.
If a site profile is linked to a security policy, you cannot edit the profile from this page. See
scan execution policies
for more information.
To activate the site validation pipeline, you must define a runner with the tag
dast-validation-runner
or define a runner that can run untagged jobs.
Prerequisites:
If a DAST scan uses the profile, you must be able to push to the branch associated with the scan.
To edit a site profile:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select the
Site Profiles
tab.
In the profile’s row select the
More actions
(
ellipsis_v
) menu, then select
Edit
.
Edit the fields then select
Save profile
.
If a site profile’s target or authenticated URL is updated, the request headers and password fields associated with that profile are cleared.
Delete a site profile
Prerequisites:
If a DAST scan uses the profile, you must be able to push to the branch associated with the scan.
If a site profile is linked to a security policy, a user cannot delete the profile from this page.
See
Scan execution policies
for more information.
To delete a site profile:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select the
Site Profiles
tab.
In the profile’s row, select the
More actions
(
ellipsis_v
) menu, then select
Delete
.
Select
Delete
to confirm the deletion.
Validate a site profile
Validating a site is required to run an active scan.
Prerequisites:
A runner must be available in the project to run a validation job.
To validate a site profile:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select the
Site Profiles
tab.
In the profile’s row, select
Validate
.
Select the validation method.
For
Text file validation
:
Download the validation file listed in
Step 2
.
Upload the validation file to the host, to the location in
Step 3
or any location you
prefer.
If required, edit the file location in
Step 3
.
Select
Validate
.
For
Header validation
:
Select the clipboard icon in
Step 2
.
Edit the header of the site to validate, and paste the clipboard content.
Select the input field in
Step 3
and enter the location of the header.
Select
Validate
.
For
Meta tag validation
:
Select the clipboard icon in
Step 2
.
Edit the content of the site to validate, and paste the clipboard content.
Select the input field in
Step 3
and enter the location of the meta tag.
Select
Validate
.
The site is validated and an active scan can run against it. A site profile’s validation status is
revoked only when it’s revoked manually, or its file, header, or meta tag is edited.
Retry a failed validation
Failed site validation attempts are listed on the
Site profiles
tab of the
Manage profiles
page.
To retry a site profile’s failed validation:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select the
Site Profiles
tab.
In the profile’s row, select
Retry validation
.
Revoke a site profile’s validation status
When a site profile’s validation status is revoked, all site profiles that share the same URL also
have their validation status revoked.
To revoke a site profile’s validation status:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Beside the validated profile, select
Revoke validation
.
The site profile’s validation status is revoked.
Validated site profile headers
The following are code samples of how you can provide the required site profile header in your
application.
Ruby on Rails example for on-demand scan
Here’s how you can add a custom header in a Ruby on Rails application:
class
DastWebsiteTargetController
<
ActionController
::
Base
def
dast_website_target
response
.
headers
[
'Gitlab-On-Demand-DAST'
]
=
'0dd79c9a-7b29-4e26-a815-eaaf53fcab1c'
head
:ok
end
end
Django example for on-demand scan
Here’s how you can add a
custom header in Django
:
class
DastWebsiteTargetView
(
View
):
def
head
(
self
,
*
args
,
**
kwargs
):
response
=
HttpResponse
()
response
[
'Gitlab-On-Demand-DAST'
]
=
'0dd79c9a-7b29-4e26-a815-eaaf53fcab1c'
return
response
Node (with Express) example for on-demand scan
Here’s how you can add a
custom header in Node (with Express)
:
app
.
get
(
'/dast-website-target'
,
function
(
req
,
res
)
{
res
.
append
(
'Gitlab-On-Demand-DAST'
,
'0dd79c9a-7b29-4e26-a815-eaaf53fcab1c'
)
res
.
send
(
'Respond to DAST ping'
)
})
Scanner profile
History
Deprecated AJAX Spider option with the introduction of Browser based on-demand DAST scans in GitLab 17.0.
Renamed spider timeout to crawl timeout with the introduction of Browser based on-demand DAST scans in GitLab 17.0.
A scanner profile defines the configuration details of a security scanner.
A scanner profile contains:
Profile name
: A name you give the scanner profile. For example, “Spider_15”. While a scanner
profile is referenced in either
.gitlab-ci.yml
or an on-demand scan, it
cannot
be renamed.
Scan mode
: A passive scan monitors all HTTP messages (requests and responses) sent to the target. An active scan attacks the target to find potential vulnerabilities.
Crawl timeout
: The maximum number of minutes allowed for the crawler to traverse the site.
Target timeout
: The maximum number of seconds DAST waits for the site to be available before
starting the scan.
Debug messages
: Include debug messages in the DAST console output.
You can reference a scanner profile in
.gitlab-ci.yml
and
on-demand scans.
stages
:
-
dast
include
:
-
template
:
DAST.gitlab-ci.yml
dast
:
stage
:
dast
dast_configuration
:
scanner_profile
:
"<profile name>"
Create a scanner profile
To create a scanner profile:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select
New
>
Scanner profile
.
Complete the form. For details of each field, see
Scanner profile
.
Select
Save profile
.
Edit a scanner profile
Prerequisites:
If a DAST scan uses the profile, you must be able to push to the branch associated with the scan.
If a scanner profile is linked to a security policy, you cannot edit the profile from this page.
For more information, see
Scan execution policies
.
To edit a scanner profile:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select the
Scanner profiles
tab.
In the scanner’s row, select the
More actions
(
ellipsis_v
) menu, then select
Edit
.
Edit the form.
Select
Save profile
.
Delete a scanner profile
Prerequisites:
If a DAST scan uses the profile, you must be able to push to the branch associated with the scan.
If a scanner profile is linked to a security policy, a user cannot delete the profile from this
page. For more information, see
Scan execution policies
.
To delete a scanner profile:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Secure
>
Security configuration
.
In the
Dynamic Application Security Testing (DAST)
section, select
Manage profiles
.
Select the
Scanner profiles
tab.
In the scanner’s row, select the
More actions
(
ellipsis_v
) menu, then select
Delete
.
Select
Delete
.
