# MTRX — Build List
### TDS V1.0.2 | Feature Inclusion Checklist

Check each item to include in V1. Leave unchecked to defer.

---

## Constants & Configuration
*`mtrx_constants.py` — shared infrastructure; all items here are load-bearing for any downstream feature.*

- [V1] **STIMULUS_TABLE** — defines the four stimulus types (N, MT, MD, MS) with adaptation window, fatigue window, and display color for each.
- [V1] **CANONICAL_SCHEMES** — defines the four standard rep schemes (3×2, 3×5, 3×10, 3×20) with their associated stimulus type and percentage of DDM.
- [V1] **MEASUREMENT_UNITS** — defines the five exercise measurement unit types (VOLUME, DURATION, DISTANCE, LOAD_DISTANCE, REPS_ONLY) and the required data fields for each.
- [V1] **SEGMENT_TEMPLATES — BLANK** — the default empty category plan template with all 24 plane × movement combinations pre-populated with classification slots and weights set to zero; seeded into each new user's plan via `deepcopy` on `add_user`.
- [ ] **SEGMENT_TEMPLATES — named presets** (GPP, STRENGTH, HYPERTROPHY, POWERLIFTING, FUNCTIONAL) — optional, scale-adaptable allocation pattern templates; applied at the segment level when building training blocks; proportional distributions that scale to any exercise budget; currently empty stubs in the TDS.
- [V1] **Controlled vocabulary sets** (MOVEMENT_PLANES, MOVEMENT_TYPES, WORKOUT_TYPES, LATERALITY, LOAD_TYPES) — validation sets used at every write boundary to reject invalid inputs.
- [V1] **PROGRAM_START_DATE** — single calendar anchor from which all week-number and block-label arithmetic is derived; required by `get_program_week_bounds` and segment week arithmetic.

---

## Users
*`MtrxDatabase` — user identity and registration.*

- [V1] **`add_user`** — registers a new user with a unique username and email, seeds their category plan from a preset, and initialises all per-user data stores.
- [V1] **`get_user`** — retrieves a copy of one user's profile by user ID.
- [V1] **`get_all_users`** — retrieves copies of all user profiles.

---

## User Measurements
*`MtrxDatabase` — bodyweight time series per user.*

- [V1] **`add_measurement`** — logs a dated bodyweight entry (and optional additional metrics) for a user; maintains the list in ascending date order.
- [V1] **`get_bodyweight_on_date`** — returns the most recent bodyweight recorded on or before a given date; used to auto-resolve weight for bodyweight exercises at log time.
- [V1] **`delete_measurement`** — removes a measurement entry by ID; for correcting data-entry errors.

---

## Exercise Library
*`MtrxDatabase` — shared across all users; links exercises to plane × movement × classification.*

- [V1] **`add_exercise`** — adds a new exercise to the shared library with its plane, movement type, classification, laterality, workout type, and default load type.
- [V1] **`get_exercise`** — retrieves one exercise record by name (case-insensitive).
- [V1] **`get_exercises_for_cell`** — returns all exercise names mapped to a given plane × movement combination; used by the prescription engine and views.
- [V1] **`get_all_exercises`** — returns the full exercise library dict; required by view functions that need to look up exercise attributes across all records.
- [V1] **`update_exercise`** — updates attributes of an existing exercise (name change is blocked to protect historical records).
- [V1] **`delete_exercise`** — removes an exercise from the library; blocked if any workout records reference it.
- [ ] **`merge_exercises`** — re-points all historical records from a source exercise name to a canonical target name, then removes the source entry; resolves duplicates like 'bench press' / 'bench-press' without data loss.

---

## Workout Records
*`MtrxDatabase` — the append-only log of all training activity.*

- [V1] **`add_record`** — logs a workout set to a user's history, validates required fields against the exercise's measurement unit, and auto-resolves bodyweight when applicable.
- [V1] **`get_records`** — retrieves records filtered by any combination of user, date range, and exercise name; primary data source for all views.
- [V1] **`delete_record`** — removes a record by ID; for correcting data-entry errors.

---

## Category Plans
*`MtrxDatabase` — per-user hierarchical plan: plane × movement combinations each containing classification slots.*

