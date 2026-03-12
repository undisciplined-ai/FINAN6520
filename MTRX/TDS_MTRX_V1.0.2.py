"""
================================================================================
  MTRX — Technical Design Specification
================================================================================
  Version: V1.0.2
"""

# ── Document Purpose ──────────────────────────────────────────────────────────
PURPOSE = """
This document is a complete technical design specification for the MTRX training
management system. It maps every component of the system described in this
specification to the specific Python constructs, data structures, and libraries.
The resolution target is: a senior developer should be able to build the full
application using only this document, without external references.

The document is organized into nine sections mirroring the system's logical
layers, followed by an Implementation Roadmap.
"""

# ── System Identity ───────────────────────────────────────────────────────────
SYSTEM_IDENTITY = """
MTRX is a training management system with four integrated layers:

1. TRACKING LAYER — Records training sessions against a user-defined movement
   category plan. Every workout is mapped to a parent category (defined by
   movement plane and movement type) and a sub-category within it.

2. PRESCRIPTION LAYER — An adaptive, forward-looking engine that generates
   workout recommendations based on the delta between what was planned and what
   was completed. The engine recalibrates continuously as sessions are logged.

3. COMPETITIVE PLATFORM LAYER — A deterministic scoring system enabling
   relative performance comparison across users with different goals, strategies,
   training ages, and time commitments. Handicap-adjusted competition across
   peer groups.

4. AI-DRIVEN DATA ACCESS LAYER — A Python API surface optimized for LLM
   tool-calling. An AI agent consumes structured outputs from the Python layer
   and presents them conversationally, generates Jupyter notebooks, and can
   modify user programming through the same validated API surface.
"""

# ── Design Philosophy ─────────────────────────────────────────────────────────
DESIGN_PHILOSOPHY = """
The training plan is a living target, not a rigid schedule.

Each training week resets. Deviation from plan is absorbed and redistributed --
a skipped session shifts remaining volume across remaining days; an off-plan
workout is logged and reduces the corresponding category's remaining need.
The prescription engine continuously recalculates from the delta between what
was planned and what was completed.

The system does not penalize deviation; it recalibrates.
"""

# ── System Architecture Overview ──────────────────────────────────────────────
ARCHITECTURE = """
The application is organized into four files with a strict dependency hierarchy.
Each layer imports only from the layer(s) below it.

    mtrx_constants.py   <- no imports; pure data definitions
            |
    mtrx_functions.py   <- imports: mtrx_constants, datetime, math
            |
    mtrx_database.py    <- imports: mtrx_constants, mtrx_functions, datetime, json
            |
    mtrx_app.py         <- imports: mtrx_database, mtrx_functions, pandas, matplotlib

WHY THIS SEPARATION ELIMINATES ERRORS:
Every derived metric is defined once, as a pure function in mtrx_functions.py,
with explicit inputs and outputs. The database never recomputes anything -- it
stores only raw records. The app never accesses raw state directly -- it calls
database methods and passes the results to functions. A bug in any calculation
should be isolated to one function in one file.

"""


###############################################################################
# SECTION 1: SYSTEM-WIDE CONSTANTS  (mtrx_constants.py)
###############################################################################
# These values are fixed program-wide. They are never passed as arguments and
# never modified at runtime. Any function or class that needs them imports this
# module directly.

# ── 1.1 Stimulus Table ────────────────────────────────────────────────────────

STIMULUS_TABLE = {
    'N':  {'name': 'Neural',             'adaptation_days': 21, 'fatigue_days': 1, 'hex': '#00C853'},
    'MT': {'name': 'Mechanical Tension', 'adaptation_days': 56, 'fatigue_days': 3, 'hex': '#FF6A00'},
    'MD': {'name': 'Muscle Damage',      'adaptation_days': 42, 'fatigue_days': 5, 'hex': '#FF2D95'},
    'MS': {'name': 'Metabolic Stress',   'adaptation_days': 28, 'fatigue_days': 2, 'hex': '#007BFF'},
}

STIMULUS_TABLE_NOTES = """
rep_min and rep_max are intentionally absent. Stimulus classification is defined
by an ordered if/elif chain in classify_stimulus (Section 4.1) -- not by
iterating this table. Including those fields here would suggest a table-driven
classification approach to any developer reading constants before functions, and
would create a second place to update if boundaries ever changed. This table's
sole purpose is to supply adaptation_days, fatigue_days, and hex by stimulus key.
"""

# ── 1.2 Canonical Schemes ─────────────────────────────────────────────────────

CANONICAL_SCHEMES = {
    '3x5':  {'sets': 3, 'reps': 5,  'stimulus': 'MT', 'pct_of_ddm': 0.80, 'priority': 'Primary'},

    '3x10': {'sets': 3, 'reps': 10, 'stimulus': 'MD', 'pct_of_ddm': 0.65, 'priority': 'Primary'},
    '3x2':  {'sets': 3, 'reps': 2,  'stimulus': 'N',  'pct_of_ddm': 0.95, 'priority': 'Secondary'},
    '3x20': {'sets': 3, 'reps': 20, 'stimulus': 'MS', 'pct_of_ddm': 0.50, 'priority': 'Secondary'},
}

CANONICAL_SCHEMES_NOTES = """
The key structure is 'sets x reps' as a string. sets and reps are explicit
fields -- not parsed from the key string -- so compute_ddm (Section 4.8) reads
CANONICAL_SCHEMES[scheme_key]['sets'] and ['reps'] directly from the single
source of truth. DDM derivation and weight suggestion functions use
['pct_of_ddm'] directly.
"""

# ── 1.3 REMOVED IN V1.0.2 ─────────────────────────────────────────────────────
# PRIORITY_TARGETS dict and PRIORITY_OPTIONS set have been removed.
# Both are replaced by per-category weights in PRESET_MATRIX_CONFIGS (Section 1.4).
# PRIORITY_OPTIONS was used only to validate update_matrix_cell(priority: str),
# which no longer accepts a priority string -- it now accepts a categories list.

# ── 1.4 Category Structure ────────────────────────────────────────────────────
# DEFAULT_MATRIX_GRID (dict[tuple, str] mapping each (plane, type) to a priority
# string) is replaced by a hierarchical parent/category model.
#
# Structure per user (stored in __matrix_plans):
#   dict[tuple, dict]
#   Key:   (movement_plane, movement_type)   <- canonical join key, unchanged
#   Value: {
#       'categories': [
#           {
#               'name':             str,        # e.g. 'Vertical Press'
#               'weight':           int,        # category weight (0 = unset)
#               'measurement_unit': str,        # key from MEASUREMENT_UNITS
#               'exercise_examples': list[str], # reference only, not enforced
#           },
#           ...
#       ],
#   }
#
# Parent weight = sum(cat['weight'] for cat in cell['categories'])
# Parent weight is never stored -- always derived. This eliminates sync errors.
#
# The 24 parent categories correspond to the 3 planes x 8 movement types in the
# initial configuration. Additional parent categories can be appended without
# structural change -- the structure is an appendable list, not a fixed grid.
#
# The tuple key (movement_plane, movement_type) is preserved as the canonical
# join key. Every downstream lookup -- exercise library, records, views --
# continues to use this key unchanged.

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

MEASUREMENT_UNITS_NOTES = """
This constant lives in mtrx_constants.py. The exercise library does not need
to change -- the measurement unit is a property of the category, not the
exercise. The same exercise (e.g. Farmer Walk) always maps to a cell; the
category within that cell defines how the exercise's output is measured.

Downstream impact on add_record: the record schema expands to include
duration_seconds and distance_meters as nullable fields. Validation at log
time checks that the required fields for the category's measurement_unit
are present (Section 3.4).
"""

