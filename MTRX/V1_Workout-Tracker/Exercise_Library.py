"""
Workout Tracker — Exercise Library
Pre-defined exercise catalog conforming to the classification taxonomy in
constants.py.

Keys are canonical exercise names.
Values contain every field required by WorkoutDatabase.add_exercise().

── CSV-to-Constants Mapping Decisions ────────────────────────────────────────

  CSV 'Type' column       → constants.py WORKOUT_TYPES
  ─────────────────────────────────────────────────────
  'Matrix'                → 'Weightlifting'
  'Powerlifting'          → 'Powerlifting'   (unchanged)
  'Conditioning'          → 'Conditioning'   (unchanged)
  'Mobility'              → 'Mobility'        (unchanged)
  'Recovery'              → 'Recovery'        (unchanged)

  CSV 'Plane' column      → constants.py MOVEMENT_PLANES
  ─────────────────────────────────────────────────────
  'Neutral' exercises with a clear structural home in the Sagittal plane are
  mapped to 'Sagittal'. Passive recovery activities (Cold Plunge, Sauna) have
  no valid plane mapping and are held in EXERCISE_LIBRARY_OTHER.

  CSV 'Load Type' corrections
  ─────────────────────────────────────────────────────
  'Medicine.Ball' / 'Med-Ball' → 'Medicine Ball'
  Cable.Lateral.Raises         → load corrected Barbell → 'Cable'

── Deliberate Reclassifications ──────────────────────────────────────────────

  Face Pulls
    CSV: Frontal / Accessory/Isolation
    Library: Frontal / Pull / Face Pull
    (Exact classification name exists in table; Pull is more precise.)

  Lateral Raise / Cable Lateral Raise
    CSV: Frontal / Accessory/Isolation
    Library: Frontal / Push / Lateral Raise
    (Exact classification name exists in table; Push is more precise.)

  Upright Row
    CSV: Sagittal / Pull
    Library: Frontal / Pull / Upright Row
    (Exact classification name exists in CLASSIFICATION_TABLE under
    Frontal/Pull. The frontal plane elbow flare is the defining motion.)

  Seated Row (Machine)
    CSV: Horizontal Pull / Machine
    Library: Sagittal / Pull / Horizontal Pull
    (Renamed to 'Seated Row (Machine)' — qualifier distinguishes the
    machine variant from 'Seated Row' (Cable).)

  Single Arm Overhead Squat
    CSV: Single.Arm.OHS.OHP / Push / Sagittal
    Library: Sagittal / Squat / Unilateral Squat
    (Renamed to reflect the movement; reclassified from Push to Squat.)

  Bosu Weighted Squat Rock
    CSV: Frontal / Carry/Bracing
    Library: Frontal / Squat / Lateral Squat
    (VOLUME tracking needed; Static Brace → DURATION only.)

  Pallof Press — two entries for two distinct uses:
    'Pallof Press (Cable)' : Transverse / Rotation / Anti-Rotation → REPS_ONLY
    'Pallof Press (Band)'  : Transverse / Carry/Bracing / Anti-Rotation Hold → DURATION
    (Qualifier retained — different classification and measurement unit.)

── Name Conventions ──────────────────────────────────────────────────────────
  Space-separated readable names; no dot separators.
  Load-type qualifiers are NOT used in exercise names — load is recorded as a
  separate field. Exception: Pallof Press (Cable/Band) qualifiers are retained
  because the two entries have different classifications and measurement units.
"""

