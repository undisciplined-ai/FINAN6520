"""
================================================================================
  MTRX — Technical Design Specification  (V2)
  FINAN 6520 | Final Project | Harmer, Kai | U0895215
================================================================================
"""

# ── Document Purpose ──────────────────────────────────────────────────────────
PURPOSE = """
This document is a complete technical design specification for the MTRX workout
tracking application. It maps every component of the system described in the
Assignment Context to the specific Python constructs, data structures, and
libraries covered in Modules 1-13. The resolution target is: a senior developer
should be able to build the full application using only this document and the
course materials, without external references.

The document is organized into seven sections mirroring the system's logical
layers, followed by an optional Extra Credit section containing the full
implementation roadmap.
"""

# ── System Architecture Overview ──────────────────────────────────────────────
ARCHITECTURE = """
The application is organized into four files with a strict dependency hierarchy.
Each layer imports only from the layer(s) below it.

    mtrx_constants.py   <- no imports; pure data definitions
            |
    mtrx_functions.py   <- imports: mtrx_constants, datetime, math
            |
    mtrx_database.py    <- imports: mtrx_constants, mtrx_functions, datetime, pickle
            |
    mtrx_app.py         <- imports: mtrx_database, mtrx_functions, pandas, matplotlib

WHY THIS SEPARATION ELIMINATES TELEPHONE-GAME ERRORS:
Every derived metric is defined once, as a pure function in mtrx_functions.py,
with explicit inputs and outputs. The database never recomputes anything -- it
stores only raw records. The app never accesses raw state directly -- it calls
database methods and passes the results to functions. A bug in any calculation
is isolated to one function in one file.

STRUCTURAL ANALOG IN THE COURSE:
This is the Module 12 Bank system pattern -- Database holding private state,
Branch as the public controller -- extended with a dedicated pure-function layer
and a constants module.
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

# ── 1.3 Priority Targets ──────────────────────────────────────────────────────

PRIORITY_TARGETS = {
    'High':   3,
    'Medium': 2,
    'Low':    1,
    'N/A':    0,
}

# ── 1.4 Default Matrix Grid ───────────────────────────────────────────────────
# Key: (movement_plane, movement_type) tuple -- the canonical join key between
# the Exercise Library and the Matrix. This same key structure is used in every
# matrix_plan dict (Section 3.5), so lookups are direct and consistent everywhere.

DEFAULT_MATRIX_GRID = {
    ('Sagittal',   'Accessory/Isolation'): 'Low',
    ('Sagittal',   'Carry/Bracing'):       'High',
    ('Sagittal',   'Gait/Locomotion'):     'High',
    ('Sagittal',   'Hinge'):               'High',
    ('Sagittal',   'Pull'):                'High',
    ('Sagittal',   'Push'):                'High',
    ('Sagittal',   'Rotation'):            'N/A',
    ('Sagittal',   'Squat'):               'High',
    ('Frontal',    'Accessory/Isolation'): 'Low',
    ('Frontal',    'Carry/Bracing'):       'Medium',
    ('Frontal',    'Gait/Locomotion'):     'Medium',
    ('Frontal',    'Hinge'):               'N/A',
    ('Frontal',    'Pull'):                'Low',
    ('Frontal',    'Push'):                'N/A',
    ('Frontal',    'Rotation'):            'N/A',
    ('Frontal',    'Squat'):               'Medium',
    ('Transverse', 'Accessory/Isolation'): 'Low',
    ('Transverse', 'Carry/Bracing'):       'Medium',
    ('Transverse', 'Gait/Locomotion'):     'Medium',
    ('Transverse', 'Hinge'):               'N/A',
    ('Transverse', 'Pull'):                'Medium',
    ('Transverse', 'Push'):                'Medium',
    ('Transverse', 'Rotation'):            'High',
    ('Transverse', 'Squat'):               'N/A',
    ('Neutral',    'Accessory/Isolation'): 'N/A',
    ('Neutral',    'Carry/Bracing'):       'N/A',
    ('Neutral',    'Gait/Locomotion'):     'N/A',
    ('Neutral',    'Hinge'):               'N/A',
    ('Neutral',    'Pull'):                'N/A',
    ('Neutral',    'Push'):                'N/A',
    ('Neutral',    'Rotation'):            'N/A',
    ('Neutral',    'Squat'):               'N/A',
}

# ── 1.5 Controlled Vocabulary Lists ───────────────────────────────────────────
# These are the validation sets used on data entry. Any write method checks
# membership before accepting a value: if value not in VALID_LIST: raise ValueError
# This is a Module 3 membership check (in).

MOVEMENT_PLANES  = ['Sagittal', 'Frontal', 'Transverse', 'Neutral']
MOVEMENT_TYPES   = ['Accessory/Isolation', 'Carry/Bracing', 'Gait/Locomotion',
                    'Hinge', 'Pull', 'Push', 'Rotation', 'Squat']
WORKOUT_TYPES    = ['Conditioning', 'Weightlifting', 'Mobility', 'Recovery']
LATERALITY       = ['Bilateral', 'Unilateral']
LOAD_TYPES       = ['Band', 'Barbell', 'Bodyweight', 'Cable', 'Curl Bar',
                    'Dumbbell', 'Kettlebell', 'Machine', 'Medicineball', 'N/A']
PRIORITY_OPTIONS = ['High', 'Medium', 'Low', 'N/A']

# ── 1.6 Program Calendar Anchor ───────────────────────────────────────────────
# All week and block calculations derive from this single anchor. There is no
# stored calendar table -- weeks are computed arithmetically at runtime (Section 7).

import datetime
PROGRAM_START_DATE = datetime.date(2026, 1, 5)   # First Monday of the program


###############################################################################
# SECTION 2: CLASS ARCHITECTURE  (mtrx_database.py)
###############################################################################
# Two classes. The pattern mirrors the Module 12 Bank system exactly.

CLASS_ARCHITECTURE_NOTES = """
-- 2.1  MtrxDatabase --
The internal state store. All five data entities live here as private attributes.
No external code accesses them directly.

    class MtrxDatabase:

        def __init__(self):
            self.__user_counter      = 1
            self.__measure_counter   = 1
            self.__record_counter    = 1

            self.__users             = {}   # dict[int, dict]
            self.__measurements      = {}   # dict[int, list[dict]]
            self.__exercises         = {}   # dict[str, dict]
            self.__records           = []   # list[dict]
            self.__matrix_plans      = {}   # dict[int, dict[tuple, str]]

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
        'email': 'kai@example.com', 'join_date': datetime.date(2026, 1, 5)},
    2: {'username': 'jdoe',    'display_name': 'Jane Doe',
        'email': 'jane@example.com', 'join_date': datetime.date(2026, 1, 12)},
}

