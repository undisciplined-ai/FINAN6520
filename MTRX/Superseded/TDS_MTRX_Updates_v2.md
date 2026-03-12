# MTRX — TDS Update Specification v2

This document specifies all changes to `TDS_MTRX.py` required to bring the
system from its current state (a backward-looking training tracking system)
to its desired state (a training management system with an adaptive
forward-looking prescription engine, a competitive platform layer, and an
AI-driven data access and visualization layer).

The developer reading this should have already read `TDS_MTRX.py` in full.
Every change below references the existing section it modifies, or declares
itself as net-new. Changes are grouped by type: MODIFY, REMOVE, ADD.

---

## System Identity

The system tracks movement training against a user-defined plan, generates forward-looking session recommendations, and continuously recalibrates as sessions are completed. The Python layer produces deterministic, structured outputs. An LLM integration layer sits above it, consuming the Python layer's output as callable tool data and presenting it conversationally.

### Design Philosophy

The training plan is a living target, not a rigid schedule. Each training week resets. Deviation from plan is absorbed and redistributed — a skipped session shifts remaining volume across remaining days; an off-plan workout is logged and reduces the corresponding cell's remaining need. The prescription engine continuously recalculates from the delta between what was planned and what was completed. The system does not penalize deviation; it recalibrates.

---

## MODIFY: Section 1.4 — Matrix Structure

### Remove Neutral Plane

The current 4×8 grid (32 cells) becomes a 3×8 grid (24 cells). The Neutral
plane is removed. All 8 Neutral cells in `DEFAULT_MATRIX_GRID` are set to
`'N/A'` — they carry no exercises and serve no tracking purpose.

Exercises that do not map to Sagittal, Frontal, or Transverse receive a new
parent cell in the matrix rather than being assigned to a catch-all plane.
The hierarchical structure (below) supports adding parent cells without
structural change.

### Hierarchical Cell Structure

The current flat `dict[tuple, str]` mapping each `(plane, type)` to a priority
string is replaced by a hierarchical parent/category model.

```python
# Each cell is a parent node. Its weight is always the sum of its children.
# Categories carry individual weights and declare their own measurement unit.
# Resolution increases by adding children — no structural change at the parent.
#
# Structure per user:
#   dict[tuple, dict]
#   Key:   (movement_plane, movement_type)
#   Value: {
#       'categories': [
#           {
#               'name':             str,       # e.g. 'Vertical Press'
#               'weight':           int,       # category weight
#               'measurement_unit': str,       # key from MEASUREMENT_UNITS
#               'exercise_examples': list[str], # reference only, not enforced
#           },
#           ...
#       ],
#   }
#
# Parent weight = sum(cat['weight'] for cat in cell['categories'])
# Parent weight is never stored — always derived. This eliminates sync errors.
#
# Example:
# {
#     ('Sagittal', 'Push'): {
#         'categories': [
#             {'name': 'Vertical Press',   'weight': 3, 'measurement_unit': 'VOLUME',
#              'exercise_examples': ['Overhead Press', 'Push Press']},
#             {'name': 'Horizontal Press', 'weight': 3, 'measurement_unit': 'VOLUME',
#              'exercise_examples': ['Bench Press', 'Floor Press']},
#             {'name': 'Downward Press',   'weight': 1, 'measurement_unit': 'VOLUME',
#              'exercise_examples': ['Dips', 'Decline Press']},
#         ],
#     },
#     ('Sagittal', 'Carry/Bracing'): {
#         'categories': [
#             {'name': 'Loaded Carry',  'weight': 2, 'measurement_unit': 'LOAD_DISTANCE',
#              'exercise_examples': ['Farmer Walk', 'Front Rack Carry']},
#             {'name': 'Static Brace',  'weight': 1, 'measurement_unit': 'DURATION',
#              'exercise_examples': ['Plank', 'Dead Bug']},
#         ],
#     },
# }
```

The tuple key `(movement_plane, movement_type)` is preserved as the canonical
join key. Every downstream lookup — exercise library, records, views — continues
to use this key. The change is beneath it: what was a string (`'High'`) is now
a dict with categories.

### Measurement Unit Taxonomy

Categories declare their own measurement unit. The system cannot assume
sets × reps × weight universally — carries are measured by load × distance,
bracing by duration, locomotion by distance.

