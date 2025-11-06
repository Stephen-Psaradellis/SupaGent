# Install GitLab using the Linux package | GitLab Docs

Source: https://docs.gitlab.com/install/package/

Install GitLab using the Linux package | GitLab Docs
Install GitLab using the Linux package
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
The Linux packages are mature, scalable, and are used on GitLab.com. If you need additional
flexibility and resilience, we recommend deploying GitLab as described in the
reference architecture documentation
.
The Linux package is quicker to install, easier to upgrade, and contains
features to enhance reliability not found in other installation methods. Install through a
single package (also known as Omnibus GitLab) that bundles all the different services
and tools required to run GitLab. See the
installation requirements
to learn about the minimum hardware requirements.
Linux packages are available in our packages repository for:
GitLab Enterprise Edition
.
GitLab Community Edition
.
Check that the required GitLab version is available for your host operating system.
Supported platforms
GitLab officially supports long term support (LTS) versions of operating
systems. Some operating systems, such as Ubuntu, have a clear distinction
between LTS and non-LTS versions. However, there are other operating systems,
openSUSE for example, that don’t follow the LTS concept.
We will usually provide support for a version of an operating system until it
is no longer supported by its vendor, where support is defined as standard or
maintenance support and not as expanded, extended, or premium support. However,
we might end support earlier than the operating system’s vendor in these
circumstances:
Business considerations: Including but not limited to low customer adoption,
disproportionate maintenance costs, or strategic product direction changes.
Technical constraints: When third-party dependencies, security requirements,
or underlying technology changes make continued support impractical or
impossible.
Vendor actions: When operating system vendors make changes that fundamentally
impact our software’s functionality or when required components become
unavailable.
We will usually issue a deprecation notice at least 6 months before support for
any operating system version is discontinued, on a best-effort basis. In cases
where technical constraints, vendor actions, or other external factors require
that we provide shorter notice periods, we will communicate any support changes
as soon as reasonably possible.
amd64
and
x86_64
refer to the same 64-bit architecture. The names
arm64
and
aarch64
are also interchangeable
and refer to the same architecture.
Operating system
First supported GitLab version
Architecture
Operating system EOL
Proposed last supported GitLab version
Upstream release notes
AlmaLinux 8
GitLab CE / GitLab EE 14.5.0
x86_64
,
aarch64
1
Mar 2029
GitLab CE / GitLab EE 21.10.0
AlmaLinux details
AlmaLinux 9
GitLab CE / GitLab EE 16.0.0
x86_64
,
aarch64
1
May 2032
GitLab CE / GitLab EE 25.0.0
AlmaLinux details
AlmaLinux 10
GitLab CE / GitLab EE 18.6.0
x86_64
,
aarch64
1
May 2035
GitLab CE / GitLab EE 28.0.0
AlmaLinux details
Amazon Linux 2
GitLab CE / GitLab EE 14.9.0
amd64
,
arm64
1
June 2026
GitLab CE / GitLab EE 19.1.0
Amazon Linux details
Amazon Linux 2023
GitLab CE / GitLab EE 16.3.0
amd64
,
arm64
1
June 2029
GitLab CE / GitLab EE 22.1.0
Amazon Linux details
Debian 11
GitLab CE / GitLab EE 14.6.0
amd64
,
arm64
1
Aug 2026
GitLab CE / GitLab EE 19.3.0
Debian Linux details
Debian 12
GitLab CE / GitLab EE 16.1.0
amd64
,
arm64
1
June 2028
GitLab CE / GitLab EE 19.3.0
Debian Linux details
Debian 13
GitLab CE / GitLab EE 18.5.0
amd64
,
arm64
1
June 2030
GitLab CE / GitLab EE 23.1.0
Debian Linux details
openSUSE Leap 15.6
GitLab CE / GitLab EE 17.6.0
x86_64
,
aarch64
1
Dec 2025
TBD
openSUSE details
SUSE Linux Enterprise Server 12
GitLab EE 9.0.0
x86_64
Oct 2027
TBD
SUSE Linux Enterprise Server details
SUSE Linux Enterprise Server 15
GitLab EE 14.8.0
x86_64
Dec 2024
TBD
SUSE Linux Enterprise Server details
Oracle Linux 8
GitLab CE / GitLab EE 12.8.1
x86_64
July 2029
GitLab CE / GitLab EE 22.2.0
Oracle Linux details
Oracle Linux 9
GitLab CE / GitLab EE 16.2.0
x86_64
June 2032
GitLab CE / GitLab EE 25.1.0
Oracle Linux details
Oracle Linux 10
GitLab CE / GitLab EE 18.6.0
x86_64
June 2035
GitLab CE / GitLab EE 28.1.0
Oracle Linux details
Red Hat Enterprise Linux 8
GitLab CE / GitLab EE 12.8.1
x86_64
,
arm64
1
May 2029
GitLab CE / GitLab EE 22.0.0
Red Hat Enterprise Linux details
Red Hat Enterprise Linux 9
GitLab CE / GitLab EE 16.0.0
x86_64
,
arm64
1
May 2032
GitLab CE / GitLab EE 25.0.0
Red Hat Enterprise Linux details
Red Hat Enterprise Linux 10
GitLab CE / GitLab EE 18.6.0
x86_64
,
arm64
1
May 2035
GitLab CE / GitLab EE 28.0.0
Red Hat Enterprise Linux details
Ubuntu 20.04
GitLab CE / GitLab EE 13.2.0
amd64
,
arm64
1
April 2025
GitLab CE / GitLab EE 18.8.0
Ubuntu details
Ubuntu 22.04
GitLab CE / GitLab EE 15.5.0
amd64
,
arm64
1
April 2027
GitLab CE / GitLab EE 19.11.0
Ubuntu details
. FIPS packages were added in GitLab 18.4. Before upgrading from Ubuntu 20.04, view the
upgrade notes
.
Ubuntu 24.04
GitLab CE / GitLab EE 17.1.0
amd64
,
arm64
1
April 2029
GitLab CE / GitLab EE 21.11.0
Ubuntu details
Footnotes
:
Known issues
exist for running GitLab on ARM.
Unofficial, unsupported installation methods
The following installation methods are provided as-is by the wider GitLab
community and are not supported by GitLab:
Debian native package
(by Pirate Praveen)
FreeBSD package
(by Torsten Zühlsdorff)
Arch Linux package
(by the Arch Linux community)
Puppet module
(by Vox Pupuli)
Ansible playbook
(by Jeff Geerling)
GitLab virtual appliance (KVM)
(by OpenNebula)
GitLab on Cloudron
(via Cloudron App Library)
End-of-life versions
GitLab provides Linux packages for operating systems only until their
end-of-life (EOL) date. After the EOL date, GitLab stops releasing
official packages.
However, sometimes we don’t deprecate an operating system even after it’s EOL
because we can’t provide packages for a newer version.
The most common reason for this is PackageCloud, our package repository provider,
not supporting newer versions and so we can’t upload packages to it.
The list of deprecated operating systems and the final GitLab
release for them can be found below:
OS version
End of life
Last supported GitLab version
CentOS 6 and RHEL 6
November 2020
GitLab CE
/
GitLab EE
13.6
CentOS 7 and RHEL 7
June 2024
GitLab CE
/
GitLab EE
17.7
CentOS 8
December 2021
GitLab CE
/
GitLab EE
14.6
Oracle Linux 7
December 2024
GitLab CE
/
GitLab EE
17.7
Scientific Linux 7
June 2024
GitLab CE
/
GitLab EE
17.7
Debian 7 Wheezy
May 2018
GitLab CE
/
GitLab EE
11.6
Debian 8 Jessie
June 2020
GitLab CE
/
GitLab EE
13.3
Debian 9 Stretch
June 2022
GitLab CE
/
GitLab EE
15.2
Debian 10 Buster
June 2024
GitLab CE
/
GitLab EE
17.5
OpenSUSE 42.1
May 2017
GitLab CE
/
GitLab EE
9.3
OpenSUSE 42.2
January 2018
GitLab CE
/
GitLab EE
10.4
OpenSUSE 42.3
July 2019
GitLab CE
/
GitLab EE
12.1
OpenSUSE 13.2
January 2017
GitLab CE
/
GitLab EE
9.1
OpenSUSE 15.0
December 2019
GitLab CE
/
GitLab EE
12.5
OpenSUSE 15.1
November 2020
GitLab CE
/
GitLab EE
13.12
OpenSUSE 15.2
December 2021
GitLab CE
/
GitLab EE
14.7
OpenSUSE 15.3
December 2022
GitLab CE
/
GitLab EE
15.10
OpenSUSE 15.4
December 2023
GitLab CE
/
GitLab EE
16.7
OpenSUSE 15.5
December 2024
GitLab CE
/
GitLab EE
17.8
SLES 15 SP2
December 2024
GitLab EE
Raspbian Wheezy
May 2015
GitLab CE
8.17
Raspbian Jessie
May 2017
GitLab CE
11.7
Raspbian Stretch
June 2020
GitLab CE
13.3
Raspberry Pi OS Buster
June 2024
GitLab CE
17.7
Ubuntu 12.04
April 2017
GitLab CE
/
GitLab EE
9.1
Ubuntu 14.04
April 2019
GitLab CE
/
GitLab EE
11.10
Ubuntu 16.04
April 2021
GitLab CE
/
GitLab EE
13.12
Ubuntu 18.04
June 2023
GitLab CE
/
GitLab EE
16.11
Raspberry Pi OS (32-bit - Raspbian)
GitLab dropped support for Raspberry Pi OS (32 bit - Raspbian) with GitLab
17.11 being the last version available for the 32-bit platform. Starting with
GitLab 18.0, you should move to Raspberry Pi OS (64 bit) and use the
Debian arm64 package
.
For information on backing up data on a 32-bit OS and restoring it to a 64-bit
OS, see
Upgrading operating systems for PostgreSQL
.
Uninstall the Linux package
To uninstall the Linux package, you can opt to either keep your data (repositories,
database, configuration) or remove all of them:
Optional. To remove
all users and groups created by the Linux package
before removing the package:
sudo gitlab-ctl stop
&&
sudo gitlab-ctl remove-accounts
If you have a problem removing accounts or groups, run
userdel
or
groupdel
manually
to delete them. You might also want to manually remove the leftover user home directories
from
/home/
.
Choose whether to keep your data or remove all of them:
To preserve your data (repositories, database, configuration), stop GitLab and
remove its supervision process:
sudo systemctl stop gitlab-runsvdir
sudo systemctl disable gitlab-runsvdir
sudo rm /usr/lib/systemd/system/gitlab-runsvdir.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
sudo gitlab-ctl uninstall
To remove all data:
sudo gitlab-ctl cleanse
&&
sudo rm -r /opt/gitlab
Uninstall the package (replace with
gitlab-ce
if you have GitLab FOSS installed):
apt
# Debian/Ubuntu
sudo apt remove gitlab-ee
dnf
# AlmaLinux/RHEL/Oracle Linux/Amazon Linux 2023
sudo dnf remove gitlab-ee
zypper
# OpenSUSE Leap/SLES
sudo zypper remove gitlab-ee
yum
# Amazon Linux 2
sudo yum remove gitlab-ee
Ubuntu 22.04 FIPS
Known compatibility issues currently exist between GitLab FIPS mode and Ubuntu 22.04. Administrators should refrain from upgrading their host operating system to Ubuntu 22.04 until further notice.
This advisory will be updated once the issues have been identified and resolved.
In GitLab 18.4 and later, FIPS builds are available for Ubuntu 22.04.
Before you upgrade:
Verify password hash migration for all active users: In GitLab 17.11 and later,
user passwords are automatically rehashed with enhanced salt when users sign in.
Any users who haven’t completed this hash migration will be unable to sign in to
Ubuntu 22 FIPS installations and will need to perform a password reset.
To find for users who have not migrated, use
this Rake task
before upgrading to Ubuntu 22.04.
Check the GitLab secrets JSON: Rails now requires stronger active dispatch salts to
issue cookies. The Linux package uses static values with sufficient length by default on
Ubuntu 22.04. However, you can customize these salts by setting the following keys
in your Linux package configuration:
gitlab_rails
[
'signed_cookie_salt'
]
=
'custom value'
gitlab_rails
[
'authenticated_encrypted_cookie_salt'
]
=
'another custom value'
The values are written to the
gitlab-secrets.json
and must be synchronized across
all Rails nodes.
