"""
Workout Tracker — Database Layer
All data entities live here as private attributes. No external code accesses
them directly — only via public methods. This boundary makes the storage
backend swappable.
"""

import copy
import datetime
import json

from constants import (
    SEGMENT_TEMPLATES,
    DEFAULT_PRESET,
    MEASUREMENT_UNITS,
    MOVEMENT_PLANES,
    MOVEMENT_TYPES,
    WORKOUT_TYPES,
    LATERALITY,
    LOAD_TYPES,
)

SCHEMA_VERSION = 2


class WorkoutDatabase:

    def __init__(self):
        self.__user_counter    = 1
        self.__measure_counter = 1
        self.__record_counter  = 1
        self.__config_counter  = 1
        self.__block_counter   = 1

        self.__users           = {}   # dict[int, dict]
        self.__measurements    = {}   # dict[int, list[dict]]
        self.__exercises       = {}   # dict[str, dict]
        self.__records         = []   # list[dict]
        self.__matrix_plans    = {}   # dict[int, dict[tuple, dict]]
        self.__plan_history    = {}   # dict[int, list[dict]]
        self.__training_blocks = {}   # dict[int, list[dict]]

    def __repr__(self):
        return (f'WorkoutDatabase | Users: {len(self.__users)} | '
                f'Exercises: {len(self.__exercises)} | '
                f'Records: {len(self.__records)}')

    # ── Users ─────────────────────────────────────────────────────────────────

    def add_user(self, username: str, display_name: str, email: str,
                 age: int = None, training_experience: int = None,
                 preset_key: str = None) -> int:
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

        preset = preset_key or DEFAULT_PRESET
        if preset not in SEGMENT_TEMPLATES:
            raise ValueError(f'Unknown preset_key: {preset!r}')
        self.__matrix_plans[user_id] = copy.deepcopy(SEGMENT_TEMPLATES[preset]['grid'])
        self.__measurements[user_id] = []
        self.__plan_history[user_id] = []
        self.__training_blocks[user_id] = []
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

        # Validate classification against BLANK template
        cell = SEGMENT_TEMPLATES['BLANK']['grid'].get((movement_plane, movement_type))
        if cell is None:
            raise ValueError(f'No cell found for ({movement_plane!r}, {movement_type!r})')
        if not any(cat['name'] == classification for cat in cell['categories']):
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

        # Resolve measurement_unit via exercise → classification → category
        classification = exercise['classification']
        cell_key = (exercise['movement_plane'], exercise['movement_type'])
        plan = self.__matrix_plans[user_id]
        cat = next(
            (c for c in plan[cell_key]['categories']
             if c['name'] == classification),
            None
        )
        if cat is None:
            raise ValueError(
                f'Classification {classification!r} not found in user '
                f'{user_id} plan for {cell_key}'
            )
        unit = cat['measurement_unit']
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

        if rpe is not None and not (6.0 <= float(rpe) <= 10.0):
            raise ValueError(f'rpe must be in range [6.0, 10.0], got {rpe}')

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

    # ── Matrix Plans ──────────────────────────────────────────────────────────

    def update_category_plan_cell(self, user_id: int, movement_plane: str,
                                  movement_type: str,
                                  categories: list) -> None:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        if movement_plane not in MOVEMENT_PLANES:
            raise ValueError(f'Invalid movement_plane: {movement_plane!r}')
        if movement_type not in MOVEMENT_TYPES:
            raise ValueError(f'Invalid movement_type: {movement_type!r}')

        required_keys = {'name', 'weight', 'measurement_unit', 'exercise_examples'}
        for cat in categories:
            if not required_keys.issubset(cat.keys()):
                raise ValueError(
                    f'Category missing required keys: {required_keys - cat.keys()}'
                )
            if cat['measurement_unit'] not in MEASUREMENT_UNITS:
                raise ValueError(
                    f"Invalid measurement_unit: {cat['measurement_unit']!r}"
                )

        self.__matrix_plans[user_id][(movement_plane, movement_type)] = {
            'categories': categories
        }
        self.save_config_snapshot(user_id)

    def add_classification(self, user_id: int, movement_plane: str,
                           movement_type: str, name: str, weight: int,
                           measurement_unit: str,
                           exercise_examples: list = None) -> None:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        if movement_plane not in MOVEMENT_PLANES:
            raise ValueError(f'Invalid movement_plane: {movement_plane!r}')
        if movement_type not in MOVEMENT_TYPES:
            raise ValueError(f'Invalid movement_type: {movement_type!r}')
        if measurement_unit not in MEASUREMENT_UNITS:
            raise ValueError(f'Invalid measurement_unit: {measurement_unit!r}')

        self.__matrix_plans[user_id][(movement_plane, movement_type)][
            'categories'
        ].append({
            'name': name,
            'weight': weight,
            'measurement_unit': measurement_unit,
            'exercise_examples': exercise_examples or [],
        })
        self.save_config_snapshot(user_id)

    def get_category_plan(self, user_id: int) -> dict:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        return copy.deepcopy(self.__matrix_plans[user_id])

    def get_parent_weight(self, user_id: int, movement_plane: str,
                          movement_type: str) -> int:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        cell = self.__matrix_plans[user_id][(movement_plane, movement_type)]
        return sum(cat['weight'] for cat in cell['categories'])

    # ── Plan History ──────────────────────────────────────────────────────────

    def save_config_snapshot(self, user_id: int) -> int:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        snapshot_id = self.__config_counter
        snapshot = {
            'snapshot_id': snapshot_id,
            'timestamp': datetime.datetime.now(),
            'matrix_state': copy.deepcopy(self.__matrix_plans[user_id]),
        }
        self.__plan_history[user_id].append(snapshot)
        self.__config_counter += 1
        return snapshot_id

    def get_active_config(self, user_id: int) -> dict:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        if not self.__plan_history[user_id]:
            return copy.deepcopy(self.__matrix_plans[user_id])
        return copy.deepcopy(
            self.__plan_history[user_id][-1]['matrix_state']
        )

    def get_plan_history(self, user_id: int) -> list:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        return [copy.deepcopy(s) for s in self.__plan_history[user_id]]

    # ── Training Blocks ───────────────────────────────────────────────────────

    def add_training_block(self, user_id: int, name: str,
                           start_date: datetime.date,
                           segments: list) -> int:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        if not segments:
            raise ValueError('segments must be a non-empty list')

        required_seg_keys = {'name', 'weeks', 'workouts_per_week',
                             'exercises_per_workout', 'allocation', 'preset_key'}
        user_plan = self.__matrix_plans[user_id]

        for seg in segments:
            missing = required_seg_keys - seg.keys()
            if missing:
                raise ValueError(f'Segment missing keys: {missing}')
            if not seg['weeks'] or not all(
                isinstance(w, int) and w > 0 for w in seg['weeks']
            ):
                raise ValueError('weeks must be a non-empty list of positive integers')
            if not isinstance(seg['workouts_per_week'], int) or seg['workouts_per_week'] <= 0:
                raise ValueError('workouts_per_week must be a positive integer')
            if not isinstance(seg['exercises_per_workout'], int) or seg['exercises_per_workout'] <= 0:
                raise ValueError('exercises_per_workout must be a positive integer')

            for cell_key, class_alloc in seg['allocation'].items():
                plane, mtype = cell_key
                if plane not in MOVEMENT_PLANES:
                    raise ValueError(f'Invalid movement_plane in allocation: {plane!r}')
                if mtype not in MOVEMENT_TYPES:
                    raise ValueError(f'Invalid movement_type in allocation: {mtype!r}')
                cell_cats = user_plan.get(cell_key, {}).get('categories', [])
                cat_names = {c['name'] for c in cell_cats}
                for cls_name in class_alloc:
                    if cls_name not in cat_names:
                        raise ValueError(
                            f'Classification {cls_name!r} not in user plan for {cell_key}'
                        )

            if seg['preset_key'] is not None and seg['preset_key'] not in SEGMENT_TEMPLATES:
                raise ValueError(f"Invalid preset_key: {seg['preset_key']!r}")

        max_week = max(w for seg in segments for w in seg['weeks'])
        end_date = start_date + datetime.timedelta(days=(max_week * 7) - 1)

        block_id = self.__block_counter
        self.__training_blocks[user_id].append({
            'block_id': block_id,
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
            'segments': segments,
        })
        self.__block_counter += 1
        return block_id

    def get_active_block(self, user_id: int,
                         as_of: datetime.date = None) -> dict | None:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        as_of = as_of or datetime.date.today()
        blocks = self.__training_blocks[user_id]
        matching = [b for b in blocks
                    if b['start_date'] <= as_of <= b['end_date']]
        if not matching:
            return None
        return dict(matching[-1])

    def get_active_segment(self, user_id: int, block_id: int,
                           as_of: datetime.date = None) -> dict | None:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        block = None
        for b in self.__training_blocks[user_id]:
            if b['block_id'] == block_id:
                block = b
                break
        if block is None:
            raise KeyError(f'block_id {block_id} not found for user {user_id}')

        as_of = as_of or datetime.date.today()
        days_into_block = (as_of - block['start_date']).days
        if days_into_block < 0:
            return None
        week_in_block = (days_into_block // 7) + 1

        return next(
            (seg for seg in block['segments']
             if week_in_block in seg['weeks']),
            None
        )

    def get_training_block(self, user_id: int, block_id: int) -> dict:
        if user_id not in self.__users:
            raise KeyError(f'user_id {user_id} not found')
        block = None
        for b in self.__training_blocks[user_id]:
            if b['block_id'] == block_id:
                block = b
                break
        if block is None:
            raise KeyError(f'block_id {block_id} not found for user {user_id}')
        return dict(block)

    # ── Serialization ─────────────────────────────────────────────────────────

    def serialize(self) -> dict:
        def _convert_date(obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()
            return obj

        def _serialize_dict(d):
            """Recursively convert dates and tuple keys."""
            if isinstance(d, dict):
                result = {}
                for k, v in d.items():
                    key = '|'.join(k) if isinstance(k, tuple) else k
                    result[key] = _serialize_dict(v)
                return result
            elif isinstance(d, list):
                return [_serialize_dict(item) for item in d]
            else:
                return _convert_date(d)

        # Convert user_id int keys to strings for JSON
        users = {str(k): _serialize_dict(v) for k, v in self.__users.items()}
        measurements = {str(k): _serialize_dict(v)
                        for k, v in self.__measurements.items()}
        exercises = _serialize_dict(self.__exercises)
        records = _serialize_dict(self.__records)
        matrix_plans = {}
        for uid, plan in self.__matrix_plans.items():
            matrix_plans[str(uid)] = _serialize_dict(plan)
        plan_history = {}
        for uid, snapshots in self.__plan_history.items():
            plan_history[str(uid)] = _serialize_dict(snapshots)
        training_blocks = {}
        for uid, blocks in self.__training_blocks.items():
            training_blocks[str(uid)] = _serialize_dict(blocks)

        return {
            'schema_version': SCHEMA_VERSION,
            'user_counter': self.__user_counter,
            'measure_counter': self.__measure_counter,
            'record_counter': self.__record_counter,
            'config_counter': self.__config_counter,
            'block_counter': self.__block_counter,
            'users': users,
            'measurements': measurements,
            'exercises': exercises,
            'records': records,
            'matrix_plans': matrix_plans,
            'plan_history': plan_history,
            'training_blocks': training_blocks,
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
        db.__config_counter = data['config_counter']
        db.__block_counter = data['block_counter']

        # Restore users
        for uid_str, user_data in data['users'].items():
            uid = int(uid_str)
            user_data['join_date'] = datetime.date.fromisoformat(user_data['join_date'])
            db.__users[uid] = user_data

        # Restore measurements
        for uid_str, meas_list in data['measurements'].items():
            uid = int(uid_str)
            for m in meas_list:
                m['date'] = datetime.date.fromisoformat(m['date'])
            db.__measurements[uid] = meas_list

        # Restore exercises
        db.__exercises = data['exercises']

        # Restore records
        for r in data['records']:
            r['date'] = datetime.date.fromisoformat(r['date'])
        db.__records = data['records']

        # Restore matrix plans (convert pipe-separated keys back to tuples)
        def _restore_tuple_keys(plan_dict):
            result = {}
            for key_str, val in plan_dict.items():
                if '|' in key_str:
                    key = tuple(key_str.split('|'))
                else:
                    key = key_str
                result[key] = val
            return result

        for uid_str, plan in data['matrix_plans'].items():
            db.__matrix_plans[int(uid_str)] = _restore_tuple_keys(plan)

        # Restore plan history
        for uid_str, snapshots in data['plan_history'].items():
            uid = int(uid_str)
            for s in snapshots:
                s['timestamp'] = datetime.datetime.fromisoformat(s['timestamp'])
                s['matrix_state'] = _restore_tuple_keys(s['matrix_state'])
            db.__plan_history[uid] = snapshots

        # Restore training blocks
        for uid_str, blocks in data['training_blocks'].items():
            uid = int(uid_str)
            for b in blocks:
                b['start_date'] = datetime.date.fromisoformat(b['start_date'])
                b['end_date'] = datetime.date.fromisoformat(b['end_date'])
                # Restore tuple keys in segment allocations
                for seg in b['segments']:
                    restored_alloc = {}
                    for key_str, val in seg['allocation'].items():
                        if '|' in key_str:
                            restored_alloc[tuple(key_str.split('|'))] = val
                        else:
                            restored_alloc[key_str] = val
                    seg['allocation'] = restored_alloc
            db.__training_blocks[uid] = blocks

        return db