```python
MEASUREMENT_UNITS = {
    'VOLUME':        {'fields': ['sets', 'reps', 'weight'],
                      'formula': 'sets * reps * weight'},
    'DURATION':      {'fields': ['sets', 'duration_seconds'],
                      'formula': 'sets * duration_seconds'},
    'DISTANCE':      {'fields': ['distance_meters'],
                      'formula': 'distance_meters'},
    'LOAD_DISTANCE': {'fields': ['weight', 'distance_meters'],
                      'formula': 'weight * distance_meters'},
    'REPS_ONLY':     {'fields': ['sets', 'reps'],
                      'formula': 'sets * reps'},
}
```

This constant lives in `mtrx_constants.py`. The exercise library does not need
to change — the measurement unit is a property of the category, not the
exercise. The same exercise (e.g. Farmer Walk) always maps to a cell; the
category within that cell defines how the exercise's output is measured.

**Downstream impact on `add_record`**: The current record schema assumes
`sets`, `reps`, `bonus_reps`, `weight` for every record. Records logged against
categories with non-VOLUME measurement units require the fields defined in
`MEASUREMENT_UNITS[unit]['fields']`. The record schema expands to include
`duration_seconds` and `distance_meters` as nullable fields. Validation at
log time checks that the required fields for the category's unit are present.

### Initial Cell Definitions

The 24-cell matrix with initial categories per cell. 3 planes × 8
movement types. Each category lists its measurement unit. Parent weight
= sum of child weights. Resolution increases by adding children without
structural change.

Measurement unit key:
- `VOLUME` — sets × reps × weight
- `DURATION` — time under load or effort
- `DISTANCE` — distance covered
- `LOAD_DISTANCE` — weight × distance
- `REPS_ONLY` — bodyweight or unweighted repetitions

---

#### Sagittal Plane

##### Push
- Vertical Press (overhead press, push press) — `VOLUME`
- Horizontal Press (bench press, floor press) — `VOLUME`
- Downward Press (dips, decline press) — `VOLUME`

##### Pull
- Vertical Pull (pull-up, chin-up, lat pulldown) — `VOLUME`
- Horizontal Pull (barbell row, cable row, chest-supported row) — `VOLUME`

##### Squat
- Bilateral Squat (back squat, front squat, goblet squat) — `VOLUME`
- Unilateral Squat (lunge, split squat, step-up) — `VOLUME`

##### Hinge
- Bilateral Hinge (deadlift, RDL, good morning) — `VOLUME`
- Unilateral Hinge (single-leg RDL, single-leg deadlift) — `VOLUME`

##### Carry/Bracing
- Loaded Carry (farmer walk, front rack carry) — `LOAD_DISTANCE`
- Static Brace (plank, dead bug, pallof hold) — `DURATION`

##### Gait/Locomotion
- Running / Sprinting — `DISTANCE`
- Sled Push / Drag — `LOAD_DISTANCE`
- Stair / Incline — `DISTANCE`

##### Rotation
- N/A for sagittal plane (pure sagittal movement has no rotation axis)

##### Accessory/Isolation
- Arm Flexion (bicep curl variations) — `VOLUME`
- Arm Extension (tricep extension variations) — `VOLUME`
- Calf / Ankle (calf raise, tibialis raise) — `VOLUME`

---

#### Frontal Plane

##### Push
- Lateral Raise (dumbbell, cable lateral raise) — `VOLUME`
- Landmine Press (angled lateral press) — `VOLUME`

##### Pull
- Upright Row (barbell, dumbbell, cable) — `VOLUME`
- Face Pull (cable, band) — `VOLUME`

##### Squat
- Lateral Squat (cossack squat, lateral lunge) — `VOLUME`
- Curtsy Lunge — `VOLUME`

##### Hinge
- Lateral Hinge (side-bending deadlift patterns) — `VOLUME`

##### Carry/Bracing
- Suitcase Carry (single-arm loaded carry) — `LOAD_DISTANCE`
- Side Plank / Lateral Brace — `DURATION`

##### Gait/Locomotion
- Lateral Shuffle / Skater — `DISTANCE`
- Lateral Sled Drag — `LOAD_DISTANCE`

##### Rotation
- Lateral Flexion (side bend, windmill) — `VOLUME`

##### Accessory/Isolation
- Adduction (adductor machine, Copenhagen plank) — `VOLUME`
- Abduction (abductor machine, banded walks) — `VOLUME`
- Rear Delt (reverse fly, band pull-apart) — `VOLUME`

---

#### Transverse Plane

##### Push
- Rotational Press (single-arm cable press with rotation) — `VOLUME`
- Landmine Rotation Press — `VOLUME`

##### Pull
- Rotational Row (single-arm cable row with rotation) — `VOLUME`
- Woodchop Pull (high-to-low cable) — `VOLUME`

