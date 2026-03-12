# MTRX — Build List
### TDS V1.0.2 | Feature Inclusion Checklist

Check each item to include in V1. Leave unchecked to defer.

---

## Constants & Configuration
*`mtrx_constants.py` — shared infrastructure; all items here are load-bearing for any downstream feature.*

- [ ] **STIMULUS_TABLE** — defines the four stimulus types (N, MT, MD, MS) with adaptation window, fatigue window, and display color for each.
- [ ] **CANONICAL_SCHEMES** — defines the four standard rep schemes (3×2, 3×5, 3×10, 3×20) with their associated stimulus type and percentage of DDM.
- [ ] **MEASUREMENT_UNITS** — defines the five exercise measurement unit types (VOLUME, DURATION, DISTANCE, LOAD_DISTANCE, REPS_ONLY) and the required data fields for each.
- [ ] **PRESET_MATRIX_CONFIGS — BLANK** — the default empty category plan template with all 24 plane × movement combinations pre-populated with dimensionality slots and weights set to zero.
- [ ] **PRESET_MATRIX_CONFIGS — named presets** (GPP, STRENGTH, HYPERTROPHY, POWERLIFTING, FUNCTIONAL) — additional starting templates with pre-configured weights; currently empty shells in the TDS.
- [ ] **Controlled vocabulary sets** (MOVEMENT_PLANES, MOVEMENT_TYPES, WORKOUT_TYPES, LATERALITY, LOAD_TYPES) — validation sets used at every write boundary to reject invalid inputs.
- [ ] **PROGRAM_START_DATE** — single calendar anchor from which all week-number and block-label arithmetic is derived.

---

## Users
*`MtrxDatabase` — user identity and registration.*

- [ ] **`add_user`** — registers a new user with a unique username and email, seeds their category plan from a preset, and initialises all per-user data stores.
- [ ] **`get_user`** — retrieves a copy of one user's profile by user ID.
- [ ] **`get_all_users`** — retrieves copies of all user profiles.

---

## User Measurements
*`MtrxDatabase` — bodyweight time series per user.*

- [ ] **`add_measurement`** — logs a dated bodyweight entry (and optional additional metrics) for a user; maintains the list in ascending date order.
- [ ] **`get_bodyweight_on_date`** — returns the most recent bodyweight recorded on or before a given date; used to auto-resolve weight for bodyweight exercises at log time.
- [ ] **`delete_measurement`** — removes a measurement entry by ID; for correcting data-entry errors.

---

## Exercise Library
*`MtrxDatabase` — shared across all users; links exercises to plane × movement × dimensionality.*

- [ ] **`add_exercise`** — adds a new exercise to the shared library with its plane, movement type, dimensionality slot, laterality, workout type, and default load type.
- [ ] **`get_exercise`** — retrieves one exercise record by name (case-insensitive).
- [ ] **`get_exercises_for_cell`** — returns all exercise names mapped to a given plane × movement combination; used by the prescription engine and views.
- [ ] **`get_all_exercises`** — returns the full exercise library dict; required by view functions that need to look up exercise attributes across all records.
- [ ] **`update_exercise`** — updates attributes of an existing exercise (name change is blocked to protect historical records).
- [ ] **`delete_exercise`** — removes an exercise from the library; blocked if any workout records reference it.

---

## Workout Records
*`MtrxDatabase` — the append-only log of all training activity.*

- [ ] **`add_record`** — logs a workout set to a user's history, validates required fields against the exercise's measurement unit, and auto-resolves bodyweight when applicable.
- [ ] **`get_records`** — retrieves records filtered by any combination of user, date range, and exercise name; primary data source for all views.
- [ ] **`delete_record`** — removes a record by ID; for correcting data-entry errors.

---

## Category Plans
*`MtrxDatabase` — per-user hierarchical plan: plane × movement combinations each containing dimensionality slots.*

