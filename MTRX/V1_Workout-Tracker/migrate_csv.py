"""
migrate_csv.py — One-time import of Workout Records.csv → workout_data.json

Run from the V1_Workout-Tracker directory:
    python3 migrate_csv.py

Output: workout_data.json (ready for WorkoutApp.load())

── What this script does ─────────────────────────────────────────────────────
1. Registers the 5 athletes as users.
2. Seeds the exercise library from EXERCISE_LIBRARY.
3. Maps every CSV exercise name to its canonical library name (see NAME_MAP).
4. Parses and imports all VOLUME-measurable workout records.
5. Skips Cold Plunge / Sauna (EXERCISE_LIBRARY_OTHER — no plane/classification).
6. Saves the fully-populated state to workout_data.json.
"""

import csv
import datetime
import sys

from app import WorkoutApp
from Exercise_Library import EXERCISE_LIBRARY

# ── Config ────────────────────────────────────────────────────────────────────

CSV_PATH    = 'csv-data_unstaged/Workout Records.csv'
OUTPUT_PATH = 'workout_data.json'

# ── User Registry ─────────────────────────────────────────────────────────────
# username → (display_name, email)
ATHLETES = {
    'Kai.Harmer':        ('Kai Harmer',        'kai.harmer@example.com'),
    'Zo.Harmer':         ('Zo Harmer',          'zo.harmer@example.com'),
    'Griffin.Rasmussen': ('Griffin Rasmussen',  'griffin.rasmussen@example.com'),
    'Nate.Carlisle':     ('Nate Carlisle',      'nate.carlisle@example.com'),
    'Rachel.Arnold':     ('Rachel Arnold',      'rachel.arnold@example.com'),
}

# ── Name Map ──────────────────────────────────────────────────────────────────
# CSV dot-name → canonical library name.
# None = skip this exercise (no plane/movement classification).
# Exercises that resolve to just dot→space are not listed here; they fall
# through to the default conversion path at the bottom of resolve_name().

NAME_MAP = {
    # Plural/singular fix
    'Lateral.Raises':           'Lateral Raise',
    # Renamed in library
    'Swimming.50M':             'Swimming',
    'OH.Lunge.KB':              'Overhead Lunge',
    'Cable.Lateral.Raises':     'Cable Lateral Raise',
    'Single.Arm.OHS.OHP':       'Single Arm Overhead Squat',
    'Worlds.Greatest.Stretch':  "World's Greatest Stretch",
    # Consolidated in library (KB variant → single entry)
    'Cossack.Squat.(KB)':       'Cossack Squat',
    'Russian.Twist.Medball':    'Russian Twist',
    # Pallof Press — two CSV spellings, two distinct classifications
    'Pallof.Press':             'Pallof Press (Cable)',   # dynamic rep press
    'Palloff.Press':            'Pallof Press (Band)',    # isometric hold
    # No plane/classification — skip
    'Cold.Plunge':              None,
    'Sauna.10Min':              None,
}

# ── Load Type Normalisation ───────────────────────────────────────────────────

LOAD_TYPE_MAP = {
    'Med-Ball':      'Medicine Ball',
    'Medicine.Ball': 'Medicine Ball',
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def resolve_name(csv_name: str) -> str | None:
    """Return the canonical library name, or None to skip."""
    csv_name = csv_name.strip()
    if csv_name in NAME_MAP:
        return NAME_MAP[csv_name]
    # Default: dots → spaces
    return csv_name.replace('.', ' ')


def parse_date(date_str: str) -> datetime.date:
    """'18-Aug-25' → datetime.date(2025, 8, 18)"""
    return datetime.datetime.strptime(date_str.strip(), '%d-%b-%y').date()


def normalise_load_type(raw: str) -> str:
    raw = raw.strip()
    return LOAD_TYPE_MAP.get(raw, raw)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    workout_app = WorkoutApp()

    # ── 1. Register users ─────────────────────────────────────────────────────
    username_to_id = {}
    for csv_athlete, (display_name, email) in ATHLETES.items():
        username = csv_athlete.replace('.', '.').lower()  # e.g. 'kai.harmer'
        result = workout_app.register_user(
            username=username,
            display_name=display_name,
            email=email,
        )
        username_to_id[csv_athlete] = result['user_id']
        print(f'  Registered user: {display_name} (id={result["user_id"]})')

    # ── 2. Seed exercise library ──────────────────────────────────────────────
    for name, props in EXERCISE_LIBRARY.items():
        workout_app.add_exercise(
            exercise_name=name,
            workout_type=props['workout_type'],
            laterality=props['laterality'],
            default_load_type=props['default_load_type'],
            movement_type=props['movement_type'],
            movement_plane=props['movement_plane'],
            classification=props['classification'],
        )
    print(f'  Seeded {len(EXERCISE_LIBRARY)} exercises.')

    # ── 3. Import records ─────────────────────────────────────────────────────
    imported = 0
    skipped  = 0
    errors   = []

    with open(CSV_PATH, newline='') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # row 1 = header
            exercise_name = resolve_name(row['Exercise'])
            if exercise_name is None:
                skipped += 1
                continue

            try:
                date      = parse_date(row['Date'])
                user_id   = username_to_id[row['Athlete'].strip()]
                sets      = int(row['Sets'])
                reps      = int(row['Reps'])
                bonus     = int(row['Bonus']) if row['Bonus'].strip() else 0
                weight    = float(row['Weight']) if row['Weight'].strip() else None
                rpe_raw   = row['RPE'].strip()
                rpe       = float(rpe_raw) if rpe_raw else None
                load_type = normalise_load_type(row['Load Type'])

                workout_app.log_workout(
                    user_id=user_id,
                    date=date,
                    exercise_name=exercise_name,
                    sets=sets,
                    reps=reps,
                    bonus_reps=bonus if bonus else None,
                    weight=weight,
                    rpe=rpe,
                    load_type=load_type,
                )
                imported += 1

            except Exception as e:
                errors.append(f'  Row {row_num} [{row["Exercise"]}]: {e}')
                skipped += 1

    # ── 4. Save ───────────────────────────────────────────────────────────────
    workout_app.save(OUTPUT_PATH)

    # ── 5. Report ─────────────────────────────────────────────────────────────
    print()
    print(f'Import complete.')
    print(f'  Imported : {imported}')
    print(f'  Skipped  : {skipped}')
    if errors:
        print(f'  Errors ({len(errors)}):')
        for e in errors:
            print(e)
    print(f'  Saved to : {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