##### Squat
- Rotational Lunge (lunge with trunk rotation) — `VOLUME`
- Pivot Squat — `VOLUME`

##### Hinge
- Rotational Hinge (single-arm dumbbell snatch, rotational clean) — `VOLUME`

##### Carry/Bracing
- Offset Carry (asymmetric load carry) — `LOAD_DISTANCE`
- Anti-Rotation Hold (pallof press iso, bird dog) — `DURATION`

##### Gait/Locomotion
- Agility / Cutting (cone drills, shuttle runs) — `DISTANCE`
- Rotational Sled Work — `LOAD_DISTANCE`

##### Rotation
- Anti-Rotation (pallof press, cable chop) — `VOLUME`
- Rotational Power (med ball throw, Russian twist) — `REPS_ONLY`
- Thoracic Rotation (open book, seated rotation) — `REPS_ONLY`

##### Accessory/Isolation
- Oblique Isolation (cable twist, woodchop) — `VOLUME`
- Rotator Cuff (internal/external rotation) — `VOLUME`
- Forearm Rotation (pronation/supination) — `VOLUME`

### Preset Configs

Presets define category weights for every cell, not flat priority strings.
Each preset is a complete set of weighted categories per cell.

```python
PRESET_MATRIX_CONFIGS = {
    'GPP': {
        'name': 'General Physical Preparedness',
        'grid': {
            ('Sagittal', 'Push'): {
                'categories': [
                    {'name': 'Vertical Press',   'weight': 3, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Overhead Press', 'Push Press']},
                    {'name': 'Horizontal Press', 'weight': 3, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Bench Press', 'Floor Press']},
                    {'name': 'Downward Press',   'weight': 1, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Dips', 'Decline Press']},
                ],
            },
            # ... all 24 cells with categories and weights
        },
    },
    # Additional presets:
    # 'STRENGTH':    {...},
    # 'HYPERTROPHY': {...},
    # 'POWERLIFTING': {...},
    # 'FUNCTIONAL':  {...},
}

DEFAULT_PRESET = 'GPP'
```

The current `DEFAULT_MATRIX_GRID` values are replaced by the `'GPP'` preset.
The old `PRIORITY_TARGETS` dict (`{'High': 3, 'Medium': 2, 'Low': 1, 'N/A': 0}`)
is no longer the mechanism — category weights express the same intent with
higher resolution. `PRIORITY_TARGETS` is removed.

---

## MODIFY: Section 1.5 — Controlled Vocabulary Updates

### Remove Neutral from MOVEMENT_PLANES

```python
MOVEMENT_PLANES  = {'Sagittal', 'Frontal', 'Transverse'}
MOVEMENT_PLANES_ORDERED = ['Sagittal', 'Frontal', 'Transverse']
```

All validation checks, iteration loops, and grid-building logic that reference
`MOVEMENT_PLANES` or `MOVEMENT_PLANES_ORDERED` automatically reflect the
removal. No separate code changes needed beyond the constant definitions.

`MOVEMENT_TYPES` and `MOVEMENT_TYPES_ORDERED` are unchanged.

---

## MODIFY: Section 3.1 — Users & Plan History

### Expanded Identity Fields

```python
def add_user(self, username: str, display_name: str, email: str,
             age: int = None, training_experience: int = None) -> int:
```

`age` and `training_experience` are stored on the user record as data-only
fields. They are not inputs to any calculation, scoring, or handicap logic.

```python
# Example state after expansion:
# {
#     1: {
#         'username':            'kharmer',
#         'display_name':        'Kai Harmer',
#         'email':               'kai@example.com',
#         'join_date':           datetime.date(2026, 1, 5),
#         'age':                 38,
#         'training_experience': 10,
#     },
# }
```

### Plan History

An append-only, timestamped snapshot of the full matrix state. A new snapshot
is appended whenever any matrix modification occurs (via `update_matrix_cell`,
`add_category`, or preset change). The plan history provides plan-side data
for plan-vs-completed analysis.

No training parameters (`days_per_week`, `exercises_per_session`) are stored
in the plan history. It captures the matrix structure only.

```python
self.__plan_history: dict[int, list[dict]]

# Example state:
# {
#     1: [
#         {
#             'snapshot_id':    1,
#             'timestamp':      datetime.datetime(2026, 1, 5, 10, 0, 0),
#             'matrix_state':   { ... },  # deep copy of __matrix_plans[user_id]
#         },
#         {
#             'snapshot_id':    2,
#             'timestamp':      datetime.datetime(2026, 2, 14, 8, 30, 0),
#             'matrix_state':   { ... },
#         },
#     ],
# }
```