WHY dict[int, dict] KEYED BY user_id:
Every other entity references user_id as a foreign key. O(1) lookup at every
join point. Username and email uniqueness are enforced on write using a generator
expression over values -- this is a one-time cost at insert, not a structural
requirement.
"""

USERS_METHODS = """
def add_user(self, username: str, display_name: str, email: str) -> int:
    # 1. Validate: if any(u['username'] == username for u in self.__users.values()): raise ValueError
    # 2. Validate: if any(u['email'] == email for u in self.__users.values()): raise ValueError
    # 3. user_id = self.__user_counter
    # 4. self.__users[user_id] = {'username': username, 'display_name': display_name,
    #                              'email': email, 'join_date': datetime.date.today()}
    # 5. self.__matrix_plans[user_id] = dict(DEFAULT_MATRIX_GRID)  # seed from defaults
    # 6. self.__measurements[user_id] = []                         # initialize empty list
    # 7. self.__user_counter += 1
    # 8. return user_id

def get_user(self, user_id: int) -> dict:
    # if user_id not in self.__users: raise KeyError
    # return dict(self.__users[user_id])   # return a copy, not the live dict

def get_all_users(self) -> dict:
    # return dict(self.__users)
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
reverse iteration finds this in O(n) where n is measurements per user (small).
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
user selects an exercise to log). The canonical Matrix join key --
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
    # 3. for field, value in kwargs.items():
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
"""

# ── 3.4 Workout Records ───────────────────────────────────────────────────────

RECORDS_STRUCTURE = """
self.__records: list[dict]