- [ ] **`update_category_plan_cell`** — replaces the full list of dimensionality slots for one plane × movement combination; auto-triggers a plan history snapshot.
- [ ] **`add_dimensionality`** — appends a new dimensionality slot to an existing plane × movement combination without affecting existing slots; auto-triggers a plan history snapshot.
- [ ] **`get_category_plan`** — returns a deep copy of the full hierarchical plan for one user.
- [ ] **`get_parent_weight`** — computes and returns the derived parent weight (sum of dimensionality weights) for one plane × movement combination.

---

## Plan History
*`MtrxDatabase` — append-only audit trail of category plan changes.*

- [ ] **`save_config_snapshot`** — captures a timestamped deep copy of the current category plan state; called automatically on every plan modification, not by the caller.
- [ ] **`get_active_config`** — returns the most recent plan snapshot (the current effective configuration).
- [ ] **`get_plan_history`** — returns the full ordered list of plan snapshots for a user; enables strategy-over-time analysis.

---

## Training Blocks
*`MtrxDatabase` — user-defined programming periods with explicit targets.*

- [ ] **`add_training_block`** — creates a named programming period with start/end dates and a per-dimensionality weekly session target dict.
- [ ] **`get_active_block`** — returns the training block covering a given date (defaults to today); returns `None` if no block is active.
- [ ] **`get_block_progress`** — returns plan vs. completed session counts per dimensionality, broken down by program week, for the duration of a block.

---

## Derived Metrics
*`mtrx_functions.py` — pure functions; no side effects; all inputs explicit.*

- [ ] **`classify_stimulus`** — maps a rep count to one of four stimulus types (N / MT / MD / MS) via an ordered boundary check.
- [ ] **`compute_actual_reps`** — calculates total reps performed including bonus reps: `(sets × reps) + bonus_reps`.
- [ ] **`compute_actual_volume`** — calculates total volume with a ×2 multiplier applied for unilateral exercises.
- [ ] **`compute_unrealized_vesting_pct`** — returns the fraction of the adaptation window still remaining (0–1) for a given workout date.
- [ ] **`compute_unrealized_volume`** — the portion of actual volume still within the adaptation window, decaying to zero as the window closes.
- [ ] **`compute_realized_volume`** — the portion of actual volume with full adaptation complete; derived as `actual − unrealized` to enforce the accounting identity.
- [ ] **`compute_fatigue_volume`** — the portion of actual volume still within the shorter fatigue window; an independent sub-filter of unrealized volume.
- [ ] **`compute_ddm`** — computes the Desirable Difficulty Max by back-calculating an implied reference weight from recent sessions across canonical schemes; requires ≥2 schemes with history in the last 90 days.
- [ ] **`compute_weight_suggestions`** — produces per-scheme working weight targets for all four canonical schemes from a given DDM value.
- [ ] **`compute_blended_adaptation`** — calculates a volume-weighted blended vesting percentage and display color for sessions involving multiple stimulus types.
- [ ] **`build_session`** — generates a full session prescription for a given day by computing category deficits, ranking by weighted remaining value, and selecting exercises with scheme and weight suggestions.

---

## Views
*`mtrx_functions.py` — DataFrame-returning aggregation functions; VOLUME records only in V1.*

- [ ] **`build_summary_matrix`** — aggregates all-time volume by exercise and stimulus type, broken into realized, unrealized, fatigue, and non-fatigue buckets.
- [ ] **`build_vesting_grid`** — pivots records into a date × exercise grid showing volume (or reps) within the active adaptation window.
- [ ] **`build_color_matrix`** — companion to the vesting grid; produces a blended hex color and opacity value for each date × exercise cell based on stimulus mix.
- [ ] **`build_program_balance`** — iterates all plane × movement combinations and returns plan vs. completed session counts, status, and volume for a given period.
- [ ] **`build_weight_guidance`** — surfaces DDM and per-scheme weight suggestions for one exercise; returns a structured note if DDM cannot yet be calculated.