### Methods

```python
def save_config_snapshot(self, user_id: int) -> int:
    # 1. Validate user_id exists
    # 2. snapshot_id = self.__config_counter
    # 3. Deep copy current __matrix_plans[user_id]
    # 4. Append {'snapshot_id': snapshot_id, 'timestamp': datetime.datetime.now(),
    #            'matrix_state': deep_copy}
    # 5. self.__config_counter += 1
    # 6. return snapshot_id
    #
    # Called internally by update_matrix_cell and any method that
    # modifies the matrix structure. Not a public user action.

def get_active_config(self, user_id: int) -> dict:
    # Returns the most recent snapshot's matrix_state (last entry).
    # Returns current __matrix_plans[user_id] if no snapshots exist.

def get_plan_history(self, user_id: int) -> list:
    # Returns full plan history (list of dicts, deep copies).
```

**`__init__` changes:**
- Add `self.__config_counter = 1`
- Add `self.__plan_history = {}`
- `add_user` initializes `self.__plan_history[user_id] = []`

---

## MODIFY: Section 3.5 — Matrix Plans (Structural Change)

### Updated Data Model

`__matrix_plans` changes from `dict[int, dict[tuple, str]]` to
`dict[int, dict[tuple, dict]]` matching the hierarchical structure defined
in Section 1.4.

The inner value changes from a priority string (e.g. `'High'`) to a dict
containing `'categories'` — a list of category dicts each with `name`,
`weight`, `measurement_unit`, and `exercise_examples`.

All existing methods that read or write matrix plans are updated:

```python
def update_matrix_cell(self, user_id: int, movement_plane: str,
                       movement_type: str, categories: list) -> None:
    # 1. Validate user_id, movement_plane, movement_type
    # 2. Validate each category has required keys
    # 3. Validate measurement_unit in MEASUREMENT_UNITS for each category
    # 4. self.__matrix_plans[user_id][(movement_plane, movement_type)] = {
    #        'categories': categories
    #    }
    # 5. self.save_config_snapshot(user_id)   # trigger plan history snapshot

def add_category(self, user_id: int, movement_plane: str,
                 movement_type: str, name: str, weight: int,
                 measurement_unit: str,
                 exercise_examples: list = None) -> None:
    # Appends a category to an existing cell.
    # Triggers save_config_snapshot.

def get_matrix_plan(self, user_id: int) -> dict:
    # Returns deep copy of the hierarchical matrix.

def get_cell_weight(self, user_id: int, movement_plane: str,
                    movement_type: str) -> int:
    # Returns sum of category weights for the cell (derived, never stored).
```

### Seeding from Presets

Seeding in `add_user` changes from `dict(DEFAULT_MATRIX_GRID)` to a deep copy
of `PRESET_MATRIX_CONFIGS[preset_key]['grid']`. The `add_user` signature
expands to accept an optional `preset_key` parameter:

```python
def add_user(self, username: str, display_name: str, email: str,
             age: int = None, training_experience: int = None,
             preset_key: str = None) -> int:
    # ...
    # preset = preset_key or DEFAULT_PRESET
    # self.__matrix_plans[user_id] = deep_copy(PRESET_MATRIX_CONFIGS[preset]['grid'])
```

---

## REMOVE: Section 5 — System Behaviors (Flags)

Remove the entire Section 5, including:

- `check_intra_cell_variation` function (lines 789–824 of `TDS_MTRX.py`)
- `check_stimulus_interleaving` function (lines 828–851)
- Section header and docstring framing them as “stateless flag functions”

Also remove all downstream references:

- `IMPLEMENTATION_ROADMAP` Stage 2 item 7 (test instructions for both flags)
- `IMPLEMENTATION_ROADMAP` Stage 4 `log_workout` references to both functions
- `log_workout` return value keys `repeat_exercise_flag` and
  `repeat_stimulus_flag`
- `get_all_exercises` docstring reference to `check_intra_cell_variation`

The underlying data queries these functions perform — “which exercises have
been used in this cell this week” and “what stimulus was last used for this
exercise” — become internal steps within the prescription engine (Section
4.11). They are not standalone outputs.

---

## ADD: Section 4.11 — Prescription Engine

### Session Generation

The prescription engine generates a complete workout session. Each slot in
the session contains a primary exercise recommendation plus a short list of
variations that satisfy the same stimulus type and category. The user
modifies, swaps, or accepts recommendations in real time before or during
the session.

The output is a session, not a ranked menu of cells.

