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

# ── Segment Templates ─────────────────────────────────────────────────────────

SEGMENT_TEMPLATES = {

    'BLANK': {
        'name': 'Blank (No Weights)',
        'grid': {

            # ── Sagittal Plane ────────────────────────────────────────────────

            ('Sagittal', 'Push'): {
                'categories': [
                    {'name': 'Upward Press',     'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Overhead Press', 'Push Press']},
                    {'name': 'Horizontal Press', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Bench Press', 'Floor Press']},
                    {'name': 'Downward Press',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Dips', 'Decline Press']},
                ],
            },
            ('Sagittal', 'Pull'): {
                'categories': [
                    {'name': 'Upward Pull',     'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Pull-Up', 'Chin-Up']},
                    {'name': 'Downward Pull',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Lat Pulldown', 'Cable Pulldown']},
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
                'categories': [],
            },
            ('Sagittal', 'Accessory/Isolation'): {
                'categories': [
                    {'name': 'Arm Flexion',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Bicep Curl', 'Hammer Curl', 'Preacher Curl']},
                    {'name': 'Arm Extension', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Tricep Extension', 'Skull Crusher', 'Pushdown']},
                    {'name': 'Leg Extension', 'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Leg Extension', 'Sissy Squat']},
                    {'name': 'Leg Flexion',   'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Leg Curl', 'Nordic Curl', 'Hamstring Curl']},
                    {'name': 'Calf / Ankle',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Calf Raise', 'Tibialis Raise']},
                ],
            },

            # ── Frontal Plane ─────────────────────────────────────────────────

            ('Frontal', 'Push'): {
                'categories': [
                    {'name': 'Lateral Raise',  'weight': 0, 'measurement_unit': 'VOLUME',
                     'exercise_examples': ['Dumbbell Lateral Raise', 'Cable Lateral Raise']},
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
                    {'name': 'Suitcase Carry',              'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Single-Arm Suitcase Carry', 'Offset Farmer Walk']},
                    {'name': 'Side Plank / Lateral Brace',  'weight': 0, 'measurement_unit': 'DURATION',
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
                    {'name': 'Offset Carry',       'weight': 0, 'measurement_unit': 'LOAD_DISTANCE',
                     'exercise_examples': ['Asymmetric Load Carry', 'Single-Arm Overhead Carry']},
                    {'name': 'Anti-Rotation Hold', 'weight': 0, 'measurement_unit': 'DURATION',
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

    # Named preset stubs — V2
    'GPP':          {'name': 'General Physical Preparedness', 'grid': {}},
    'STRENGTH':     {'name': 'Strength',                      'grid': {}},
    'HYPERTROPHY':  {'name': 'Hypertrophy',                   'grid': {}},
    'POWERLIFTING': {'name': 'Powerlifting',                  'grid': {}},
    'FUNCTIONAL':   {'name': 'Functional Fitness',            'grid': {}},
}

DEFAULT_PRESET = 'BLANK'

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