Example state:
[
    {
        'record_id':     1,
        'user_id':       1,
        'date':          datetime.date(2026, 1, 12),
        'exercise_name': 'Bench Press',
        'sets':          3,
        'reps':          5,
        'bonus_reps':    1,
        'weight':        255.0,
        'rpe':           8.0,
        'load_type':     'Barbell',
        'notes':         '',
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

BODYWEIGHT EXERCISE HANDLING:
When load_type == 'Bodyweight', weight is resolved at log time by calling
get_bodyweight_on_date(user_id, date) before the record is created. The stored
record is always self-contained -- no secondary lookup is needed at read time.
"""

RECORDS_METHODS = """
def add_record(self, user_id: int, date: datetime.date, exercise_name: str,
               sets: int, reps: int, bonus_reps: int, weight: float,
               rpe: float, load_type: str, notes: str = '') -> int:
    # 1. Validate user_id exists
    # 2. exercise = self.get_exercise(exercise_name)  -- raises KeyError if not found
    # 3. Validate load_type in LOAD_TYPES
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
    # 7. self.__records.append({'record_id': record_id, 'user_id': user_id,
    #                           'date': date, 'exercise_name': exercise_name,
    #                           'sets': sets, 'reps': reps, 'bonus_reps': bonus_reps,
    #                           'weight': float(weight), 'rpe': float(rpe),
    #                           'load_type': load_type, 'notes': notes})
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
    # Chained list comprehensions (Module 3). For view functions, the caller
    # either passes user_id only and does further filtering in pandas, or passes
    # all filters and receives a minimal pre-filtered list.
"""

# ── 3.5 Matrix Plan ───────────────────────────────────────────────────────────

MATRIX_PLAN_STRUCTURE = """
self.__matrix_plans: dict[int, dict[tuple, str]]

Example state:
{
    1: {
        ('Sagittal',   'Push'):  'High',
        ('Sagittal',   'Pull'):  'High',
        ('Frontal',    'Squat'): 'Medium',
        ...
    },
    2: {
        ('Sagittal',   'Push'):  'High',
        ('Frontal',    'Squat'): 'Low',     # User 2 modified this cell
        ...
    },
}

WHY dict[tuple, str] FOR THE INNER STRUCTURE:
(movement_plane, movement_type) is the canonical join key defined in the spec.
A tuple key is immutable, hashable, and enables direct O(1) cell lookup:
matrix_plans[user_id][(plane, type)]. The alternative -- a nested dict[plane][type]
-- requires two accesses and complicates iteration. The tuple approach also aligns
with DEFAULT_MATRIX_GRID in mtrx_constants.py, which uses the same key structure,
making dict(DEFAULT_MATRIX_GRID) a valid seed copy.

SEEDING: Called automatically inside add_user. Uses dict(DEFAULT_MATRIX_GRID) --
a shallow copy is correct here because all values are strings (immutable); no
deep copy needed.
"""

MATRIX_PLAN_METHODS = """
def seed_matrix_plan(self, user_id: int) -> None:
    # self.__matrix_plans[user_id] = dict(DEFAULT_MATRIX_GRID)
    # (called internally by add_user; not exposed publicly)

def update_matrix_cell(self, user_id: int, movement_plane: str,
                       movement_type: str, priority: str) -> None:
    # 1. Validate user_id, movement_plane in MOVEMENT_PLANES,
    #    movement_type in MOVEMENT_TYPES
    # 2. Validate priority in PRIORITY_OPTIONS
    # 3. self.__matrix_plans[user_id][(movement_plane, movement_type)] = priority

def get_matrix_plan(self, user_id: int) -> dict:
    # return dict(self.__matrix_plans[user_id])   # copy

def get_cell_priority(self, user_id: int, movement_plane: str,
                      movement_type: str) -> str:
    # return self.__matrix_plans[user_id][(movement_plane, movement_type)]
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
    count (Module 5). max and min clamp to [0, 1] (Module 2 built-ins). No
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
                user_id: int,
                records: list,
                today: datetime.date,
                lookback_days: int = 90) -> float | None:
    """
    Computes the Desirable Difficulty Max for a given user and exercise.

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
    and one exercise) is handled cleanly by list comprehension and sorted() --
    both Module 3. Constructing a DataFrame for these lookups would add overhead
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

        # Filter to matching records within the recency window (Module 3 list comprehension)
        candidates = [
            r for r in records
            if r['user_id'] == user_id
            and r['exercise_name'].strip().lower() == exercise_key
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
    Dict comprehension (Module 3) over CANONICAL_SCHEMES. Result is a dict of
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

    Hex-to-RGB uses string slicing and int(string, 16) -- base-16 integer cast
    introduced in Module 2 type casting. RGB-to-hex uses an f-string format
    specifier (Module 3). No external color library is used or needed.
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
        r = int(hex_color[1:3], 16)   # Module 2 string slicing + base-16 cast
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r_blend += weight * r
        g_blend += weight * g
        b_blend += weight * b

    blended_hex = '#{:02X}{:02X}{:02X}'.format(int(r_blend), int(g_blend), int(b_blend))
    return {'blended_pct': round(blended_pct, 4), 'blended_hex': blended_hex}


###############################################################################
# SECTION 5: SYSTEM BEHAVIORS  (mtrx_functions.py)
###############################################################################
# Stateless flag functions. They take data as arguments and return a boolean.
# The system surfaces the flag; the user decides.

# ── 5.1 Intra-Cell Exercise Variation Flag ────────────────────────────────────

def check_intra_cell_variation(user_id: int,
                                week_start: datetime.date,
                                week_end: datetime.date,
                                movement_plane: str,
                                movement_type: str,
                                exercise_name: str,
                                records: list,
                                exercises: dict) -> bool:
    """
    Returns True if the given exercise has already been used in this Matrix cell
    during the current program week -- flagging a repeat.

    WHY A set FOR used_in_cell:
    Membership check is the only operation. set provides O(1) lookup (Module 2).
    Building it with .add() in a loop (Module 3) is clear and does not depend on
    sorted order.
    """
    # Step 1 -- Filter records to this user and this week
    week_records = [
        r for r in records
        if r['user_id'] == user_id
        and week_start <= r['date'] <= week_end
    ]

    # Step 2 -- Build a set of exercise names already used in this cell this week
    used_in_cell = set()
    for r in week_records:
        ex_key = r['exercise_name'].strip().lower()
        if ex_key in exercises:
            ex = exercises[ex_key]
            if (ex['movement_plane'] == movement_plane
                    and ex['movement_type'] == movement_type):
                used_in_cell.add(ex_key)

    # Step 3 -- Check if the incoming exercise is already in the set
    return exercise_name.strip().lower() in used_in_cell

# ── 5.2 Stimulus Interleaving Flag ───────────────────────────────────────────

def check_stimulus_interleaving(user_id: int,
                                 exercise_name: str,
                                 current_reps: int,
                                 records: list) -> bool:
    """
    Returns True if the current session uses the same stimulus type as the most
    recent prior session of the same exercise -- flagging a consecutive repeat.
    """
    exercise_key    = exercise_name.strip().lower()
    current_stimulus = classify_stimulus(current_reps)

    prior = [
        r for r in records
        if r['user_id'] == user_id
        and r['exercise_name'].strip().lower() == exercise_key
    ]

    if not prior:
        return False   # No prior session to compare against

    most_recent_prior = sorted(prior, key=lambda r: r['date'], reverse=True)[0]
    prior_stimulus    = classify_stimulus(most_recent_prior['reps'])

    return current_stimulus == prior_stimulus


###############################################################################
# SECTION 6: VIEWS  (mtrx_functions.py)
###############################################################################
# All view functions accept the flat records list and other data structures as
# arguments and return a pandas DataFrame. The conversion pd.DataFrame(records)
# happens once at the top of each function. Derived columns are added via
# .apply() (Module 4).

# ── 6.1 Summary Matrix ────────────────────────────────────────────────────────

SUMMARY_MATRIX_SPEC = """
def build_summary_matrix(user_id: int,
                         records: list,
                         exercises: dict,
                         today: datetime.date,
                         metric: str = 'volume') -> pd.DataFrame:

    # Step 1 -- Filter and build DataFrame
    user_records = [r for r in records if r['user_id'] == user_id]
    if not user_records:
        return pd.DataFrame()

    df = pd.DataFrame(user_records)

    # Step 2 -- Add derived columns via .apply() (Module 4)
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

    # Add cell coordinates to each record
    if not df.empty:
        df['movement_plane'] = df['exercise_name'].apply(
            lambda x: exercises.get(x.strip().lower(), {}).get('movement_plane', None)
        )
        df['movement_type']  = df['exercise_name'].apply(
            lambda x: exercises.get(x.strip().lower(), {}).get('movement_type', None)
        )
        df = df.dropna(subset=['movement_plane', 'movement_type'])

    # Build the 4x8 output grid
    result_rows  = []
    period_days  = (period_end - period_start).days + 1
    days_elapsed = min((today - period_start).days + 1, period_days)

    for plane in MOVEMENT_PLANES:
        for mtype in MOVEMENT_TYPES:
            cell_key     = (plane, mtype)
            priority     = matrix_plan.get(cell_key, 'N/A')
            weekly_target = PRIORITY_TARGETS[priority]
            period_target = round(weekly_target * (period_days / 7))

            cell_df  = (df[(df['movement_plane'] == plane) & (df['movement_type'] == mtype)]
                        if not df.empty else pd.DataFrame())
            sessions = len(cell_df['date'].unique()) if not cell_df.empty else 0

            # Status logic -- ordered if/elif mirrors spec language exactly
            if priority == 'N/A':
                status = 'N/A'
            elif sessions > period_target and period_target > 0:
                status = 'Exceeded'
            elif sessions == period_target and period_target > 0:
                status = 'Complete'
            elif today <= period_end:
                expected_by_now = period_target * (days_elapsed / period_days)
                status = 'On Track' if sessions >= expected_by_now else 'Behind'
            else:
                status = 'Behind'

            unique_exercises = (list(cell_df['exercise_name'].unique())
                                if not cell_df.empty else [])
            repeat_exercise  = len(unique_exercises) < sessions

            unique_stimuli = []
            if not cell_df.empty:
                cell_df = cell_df.copy()
                cell_df['stimulus'] = cell_df['reps'].apply(classify_stimulus)
                unique_stimuli = list(cell_df['stimulus'].unique())

            row = {
                'movement_plane':  plane,
                'movement_type':   mtype,
                'priority':        priority,
                'period_target':   period_target,
                'sessions':        sessions,
                'status':          status,
                'exercises_used':  unique_exercises,
                'repeat_flag':     repeat_exercise,
                'stimuli_used':    unique_stimuli,
            }

            if view_mode in ('volume', 'reps') and not df.empty:
                df_temp = df.copy()
                df_temp['actual_reps']   = df_temp.apply(
                    lambda r: compute_actual_reps(r['sets'], r['reps'], r['bonus_reps']),
                    axis=1
                )
                df_temp['laterality']    = df_temp['exercise_name'].apply(
                    lambda x: exercises.get(x.strip().lower(), {}).get('laterality', 'Bilateral')
                )
                df_temp['actual_volume'] = df_temp.apply(
                    lambda r: compute_actual_volume(r['actual_reps'], r['weight'], r['laterality']),
                    axis=1
                )
                cell_vals = df_temp[
                    (df_temp['movement_plane'] == plane) & (df_temp['movement_type'] == mtype)
                ]
                row['cell_volume'] = cell_vals['actual_volume'].sum() if not cell_vals.empty else 0
                row['cell_reps']   = cell_vals['actual_reps'].sum()   if not cell_vals.empty else 0
            else:
                row['cell_volume'] = 0
                row['cell_reps']   = 0

            result_rows.append(row)

    return pd.DataFrame(result_rows)
"""

# ── 6.4 Weight Guidance View ──────────────────────────────────────────────────

def build_weight_guidance(exercise_name: str,
                          user_id: int,
                          records: list,
                          today: datetime.date) -> dict:
    """
    Surfaces DDM-derived weight suggestions for all four canonical schemes.
    All suggestions are user-overridable. DDM recalculates automatically as
    new sessions are logged.
    """
    ddm = compute_ddm(exercise_name, user_id, records, today)

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
# SECTION 7: MULTI-USER BOUNDARIES AND PROGRAM CALENDAR
###############################################################################

MULTI_USER_BOUNDARY_TABLE = """
| Component              | Scope                              | Implementation                                    |
|------------------------|------------------------------------|---------------------------------------------------|
| Exercise Library       | Shared -- all users                | self.__exercises single dict in MtrxDatabase      |
| System Constants       | Shared -- all users                | Module-level constants in mtrx_constants.py       |
| Program Calendar       | Shared -- all users                | Computed from PROGRAM_START_DATE                  |
| Default Matrix Grid    | Shared seed, copied per user       | dict(DEFAULT_MATRIX_GRID) shallow copy            |
| Workout Records        | Per user                           | user_id field on every record; filtered at query  |
| User Measurements      | Per user                           | self.__measurements keyed by user_id              |
| Matrix Plan            | Per user after registration        | self.__matrix_plans[user_id] independent per user |
| DDM                    | Per user per exercise              | Computed from filtered records; no shared state   |
"""

# ── 7.2 Program Calendar ──────────────────────────────────────────────────────
# The program calendar is not a stored table. All week and block information is
# derived arithmetically from PROGRAM_START_DATE.

def get_program_week_bounds(target_date: datetime.date) -> tuple:
    """
    Returns (week_start, week_end) for the program week containing target_date.
    datetime.timedelta arithmetic (Module 5). Floor division (//) for week
    number (Module 2). No external calendar library.
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
    """
    days_offset   = (target_date - PROGRAM_START_DATE).days
    week_number   = days_offset // 7
    block_number  = (week_number // weeks_per_block) + 1
    week_in_block = (week_number % weeks_per_block) + 1
    return f'Round {block_number} | Week {week_in_block}'


###############################################################################
# EXTRA CREDIT: IMPLEMENTATION ROADMAP
###############################################################################
# This section outlines the build sequence for the full application. Each stage
# produces testable output using only tools established by that stage.

EXTRA_CREDIT_ROADMAP = """
=== STAGE 1 — Constants (mtrx_constants.py) ===

BUILD:   Define all constants from Section 1 in a single file.
TEST:    Import the file and print STIMULUS_TABLE, DEFAULT_MATRIX_GRID,
         CANONICAL_SCHEMES. Verify all 32 matrix cells are present. No test
         framework needed -- visual inspection via print.
MODULE:  Module 2 (dicts, lists, sets).


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
7. check_intra_cell_variation   -- test with manually constructed records + exercises
   check_stimulus_interleaving

TEST PATTERN: Each function is called directly with hardcoded inputs and the
result is printed and verified by hand. This is the Module 6 homework pattern
applied to each function.
MODULES:  1-5 (arithmetic, control flow, datetime, math).


=== STAGE 3 — Database (mtrx_database.py) ===

BUILD ORDER:
1. __users          + add_user + get_user
                    -- verify counter increments, duplicate rejection
2. __measurements   + add_measurement + get_bodyweight_on_date
                    -- verify sort invariant and date boundary behavior
3. __exercises      + add_exercise + get_exercise + update_exercise
                    -- verify dedup and vocab validation
4. __records        + add_record + get_records
                    -- verify flat list grows, bodyweight auto-resolution,
                       filter combinations
5. __matrix_plans   seeded at user creation
                    + update_matrix_cell + get_cell_priority
                    -- verify seed matches defaults, update persists

TEST: After each entity group is added, print the database __repr__ and inspect
one get_* call. Use the same safe_call / try-except wrapper pattern from the
homework checker files.
MODULES: 8-12 (OOP, encapsulation, __init__, __repr__, private attributes).


=== STAGE 4 — App Controller (mtrx_app.py) ===

BUILD: MtrxApp class wrapping MtrxDatabase and calling mtrx_functions.

KEY METHODS:
  register_user(username, display_name, email)        -> db.add_user
  log_measurement(user_id, date, bodyweight, ...)     -> db.add_measurement
  add_exercise(...)                                   -> db.add_exercise
  log_workout(user_id, date, exercise_name, ...)      -> db.add_record
                                                         check_intra_cell_variation
                                                         check_stimulus_interleaving
                                                         returns record_id + flags
  get_weight_guidance(exercise_name, user_id)         -> build_weight_guidance
  get_summary_matrix(user_id, metric)                 -> build_summary_matrix
  get_vesting_grid(user_id, axis_filter, metric)      -> build_vesting_grid
  get_program_balance(user_id, period, view_mode)     -> build_program_balance
  update_matrix_cell(user_id, plane, type, priority)  -> db.update_matrix_cell

log_workout RETURN VALUE:
  {
      'record_id':            int,
      'repeat_exercise_flag': bool,
      'repeat_stimulus_flag': bool,
      'ddm':                  float | None,
      'weight_suggestions':   dict | None,
  }

TEST: Register 2 users, add 5 exercises, log 10 workouts across 2 weeks, call
all four view functions, print outputs.
MODULES: 8-12 (OOP, composition -- MtrxApp holds MtrxDatabase as private attr).


=== STAGE 5 — Views and Visualization ===

BUILD: Finalize view functions. Add matplotlib display functions in mtrx_app.py.

  Vesting Grid       -> color-coded heatmap; per-cell hex + opacity via
                        compute_blended_adaptation
  Program Balance    -> styled 4x8 grid with status color coding
  Summary Matrix     -> grouped bar chart by workout type

MATPLOTLIB APPROACH: Use fig, ax = plt.subplots() (Module 4 OOP API). For color
grids, iterate cells and set background as RGBA tuple: (r, g, b, alpha) where
alpha = blended_pct.
MODULES: 4-5 (pandas, groupby, pivot_table, matplotlib).


=== STAGE 6 — Persistence ===

BUILD: Add serialize() / deserialize() to MtrxDatabase; add save() / load() to
MtrxApp. Use JSON with an explicit schema_version field -- human-readable,
migratable, and free of the class-structure coupling that makes pickle files
break on any __init__ attribute change.

SCHEMA_VERSION = 1   # increment and add a migration function on any structural change

-- MtrxDatabase (serialization logic lives with the state it describes) --

  def serialize(self) -> dict:
      # Returns a plain dict of all five internal structures.
      # datetime.date objects  -> ISO 8601 strings via .isoformat()
      # tuple keys in __matrix_plans -> '|'.join(key)  e.g. 'Sagittal|Push'
      return {
          'schema_version':  SCHEMA_VERSION,
          'user_counter':    self.__user_counter,
          'measure_counter': self.__measure_counter,
          'record_counter':  self.__record_counter,
          'users':           {str(k): {**v, 'join_date': v['join_date'].isoformat()}
                              for k, v in self.__users.items()},
          'measurements':    {str(k): [{**m, 'date': m['date'].isoformat()} for m in lst]
                              for k, lst in self.__measurements.items()},
          'exercises':       dict(self.__exercises),
          'records':         [{**r, 'date': r['date'].isoformat()} for r in self.__records],
          'matrix_plans':    {str(k): {'|'.join(cell): pri for cell, pri in plan.items()}
                              for k, plan in self.__matrix_plans.items()},
      }

  @classmethod
  def deserialize(cls, data: dict) -> 'MtrxDatabase':
      # 1. Verify data['schema_version'] == SCHEMA_VERSION; raise ValueError if not.
      #    If schema migrations are ever needed, add a migration chain here
      #    keyed by version number before this check.
      # 2. Construct a fresh MtrxDatabase instance.
      # 3. Re-hydrate each structure:
      #    - str keys back to int for users/measurements/matrix_plans
      #    - ISO strings back to datetime.date via datetime.date.fromisoformat()
      #    - '|'-joined strings back to tuple keys for matrix_plans
      # 4. Restore __user_counter, __measure_counter, __record_counter from data.
      # 5. Return the reconstructed instance.

-- MtrxApp --

  import json

  def save(self, filepath: str) -> None:
      with open(filepath, 'w') as f:
          json.dump(self.__db.serialize(), f, indent=2)

  def load(self, filepath: str) -> None:
      with open(filepath, 'r') as f:
          self.__db = MtrxDatabase.deserialize(json.load(f))

WHY NOT PICKLE:
pickle couples the save file to the live class structure. Any new attribute
added to __init__ after a file was saved raises AttributeError on load -- with
no migration path and no human-readable audit trail. For a system used over
multiple months with real training data, this is an unacceptable data-loss risk.

WHY serialize() / deserialize() ON MtrxDatabase AND NOT MtrxApp:
Serialization logic belongs next to the state it serializes. MtrxApp.save() and
.load() stay thin -- open a file and delegate. This maintains the Repository
interface contract from Section 2: if the backend later becomes SQLite,
serialize() is replaced with a commit() call and MtrxApp is completely unchanged.

MODULES: Module 12 (file I/O, json stdlib), Module 3 (dict/list comprehensions
for serialize/deserialize hydration logic).
"""

# ── End of Technical Design Specification ─────────────────────────────────────
