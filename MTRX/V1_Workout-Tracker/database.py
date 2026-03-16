"""
Workout Tracker — Database Layer
All data entities live here as private attributes. No external code accesses
them directly — only via public methods. This boundary makes the storage
backend swappable.
"""

import datetime
import json

from constants import (
    CLASSIFICATION_TABLE,
    MEASUREMENT_UNITS,
    MOVEMENT_PLANES,
    MOVEMENT_TYPES,
    WORKOUT_TYPES,
    LATERALITY,
    LOAD_TYPES,
)

SCHEMA_VERSION = 3


class WorkoutDatabase:

    def __init__(self):
        self.__user_counter    = 1
        self.__measure_counter = 1
        self.__record_counter  = 1

        self.__users           = {}   # dict[int, dict]
        self.__measurements    = {}   # dict[int, list[dict]]
        self.__exercises       = {}   # dict[str, dict]
        self.__records         = []   # list[dict]

    def __repr__(self):
        return (f'WorkoutDatabase | Users: {len(self.__users)} | '
                f'Exercises: {len(self.__exercises)} | '
                f'Records: {len(self.__records)}')

    # ── Users ─────────────────────────────────────────────────────────────────

    def add_user(self, username: str, display_name: str, email: str,
                 age: int = None, training_experience: int = None) -> int:
        if any(u['username'] == username for u in self.__users.values()):
            raise ValueError(f'Username {username!r} already exists')
        if any(u['email'] == email for u in self.__users.values()):
            raise ValueError(f'Email {email!r} already exists')

        user_id = self.__user_counter
        self.__users[user_id] = {
            'username': username,
            'display_name': display_name,
            'email': email,
            'join_date': datetime.date.today(),
            'age': age,
            'training_experience': training_experience,
        }
        self.__measurements[user_id] = []
        self.__user_counter += 1
        return user_id

    def get_user(self, user_id: int) -> dict:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        return dict(self.__users[user_id])

    def get_all_users(self) -> dict:
        return {k: dict(v) for k, v in self.__users.items()}

    # ── Measurements ──────────────────────────────────────────────────────────

    def add_measurement(self, user_id: int, date: datetime.date,
                        bodyweight: float, additional: dict = None) -> int:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')

        measurement_id = self.__measure_counter
        record = {
            'measurement_id': measurement_id,
            'date': date,
            'bodyweight': float(bodyweight),
            'additional': additional or {},
        }
        self.__measurements[user_id].append(record)
        self.__measurements[user_id] = sorted(
            self.__measurements[user_id], key=lambda m: m['date']
        )
        self.__measure_counter += 1
        return measurement_id

    def get_bodyweight_on_date(self, user_id: int,
                               target_date: datetime.date) -> float | None:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        result = None
        for m in self.__measurements[user_id]:
            if m['date'] <= target_date:
                result = m['bodyweight']
        return result

    def delete_measurement(self, user_id: int, measurement_id: int) -> None:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        original_len = len(self.__measurements[user_id])
        self.__measurements[user_id] = [
            m for m in self.__measurements[user_id]
            if m['measurement_id'] != measurement_id
        ]
        if len(self.__measurements[user_id]) == original_len:
            raise KeyError(f'measurement_id {measurement_id} not found for user {user_id}')

    # ── Exercise Library ──────────────────────────────────────────────────────

    def add_exercise(self, exercise_name: str, workout_type: str,
                     laterality: str, default_load_type: str,
                     movement_type: str, movement_plane: str,
                     classification: str) -> str:
        key = exercise_name.strip().lower()
        if key in self.__exercises:
            raise ValueError(f'Duplicate exercise name: {exercise_name!r}')
        if workout_type not in WORKOUT_TYPES:
            raise ValueError(f'Invalid workout_type: {workout_type!r}')
        if laterality not in LATERALITY:
            raise ValueError(f'Invalid laterality: {laterality!r}')
        if default_load_type not in LOAD_TYPES:
            raise ValueError(f'Invalid default_load_type: {default_load_type!r}')
        if movement_type not in MOVEMENT_TYPES:
            raise ValueError(f'Invalid movement_type: {movement_type!r}')
        if movement_plane not in MOVEMENT_PLANES:
            raise ValueError(f'Invalid movement_plane: {movement_plane!r}')

        # Validate classification against CLASSIFICATION_TABLE
        cell = CLASSIFICATION_TABLE.get((movement_plane, movement_type))
        if cell is None:
            raise ValueError(f'No cell found for ({movement_plane!r}, {movement_type!r})')
        match = next((c for c in cell if c['name'] == classification), None)
        if match is None:
            raise ValueError(
                f'classification {classification!r} not found in '
                f'{movement_plane}/{movement_type} sub-categories'
            )

        self.__exercises[key] = {
            'exercise_name': exercise_name,
            'workout_type': workout_type,
            'laterality': laterality,
            'default_load_type': default_load_type,
            'movement_type': movement_type,
            'movement_plane': movement_plane,
            'classification': classification,
            'measurement_unit': match['measurement_unit'],
        }
        return exercise_name

    def update_exercise(self, exercise_name: str, **kwargs) -> None:
        key = exercise_name.strip().lower()
        if key not in self.__exercises:
            raise KeyError(f'Exercise {exercise_name!r} not found')
        if 'exercise_name' in kwargs:
            raise ValueError(
                'exercise_name cannot be changed. Records reference exercises '
                'by name; renaming would orphan historical data.'
            )

        valid_fields = {'workout_type', 'laterality', 'default_load_type',
                        'movement_type', 'movement_plane', 'classification'}
        validators = {
            'workout_type': WORKOUT_TYPES,
            'laterality': LATERALITY,
            'default_load_type': LOAD_TYPES,
            'movement_type': MOVEMENT_TYPES,
            'movement_plane': MOVEMENT_PLANES,
        }

        for field, value in kwargs.items():
            if field not in valid_fields:
                raise ValueError(f'Unknown exercise field: {field!r}')
            if field in validators and value not in validators[field]:
                raise ValueError(f'Invalid {field}: {value!r}')
            self.__exercises[key][field] = value

        # Re-resolve measurement_unit if classification-related fields changed
        if any(f in kwargs for f in ('movement_plane', 'movement_type', 'classification')):
            ex = self.__exercises[key]
            cell = CLASSIFICATION_TABLE.get((ex['movement_plane'], ex['movement_type']))
            match = next((c for c in cell if c['name'] == ex['classification']), None)
            if match is None:
                raise ValueError(
                    f"classification {ex['classification']!r} not found in "
                    f"{ex['movement_plane']}/{ex['movement_type']} sub-categories"
                )
            self.__exercises[key]['measurement_unit'] = match['measurement_unit']

    def get_exercise(self, exercise_name: str) -> dict:
        key = exercise_name.strip().lower()
        if key not in self.__exercises:
            raise KeyError(f'Exercise {exercise_name!r} not found')
        return dict(self.__exercises[key])

    def get_exercises_for_cell(self, movement_plane: str,
                               movement_type: str) -> list:
        return [v['exercise_name'] for v in self.__exercises.values()
                if v['movement_plane'] == movement_plane
                and v['movement_type'] == movement_type]

    def get_all_exercises(self) -> dict:
        return {k: dict(v) for k, v in self.__exercises.items()}

    def delete_exercise(self, exercise_name: str) -> None:
        key = exercise_name.strip().lower()
        if key not in self.__exercises:
            raise KeyError(f'Exercise {exercise_name!r} not found')
        if any(r['exercise_name'].strip().lower() == key for r in self.__records):
            raise ValueError('Cannot delete exercise with existing workout records.')
        del self.__exercises[key]

    # ── Workout Records ───────────────────────────────────────────────────────

    def add_record(self, user_id: int, date: datetime.date,
                   exercise_name: str,
                   sets: int = None, reps: int = None,
                   bonus_reps: int = None, weight: float = None,
                   rpe: float = None, load_type: str = None,
                   notes: str = '',
                   duration_seconds: float = None,
                   distance_meters: float = None) -> int:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')

        exercise = self.get_exercise(exercise_name)

        if load_type is not None and load_type not in LOAD_TYPES:
            raise ValueError(f'Invalid load_type: {load_type!r}')

        # Measurement unit is a fixed property of the exercise
        unit = exercise['measurement_unit']
        required_fields = MEASUREMENT_UNITS[unit]['fields']

        field_values = {
            'sets': sets, 'reps': reps, 'weight': weight,
            'duration_seconds': duration_seconds,
            'distance_meters': distance_meters,
        }
        missing = [f for f in required_fields if field_values.get(f) is None]

        # Bodyweight auto-resolution: if load_type is Bodyweight and weight is
        # required but missing, resolve it before checking missing fields
        if load_type == 'Bodyweight' and 'weight' in missing:
            resolved_weight = self.get_bodyweight_on_date(user_id, date)
            if resolved_weight is None:
                raise ValueError(
                    'No bodyweight measurement found on or before this date'
                )
            weight = resolved_weight
            missing = [f for f in missing if f != 'weight']

        if missing:
            raise ValueError(
                f'Missing required fields for {unit}: {missing}'
            )

        if rpe is not None and not (0.0 <= float(rpe) <= 10.0):
            raise ValueError(f'rpe must be in range [0.0, 10.0], got {rpe}')

        record_id = self.__record_counter
        self.__records.append({
            'record_id': record_id,
            'user_id': user_id,
            'date': date,
            'exercise_name': exercise_name,
            'sets': sets,
            'reps': reps,
            'bonus_reps': bonus_reps,
            'weight': float(weight) if weight is not None else None,
            'rpe': float(rpe) if rpe is not None else None,
            'load_type': load_type,
            'notes': notes,
            'duration_seconds': duration_seconds,
            'distance_meters': distance_meters,
        })
        self.__record_counter += 1
        return record_id

    def get_records(self, user_id: int = None,
                    date_start: datetime.date = None,
                    date_end: datetime.date = None,
                    exercise_name: str = None) -> list:
        result = self.__records
        if user_id is not None:
            result = [r for r in result if r['user_id'] == user_id]
        if date_start is not None:
            result = [r for r in result if r['date'] >= date_start]
        if date_end is not None:
            result = [r for r in result if r['date'] <= date_end]
        if exercise_name is not None:
            key = exercise_name.strip().lower()
            result = [r for r in result
                      if r['exercise_name'].strip().lower() == key]
        return [dict(r) for r in result]

    def delete_record(self, record_id: int) -> None:
        match = [r for r in self.__records if r['record_id'] == record_id]
        if not match:
            raise KeyError(f'record_id {record_id} not found')
        self.__records = [r for r in self.__records
                          if r['record_id'] != record_id]

    # ── Serialization ─────────────────────────────────────────────────────────

    def serialize(self) -> dict:
        def _convert_date(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return obj

        def _serialize_dict(d):
            if isinstance(d, dict):
                return {k: _serialize_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [_serialize_dict(item) for item in d]
            else:
                return _convert_date(d)

        return {
            'schema_version': SCHEMA_VERSION,
            'user_counter': self.__user_counter,
            'measure_counter': self.__measure_counter,
            'record_counter': self.__record_counter,
            'users': {str(k): _serialize_dict(v)
                      for k, v in self.__users.items()},
            'measurements': {str(k): _serialize_dict(v)
                             for k, v in self.__measurements.items()},
            'exercises': _serialize_dict(self.__exercises),
            'records': _serialize_dict(self.__records),
        }

    @classmethod
    def deserialize(cls, data: dict) -> 'WorkoutDatabase':
        if data.get('schema_version') != SCHEMA_VERSION:
            raise ValueError(
                f"Expected schema_version {SCHEMA_VERSION}, "
                f"got {data.get('schema_version')}"
            )

        db = cls()
        db.__user_counter = data['user_counter']
        db.__measure_counter = data['measure_counter']
        db.__record_counter = data['record_counter']

        for uid_str, user_data in data['users'].items():
            uid = int(uid_str)
            user_data['join_date'] = datetime.date.fromisoformat(user_data['join_date'])
            db.__users[uid] = user_data

        for uid_str, meas_list in data['measurements'].items():
            uid = int(uid_str)
            for m in meas_list:
                m['date'] = datetime.date.fromisoformat(m['date'])
            db.__measurements[uid] = meas_list

        db.__exercises = data['exercises']

        for r in data['records']:
            r['date'] = datetime.date.fromisoformat(r['date'])
        db.__records = data['records']

        return db