EXERCISE_LIBRARY = {

    # ══════════════════════════════════════════════════════════════════════════
    # SAGITTAL
    # ══════════════════════════════════════════════════════════════════════════

    # ── Sagittal / Push ───────────────────────────────────────────────────────

    'Bench Press': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Horizontal Press',
    },
    'Overhead Press': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Upward Press',
    },
    'Half-Knee OHP': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Upward Press',
    },
    'Single Arm Overhead Press': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Upward Press',
    },
    'Tricep Dips': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Downward Press',
    },

    'Shoulder Press': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Upward Press',
    },
    'Chest Press': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Horizontal Press',
    },
    'Pec Fly': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Push',
        'classification': 'Horizontal Press',
    },

    # ── Sagittal / Pull ───────────────────────────────────────────────────────

    'Pull Ups': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Downward Pull',
    },
    'Lat Pulldown': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Downward Pull',
    },
    'Single Arm Lat Pulldown': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Downward Pull',
    },
    'Seated Row (Machine)': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Horizontal Pull',
    },
    'Inverted Row': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Horizontal Pull',
    },
    'Rows': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Curl Bar',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Horizontal Pull',
    },
    'Seated Row': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Horizontal Pull',
    },
    'Single Arm Rows': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Horizontal Pull',
    },

    'Vertical Traction': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Pull',
        'classification': 'Downward Pull',
    },

    # ── Sagittal / Squat ──────────────────────────────────────────────────────

    'Back Squat': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Bilateral Squat',
    },
    'Front Squat': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Bilateral Squat',
    },
    'Overhead Squat': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Bilateral Squat',
    },
    'Leg Press': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Bilateral Squat',
    },
    'Hurdle to Box Jump': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Bilateral Squat',
    },
    'Seated Hurdle Jump': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Bilateral Squat',
    },
    'Bulgarian Split Squat': {
        'workout_type': 'Powerlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Unilateral Squat',
    },
    'Box Pistol Squat': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Unilateral Squat',
    },
    'Pistol Squat': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Unilateral Squat',
    },
    'Single Arm Overhead Squat': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Unilateral Squat',
    },
    'Overhead Lunge': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Sagittal', 'movement_type': 'Squat',
        'classification': 'Unilateral Squat',
    },

    # ── Sagittal / Hinge ──────────────────────────────────────────────────────

    'Deadlift': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Hinge',
        'classification': 'Bilateral Hinge',
    },
    'Power Clean': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Hinge',
        'classification': 'Bilateral Hinge',
    },
    'Clean Pulls': {
        'workout_type': 'Powerlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Hinge',
        'classification': 'Bilateral Hinge',
    },
    'Jefferson Curl': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Hinge',
        'classification': 'Bilateral Hinge',
    },
    'Single Leg RDL': {
        'workout_type': 'Powerlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Hinge',
        'classification': 'Unilateral Hinge',
    },

    # ── Sagittal / Carry/Bracing ──────────────────────────────────────────────
    # Measurement unit: Loaded Carry → LOAD_DISTANCE (weight × distance_meters)
    #                   Static Brace → DURATION (duration_seconds)

    'Farmers Carry': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Dumbbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Carry/Bracing',
        'classification': 'Loaded Carry',
    },
    'Front Rack Carry': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Sagittal', 'movement_type': 'Carry/Bracing',
        'classification': 'Loaded Carry',
    },
    'Overhead Carry': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Sagittal', 'movement_type': 'Carry/Bracing',
        'classification': 'Loaded Carry',
    },
    'Inchworm': {
        'workout_type': 'Mobility', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Carry/Bracing',
        'classification': 'Static Brace',
    },
    'Dead Bug': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Sagittal', 'movement_type': 'Carry/Bracing',
        'classification': 'Static Brace',
    },

    # ── Sagittal / Gait/Locomotion ────────────────────────────────────────────
    # Measurement unit: DISTANCE_DURATION (distance_meters or duration_seconds)

    'Cardio': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'N/A',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Treadmill': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Swimming': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Jump Rope': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Burpee': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Flat Iron Uphill Run': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Flat Iron Uphill Bear Crawl': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Flat Iron Downhill Bear Crawl': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Single Leg Hops': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Walk Heels': {
        'workout_type': 'Mobility', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Walk Tip-Toe': {
        'workout_type': 'Mobility', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },
    'Warm-up': {
        'workout_type': 'Mobility', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Running / Sprinting',
    },

    # ── Sagittal / Accessory/Isolation ────────────────────────────────────────
    # Note: Trunk/core flexion exercises (Crunches, Cable Crunch, Hanging Leg
    # Raises) have no dedicated core classification in the current taxonomy.
    # 'Leg Flexion' is the closest available classification for hip/trunk
    # flexion-pattern movements.

    'Tricep Extension': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Arm Extension',
    },
    'Leg Extension': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Extension',
    },
    'Bicep Curl': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Curl Bar',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Arm Flexion',
    },
    'Front Raises': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Dumbbell',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Arm Flexion',
    },
    'Skull Crushers': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Curl Bar',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Arm Extension',
    },
    'Hamstring Curl': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Machine',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Flexion',
    },
    'Single Leg Hamstring Curl': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Flexion',
    },
    'Nordic Curls': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Flexion',
    },
    'Hanging Leg Raises': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Flexion',
    },
    'Crunches': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Flexion',
    },
    'Cable Crunch': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Flexion',
    },
    'Walking Quad Stretch': {
        'workout_type': 'Mobility', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Leg Extension',
    },
    'Tibialis Raises': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Calf / Ankle',
    },
    'Calf Raises': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Sagittal', 'movement_type': 'Accessory/Isolation',
        'classification': 'Calf / Ankle',
    },

    # ══════════════════════════════════════════════════════════════════════════
    # FRONTAL
    # ══════════════════════════════════════════════════════════════════════════

    # ── Frontal / Push ────────────────────────────────────────────────────────
    # CSV had all lateral raises under Frontal/Accessory/Isolation.
    # Reclassified to Frontal/Push — 'Lateral Raise' is an exact classification
    # name in CLASSIFICATION_TABLE under this cell.

    'Lateral Raise': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Dumbbell',
        'movement_plane': 'Frontal', 'movement_type': 'Push',
        'classification': 'Lateral Raise',
    },
    'Cable Lateral Raise': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Frontal', 'movement_type': 'Push',
        'classification': 'Lateral Raise',
    },

    # ── Frontal / Pull ────────────────────────────────────────────────────────
    # Face Pulls: reclassified from CSV Frontal/Accessory/Isolation →
    #   Frontal/Pull because 'Face Pull' is an exact name in the table.
    # Upright Row: reclassified from CSV Sagittal/Pull →
    #   Frontal/Pull because 'Upright Row' is an exact name in the table
    #   and the frontal plane elbow flare is the defining motion.

    'Face Pulls': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Frontal', 'movement_type': 'Pull',
        'classification': 'Face Pull',
    },
    'Upright Row': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Frontal', 'movement_type': 'Pull',
        'classification': 'Upright Row',
    },
    'Single-Arm Row': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Frontal', 'movement_type': 'Pull',
        'classification': 'Upright Row',
    },

    # ── Frontal / Squat ───────────────────────────────────────────────────────
    # Bosu Weighted Squat Rock: reclassified from CSV Frontal/Carry/Bracing →
    #   Frontal/Squat so that VOLUME tracking (sets × reps × weight) applies.
    #   Static Brace (DURATION) would make it impossible to track load or reps.

    'Cossack Squat': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Frontal', 'movement_type': 'Squat',
        'classification': 'Lateral Squat',
    },
    'Bosu Weighted Squat Rock': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Medicine Ball',
        'movement_plane': 'Frontal', 'movement_type': 'Squat',
        'classification': 'Lateral Squat',
    },

    # ── Frontal / Carry/Bracing ───────────────────────────────────────────────
    # Measurement unit: Suitcase Carry      → LOAD_DISTANCE (weight × distance)
    #                   Side Plank / Lat.   → DURATION (duration_seconds)

    'Suitcase Carry': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Dumbbell',
        'movement_plane': 'Frontal', 'movement_type': 'Carry/Bracing',
        'classification': 'Suitcase Carry',
    },
    'Offset Front Rack Carry': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Frontal', 'movement_type': 'Carry/Bracing',
        'classification': 'Suitcase Carry',
    },
    'Elevated Side Plank Dip': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Frontal', 'movement_type': 'Carry/Bracing',
        'classification': 'Side Plank / Lateral Brace',
    },

    # ── Frontal / Gait/Locomotion ─────────────────────────────────────────────
    # Measurement unit: DISTANCE_DURATION

    'Lateral Shuffle': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Frontal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Lateral Shuffle / Skater',
    },
    'Lateral Banded Walk': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Band',
        'movement_plane': 'Frontal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Lateral Shuffle / Skater',
    },
    'Skater Jumps': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Frontal', 'movement_type': 'Gait/Locomotion',
        'classification': 'Lateral Shuffle / Skater',
    },

    # ══════════════════════════════════════════════════════════════════════════
    # TRANSVERSE
    # ══════════════════════════════════════════════════════════════════════════

    # ── Transverse / Push ─────────────────────────────────────────────────────

    'Landmine Press': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Transverse', 'movement_type': 'Push',
        'classification': 'Landmine Rotation Press',
    },
    'Cable Rotational Press': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Transverse', 'movement_type': 'Push',
        'classification': 'Rotational Press',
    },

    # ── Transverse / Pull ─────────────────────────────────────────────────────
    # Indoor Climbing: multi-plane pulling effort; Rotational Row is the
    # closest classification for a dynamic transverse pulling pattern.

    'Bird Dog Row': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Dumbbell',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Renegade Row': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Dumbbell',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 10a': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 10b': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 10c': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 10d': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 11a': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 11b': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 11c': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },
    'Indoor Climbing 11d': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Pull',
        'classification': 'Rotational Row',
    },

    # ── Transverse / Carry/Bracing ────────────────────────────────────────────
    # Measurement unit: Offset Carry      → LOAD_DISTANCE (weight × distance)
    #                   Anti-Rotation Hold → DURATION (duration_seconds)
    #
    # Pallof Press (Band): CSV 'Palloff.Press', Carry/Bracing — isometric hold.
    # See also Pallof Press (Cable) under Transverse/Rotation for the
    # dynamic rep-based variant.

    'Anti-Rotation Carry': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Dumbbell',
        'movement_plane': 'Transverse', 'movement_type': 'Carry/Bracing',
        'classification': 'Offset Carry',
    },
    'Single Arm Overhead Carry': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Transverse', 'movement_type': 'Carry/Bracing',
        'classification': 'Offset Carry',
    },
    'Single Arm Plank': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Carry/Bracing',
        'classification': 'Anti-Rotation Hold',
    },
    'Pallof Press (Band)': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Band',
        'movement_plane': 'Transverse', 'movement_type': 'Carry/Bracing',
        'classification': 'Anti-Rotation Hold',
    },

    # ── Transverse / Gait/Locomotion ──────────────────────────────────────────
    # Measurement unit: DISTANCE_DURATION
    # 180 Squat Jumps: CSV lists as Unilateral; corrected to Bilateral —
    # a bilateral jump that rotates 180 degrees.

    'Carioca': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Gait/Locomotion',
        'classification': 'Agility / Cutting',
    },
    '180 Squat Jumps': {
        'workout_type': 'Conditioning', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Gait/Locomotion',
        'classification': 'Agility / Cutting',
    },

    # ── Transverse / Rotation ─────────────────────────────────────────────────
    # Measurement unit: Anti-Rotation   → VOLUME    (sets × reps × weight)
    #                   Rotational Power → REPS_ONLY (sets × reps, no weight)
    #                   Thoracic Rotation→ REPS_ONLY
    #
    # Pallof Press (Cable): dynamic rep-based press — Rotation / Anti-Rotation.
    # Landmine Rotation: load_type corrected N/A → Barbell.

    'Pallof Press (Cable)': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Transverse', 'movement_type': 'Rotation',
        'classification': 'Anti-Rotation',
    },
    'Landmine Rotation': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Barbell',
        'movement_plane': 'Transverse', 'movement_type': 'Rotation',
        'classification': 'Rotational Power',
    },
    'Cable Chop': {
        'workout_type': 'Weightlifting', 'laterality': 'Unilateral',
        'default_load_type': 'Cable',
        'movement_plane': 'Transverse', 'movement_type': 'Rotation',
        'classification': 'Rotational Power',
    },
    "World's Greatest Stretch": {
        'workout_type': 'Mobility', 'laterality': 'Bilateral',
        'default_load_type': 'Bodyweight',
        'movement_plane': 'Transverse', 'movement_type': 'Rotation',
        'classification': 'Thoracic Rotation',
    },

    # ── Transverse / Accessory/Isolation ──────────────────────────────────────

    'Russian Twist': {
        'workout_type': 'Weightlifting', 'laterality': 'Bilateral',
        'default_load_type': 'Kettlebell',
        'movement_plane': 'Transverse', 'movement_type': 'Accessory/Isolation',
        'classification': 'Oblique Isolation',
    },
}


# ── Other ─────────────────────────────────────────────────────────────────────
# Passive recovery activities that do not conform to the plane / movement-type /
# classification taxonomy. These carry a minimal schema and are NOT passed to
# WorkoutDatabase.add_exercise(). Measurement unit is always 'DURATION'.

EXERCISE_LIBRARY_OTHER = {
    'Cold Plunge': {
        'workout_type': 'Recovery',
        'laterality': 'Bilateral',
        'default_load_type': 'N/A',
        'measurement_unit': 'DURATION',
    },
    'Sauna': {
        'workout_type': 'Recovery',
        'laterality': 'Bilateral',
        'default_load_type': 'N/A',
        'measurement_unit': 'DURATION',
    },
}
