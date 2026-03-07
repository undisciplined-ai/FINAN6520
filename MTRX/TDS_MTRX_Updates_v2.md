# MTRX — TDS Update Specification v2

This document specifies all changes to `TDS_MTRX.py` required to bring the
system from its current state (a backward-looking fitness accounting system)
to its desired state (a fitness accounting system with an adaptive
forward-looking prescription engine, a competitive platform layer, and an
AI-driven data access and visualization layer).

The developer reading this should have already read `TDS_MTRX.py` in full.
Every change below references the existing section it modifies, or declares
itself as net-new. Changes are grouped by type: MODIFY, REMOVE, ADD.

---

## System Identity

The system is a **fitness accounting system**. It operates on a budget-vs-actual
model: the matrix defines the budget (what the user intends to train), workout
records capture the actual (what was done), and the prescription engine
continuously recalculates forward-looking recommendations from the delta.

Each accounting period (week) resets. The system does not penalize deviation
from plan — it absorbs reality and recalibrates. A skipped session redistributes
remaining budget across remaining days. An off-plan workout is recorded as
actual activity and reduces the corresponding cell's remaining need.

The Python layer produces deterministic, structured outputs. An LLM integration
layer sits above it, consuming the Python layer's output as callable tool data
and presenting it conversationally.

---

## MODIFY: Section 1.4 — Matrix Structure (Chart of Accounts)

### Remove Neutral Plane

The current 4×8 grid (32 cells) becomes a 3×8 grid (24 cells). The Neutral
plane is removed. All 8 Neutral cells in `DEFAULT_MATRIX_GRID` are set to
`'N/A'` — they carry no exercises and serve no tracking purpose.

Exercises that do not map to Sagittal, Frontal, or Transverse receive a new
parent account in the matrix rather than being assigned to a catch-all plane.
The hierarchical structure (below) supports adding parent accounts without
structural change.

### Hierarchical Cell Structure

The current flat `dict[tuple, str]` mapping each `(plane, type)` to a priority
string is replaced by a hierarchical parent/sub-account model.