- [V1] **`update_category_plan_cell`** — replaces the full list of classification slots for one plane × movement combination; auto-triggers a plan history snapshot.
- [V1] **`add_classification`** — appends a new classification slot to an existing plane × movement combination without affecting existing slots; auto-triggers a plan history snapshot.
- [V1] **`get_category_plan`** — returns a deep copy of the full hierarchical plan for one user.
- [V1] **`get_parent_weight`** — computes and returns the derived parent weight (sum of classification weights) for one plane × movement combination.

---

## Plan History
*`MtrxDatabase` — append-only audit trail of category plan changes.*

- [V1] **`save_config_snapshot`** — captures a timestamped deep copy of the current category plan state; called automatically on every plan modification, not by the caller.
- [V1] **`get_active_config`** — returns the most recent plan snapshot (the current effective configuration).
- [V1] **`get_plan_history`** — returns the full ordered list of plan snapshots for a user; enables strategy-over-time analysis.

---

## Training Blocks
*`MtrxDatabase` — user-defined programming periods containing ordered segments; each segment has independent allocation, workouts_per_week, and exercises_per_workout.*

- [V1] **`add_training_block`** — creates a named programming period with a start date and an ordered segments list; each segment specifies `weeks`, `workouts_per_week`, `exercises_per_workout`, `allocation` (classification slot counts per workout), and an optional `preset_key`; block budget and end date are derived from segments.
- [V1] **`get_active_block`** — returns the training block covering a given date (defaults to today); returns `None` if no block is active.
- [V1] **`get_active_segment`** — returns the segment within a given block that covers a given date; used by the session planning engine to resolve current allocation and exercises_per_workout.
- [V1] **`get_block_progress`** — returns per-segment allocation coverage and output metrics (volume accumulated, sessions logged) per classification slot; surfaced as context — time elapsed is never the primary progress measure.

---

## Derived Metrics
*`mtrx_functions.py` — pure functions; no side effects; all inputs explicit.*

- [V1] **`classify_stimulus`** — maps a rep count to one of four stimulus types (N / MT / MD / MS) via an ordered boundary check.
- [V1] **`compute_actual_reps`** — calculates total reps performed including bonus reps: `(sets × reps) + bonus_reps`.
- [V1] **`compute_actual_volume`** — calculates total volume with a ×2 multiplier applied for unilateral exercises.
- [V1] **`compute_unrealized_vesting_pct`** — returns the fraction of the adaptation window still remaining (0–1) for a given workout date.
- [V1] **`compute_unrealized_volume`** — the portion of actual volume still within the adaptation window, decaying to zero as the window closes.
- [V1] **`compute_realized_volume`** — the portion of actual volume with full adaptation complete; derived as `actual − unrealized` to enforce the accounting identity.
- [V1] **`compute_fatigue_volume`** — the portion of actual volume still within the shorter fatigue window; an independent sub-filter of unrealized volume.
- [V1] **`compute_ddm`** — computes the Desirable Difficulty Max by back-calculating an implied reference weight from recent sessions across canonical schemes; requires ≥2 schemes with history in the last 90 days.
- [V1] **`compute_weight_suggestions`** — produces per-scheme working weight targets for all four canonical schemes from a given DDM value.
- [V1] **`compute_blended_adaptation`** — calculates a volume-weighted blended vesting percentage and display color for sessions involving multiple stimulus types.
- [] **`build_session`** — surfaces a ranked session plan for the day by computing category deficits across the active segment, ranking by weighted remaining allocation, and presenting exercise options with scheme and weight suggestions for each slot.

---

## Views
*`mtrx_functions.py` — DataFrame-returning aggregation functions; VOLUME records only in V1.*

- [V1] **`build_summary_matrix`** — aggregates volume by exercise and stimulus type into realized, unrealized, fatigue, and non-fatigue buckets; filterable by period (all-time, last 30 / 60 / 90 days, YTD, TTM).
- [V1] **`build_vesting_grid`** — pivots records into a date × exercise grid showing volume (or reps) within the active adaptation window.
- [V1] **`build_color_matrix`** — companion to the vesting grid; produces a blended hex color and opacity value for each date × exercise cell based on stimulus mix.
- [ ] **`build_program_balance`** — iterates all plane × movement combinations and returns plan vs. completed session counts, status, and volume for a given period.
- [V1] **`build_weight_guidance`** — surfaces DDM and per-scheme weight suggestions for one exercise; returns a structured note if DDM cannot yet be calculated.

---

