

# MTRX_UPDATES.md — Draft

---

```markdown
# MTRX — TDS Update Specification

This document specifies all changes to `TDS_MTRX.py` required to bring the
system from its current state (a backward-looking fitness accounting system)
to its desired state (a fitness accounting system with an adaptive
forward-looking prescription engine and a competitive platform layer).

The developer reading this should have already read `TDS_MTRX.py` in full.
Every change below references the existing section it modifies, or declares
itself as net-new. Changes are grouped by type: MODIFY, REMOVE, ADD.

---

## System Identity (Context for All Changes)

The system is fundamentally a **fitness accounting system** — analogous to a
solver equation in a spreadsheet. It records all actual training activity
regardless of plan alignment, then continuously recalculates forward-looking
recommendations based on the current state of the user's matrix intent vs.
what has actually been done. Each week is a fresh accounting period. The
system does not penalize deviation — it absorbs reality and recalibrates.

An LLM integration layer (Claude with tool calling / MCPs) will sit above
the Python system. The LLM uses the prescription engine's output as callable
tool data and presents it conversationally. The Python layer produces
deterministic, structured outputs; the LLM layer makes them accessible. This
document specifies only the Python layer.

---

## MODIFY: Section 1.4 — DEFAULT_MATRIX_GRID → PRESET_MATRIX_CONFIGS

### Current State

One `DEFAULT_MATRIX_GRID` dict. Every user is seeded from it.

### Desired State

Replace `DEFAULT_MATRIX_GRID` with `PRESET_MATRIX_CONFIGS`: a dict of named
preset configurations, each representing a distinct fitness goal archetype.

```python
PRESET_MATRIX_CONFIGS = {
    'GPP': {
        'name': 'General Physical Preparedness',
        'description': 'Balanced across all planes and movement types.',
        'grid': {
            ('Sagittal',   'Accessory/Isolation'): 'Low',
            ('Sagittal',   'Carry/Bracing'):       'High',
            ('Sagittal',   'Gait/Locomotion'):     'High',
            ('Sagittal',   'Hinge'):               'High',
            ('Sagittal',   'Pull'):                'High',
            ('Sagittal',   'Push'):                'High',
            ('Sagittal',   'Rotation'):            'N/A',
            ('Sagittal',   'Squat'):               'High',
            # ... all 32 cells
        },
    },
    # Additional presets to be defined:
    # 'STRENGTH':      {...},
    # 'HYPERTROPHY':   {...},
    # 'POWERLIFTING':  {...},
    # 'FUNCTIONAL':    {...},
    # Each preset is a complete 32-cell grid with its own priority weightings.
}

