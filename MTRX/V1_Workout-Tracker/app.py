"""
Workout Tracker — App Controller
Thin orchestration layer. All business logic is delegated to functions.py;
all state management is delegated to database.py. This class never
reimplements logic inline.
"""

import datetime
import json

import pandas as pd

from database import WorkoutDatabase
from functions import (
    build_color_matrix,
    build_leaderboard,
    build_summary_matrix,
    build_vesting_grid,
    build_weight_guidance,
    compute_ddm,
    compute_weight_suggestions,
    get_program_week_bounds,
)


class WorkoutApp:

    def __init__(self):
        self.__db = WorkoutDatabase()

    def __repr__(self):
        return f'WorkoutApp | {self.__db}'

    # ── Users ─────────────────────────────────────────────────────────────────

    def register_user(self, username: str, display_name: str, email: str,
                      age: int = None, training_experience: int = None,
                      preset_key: str = None) -> dict:
        user_id = self.__db.add_user(
            username=username,
            display_name=display_name,
            email=email,
            age=age,
            training_experience=training_experience,
            preset_key=preset_key,
        )
        return {'user_id': user_id, **self.__db.get_user(user_id)}

    # ── Measurements ──────────────────────────────────────────────────────────

    def log_measurement(self, user_id: int, date: datetime.date,
                        bodyweight: float, additional: dict = None) -> dict:
        measurement_id = self.__db.add_measurement(
            user_id=user_id,
            date=date,
            bodyweight=bodyweight,
            additional=additional,
        )
        return {'measurement_id': measurement_id}

    # ── Exercise Library ──────────────────────────────────────────────────────

    def add_exercise(self, exercise_name: str, workout_type: str,
                     laterality: str, default_load_type: str,
                     movement_type: str, movement_plane: str,
                     classification: str) -> dict:
        name = self.__db.add_exercise(
            exercise_name=exercise_name,
            workout_type=workout_type,
            laterality=laterality,
            default_load_type=default_load_type,
            movement_type=movement_type,
            movement_plane=movement_plane,
            classification=classification,
        )
        return self.__db.get_exercise(name)

    # ── Workout Logging ───────────────────────────────────────────────────────

    def log_workout(self, user_id: int, date: datetime.date,
                    exercise_name: str,
                    sets: int = None, reps: int = None,
                    bonus_reps: int = None, weight: float = None,
                    rpe: float = None, load_type: str = None,
                    notes: str = '',
                    duration_seconds: float = None,
                    distance_meters: float = None) -> dict:
        record_id = self.__db.add_record(
            user_id=user_id,
            date=date,
            exercise_name=exercise_name,
            sets=sets,
            reps=reps,
            bonus_reps=bonus_reps,
            weight=weight,
            rpe=rpe,
            load_type=load_type,
            notes=notes,
            duration_seconds=duration_seconds,
            distance_meters=distance_meters,
        )

        records = self.__db.get_records(user_id=user_id)
        ddm = compute_ddm(exercise_name, records, date)
        suggestions = compute_weight_suggestions(ddm) if ddm is not None else None

        return {
            'record_id': record_id,
            'ddm': round(ddm, 1) if ddm is not None else None,
            'weight_suggestions': suggestions,
        }

    # ── Weight Guidance ───────────────────────────────────────────────────────

    def get_weight_guidance(self, exercise_name: str,
                            user_id: int,
                            today: datetime.date = None) -> dict:
        today = today or datetime.date.today()
        records = self.__db.get_records(user_id=user_id)
        return build_weight_guidance(exercise_name, records, today)

    # ── Views ─────────────────────────────────────────────────────────────────

    def get_summary_matrix(self, user_id: int,
                           today: datetime.date = None,
                           metric: str = 'volume',
                           period_start: datetime.date = None,
                           period_end: datetime.date = None) -> pd.DataFrame:
        today = today or datetime.date.today()
        records = self.__db.get_records()
        exercises = self.__db.get_all_exercises()
        return build_summary_matrix(
            user_id=user_id,
            records=records,
            exercises=exercises,
            today=today,
            metric=metric,
            period_start=period_start,
            period_end=period_end,
        )

    def get_vesting_grid(self, user_id: int,
                         today: datetime.date = None,
                         axis_filter: str = 'adaptation',
                         metric: str = 'volume') -> pd.DataFrame:
        today = today or datetime.date.today()
        records = self.__db.get_records()
        exercises = self.__db.get_all_exercises()
        return build_vesting_grid(
            user_id=user_id,
            records=records,
            exercises=exercises,
            today=today,
            axis_filter=axis_filter,
            metric=metric,
        )

    def get_color_matrix(self, user_id: int,
                         today: datetime.date = None) -> dict:
        today = today or datetime.date.today()
        records = self.__db.get_records()
        exercises = self.__db.get_all_exercises()
        return build_color_matrix(
            user_id=user_id,
            records=records,
            exercises=exercises,
            today=today,
        )

    # ── Training Blocks ───────────────────────────────────────────────────────

    def add_training_block(self, user_id: int, name: str,
                           start_date: datetime.date,
                           segments: list) -> dict:
        block_id = self.__db.add_training_block(
            user_id=user_id,
            name=name,
            start_date=start_date,
            segments=segments,
        )
        return self.__db.get_active_block(user_id, as_of=start_date)

    def get_active_block(self, user_id: int,
                         as_of: datetime.date = None) -> dict | None:
        return self.__db.get_active_block(user_id, as_of=as_of)

    def get_active_segment(self, user_id: int, block_id: int,
                           as_of: datetime.date = None) -> dict | None:
        return self.__db.get_active_segment(user_id, block_id, as_of=as_of)

    def get_block_progress(self, user_id: int, block_id: int) -> dict:
        return self.__db.get_block_progress(user_id, block_id)

    # ── Leaderboard ───────────────────────────────────────────────────────────

    def get_leaderboard(self, today: datetime.date = None,
                        user_ids: list = None,
                        exercise_name: str = None,
                        workout_type: str = None,
                        movement_plane: str = None,
                        movement_type: str = None,
                        classification: str = None,
                        period_start: datetime.date = None,
                        period_end: datetime.date = None,
                        metric: str = 'volume',
                        top_n: int = None) -> pd.DataFrame:
        today = today or datetime.date.today()
        records = self.__db.get_records()
        exercises = self.__db.get_all_exercises()
        return build_leaderboard(
            records=records,
            exercises=exercises,
            today=today,
            user_ids=user_ids,
            exercise_name=exercise_name,
            workout_type=workout_type,
            movement_plane=movement_plane,
            movement_type=movement_type,
            classification=classification,
            period_start=period_start,
            period_end=period_end,
            metric=metric,
            top_n=top_n,
        )

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, filepath: str) -> None:
        data = self.__db.serialize()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str) -> None:
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.__db = WorkoutDatabase.deserialize(data)
