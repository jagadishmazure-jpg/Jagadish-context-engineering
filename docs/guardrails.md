# Guardrails and security controls

| risk | control | where | test |
| --- | --- | --- | --- |
| Instructions hidden in tool output | system prompt frames tool text as data; pruning drops non-fact text | `strategies.py` | `test_tool_text_framed_as_data_in_system_prompt`, `test_prune_drops_filler_keeps_facts_and_goal_mentions` |
| Path traversal through scratch names | slug-only names, resolved path must stay in root | `offload.py` | `test_unsafe_names_rejected` |
| Scratch leftovers | owned temp dir removed on close | `offload.py` | `test_owned_scratch_cleaned_up` |
| PII in logs or errors | `MaskingFilter` masks message, args and exception text; errors never echo input | `pii.py` | `test_logger_masks_args_and_exceptions`, `test_scratch_error_does_not_echo_input` |
| Runaway reflection cost | hard retry cap, cost check under 10% | `critic.py`, `bench.py` | `test_retries_bounded`, `test_critic_cost_check_under_ten_percent` |
| Agents drifting apart | versioned deltas, refuse on gap, full resync | `deltas.py` | `test_peer_rejects_version_gap`, `test_lost_deltas_trigger_resync_and_recover` |
| Context overflow | allocator never exceeds window minus output reserve | `budget.py` | `test_never_exceeds_usable_window` |
| Leaked secrets / real brands | gitleaks full history, hashed brand blocklist | CI | `test_brand_check_passes_on_repo` |