```python
# Each cell is a parent account. Its weight is always the sum of its children.
# Sub-accounts carry individual weights and declare their own measurement unit.
# Resolution increases by adding children — no structural change at the parent.
#
# Structure per user:
#   dict[tuple, dict]
#   Key:   (movement_plane, movement_type)
#   Value: {
#       'sub_accounts': [
#           {
#               'name':             str,       # e.g. 'Vertical Press'
#               'weight':           int,       # sub-account weight
#               'measurement_unit': str,       # key from MEASUREMENT_UNITS
#               'exercise_examples': list[str], # reference only, not enforced
#           },
#           ...
#       ],
#   }
#
# Parent weight = sum(sa['weight'] for sa in cell['sub_accounts'])
# Parent weight is never stored — always derived. This eliminates sync errors.
#
# Example:
# {
#     ('Sagittal', 'Push'): {
#         'sub_accounts': [
#             {'name': 'Vertical Press',   'weight': 3, 'measurement_unit': 'VOLUME',
#              'exercise_examples': ['Overhead Press', 'Push Press']},
#             {'name': 'Horizontal Press', 'weight': 3, 'measurement_unit': 'VOLUME',
#              'exercise_examples': ['Bench Press', 'Floor Press']},
#             {'name': 'Downward Press',   'weight': 1, 'measurement_unit': 'VOLUME',
#              'exercise_examples': ['Dips', 'Decline Press']},
#         ],
#     },
#     ('Sagittal', 'Carry/Bracing'): {
#         'sub_accounts': [
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
a dict with sub-accounts.

### Measurement Unit Taxonomy

Sub-accounts declare their own measurement unit. The system cannot assume
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
to change — the measurement unit is a property of the sub-account, not the
exercise. The same exercise (e.g. Farmer Walk) always maps to a cell; the
sub-account within that cell defines how the exercise's output is measured.

**Downstream impact on `add_record`**: The current record schema assumes
`sets`, `reps`, `bonus_reps`, `weight` for every record. Records logged against
sub-accounts with non-VOLUME measurement units require the fields defined in
`MEASUREMENT_UNITS[unit]['fields']`. The record schema expands to include
`duration_seconds` and `distance_meters` as nullable fields. Validation at
log time checks that the required fields for the sub-account's unit are present.

### V1 Chart of Accounts

The 24-cell matrix with initial sub-accounts per cell. 3 planes × 8
movement types. Each sub-account lists its measurement unit. Parent weight
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

Presets define sub-account weights for every cell, not flat priority strings.
Each preset is a complete chart of accounts with weighted sub-accounts.

```python
PRESET_MATRIX_CONFIGS = {
    'GPP': {
        'name': 'General Physical Preparedness',
        'grid': {
            ('Sagittal', 'Push'): {
                'sub_accounts': [
                    {'name': 'Vertical Press',   'weight': 3, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Overhead Press', 'Push Press']},
                    {'name': 'Horizontal Press', 'weight': 3, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Bench Press', 'Floor Press']},
                    {'name': 'Downward Press',   'weight': 1, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Dips', 'Decline Press']},
                ],
            },
            # ... all 24 cells with sub-accounts and weights
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
is no longer the mechanism — sub-account weights express the same intent with
higher resolution. `PRIORITY_TARGETS` may be retained as a reference mapping
for backward compatibility during migration but is not used by the prescription
engine.

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

## MODIFY: Section 3.1 — Users & Configuration Ledger

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

### Configuration Ledger

An append-only, timestamped snapshot of the full matrix state. A new snapshot
is appended whenever any matrix modification occurs (via `update_matrix_cell`,
`add_sub_account`, or preset change). The ledger provides the budget-side
historical data for budget-vs-actual analysis.

No training parameters (`days_per_week`, `exercises_per_session`) are stored
on the ledger. It captures the matrix structure only.

```python
self.__config_ledger: dict[int, list[dict]]

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

def get_config_ledger(self, user_id: int) -> list:
    # Returns full snapshot history (list of dicts, deep copies).
```

**`__init__` changes:**
- Add `self.__config_counter = 1`
- Add `self.__config_ledger = {}`
- `add_user` initializes `self.__config_ledger[user_id] = []`

---

## MODIFY: Section 3.5 — Matrix Plans (Structural Change)

### Updated Data Model

`__matrix_plans` changes from `dict[int, dict[tuple, str]]` to
`dict[int, dict[tuple, dict]]` matching the hierarchical structure defined
in Section 1.4.

The inner value changes from a priority string (e.g. `'High'`) to a dict
containing `'sub_accounts'` — a list of sub-account dicts each with `name`,
`weight`, `measurement_unit`, and `exercise_examples`.

All existing methods that read or write matrix plans are updated:

```python
def update_matrix_cell(self, user_id: int, movement_plane: str,
                       movement_type: str, sub_accounts: list) -> None:
    # 1. Validate user_id, movement_plane, movement_type
    # 2. Validate each sub-account has required keys
    # 3. Validate measurement_unit in MEASUREMENT_UNITS for each sub-account
    # 4. self.__matrix_plans[user_id][(movement_plane, movement_type)] = {
    #        'sub_accounts': sub_accounts
    #    }
    # 5. self.save_config_snapshot(user_id)   # trigger ledger snapshot

def add_sub_account(self, user_id: int, movement_plane: str,
                    movement_type: str, name: str, weight: int,
                    measurement_unit: str,
                    exercise_examples: list = None) -> None:
    # Appends a sub-account to an existing cell.
    # Triggers save_config_snapshot.

def get_matrix_plan(self, user_id: int) -> dict:
    # Returns deep copy of the hierarchical matrix.

def get_cell_weight(self, user_id: int, movement_plane: str,
                    movement_type: str) -> int:
    # Returns sum of sub-account weights for the cell (derived, never stored).
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

<!-- Remove check_intra_cell_variation, check_stimulus_interleaving.
     Remove all downstream references. Logic absorbed by prescription engine. -->

---

## ADD: Section 4.11 — Prescription Engine

### Session Generation

<!-- Generates a complete workout session, not a ranked menu.
     Each slot: primary recommendation + dropdown variations
     matching same stimulus/muscle category.
     User modifies in real time before or during session. -->

### Sub-Account Level Operation

<!-- Targets expressed in each sub-account's measurement unit.
     Remaining value calculation handles heterogeneous units.
     Variety and stimulus rotation logic internal to engine. -->

---

## MODIFY: Section 4 — log_workout Return Value

### Remove Flag Keys

<!-- Remove repeat_exercise_flag and repeat_stimulus_flag. -->

---

## MODIFY: Section 7.2 — Training Blocks

### User-Defined Programming Periods

<!-- Remove hardcoded 5-week block logic.
     Blocks are user-defined with goal targets at sub-account level.
     Programming view tracks budget vs. actual across active block.
     Progress tracking analogous to FloQast month-end close view. -->

---

## ADD: Section 8 — Competitive Platform (Intent Specification)

### Deterministic Scoring
### Relative Performance
### Handicap System
### Peer Group Comparison
### Multi-Dimensional Leaderboards
### Radar Grid Positioning
### Temporal Challenges

---

## ADD: Section 9 — Data Access & Visualization Layer

### API Connection Points

<!-- Python layer exposes structured, well-defined API endpoints
     for AI agent consumption. -->

### AI-Driven Jupyter Notebook Integration

<!-- LLM agent navigates the data access layer to generate:
     charts, graphs, gap analysis, natural language recommendations.
     Not feature-per-dataset — a general data access layer. -->

### Dynamic Filtering & Complex Visualizations

<!-- Leaderboards filterable by lift, dimension, peer group.
     Historical data, matrix history, body metrics all feed same engine. -->

### Agentic Programming Modification

<!-- The visualization agent can modify user programming
     based on its analysis. -->

---

## MODIFY: Implementation Roadmap

### Stage 1 — Constants
### Stage 2 — Pure Functions
### Stage 3 — Database
### Stage 4 — App Controller
### Stage 5 — Visualization & Reports
### Stage 6 — Persistence
### Stage 7 — Competitive Platform (Future)
### Stage 8 — AI Visualization Layer (Future)

---

## Change Summary

<!-- Summary table of all changes by number, type, section, description. -->
