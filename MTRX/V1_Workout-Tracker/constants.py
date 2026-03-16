"""
Workout Tracker — System Constants
All values are fixed program-wide, never modified at runtime.
"""

import datetime

# ── Stimulus Table ────────────────────────────────────────────────────────────

STIMULUS_TABLE = {
    'N':  {'name': 'Neural',             'adaptation_days': 21, 'fatigue_days': 1, 'hex': '#00C853'},
    'MT': {'name': 'Mechanical Tension', 'adaptation_days': 56, 'fatigue_days': 3, 'hex': '#FF6A00'},
    'MD': {'name': 'Muscle Damage',      'adaptation_days': 42, 'fatigue_days': 5, 'hex': '#FF2D95'},
    'MS': {'name': 'Metabolic Stress',   'adaptation_days': 28, 'fatigue_days': 2, 'hex': '#007BFF'},
}

# ── Canonical Schemes ─────────────────────────────────────────────────────────

CANONICAL_SCHEMES = {
    '3x5':  {'sets': 3, 'reps': 5,  'stimulus': 'MT', 'pct_of_ddm': 0.80, 'priority': 'Primary'},
    '3x10': {'sets': 3, 'reps': 10, 'stimulus': 'MD', 'pct_of_ddm': 0.65, 'priority': 'Primary'},
    '3x2':  {'sets': 3, 'reps': 2,  'stimulus': 'N',  'pct_of_ddm': 0.95, 'priority': 'Secondary'},
    '3x20': {'sets': 3, 'reps': 20, 'stimulus': 'MS', 'pct_of_ddm': 0.50, 'priority': 'Secondary'},
}

# ── Measurement Units ─────────────────────────────────────────────────────────

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

# ── Classification Lookup Table ────────────────────────────────────────────────
# Maps (plane, movement_type) → list of valid classification names with
# their measurement unit.  This is the single source of truth used by the
# exercise library to resolve which fields a workout record requires.

