# MTRX — System Overview
### TDS V1.0.2 Reference Map

---

## 1. What Is MTRX?

A training management system with four integrated layers:

| Layer | Role |
|---|---|
| **Tracking** | Records workout sessions and maps them to a user-defined movement category plan |
| **Prescription** | Generates adaptive session recommendations based on plan vs. completed delta |
| **Competitive Platform** | Deterministic scoring enabling handicap-adjusted comparison across users *(V2 — intent only)* |
| **AI Data Access** | LLM-ready API surface for conversational data access, notebook generation, and programmatic plan modification *(V2 — intent only)* |

**Core philosophy:** the plan is a living target. Deviation is absorbed and redistributed week-to-week, not penalized.

---

## 2. File Architecture

Four files with a strict one-way dependency chain — each layer imports only from below it.

```
mtrx_constants.py   ← no imports; pure data definitions
        ↓
mtrx_functions.py   ← pure functions; no side effects; imports constants
        ↓
mtrx_database.py    ← stateful storage; calls functions, never recomputes inline
        ↓
mtrx_app.py         ← public controller; thin orchestration; calls db + functions
```

**Why this matters:** every derived metric is defined exactly once in `mtrx_functions.py`. A calculation bug is isolated to one function in one file. The storage backend is swappable (e.g. in-memory → SQLite) by changing only `mtrx_database.py` internals — `mtrx_app.py` and all view functions are untouched.

---

## 3. Constants Layer (`mtrx_constants.py`)

Fixed values imported wherever needed. Never passed as arguments, never modified at runtime.

| Constant | What It Is | Used By |
|---|---|---|
| `STIMULUS_TABLE` | Four stimulus types (N/MT/MD/MS) with adaptation days, fatigue days, and hex color | `classify_stimulus`, vesting calculations, color rendering |
| `CANONICAL_SCHEMES` | Four rep schemes (3×2, 3×5, 3×10, 3×20) each mapped to a stimulus type and a % of DDM | `compute_ddm`, `compute_weight_suggestions` |
| `MEASUREMENT_UNITS` | Five unit types (VOLUME, DURATION, DISTANCE, LOAD_DISTANCE, REPS_ONLY) with required fields per unit | Record validation in `add_record`; prescription logic in `build_session` |
| `PRESET_MATRIX_CONFIGS` | Pre-built training templates (BLANK + named presets) containing 24 parent categories with sub-categories and per-category measurement units | Seeds each new user's matrix via `deepcopy` on `add_user` |
| `MOVEMENT_PLANES / TYPES / etc.` | Controlled vocabulary sets for validation at every write boundary | All `add_*` and `update_*` methods |
| `PROGRAM_START_DATE` | Single calendar anchor (2026-01-05) from which all week/block arithmetic derives | `get_program_week_bounds`, `get_block_label` |

**Key V1.0.2 change:** `PRIORITY_TARGETS` and `PRIORITY_OPTIONS` removed. Priority is no longer a single string per cell — it is expressed as per-category integer weights inside the hierarchical matrix structure.

---

## 4. Class Architecture

Two classes. One boundary between them that must never be crossed.

### `MtrxDatabase`
The internal state store. All data lives here as private attributes. External code never touches them directly — only through public methods. This contract is what makes the backend swappable.

Private state:

| Attribute | Type | What It Holds |
|---|---|---|
| `__users` | `dict[int, dict]` | User profiles, keyed by `user_id` |
| `__measurements` | `dict[int, list[dict]]` | Per-user bodyweight time series, sorted ascending by date |
| `__exercises` | `dict[str, dict]` | Shared exercise library, keyed by normalized name |
| `__records` | `list[dict]` | All workout records, flat, with `user_id` field |
| `__matrix_plans` | `dict[int, dict[tuple, dict]]` | Per-user category plan: plane × movement combinations, each with dimensionality slots |
| `__plan_history` | `dict[int, list[dict]]` | Append-only snapshots of matrix state over time |
| `__training_blocks` | `dict[int, list[dict]]` | Per-user user-defined programming periods with targets |

### `MtrxApp`
The public controller. Holds one `MtrxDatabase`. Methods pull data from the db, pass it to functions, return or display results. No business logic lives here.

---

## 5. Data Layer — Entities

### 5.1 Users
Profile data plus `age` and `training_experience` (stored, not yet computed against). On creation, automatically seeds `matrix_plans`, `measurements`, `plan_history`, and `training_blocks` for that user. `deepcopy` of the chosen preset grid is mandatory — shallow copy would share mutable lists across users.

### 5.2 Measurements
Bodyweight time series per user, kept sorted ascending. Used to auto-resolve `weight` at record-log time when `load_type == 'Bodyweight'`. The most-recent-on-or-before query is a forward scan — no index needed.

### 5.3 Exercise Library
Shared across all users. Keyed by `exercise_name.strip().lower()` for dedup. Every exercise maps to a three-part identity: **plane × movement × dimensionality**. Each exercise record carries:

- `movement_plane` + `movement_type` — the parent combination (e.g., `'Sagittal'`, `'Push'`)
- `dimensionality` — the named slot within that combination (e.g., `'Vertical Press'`, `'Horizontal Press'`, or `'Downward Press'` within Sagittal Push)
- `laterality` — `Bilateral` or `Unilateral`; drives the ×2 volume multiplier at record time
- `workout_type`, `default_load_type` — used for filtering and weight resolution

Exercise names cannot be renamed (would orphan historical records). The `dimensionality` field is the formal link between the shared exercise library and the per-user category plan defined in 5.5; it is required for correct category-level aggregation in views and deficit calculation in the prescription engine.

Duplicate entries (e.g. `'bench press'` vs `'bench-press'`) are resolved via `merge_exercises`, which re-points all historical records from the source name to the canonical target and removes the source entry without data loss.

> **Open issue:** the `dimensionality` field is not present in the exercise schema in TDS §3.3. The `add_record` spec currently resolves category by "exercise characteristics or first match," which is ambiguous. This needs to be resolved before Stage 3 implementation.

### 5.4 Workout Records
A flat `list[dict]`. Every view is a different aggregation; a flat list feeds `pd.DataFrame(records)` directly, supporting any pandas groupby or filter in one line. Records include nullable `duration_seconds` and `distance_meters` to support all five measurement units.

### 5.5 Category Plans
Per-user hierarchical plan with two levels:

- **Plane × movement combination** — keyed by `(movement_plane, movement_type)` tuple; 24 combinations in the default configuration (3 planes × 8 movement types)
- **Dimensionality** — named slots within each combination (e.g., `'Vertical Press'`, `'Horizontal Press'`, `'Downward Press'` within `('Sagittal', 'Push')`), each carrying an integer `weight`, `measurement_unit`, and `exercise_examples`

Parent weight is always derived (`sum` of dimensionality weights) — never stored — eliminating sync errors. The tuple key `(plane, type)` is the canonical join key used throughout the system to link exercises, records, and views back to the category plan.

**Key V1.0.2 change:** replaces the old flat structure of priority strings. The `exercise_examples` list on each dimensionality slot is a reference hint, not an enforcement mechanism — exercises are formally linked via the `dimensionality` field on the exercise record (see 5.3).

### 5.6 Plan History
Append-only, timestamped snapshots of the full category plan state. Auto-triggered by any plan modification. Enables plan-vs-completed analysis even after the user later changes their configuration. All snapshots are `deepcopy` — mutation-isolated from the live plan.

### 5.7 Training Blocks
User-defined programming periods with start/end dates used as loose boundaries. Progress is measured by volume accumulated, session exposure, and other output metrics — not by elapsed time. Time is a view; the authoritative progress signal is what was done, not how long it took. The `targets` dict expresses per-dimensionality goals in the relevant measurement unit for each category.

> **Open TODO in TDS:** block targets currently use `weekly_target` (session count). These should be extended to support volume and exposure targets per the measurement unit of each dimensionality slot. Needs resolution before Stage 3 implementation.

---

## 6. Derived Metrics Layer (`mtrx_functions.py`)

All pure functions — no side effects, deterministic, testable in isolation. `today` is always an explicit argument (never `datetime.date.today()` inside a function), enabling back-testing.

| Function | What It Computes | Depends On |
|---|---|---|
| `classify_stimulus(reps)` | N / MT / MD / MS from rep count | Ordered if/elif chain; not a table lookup |
| `compute_actual_reps` | `(sets × reps) + bonus_reps` | Called before volume |
| `compute_actual_volume` | Total volume; applies ×2 multiplier for unilateral | `actual_reps`, `weight`, `laterality` |
| `compute_unrealized_vesting_pct` | Fraction of adaptation window remaining (0–1) | `workout_date`, `today`, `adaptation_days` |
| `compute_unrealized_volume` | Volume still within adaptation window | `actual_volume × unrealized_pct` |
| `compute_realized_volume` | Volume with full adaptation complete | `actual − unrealized` (accounting identity) |
| `compute_fatigue_volume` | Volume still within fatigue window | Independent decay; sub-filter of adaptation |
| `compute_ddm` | Desirable Difficulty Max — implied 1RM proxy averaged across 2–4 canonical schemes | Requires ≥2 schemes in 90-day window; returns `None` otherwise |
| `compute_weight_suggestions` | Per-scheme weight targets from DDM | Dict comprehension over `CANONICAL_SCHEMES` |
| `compute_blended_adaptation` | Volume-weighted blended color + vesting % for mixed-stimulus sessions | Hex-to-RGB string slicing; no external color library |
| `build_session` | Full session prescription for today | Matrix plan, records, exercise library, block targets, week bounds |

**Key V1.0.2 change:** `check_intra_cell_variation` and `check_stimulus_interleaving` removed as standalone functions. Their logic is now internal steps inside `build_session`.

---

