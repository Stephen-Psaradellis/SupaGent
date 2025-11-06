# All feature flags in GitLab | GitLab Docs

Source: https://docs.gitlab.com/administration/feature_flags/list/

All feature flags in GitLab | GitLab Docs
All feature flags in GitLab
Tier
: Free, Premium, Ultimate
Offering
: GitLab Self-Managed
GitLab provides feature flags to turn specific features on or off.
This page contains a list of all feature flags provided by GitLab. In GitLab Self-Managed,
GitLab administrators can
change the state of these feature flags
.
For help developing custom feature flags, see
Create a feature flag
.
If you don't see the feature flag tables below, view them at
docs.gitlab.com
.
Available feature flags
The feature flags available to you depend on:
The edition of GitLab:
Community Edition or Enterprise Edition
.
The version of GitLab: For example, 17.8 or 18.0.
The installation of GitLab: GitLab Self-Managed or GitLab.com.
GitLab Community Edition and Enterprise Edition
Number of feature flags available: 405
Name
Group
Milestone
Default state
Rollout issue
admin_groups_vue
group::organizations
18.2
Enabled
#553229
avoid_branch_names_cache
group::source code
18.6
Disabled
#576403
avoid_tag_names_cache
group::source code
18.6
Disabled
#578116
bitbucket_server_user_mapping
group::import and integrate
17.7
Enabled
#509897
cells_unique_claims
group::cells infrastructure
18.6
Disabled
#572819
ci_component_context_interpolation
group::pipeline authoring
18.5
Disabled
#571986
ci_job_token_jwt
group::authorization
17.7
Disabled
#497392
custom_prefix_for_all_token_types
group::authentication
17.10
Disabled
#522940
custom_project_badges
group::organizations
18.5
Enabled
#574344
custom_webhook_template_serialization
group::import
18.4
Disabled
#560952
destroy_fork_network_on_archive
group::source code
18.0
Enabled
#538925
directory_code_dropdown_updates
group::source code
17.9
Enabled
#514750
dpop_authentication
group::authentication
17.9
Disabled
#17713
edit_branch_rules
group::source code
16.11
Enabled
#454501
enforce_language_server_version
group::editor extensions
18.1
Disabled
#541743
enrol_new_users_in_email_otp
group::authentication
18.4
Disabled
#561975
github_user_mapping
group::import and integrate
17.6
Enabled
#499993
glql_es_integration
group::knowledge
17.11
Enabled
#527280
glql_work_items
group::knowledge
17.11
Enabled
#525480
group_agnostic_token_revocation
group::authentication
17.2
Disabled
#463157
import_rescue_query_canceled
group::import and integrate
18.1
Disabled
#545313
import_vulnerabilities
group::import and integrate
17.7
Disabled
#516220
incremental_cache_for_refs
group::source code
18.4
Disabled
#567993
inline_blame
group::source code
17.6
Disabled
#501539
insert_into_p_sent_notifications
group::project management
18.6
Disabled
#568170
merge_widget_stop_polling
group::code review
18.6
Disabled
#579437
mirroring_lfs_optimization
group::source code
18.4
Enabled
#559226
mr_review_batch_submit
group::code review
18.2
Enabled
#551171
new_default_for_auto_stop
group::environments
17.10
Disabled
#523169
no_webhook_rate_limit
group::pipeline execution
18.3
Disabled
Not defined
organization_users_internal
group::authentication
18.1
Disabled
#547109
personal_homepage
group::personal productivity
18.1
Enabled
#561388
post_receive_sync_refresh_cache
group::pipeline execution
17.3
Enabled
#474741
project_studio_early_access
group::engagement
18.6
Disabled
#577848
push_rule_ordered_by_id
group::source code
18.3
Disabled
#559013
rapid_diffs_on_compare_show
group::code review
18.0
Enabled
#539580
read_organization_push_rules
group::source code
18.4
Disabled
#544651
reassignment_throttling
group::import and integrate
17.7
Enabled
#504995
ref_existence_check_gitaly
group::source code
18.4
Disabled
#556727
render_gpg_signed_tags_verification_status
group::source code
18.3
Disabled
#560619
repository_set_cache_logging
group::source code
18.1
Enabled
#549485
required_pipelines
group::compliance
17.4
Disabled
#483550
show_role_details_in_drawer
group::authorization
17.2
Enabled
#468669
token_api_expire_pipeline_triggers
group::pipeline execution
17.10
Disabled
#520713
truncate_ci_commit_message
group::runner core
18.6
Disabled
#576807
unstick_locked_merge_requests_redis
group::code review
17.3
Disabled
#470696
unstick_locked_mrs_without_merge_jid
group::code review
17.3
Disabled
#461560
update_organization_push_rules
group::source code
18.6
Disabled
#569118
user_mapping_direct_reassignment
group::import
18.6
Disabled
#575652
user_mapping_service_account_and_bots
group::import
18.5
Enabled
#573124
user_mapping_to_personal_namespace_owner
group::import
18.3
Disabled
#556557
work_item_view_for_issues
group::project management
17.11
Enabled
#520791
workhorse_circuit_breaker
group::source code
18.0
Disabled
#541105
achievements
group::organizations
15.8
Disabled
#386817
activity_pub
group::source code
16.4
Disabled
#424008
activity_pub_project
group::source code
16.4
Disabled
#424008
approval_group_rules
group::source code
16.7
Disabled
#432248
archive_rate_limit
group::source code
12.9
Disabled
#369432
auto_devops_banner_disabled
group::environments
10.0
Enabled
#350882
board_multi_select
group::product planning
14.0
Disabled
#331189
branch_list_keyset_pagination
group::source code
13.2
Disabled
#369435
build_service_proxy
group::ide
11.11
Disabled
Not defined
bulk_import_deferred_workers
group::import and integrate
16.6
Disabled
#431032
ci_dynamic_pipeline_inputs
group::pipeline authoring
18.6
Disabled
#572854
ci_job_assistant_drawer
Not defined
15.9
Disabled
Not defined
ci_variables_pages
group::pipeline authoring
15.10
Disabled
#392874
cloudseed_aws
group::incubation
15.10
Disabled
#395777
collect_all_diff_paths
group::gitaly
16.4
Disabled
#421460
data_transfer_monitoring
group::source code
15.9
Disabled
#391682
debian_group_packages
group::package registry
14.1
Disabled
#336536
debian_packages
group::package registry
13.5
Disabled
#337288
design_management_allow_dangerous_images
group::product planning
12.4
Disabled
#34279
diff_line_syntax_highlighting
group::source code
13.10
Disabled
#324159
diffs_batch_cache_with_max_age
group::code review
15.9
Disabled
#388778
disable_all_mention
group::project management
16.1
Disabled
#415280
disable_git_http_fetch_writes
group::source code
13.9
Disabled
#883
disable_unsafe_regexp
group::pipeline authoring
14.9
Disabled
Not defined
display_cost_factored_storage_size_on_project_pages
group::utilization
16.6
Disabled
#428743
do_not_run_safety_net_auth_refresh_jobs
group::authorization
15.9
Disabled
#390336
dora_configuration
group::optimize
15.4
Disabled
#372545
enforce_acceptance_of_changed_terms
group::authentication
16.7
Disabled
#430799
epic_relations_for_non_members
group::product planning
16.4
Disabled
#424704
epic_widget_edit_confirmation
group::product planning
15.4
Disabled
#372429
exclude_protected_variables_from_multi_project_pipeline_triggers
group::pipeline authoring
16.6
Disabled
#431266
expired_storage_check
group::utilization
16.1
Disabled
#411919
export_csv_preload_in_batches
group::project management
15.9
Disabled
#389847
force_autodevops_on_by_default
group::environments
11.3
Disabled
Not defined
forti_authenticator
group::authentication
13.5
Disabled
Not defined
forti_token_cloud
group::authentication
13.7
Disabled
Not defined
gitlab_error_tracking
group::observability
15.2
Disabled
#366382
global_time_tracking_report
group::project management
15.11
Disabled
#394715
go_proxy
group::package registry
13.1
Disabled
Not defined
go_proxy_disable_gomod_validation
group::package registry
13.1
Disabled
Not defined
incident_declare_slash_command
group::respond
15.6
Disabled
#378072
incident_timeline_events_from_labels
group::respond
15.3
Disabled
#369416
integrated_error_tracking
group::observability
14.9
Disabled
#353956
invitation_flow_enforcement_setting
group::authorization
15.4
Disabled
#367666
issue_date_filter
group::product planning
16.2
Disabled
#420173
issue_email_participants
group::project management
13.8
Enabled
#350460
k8s_dashboard
group::environments
16.4
Disabled
#424237
last_pipeline_from_pipeline_status
group::pipeline execution
16.0
Disabled
#407789
log_git_streaming_audit_events
group::source code
16.5
Disabled
#415138
main_branch_over_master
group::source code
13.12
Enabled
#329190
maven_central_request_forwarding
group::package registry
15.4
Disabled
#359553
merge_request_cleanup_ref_worker_async
group::gitaly
16.2
Disabled
#421695
merge_request_delete_gitaly_refs_in_batches
group::gitaly
16.3
Disabled
#416969
merge_trains_skip_train
group::pipeline execution
16.4
Enabled
#422111
mr_pipelines_graphql
group::pipeline authoring
16.4
Disabled
#419726
namespace_storage_limit_show_preenforcement_banner
group::utilization
15.2
Disabled
#362340
notifications_todos_buttons
group::ux paper cuts
16.5
Disabled
#426305
npm_allow_packages_in_multiple_projects
group::package registry
15.10
Disabled
#391692
okr_checkin_reminders
group::product planning
16.4
Disabled
#424235
only_positive_pagination_values
group::source code
15.3
Disabled
#369225
page_specific_styles
group::project management
16.5
Disabled
#425035
personal_snippet_reference_filters
group::source code
13.3
Disabled
#235155
pipeline_cleanup_ref_worker_async
group::gitaly
16.1
Disabled
#421696
pipeline_delete_gitaly_refs_in_batches
group::gitaly
16.3
Disabled
#416969
preserve_markdown
group::knowledge
17.3
Disabled
#474407
product_usage_data
group::analytics instrumentation
17.10
Enabled
#515960
prohibited_tag_name_encoding_check
group::source code
16.5
Disabled
#426013
project_templates_without_min_access
group::source code
16.5
Disabled
#425452
registry_data_repair_worker
group::container registry
16.0
Disabled
#397505
reject_unsigned_commits_by_gitlab
group::ide
13.11
Enabled
#326775
remove_monitor_metrics
group::respond
15.11
Enabled
#399248
rollup_timebox_chart
group::project management
15.11
Disabled
#399186
rpm_packages
group::package registry
15.4
Disabled
#371863
rubygem_packages
group::package registry
13.9
Disabled
#299383
scip_code_intelligence
group::code review
18.6
Disabled
Not defined
secret_detection_enable_spp_for_public_projects
group::secret detection
18.1
Disabled
Not defined
secret_detection_partner_token_verification
group::secret detection
18.6
Disabled
#567736
service_desk_ticket
group::project management
16.2
Disabled
#416343
skip_group_share_unlink_auth_refresh
group::organizations
15.2
Disabled
#366086
support_sha256_repositories
group::source code
16.7
Disabled
#431864
timelog_categories
group::project management
15.3
Disabled
#365829
two_factor_for_cli
group::authentication
13.5
Disabled
#443750
use_repository_info_for_repository_size
group::source code
16.1
Disabled
#416490
work_items_alpha
group::project management
17.2
Disabled
#18942
workhorse_archive_cache_disabled
group::source code
10.5
Disabled
#369437
allow_self_hosted_features_for_com
group::custom models
17.5
Disabled
#497994
cached_author_avatar_helper
group::source code
16.10
Disabled
#442216
experimental_group_o11y_settings_access
group::embody
18.4
Disabled
#565658
forbid_composite_identities_to_run_pipelines
group::ci platform
17.11
Disabled
#535715
null_hypothesis
group::acquisition
13.7
Disabled
Not defined
o11y_settings_access
group::embody
18.3
Disabled
Not defined
observability_sass_features
group::platform insights
18.1
Disabled
Not defined
accessible_loading_button
group::design system
18.6
Disabled
#577222
active_context_code_incremental_index_project
group::global search
18.4
Disabled
#561020
active_context_saas_initial_indexing_namespace
group::global search
18.5
Disabled
#569746
allow_group_items_in_project_autocompletion
group::product planning
18.1
Disabled
#543707
allow_guest_plus_roles_to_pull_packages
group::package registry
17.9
Disabled
#512210
allow_immediate_namespaces_deletion
group::organizations
18.5
Disabled
#576726
allow_runner_job_acknowledgement
group::ci platform
18.5
Disabled
#568905
authorize_granular_pats
group::authorization
18.5
Disabled
#570314
authorize_issue_types_in_finder
group::product planning
18.2
Disabled
#548096
auto_spp_public_com_projects
group::secret detection
18.5
Disabled
#574641
cached_state_counts_for_group_issues
group::product planning
18.6
Disabled
#578515
ci_job_created_subscription
group::pipeline execution
18.3
Disabled
#562507
ci_pipeline_creation_requests_realtime
group::pipeline authoring
18.6
Disabled
#576639
ci_require_api_token_for_ci_lint
group::pipeline authoring
18.6
Disabled
#578076
commit_files_target_sha
group::source code
17.10
Disabled
#520058
commit_time_tracking
group::project management
18.3
Disabled
#553942
concurrency_limit_current_limit_from_redis
group::durability
18.2
Disabled
#549836
container_registry_protected_containers_delete
group::container registry
17.11
Disabled
#517986
deduplicate_new_path_value
group::code review
18.4
Disabled
#567834
dependency_proxy_for_containers_ssrf_protection
group::package registry
18.0
Disabled
#523245
diff_line_match
group::source code
17.6
Disabled
#503981
disable_message_attribute_on_mr_diff_commits
group::source code
17.10
Disabled
#520384
early_access_program_toggle
Contributor Success
17.1
Disabled
#465147
encrypted_trigger_token_lookup
group::pipeline execution
18.3
Disabled
#558025
generic_package_registry_ssrf_protection
group::package registry
18.2
Disabled
#547452
gpg_commit_delegate_to_signature
group::source code
18.4
Disabled
#560641
ignore_supported_cwe_list_check
group::security insights
17.8
Disabled
#508174
import_by_url_new_page
group::import
18.4
Disabled
#566389
limit_commit_markdown_preload
group::source code
18.4
Disabled
#567341
load_balancer_low_statement_timeout
group::database
17.4
Disabled
#473429
log_find_with_user_password
group::authentication
18.5
Disabled
#571378
log_large_json_objects
group::import
18.4
Disabled
Not defined
manage_pat_by_group_owners_ready
group::authentication
17.8
Disabled
#511922
markdown_placeholders
group::knowledge
18.2
Disabled
#544860
merge_request_title_regex
group::code review
17.11
Disabled
#508022
merge_requests_diff_commits_limit
group::source code
17.11
Disabled
#527036
merge_requests_diffs_limit
group::source code
17.10
Disabled
#521970
new_ui_dot_com_rollout
group::engagement
18.6
Disabled
#579545
omniauth_step_up_auth_for_admin_mode
group::authentication
17.11
Disabled
#502544
omniauth_step_up_auth_for_namespace
group::authentication
18.4
Disabled
#510951
optimized_commit_storage
group::source code
17.10
Disabled
#520259
organization_scoped_paths
group::organizations
18.3
Disabled
#556359
packages_protected_packages_delete
group::package registry
17.10
Disabled
#516215
paneled_view
group::project management
18.3
Disabled
#574049
policy_violations_es_filter
group::security policies
18.6
Disabled
#577591
project_authorizations_update_in_background_in_transfer_service
group::authorization
18.1
Disabled
#548979
project_deploy_token_expiring_notifications
group::environments
18.3
Disabled
#555470
project_repositories_health
group::gitaly
17.10
Disabled
#521115
rate_limiting_headers_for_unthrottled_requests
group::networking_and_incident_management
18.6
Disabled
#578191
read_audit_events_from_new_tables
group::compliance
17.6
Disabled
#493723
reassignment_throttling_table_check
group::import and integrate
17.11
Disabled
#534613
rebase_on_merge_automatic
group::code review
18.0
Disabled
#524048
rename_post_receive_worker
group::source code
17.9
Disabled
#512125
render_ssh_signed_tags_verification_status
group::source code
18.3
Disabled
#561452
restrict_namespace_api_billing_fields
group::billing and subscription management
18.3
Disabled
Not defined
search_merge_request_queries_notes
group::global search
18.6
Disabled
#573750
ship_mr_quick_action
group::pipeline execution
18.6
Disabled
#513948
sidekiq_concurrency_limit_middleware_v2
group::durability
18.3
Disabled
#565604
single_pipeline_for_resolver
group::pipeline execution
18.1
Disabled
#544930
slsa_provenance_statement
group::pipeline security
18.3
Disabled
#547866
track_api_request_from_runner
group::authorization
18.1
Disabled
#538150
use_max_concurrency_limit_percentage_as_default_limit
group::durability
18.2
Disabled
#553604
use_primary_and_secondary_stores_for_trace_chunks
group::durability
18.2
Disabled
#553057
use_primary_store_as_default_for_trace_chunks
group::durability
18.2
Disabled
#553060
validity_check_es_filter
group::security insights
18.3
Disabled
#560433
work_items_list_es_integration
group::knowledge
18.4
Disabled
#561475
access_rest_chat
group::ai framework
16.5
Disabled
Not defined
active_record_transactions_tracking
group::pipeline execution
14.2
Disabled
#338306
additional_snowplow_tracking
group::analytics instrumentation
11.11
Disabled
Not defined
admin_jobs_filter_runner_type
group::runner
16.4
Disabled
Not defined
ai_duo_code_suggestions_switch
group::ai framework
16.1
Enabled
Not defined
archive_authentication_events
group::authentication
18.5
Disabled
#573714
archive_revoked_access_grants
group::authentication
18.5
Disabled
#574827
archive_revoked_access_tokens
group::authentication
18.5
Disabled
#571771
authenticate_markdown_api
group::knowledge
15.3
Enabled
Not defined
auto_disabling_web_hooks
group::import and integrate
15.10
Disabled
Not defined
automatic_lock_writes_on_partition_tables
group::cells infrastructure
16.5
Enabled
Not defined
automatic_lock_writes_on_table
group::cells infrastructure
15.7
Enabled
Not defined
batched_migrations_health_status_autovacuum
group::database
15.2
Enabled
#360331
batched_migrations_health_status_patroni_apdex
group::database
15.10
Disabled
Not defined
batched_migrations_health_status_wal
group::database
15.2
Disabled
#366855
block_issue_repositioning
group::project management
13.12
Disabled
#329663
cascading_auto_duo_code_review_settings
group::code creation
18.3
Disabled
#561363
certificate_based_clusters
group::environments
14.9
Disabled
#353410
check_path_traversal_middleware
group::package registry
16.5
Enabled
#415460
ci_build_dependencies_artifacts_logger
group::pipeline execution
15.3
Disabled
#369441
ci_enforce_throttle_pipelines_creation_override
group::pipeline authoring
15.1
Disabled
#362513
ci_jwt_groups_direct
group::pipeline security
17.3
Disabled
#474908
ci_minimal_cost_factor_for_gitlab_namespaces
group::pipeline execution
15.2
Disabled
#367692
ci_partitioning_analyze_queries
group::ci platform
15.4
Disabled
#372840
ci_pipeline_age_histogram
group::pipeline execution
15.1
Disabled
Not defined
ci_pipeline_archived_access
group::ci platform
18.2
Disabled
Not defined
ci_pipeline_command_logger_commit
group::pipeline authoring
17.3
Disabled
#474790
ci_pipeline_creation_logger
group::pipeline authoring
14.5
Disabled
#345779
ci_pipeline_creation_step_duration_tracking
group::pipeline authoring
14.2
Disabled
#339486
ci_queueing_disaster_recovery_disable_fair_scheduling
group::pipeline execution
13.12
Disabled
Not defined
ci_queueing_disaster_recovery_disable_quota
group::pipeline execution
13.12
Disabled
Not defined
ci_queuing_disaster_recovery_disable_allowed_plans
group::hosted runners
17.4
Disabled
Not defined
ci_register_job_instrumentation_logger
group::pipeline authoring
17.9
Disabled
#512402
ci_register_job_temporary_lock
group::pipeline execution
13.10
Enabled
#323180
ci_release_cli_catalog_publish_option
group::pipeline authoring
16.11
Disabled
#443782
ci_trace_log_invalid_chunks
group::pipeline execution
13.5
Disabled
Not defined
ci_unlock_pipelines
group::pipeline execution
16.2
Enabled
#415503
ci_unlock_pipelines_extra_low
group::pipeline execution
16.7
Disabled
Not defined
ci_unlock_pipelines_high
group::pipeline execution
16.2
Disabled
#415503
ci_unlock_pipelines_medium
group::pipeline execution
16.2
Disabled
#415503
ci_unsafe_regexp_logger
group::pipeline authoring
14.8
Enabled
Not defined
commit_sha_scope_logger
group::code review
17.10
Disabled
#523367
database_async_foreign_key_validation
group::database
15.9
Disabled
Not defined
database_async_index_creation
group::database
14.2
Disabled
Not defined
database_async_index_operations
group::database
15.9
Disabled
Not defined
database_reindexing
group::database
13.5
Enabled
Not defined
db_health_check_using_mimir_client
group::database
17.1
Disabled
Not defined
db_health_check_wal_rate
group::database
16.3
Disabled
Not defined
detect_cross_database_modification
group::cells infrastructure
14.5
Disabled
Not defined
disable_anonymous_project_search
group::project management
14.3
Disabled
Not defined
disable_cancel_redundant_pipelines_service
group::pipeline execution
16.1
Disabled
Not defined
disable_keep_around_refs
group::gitaly
16.1
Disabled
Not defined
disable_preferred_language_cookie
group::personal productivity
16.10
Disabled
Not defined
disallow_database_ddl_feature_flags
group::database
16.4
Disabled
Not defined
duo_code_review_response_logging
group::code review
18.0
Disabled
#538176
ecomm_instrumentation
group::analytics instrumentation
14.4
Disabled
Not defined
emit_db_transaction_sli_metrics
group::durability
17.0
Disabled
#456667
emit_sidekiq_histogram_metrics
group::durability
16.3
Enabled
#421499
enable_sidekiq_resource_usage_tracking
group::durability
17.6
Disabled
#501502
enable_sidekiq_shard_router
group::durability
16.10
Disabled
#444293
enforce_ci_builds_pagination_limit
group::pipeline execution
16.6
Disabled
#429453
enforce_locked_labels_on_merge
group::project management
16.3
Disabled
Not defined
execute_batched_migrations_on_schedule
group::database
13.11
Enabled
#326241
expanded_ai_logging
group::ai framework
16.7
Disabled
Not defined
export_reduce_relation_batch_size
group::import and integrate
16.10
Disabled
#442465
feature_flag_state_logs
group::incubation
14.6
Disabled
#345888
gitlab_ci_builds_queuing_metrics
group::pipeline execution
13.10
Disabled
#350888
gitlab_experiment
group::acquisition
14.9
Enabled
#353921
glql_load_on_click
group::knowledge
17.9
Disabled
#517914
import_admin_override_max_file_size
group::import
18.2
Disabled
Not defined
incident_fail_over_completion_provider
group::code creation
17.6
Disabled
Not defined
incident_fail_over_generation_provider
group::code creation
17.8
Disabled
#511072
legacy_open_source_license_available
group::organizations
14.8
Enabled
Not defined
load_balancer_double_replication_lag_time
group::database
17.0
Disabled
Not defined
load_balancer_ignore_replication_lag_time
group::database
17.0
Disabled
Not defined
lock_tables_in_monitoring
group::cells infrastructure
16.4
Enabled
Not defined
log_large_in_list_queries
group::database
16.9
Disabled
#17359
loose_foreign_key_worker_feature_category_override
group::database frameworks
18.6
Disabled
#578006
loose_foreign_keys_turbo_mode_ci
group::database frameworks
16.4
Disabled
Not defined
loose_foreign_keys_turbo_mode_main
group::database frameworks
16.4
Disabled
Not defined
loose_foreign_keys_turbo_mode_sec
group::security infrastructure
17.7
Disabled
Not defined
mask_page_urls
group::analytics instrumentation
14.3
Disabled
#340181
monitor_database_locked_tables
group::cells infrastructure
16.1
Enabled
Not defined
omit_aggregated_db_log_fields
group::durability
17.6
Disabled
#501156
ops_prune_old_events
group::organizations
15.10
Enabled
Not defined
override_bulk_import_disabled
group::import and integrate
16.5
Disabled
Not defined
partition_manager_sync_partitions
group::database
16.0
Enabled
#410997
performance_bar_stats
group::product planning
13.7
Disabled
#285480
projects_build_artifacts_size_refresh
group::pipeline execution
15.1
Enabled
Not defined
projects_build_artifacts_size_refresh_high
group::pipeline execution
15.8
Disabled
Not defined
projects_build_artifacts_size_refresh_medium
group::pipeline execution
15.8
Disabled
Not defined
prometheus_notify_max_alerts
group::respond
14.7
Disabled
#6086
query_analyzer_gitlab_schema_metrics
group::database frameworks
14.5
Disabled
Not defined
rapid_diffs_debug
group::code review
18.2
Disabled
#542953
redis_hll_tracking
group::analytics instrumentation
13.11
Enabled
Not defined
remote_mirror_no_delay
group::durability
15.2
Disabled
Not defined
remove_file_commit_history_following
group::gitaly
16.10
Disabled
#441312
report_heap_dumps
group::durability
15.7
Disabled
#385175
report_jemalloc_stats
group::durability
15.2
Disabled
#367845
require_login_for_commit_tree
group::source code
18.5
Disabled
#572011
reset_column_information_on_statement_invalid
group::database frameworks
16.1
Enabled
Not defined
runner_migrations_backoff
group::pipeline execution
16.0
Disabled
Not defined
s3_multithreaded_uploads
group::pipeline execution
13.8
Enabled
#296772
sample_pg_stat_activity
group::durability
17.6
Disabled
#503486
secure_files_p12_parser
group::mobile devops
17.0
Enabled
#458736
show_gitlab_agent_feedback
group::environments
14.8
Enabled
Not defined
show_terraform_banner
group::environments
14.4
Enabled
Not defined
sidekiq_concurrency_limit_middleware
group::durability
16.9
Enabled
#435391
skip_require_email_verification
group::test governance
15.9
Disabled
#389235
split_log_bulk_increment_counter
group::pipeline execution
15.9
Disabled
Not defined
track_organization_fallback
group::organizations
17.6
Disabled
Not defined
track_struct_event_logger
group::acquisition
18.4
Disabled
#563347
usage_data_non_sql_metrics
group::analytics instrumentation
13.11
Disabled
Not defined
usage_data_queries_api
group::analytics instrumentation
13.11
Disabled
Not defined
web_hook_event_resend_api_endpoint_rate_limit
group::import and integrate
17.4
Enabled
Not defined
web_hook_test_api_endpoint_rate_limit
group::import and integrate
17.0
Enabled
Not defined
x509_forced_cert_loading
group::source code
13.10
Disabled
#506033
gitaly_enforce_requests_limits
group::gitaly
Not defined
Disabled
Not defined
gitaly_go_user_merge_branch
group::gitaly
Not defined
Disabled
Not defined
gitaly_mep_mep
group::gitaly
Not defined
Disabled
Not defined
gitaly_revlist_for_repo_size
group::gitaly
Not defined
Disabled
Not defined
gitaly_upload_pack_gitaly_hooks
group::gitaly
13.9
Disabled
#807
gitaly_user_merge_branch_access_error
group::gitaly
14.3
Disabled
#3757
kas_k8s_api_proxy_response_header_allowlist
group::environments
18.3
Disabled
#560088
allow_iframes_in_markdown
group::knowledge
18.5
Disabled
Not defined
archive_group
group::organizations
17.11
Disabled
#526771
autoflow_enabled
group::environments
17.3
Disabled
Not defined
autoflow_issue_events_enabled
group::environments
17.10
Disabled
#516169
autoflow_merge_request_events_enabled
group::environments
17.10
Disabled
#516168
blob_edit_refactor
group::source code
18.5
Disabled
Not defined
buffered_token_expiration_limit
group::authentication
17.6
Disabled
#490989
check_for_mailmapped_commit_emails
group::source code
17.5
Disabled
#481441
ci_pipeline_statuses_updated_subscription
group::pipeline execution
18.6
Disabled
#578884
ci_skip_locked_pipelines
group::ci platform
18.3
Disabled
Not defined
ci_skip_old_protected_pipelines
group::ci platform
18.0
Disabled
Not defined
cleanup_data_source_work_item_data
group::project management
17.7
Disabled
Not defined
contributions_analytics_dashboard
group::platform insights
17.9
Disabled
#516180
current_organization_policy
group::organizations
18.4
Disabled
#559251
early_access_program
Contributor Success
17.0
Disabled
Not defined
edit_user_profile_vue
group::organizations
16.1
Disabled
#414552
email_based_mfa
group::authentication
18.4
Disabled
Not defined
existing_jira_issue_attachment_from_vulnerability_bulk_action
group::security insights
17.9
Disabled
#518038
explore_topics_cleaned_path
group::organizations
16.1
Disabled
#414892
find_and_replace
group::knowledge
17.6
Disabled
#504599
fine_grained_personal_access_tokens
group::authorization
18.6
Disabled
Not defined
glql_aggregation
group::platform insights
18.3
Disabled
#560582
glql_typescript
group::knowledge
18.4
Disabled
#562608
group_import_history_visibility
group::import and integrate
18.0
Disabled
Not defined
hide_error_tracking_features
group::platform insights
18.3
Disabled
#554555
hide_incident_management_features
group::platform insights
18.1
Disabled
#539351
historical_add_on_assigned_users_enabled
group::optimize
18.4
Disabled
Not defined
k8s_tree_view
group::environments
17.1
Disabled
#463616
labels_archive
group::project management
18.3
Disabled
#556700
log_merge_request_after_create_duration
group::code review
18.6
Disabled
#579080
log_refresh_service_duration
group::code review
18.6
Disabled
#576798
merge_request_diff_commits_dedup
group::code review
18.3
Disabled
#527239
merge_request_diff_commits_partition
group::code review
18.5
Disabled
#528421
merge_requests_merge_data_dual_write
group::code review
18.6
Disabled
#577053
mr_reports_tab
group::code review
17.4
Disabled
Not defined
new_project_creation_form
group::import and integrate
17.9
Disabled
Not defined
new_security_dashboard_total_risk_score
group::security insights
18.4
Disabled
#563079
oauth_dynamic_client_registration
group::api
18.3
Disabled
#555942
observability_features
group::platform insights
17.3
Disabled
#472815
offline_transfer_exports
group::import
18.6
Disabled
#577715
opt_out_organizations
group::organizations
18.4
Disabled
#562264
optional_personal_namespace
group::organizations
16.8
Disabled
#431978
organization_switching
group::organizations
16.11
Disabled
#454890
package_registry_cargo_support
group::package registry
17.11
Disabled
#525330
passkeys
group::authentication
18.5
Disabled
#564495
pipelines_page_graphql
group::pipeline execution
18.5
Disabled
#572262
profile_tabs_vue
group::organizations
15.9
Disabled
#388708
project_commits_refactor
group::source code
18.1
Disabled
#545170
rapid_diffs_on_commit_show
group::code review
18.0
Disabled
#539577
rapid_diffs_on_mr_show
group::code review
18.0
Disabled
#539581
repository_file_tree_browser
group::source code
18.0
Disabled
#537970
runner_create_wizard_admin
group::runner
17.11
Disabled
#533827
show_child_security_reports_in_mr_widget
group::security insights
18.3
Disabled
Not defined
show_merge_request_status_draft
group::code review
18.2
Disabled
#550387
split_refresh_approval_worker
group::code review
18.5
Disabled
#576277
split_refresh_worker_pipeline
group::code review
18.5
Disabled
#570746
split_refresh_worker_web_hooks
group::code review
18.4
Disabled
#569485
ui_for_organizations
group::organizations
16.1
Disabled
#414592
use_namespace_id_for_issue_and_work_item_finders
group::product planning
18.0
Disabled
Not defined
use_namespace_traversal_ids_for_work_items_finder
group::product planning
18.6
Disabled
#577261
v2_approval_rules
group::source code
17.11
Disabled
#533478
verify_mastodon_user
group::authentication
17.4
Disabled
Not defined
vue_project_runners_settings
group::runner
17.11
Disabled
#527130
work_item_planning_view
group::product planning
17.10
Disabled
#520452
work_item_scope_frontend
group::global search
17.6
Disabled
#500062
work_item_tasks_on_boards
group::project management
18.6
Disabled
#577427
work_items_client_side_boards
group::product planning
17.10
Disabled
Not defined
work_items_consolidated_list_user
group::product planning
18.6
Disabled
#578857
sidekiq_throttling_middleware
group::durability
18.2
Disabled
#554621
suspend_click_house_data_ingestion
group::optimize
17.0
Disabled
Not defined
GitLab Enterprise Edition only
Number of feature flags available: 246
Name
Group
Milestone
Default state
Rollout issue
advanced_context_resolver
group::editor extensions
17.1
Enabled
#464767
advanced_vulnerability_management
group::security infrastructure
18.0
Enabled
#537673
agent_platform_claude_code
group::ai framework
18.4
Disabled
#563856
ai_catalog_item_project_curation
group::workflow catalog
18.5
Disabled
#579503
ai_catalog_third_party_flows
group::workflow catalog
18.5
Disabled
#578074
ai_duo_agent_fix_pipeline_button
group::agent foundations
18.4
Enabled
#567988
ai_flow_triggers
group::duo workflow
18.3
Enabled
#560138
ai_model_switching
group::custom models
18.1
Disabled
#526307
ai_prompts_v2
group::ai framework
18.2
Disabled
#552131
ai_user_default_duo_namespace
group::custom models
18.3
Disabled
#560319
allow_merge_train_retry_merge
group::pipeline execution
18.6
Disabled
Not defined
analyzer_status_update_worker_lock
group::security platform management
18.2
Enabled
#555173
assign_custom_roles_to_group_links_saas
group::authorization
17.4
Disabled
#471999
assign_custom_roles_to_group_links_sm
group::authorization
17.4
Enabled
#471999
check_inherited_groups_for_codeowners
group::source code
18.5
Enabled
#566627
collect_scheduled_security_policy_not_enforced_audit_events
group::security policies
18.4
Disabled
#562207
comment_temperature
group::ai framework
17.7
Disabled
#508305
configure_web_based_commit_signing
group::source code
18.3
Disabled
#542975
custom_ability_admin_security_attributes
group::security platform management
18.2
Disabled
Not defined
custom_ability_admin_security_testing
group::security platform management
17.9
Disabled
#513510
custom_ability_read_security_attribute
group::security platform management
18.6
Disabled
Not defined
custom_admin_roles
group::authorization
17.9
Enabled
#548639
cvs_for_container_scanning
group::composition analysis
17.4
Disabled
#483636
dependency_graph_graphql
group::security infrastructure
17.10
Enabled
#521318
dependency_paths
group::security insights
17.10
Enabled
#520269
dora_metrics_dashboard
group::optimize
17.10
Enabled
#542910
duo_agentic_chat
group::duo chat
18.0
Enabled
#542441
duo_agentic_chat_openai_gpt_5
group::ai framework
18.3
Disabled
#560561
duo_code_review_on_agent_platform
group::code creation
18.5
Disabled
#570797
duo_developer_button
group::agent foundations
18.6
Disabled
#579076
duo_include_context_repository
group::code creation
18.0
Disabled
#540543
duo_include_context_terminal
group::editor extensions
17.10
Disabled
#524788
duo_use_billing_endpoint
group::ai framework
18.6
Disabled
Not defined
duo_workflow
group::duo workflow
17.2
Enabled
#468627
duo_workflow_in_ci
group::duo workflow
17.9
Enabled
Not defined
edit_service_account_email
group::authentication
18.3
Enabled
Not defined
enable_vulnerability_fp_detection
group::compliance
18.5
Disabled
#576096
finding_create_jira_issue_mutation
group::security insights
18.4
Enabled
#577296
geo_proxy_fetch_ssh_to_primary
group::source code
17.1
Disabled
#466045
geo_proxy_push_ssh_to_primary
group::source code
17.2
Disabled
#466057
group_owner_placeholder_confirmation_bypass
group::import
18.1
Disabled
#548946
group_settings_based_update_worker
group::security platform management
18.2
Enabled
#553607
hide_suggested_reviewers
group::code review
17.7
Disabled
#505999
instance_level_model_selection
group::custom models
18.4
Enabled
#565710
maven_virtual_registry
group::package registry
18.1
Enabled
#542415
members_permissions_detailed_export
group::authorization
17.4
Disabled
#467359
merged_results_pipeline_ignore_target_branch_race
group::pipeline execution
18.5
Enabled
#470550
prevent_blocking_non_deployment_jobs
group::environments
17.4
Disabled
#477606
product_analytics_admin_settings
group::platform insights
17.5
Disabled
#494428
product_analytics_features
group::platform insights
17.5
Disabled
#494701
project_security_dashboard_new
group::security insights
18.3
Disabled
Not defined
project_work_item_epics
group::product planning
17.10
Disabled
#516901
read_and_write_group_push_rules
group::source code
18.5
Disabled
#571517
related_epic_links_from_work_items
group::product planning
17.10
Disabled
#516212
scheduled_pipeline_execution_policies
group::security policies
17.9
Enabled
#513337
search_work_items_hybrid_search
group::global search
17.6
Disabled
#499450
secret_detection_validity_checks_refresh_token
group::secret detection
18.2
Disabled
#552306
security_categories_and_attributes
group::security platform management
18.4
Disabled
Not defined
security_context_labels
group::security platform management
18.2
Disabled
#551226
security_inventory_filtering
group::security platform management
18.5
Enabled
#552224
security_policies_combined_list
group::security policies
18.4
Enabled
#552189
security_policies_split_view
group::security policies
17.8
Enabled
#450705
smartcard_ad_formats_v2
group::authentication
18.6
Enabled
#577375
stream_audit_events_from_new_tables
group::compliance
17.9
Disabled
#516895
ui_for_virtual_registries
group::package registry
18.5
Enabled
#525934
ui_for_virtual_registry_cleanup_policy
group::package registry
18.6
Disabled
#578060
use_claude_code_completion
group::code creation
17.10
Disabled
#524897
use_consolidated_audit_event_stream_dest_api
group::compliance
17.10
Enabled
#523880
use_duo_context_exclusion
group::code creation
18.2
Enabled
#548612
use_gemini_2_5_flash_in_code_generation
group::code creation
18.2
Disabled
#550215
use_web_based_commit_signing_enabled
group::source code
18.1
Disabled
#542975
validity_checks_security_finding_status
group::secret detection
18.3
Disabled
#560711
vulnerability_archival
group::security infrastructure
17.10
Disabled
Not defined
vulnerability_partial_scans
group::security insights
18.2
Enabled
#552051
zoekt_traversal_id_queries
group::global search
18.3
Enabled
#551855
add_ai_summary_for_new_mr
group::code creation
16.9
Enabled
#17533
agent_registry
group::mlops
16.8
Disabled
#437540
agent_registry_nav
group::mlops
16.10
Disabled
#441966
ai_user_model_switching
group::custom models
18.4
Disabled
#568855
dast_pre_scan_verification
group::dynamic analysis
15.5
Disabled
#376711
duo_agent_platform_model_selection
group::custom models
18.4
Disabled
#568112
enable_hamilton_in_user_preferences
group::provision
16.3
Disabled
#419821
free_user_cap_without_storage_check
group::utilization
16.0
Disabled
#410372
geo_object_storage_verification
group::geo
16.4
Enabled
#410387
group_managed_accounts
group::authentication
11.9
Disabled
Not defined
inherited_push_rule_for_project
group::source code
Not defined
Disabled
#385375
lazy_aggregate_epic_health_statuses
group::product planning
15.6
Disabled
#382242
namespace_storage_limit
group::utilization
Not defined
Disabled
#362340
okr_automatic_rollups
group::product planning
15.8
Disabled
#388368
okrs_mvc
group::product planning
15.6
Disabled
#382070
product_analytics_billing
group::product analytics
16.9
Enabled
#438399
project_quality_summary_page
group::pipeline execution
14.4
Disabled
#343687
saas_user_caps_auto_approve_pending_users_on_cap_increase
group::utilization
14.6
Disabled
#346156
secret_detection_sdrs_token_verification_flow
group::secret detection
18.3
Disabled
#551358
self_hosted_agent_platform
group::custom models
18.3
Disabled
#556185
show_overage_on_role_promotion
group::subscription management
15.7
Disabled
#385496
summarize_my_code_review
group::code creation
16.0
Enabled
#408869
allow_with_code_embeddings_indexed_projects_filter
group::code creation
18.2
Disabled
#553819
code_snippet_search_graphqlapi
group::code creation
18.4
Disabled
#568359
default_pinned_nav_items
group::activation
18.4
Disabled
#560908
legacy_onboarding
group::activation
18.5
Disabled
#573753
lightweight_trial_registration_redesign
group::acquisition
18.1
Disabled
#543761
premium_message_during_trial
group::acquisition
18.6
Disabled
#576856
premium_trial_positioning
group::acquisition
18.5
Disabled
#570711
user_billing_pricing_information
group::acquisition
18.3
Disabled
#560770
with_duo_eligible_projects_filter
group::code creation
18.6
Disabled
#578113
active_context_code_index_project
group::code creation
18.3
Disabled
#556108
ai_dap_use_headless_node_executor
group::agent foundations
18.6
Disabled
#579500
ai_flow_triggers_use_composite_identity
group::agent foundations
18.5
Disabled
#576880
allow_service_account_creation_on_trial
group::authentication
18.6
Disabled
#577286
analyzer_namespace_status_query_optimization
group::security platform management
18.6
Disabled
#578718
approval_policies_enforce_target_scans
group::security policies
18.6
Disabled
#577681
cache_user_project_member_roles
group::authorization
18.5
Disabled
#572176
disable_audit_event_streaming
group::compliance
18.0
Disabled
#536591
duo_agent_platform_enable_direct_http
group::agent foundations
18.4
Disabled
#569655
duo_agent_platform_widget_gitlab_com
group::activation
18.4
Disabled
#568138
duo_include_context_dependency
group::duo chat
17.7
Disabled
#508760
duo_include_context_issue
group::duo chat
17.7
Disabled
#508759
duo_include_context_local_git
group::duo chat
17.7
Disabled
#508761
duo_include_context_merge_request
group::duo chat
17.7
Disabled
#508757
duo_vulnerability_resolution_use_files_multiservice
group::security insights
18.4
Disabled
#545668
duo_workflow_cloud_connector_url
group::duo workflow
18.3
Disabled
#559199
duo_workflow_compress_checkpoint
group::agent foundations
18.6
Disabled
#577674
duo_workflow_stream_during_tool_call_generation
group::agent foundations
18.5
Disabled
#573016
duo_workflow_use_composite_identity
group::duo workflow
18.3
Disabled
#554199
elastic_group_archived_event
group::global search
18.6
Disabled
#578810
enterprise_disable_ssh_keys
group::authentication
18.6
Disabled
#572256
foundational_duo_planner
group::product planning
18.6
Disabled
#579375
foundational_security_agent
group::product planning
18.6
Disabled
#579377
global_ai_catalog
group::workflow catalog
18.2
Disabled
#549914
group_vulnerability_risk_scores_by_project
group::security infrastructure
18.6
Disabled
#579438
id_check_for_oss
Contributor Success
18.2
Disabled
#553337
ingest_sec_reports_when_sec_jobs_completed
group::security infrastructure
18.3
Disabled
#554222
limit_number_of_vulnerabilities_per_project
group::security infrastructure
17.5
Disabled
#483066
mcp_client
group::agent foundations
18.5
Disabled
#572340
pipeline_security_ai_vr
group::security insights
18.2
Disabled
#548930
preload_member_roles
group::authorization
17.9
Disabled
#512871
secret_detection_transition_to_raw_info_gitaly_endpoint
group::secret detection
18.3
Disabled
#558983
security_policy_bot_cleanup_cron_worker
group::security policies
18.2
Disabled
Not defined
security_policy_sync_propagation_tracking
group::security policies
18.4
Disabled
#561007
show_private_groups_as_approvers
group::source code
16.11
Disabled
#454590
stop_welcome_redirection
group::acquisition
17.10
Disabled
#523927
sync_mr_approvals_on_vulnerability_dismiss
group::security policies
18.6
Disabled
Not defined
targeted_messages_admin_ui
group::acquisition
17.10
Disabled
#528820
turn_off_vulnerability_read_create_db_trigger_function
group::security infrastructure
18.3
Disabled
#553939
use_secret_detection_service
group::secret detection
17.7
Disabled
#501441
use_user_group_member_roles_members_page
group::authorization
18.5
Disabled
#576194
virtual_registry_cleanup_policies
group::package registry
18.6
Disabled
#572839
zoekt_debug_delete_repo_logging
group::global search
18.2
Disabled
#553831
zoekt_load_balancer
group::global search
18.4
Disabled
#569789
ai_global_switch
group::ai framework
16.6
Disabled
Not defined
code_completion_opt_out_fireworks
group::code creation
17.11
Disabled
#527111
disable_zoekt_search_for_saas
group::global search
17.1
Disabled
Not defined
duo_evaluation_ready
group::ai model validation
17.6
Disabled
#504575
duo_workflow_extended_logging
group::ai framework
17.5
Disabled
#496323
elasticsearch_work_item_embedding
group::global search
17.6
Disabled
#499449
geo_ci_secure_file_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_ci_secure_file_replication
group::geo
15.2
Enabled
Not defined
geo_container_repository_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_container_repository_replication
group::geo
15.5
Enabled
#366662
geo_dependency_proxy_blob_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_dependency_proxy_blob_replication
group::geo
15.6
Enabled
#375151
geo_dependency_proxy_manifest_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_dependency_proxy_manifest_replication
group::geo
15.6
Enabled
#382225
geo_design_management_repository_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_design_management_repository_replication
group::geo
16.1
Enabled
#411846
geo_group_wiki_repository_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_group_wiki_repository_replication
group::geo
13.10
Enabled
Not defined
geo_job_artifact_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_job_artifact_replication
group::geo
14.8
Enabled
#353995
geo_lfs_object_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_lfs_object_replication
group::geo
13.11
Enabled
#329697
geo_merge_request_diff_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_merge_request_diff_replication
group::geo
13.4
Enabled
#247100
geo_metrics_update_worker
group::geo
17.6
Enabled
Not defined
geo_package_file_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_package_file_replication
group::geo
13.3
Enabled
Not defined
geo_packages_nuget_symbol_force_primary_checksumming
group::geo
18.6
Disabled
#575449
geo_packages_nuget_symbol_replication
group::geo
18.6
Disabled
#565859
geo_pages_deployment_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_pages_deployment_replication
group::geo
14.3
Enabled
#337676
geo_pipeline_artifact_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_pipeline_artifact_replication
group::geo
13.11
Enabled
#326228
geo_project_repository_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_project_repository_replication
group::geo
16.2
Enabled
#367926
geo_project_repository_replication_v2
group::geo
18.6
Disabled
#549772
geo_project_wiki_repository_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_project_wiki_repository_replication
group::geo
15.11
Enabled
#395807
geo_secondary_proxy_separate_urls
group::geo
14.6
Enabled
#325732
geo_snippet_repository_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_snippet_repository_replication
group::geo
13.4
Enabled
#224168
geo_terraform_state_version_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_terraform_state_version_replication
group::geo
13.5
Enabled
#254622
geo_upload_force_primary_checksumming
group::geo
17.2
Enabled
Not defined
geo_upload_replication
group::geo
14.4
Enabled
#340617
hide_vulnerability_severity_override
group::security platform management
18.1
Disabled
Not defined
org_mover_extend_selective_sync_to_primary_checksumming
group::geo
17.7
Disabled
Not defined
parallel_push_checks
group::source code
13.6
Disabled
#506027
refresh_billings_seats
group::subscription management
14.2
Disabled
Not defined
sm_duo_seat_assignment_email
group::activation
18.4
Enabled
Not defined
track_semver_dialect_errors_for_cvs_in_sentry
group::composition analysis
17.5
Disabled
Not defined
zoekt_cross_namespace_search
group::global search
16.11
Disabled
Not defined
zoekt_rollout_worker
group::global search
17.9
Enabled
#519660
zoekt_search_meta_project_ids
group::global search
18.3
Disabled
#557723
activate_nonbillable_users_over_instance_user_cap
group::utilization
16.9
Disabled
#439520
agentic_sast_vr_ui
group::compliance
18.5
Disabled
Not defined
ai_catalog_enforce_readonly_versions
group::workflow catalog
18.3
Disabled
Not defined
ai_catalog_flows
group::workflow catalog
18.4
Disabled
#569060
ai_experiment_sast_fp_detection
group::ai framework
18.5
Disabled
Not defined
ai_self_hosted_vendored_features
group::custom models
18.3
Disabled
Not defined
allow_personal_snippets_setting
group::source code
18.5
Disabled
Not defined
analyze_data_explorer
group::optimize
18.5
Disabled
Not defined
assign_custom_roles_to_project_links_saas
group::authorization
17.7
Disabled
#505998
branch_rules_merge_request_approval_settings
group::source code
17.10
Disabled
#520671
bso_minimal_access_fallback
group::seat management
18.4
Disabled
Not defined
compliance_violation_comments_ui
group::compliance
18.6
Disabled
Not defined
container_virtual_registries
group::container registry
18.4
Disabled
#564803
custom_ability_manage_protected_tags
group::authorization
17.9
Disabled
#514379
dependencies_page_filter_by_package_manager
group::security insights
17.10
Disabled
#517271
dependency_scanning_sbom_scan_api
group::composition analysis
18.4
Disabled
Not defined
duo_ui_next
group::ai framework
18.5
Disabled
Not defined
duo_usage_dashboard
group::optimize
18.2
Disabled
Not defined
extract_admin_roles_from_member_roles
group::authorization
17.11
Disabled
#534584
fetch_contributions_data_from_new_tables
group::optimize
18.0
Disabled
Not defined
geo_postgresql_replication_agnostic
group::geo
17.5
Disabled
Not defined
geo_primary_verification_view
group::geo
18.3
Disabled
#537681
geo_selective_sync_by_organizations
group::geo
18.4
Disabled
Not defined
group_dependencies_graphql
group::security insights
18.0
Disabled
Not defined
group_secrets_manager
group::pipeline security
18.6
Disabled
#578534
group_security_dashboard_new
group::security insights
18.1
Disabled
Not defined
knowledge_graph_indexing
group::code creation
18.1
Disabled
#547433
mr_description_composer
group::code review
17.10
Disabled
Not defined
notify_all_seats_used
group::seat management
18.4
Disabled
Not defined
packages_dependency_proxy_npm
group::package registry
16.11
Disabled
Not defined
product_analytics_billing_override
group::product analytics
16.11
Disabled
#438399
repository_lock_information
group::source code
18.0
Disabled
Not defined
secrets_manager
group::pipeline security
17.3
Disabled
#474432
security_policies_kev_filter
group::security policies
18.6
Disabled
#576858
security_policy_approval_warn_mode
group::security policies
17.8
Disabled
#505352
security_scan_error_rate
group::security insights
17.9
Disabled
Not defined
usage_billing_dev
group::utilization
18.4
Disabled
#566581
use_ai_events_namespace_path_filter
group::optimize
18.2
Disabled
Not defined
validity_checks
group::secret detection
17.11
Disabled
#531222
vsa_stage_time_scatter_chart
group::optimize
18.1
Disabled
Not defined
vulnerabilities_across_contexts
group::security insights
18.6
Disabled
#578047
work_item_status_on_dashboard
group::project management
18.5
Disabled
#575108
Number of flags per development group
Count of feature flags introduced or maintained by each engineering group:
Group
Count
Enabled
Disabled
Contributor Success
3
0
3
Not defined
1
0
1
group::acquisition
9
1
8
group::activation
4
1
3
group::agent foundations
8
1
7
group::ai framework
12
1
11
group::ai model validation
1
0
1
group::analytics instrumentation
7
2
5
group::api
1
0
1
group::authentication
25
2
23
group::authorization
18
3
15
group::billing and subscription management
1
0
1
group::cells infrastructure
6
4
2
group::ci platform
6
0
6
group::code creation
16
3
13
group::code review
27
2
25
group::compliance
8
1
7
group::composition analysis
3
0
3
group::container registry
3
0
3
group::custom models
8
1
7
group::database
16
4
12
group::database frameworks
5
1
4
group::design system
1
0
1
group::duo chat
5
1
4
group::duo workflow
5
3
2
group::durability
16
2
14
group::dynamic analysis
1
0
1
group::editor extensions
3
1
2
group::embody
2
0
2
group::engagement
2
0
2
group::environments
14
3
11
group::geo
44
37
7
group::gitaly
14
0
14
group::global search
14
2
12
group::hosted runners
1
0
1
group::ide
2
1
1
group::import
9
1
8
group::import and integrate
14
5
9
group::incubation
2
0
2
group::knowledge
10
3
7
group::mlops
2
0
2
group::mobile devops
1
1
0
group::networking_and_incident_management
1
0
1
group::observability
2
0
2
group::optimize
9
1
8
group::organizations
18
4
14
group::package registry
19
3
16
group::personal productivity
2
1
1
group::pipeline authoring
15
1
14
group::pipeline execution
35
7
28
group::pipeline security
4
0
4
group::platform insights
8
0
8
group::product analytics
2
1
1
group::product planning
22
0
22
group::project management
20
2
18
group::provision
1
0
1
group::respond
4
1
3
group::runner
3
0
3
group::runner core
1
0
1
group::seat management
2
0
2
group::secret detection
9
0
9
group::security infrastructure
8
2
6
group::security insights
16
3
13
group::security platform management
10
3
7
group::security policies
11
3
8
group::source code
62
7
55
group::subscription management
2
0
2
group::test governance
1
0
1
group::utilization
8
0
8
group::ux paper cuts
1
0
1
group::workflow catalog
5
0
5
Number of flags per milestone
Count of feature flags introduced in each milestone:
Milestone
Count
Enabled
Disabled
10.0
1
1
0
10.5
1
0
1
11.11
2
0
2
11.3
1
0
1
11.9
1
0
1
12.4
1
0
1
12.9
1
0
1
13.1
2
0
2
13.10
5
2
3
13.11
7
5
2
13.12
4
1
3
13.2
1
0
1
13.3
2
1
1
13.4
2
2
0
13.5
6
2
4
13.6
1
0
1
13.7
3
0
3
13.8
2
2
0
13.9
3
0
3
14.0
1
0
1
14.1
1
0
1
14.2
4
0
4
14.3
4
1
3
14.4
4
2
2
14.5
3
0
3
14.6
3
1
2
14.7
1
0
1
14.8
4
4
0
14.9
4
1
3
15.1
3
1
2
15.10
6
1
5
15.11
4
2
2
15.2
9
2
7
15.3
5
1
4
15.4
6
0
6
15.5
2
1
1
15.6
5
2
3
15.7
3
1
2
15.8
4
0
4
15.9
10
0
10
16.0
6
2
4
16.1
13
4
9
16.10
6
0
6
16.11
7
1
6
16.2
7
2
5
16.3
6
1
5
16.4
14
3
11
16.5
9
2
7
16.6
5
0
5
16.7
5
0
5
16.8
2
0
2
16.9
5
3
2
17.0
7
2
5
17.1
6
1
5
17.10
29
5
24
17.11
17
3
14
17.2
22
19
3
17.3
9
1
8
17.4
11
2
9
17.5
8
0
8
17.6
16
2
14
17.7
15
2
13
17.8
5
1
4
17.9
18
5
13
18.0
19
4
15
18.1
22
3
19
18.2
31
6
25
18.3
46
3
43
18.4
47
6
41
18.5
42
6
36
18.6
58
1
57
Not defined
6
0
6