```python
def build_session(user_id: int,
                  matrix_plan: dict,
                  records: list,
                  exercises: dict,
                  block_targets: dict,
                  week_start: datetime.date,
                  week_end: datetime.date,
                  today: datetime.date) -> list:
    """
    Generates a workout session for today.

    CALLER CONTRACT: All inputs are assembled by MtrxApp from the database.
    This function is pure — no side effects, deterministic given same inputs.

    INPUTS:
        user_id:         int
        matrix_plan: dict[tuple, dict]   — hierarchical matrix with categories
        records:         list[dict]           — this user's records
        exercises:       dict[str, dict]      — full exercise library
        block_targets:   dict                 — from active training block (Section 7.2)
        week_start:      datetime.date
        week_end:        datetime.date
        today:           datetime.date

    OUTPUT:
        list of dicts, one per exercise slot in the session. Each dict:
        {
            'slot':              int,           — position in session (1-based)
            'cell':              (str, str),    — (movement_plane, movement_type)
            'category':          str,           — category name
            'measurement_unit':  str,           — from category
            'primary': {
                'exercise_name':     str,
                'suggested_scheme':  str,       — canonical scheme key
                'suggested_weight':  float | None,
                'stimulus':          str,       — N/MT/MD/MS
            },
            'variations': [
                {
                    'exercise_name':     str,
                    'suggested_scheme':  str,
                    'suggested_weight':  float | None,
                    'stimulus':          str,
                },
                ...
            ],
            'reason':            str,           — why this slot was filled this way
        }

    LOGIC:

    1. COMPUTE CATEGORY TARGETS
       For each cell in matrix_plan, for each category:
           target = category['weight']  (weekly target from the matrix)
       If block_targets specifies overrides for specific categories,
       apply those.

    2. COMPUTE COVERAGE SO FAR
       Filter records to this user, this week (week_start <= date <= today).
       For each record, look up the exercise's cell and determine which
       category it serves via the exercise library.
       Build:
           category_sessions:    dict  — sessions completed per category
           cell_exercises:       dict  — exercise names used per cell
           exercise_last_stim:   dict  — last stimulus per exercise

    3. COMPUTE REMAINING VALUE
       For each category:
           remaining = max(0, target - completed)
       Weight by category weight and remaining/target ratio.
       Sort categories descending by weighted remaining value.

    4. FILL SESSION SLOTS
       For each slot (up to the session size):
           Pick the highest-value unfilled category.
           Select a primary exercise:
               - Not already used in this cell this week (prefer variety)
               - Uses a stimulus not recently repeated for this exercise
           Select 2–3 variations from the same category that satisfy
           the same stimulus type.
           For each, compute suggested_weight via DDM if available,
           using the category's measurement_unit for field selection.

    5. RETURN SESSION
       Return the ordered list of slot dicts.
    """
    pass
```

### Category-Level Operation

The engine operates at category granularity:

- Targets are expressed in each category's measurement unit. A carry
  category's deficit is measured in load × distance, not in reps.
- Remaining value calculations handle heterogeneous units across the
  hierarchy. Categories within the same cell may have different units
  (e.g. Carry/Bracing has both `LOAD_DISTANCE` and `DURATION`).
- Exercise-to-category mapping uses the exercise library's
  `movement_plane` and `movement_type` for cell lookup, then matches
  to a category based on the exercise's characteristics.
- Variety and stimulus rotation logic (formerly in the removed flag
  functions) is internal to steps 2 and 4 above.

---

## MODIFY: Section 4 — log_workout Return Value

### Remove Flag Keys

Remove `repeat_exercise_flag` and `repeat_stimulus_flag` from the
`log_workout` return value. These flags no longer exist as standalone
concepts — the logic is internal to the prescription engine.

Updated return value:

```python
{
    'record_id':          int,
    'ddm':                float | None,
    'weight_suggestions': dict | None,
}
```

The `MtrxApp.log_workout` method:
1. Calls `db.add_record(...)` → returns `record_id`
2. Calls `compute_ddm(...)` with the user's records for this exercise
3. Calls `build_weight_guidance(...)` if DDM is available
4. Returns the dict above

No flag function calls. No flag keys.

---

## MODIFY: Section 7.2 — Training Blocks

### User-Defined Programming Periods

Remove the hardcoded `weeks_per_block=4`. Training blocks are user-defined programming periods
with explicit start dates, end dates, and goal targets.

