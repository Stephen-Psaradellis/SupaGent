# GitLab container registry | GitLab Docs

Source: https://docs.gitlab.com/user/packages/container_registry/

GitLab container registry | GitLab Docs
GitLab container registry
Tier
: Free, Premium, Ultimate
Offering
: GitLab.com, GitLab Self-Managed, GitLab Dedicated
You can use the integrated container registry to store container images for each GitLab project.
An administrator must enable the container registry for your GitLab instance. For more information,
see
GitLab container registry administration
.
If you pull container images from Docker Hub, you can use the
GitLab Dependency Proxy
to avoid
rate limits and speed up your pipelines.
View the container registry
You can view the container registry for a project or group.
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Deploy
>
Container Registry
.
You can search, sort, filter, and
delete
your container images. You can share a filtered view by copying the URL from your browser.
View the tags of a specific container image in the container registry
You can use the container registry
Tag Details
page to view a list of tags associated with a given container image:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Deploy
>
Container Registry
.
Select your container image.
You can view details about each tag, such as when it was published, how much storage it consumes,
and the manifest and configuration digests.
You can search, sort (by tag name), and delete tags on this page.
You can share a filtered view by copying the URL from your browser.
Storage usage
View container registry storage usage to track and manage the size of your container repositories across projects and groups.
For more information, see
View container registry usage
.
Use container images from the container registry
To download and run a container image hosted in the container registry:
On the left sidebar, select
Search or go to
and find your project or group. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Deploy
>
Container Registry
.
Find the container image you want to work with and select
Copy image path
（
copy-to-clipboard
）.
Use
docker run
with the copied link:
docker run
[
options
]
registry.example.com/group/project/image
[
arguments
]
You must authenticate with the container registry to download
container images from a private repository.
For more information, see
authenticate with the container registry
.
Naming convention for your container images
Your container images must follow this naming convention:
<registry server>/<namespace>/<project>[/<optional path>]
For example, if your project is
gitlab.example.com/mynamespace/myproject
,
then your container image must be named
gitlab.example.com/mynamespace/myproject
.
You can append additional names to the end of a container image name, up to two levels deep.
For example, these are all valid names for container images in the project named
myproject
:
registry.example.com/mynamespace/myproject:some-tag
registry.example.com/mynamespace/myproject/image:latest
registry.example.com/mynamespace/myproject/my/image:rc1
Move or rename container registry repositories
The path of a container repository always matches the related project’s repository path,
so renaming or moving only the container registry is not possible. Instead, you can either:
Rename the project’s repository
.
Transfer the project
.
Renaming projects with populated container repositories is only supported on GitLab.com.
On a GitLab Self-Managed instance, you can delete all container images before moving or renaming
a group or project. Alternatively,
issue 18383
contains community suggestions to work around this limitation.
Epic 9459
proposes adding support for moving projects and groups with container repositories
to GitLab Self-Managed.
Disable the container registry for a project
The container registry is enabled by default.
You can, however, remove the container registry for a project:
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand the
Visibility, project features, permissions
section
and disable
Container registry
.
Select
Save changes
.
The
Deploy
>
Container Registry
entry is removed from the project’s sidebar.
Change visibility of the container registry
By default, the container registry is visible to everyone with access to the project.
You can, however, change the visibility of the container registry for a project.
For more information about the permissions that this setting grants to users,
see
Container registry visibility permissions
.
On the left sidebar, select
Search or go to
and find your project. If you’ve
turned on the new navigation
, this field is on the top bar.
Select
Settings
>
General
.
Expand the section
Visibility, project features, permissions
.
Under
Container registry
, select an option from the dropdown list:
Everyone With Access
(Default): The container registry is visible to everyone with access
to the project. If the project is public, the container registry is also public. If the project
is internal or private, the container registry is also internal or private.
Only Project Members
: The container registry is visible only to project members with
at least the Reporter role. This visibility is similar to the behavior of a private project with Container
Registry visibility set to
Everyone With Access
.
Select
Save changes
.
Container registry visibility permissions
The ability to view the container registry and pull container images is controlled by the container registry’s
visibility permissions. You can change the visibility through the visibility setting on the UI
or the
API
.
Other permissions, such as updating the container registry and pushing or deleting container images, are not affected by
this setting. However, disabling the container registry disables all container registry operations. For more information,
see
Roles and permissions
.
Anonymous
(Everyone on internet)
Guest
Reporter, Developer, Maintainer, Owner
Public project with container registry visibility
set to
Everyone With Access
(UI) or
enabled
(API)
View container registry
and pull images
Yes
Yes
Yes
Public project with container registry visibility
set to
Only Project Members
(UI) or
private
(API)
View container registry
and pull images
No
No
Yes
Internal project with container registry visibility
set to
Everyone With Access
(UI) or
enabled
(API)
View container registry
and pull images
No
Yes
Yes
Internal project with container registry visibility
set to
Only Project Members
(UI) or
private
(API)
View container registry
and pull images
No
No
Yes
Private project with container registry visibility
set to
Everyone With Access
(UI) or
enabled
(API)
View container registry
and pull images
No
No
Yes
Private project with container registry visibility
set to
Only Project Members
(UI) or
private
(API)
View container registry
and pull images
No
No
Yes
Any project with container registry
disabled
All operations on container registry
No
No
No
Supported image types
History
OCI conformance
introduced
in GitLab 16.6.
The container registry supports the
Docker V2
and
Open Container Initiative (OCI)
image formats. Additionally, the container registry
conforms to the OCI distribution specification
.
OCI support means that you can host OCI-based image formats in the registry, such as Helm 3+ chart packages. There is no distinction between image formats in the GitLab API and the UI.
Issue 38047
addresses this distinction, starting with Helm.
Container image signatures
History
Container image signature display
introduced
in GitLab 17.1.
In the GitLab container registry, you can use the
OCI 1.1 manifest
subject
field
to associate container images with
Cosign signatures
.
You can then view signature information alongside its associated container image without having to
search for that signature’s tag.
When viewing a container image’s tags, you see an icon displayed
next to each tag that has an associated signature. To see the details of the signature, select the icon.
Prerequisites:
To sign container images, Cosign v2.0 or later.
For GitLab Self-Managed, you need a GitLab container
registry configured with a metadata database
to display signatures. For more information, see
container registry metadata database
.
Sign container images with OCI referrer data
To add referrer data to signatures using Cosign, you must:
Set the
COSIGN_EXPERIMENTAL
environment variable to
1
.
Add
--registry-referrers-mode oci-1-1
to the signature command.
For example:
COSIGN_EXPERIMENTAL
=
1
cosign sign --registry-referrers-mode oci-1-1 <container image>
While the GitLab container registry supports the OCI 1.1 manifest
subject
field, it does not fully
implement the
OCI 1.1 Referrers API
.