DEFAULT_PRESET = 'GPP'
```

The current `DEFAULT_MATRIX_GRID` values become the `'GPP'` preset's grid.

### Downstream Impact

- `add_user` (Section 3.1): Seeding changes from `dict(DEFAULT_MATRIX_GRID)`
  to `dict(PRESET_MATRIX_CONFIGS[preset_key]['grid'])` where `preset_key` is
  provided at registration or defaults to `DEFAULT_PRESET`.
- `MULTI_USER_BOUNDARY_TABLE` (Section 7): Update the "Default Matrix Grid"
  row to reflect that presets are shared but per-user copies are made from a
  selected preset, not a single default.
- `serialize` / `deserialize`: No structural change — `__matrix_plans` still
  stores `dict[int, dict[tuple, str]]` per user. The preset key should be
  recorded on the user's configuration ledger (see MODIFY: Section 3.1).

---

## ADD: Section 1.7 — Personal Constraints

### Rationale

The matrix expresses general strategy via cell priorities. But users have
specific goals that don't map cleanly to a single cell's priority level.
Example: "I want big biceps — 2× per week" maps to Sagittal Accessory, but
that cell may also serve other accessory work. Stacking multiple specific
goals into one cell's priority value loses the intent.

### Specification

```python
# Personal constraints supplement the matrix. Each constraint names a
# specific cell and defines a weekly target and purpose independent of
# the cell's base priority. The prescription engine honors these alongside
# the matrix grid.
#
# Structure: list of dicts per user, stored on the user's configuration
# ledger (Section 3.1).
#
# Example:
# [
#     {
#         'cell': ('Sagittal', 'Accessory/Isolation'),
#         'purpose': 'Bicep isolation',
#         'weekly_target': 2,
#         'exercise_filter': ['Barbell Curl', 'Dumbbell Curl', 'Cable Curl'],
#     },
#     {
#         'cell': ('Transverse', 'Rotation'),
#         'purpose': 'Golf swing mobility',
#         'weekly_target': 1,
#         'exercise_filter': [],   # empty = any exercise in this cell qualifies
#     },
# ]
#
# DESIGN NOTE: The structure chosen here is a rules layer that supplements
# the matrix rather than sub-accounts within cells. This keeps the matrix
# grid clean (32 cells, each with one priority) and layers personal goals
# as explicit named constraints. The prescription engine treats these as
# additional allocation targets when computing remaining weekly value.
#
# OPEN QUESTION: If a personal constraint's weekly_target exceeds or
# conflicts with the cell's base priority allocation, which takes
# precedence? The current intent is that personal constraints are additive
# — they represent demand on top of the matrix, not a replacement for it.
# The prescription engine sums both when determining what to recommend.
```

### Downstream Impact

- `mtrx_constants.py`: No new constants needed — personal constraints are
  user-defined data, not system-wide constants.
- `mtrx_database.py`: Personal constraints are stored as part of the user's
  configuration ledger (Section 3.1 below).
- Prescription engine (new Section 4.11): Must read personal constraints and
  treat them as additional allocation targets.

---

## MODIFY: Section 3.1 — Users → User Configuration Ledger

### Current State

```python
self.__users: dict[int, dict]
# Each user: {'username', 'display_name', 'email', 'join_date'}
```

User profile is a single mutable record. Contains only identity fields.

### Desired State

The user entity splits into two concerns:

**A) User Identity (unchanged structure, expanded fields)**

```python
self.__users: dict[int, dict]

# Example state:
# {
#     1: {
#         'username':            'kharmer',
#         'display_name':        'Kai Harmer',
#         'email':               'kai@example.com',
#         'join_date':           datetime.date(2026, 1, 5),
#         'age':                 38,
#         'training_experience': 10,   # years
#     },
# }
```

New fields `age` and `training_experience` are added. These are relevant to
the eventual handicap/competition layer. Additional fields may be added as
the handicap formula is defined — the structure accommodates this naturally.

`add_user` signature expands:

```python
def add_user(self, username: str, display_name: str, email: str,
             age: int = None, training_experience: int = None) -> int:
```

`age` and `training_experience` are optional at registration (nullable).

**B) Configuration Ledger (new entity)**

```python
self.__config_ledger: dict[int, list[dict]]