```python
self.__training_blocks: dict[int, list[dict]]

# Example state:
# {
#     1: [
#         {
#             'block_id':     1,
#             'name':         'Spring Strength Block',
#             'start_date':   datetime.date(2026, 1, 5),
#             'end_date':     datetime.date(2026, 3, 1),
#             'targets': {
#                 ('Sagittal', 'Push'): {
#                     'Vertical Press':   {'weekly_target': 3, 'unit': 'VOLUME'},
#                     'Horizontal Press': {'weekly_target': 3, 'unit': 'VOLUME'},
#                 },
#                 ('Sagittal', 'Hinge'): {
#                     'Bilateral Hinge':  {'weekly_target': 2, 'unit': 'VOLUME'},
#                 },
#                 # ... targets for categories the user wants to emphasize
#             },
#         },
#     ],
# }
```

The programming view tracks plan vs. completed across the active block:

- **Plan**: The `targets` dict above — what the user planned to
  accomplish per category per week for this block.
- **Completed**: Derived from `records` filtered to the block's date range,
  aggregated by category and week.
- **Progress**: Weekly and cumulative completion ratios, displayed as a
  tracking view showing each category's status (ahead / on track /
  behind / not started).

**Methods:**

```python
def add_training_block(self, user_id: int, name: str,
                       start_date: datetime.date, end_date: datetime.date,
                       targets: dict) -> int:
    # 1. Validate user_id exists
    # 2. Validate end_date > start_date
    # 3. Validate target categories exist in user's matrix_plan
    # 4. Validate measurement units match category definitions
    # 5. Append to self.__training_blocks[user_id]
    # 6. Return block_id

def get_active_block(self, user_id: int,
                     as_of: datetime.date = None) -> dict | None:
    # Returns the block where start_date <= as_of <= end_date.
    # Returns None if no block covers the date.

def get_block_progress(self, user_id: int, block_id: int) -> dict:
    # Returns plan vs. completed for each category in the block,
    # broken down by week.
```

**`__init__` changes:**
- Add `self.__block_counter = 1`
- Add `self.__training_blocks = {}`
- `add_user` initializes `self.__training_blocks[user_id] = []`

The existing `get_block_label` function is retained for display labeling
but its `weeks_per_block` parameter becomes informational, not structural.
Blocks are no longer derived from arithmetic on `PROGRAM_START_DATE`.

---

## ADD: Section 8 — Competitive Platform (Intent Specification)

> **Version 2:** This section is under development and will be implemented after Version 1 is complete.

This section defines the constraints the competitive layer must satisfy.
No formulas, data structures, or calculations are specified. The data model
from preceding sections is sufficient to support all requirements when
the mechanics are defined.

### Deterministic Scoring

The scoring system produces the same result for any matrix configuration
given the same inputs. It is not based on adherence percentages or
quality-of-execution deviation.

### Relative Performance

The core metric measures relative performance — how much a user moved
toward their own goal given their own constraints. Absolute comparisons
(who lifted more) are not the basis of competition.

### Handicap System

A handicap enables competition across users with fundamentally different
objectives, strategies, time commitments, ages, experience levels, and
starting points. The handicap adjusts scores so that a 62-year-old
training 3 days/week for functional fitness competes fairly against a
28-year-old training 5 days/week for powerlifting.

### Peer Group Comparison

Users are compared within peer groups — people with similar strategy,
configuration, and matrix selection.

### Multi-Dimensional Leaderboards

Leaderboards are viewable across many dimensions, using a multi-tier
jersey format:
- Yellow jersey: balanced/overall matrix leader
- Additional jerseys for other dimensions of excellence (TBD)

Users view standings from multiple perspectives simultaneously.
Leaderboards are filterable by lift, category, cell, plane, and
user-defined dimensions.

### Radar Grid Positioning

Each user's matrix configuration places them on a radar/spider chart
defined by the preset matrix configurations. This positioning determines:
- Eligibility for specific challenges
- Peer group membership for direct comparison
- Handicap calibration inputs

### Temporal Challenges

Time-bound competitive formats layered on top of the ongoing system:
- Monthly competitions
- Centralities-of-effort challenges (concentrated effort windows)
- Other structured events

### Data Model Dependencies

- User identity (Section 3.1) carries `age` and `training_experience`.
- Plan history (Section 3.1) records strategy over time, feeding
  radar grid positioning.
- Workout records (Section 3.4) are the raw input to any scoring formula.
- Preset matrix configs (Section 1.4) define the axes of the radar grid.
- Training blocks (Section 7.2) provide the plan-vs-completed structure
  that scoring formulas can reference.

---

## ADD: Section 9 — Data Access & Visualization Layer

> **Version 2:** This section is under development and will be implemented after Version 1 is complete.

### API Connection Points

