# Enable and disable GitLab features deployed behind feature flags | GitLab Docs

Source: https://docs.gitlab.com/administration/feature_flags/

Enable and disable GitLab features deployed behind feature flags | GitLab Docs
Enable and disable GitLab features deployed behind feature flags
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
GitLab adopted feature flags strategies
to deploy features in an early stage of development so that they can be
incrementally rolled out.
Before making them permanently available, features can be deployed behind
flags for a number of reasons, such as:
To test the feature.
To get feedback from users and customers while in an early stage of the development of the feature.
To evaluate users adoption.
To evaluate how it impacts the performance of GitLab.
To build it in smaller pieces throughout releases.
Features behind flags can be gradually rolled out, typically:
The feature starts disabled by default.
The feature becomes enabled by default.
The feature flag is removed.
These features can be enabled and disabled to allow or prevent users from using
them. It can be done by GitLab administrators with access to the
Rails console
or the
Feature flags API
.
When you disable a feature flag, the feature is hidden from users and all of the functionality is turned off.
For example, data is not recorded and services do not run.
If you used a certain feature and identified a bug, a misbehavior, or an
error, it’s very important that you
provide feedback
to GitLab as soon
as possible so we can improve or fix it while behind a flag. When you upgrade
GitLab, the feature flag status may change.
Risks when enabling features still in development
Before enabling a disabled feature flag in a production GitLab environment, it is crucial to understand the potential risks involved.
Data corruption, stability degradation, performance degradation, and security issues may occur if you enable a feature that’s disabled by default.
Features that are disabled by default may change or be removed without notice in a future version of GitLab.
Features behind default-disabled feature flags are not recommended for use in a production environment
and problems caused by using a default disabled features aren’t covered by GitLab Support.
Security issues found in features that are disabled by default are patched in regular releases
and do not follow our regular
maintenance policy
with regards to backporting the fix.
Risks when disabling released features
In most cases, the feature flag code is removed in a future version of GitLab.
If and when that occurs, from that point onward you can’t keep the feature in a disabled state.
How to enable and disable features behind flags
Each feature has its own flag that should be used to enable and disable it.
The documentation of each feature behind a flag includes a section informing
the status of the flag and the command to enable or disable it.
Start the GitLab Rails console
The first thing you must do to enable or disable a feature behind a flag is to
start a session on GitLab Rails console.
For Linux package installations:
sudo gitlab-rails console
For installations from the source:
sudo -u git -H bundle
exec
rails console -e production
For details, see
starting a Rails console session
.
Enable or disable the feature
After the Rails console session has started, run the
Feature.enable
or
Feature.disable
commands accordingly. The specific flag can be found
in the feature’s documentation itself.
To enable a feature, run:
Feature
.
enable
(
:<
feature
flag
>
)
Example, to enable a fictional feature flag named
example_feature
:
Feature
.
enable
(
:example_feature
)
To disable a feature, run:
Feature
.
disable
(
:<
feature
flag
>
)
Example, to disable a fictional feature flag named
example_feature
:
Feature
.
disable
(
:example_feature
)
Some feature flags can be enabled or disabled on a per project basis:
Feature
.
enable
(
:<
feature
flag
>
,
Project
.
find
(
<
project
id
>
))
For example, to enable the
:example_feature
feature flag for project
1234
:
Feature
.
enable
(
:example_feature
,
Project
.
find
(
1234
))
Some feature flags can be enabled or disabled on a per user basis. For example, to enable the
:example_feature
flag for user
sidney_jones
:
Feature
.
enable
(
:example_feature
,
User
.
find_by_username
(
"sidney_jones"
))
Feature.enable
and
Feature.disable
always return
true
, even if the application doesn’t use the flag:
irb
(
main
):
001
:
0
>
Feature
.
enable
(
:example_feature
)
=>
true
When the feature is ready, GitLab removes the feature flag, and the option for
enabling and disabling it no longer exists. The feature becomes available in all instances.
Check if a feature flag is enabled
To check if a flag is enabled or disabled, use
Feature.enabled?
or
Feature.disabled?
.
For example, for a feature flag named
example_feature
that is already enabled:
Feature
.
enabled?
(
:example_feature
)
=>
true
Feature
.
disabled?
(
:example_feature
)
=>
false
When the feature is ready, GitLab removes the feature flag, and the option for
enabling and disabling it no longer exists. The feature becomes available in all instances.
View set feature flags
You can view all GitLab administrator set feature flags:
Feature
.
all
=>
[
#<Flipper::Feature:198220 name="example_feature", state=:on, enabled_gate_names=[:boolean], adapter=:memoizable>]
# Nice output
Feature
.
all
.
map
{
|
f
|
[
f
.
name
,
f
.
state
]
}
Unset feature flag
You can unset a feature flag so that GitLab falls back to the current defaults for that flag:
Feature
.
remove
(
:example_feature
)
=>
true