# Example state:
# {
#     1: [
#         {
#             'config_id':           1,
#             'effective_date':      datetime.date(2026, 1, 5),
#             'preset_key':          'GPP',
#             'days_per_week':       5,
#             'exercises_per_session': 8,
#             'personal_constraints': [
#                 {
#                     'cell': ('Sagittal', 'Accessory/Isolation'),
#                     'purpose': 'Bicep isolation',
#                     'weekly_target': 2,
#                     'exercise_filter': ['Barbell Curl', 'Dumbbell Curl'],
#                 },
#             ],
#         },
#         {
#             'config_id':           2,
#             'effective_date':      datetime.date(2026, 3, 9),
#             'preset_key':          'STRENGTH',
#             'days_per_week':       4,
#             'exercises_per_session': 6,
#             'personal_constraints': [],
#         },
#     ],
# }
```

This is a time-series ledger — like a budget. Each entry records "what we
were aiming for starting on this date." The actual workout records show
where you hit. The prescription engine always reads the most recent
configuration (last entry in the list). Historical entries are never
mutated — they are the audit trail of strategic evolution.

**Sort invariant**: Maintained ascending by `effective_date`, same pattern
as `__measurements`.

**Methods:**

```python
def add_config(self, user_id: int, effective_date: datetime.date,
               preset_key: str, days_per_week: int,
               exercises_per_session: int,
               personal_constraints: list = None) -> int:
    # 1. Validate user_id exists
    # 2. Validate preset_key in PRESET_MATRIX_CONFIGS
    # 3. Validate days_per_week > 0, exercises_per_session > 0
    # 4. config_id = self.__config_counter
    # 5. entry = {'config_id': config_id, 'effective_date': effective_date,
    #             'preset_key': preset_key, 'days_per_week': days_per_week,
    #             'exercises_per_session': exercises_per_session,
    #             'personal_constraints': personal_constraints or []}
    # 6. self.__config_ledger[user_id].append(entry)
    # 7. Re-sort by effective_date ascending
    # 8. Copy preset grid into __matrix_plans[user_id] so the user starts
    #    with the preset's priorities (user can still update_matrix_cell
    #    after this to fine-tune)
    # 9. self.__config_counter += 1
    # 10. return config_id

def get_active_config(self, user_id: int,
                      as_of: datetime.date = None) -> dict:
    # Returns the most recent config where effective_date <= as_of.
    # If as_of is None, uses the last entry (current config).
    # Same scan pattern as get_bodyweight_on_date.

def get_config_ledger(self, user_id: int) -> list:
    # Returns full history (list of dicts, copies).