The Python layer exposes structured, well-defined methods optimized for
AI agent consumption. Every data entity and derived metric is accessible
through a consistent interface that returns JSON-serializable dicts or
lists. The API surface is designed so that an LLM with tool-calling
capability can discover, query, and combine data without custom glue code.

Key design constraints:
- Every public method on `MtrxApp` is a potential tool endpoint.
- Return types are always `dict`, `list[dict]`, or `pd.DataFrame`
  (convertible to dict via `.to_dict()`).
- Method names and parameter names are self-documenting for LLM tool
  descriptions.
- No method requires understanding internal state to call correctly.

### AI-Driven Jupyter Notebook Integration

An LLM agent navigates the data access layer to generate Jupyter notebook
cells containing charts, graphs, gap analysis, and natural language
recommendations. The agent is not a feature-per-dataset tool — it is a
general analyst that can combine any available data.

Capabilities:
- Query any combination of records, matrix state, measurements,
  configuration history, block progress, and prescription output.
- Generate visualizations using matplotlib, plotly, or other libraries
  available in the notebook environment.
- Produce natural language interpretation of data (trends, gaps,
  recommendations) alongside the visualizations.
- Respond to freeform user questions about their training data.

### Dynamic Filtering & Complex Visualizations

All data views support dynamic filtering:
- Leaderboards filterable by lift, category, cell, plane, peer group,
  time period, and user-defined dimensions.
- Historical data viewable at any granularity (session, week, block,
  all-time).
- Matrix history (from plan history) visualized as strategy evolution
  over time.
- Body metrics (from measurements) overlaid with training volume and
  performance trends.

The Python layer provides the filtering and aggregation logic. The
notebook environment handles rendering.

### Agentic Programming Modification

The visualization agent can modify user programming based on its analysis:
- Adjust category weights in the matrix.
- Create or modify training blocks.
- Suggest prescription engine parameter changes.

All modifications flow through the same `MtrxApp` methods used by direct
user interaction. The agent does not bypass the data access layer — it
uses the same API surface, ensuring all validation, plan history snapshots,
and invariants are maintained.

---

## MODIFY: Implementation Roadmap

### Stage 1 — Constants

**Changes from original:**
- Replace `DEFAULT_MATRIX_GRID` with `PRESET_MATRIX_CONFIGS` (hierarchical
  category structure, GPP preset fully defined).
- Add `MEASUREMENT_UNITS` constant (5 measurement types with fields and
  formulas).
- Remove `'Neutral'` from `MOVEMENT_PLANES` and `MOVEMENT_PLANES_ORDERED`.
- Add `DEFAULT_PRESET = 'GPP'`.

**Test:** Import the file. Print `PRESET_MATRIX_CONFIGS['GPP']['grid']` and
verify all 24 cells are present with categories. Print `MEASUREMENT_UNITS`.
Verify `'Neutral'` is absent from `MOVEMENT_PLANES`.

### Stage 2 — Pure Functions

**Changes from original:**
- Remove item 7 (`check_intra_cell_variation`, `check_stimulus_interleaving`).
- Add `build_session` — test with manually constructed hierarchical matrix,
  records, and exercises. Test cases:
  - Empty week (no records): fills slots from highest-weight categories
  - Partially completed week: shifts to underserved categories
  - Off-plan workout logged: absorbs and recalibrates remaining slots
  - Categories with different measurement units: verify unit-appropriate
    targets and suggestions
  - Verify each slot has primary + variations from same category

**Unchanged:** Items 1–6 (classify_stimulus through compute_blended_adaptation)
are unaffected.

### Stage 3 — Database

**Changes from original:**
- Item 1 (`__users`): `add_user` signature expands with `age`,
  `training_experience`, and `preset_key` parameters.
- Item 5 (`__matrix_plans`): Seeding uses deep copy from
  `PRESET_MATRIX_CONFIGS[preset]['grid']`. `update_matrix_cell` accepts
  `categories` list. Add `add_category` method.
- Add item 6: `__plan_history` + `save_config_snapshot` +
  `get_active_config` + `get_plan_history`.
  - Verify snapshot is appended on every `update_matrix_cell` call
  - Verify `get_active_config` returns most recent snapshot
  - Verify snapshots are deep copies (mutation isolation)
- Add item 7: `__training_blocks` + `add_training_block` +
  `get_active_block` + `get_block_progress`.
  - Verify date range validation
  - Verify target categories are validated against user's matrix
  - Verify `get_block_progress` returns plan vs. completed breakdown
- Item 4 (`__records`): `add_record` schema expands with nullable
  `duration_seconds` and `distance_meters` fields. Validation checks
  required fields based on category's `measurement_unit`.