---

## Program Calendar
*`mtrx_functions.py` — arithmetic week and block labeling from `PROGRAM_START_DATE`.*

- [ ] **`get_program_week_bounds`** — returns the Monday–Sunday bounds of the program week containing a given date; used by the prescription engine and block progress tracking.
- [ ] **`get_block_label`** — returns a human-readable display label (e.g., `'Round 2 | Week 3'`) for a given date; display-only, not authoritative for block structure.

---

## App Controller
*`mtrx_app.py` — thin orchestration layer; all business logic delegated to functions.*

- [ ] **`register_user`** — creates a new user account and seeds their category plan from a chosen preset.
- [ ] **`log_measurement`** — records a dated bodyweight entry for a user.
- [ ] **`add_exercise`** — adds an exercise to the shared library.
- [ ] **`log_workout`** — logs a training set, returns the record ID, and — if DDM is calculable — returns working weight suggestions for all four schemes.
- [ ] **`generate_session`** — assembles all required inputs and calls `build_session` to return today's prescribed workout.
- [ ] **`get_weight_guidance`** — returns DDM and per-scheme weight suggestions for a given exercise and user.
- [ ] **`get_summary_matrix`** — returns the summary volume aggregation for a user.
- [ ] **`get_vesting_grid`** — returns the date × exercise adaptation grid for a user.
- [ ] **`get_program_balance`** — returns plan vs. completed session counts across all plane × movement combinations for a given period.
- [ ] **`update_category_plan_cell`** — replaces the dimensionality slots for one plane × movement combination in a user's plan.
- [ ] **`add_training_block`** — creates a training block with period dates and per-dimensionality weekly targets.
- [ ] **`get_block_progress`** — returns plan vs. completed breakdown for a training block by week.
- [ ] **`get_plan_history`** — returns the full plan change history for a user.

---

## Persistence
*`mtrx_database.py` — save and restore full application state.*

- [ ] **`serialize`** — converts the full `MtrxDatabase` state to a JSON-serializable dict, encoding tuple keys and all nested structures; `SCHEMA_VERSION = 2`.
- [ ] **`deserialize`** — reconstructs a `MtrxDatabase` instance from a serialized dict, restoring all counters, records, plan history, and training blocks.

---

## V2 — Competitive Platform *(intent only; no implementation spec)*

- [ ] **Deterministic scoring** — produces a consistent score from any matrix configuration given the same inputs; not adherence-based.
- [ ] **Relative performance metric** — measures progress toward a user's own goal rather than absolute output comparisons.
- [ ] **Handicap system** — adjusts scores to enable fair competition across users with different goals, experience, age, and training frequency.
- [ ] **Peer group comparison** — groups users by similar strategy, configuration, and category plan for direct comparison.
- [ ] **Multi-dimensional leaderboards** — standings viewable by lift, category, plane, time period, and user-defined dimensions using a multi-tier jersey format.
- [ ] **Radar grid positioning** — places each user on a spider chart defined by preset configurations to determine peer group membership and handicap inputs.
- [ ] **Temporal challenges** — time-bound competitive formats including monthly competitions and centrality-of-effort windows.

---

## V2 — AI Data Access Layer *(intent only; no implementation spec)*

- [ ] **JSON-serializable API surface** — all `MtrxApp` methods return `dict`, `list[dict]`, or `pd.DataFrame` suitable for LLM tool-calling with no custom glue code.
- [ ] **Jupyter notebook generation** — agent queries the data layer and generates notebook cells with charts, gap analysis, and natural language recommendations.
- [ ] **Dynamic filtering and visualization** — all views support filterable, granular queries (session / week / block / all-time) rendered in the notebook environment.
- [ ] **Agentic programming modification** — agent adjusts category plan weights, creates training blocks, and modifies prescriptions through the same validated `MtrxApp` API surface used by direct user interaction.
