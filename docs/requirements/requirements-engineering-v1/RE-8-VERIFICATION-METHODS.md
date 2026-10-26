# RE-8 — Verification methods

[Package index](index.md) · [Review state](review-state.md)

How each requirement is checked. **Test** = automated test in `tests/`;
**Manual** = `docs/arcade-smoke-checklist.md`; **Inspection** = reading code
or config. "Planned" means no check exists yet. No test was run to produce
this table; it maps existing tests by name.

| Requirement | Method | Where |
| --- | --- | --- |
| REQ-001 – REQ-006 | Test | `test_snake_engine.py`, `test_snake_engine_gameplay.py`, `test_engine_transitions.py`, `test_direction.py`, `test_game_config.py` |
| REQ-007 – REQ-011 | Test + Manual | `test_game_session.py`; key mapping only Manual (G-16) |
| REQ-012 | Test + Manual | `test_bot_mode_contract.py`, `test_bot_mode_headless.py`; Play buttons Manual |
| REQ-013 | Test | `test_bot_mode_board_support.py`, `test_hamiltonian_validation.py`, `test_experiment_command.py`; Play message Manual |
| REQ-014 | Test | `test_session_settings.py`, `test_bot_mode_headless.py` |
| REQ-015 – REQ-016 | Test | `test_session_settings.py`, `test_settings_file.py`, `test_app_settings.py` |
| REQ-017 | Test | `test_window_layout.py` |
| REQ-018 – REQ-019 | Test | `test_game_session.py`, `test_records_browser.py` |
| REQ-020 – REQ-022 | Test | `test_replay_session.py`, `test_replay_schema.py`, `test_records_browser.py`, `test_grid_coordinate_migration.py` |
| REQ-023 | Manual | No test of `TrainingStartView` (G-16); summary logic in `test_training_saves.py` |
| REQ-024, REQ-027 | Test | `test_training_saves.py` |
| REQ-025, REQ-026 | Test | `test_app_q_learning_training.py`, `test_live_training_session.py` |
| REQ-028 | Test + Manual | `test_live_training_session.py`, `test_live_training_save.py`, `test_live_training_start.py`; save on leave/close Manual |
| REQ-029 | Test | `test_dqn_optional_dependency.py` (ImportError only) |
| REQ-030 | Test (partial) | `test_q_table_loading.py`, `test_live_training_start.py`; Continue crash case Planned (G-4) |
| REQ-031 | Test | `test_q_learning_training_history.py`, `test_app_training_history.py` |
| REQ-032 – REQ-034 | Test | `test_evaluation_session.py`, `test_dqn_evaluation_session.py` |
| REQ-035 | Test + Manual | `test_evaluation_session.py` (path); button Manual |
| REQ-036 | Test | `test_showcase_bots.py` |
| REQ-037 | Test | `test_evaluation_reports.py` |
| REQ-038 – REQ-043 | Test | `test_bot_report_command.py`, `test_paired_comparison.py`, `test_experiment_command.py`, `test_dqn_evaluation_command.py` |
| REQ-044 – REQ-047 | Test | `test_training_command.py`, `test_q_learning_v3_commands.py`, `test_dqn_training_command.py`, `test_experiment_command.py`, `test_dqn_experiment_command.py`, `test_dqn_evaluation_command.py` |
| REQ-048 – REQ-049 | Test | `test_evaluation_session.py`, `test_bot_mode_contract.py`, `test_bot_mode_headless.py` |
| REQ-050 | Test | `test_bot_report_command.py` |
| REQ-051 | Test (partial) | `test_atomic_saves.py`, `test_settings_file.py`; records and reports Planned (G-2, G-3) |
| REQ-052 | Test | `test_training_saves.py`, `test_training_command.py`, `test_dqn_training_command.py` |
| REQ-053 | Test (partial) | `test_replay_schema.py`, `test_settings_file.py`, `test_records_browser.py`; gaps Planned (G-1, G-4, G-6) |
| REQ-054 | Planned | Only Settings is tested (`test_settings_file.py`) |
| REQ-055 | Manual | Smoke checklist |
| REQ-056 | Manual | Quick Start on a clean computer |
| REQ-057 | Test | CI workflow `tests.yml`; `test_arcade_path_guard.py` |
| REQ-058 – REQ-062 | Inspection | `pyproject.toml`, `uv.lock`, `.gitignore`, `LICENSE`, imports |