CLASSIFICATION_TABLE = {

    # ── Sagittal ──────────────────────────────────────────────────────────────

    ('Sagittal', 'Push'): [
        {'name': 'Upward Press',     'measurement_unit': 'VOLUME'},
        {'name': 'Horizontal Press', 'measurement_unit': 'VOLUME'},
        {'name': 'Downward Press',   'measurement_unit': 'VOLUME'},
    ],
    ('Sagittal', 'Pull'): [
        {'name': 'Upward Pull',     'measurement_unit': 'VOLUME'},
        {'name': 'Downward Pull',   'measurement_unit': 'VOLUME'},
        {'name': 'Horizontal Pull', 'measurement_unit': 'VOLUME'},
    ],
    ('Sagittal', 'Squat'): [
        {'name': 'Bilateral Squat',  'measurement_unit': 'VOLUME'},
        {'name': 'Unilateral Squat', 'measurement_unit': 'VOLUME'},
    ],
    ('Sagittal', 'Hinge'): [
        {'name': 'Bilateral Hinge',  'measurement_unit': 'VOLUME'},
        {'name': 'Unilateral Hinge', 'measurement_unit': 'VOLUME'},
    ],
    ('Sagittal', 'Carry/Bracing'): [
        {'name': 'Loaded Carry', 'measurement_unit': 'LOAD_DISTANCE'},
        {'name': 'Static Brace', 'measurement_unit': 'DURATION'},
    ],
    ('Sagittal', 'Gait/Locomotion'): [
        {'name': 'Running / Sprinting', 'measurement_unit': 'DISTANCE'},
        {'name': 'Sled Push / Drag',    'measurement_unit': 'LOAD_DISTANCE'},
        {'name': 'Stair / Incline',     'measurement_unit': 'DISTANCE'},
    ],
    ('Sagittal', 'Rotation'): [],
    ('Sagittal', 'Accessory/Isolation'): [
        {'name': 'Arm Flexion',   'measurement_unit': 'VOLUME'},
        {'name': 'Arm Extension', 'measurement_unit': 'VOLUME'},
        {'name': 'Leg Extension', 'measurement_unit': 'VOLUME'},
        {'name': 'Leg Flexion',   'measurement_unit': 'VOLUME'},
        {'name': 'Calf / Ankle',  'measurement_unit': 'VOLUME'},
    ],

    # ── Frontal ───────────────────────────────────────────────────────────────

    ('Frontal', 'Push'): [
        {'name': 'Lateral Raise', 'measurement_unit': 'VOLUME'},
    ],
    ('Frontal', 'Pull'): [
        {'name': 'Upright Row', 'measurement_unit': 'VOLUME'},
        {'name': 'Face Pull',   'measurement_unit': 'VOLUME'},
    ],
    ('Frontal', 'Squat'): [
        {'name': 'Lateral Squat', 'measurement_unit': 'VOLUME'},
        {'name': 'Curtsy Lunge',  'measurement_unit': 'VOLUME'},
    ],
    ('Frontal', 'Hinge'): [
        {'name': 'Lateral Hinge', 'measurement_unit': 'VOLUME'},
    ],
    ('Frontal', 'Carry/Bracing'): [
        {'name': 'Suitcase Carry',             'measurement_unit': 'LOAD_DISTANCE'},
        {'name': 'Side Plank / Lateral Brace', 'measurement_unit': 'DURATION'},
    ],
    ('Frontal', 'Gait/Locomotion'): [
        {'name': 'Lateral Shuffle / Skater', 'measurement_unit': 'DISTANCE'},
        {'name': 'Lateral Sled Drag',        'measurement_unit': 'LOAD_DISTANCE'},
    ],
    ('Frontal', 'Rotation'): [
        {'name': 'Lateral Flexion', 'measurement_unit': 'VOLUME'},
    ],
    ('Frontal', 'Accessory/Isolation'): [
        {'name': 'Adduction', 'measurement_unit': 'VOLUME'},
        {'name': 'Abduction', 'measurement_unit': 'VOLUME'},
        {'name': 'Rear Delt', 'measurement_unit': 'VOLUME'},
    ],

    # ── Transverse ────────────────────────────────────────────────────────────

    ('Transverse', 'Push'): [
        {'name': 'Rotational Press',        'measurement_unit': 'VOLUME'},
        {'name': 'Landmine Rotation Press', 'measurement_unit': 'VOLUME'},
    ],
    ('Transverse', 'Pull'): [
        {'name': 'Rotational Row', 'measurement_unit': 'VOLUME'},
        {'name': 'Woodchop Pull',  'measurement_unit': 'VOLUME'},
    ],
    ('Transverse', 'Squat'): [
        {'name': 'Rotational Lunge', 'measurement_unit': 'VOLUME'},
        {'name': 'Pivot Squat',      'measurement_unit': 'VOLUME'},
    ],
    ('Transverse', 'Hinge'): [
        {'name': 'Rotational Hinge', 'measurement_unit': 'VOLUME'},
    ],
    ('Transverse', 'Carry/Bracing'): [
        {'name': 'Offset Carry',       'measurement_unit': 'LOAD_DISTANCE'},
        {'name': 'Anti-Rotation Hold', 'measurement_unit': 'DURATION'},
    ],
    ('Transverse', 'Gait/Locomotion'): [
        {'name': 'Agility / Cutting',    'measurement_unit': 'DISTANCE'},
        {'name': 'Rotational Sled Work', 'measurement_unit': 'LOAD_DISTANCE'},
    ],
    ('Transverse', 'Rotation'): [
        {'name': 'Anti-Rotation',     'measurement_unit': 'VOLUME'},
        {'name': 'Rotational Power',  'measurement_unit': 'REPS_ONLY'},
        {'name': 'Thoracic Rotation', 'measurement_unit': 'REPS_ONLY'},
    ],
    ('Transverse', 'Accessory/Isolation'): [
        {'name': 'Oblique Isolation', 'measurement_unit': 'VOLUME'},
        {'name': 'Rotator Cuff',      'measurement_unit': 'VOLUME'},
        {'name': 'Forearm Rotation',  'measurement_unit': 'VOLUME'},
    ],
}

# ── Controlled Vocabulary Sets ────────────────────────────────────────────────

MOVEMENT_PLANES = {'Sagittal', 'Frontal', 'Transverse'}
MOVEMENT_TYPES  = {'Accessory/Isolation', 'Carry/Bracing', 'Gait/Locomotion',
                   'Hinge', 'Pull', 'Push', 'Rotation', 'Squat'}
WORKOUT_TYPES   = {'Conditioning', 'Weightlifting', 'Mobility', 'Recovery'}
LATERALITY      = {'Bilateral', 'Unilateral'}
LOAD_TYPES      = {'Band', 'Barbell', 'Bodyweight', 'Cable', 'Curl Bar',
                   'Dumbbell', 'Kettlebell', 'Machine', 'Medicineball', 'N/A'}

MOVEMENT_PLANES_ORDERED = ['Sagittal', 'Frontal', 'Transverse']
MOVEMENT_TYPES_ORDERED  = ['Accessory/Isolation', 'Carry/Bracing', 'Gait/Locomotion',
                           'Hinge', 'Pull', 'Push', 'Rotation', 'Squat']

# ── Program Calendar Anchor ───────────────────────────────────────────────────

PROGRAM_START_DATE = datetime.date(2026, 1, 5)