## Program Calendar
*`mtrx_functions.py` — arithmetic week and block labeling from `PROGRAM_START_DATE`.*

- [V1] **`get_program_week_bounds`** — returns the Monday–Sunday bounds of the program week containing a given date; required by the session planning engine, segment week arithmetic, and block progress tracking.
- [ ] **`get_block_label`** — returns a human-readable display label (e.g., `'Round 2 | Week 3'`) for a given date; display-only, not authoritative for block structure.

---

## App Controller
*`mtrx_app.py` — thin orchestration layer; all business logic delegated to functions.*

- [V1] **`register_user`** — creates a new user account and seeds their category plan from a chosen preset template (`SEGMENT_TEMPLATES`).
- [V1] **`log_measurement`** — records a dated bodyweight entry for a user.
- [V1] **`add_exercise`** — adds an exercise to the shared library.
- [V1] **`log_workout`** — logs a training set, returns the record ID, and — if DDM is calculable — returns working weight suggestions for all four schemes.
- [ ] **`generate_session`** — assembles all required inputs, resolves the active segment via `get_active_segment`, and calls `build_session` to return today's session plan.
- [V1] **`get_weight_guidance`** — returns DDM and per-scheme weight suggestions for a given exercise and user.
- [V1] **`get_summary_matrix`** — returns the summary volume aggregation for a user.
- [V1] **`get_vesting_grid`** — returns the date × exercise adaptation grid for a user.
- [ ] **`get_program_balance`** — returns plan vs. completed session counts across all plane × movement combinations for a given period.
- [ ] **`update_category_plan_cell`** — replaces the classification slots for one plane × movement combination in a user's plan.
- [V1] **`add_training_block`** — creates a training block with a start date and ordered segments list.
- [V1] **`get_active_block`** — returns the active block for a given date.
- [V1] **`get_active_segment`** — returns the segment covering a given date within the active block; required by `generate_session` to resolve current allocation.
- [V1] **`get_block_progress`** — returns per-segment allocation coverage and output metrics for a training block.
- [ ] **`get_plan_history`** — returns the full plan change history for a user.

---

## Persistence
*`mtrx_database.py` — save and restore full application state.*

- [V1] **`serialize`** — converts the full `MtrxDatabase` state to a JSON-serializable dict, encoding tuple keys and all nested structures; `SCHEMA_VERSION = 2`.
- [V1] **`deserialize`** — reconstructs a `MtrxDatabase` instance from a serialized dict, restoring all counters, records, plan history, and training blocks.

---

## Leaderboards
*`mtrx_functions.py` + `mtrx_app.py` — filterable high-score standings across users.*

- [V1] **`build_leaderboard`** — returns ranked standings for any combination of users filterable by exercise, classification, plane × movement combination, workout type, or full-library total; metrics include total volume, total reps, max load, session count, and exercise count; supports period windows of all-time, last 30 / 60 / 90 days, YTD, and TTM.

---

## V2 — Competitive Platform *(intent only; no implementation spec)*

- [ ] **Deterministic scoring** — produces a consistent score from any category plan configuration given the same inputs; not adherence-based.
- [ ] **Relative performance metric** — measures progress toward a user's own goal rather than absolute output comparisons.
- [ ] **Handicap system** — adjusts scores to enable fair competition across users with different goals, experience, age, and training frequency.
- [ ] **Peer group comparison** — groups users by similar strategy, configuration, and category plan for direct comparison.
- [ ] **Radar grid positioning** — places each user on a spider chart defined by preset configurations to determine peer group membership and handicap inputs.
- [ ] **Temporal challenges** — time-bound competitive formats including monthly competitions and centrality-of-effort windows.

---

## V2 — AI Data Access Layer *(intent only; no implementation spec)*

- [ ] **JSON-serializable API surface** — all `MtrxApp` methods return `dict`, `list[dict]`, or `pd.DataFrame` suitable for LLM tool-calling with no custom glue code.
- [ ] **Jupyter notebook generation** — agent queries the data layer and generates notebook cells with charts, gap analysis, and natural language recommendations.
- [ ] **Dynamic filtering and visualization** — all views support filterable, granular queries (session / week / block / all-time) rendered in the notebook environment.
- [ ] **Agentic programming modification** — agent adjusts category plan weights, creates training blocks, and modifies prescriptions through the same validated `MtrxApp` API surface used by direct user interaction.