```

### Downstream Impact

- `__init__`: Add `self.__config_counter = 1` and
  `self.__config_ledger = {}`.
- `add_user`: Initialize `self.__config_ledger[user_id] = []`. The first
  `add_config` call populates both the ledger and `__matrix_plans`.
- `serialize` / `deserialize`: Add `config_ledger` to the schema. Tuple
  keys in `personal_constraints[n]['cell']` use the same `'|'.join()`
  pattern as `__matrix_plans`. Increment `SCHEMA_VERSION`.
- `MULTI_USER_BOUNDARY_TABLE`: Add row for Configuration Ledger
  (per user, time-series).
- `MtrxApp.__repr__`: Consider surfacing active config info.

---

## MODIFY: Section 7.2 — Program Calendar (5-Week Blocks)

### Current State

`get_block_label` defaults to `weeks_per_block=4`. No concept of a
structurally distinct week within a block.

### Desired State

Blocks are 5 weeks. `weeks_per_block` default changes from 4 to 5.
A new function identifies the week's role within the block.

```python
def get_block_label(target_date: datetime.date,
                    weeks_per_block: int = 5) -> str:
    """
    Returns 'Round 2 | Week 3' style label.
    """
    days_offset   = (target_date - PROGRAM_START_DATE).days
    week_number   = days_offset // 7
    block_number  = (week_number // weeks_per_block) + 1
    week_in_block = (week_number % weeks_per_block) + 1
    return f'Round {block_number} | Week {week_in_block}'


def get_week_role(target_date: datetime.date,
                  weeks_per_block: int = 5) -> str:
    """
    Returns 'strategic' for weeks 1-4 or 'assessment' for week 5.

    Weeks 1-4: The prescription engine operates in full strategic mode —
    inter/intraleaving of matrix cells, exercise variations, and stimulus
    rotation are actively optimized.

    Week 5: Assessment week. Its purpose is determined by context and need:
    evaluate whether the program is working, adjust matrix configuration for
    the next block, focus on goal-specific work, or recover. The prescription
    engine may still produce output, but the week is structurally distinct.
    """
    days_offset   = (target_date - PROGRAM_START_DATE).days
    week_number   = days_offset // 7
    week_in_block = (week_number % weeks_per_block) + 1

    if week_in_block <= 4:
        return 'strategic'
    else:
        return 'assessment'
```

### Downstream Impact

- `build_program_balance` (Section 6.3): Period calculations that use
  `period_days / 7` for weekly targets should be aware of the 5-week block.
  When the period spans a full block, week 5 may have different target
  expectations.
- Prescription engine (new Section 4.11): Checks `get_week_role` to
  determine operating mode.

---

## REMOVE: Section 5 — System Behaviors (Flags)

### What to Remove

The entire Section 5, including:
- `check_intra_cell_variation` function (lines 789–824)
- `check_stimulus_interleaving` function (lines 828–851)
- Section header and docstring framing them as "stateless flag functions"

Also remove all downstream references to these flags:
- `IMPLEMENTATION_ROADMAP` Stage 2 item 7 (test instructions for both flags)
- `IMPLEMENTATION_ROADMAP` Stage 4 `log_workout` references to
  `check_intra_cell_variation` and `check_stimulus_interleaving`
- `log_workout` return value keys `repeat_exercise_flag` and
  `repeat_stimulus_flag`
- `get_all_exercises` docstring reference to `check_intra_cell_variation`

### Rationale

The flags are artifacts of a misunderstanding. Inter/intraleaving logic is
not a post-hoc warning system — it is an input to the prescription engine.
The system doesn't warn you after you repeat an exercise or stimulus; it
incorporates what you actually did and recalibrates forward. The underlying
data queries (what exercises/stimuli have been used in a cell this week)
remain valid but become internal to the prescription engine, not standalone
outputs.

### What Replaces It

The prescription engine (new Section 4.11) absorbs this logic. The queries
these functions perform — "which exercises have been used in this cell this
week" and "what stimulus was last used for this exercise" — become internal
steps within the prescription function, not public API.

---

## ADD: Section 4.11 — Adaptive Prescription Engine

### Location

After Section 4.10 (Blended Adaptation), before Section 6 (Views).
Section 5 is removed (see above), so this becomes the natural bridge
between derived metrics and views.

### Specification

```python
def build_weekly_prescription(user_id: int,
                              matrix_plan: dict,
                              personal_constraints: list,
                              records: list,
                              exercises: dict,
                              week_start: datetime.date,
                              week_end: datetime.date,
                              today: datetime.date,
                              days_per_week: int,
                              exercises_per_session: int) -> list:
    """
    Given the current state of a user's week, produces a ranked menu of
    exercise recommendations that maximize remaining value toward the
    user's matrix intent.

    CALLER CONTRACT: records is pre-filtered to this user. matrix_plan is
    the user's current matrix (from get_matrix_plan). personal_constraints
    comes from get_active_config. The caller (MtrxApp) assembles these
    inputs from the database.

    INPUTS:
        user_id:                 int
        matrix_plan:             dict[tuple, str]  — the user's 32-cell grid
        personal_constraints:    list[dict]         — from config ledger
        records:                 list[dict]         — this user's records
        exercises:               dict[str, dict]    — full exercise library
        week_start:              datetime.date
        week_end:                datetime.date
        today:                   datetime.date      — current date
        days_per_week:           int                — from config ledger
        exercises_per_session:   int                — from config ledger

    OUTPUT:
        list of dicts, ranked by descending value. Each dict:
        {
            'cell':             (str, str),      — (movement_plane, movement_type)
            'priority':         str,             — cell priority from matrix_plan
            'available_exercises': [              — filtered menu of options
                {
                    'exercise_name':      str,
                    'suggested_scheme':   str,    — canonical scheme key
                    'suggested_weight':   float | None,  — from DDM if available
                    'stimulus':           str,    — N/MT/MD/MS
                },
                ...
            ],
            'cell_value':       float,           — relative importance score
            'reason':           str,             — why this cell ranks here
        }

    LOGIC (step by step):

    1. COMPUTE TOTAL WEEKLY BUDGET
       total_slots = days_per_week * exercises_per_session
       This is the total number of exercise slots available this week.

    2. COMPUTE CELL TARGETS
       For each cell in matrix_plan:
           cell_target = PRIORITY_TARGETS[priority]
       For each personal constraint:
           Add weekly_target to the relevant cell's demand.
       Result: dict[tuple, int] mapping each cell to its total weekly
       target (base priority + personal constraints).

    3. COMPUTE CELL COVERAGE SO FAR
       Filter records to this user, this week (week_start <= date <= today).
       For each record, look up the exercise's cell via exercises dict.
       Build:
           cell_sessions:     dict[tuple, int]    — sessions completed per cell
           cell_exercises:    dict[tuple, set]     — exercise names used per cell
           cell_stimuli:      dict[tuple, set]     — stimulus types used per cell
           exercise_last_stimulus: dict[str, str]  — last stimulus per exercise

    4. COMPUTE REMAINING VALUE PER CELL
       For each cell:
           remaining = max(0, cell_target - cell_sessions)
           remaining_days = number of days from today through week_end
                            (capped at days_per_week minus days already trained)
       Weight remaining value by:
           a) Cell priority (High > Medium > Low; N/A = skip)
           b) How underserved the cell is (remaining / target ratio)
           c) Personal constraint urgency (if a constraint targets this cell
              and its weekly_target is unmet, boost its value)
       Sort cells descending by weighted value.

    5. FOR EACH CELL, BUILD EXERCISE MENU
       Get all exercises in the library for this cell:
           candidates = get_exercises_for_cell(plane, type)
       If the cell has a personal constraint with a non-empty
       exercise_filter, intersect candidates with that filter.
       For each candidate exercise:
           Determine which stimulus types have NOT been used for this
           exercise recently (exercise_last_stimulus).
           Determine which stimulus types have NOT been used in this cell
           this week (cell_stimuli).
           Prefer stimuli that satisfy both: new for the exercise AND
           new for the cell.
           For each viable stimulus, map to a canonical scheme and compute
           suggested_weight via DDM if available.
       Filter out exercises already used in this cell this week
       (cell_exercises) — prefer variety, but do not hard-exclude if no
       alternatives exist.
       Rank candidates within the cell by variety value (exercises not yet
       used this week rank higher; stimuli not yet used rank higher).

    6. ASSEMBLE OUTPUT
       Return the ranked list of cell recommendations, each with its
       filtered exercise menu. The list length is at most the number of
       remaining slots for the day (or the week, depending on caller need).

    BEHAVIORAL NOTES:

    - If the user skipped all workouts until the last day of the week, the
      function concentrates on the highest-weighted unfilled cells. The
      budget of remaining slots determines how many cells get served.

    - If the user did an off-plan workout (e.g., spontaneous powerlifting
      session), the records for that session are already logged. Step 3
      accounts for them naturally — those cells show coverage, and the
      remaining recommendations shift to what's still underserved.

    - Each week resets. The function only looks at records within
      [week_start, today] for coverage. Historical records outside this
      week are irrelevant to the current week's prescription (though they
      feed DDM via compute_ddm's 90-day lookback).

    - The output is always a MENU of options within constraints of optimal.
      The user (or the LLM layer above) picks from it. The function never
      returns a single dictated exercise.

    - This function is pure: all inputs are arguments, no side effects,
      deterministic given the same inputs. The LLM layer sits above this.

    WHY THIS IS ONE FUNCTION AND NOT SEVERAL:
    The prescription is a single computational pipeline: budget → targets →
    coverage → remaining value → exercise menus. Breaking it into smaller
    functions would require passing intermediate state between them with no
    reuse benefit — no other caller needs "cell coverage so far" in
    isolation. The steps are documented inline. If the function body exceeds
    ~80 lines, the inner steps (especially step 5) can be extracted as
    private helpers within mtrx_functions.py.
    """
    pass  # Implementation follows the steps above
```

### Downstream Impact

- `mtrx_functions.py`: This function lives here alongside the other pure
  functions. It imports `PRIORITY_TARGETS`, `CANONICAL_SCHEMES`,
  `STIMULUS_TABLE` from `mtrx_constants`.
- `mtrx_app.py`: New method `get_prescription(user_id, date)` that:
  1. Calls `get_active_config(user_id)` for days_per_week,
     exercises_per_session, personal_constraints
  2. Calls `get_matrix_plan(user_id)` for the grid
  3. Calls `get_records(user_id=user_id)` for records
  4. Calls `get_all_exercises()` for the library
  5. Calls `get_program_week_bounds(date)` for week_start/week_end
  6. Passes all of the above to `build_weekly_prescription`
  7. Returns the ranked menu
- `log_workout` return value: Remove `repeat_exercise_flag` and
  `repeat_stimulus_flag`. The return value becomes:
  ```python
  {
      'record_id':          int,
      'ddm':                float | None,
      'weight_suggestions': dict | None,
  }
  ```
- `IMPLEMENTATION_ROADMAP`: Add a new stage between Stage 2 and Stage 3
  (or after Stage 4) for the prescription engine, with test instructions.

---

## ADD: Section 8 — Competitive Platform (Intent Specification)

### Location

After Section 7, before the Implementation Roadmap.

### Specification

This section documents the competitive layer as a **planned addition with
defined intent and undefined mechanics**. No formulas, calculations, or
data structures are specified here — only the constraints the system must
eventually satisfy. This section exists so that all upstream design
decisions accommodate the competitive layer when it arrives.

```python
COMPETITIVE_PLATFORM_INTENT = """
KNOWN REQUIREMENTS:

1. DETERMINISTIC SCORING
   The scoring system will be a deterministic calculation that produces the
   same result for any matrix configuration. It is not based on adherence
   percentages or quality-of-execution deviation. The specific formula is
   not yet defined.

2. RELATIVE PERFORMANCE
   The core metric measures relative performance — how much a user moved
   the needle toward their own goal given their own constraints. Absolute
   comparisons (who lifted more) are not the basis of competition. The
   specific measurement methodology is not yet defined.

3. HANDICAP SYSTEM
   A handicap enables competition across users with fundamentally different
   objectives, strategies, time commitments, ages, experience levels, and
   starting points. The handicap adjusts scores so that a 62-year-old
   training 3 days/week for functional fitness competes fairly against a
   28-year-old training 5 days/week for powerlifting. The handicap formula
   is not yet defined.

4. PEER GROUP COMPARISON
   In addition to the handicapped leaderboard, users are compared within
   peer groups — people with similar strategy, configuration, and matrix
   selection. Analogous to industry comparables in financial analysis.
   Peer grouping criteria are not yet defined.

5. MULTI-DIMENSIONAL LEADERBOARDS
   Leaderboards are viewable across many dimensions, modeled after the
   Tour de France jersey system:
   - Yellow jersey: balanced/overall matrix leader
   - Additional jerseys for other dimensions of excellence (TBD)
   Users can view standings from multiple perspectives simultaneously.
   The specific dimensions are not yet defined.

6. RADAR GRID POSITIONING
   Each user's matrix configuration places them on a radar/spider chart
   defined by the core preset matrix configurations. This positioning
   determines:
   - Eligibility for specific challenges
   - Peer group membership for direct comparison
   - Handicap calibration inputs
   The radar grid dimensions and positioning logic are not yet defined.

7. TEMPORAL CHALLENGES
   Time-bound competitive formats layered on top of the ongoing system:
   - Monthly competitions
   - Centralities-of-effort challenges (concentrated effort windows)
   - Other structured events
   Challenge formats and eligibility rules are not yet defined.

DATA MODEL IMPLICATIONS (for upstream design):
- User identity (Section 3.1) carries age and training_experience now.
  Additional handicap-relevant fields may be added later.
- Configuration ledger (Section 3.1) records strategy over time, which
  feeds the radar grid positioning.
- Workout records (Section 3.4) are the raw input to any scoring formula.
- Preset matrix configs (Section 1.4) define the axes of the radar grid.
- All of the above are already in place or specified in this update
  document. No additional structural changes are needed to accommodate the
  competitive layer — it will be built on top of existing data.
"""
```

### Downstream Impact

None at this time. This section is a structural placeholder. When the
competitive mechanics are defined, they will produce new constants (scoring
parameters), new functions (scoring calculations, handicap formula,
leaderboard builders), new database entities (scores, leaderboards), and
new app methods. The data model is ready for them.

---

## MODIFY: Implementation Roadmap

### Changes to Existing Stages

**Stage 2 — Pure Functions:**
- Remove item 7 (check_intra_cell_variation, check_stimulus_interleaving).
- Add: `build_weekly_prescription` — test with manually constructed matrix,
  records, and exercises. Test cases:
  - Empty week (no records): should recommend highest-priority cells first
  - Partially completed week: should shift to underserved cells
  - Fully completed week: should return empty or minimal list
  - Off-plan workout logged: should absorb and recalibrate
  - Personal constraints present: should honor them alongside matrix
  - Last day of week, nothing done: should concentrate on highest value

**Stage 3 — Database:**
- Add item 6: `__config_ledger` + `add_config` + `get_active_config` +
  `get_config_ledger`
  - Verify sort invariant on effective_date
  - Verify get_active_config returns correct entry for mid-ledger dates
  - Verify add_config copies preset grid into __matrix_plans

**Stage 4 — App Controller:**
- Add method: `get_prescription(user_id, date)` → assembles inputs from
  database, calls `build_weekly_prescription`, returns ranked menu
- Add method: `add_config(user_id, ...)` → `db.add_config`
- Modify `log_workout` return value: remove flag keys
- Add method: `get_config_history(user_id)` → `db.get_config_ledger`

**Stage 6 — Persistence:**
- Add `config_ledger` to `serialize` / `deserialize`
- Add `config_counter` to serialized state
- Tuple keys in personal_constraints use `'|'.join()` pattern
- Increment `SCHEMA_VERSION` to 2

### New Stage

**Stage 7 — Competitive Platform (Future)**

Not built now. Placeholder stage acknowledging that scoring, handicapping,
leaderboards, and temporal challenges will be implemented here when the
mechanics are defined. The data model from Stages 1–6 is designed to
support this without structural changes.

---

## Change Summary

| #  | Type   | Section         | Change                                                        |
|----|--------|-----------------|---------------------------------------------------------------|
| 1  | MODIFY | 1.4             | DEFAULT_MATRIX_GRID → PRESET_MATRIX_CONFIGS (named presets)   |
| 2  | ADD    | 1.7             | Personal constraints specification                            |
| 3  | MODIFY | 3.1             | Expand user fields; add configuration ledger entity + methods |
| 4  | MODIFY | 3.5             | Seeding reads from selected preset, not single default        |
| 5  | REMOVE | 5 (entire)      | Remove flag functions and all references                      |
| 6  | ADD    | 4.11            | Adaptive prescription engine (build_weekly_prescription)      |
| 7  | MODIFY | 7.2             | 5-week blocks; add get_week_role function                     |
| 8  | ADD    | 8               | Competitive platform intent (placeholder, no mechanics)       |
| 9  | MODIFY | Roadmap         | Update stages 2–6; add stage 7 placeholder                   |
| 10 | MODIFY | 4 (log_workout) | Remove flag keys from return value                            |
```

---

That's the full draft. Want me to push this to the repo, or do you want to review / revise any sections first?