### Stage 4 — App Controller

**Changes from original:**
- `log_workout` return value: remove `repeat_exercise_flag` and
  `repeat_stimulus_flag`. Remove calls to both flag functions.
- Add method: `generate_session(user_id, date)` → assembles inputs from
  database, calls `build_session`, returns session list.
- Add method: `add_training_block(user_id, ...)` → `db.add_training_block`.
- Add method: `get_block_progress(user_id, block_id)` →
  `db.get_block_progress`.
- Add method: `get_plan_history(user_id)` → `db.get_plan_history`.
- `update_matrix_cell` now triggers `db.save_config_snapshot` internally.
- `register_user` passes `preset_key` to `db.add_user`.

**Test:** Register 2 users with different presets. Add exercises. Log workouts
including non-VOLUME measurement units. Call `generate_session`. Verify
block progress tracking. Verify plan history grows on matrix changes.

### Stage 5 — Visualization & Reports

**Changes from original:**
- Program Balance view: update from 4×8 grid to 3×8 grid (no Neutral
  plane). Display category detail within cells.
- Block Progress view: new visualization showing plan vs. completed per
  category across the active training block, with status color coding
  (ahead / on track / behind / not started).
- All views operate on the hierarchical matrix structure. Cell-level
  aggregations sum across categories.

### Stage 6 — Persistence

**Changes from original:**
- `serialize` / `deserialize`: handle hierarchical `__matrix_plans`
  structure (category dicts within each cell).
- Add `plan_history` to serialized state.
- Add `config_counter` to serialized state.
- Add `training_blocks` and `block_counter` to serialized state.
- Record schema includes nullable `duration_seconds` and `distance_meters`.
- Tuple keys in category structures use the same `'|'.join()` pattern.
- Increment `SCHEMA_VERSION` to 2.

### Stage 7 — Competitive Platform (Version 2)

Scoring, handicapping, leaderboards, and temporal challenges are implemented
in this stage when the mechanics are defined. The data model from Stages 1–6
requires no structural changes to support this stage. Deliverables:
- Scoring constants and calculation functions in `mtrx_constants.py` /
  `mtrx_functions.py`.
- Leaderboard and peer group entities in `mtrx_database.py`.
- Leaderboard views and radar grid visualization in `mtrx_app.py`.

### Stage 8 — AI Visualization Layer (Version 2)

The AI-driven data access and visualization layer is implemented in this
stage. Deliverables:
- Ensure all `MtrxApp` methods return JSON-serializable structures suitable
  for LLM tool-calling.
- Build Jupyter notebook templates for common analyses.
- Define the agent’s tool manifest (method names, parameter schemas,
  return types) for LLM integration.
- Implement agentic programming modification flows (matrix adjustment,
  block creation) through the existing API surface.

---

## Change Summary

| #  | Type   | Section         | Change                                                                  |
|----|--------|-----------------|-------------------------------------------------------------------------|
| 1  | MODIFY | 1.4             | Hierarchical category structure (24 cells, weighted categories)         |
| 2  | ADD    | 1.4             | Measurement unit taxonomy (VOLUME, DURATION, DISTANCE, LOAD_DISTANCE, REPS_ONLY) |
| 3  | MODIFY | 1.4             | PRESET_MATRIX_CONFIGS replaces DEFAULT_MATRIX_GRID                      |
| 4  | REMOVE | 1.4             | Neutral plane removed (32 cells → 24 cells)                            |
| 5  | MODIFY | 1.5             | Remove Neutral from MOVEMENT_PLANES and MOVEMENT_PLANES_ORDERED         |
| 6  | MODIFY | 3.1             | Add age and training_experience to user identity (data-only)            |
| 7  | ADD    | 3.1             | Plan history (append-only matrix snapshots)                             |
| 8  | MODIFY | 3.4             | Record schema expands with duration_seconds and distance_meters         |
| 9  | MODIFY | 3.5             | Matrix plans use hierarchical category structure                        |
| 10 | REMOVE | 5 (entire)      | Remove flag functions and all references                                |
| 11 | ADD    | 4.11            | Prescription engine (build_session — full session generation)           |
| 12 | MODIFY | 4 (log_workout) | Remove flag keys from return value                                      |
| 13 | MODIFY | 7.2             | User-defined training blocks replace hardcoded week arithmetic          |
| 14 | ADD    | 8               | Competitive platform intent specification                               |
| 15 | ADD    | 9               | Data access & visualization layer (AI-driven Jupyter integration)       |
| 16 | MODIFY | Roadmap         | Update stages 1–6; add stages 7–8                                       |