PRESET_MATRIX_CONFIGS = {

    # ── BLANK (default) ───────────────────────────────────────────────────────
    # All 24 parent categories pre-populated with sub-categories and measurement
    # units. All weights are 0 -- the user sets them after registration.
    # GPP and other named presets are stubs; their grids are defined later.
    'BLANK': {
        'name': 'Blank (No Weights)',
        'grid': {

            # ── Sagittal Plane ────────────────────────────────────────────────

            ('Sagittal', 'Push'): {
                'categories': [
                    {'name': 'Vertical Press',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Overhead Press', 'Push Press']},
                    {'name': 'Horizontal Press', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Bench Press', 'Floor Press']},
                    {'name': 'Downward Press',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Dips', 'Decline Press']},
                ],
            },
            ('Sagittal', 'Pull'): {
                'categories': [
                    {'name': 'Vertical Pull',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Pull-Up', 'Chin-Up', 'Lat Pulldown']},
                    {'name': 'Horizontal Pull', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Barbell Row', 'Cable Row', 'Chest-Supported Row']},
                ],
            },
            ('Sagittal', 'Squat'): {
                'categories': [
                    {'name': 'Bilateral Squat',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Back Squat', 'Front Squat', 'Goblet Squat']},
                    {'name': 'Unilateral Squat', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Lunge', 'Split Squat', 'Step-Up']},
                ],
            },
            ('Sagittal', 'Hinge'): {
                'categories': [
                    {'name': 'Bilateral Hinge',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Deadlift', 'RDL', 'Good Morning']},
                    {'name': 'Unilateral Hinge', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Single-Leg RDL', 'Single-Leg Deadlift']},
                ],
            },
            ('Sagittal', 'Carry/Bracing'): {
                'categories': [
                    {'name': 'Loaded Carry', 'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Farmer Walk', 'Front Rack Carry']},
                    {'name': 'Static Brace', 'weight': 0, 'measurement_unit': 'DURATION',
                     'exercise_examples': ['Plank', 'Dead Bug', 'Pallof Hold']},
                ],
            },
            ('Sagittal', 'Gait/Locomotion'): {
                'categories': [
                    {'name': 'Running / Sprinting', 'weight': 0, 'measurement_unit': 'DISTANCE',
                     'exercise_examples': ['Sprint', 'Tempo Run', 'Jog']},
                    {'name': 'Sled Push / Drag',    'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Sled Push', 'Sled Drag']},
                    {'name': 'Stair / Incline',     'weight': 0, 'measurement_unit': 'DISTANCE',
                     'exercise_examples': ['Stair Climb', 'Hill Run', 'Incline Walk']},
                ],
            },
            ('Sagittal', 'Rotation'): {
                # N/A for the sagittal plane -- pure sagittal movement has no rotation axis.
                # Cell is present for structural completeness; no sub-categories defined.
                'categories': [],
            },
            ('Sagittal', 'Accessory/Isolation'): {
                'categories': [
                    {'name': 'Arm Flexion',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Bicep Curl', 'Hammer Curl', 'Preacher Curl']},
                    {'name': 'Arm Extension', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Tricep Extension', 'Skull Crusher', 'Pushdown']},
                    {'name': 'Calf / Ankle',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Calf Raise', 'Tibialis Raise']},
                ],
            },

            # ── Frontal Plane ─────────────────────────────────────────────────

            ('Frontal', 'Push'): {
                'categories': [
                    {'name': 'Lateral Raise',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Dumbbell Lateral Raise', 'Cable Lateral Raise']},
                    {'name': 'Landmine Press', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Landmine Press', 'Angled Lateral Press']},
                ],
            },
            ('Frontal', 'Pull'): {
                'categories': [
                    {'name': 'Upright Row', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Barbell Upright Row', 'Dumbbell Upright Row', 'Cable Upright Row']},
                    {'name': 'Face Pull',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Cable Face Pull', 'Band Face Pull']},
                ],
            },
            ('Frontal', 'Squat'): {
                'categories': [
                    {'name': 'Lateral Squat', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Cossack Squat', 'Lateral Lunge']},
                    {'name': 'Curtsy Lunge',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Curtsy Lunge', 'Crossover Lunge']},
                ],
            },
            ('Frontal', 'Hinge'): {
                'categories': [
                    {'name': 'Lateral Hinge', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Side-Bending Deadlift', 'Lateral RDL']},
                ],
            },
            ('Frontal', 'Carry/Bracing'): {
                'categories': [
                    {'name': 'Suitcase Carry',            'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Single-Arm Suitcase Carry', 'Offset Farmer Walk']},
                    {'name': 'Side Plank / Lateral Brace', 'weight': 0, 'measurement_unit': 'DURATION',
                     'exercise_examples': ['Side Plank', 'Side-Lying Hip Abduction Hold']},
                ],
            },
            ('Frontal', 'Gait/Locomotion'): {
                'categories': [
                    {'name': 'Lateral Shuffle / Skater', 'weight': 0, 'measurement_unit': 'DISTANCE',
                     'exercise_examples': ['Lateral Shuffle', 'Skater Hop']},
                    {'name': 'Lateral Sled Drag',        'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Lateral Sled Drag', 'Band-Resisted Lateral Walk']},
                ],
            },
            ('Frontal', 'Rotation'): {
                'categories': [
                    {'name': 'Lateral Flexion', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Side Bend', 'Windmill', 'Cable Side Bend']},
                ],
            },
            ('Frontal', 'Accessory/Isolation'): {
                'categories': [
                    {'name': 'Adduction', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Adductor Machine', 'Copenhagen Plank']},
                    {'name': 'Abduction', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Abductor Machine', 'Banded Walk']},
                    {'name': 'Rear Delt', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Reverse Fly', 'Band Pull-Apart']},
                ],
            },

            # ── Transverse Plane ──────────────────────────────────────────────

            ('Transverse', 'Push'): {
                'categories': [
                    {'name': 'Rotational Press',        'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Single-Arm Cable Press with Rotation']},
                    {'name': 'Landmine Rotation Press', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Landmine Rotation Press']},
                ],
            },
            ('Transverse', 'Pull'): {
                'categories': [
                    {'name': 'Rotational Row', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Single-Arm Cable Row with Rotation']},
                    {'name': 'Woodchop Pull',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['High-to-Low Cable Woodchop']},
                ],
            },
            ('Transverse', 'Squat'): {
                'categories': [
                    {'name': 'Rotational Lunge', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Lunge with Trunk Rotation', 'Rotational Step-Up']},
                    {'name': 'Pivot Squat',      'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Pivot Squat', 'Rotational Squat']},
                ],
            },
            ('Transverse', 'Hinge'): {
                'categories': [
                    {'name': 'Rotational Hinge', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Single-Arm Dumbbell Snatch', 'Rotational Clean']},
                ],
            },
            ('Transverse', 'Carry/Bracing'): {
                'categories': [
                    {'name': 'Offset Carry',         'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Asymmetric Load Carry', 'Single-Arm Overhead Carry']},
                    {'name': 'Anti-Rotation Hold',   'weight': 0, 'measurement_unit': 'DURATION',
                     'exercise_examples': ['Pallof Press Iso', 'Bird Dog Hold']},
                ],
            },
            ('Transverse', 'Gait/Locomotion'): {
                'categories': [
                    {'name': 'Agility / Cutting',    'weight': 0, 'measurement_unit': 'DISTANCE',
                     'exercise_examples': ['Cone Drill', 'Shuttle Run', 'T-Drill']},
                    {'name': 'Rotational Sled Work', 'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Rotational Sled Push', 'Lateral Sled Rotation']},
                ],
            },
            ('Transverse', 'Rotation'): {
                'categories': [
                    {'name': 'Anti-Rotation',     'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Pallof Press', 'Cable Chop']},
                    {'name': 'Rotational Power',  'weight': 0, 'measurement_unit': 'REPS_ONLY',
                     'exercise_examples': ['Med Ball Throw', 'Russian Twist']},
                    {'name': 'Thoracic Rotation', 'weight': 0, 'measurement_unit': 'REPS_ONLY',
                     'exercise_examples': ['Open Book', 'Seated Rotation']},
                ],
            },
            ('Transverse', 'Accessory/Isolation'): {
                'categories': [
                    {'name': 'Oblique Isolation', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Cable Twist', 'Woodchop']},
                    {'name': 'Rotator Cuff',      'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Internal Rotation', 'External Rotation']},
                    {'name': 'Forearm Rotation',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Pronation', 'Supination']},
                ],
            },
        },
    },

    # ── Named preset stubs (category weights to be defined) ───────────────────
    'GPP':          {'name': 'General Physical Preparedness', 'grid': {}},  # TBD
    'STRENGTH':     {'name': 'Strength',                      'grid': {}},  # TBD
    'HYPERTROPHY':  {'name': 'Hypertrophy',                   'grid': {}},  # TBD
    'POWERLIFTING': {'name': 'Powerlifting',                  'grid': {}},  # TBD
    'FUNCTIONAL':   {'name': 'Functional Fitness',            'grid': {}},  # TBD
}

DEFAULT_PRESET = 'BLANK'

PRESET_MATRIX_CONFIGS_NOTES = """
BLANK is the default preset. All 24 parent categories are pre-populated with
their sub-categories and measurement units; all weights are 0. The user
populates weights after registration to express their training priorities.

The 24 parent categories correspond to the initial 3 planes x 8 movement types.
Additional parent categories can be appended via add_category without structural
change -- the structure is an appendable list, not a fixed grid.

The tuple key (movement_plane, movement_type) is preserved as the canonical
join key across the exercise library, records, and all views (unchanged from
V1.0.1).

Parent weight = sum(cat['weight'] for cat in cell['categories'])
Parent weight is never stored -- always derived. This eliminates sync errors.

SEEDING: add_user calls copy.deepcopy(PRESET_MATRIX_CONFIGS[preset]['grid'])
because the value at each key is a mutable dict containing a mutable list.
A shallow copy would share the same category list objects across users.
deepcopy is required (Section 3.1).
"""

# ── 1.5 Controlled Vocabulary Lists ───────────────────────────────────────────
# These are the validation sets used on data entry. Any write method checks
# membership before accepting a value: if value not in VALID_SET: raise ValueError
# Membership check using the 'in' operator. Sets provide O(1) lookup and
# communicate intent: these are bags of valid values, not ordered sequences.

MOVEMENT_PLANES  = {'Sagittal', 'Frontal', 'Transverse'}
MOVEMENT_TYPES   = {'Accessory/Isolation', 'Carry/Bracing', 'Gait/Locomotion',
                    'Hinge', 'Pull', 'Push', 'Rotation', 'Squat'}
WORKOUT_TYPES    = {'Conditioning', 'Weightlifting', 'Mobility', 'Recovery'}
LATERALITY       = {'Bilateral', 'Unilateral'}
LOAD_TYPES       = {'Band', 'Barbell', 'Bodyweight', 'Cable', 'Curl Bar',
                    'Dumbbell', 'Kettlebell', 'Machine', 'Medicineball', 'N/A'}

# Note: PRIORITY_OPTIONS removed in V1.0.2. Priority validation is no longer
# required -- update_matrix_cell now accepts a categories list, not a priority string.
# (See Section 1.3 tombstone and Section 3.5 for updated method signatures.)

# Ordered lists for deterministic iteration over the category list.
# Validation uses the sets above; iteration uses these lists for stable order.
MOVEMENT_PLANES_ORDERED = ['Sagittal', 'Frontal', 'Transverse']
MOVEMENT_TYPES_ORDERED  = ['Accessory/Isolation', 'Carry/Bracing', 'Gait/Locomotion',
                           'Hinge', 'Pull', 'Push', 'Rotation', 'Squat']

# ── 1.6 Program Calendar Anchor ───────────────────────────────────────────────
# All week and block calculations derive from this single anchor. There is no
# stored calendar table -- weeks are computed arithmetically at runtime (Section 7).

import datetime
PROGRAM_START_DATE = datetime.date(2026, 1, 5)   # First Monday of the program



###############################################################################
# SECTION 2: CLASS ARCHITECTURE  (mtrx_database.py)
###############################################################################
# Two classes.

CLASS_ARCHITECTURE_NOTES = """
-- 2.1  MtrxDatabase --
The internal state store. All data entities live here as private attributes.
No external code accesses them directly.

    class MtrxDatabase:

        def __init__(self):
            self.__user_counter      = 1
            self.__measure_counter   = 1
            self.__record_counter    = 1
            self.__config_counter    = 1
            self.__block_counter     = 1

            self.__users             = {}   # dict[int, dict]
            self.__measurements      = {}   # dict[int, list[dict]]
            self.__exercises         = {}   # dict[str, dict]
            self.__records           = []   # list[dict]
            self.__matrix_plans      = {}   # dict[int, dict[tuple, dict]]
            self.__plan_history      = {}   # dict[int, list[dict]]
            self.__training_blocks   = {}   # dict[int, list[dict]]

        def __repr__(self):
            return (f'MtrxDatabase | Users: {len(self.__users)} | '
                    f'Exercises: {len(self.__exercises)} | '
                    f'Records: {len(self.__records)}')

Full method signatures are specified in Section 3. All methods that could fail
receive a try/except wrapper at the MtrxApp call site -- the database methods
themselves raise ValueError or KeyError with descriptive messages on bad input.

-- 2.2  MtrxApp --
The public controller. Holds one MtrxDatabase instance. All user-facing
operations flow through this class. Calls mtrx_functions for every derived
computation; never reimplements them inline.

    import mtrx_database
    import mtrx_functions as fn
    import pandas as pd
    import matplotlib.pyplot as plt

    class MtrxApp:

        def __init__(self):
            self.__db = MtrxDatabase()

        def __repr__(self):
            return f'MtrxApp | {self.__db}'

MtrxApp methods are thin orchestrators: pull data from the database, pass it to
a function, return or display the result. No business logic lives here.

INTERFACE CONTRACT (Repository Pattern):
MtrxDatabase's public methods -- get_records(), get_exercise(), get_user(), etc.
-- are a stable contract. No code outside MtrxDatabase ever touches
self.__records, self.__exercises, or any private attribute directly. This
boundary is what makes the storage backend swappable: replacing in-memory lists
with SQLite queries requires changing only MtrxDatabase internals; MtrxApp and
all view functions are completely untouched. At thousands of users this swap is
a localized change, not a rewrite. Treat this boundary as an invariant: if a
view function ever accesses a private attribute directly, the contract is broken.
"""

MULTI_USER_BOUNDARY_TABLE = """
| Component              | Scope                              | Implementation                                                      |
|------------------------|------------------------------------|---------------------------------------------------------------------|
| Exercise Library       | Shared -- all users                | self.__exercises single dict in MtrxDatabase                        |
| System Constants       | Shared -- all users                | Module-level constants in mtrx_constants.py                         |
| Program Calendar       | Shared -- all users                | Computed from PROGRAM_START_DATE                                    |
| Preset Configs         | Shared seed, deep-copied per user  | copy.deepcopy(PRESET_MATRIX_CONFIGS[preset]['grid']) on add_user    |
| Workout Records        | Per user                           | user_id field on every record; filtered at query                    |
| User Measurements      | Per user                           | self.__measurements keyed by user_id                                |
| Matrix Plan            | Per user after registration        | self.__matrix_plans[user_id] -- dict[tuple, dict] with categories   |
| Plan History           | Per user                           | self.__plan_history[user_id] -- append-only snapshots of matrix     |
| Training Blocks        | Per user                           | self.__training_blocks[user_id] -- user-defined programming periods |
| DDM                    | Per user per exercise              | Computed from filtered records; no shared state                     |
"""



###############################################################################
# SECTION 3: DATA LAYER
###############################################################################
# This section specifies the internal representation of each entity, the
# reasoning behind that choice, and the complete method signatures for the
# database.

# ── 3.1 Users ─────────────────────────────────────────────────────────────────

USERS_STRUCTURE = """
self.__users: dict[int, dict]

Example state:
{
    1: {'username': 'kharmer', 'display_name': 'Kai Harmer',
        'email': 'kai@example.com', 'join_date': datetime.date(2026, 1, 5),
        'age': 38, 'training_experience': 10},
    2: {'username': 'jdoe',    'display_name': 'Jane Doe',
        'email': 'jane@example.com', 'join_date': datetime.date(2026, 1, 12),
        'age': None, 'training_experience': None},
}

WHY dict[int, dict] KEYED BY user_id:
Every other entity references user_id as a foreign key. O(1) lookup at every
join point. Username and email uniqueness are enforced on write using a generator
expression over values -- this is a one-time cost at insert, not a structural
requirement.

age and training_experience are stored as data-only fields. They are not inputs
to any calculation, scoring, or handicap logic in this version.
"""

USERS_METHODS = """
def add_user(self, username: str, display_name: str, email: str,
             age: int = None, training_experience: int = None,
             preset_key: str = None) -> int:
    # 1. Validate: if any(u['username'] == username for u in self.__users.values()): raise ValueError
    # 2. Validate: if any(u['email'] == email for u in self.__users.values()): raise ValueError
    # 3. user_id = self.__user_counter
    # 4. self.__users[user_id] = {'username': username, 'display_name': display_name,
    #                              'email': email, 'join_date': datetime.date.today(),
    #                              'age': age, 'training_experience': training_experience}
    # 5. preset = preset_key or DEFAULT_PRESET
    #    self.__matrix_plans[user_id] = copy.deepcopy(PRESET_MATRIX_CONFIGS[preset]['grid'])
    #    (deepcopy required -- values are mutable dicts containing mutable lists)
    # 6. self.__measurements[user_id] = []
    # 7. self.__plan_history[user_id] = []
    # 8. self.__training_blocks[user_id] = []
    # 9. self.__user_counter += 1
    # 10. return user_id

def get_user(self, user_id: int) -> dict:
    # if user_id not in self.__users: raise KeyError
    # return dict(self.__users[user_id])   # return a copy, not the live dict

def get_all_users(self) -> dict:
    # return {k: dict(v) for k, v in self.__users.items()}
    # Deep-copy each inner dict so callers cannot mutate internal state.
"""

# ── 3.1b Plan History ─────────────────────────────────────────────────────────

PLAN_HISTORY_STRUCTURE = """
self.__plan_history: dict[int, list[dict]]

An append-only, timestamped snapshot of the full matrix state per user.
A new snapshot is appended automatically whenever any matrix modification
occurs (via update_matrix_cell, add_category, or preset change).
The plan history provides plan-side data for plan-vs-completed analysis
and supports the competitive platform's radar grid positioning.

Example state:
{
    1: [
        {
            'snapshot_id': 1,
            'timestamp':   datetime.datetime(2026, 1, 5, 10, 0, 0),
            'matrix_state': {
                ('Sagittal', 'Push'): {
                    'categories': [
                        {'name': 'Vertical Press', 'weight': 3, ...},
                        ...
                    ],
                },
                ...
            },
        },
        {
            'snapshot_id': 2,
            'timestamp':   datetime.datetime(2026, 2, 14, 8, 30, 0),
            'matrix_state': { ... },
        },
    ],
}

WHY APPEND-ONLY:
Snapshots are never modified or deleted. Each represents the matrix state at
a point in time. Immutability enables reliable plan-vs-completed analysis
even when the user later changes their matrix configuration.

DEEPCOPY INVARIANT: matrix_state is always a deep copy of __matrix_plans[user_id]
at the time of the snapshot. Any subsequent mutation of the live matrix does not
affect stored snapshots.
"""

PLAN_HISTORY_METHODS = """
def save_config_snapshot(self, user_id: int) -> int:
    # 1. Validate user_id exists
    # 2. snapshot_id = self.__config_counter
    # 3. snapshot = {
    #        'snapshot_id':  snapshot_id,
    #        'timestamp':    datetime.datetime.now(),
    #        'matrix_state': copy.deepcopy(self.__matrix_plans[user_id]),
    #    }
    # 4. self.__plan_history[user_id].append(snapshot)
    # 5. self.__config_counter += 1
    # 6. return snapshot_id
    #
    # Called internally by update_matrix_cell and add_category.
    # Not a public user action.

def get_active_config(self, user_id: int) -> dict:
    # Returns the most recent snapshot's matrix_state (last entry in list).
    # Returns copy.deepcopy(self.__matrix_plans[user_id]) if no snapshots exist.

def get_plan_history(self, user_id: int) -> list:
    # Returns full plan history as a list of dicts (deep copies).
    # return [copy.deepcopy(s) for s in self.__plan_history[user_id]]
"""

# ── 3.2 User Measurements ─────────────────────────────────────────────────────

MEASUREMENTS_STRUCTURE = """
self.__measurements: dict[int, list[dict]]

Example state:
{
    1: [
        {'measurement_id': 1, 'date': datetime.date(2026, 1, 5),
         'bodyweight': 185.0, 'additional': {}},
        {'measurement_id': 3, 'date': datetime.date(2026, 2, 1),
         'bodyweight': 183.5, 'additional': {'waist': 34.0}},
    ],
}

WHY dict[int, list[dict]] SORTED BY DATE:
This is a time-series per user. The most-recent-on-or-before query (used every
time a bodyweight exercise is logged) requires finding the largest date that does
not exceed the target. With the list maintained in ascending date order, a single
forward scan finds this in O(n) where n is measurements per user (small): iterate
forward, updating the result at each entry where date <= target_date, so the last
update is the most recent qualifying measurement.
An unsorted structure would require a .sort() call on every query.

SORT INVARIANT: add_measurement inserts and re-sorts using
sorted(..., key=lambda m: m['date']). The list is always sorted ascending after
every write.
"""

MEASUREMENTS_METHODS = """
def add_measurement(self, user_id: int, date: datetime.date,
                    bodyweight: float, additional: dict = None) -> int:
    # 1. Validate user_id exists
    # 2. measurement_id = self.__measure_counter
    # 3. record = {'measurement_id': measurement_id, 'date': date,
    #              'bodyweight': float(bodyweight), 'additional': additional or {}}
    # 4. self.__measurements[user_id].append(record)
    # 5. self.__measurements[user_id] = sorted(self.__measurements[user_id],
    #                                          key=lambda m: m['date'])
    # 6. self.__measure_counter += 1
    # 7. return measurement_id

def get_bodyweight_on_date(self, user_id: int, target_date: datetime.date) -> float | None:
    # 1. Validate user_id exists
    # 2. result = None
    # 3. for m in self.__measurements[user_id]:    # list is sorted ascending
    #        if m['date'] <= target_date:
    #            result = m['bodyweight']           # keep updating; last valid = most recent
    # 4. return result                             # None if no measurement on or before date
"""

# ── 3.3 Exercise Library ──────────────────────────────────────────────────────

EXERCISES_STRUCTURE = """
self.__exercises: dict[str, dict]

Key: exercise_name.strip().lower()  (normalized for dedup)

Example state:
{
    'bench press': {
        'exercise_name':    'Bench Press',
        'workout_type':     'Weightlifting',
        'laterality':       'Bilateral',
        'default_load_type':'Barbell',
        'movement_type':    'Push',
        'movement_plane':   'Sagittal',
    },
    'single-arm dumbbell row': {
        'exercise_name':    'Single-Arm Dumbbell Row',
        'workout_type':     'Weightlifting',
        'laterality':       'Unilateral',
        'default_load_type':'Dumbbell',
        'movement_type':    'Pull',
        'movement_plane':   'Sagittal',
    },
}

WHY dict KEYED BY NORMALIZED NAME:
The uniqueness constraint is the defining characteristic of this entity. Dict key
uniqueness enforces it structurally. All downstream lookups are by name (when a
user selects an exercise to log). The canonical join key --
(movement_plane, movement_type) -- is derived from the value at query time; it
does not need to be the storage key.

NORMALIZATION RULE: exercise_name.strip().lower() is used as the key in all read
and write operations. The display name ('exercise_name' in the value dict)
preserves original casing.
"""

EXERCISES_METHODS = """
def add_exercise(self, exercise_name: str, workout_type: str, laterality: str,
                 default_load_type: str, movement_type: str,
                 movement_plane: str) -> str:
    # 1. key = exercise_name.strip().lower()
    # 2. if key in self.__exercises: raise ValueError('Duplicate exercise name')
    # 3. Validate each attribute against controlled vocabulary constants
    # 4. self.__exercises[key] = {'exercise_name': exercise_name, ...}
    # 5. return exercise_name

def update_exercise(self, exercise_name: str, **kwargs) -> None:
    # 1. key = exercise_name.strip().lower()
    # 2. if key not in self.__exercises: raise KeyError
    # 3. if 'exercise_name' in kwargs:
    #        raise ValueError('exercise_name cannot be changed. Records reference '
    #                         'exercises by name; renaming would orphan historical data.')
    # 4. for field, value in kwargs.items():
    #        validate field is a known attribute; validate value against vocab
    #        self.__exercises[key][field] = value

def get_exercise(self, exercise_name: str) -> dict:
    # key = exercise_name.strip().lower()
    # if key not in self.__exercises: raise KeyError
    # return dict(self.__exercises[key])

def get_exercises_for_cell(self, movement_plane: str, movement_type: str) -> list:
    # return [v['exercise_name'] for v in self.__exercises.values()
    #         if v['movement_plane'] == movement_plane
    #         and v['movement_type'] == movement_type]

def get_all_exercises(self) -> dict:
    # return {k: dict(v) for k, v in self.__exercises.items()}
    # Required by view functions (build_summary_matrix, build_vesting_grid,
    # build_program_balance) which need the full exercises dict as an argument.

def merge_exercises(self, source_name: str, target_name: str) -> int:
    # Merges all records referencing source_name into target_name,
    # then removes the source entry from the exercise library.
    #
    # Pre-conditions:
    # 1. source_key = source_name.strip().lower()
    #    target_key = target_name.strip().lower()
    # 2. if source_key not in self.__exercises: raise KeyError
    # 3. if target_key not in self.__exercises: raise KeyError
    # 4. if source_key == target_key: raise ValueError('Cannot merge exercise with itself')
    # 5. Verify both exercises share the same movement_plane, movement_type,
    #    and dimensionality. Raise ValueError if they differ -- merging across
    #    categories would corrupt category-level aggregations.
    #
    # Merge:
    # 6. records_updated = 0
    #    for r in self.__records:
    #        if r['exercise_name'].strip().lower() == source_key:
    #            r['exercise_name'] = self.__exercises[target_key]['exercise_name']
    #            records_updated += 1
    # 7. del self.__exercises[source_key]
    # 8. return records_updated  -- count of records re-pointed
    #
    # No snapshot is taken -- this is a data cleanup operation, not a plan change.
    # The caller should log the merge externally if an audit trail is needed.
"""

# ── 3.4 Workout Records ───────────────────────────────────────────────────────

RECORDS_STRUCTURE = """
self.__records: list[dict]

Example state:
[
    {
        'record_id':          1,
        'user_id':            1,
        'date':               datetime.date(2026, 1, 12),
        'exercise_name':      'Bench Press',
        'sets':               3,
        'reps':               5,
        'bonus_reps':         1,
        'weight':             255.0,
        'rpe':                8.0,
        'load_type':          'Barbell',
        'notes':              '',
        'duration_seconds':   None,
        'distance_meters':    None,
    },
    {
        'record_id':          2,
        'user_id':            1,
        'date':               datetime.date(2026, 1, 12),
        'exercise_name':      'Farmer Walk',
        'sets':               None,
        'reps':               None,
        'bonus_reps':         None,
        'weight':             70.0,
        'rpe':                7.0,
        'load_type':          'Kettlebell',
        'notes':              '',
        'duration_seconds':   None,
        'distance_meters':    40.0,
    },
    ...
]

WHY A FLAT list[dict]:
This is the single most consequential structural decision in the application.
Every view (Summary Matrix, Vesting Grid, Program Balance, Weight Guidance) is a
different aggregation -- different group-by keys, different filters, different
pivot axes. A flat list is a direct input to pd.DataFrame(self.__records), which
then supports any pandas groupby, pivot, or boolean filter in a single line.
Nesting by user, date, or exercise would require reconstruction at query time and
would make each view function more complex without providing any benefit. Inserts
are list.append(dict) -- O(1). There is no access pattern that benefits from
nesting.

NULLABLE FIELDS:
duration_seconds and distance_meters are None when not applicable to the record's
measurement unit. Sets/reps/bonus_reps are None for non-VOLUME/REPS_ONLY records.
All stored records are self-contained -- no secondary lookup at read time.

BODYWEIGHT EXERCISE HANDLING:
When load_type == 'Bodyweight', weight is resolved at log time by calling
get_bodyweight_on_date(user_id, date) before the record is created. The stored
record is always self-contained -- no secondary lookup is needed at read time.
"""

RECORDS_METHODS = """
def add_record(self, user_id: int, date: datetime.date, exercise_name: str,
               sets: int = None, reps: int = None, bonus_reps: int = None,
               weight: float = None, rpe: float = None,
               load_type: str = None, notes: str = '',
               duration_seconds: float = None,
               distance_meters: float = None) -> int:
    # NOTE: All measurement fields (sets, reps, bonus_reps, weight, rpe,
    #   load_type, duration_seconds, distance_meters) default to None.
    #   Required fields are determined by the exercise's measurement_unit,
    #   which is resolved via the exercise → parent category chain.
    #   Step 3b validates that the required fields for the measurement_unit
    #   are present and non-None. Example mappings:
    #     VOLUME exercises (Bench Press):       sets, reps, weight required
    #     LOAD_DISTANCE exercises (Farmer Walk): weight, distance_meters required
    #     DURATION exercises (Plank):            sets, duration_seconds required
    #     DISTANCE exercises (Sprint):           distance_meters required
    #     REPS_ONLY exercises (Med Ball Slam):   sets, reps required
    #
    # 1. Validate user_id exists
    # 2. exercise = self.get_exercise(exercise_name)  -- raises KeyError if not found
    # 3. Validate load_type in LOAD_TYPES (if provided)
    # 3b. Validate required fields for measurement_unit:
    #        Look up the exercise's cell: cell_key = (exercise['movement_plane'],
    #                                                  exercise['movement_type'])
    #        Get the user's matrix plan: plan = self.__matrix_plans[user_id]
    #        Find the matching category (by exercise characteristics or first match).
    #        Resolve measurement_unit from the category.
    #        Verify the record supplies the fields listed in
    #        MEASUREMENT_UNITS[unit]['fields']. Raise ValueError if required fields
    #        are missing or None.
    # 4. Validate rpe is in range [6.0, 10.0]
    # 5. If load_type == 'Bodyweight':
    #        weight = self.get_bodyweight_on_date(user_id, date)
    #        if weight is None:
    #            raise ValueError('No bodyweight measurement found on or before this date')
    #    Note: check the record's load_type argument, NOT exercise['default_load_type'].
    #    The spec allows load_type to be overridden per record. If a user logs a
    #    bodyweight exercise with Barbell (override), the entered weight stands.
    #    Auto-resolution only applies when the record itself carries load_type == 'Bodyweight'.
    # 6. record_id = self.__record_counter
    # 7. self.__records.append({
    #        'record_id': record_id, 'user_id': user_id, 'date': date,
    #        'exercise_name': exercise_name, 'sets': sets, 'reps': reps,
    #        'bonus_reps': bonus_reps, 'weight': float(weight), 'rpe': float(rpe),
    #        'load_type': load_type, 'notes': notes,
    #        'duration_seconds': duration_seconds,
    #        'distance_meters': distance_meters,
    #    })
    # 8. self.__record_counter += 1
    # 9. return record_id

def get_records(self, user_id: int = None, date_start: datetime.date = None,
                date_end: datetime.date = None, exercise_name: str = None) -> list:
    # result = self.__records
    # if user_id       is not None: result = [r for r in result if r['user_id'] == user_id]
    # if date_start    is not None: result = [r for r in result if r['date'] >= date_start]
    # if date_end      is not None: result = [r for r in result if r['date'] <= date_end]
    # if exercise_name is not None:
    #     key = exercise_name.strip().lower()
    #     result = [r for r in result if r['exercise_name'].strip().lower() == key]
    # return result
    #
    # Chained list comprehensions. For view functions, the caller
    # either passes user_id only and does further filtering in pandas, or passes
    # all filters and receives a minimal pre-filtered list.

def delete_record(self, record_id: int) -> None:
    # 1. Find the record: match = [r for r in self.__records if r['record_id'] == record_id]
    # 2. if not match: raise KeyError(f'record_id {record_id} not found')
    # 3. self.__records = [r for r in self.__records if r['record_id'] != record_id]
    # Rebuilds the list excluding the target record. O(n) but records are
    # append-heavy and deletes are rare (correcting data-entry mistakes).

def delete_measurement(self, user_id: int, measurement_id: int) -> None:
    # 1. Validate user_id exists
    # 2. original_len = len(self.__measurements[user_id])
    # 3. self.__measurements[user_id] = [
    #        m for m in self.__measurements[user_id]
    #        if m['measurement_id'] != measurement_id
    #    ]
    # 4. if len(self.__measurements[user_id]) == original_len:
    #        raise KeyError(f'measurement_id {measurement_id} not found for user {user_id}')

def delete_exercise(self, exercise_name: str) -> None:
    # 1. key = exercise_name.strip().lower()
    # 2. if key not in self.__exercises: raise KeyError
    # 3. Check for referencing records:
    #        if any(r['exercise_name'].strip().lower() == key for r in self.__records):
    #            raise ValueError('Cannot delete exercise with existing workout records.')
    # 4. del self.__exercises[key]
"""

# ── 3.5 Matrix Plans ──────────────────────────────────────────────────────────

MATRIX_PLAN_STRUCTURE = """
self.__matrix_plans: dict[int, dict[tuple, dict]]

Each user has an independent matrix. The inner dict maps each
(movement_plane, movement_type) tuple to a dict containing a 'categories' list.
The tuple key is immutable, hashable, and enables direct O(1) lookup.

Example state:
{
    1: {
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
        ('Sagittal', 'Carry/Bracing'): {
            'categories': [
                {'name': 'Loaded Carry', 'weight': 2, 'measurement_unit': 'LOAD_DISTANCE',
                 'exercise_examples': ['Farmer Walk', 'Front Rack Carry']},
                {'name': 'Static Brace', 'weight': 1, 'measurement_unit': 'DURATION',
                 'exercise_examples': ['Plank', 'Dead Bug']},
            ],
        },
        ...
    },
    2: {
        ('Sagittal', 'Push'): {
            'categories': [
                {'name': 'Vertical Press', 'weight': 0, ...},   # User 2 not yet configured
                ...
            ],
        },
        ...
    },
}

WHY dict[tuple, dict] FOR THE INNER STRUCTURE:
(movement_plane, movement_type) is the canonical join key. A tuple key is
immutable, hashable, and enables direct O(1) cell lookup:
matrix_plans[user_id][(plane, type)]. The alternative -- a nested dict[plane][type]
-- requires two accesses and complicates iteration.

WHY CATEGORIES ARE A LIST, NOT A DICT:
Categories within a cell are ordered (display order, priority order). A list
preserves insertion order, supports append without key-collision concerns, and
matches the natural "add another subcategory" operation.

SEEDING: Called automatically inside add_user via copy.deepcopy(
PRESET_MATRIX_CONFIGS[preset]['grid']). Deepcopy is required because values are
mutable dicts containing mutable lists. A shallow copy would share category list
objects across users.

PARENT WEIGHT: sum(cat['weight'] for cat in cell['categories']) -- never stored,
always derived. This eliminates sync errors between stored and computed totals.
"""

MATRIX_PLAN_METHODS = """
def update_matrix_cell(self, user_id: int, movement_plane: str,
                       movement_type: str, categories: list) -> None:
    # Replaces the full categories list for a cell.
    # 1. Validate user_id, movement_plane in MOVEMENT_PLANES,
    #    movement_type in MOVEMENT_TYPES
    # 2. Validate each category dict has required keys:
    #    'name', 'weight', 'measurement_unit', 'exercise_examples'
    # 3. Validate each category's measurement_unit in MEASUREMENT_UNITS
    # 4. self.__matrix_plans[user_id][(movement_plane, movement_type)] = {
    #        'categories': categories
    #    }
    # 5. self.save_config_snapshot(user_id)   # trigger plan history snapshot

def add_category(self, user_id: int, movement_plane: str,
                 movement_type: str, name: str, weight: int,
                 measurement_unit: str,
                 exercise_examples: list = None) -> None:
    # Appends a new category to an existing cell.
    # 1. Validate user_id, movement_plane, movement_type
    # 2. Validate measurement_unit in MEASUREMENT_UNITS
    # 3. self.__matrix_plans[user_id][(movement_plane, movement_type)]['categories'].append({
    #        'name': name, 'weight': weight, 'measurement_unit': measurement_unit,
    #        'exercise_examples': exercise_examples or [],
    #    })
    # 4. self.save_config_snapshot(user_id)   # trigger plan history snapshot

def get_matrix_plan(self, user_id: int) -> dict:
    # Returns a deep copy of the hierarchical matrix for one user.
    # return copy.deepcopy(self.__matrix_plans[user_id])

def get_parent_weight(self, user_id: int, movement_plane: str,
                      movement_type: str) -> int:
    # Returns the derived parent weight (sum of subcategory weights for a
    # parent category identified by its (movement_plane, movement_type) key).
    # cell = self.__matrix_plans[user_id][(movement_plane, movement_type)]
    # return sum(cat['weight'] for cat in cell['categories'])
"""

# ── 3.6 Training Blocks ───────────────────────────────────────────────────────

TRAINING_BLOCKS_STRUCTURE = """
self.__training_blocks: dict[int, list[dict]]

User-defined programming periods. Each block has start and end dates as loose
boundaries and a targets dict expressing per-dimensionality goals for the block.
Progress is measured by volume accumulated, session exposure, and other output
metrics -- not by elapsed time. Time is a view; the authoritative progress
signal is what was completed, not how long the block has been running.

Example state:
{
    1: [
        {
            'block_id':   1,
            'name':       'Spring Strength Block',
            'start_date': datetime.date(2026, 1, 5),
            'end_date':   datetime.date(2026, 3, 1),
            'targets': {
                ('Sagittal', 'Push'): {
                    'Vertical Press':   {'target_sessions': 3, 'target_volume': None, 'unit': 'VOLUME'},
                    'Horizontal Press': {'target_sessions': 3, 'target_volume': None, 'unit': 'VOLUME'},
                },
                ('Sagittal', 'Hinge'): {
                    'Bilateral Hinge':  {'target_sessions': 2, 'target_volume': None, 'unit': 'VOLUME'},
                },
            },
        },
    ],
}

WHY USER-DEFINED BLOCKS:
Blocks are programming periods defined by the user, not derived arithmetically
from PROGRAM_START_DATE. Different users have different block lengths, different
goals per block, and may run overlapping or non-contiguous blocks. Storing them
explicitly enables output-based progress tracking.

TARGETS:
The targets dict expresses per-dimensionality goals. Each entry supports both
a session count target (target_sessions) and a volume target (target_volume),
either of which may be None if not set. The unit field aligns the volume target
with the dimensionality's measurement unit. Progress reporting surfaces both
metrics; the user decides which is the primary signal for a given block.
Elapsed time is surfaced as context (e.g. 'Week 3 of 8') but is never the
primary progress measure.

NOTE -- target_sessions vs parent_weight:
# target_sessions is the authoritative goal for a dimensionality within a block.
# category weights in the category plan express relative priority, not session count.
# These are two distinct concepts. parent_weight should NOT be used directly
# as target_sessions in build_program_balance. Block targets are the authoritative
# source for session and volume goals when a block is active.
"""

TRAINING_BLOCKS_METHODS = """
def add_training_block(self, user_id: int, name: str,
                       start_date: datetime.date, end_date: datetime.date,
                       targets: dict) -> int:
    # 1. Validate user_id exists
    # 2. Validate end_date > start_date
    # 3. Validate target cell keys exist in user's matrix_plan
    # 4. Validate measurement units in targets match category definitions
    # 5. block_id = self.__block_counter
    # 6. self.__training_blocks[user_id].append({
    #        'block_id': block_id, 'name': name, 'start_date': start_date,
    #        'end_date': end_date, 'targets': targets,
    #    })
    # 7. self.__block_counter += 1
    # 8. return block_id

def get_active_block(self, user_id: int,
                     as_of: datetime.date = None) -> dict | None:
    # Returns the block where start_date <= as_of <= end_date.
    # as_of defaults to datetime.date.today() if not provided.
    # Returns None if no block covers the date.
    # If multiple blocks cover the date, returns the most recently added.

def get_block_progress(self, user_id: int, block_id: int) -> dict:
    # Returns plan vs. completed for each category in the block, by week.
    # Structure:
    # {
    #     'block': { ... },   # the block dict
    #     'weeks': {
    #         week_start: {
    #             (plane, type): {
    #                 category_name: {
    #                     'target':    int,     # from block targets
    #                     'completed': int,     # sessions logged this week
    #                     'status':    str,     # 'Ahead' / 'On Track' / 'Behind' / 'Not Started'
    #                 },
    #             },
    #         },
    #         ...
    #     },
    # }
"""



###############################################################################
# SECTION 4: DERIVED METRICS  (mtrx_functions.py)
###############################################################################
# All derived metrics are pure functions. They have no side effects, modify no
# external state, and depend only on their arguments and constants from
# mtrx_constants.py. Every function is testable in isolation with a single call.

# ── 4.1 Stimulus Classification ───────────────────────────────────────────────

def classify_stimulus(reps: int) -> str:
    """
    Maps reps-per-set to one of four stimulus types.

    WHY if/elif AND NOT A LOOP OVER STIMULUS_TABLE:
    The spec defines this as a 'strict ordered IFS.' The classification is not a
    table lookup -- it is a sequential decision tree. An if/elif chain is O(1),
    self-documenting about the ordered nature of the check, and impossible to
    call in the wrong sequence. Iterating over STIMULUS_TABLE would require
    encoding comparison direction into the table structure, adding indirection
    for zero gain.
    """
    if reps <= 3:
        return 'N'
    elif reps <= 6:
        return 'MT'
    elif reps <= 15:
        return 'MD'
    else:
        return 'MS'

# ── 4.2 Actual Reps ───────────────────────────────────────────────────────────

def compute_actual_reps(sets: int, reps: int, bonus_reps: int) -> int:
    return (sets * reps) + bonus_reps

# ── 4.3 Actual Volume ─────────────────────────────────────────────────────────

def compute_actual_volume(actual_reps: int, weight: float, laterality: str) -> float:
    """
    The x2 multiplier is applied to volume only. Weight as stored and used by
    DDM is always the per-side working weight.
    """
    if laterality == 'Unilateral':
        return float(actual_reps * weight * 2)
    else:
        return float(actual_reps * weight)

# ── 4.4 Unrealized Vesting % ──────────────────────────────────────────────────

def compute_unrealized_vesting_pct(workout_date: datetime.date,
                                   today: datetime.date,
                                   adaptation_days: int) -> float:
    """
    datetime.date subtraction yields a timedelta; .days extracts the integer
    count. max and min clamp to [0, 1]. No
    import beyond datetime is needed.
    """
    days_elapsed = (today - workout_date).days
    return max(0.0, min(1.0, 1.0 - (days_elapsed / adaptation_days)))

# ── 4.5 Unrealized Volume ─────────────────────────────────────────────────────

def compute_unrealized_volume(actual_volume: float,
                               unrealized_vesting_pct: float) -> float:
    return round(actual_volume * unrealized_vesting_pct)

# ── 4.6 Realized Volume ───────────────────────────────────────────────────────

def compute_realized_volume(actual_volume: float,
                             unrealized_volume: float) -> float:
    """
    The accounting identity Unrealized + Realized = Actual is enforced by
    derivation order: compute unrealized first, then derive realized as the
    remainder. This guarantees the identity holds to floating-point precision.
    """
    return actual_volume - unrealized_volume

# ── 4.7 Fatigue Volume ────────────────────────────────────────────────────────

def compute_fatigue_volume(actual_volume: float,
                            workout_date: datetime.date,
                            today: datetime.date,
                            fatigue_days: int) -> float:
    """
    Fatigue Volume is always <= Unrealized Volume. It is not a separate
    accounting bucket -- it is a sub-filter of the Adaptation row in views.
    It is computed from actual_volume directly (not from unrealized_volume)
    because it has its own independent decay rate.
    """
    days_elapsed = (today - workout_date).days
    return round(actual_volume * max(0.0, 1.0 - (days_elapsed / fatigue_days)))

# ── 4.8 DDM ───────────────────────────────────────────────────────────────────

def compute_ddm(exercise_name: str,
                records: list,
                today: datetime.date,
                lookback_days: int = 90) -> float | None:
    """
    Computes the Desirable Difficulty Max for a given exercise.

    CALLER CONTRACT: records is pre-filtered to a single user before being
    passed here. The caller (MtrxApp or build_weight_guidance) is responsible
    for calling db.get_records(user_id=user_id) and passing only that user's
    records. This function does not re-filter by user_id.

    Logic:
    - All four canonical schemes (3x2, 3x5, 3x10, 3x20) are treated equally.
    - For each scheme, find the most recent session within the lookback window.
    - Back-calculate the implied reference weight: session_weight / pct_of_ddm.
    - DDM = average of all implied references found (2-4 schemes may contribute).
    - A scheme with no sessions within the window is skipped -- it does not block
      the calculation.
    - Returns None if fewer than 2 schemes have qualifying sessions within the
      window -- a single implied reference is not a reliable average.

    WHY today IS AN EXPLICIT PARAMETER AND NOT datetime.date.today() INSIDE:
    Pure functions receive all their inputs as arguments. Hard-coding
    datetime.date.today() inside would make the function non-deterministic and
    untestable. The caller controls today, which also means back-testing a
    specific date is trivial.

    WHY NO PANDAS HERE:
    The filter + sort + take-first pattern on a small list (records for one user
    and one exercise) is handled cleanly by list comprehension and sorted().
    Constructing a DataFrame for these lookups would add overhead
    without clarity. Pandas enters the picture only when aggregating across many
    records (Section 6 views).

    WHY REQUIRE A MINIMUM OF 2 SCHEMES:
    A DDM built from a single implied reference is not an average -- it is one
    data point dressed as a consensus value. Two independent references from two
    different rep ranges provide a cross-check: if they are close, DDM is
    reliable; if they diverge, the athlete's training history is inconsistent
    in a way worth surfacing. Fewer than 2 qualifying schemes returns None,
    prompting the athlete to log another scheme before receiving weight guidance.
    """
    exercise_key = exercise_name.strip().lower()
    cutoff_date  = today - datetime.timedelta(days=lookback_days)

    implied_references = []

    # Iterate all four canonical schemes equally -- no primary/secondary distinction
    for scheme_key, props in CANONICAL_SCHEMES.items():
        req_sets   = props['sets']        # single source of truth
        req_reps   = props['reps']        # single source of truth
        scheme_pct = props['pct_of_ddm']

        # Filter to matching records within the recency window
        candidates = [
            r for r in records
            if r['exercise_name'].strip().lower() == exercise_key
            and r['sets'] == req_sets
            and r['reps'] == req_reps
            and r['date'] >= cutoff_date
        ]

        if not candidates:
            continue   # No recent history for this scheme; skip -- do not block DDM

        # Most recent session within the window: sort descending, take first
        most_recent = sorted(candidates, key=lambda r: r['date'], reverse=True)[0]
        implied_references.append(most_recent['weight'] / scheme_pct)

    if len(implied_references) < 2:
        return None   # Fewer than 2 qualifying schemes -- not a reliable average

    # Average however many implied references were found (2-4)
    return float(sum(implied_references) / len(implied_references))

# ── 4.9 DDM-Derived Weight Suggestions ───────────────────────────────────────

def compute_weight_suggestions(ddm: float) -> dict:
    """
    Dict comprehension over CANONICAL_SCHEMES. Result is a dict of
    {scheme_key: suggested_weight} for all four schemes. All suggestions are
    user-overridable at the app layer.
    """
    return {
        scheme: round(ddm * props['pct_of_ddm'], 1)
        for scheme, props in CANONICAL_SCHEMES.items()
    }

# ── 4.10 Mixed-Stimulus Sessions (Blended Adaptation) ────────────────────────

def compute_blended_adaptation(contributions: list) -> dict:
    """
    Called when a single workout record contains sets across multiple stimulus
    types. Blends color and vesting percentage by volume weight.

    contributions: list of dicts, each:
        {'stimulus': str, 'actual_volume': float, 'unrealized_pct': float}

    Hex-to-RGB uses string slicing and int(string, 16) -- base-16 integer cast.
    RGB-to-hex uses an f-string format specifier. No external color library is used or needed.
    """
    total_volume = sum(c['actual_volume'] for c in contributions)
    if total_volume == 0:
        return {'blended_pct': 0.0, 'blended_hex': '#000000'}

    blended_pct = sum(
        (c['actual_volume'] / total_volume) * c['unrealized_pct']
        for c in contributions
    )

    r_blend, g_blend, b_blend = 0.0, 0.0, 0.0
    for c in contributions:
        weight    = c['actual_volume'] / total_volume
        hex_color = STIMULUS_TABLE[c['stimulus']]['hex']   # e.g., '#FF6A00'
        r = int(hex_color[1:3], 16)   # string slicing + base-16 cast
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r_blend += weight * r
        g_blend += weight * g
        b_blend += weight * b

    blended_hex = '#{:02X}{:02X}{:02X}'.format(int(r_blend), int(g_blend), int(b_blend))
    return {'blended_pct': round(blended_pct, 4), 'blended_hex': blended_hex}

# ── 4.11 Prescription Engine ──────────────────────────────────────────────────

def build_session(matrix_plan: dict,
                  records: list,
                  exercises: dict,
                  block_targets: dict,
                  week_start: datetime.date,
                  week_end: datetime.date,
                  today: datetime.date) -> list:
    """
    Generates a workout session for today.

    CALLER CONTRACT: All inputs are assembled by MtrxApp from the database.
    This function is pure -- no side effects, deterministic given same inputs.

    INPUTS:
        matrix_plan:   dict[tuple, dict]  -- hierarchical matrix with categories
        records:       list[dict]         -- this user's records (pre-filtered)
        exercises:     dict[str, dict]    -- full exercise library
        block_targets: dict               -- from active training block (Section 3.6/7.2);
                                             None if no active block
        week_start:    datetime.date
        week_end:      datetime.date
        today:         datetime.date

    OUTPUT:
        list of dicts, one per exercise slot in the session. Each dict:
        {
            'slot':             int,            # position in session (1-based)
            'cell':             (str, str),     # (movement_plane, movement_type)
            'category':         str,            # category name
            'measurement_unit': str,            # from category definition
            'primary': {
                'exercise_name':    str,
                'suggested_scheme': str,        # canonical scheme key
                'suggested_weight': float|None,
                'stimulus':         str,        # N / MT / MD / MS
            },
            'variations': [
                {
                    'exercise_name':    str,
                    'suggested_scheme': str,
                    'suggested_weight': float|None,
                    'stimulus':         str,
                },
                ...                             # 2-3 variations per slot
            ],
            'reason':           str,            # why this slot was filled this way
        }

    LOGIC:

    1. COMPUTE CATEGORY TARGETS
       For each cell in matrix_plan, for each category:
           target = category['weight']  (weekly target from the matrix)
       If block_targets specifies overrides for specific categories, apply those.
       Block targets take precedence over matrix weights when a block is active.

    2. COMPUTE COVERAGE SO FAR
       Filter records to this week (week_start <= date <= today).
       For each record, look up the exercise's cell via the exercise library.
       Build:
           category_sessions:  dict -- sessions completed per (cell_key, category_name)
           cell_exercises:     dict -- exercise names used per cell_key this week
           exercise_last_stim: dict -- last stimulus per exercise_name

       NOTE: This step absorbs the logic previously in check_intra_cell_variation
       and check_stimulus_interleaving (removed in V1.0.2). Those queries are now
       internal steps here rather than standalone flag outputs.

    3. COMPUTE REMAINING VALUE
       For each category:
           remaining = max(0, target - completed)
       Weight by category weight and remaining/target ratio.
       Sort categories descending by weighted remaining value.
       Categories with weight = 0 contribute no remaining value and are skipped.

    4. FILL SESSION SLOTS
       For each slot (up to the session size from block_targets or a default):
           Pick the highest-value unfilled category.
           Select a primary exercise:
               - Prefer exercises not already used in this cell this week (variety)
               - Prefer a stimulus not recently repeated for this exercise
                 (rotation)
           Select 2-3 variations from the same category satisfying the same
           stimulus type.
           For each candidate, compute suggested_weight via compute_ddm /
           compute_weight_suggestions if DDM is available. Uses the category's
           measurement_unit to determine which weight field to populate.

    5. RETURN SESSION
       Return the ordered list of slot dicts.

    CATEGORY-LEVEL OPERATION NOTES:
    - Targets are expressed in each category's own measurement unit. A carry
      category's deficit is measured in load x distance, not reps. A duration
      category's deficit is measured in seconds.
    - Categories within the same cell may have different units (e.g.
      Carry/Bracing has both LOAD_DISTANCE and DURATION sub-categories).
      Remaining value calculations across heterogeneous units use the
      normalized weight ratios, not raw unit values.
    - Exercise-to-category mapping is via the exercise library's
      (movement_plane, movement_type) for cell lookup. Within a cell, category
      matching uses exercise_examples as a soft hint; all exercises in a cell
      serve all categories by default unless further specified.
    """
    pass


###############################################################################
# SECTION 5: REMOVED IN V1.0.2
###############################################################################
# check_intra_cell_variation and check_stimulus_interleaving were removed.
# Their underlying queries — "which exercises used in this cell this week" and
# "what stimulus was last used for this exercise" — are now internal steps
# within build_session (Section 4.11). They are not standalone outputs.
# See TDS_MTRX_Updates_v2.md § REMOVE: Section 5 for rationale.

###############################################################################
# SECTION 6: VIEWS  (mtrx_functions.py)
###############################################################################
# All view functions accept the flat records list and other data structures as
# arguments and return a pandas DataFrame. The conversion pd.DataFrame(records)
# happens once at the top of each function. Derived columns are added via
# .apply().
#
# VIEW ARCHITECTURE NOTE — EXERCISE-TYPE-SPECIFIC VIEWS:
# Views 6.1, 6.2, 6.3 are VOLUME-centric: they compute stimulus classification,
# actual_reps, and actual_volume, all of which require non-null sets/reps/weight.
# Records with non-VOLUME measurement units (DURATION, DISTANCE, LOAD_DISTANCE,
# REPS_ONLY) are filtered out at the top of each view.
#
# Separate view functions for other exercise types (weightlifting, carries,
# cardio, etc.) are required. Each exercise type maps to a measurement unit
# (Section 1.4) and needs its own aggregation logic. Those views are future
# work — not specified in this version.

# ── 6.1 Summary Matrix ────────────────────────────────────────────────────────

SUMMARY_MATRIX_SPEC = """
def build_summary_matrix(user_id: int,
                         records: list,
                         exercises: dict,
                         today: datetime.date,
                         metric: str = 'volume',
                         period_start: datetime.date = None,
                         period_end: datetime.date = None) -> pd.DataFrame:
    # period_start / period_end define an optional date window.
    # When both are None, all records for the user are included (all-time).
    # Standard windows (last 30/60/90, YTD, TTM) are computed by the caller
    # (MtrxApp) before calling this function -- this function accepts explicit
    # dates only. This keeps the function pure and avoids embedding date
    # arithmetic inside a view.
    #
    # MtrxApp convenience method signatures:
    #   get_summary_matrix(user_id, metric, period='all_time')
    #   period options: 'all_time' | 'last_30' | 'last_60' | 'last_90' | 'ytd' | 'ttm'
    #   MtrxApp resolves the period string to (period_start, period_end) then
    #   calls build_summary_matrix with explicit dates.

    # Step 1 -- Filter and build DataFrame
    user_records = [r for r in records if r['user_id'] == user_id]
    if not user_records:
        return pd.DataFrame()

    df = pd.DataFrame(user_records)

    # Step 1b -- Filter to VOLUME-measurable records only
    # Non-VOLUME records lack sets/reps/weight and cannot be processed by
    # classify_stimulus or compute_actual_volume. See View Architecture Note.
    df = df[df['reps'].notna()]
    if df.empty:
        return pd.DataFrame()

    # Step 2 -- Add derived columns via .apply()
    df['stimulus']     = df['reps'].apply(classify_stimulus)
    df['actual_reps']  = df.apply(
        lambda r: compute_actual_reps(r['sets'], r['reps'], r['bonus_reps']),
        axis=1
    )
    df['laterality']   = df['exercise_name'].apply(
        lambda x: exercises.get(x.strip().lower(), {}).get('laterality', 'Bilateral')
    )
    df['actual_volume'] = df.apply(
        lambda r: compute_actual_volume(r['actual_reps'], r['weight'], r['laterality']),
        axis=1
    )

    # unrealized_pct depends on each row's own stimulus type (and therefore its
    # own adaptation_days). axis=1 passes the full row to the lambda so
    # r['stimulus'] is available per-row.
    df['unrealized_pct'] = df.apply(
        lambda r: compute_unrealized_vesting_pct(
            r['date'], today, STIMULUS_TABLE[r['stimulus']]['adaptation_days']
        ),
        axis=1
    )
    df['unrealized_volume']   = df.apply(
        lambda r: compute_unrealized_volume(r['actual_volume'], r['unrealized_pct']),
        axis=1
    )
    df['realized_volume']     = df.apply(
        lambda r: compute_realized_volume(r['actual_volume'], r['unrealized_volume']),
        axis=1
    )
    df['fatigue_volume']      = df.apply(
        lambda r: compute_fatigue_volume(
            r['actual_volume'], r['date'], today,
            STIMULUS_TABLE[r['stimulus']]['fatigue_days']
        ),
        axis=1
    )
    df['workout_type']        = df['exercise_name'].apply(
        lambda x: exercises.get(x.strip().lower(), {}).get('workout_type', 'Unknown')
    )
    df['non_fatigue_volume']  = df['unrealized_volume'] - df['fatigue_volume']

    # Step 3 -- Select value column based on metric toggle
    value_col = 'actual_volume' if metric == 'volume' else 'actual_reps'

    # Step 4 -- Aggregate: groupby workout_type / exercise_name / stimulus
    output = df.groupby(['workout_type', 'exercise_name', 'stimulus']).agg(
        actual_volume     = ('actual_volume',     'sum'),
        actual_reps       = ('actual_reps',       'sum'),
        unrealized_volume = ('unrealized_volume', 'sum'),
        realized_volume   = ('realized_volume',   'sum'),
        fatigue_volume    = ('fatigue_volume',    'sum'),
        non_fatigue_volume= ('non_fatigue_volume','sum'),
    ).reset_index()

    return output

OUTPUT FORMAT: build_summary_matrix returns long-format (tidy) data -- one row
per (workout_type, exercise_name, stimulus) combination. The view spec describes
a pivoted presentation with categorical rows (Realized, Adaptation, Fatigue,
Non-Fatigue, Total) and hierarchical columns (Total -> Workout Type -> Exercise).
That reshape is a display-layer concern and happens in mtrx_app.py, not here.
Long format is the correct data structure: it is pandas-native, directly
composable with matplotlib groupby charts, and does not bake any display
assumptions into the data pipeline.

COLOR LOGIC: Applied at the display layer only. For each (exercise_name, date)
cell in the vesting grid, build_color_matrix (Section 6.2b) produces a
blended_hex and blended_pct. Opacity of that hex = blended_pct as a decimal.
This is a display concern, not a data concern -- it is not stored in the DataFrame.
"""

# ── 6.2 Vesting Grid ──────────────────────────────────────────────────────────

VESTING_GRID_SPEC = """
def build_vesting_grid(user_id: int,
                       records: list,
                       exercises: dict,
                       today: datetime.date,
                       axis_filter: str = 'adaptation',
                       metric: str = 'volume') -> pd.DataFrame:

    user_records = [r for r in records if r['user_id'] == user_id]
    if not user_records:
        return pd.DataFrame()

    df = pd.DataFrame(user_records)

    # Filter to VOLUME-measurable records only (see View Architecture Note)
    df = df[df['reps'].notna()]
    if df.empty:
        return pd.DataFrame()

    df['stimulus']      = df['reps'].apply(classify_stimulus)
    df['actual_reps']   = df.apply(
        lambda r: compute_actual_reps(r['sets'], r['reps'], r['bonus_reps']), axis=1
    )
    df['laterality']    = df['exercise_name'].apply(
        lambda x: exercises.get(x.strip().lower(), {}).get('laterality', 'Bilateral')
    )
    df['actual_volume'] = df.apply(
        lambda r: compute_actual_volume(r['actual_reps'], r['weight'], r['laterality']),
        axis=1
    )
    df['unrealized_pct'] = df.apply(
        lambda r: compute_unrealized_vesting_pct(
            r['date'], today, STIMULUS_TABLE[r['stimulus']]['adaptation_days']
        ),
        axis=1
    )

    # Apply axis filter before pivot
    if axis_filter == 'adaptation':
        df = df[df['unrealized_pct'] > 0]

    value_col = 'actual_volume' if metric == 'volume' else 'actual_reps'

    # Pivot: rows = date, columns = exercise_name, values = selected metric
    grid = df.pivot_table(
        index='date',
        columns='exercise_name',
        values=value_col,
        aggfunc='sum',
        fill_value=0
    )

    return grid

COMPANION FUNCTION: build_color_matrix (Section 6.2b) takes identical inputs
and returns a dict keyed by (date, exercise_name) -> compute_blended_adaptation
output. Call both functions together; the display layer overlays the color map
onto the grid using the shared (date, exercise_name) key space. Two separate
return values (grid + color_map) rather than one combined structure keeps the
numeric data pipeline clean and independently testable.
"""

# ── 6.3 Program Balance View ──────────────────────────────────────────────────

PROGRAM_BALANCE_SPEC = """
def build_program_balance(user_id: int,
                          period_start: datetime.date,
                          period_end: datetime.date,
                          records: list,
                          exercises: dict,
                          matrix_plan: dict,
                          today: datetime.date,
                          view_mode: str = 'exposure') -> pd.DataFrame:

    # Filter records to user + period
    period_records = [
        r for r in records
        if r['user_id'] == user_id
        and period_start <= r['date'] <= period_end
    ]

    df = (pd.DataFrame(period_records) if period_records
          else pd.DataFrame(columns=['exercise_name', 'date']))

    # Filter to VOLUME-measurable records (see View Architecture Note)
    if not df.empty:
        df = df[df['reps'].notna()]

    # Add category coordinates to each record
    if not df.empty:
        df['movement_plane'] = df['exercise_name'].apply(
            lambda x: exercises.get(x.strip().lower(), {}).get('movement_plane', None)
        )
        df['movement_type']  = df['exercise_name'].apply(
            lambda x: exercises.get(x.strip().lower(), {}).get('movement_type', None)
        )
        df = df.dropna(subset=['movement_plane', 'movement_type'])

    # Compute derived columns once before the loop (used when view_mode is
    # 'volume' or 'reps'). Hoisted here so the work is done once, not 24 times.
    if not df.empty:
        df['actual_reps']   = df.apply(
            lambda r: compute_actual_reps(r['sets'], r['reps'], r['bonus_reps']),
            axis=1
        )
        df['laterality']    = df['exercise_name'].apply(
            lambda x: exercises.get(x.strip().lower(), {}).get('laterality', 'Bilateral')
        )
        df['actual_volume'] = df.apply(
            lambda r: compute_actual_volume(r['actual_reps'], r['weight'], r['laterality']),
            axis=1
        )

    # Iterate the 24 parent categories
    result_rows  = []
    period_days  = (period_end - period_start).days + 1
    days_elapsed = min((today - period_start).days + 1, period_days)

    for plane in MOVEMENT_PLANES_ORDERED:
        for mtype in MOVEMENT_TYPES_ORDERED:
            category_key    = (plane, mtype)
            categories      = matrix_plan.get(category_key, {}).get('categories', [])
            parent_weight   = sum(cat['weight'] for cat in categories)

            # period_target is None until resolved. The authoritative source
            # for session targets is the active training block's targets dict
            # (Section 3.6). parent_weight (sum of subcategory weights) is a
            # relative prioritization signal, not a session count.
            period_target = None

            cat_df   = (df[(df['movement_plane'] == plane) & (df['movement_type'] == mtype)]
                        if not df.empty else pd.DataFrame())
            sessions = len(cat_df['date'].unique()) if not cat_df.empty else 0

            # Status logic
            if parent_weight == 0:
                status = 'N/A'
            elif period_target is None:
                status = 'Unknown'   # Resolve when block targets are integrated
            elif sessions > period_target and period_target > 0:
                status = 'Exceeded'
            elif sessions == period_target and period_target > 0:
                status = 'Complete'
            elif today <= period_end:
                expected_by_now = period_target * (days_elapsed / period_days)
                status = 'On Track' if sessions >= expected_by_now else 'Behind'
            else:
                status = 'Behind'

            unique_exercises = (list(cat_df['exercise_name'].unique())
                                if not cat_df.empty else [])

            unique_stimuli = []
            if not cat_df.empty:
                cat_df = cat_df.copy()
                cat_df['stimulus'] = cat_df['reps'].apply(classify_stimulus)
                unique_stimuli = list(cat_df['stimulus'].unique())

            row = {
                'movement_plane':   plane,
                'movement_type':    mtype,
                'parent_weight':    parent_weight,
                'period_target':    period_target,
                'sessions':         sessions,
                'status':           status,
                'exercises_used':   unique_exercises,
                'stimuli_used':     unique_stimuli,
            }

            if view_mode in ('volume', 'reps') and not df.empty:
                cat_vals = df[
                    (df['movement_plane'] == plane) & (df['movement_type'] == mtype)
                ]
                row['category_volume'] = cat_vals['actual_volume'].sum() if not cat_vals.empty else 0
                row['category_reps']   = cat_vals['actual_reps'].sum()   if not cat_vals.empty else 0
            else:
                row['category_volume'] = 0
                row['category_reps']   = 0

            result_rows.append(row)

    return pd.DataFrame(result_rows)
"""

# ── 6.4 Weight Guidance View ──────────────────────────────────────────────────

def build_weight_guidance(exercise_name: str,
                          records: list,
                          today: datetime.date) -> dict:
    """
    Surfaces DDM-derived weight suggestions for all four canonical schemes.
    All suggestions are user-overridable. DDM recalculates automatically as
    new sessions are logged.

    CALLER CONTRACT: records is pre-filtered to a single user before being
    passed here (same contract as compute_ddm).
    """
    ddm = compute_ddm(exercise_name, records, today)

    if ddm is None:
        return {
            'exercise':    exercise_name,
            'ddm':         None,
            'suggestions': None,
            'note':        'Fewer than 2 canonical schemes have sessions in the last 90 days. Log at least one more scheme to establish a reliable DDM.',
        }

    return {
        'exercise':    exercise_name,
        'ddm':         round(ddm, 1),
        'suggestions': compute_weight_suggestions(ddm),
        'note':        'All suggestions are user-overridable.',
    }



###############################################################################
# SECTION 7: PROGRAM CALENDAR AND TRAINING BLOCKS
###############################################################################

# NOTE: The MULTI_USER_BOUNDARY_TABLE is defined in Section 2 of this document.
# Section 7 covers calendar utilities and training block cross-references only.

# ── 7.1 Program Calendar ─────────────────────────────────────────────────────
# The program calendar is not a stored table. Week bounds are derived
# arithmetically from PROGRAM_START_DATE.

def get_program_week_bounds(target_date: datetime.date) -> tuple:
    """
    Returns (week_start, week_end) for the program week containing target_date.
    datetime.timedelta arithmetic; floor division (//) for week number.
    No external calendar library.
    """
    days_offset = (target_date - PROGRAM_START_DATE).days
    if days_offset < 0:
        raise ValueError('Date precedes program start.')
    week_number = days_offset // 7
    week_start  = PROGRAM_START_DATE + datetime.timedelta(days=week_number * 7)
    week_end    = week_start + datetime.timedelta(days=6)
    return (week_start, week_end)

def get_block_label(target_date: datetime.date, weeks_per_block: int = 4) -> str:
    """
    Returns a human-readable block label such as 'Round 2 | Week 3'.

    DISPLAY-ONLY: This function is retained as a convenience for display
    labeling. It is not the authoritative source for block structure.
    Training blocks are user-defined programming periods (Section 3.6) with
    explicit start dates, end dates, and goal targets. The `weeks_per_block`
    parameter here is informational only -- blocks are no longer derived
    arithmetically from PROGRAM_START_DATE. For block progress tracking use
    db.get_active_block() and db.get_block_progress() (Section 3.6).
    """
    days_offset   = (target_date - PROGRAM_START_DATE).days
    week_number   = days_offset // 7
    block_number  = (week_number // weeks_per_block) + 1
    week_in_block = (week_number % weeks_per_block) + 1
    return f'Round {block_number} | Week {week_in_block}'

# ── 7.2 User-Defined Training Blocks ─────────────────────────────────────────
# Data structure and methods: see Section 3.6 (Training Blocks) of this document.
# This subsection provides cross-references and notes on the programming view.
#
# PLAN-VS-COMPLETED TRACKING:
#   Plan:      The 'targets' dict in the active block — what the user planned
#              to accomplish per category per week for this block.
#   Completed: Derived from records filtered to the block's date range,
#              aggregated by category and week.
#   Progress:  Weekly and cumulative completion ratios, displayed as a tracking
#              view showing each category's status (ahead / on track / behind /
#              not started).
#
# KEY METHODS (implemented in MtrxDatabase — see Section 3.6):
#   db.add_training_block(user_id, name, start_date, end_date, targets) -> int
#   db.get_active_block(user_id, as_of=None)                            -> dict|None
#   db.get_block_progress(user_id, block_id)                            -> dict
#
# WEEKLY BREAKDOWN:
#   Use get_program_week_bounds(date) to align records to program weeks.
#   get_block_progress iterates each week within the block's date range,
#   computes session counts per category from records, and compares against
#   the block's targets dict.
#
# NOTE ON get_block_label:
#   get_block_label (Section 7.1) produces display strings (e.g. 'Round 2 |
#   Week 3') using arithmetic on PROGRAM_START_DATE. This is independent of
#   user-defined block boundaries and useful for headings in views. It does not
#   reflect the start/end dates of the active training block.

TRAINING_BLOCKS_CROSS_REF = """
Section 3.6 defines:

  __training_blocks: dict[int, list[dict]]

  Example state:
  {
      1: [
          {
              'block_id':   1,
              'name':       'Spring Strength Block',
              'start_date': datetime.date(2026, 1, 5),
              'end_date':   datetime.date(2026, 3, 1),
              'targets': {
                  ('Sagittal', 'Push'): {
                      'Vertical Press':   {'weekly_target': 3, 'unit': 'VOLUME'},
                      'Horizontal Press': {'weekly_target': 3, 'unit': 'VOLUME'},
                  },
                  ('Sagittal', 'Hinge'): {
                      'Bilateral Hinge':  {'weekly_target': 2, 'unit': 'VOLUME'},
                  },
              },
          },
      ],
  }

  Methods: add_training_block, get_active_block, get_block_progress.
  Full spec in Section 3.6. This cross-reference exists so Section 7 remains
  the logical home for 'how do I look up the current block?' without
  duplicating the data structure definition.
"""



###############################################################################
# SECTION 8: COMPETITIVE PLATFORM  (Intent Specification)
###############################################################################
# Version 2 — intent only, no implementation spec.
# This section is under development and will be implemented after Version 1
# is complete. The data model from preceding sections is sufficient to support
# all requirements when the mechanics are defined.

COMPETITIVE_PLATFORM_SPEC = """
=== 8.1 Deterministic Scoring ===

The scoring system produces the same result for any matrix configuration given
the same inputs. It is not based on adherence percentages or
quality-of-execution deviation.


=== 8.2 Relative Performance ===

The core metric measures relative performance — how much a user moved toward
their own goal given their own constraints. Absolute comparisons (who lifted
more) are not the basis of competition.


=== 8.3 Handicap System ===

A handicap enables competition across users with fundamentally different
objectives, strategies, time commitments, ages, experience levels, and starting
points. The handicap adjusts scores so that a 62-year-old training 3 days/week
for functional fitness competes fairly against a 28-year-old training 5
days/week for powerlifting.


=== 8.4 Peer Group Comparison ===

Users are compared within peer groups — people with similar strategy,
configuration, and matrix selection.


=== 8.5 Multi-Dimensional Leaderboards ===

Leaderboards show ranked high scores across users, filterable by scope and
time period. Any combination of filters is valid.

Filter scope options:
  - Full library total (all exercises, all categories)
  - Specific exercise (e.g. Bench Press all-time volume)
  - Dimensionality slot (e.g. Horizontal Press exposure)
  - Plane x movement combination (e.g. Sagittal Push total volume)
  - Workout type

Period window options:
  - All-time
  - Last 30 / 60 / 90 days
  - YTD (year-to-date)
  - TTM (trailing twelve months)

Metric options: volume, session exposure (count), or other output measure.

Leaderboards are direct ranked aggregations of the records layer -- no separate
scoring model is required. This makes them independent of the V2 competitive
platform (scoring, handicaps, peer groups) and fully implementable in V1.

Note: multi-dimensional leaderboard filtering and competitive scoring / handicapping
are separate features. Leaderboards show raw ranked output; the competitive platform
(V2) layers relative performance and handicap adjustment on top.


=== 8.6 Radar Grid Positioning ===

Each user's matrix configuration places them on a radar/spider chart defined
by the preset matrix configurations. This positioning determines:
  - Eligibility for specific challenges
  - Peer group membership for direct comparison
  - Handicap calibration inputs


=== 8.7 Temporal Challenges ===

Time-bound competitive formats layered on top of the ongoing system:
  - Monthly competitions
  - Centralities-of-effort challenges (concentrated effort windows)
  - Other structured events


=== 8.8 Data Model Dependencies ===

  - User identity (Section 3.1) carries age and training_experience.
  - Plan history (Section 3.1b) records strategy over time, feeding
    radar grid positioning.
  - Workout records (Section 3.4) are the raw input to any scoring formula.
  - Preset matrix configs (Section 1.4) define the axes of the radar grid.
  - Training blocks (Section 3.6 / 7.2) provide the plan-vs-completed
    structure that scoring formulas can reference.
"""



###############################################################################
# SECTION 9: DATA ACCESS & VISUALIZATION LAYER  (Intent Specification)
###############################################################################
# Version 2 — intent only.
# This section is under development and will be implemented after Version 1
# is complete.

DATA_ACCESS_SPEC = """
=== 9.1 API Connection Points ===

The Python layer exposes structured, well-defined methods optimized for
AI agent consumption. Every data entity and derived metric is accessible
through a consistent interface that returns JSON-serializable dicts or
lists. The API surface is designed so that an LLM with tool-calling
capability can discover, query, and combine data without custom glue code.

Key design constraints:
  - Every public method on MtrxApp is a potential tool endpoint.
  - Return types are always dict, list[dict], or pd.DataFrame
    (convertible to dict via .to_dict()).
  - Method names and parameter names are self-documenting for LLM tool
    descriptions.
  - No method requires understanding internal state to call correctly.


=== 9.2 AI-Driven Jupyter Notebook Integration ===

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


=== 9.3 Dynamic Filtering & Complex Visualizations ===

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


=== 9.4 Agentic Programming Modification ===

The visualization agent can modify user programming based on its analysis:
  - Adjust category weights in the matrix.
  - Create or modify training blocks.
  - Suggest prescription engine parameter changes.

All modifications flow through the same MtrxApp methods used by direct
user interaction. The agent does not bypass the data access layer — it
uses the same API surface, ensuring all validation, plan history snapshots,
and invariants are maintained.
"""



###############################################################################
# IMPLEMENTATION ROADMAP
###############################################################################
# This section outlines the build sequence for the full application. Each stage
# produces testable output using only tools established by that stage.

IMPLEMENTATION_ROADMAP = """
=== STAGE 1 — Constants (mtrx_constants.py) ===

BUILD:   Define all constants from Section 1 in a single file.

TEST:    Import the file. Assert PRESET_MATRIX_CONFIGS['BLANK'] is present
         and contains exactly 24 cells (3 planes × 8 movement types). Verify
         all 24 categories have weight = 0. Print MEASUREMENT_UNITS and verify
         all 5 units are present (VOLUME, DURATION, DISTANCE, LOAD_DISTANCE,
         REPS_ONLY). Assert 'Neutral' is absent from MOVEMENT_PLANES. Assert
         PRIORITY_TARGETS and PRIORITY_OPTIONS are not defined anywhere in the
         module. No test framework needed — assertion checks and print.


=== STAGE 2 — Pure Functions (mtrx_functions.py) ===

BUILD ORDER:
1. classify_stimulus            -- test all four boundary cases: 1, 3, 4, 6, 7, 15, 16, 100
2. compute_actual_reps          -- test bilateral and unilateral cases
   compute_actual_volume
3. compute_unrealized_vesting_pct -- test day 0 (1.0), day = adaptation_days (0.0),
                                     day past window (0.0 clamped)
4. compute_unrealized_volume    -- verify accounting identity:
   compute_realized_volume         unrealized + realized == actual_volume
   compute_fatigue_volume
5. compute_ddm                  -- build stub records list manually; test with 0,
   compute_weight_suggestions      1, 2, 3, 4 qualifying schemes in the 90-day window
6. compute_blended_adaptation   -- test with single-stimulus input (should return
                                     that stimulus's pure color and pct)
7. build_session                -- test with manually constructed hierarchical matrix,
                                     records, and exercises. Test cases:
                                     - Empty week (no records): fills slots from
                                       highest-weight categories
                                     - Partially completed week: shifts to underserved
                                       categories
                                     - Off-plan workout logged: absorbs and recalibrates
                                       remaining slots
                                     - Categories with different measurement units:
                                       verify unit-appropriate targets and suggestions
                                     - Verify each slot has primary + variations
                                       from same category

NOTE: check_intra_cell_variation and check_stimulus_interleaving are removed.
Their logic is internal to build_session (Section 4.11). No standalone tests.

TEST PATTERN: Each function is called directly with hardcoded inputs and the
result is printed and verified by hand.


=== STAGE 3 — Database (mtrx_database.py) ===

BUILD ORDER:
1. __users          + add_user(username, display_name, email,
                               age=None, training_experience=None,
                               preset_key=None)
                      + get_user
                    -- verify counter increments, duplicate rejection,
                       expanded fields stored, preset_key seeds matrix correctly
2. __measurements   + add_measurement + get_bodyweight_on_date
                      + delete_measurement
                    -- verify sort invariant, date boundary behavior,
                       delete by measurement_id
3. __exercises      + add_exercise + get_exercise + update_exercise
                      + get_all_exercises + delete_exercise
                    -- verify dedup, vocab validation, name-change rejection,
                       delete blocked when records reference the exercise
4. __records        + add_record + get_records + delete_record
                    -- verify flat list grows, bodyweight auto-resolution,
                       filter combinations, delete by record_id;
                       record schema includes nullable duration_seconds and
                       distance_meters; add_record validates required fields
                       per category's measurement_unit
5. __matrix_plans   seeded at user creation via deepcopy of PRESET_MATRIX_CONFIGS
                    + update_matrix_cell(user_id, movement_plane, movement_type,
                                         categories: list)
                      + add_category(user_id, movement_plane, movement_type,
                                     name, weight, measurement_unit,
                                     exercise_examples=None)
                      + get_matrix_plan(user_id)
                      + get_parent_weight(user_id, movement_plane, movement_type)
                    -- verify deepcopy isolation (two users don't share lists),
                       update_matrix_cell triggers save_config_snapshot,
                       add_category appends without destroying existing;
                       remove get_cell_priority (no longer exists)
6. __plan_history   + save_config_snapshot(user_id)
                      + get_active_config(user_id)
                      + get_plan_history(user_id)
                    -- verify snapshot appended on every update_matrix_cell call;
                       verify get_active_config returns most recent snapshot;
                       verify snapshots are deep copies (mutation isolation);
                       verify config_counter increments
7. __training_blocks + add_training_block(user_id, name, start_date, end_date,
                                           targets)
                       + get_active_block(user_id, as_of=None)
                       + get_block_progress(user_id, block_id)
                     -- verify end_date > start_date validation;
                        verify target categories validated against user's matrix;
                        verify measurement units match category definitions;
                        verify get_block_progress returns plan vs. completed
                        breakdown with weekly granularity;
                        verify block_counter increments

TEST: After each entity group is added, print the database __repr__ and inspect
one get_* call. Use a safe_call / try-except wrapper pattern.


=== STAGE 4 — App Controller (mtrx_app.py) ===

BUILD: MtrxApp class wrapping MtrxDatabase and calling mtrx_functions.

KEY METHODS:
  register_user(username, display_name, email,
                age=None, training_experience=None,
                preset_key=None)               -> db.add_user (passes preset_key)
  log_measurement(user_id, date, bodyweight, ...) -> db.add_measurement
  add_exercise(...)                            -> db.add_exercise
  log_workout(user_id, date, exercise_name, ...)
                                               -> db.add_record
                                                  compute_ddm (if enough history)
                                                  compute_weight_suggestions
                                                  returns:
                                                    {'record_id':        int,
                                                     'ddm':              float|None,
                                                     'weight_suggestions': dict|None}
                                                  NOTE: repeat_exercise_flag and
                                                  repeat_stimulus_flag removed.
                                                  Flag functions removed in V1.0.2.
  generate_session(user_id, date)              -> assembles inputs from database,
                                                  calls build_session, returns
                                                  session list
  get_weight_guidance(exercise_name, user_id)  -> db.get_records(user_id) then
                                                  build_weight_guidance
  get_summary_matrix(user_id, metric)          -> build_summary_matrix
  get_vesting_grid(user_id, axis_filter, metric) -> build_vesting_grid
  get_program_balance(user_id, period, view_mode) -> build_program_balance
  update_matrix_cell(user_id, plane, mtype,
                     categories)               -> db.update_matrix_cell
                                                  (triggers save_config_snapshot)
  add_training_block(user_id, name,
                     start_date, end_date,
                     targets)                  -> db.add_training_block
  get_block_progress(user_id, block_id)        -> db.get_block_progress
  get_plan_history(user_id)                    -> db.get_plan_history

TEST: Register 2 users with different presets. Add exercises. Log workouts
including non-VOLUME measurement units. Call generate_session. Verify block
progress tracking. Verify plan history grows on matrix changes.


=== STAGE 5 — Visualization & Reports ===

BUILD:
  build_program_balance   -- iterates 24 parent categories; VOLUME records
                             only (see View Architecture Note in Section 6);
                             period_target = None until block targets are
                             integrated; parent_weight exposed as relative
                             prioritization signal
  Block Progress view     -- new view: plan vs. completed per category across
                             the active training block; weekly granularity;
                             status color coding (ahead / on track / behind /
                             not started)

NOTE: All views operate on the hierarchical matrix structure. Cell-level
aggregations sum across categories.


=== STAGE 6 — Persistence ===

BUILD: Serialization / deserialization of full MtrxDatabase state.

Changes from V1.0.1:
  - serialize / deserialize: handle hierarchical __matrix_plans structure
    (category dicts with lists within each cell); tuple keys use existing
    '|'.join() pattern
  - Add plan_history and config_counter to serialized state
  - Add training_blocks and block_counter to serialized state
  - Record schema includes nullable duration_seconds and distance_meters
  - SCHEMA_VERSION = 2

TEST: Serialize to JSON, reload, assert all values are identical including
nested category lists, plan history snapshots, and training block targets.


=== STAGE 7 — Competitive Platform (Version 2) ===

Scoring, handicapping, leaderboards, and temporal challenges are implemented
in this stage when the mechanics are defined. The data model from Stages 1–6
requires no structural changes to support this stage. Deliverables:
  - Scoring constants and calculation functions (mtrx_constants.py /
    mtrx_functions.py)
  - Leaderboard and peer group entities (mtrx_database.py)
  - Leaderboard views and radar grid visualization (mtrx_app.py)

See Section 8 for full intent specification.


=== STAGE 8 — AI Visualization Layer (Version 2) ===

The AI-driven data access and visualization layer is implemented in this stage.
Deliverables:
  - Ensure all MtrxApp methods return JSON-serializable structures suitable
    for LLM tool-calling
  - Build Jupyter notebook templates for common analyses
  - Define the agent's tool manifest (method names, parameter schemas,
    return types) for LLM integration
  - Implement agentic programming modification flows (matrix adjustment,
    block creation) through the existing API surface

See Section 9 for full intent specification.
"""