## 7. Views Layer (also `mtrx_functions.py`)

View functions accept flat records + supporting data, return a `pd.DataFrame`. All are VOLUME-centric in V1 — records with non-VOLUME measurement units are filtered out. Other exercise types are future work.

| View | What It Shows | Key Pandas Operation |
|---|---|---|
| `build_summary_matrix` | Volume by exercise and stimulus type in realized / unrealized / fatigue / non-fatigue buckets; filterable by period (all-time, last 30/60/90 days, YTD, TTM) | `groupby(['workout_type', 'exercise_name', 'stimulus']).agg(...)` |
| `build_vesting_grid` | Per-exercise per-date volume (adaptation window only by default) | `pivot_table(index='date', columns='exercise_name')` |
| `build_color_matrix` | Companion to vesting grid; blended hex+pct per (date, exercise) cell | Calls `compute_blended_adaptation` per cell |
| `build_program_balance` | Plan vs. completed sessions per dimensionality across all plane × movement combinations, with period status | Iterates `MOVEMENT_PLANES_ORDERED × MOVEMENT_TYPES_ORDERED` |
| `build_weight_guidance` | DDM + four scheme weight suggestions for one exercise | Calls `compute_ddm` → `compute_weight_suggestions` |

**Display-layer rule:** pivoting, coloring, and formatting happen in `mtrx_app.py`. View functions return long-format (tidy) data only.

---

## 8. Leaderboards

Filterable high-score standings across users. A single `build_leaderboard` function accepts filter parameters and a period window and returns a ranked DataFrame.

| Parameter | Options |
|---|---|
| **Filter scope** | Full library total, specific exercise, dimensionality slot, plane × movement combination, workout type |
| **Period window** | All-time, last 30 days, last 60 days, last 90 days, YTD, TTM |
| **Metric** | Volume, session exposure (count), or other output measure |

Leaderboards are not tied to the competitive scoring or handicap system (V2). They are direct ranked aggregations of the same records used by all other views, making them composable with any existing filter.

---

## 9. Program Calendar

No stored calendar table. All week bounds derived arithmetically from `PROGRAM_START_DATE`.

| Function | Returns |
|---|---|
| `get_program_week_bounds(date)` | `(week_start, week_end)` for the program week containing `date` |
| `get_block_label(date)` | Human-readable display label (`'Round 2 | Week 3'`) — display-only, not authoritative for block structure |

Authoritative block structure and targets live in `__training_blocks` (Section 5.7).

---

## 10. Competitive Platform & AI Layer (V2 — Intent Only)

Not yet implemented. Data model from V1 is sufficient to support both when mechanics are defined.

- **Competitive Platform (§8):** deterministic scoring, handicap system, peer group comparison, radar grid positioning using `PRESET_MATRIX_CONFIGS` axes, temporal challenges. Multi-dimensional leaderboards (filterable high-score boards) are V1 and specified in Section 8 above.
- **AI Data Access Layer (§9):** all `MtrxApp` methods are designed as LLM tool endpoints (return `dict` / `list[dict]` / `pd.DataFrame`). Agent modifies plans through the same validated API surface — no bypassing validation or plan history.

---

## 11. Implementation Sequence

| Stage | File(s) | Deliverable |
|---|---|---|
| 1 | `mtrx_constants.py` | All constants; assert BLANK config has 24 plane × movement combinations each populated with dimensionality slots; assert 5 measurement units; assert no `PRIORITY_TARGETS` |
| 2 | `mtrx_functions.py` | All pure functions; unit-tested with hardcoded inputs |
| 3 | `mtrx_database.py` | All entities in build order; integration between entities tested |
| 4 | `mtrx_app.py` | `MtrxApp` controller; end-to-end flow from registration to session generation |
| 5 | Views + Leaderboards | `build_program_balance`, block progress view, `build_leaderboard`; VOLUME-only filter in place |
| 6 | Persistence | JSON serialization of full state; `SCHEMA_VERSION = 2` |
| 7 | Competitive Platform | Scoring, handicapping, radar grid *(V2)* |
| 8 | AI Visualization Layer | Tool manifest, notebook templates, agentic modification *(V2)* |

---

## Key Cross-Cutting Invariants

- **`deepcopy` on user creation** — category plan preset must be deep-copied; shallow copy shares mutable lists across users.
- **Parent weight never stored** — always `sum(cat['weight'] for cat in cell['categories'])`; prevents sync errors.
- **Records flat list** — `pd.DataFrame(records)` is the universal aggregation entry point; never nest by user or date.
- **`today` always explicit** — no `datetime.date.today()` inside pure functions; enables deterministic back-testing.
- **Exercise names immutable** — records reference exercises by name; use `merge_exercises` to consolidate duplicates rather than rename.
- **Plan history on every plan change** — `save_config_snapshot` is called inside `update_matrix_cell` and `add_category`, not by the caller.
- **No business logic in `MtrxApp`** — orchestration only; all computation delegated to `mtrx_functions`.
