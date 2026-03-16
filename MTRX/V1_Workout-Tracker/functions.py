"""
Workout Tracker — Pure Functions
All functions are pure: no side effects, deterministic, testable in isolation.
Parameter `today` is always explicit — never datetime.date.today() inside.
"""

import datetime
import pandas as pd

from constants import (
    STIMULUS_TABLE,
    CANONICAL_SCHEMES,
    MEASUREMENT_UNITS,
    MOVEMENT_PLANES_ORDERED,
    MOVEMENT_TYPES_ORDERED,
)


# ── Stimulus Classification ───────────────────────────────────────────────────

def classify_stimulus(reps: int) -> str:
    if reps <= 3:
        return 'N'
    elif reps <= 6:
        return 'MT'
    elif reps <= 15:
        return 'MD'
    else:
        return 'MS'


# ── Actual Reps & Volume ──────────────────────────────────────────────────────

def compute_actual_reps(sets: int, reps: int, bonus_reps: int) -> int:
    return (sets * reps) + (bonus_reps or 0)


def compute_actual_volume(actual_reps: int, weight: float, laterality: str) -> float:
    if laterality == 'Unilateral':
        return float(actual_reps * weight * 2)
    return float(actual_reps * weight)


# ── Vesting & Adaptation ──────────────────────────────────────────────────────

def compute_unrealized_vesting_pct(workout_date: datetime.date,
                                   today: datetime.date,
                                   adaptation_days: int) -> float:
    days_elapsed = (today - workout_date).days
    return max(0.0, min(1.0, 1.0 - (days_elapsed / adaptation_days)))


def compute_unrealized_volume(actual_volume: float,
                              unrealized_vesting_pct: float) -> float:
    return round(actual_volume * unrealized_vesting_pct)


def compute_realized_volume(actual_volume: float,
                            unrealized_volume: float) -> float:
    return actual_volume - unrealized_volume


def compute_fatigue_volume(actual_volume: float,
                           workout_date: datetime.date,
                           today: datetime.date,
                           fatigue_days: int) -> float:
    days_elapsed = (today - workout_date).days
    return round(actual_volume * max(0.0, 1.0 - (days_elapsed / fatigue_days)))


# ── DDM ───────────────────────────────────────────────────────────────────────

def compute_ddm(exercise_name: str,
                records: list,
                today: datetime.date,
                lookback_days: int = 90) -> float | None:
    exercise_key = exercise_name.strip().lower()
    cutoff_date = today - datetime.timedelta(days=lookback_days)

    implied_references = []

    for scheme_key, props in CANONICAL_SCHEMES.items():
        req_sets = props['sets']
        req_reps = props['reps']
        scheme_pct = props['pct_of_ddm']

        candidates = [
            r for r in records
            if r['exercise_name'].strip().lower() == exercise_key
            and r['sets'] == req_sets
            and r['reps'] == req_reps
            and r['date'] >= cutoff_date
        ]

        if not candidates:
            continue

        most_recent = sorted(candidates, key=lambda r: r['date'], reverse=True)[0]
        implied_references.append(most_recent['weight'] / scheme_pct)

    if len(implied_references) < 2:
        return None

    return float(round(sum(implied_references) / len(implied_references), 1))


def compute_weight_suggestions(ddm: float) -> dict:
    return {
        scheme: round(ddm * props['pct_of_ddm'], 1)
        for scheme, props in CANONICAL_SCHEMES.items()
    }


# ── Blended Adaptation ───────────────────────────────────────────────────────

def compute_blended_adaptation(contributions: list) -> dict:
    total_volume = sum(c['actual_volume'] for c in contributions)
    if total_volume == 0:
        return {'blended_pct': 0.0, 'blended_hex': '#000000'}

    blended_pct = sum(
        (c['actual_volume'] / total_volume) * c['unrealized_pct']
        for c in contributions
    )

    r_blend, g_blend, b_blend = 0.0, 0.0, 0.0
    for c in contributions:
        w = c['actual_volume'] / total_volume
        hex_color = STIMULUS_TABLE[c['stimulus']]['hex']
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r_blend += w * r
        g_blend += w * g
        b_blend += w * b

    blended_hex = '#{:02X}{:02X}{:02X}'.format(int(r_blend), int(g_blend), int(b_blend))
    return {'blended_pct': round(blended_pct, 4), 'blended_hex': blended_hex}


# ── Weight Guidance View ──────────────────────────────────────────────────────

def build_weight_guidance(exercise_name: str,
                          records: list,
                          today: datetime.date) -> dict:
    ddm = compute_ddm(exercise_name, records, today)

    if ddm is None:
        return {
            'exercise':    exercise_name,
            'ddm':         None,
            'suggestions': None,
            'note':        ('Fewer than 2 canonical schemes have sessions in the '
                           'last 90 days. Log at least one more scheme to '
                           'establish a reliable DDM.'),
        }

    return {
        'exercise':    exercise_name,
        'ddm':         round(ddm, 1),
        'suggestions': compute_weight_suggestions(ddm),
        'note':        'All suggestions are user-overridable.',
    }


# ── Shared Enrichment ──────────────────────────────────────────────────────────

def _enrich_records(df: pd.DataFrame,
                    exercises: dict,
                    today: datetime.date) -> pd.DataFrame:
    df['stimulus'] = df['reps'].apply(lambda r: classify_stimulus(int(r)))
    df['actual_reps'] = df.apply(
        lambda r: compute_actual_reps(int(r['sets']), int(r['reps']),
                                      int(r['bonus_reps']) if r['bonus_reps'] is not None else 0),
        axis=1
    )
    df['laterality'] = df['exercise_name'].apply(
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
    return df


# ── Summary Matrix ────────────────────────────────────────────────────────────

def build_summary_matrix(user_id: int,
                         records: list,
                         exercises: dict,
                         today: datetime.date,
                         metric: str = 'volume',
                         period_start: datetime.date = None,
                         period_end: datetime.date = None) -> pd.DataFrame:
    user_records = [r for r in records if r['user_id'] == user_id]
    if not user_records:
        return pd.DataFrame()

    df = pd.DataFrame(user_records)

    if period_start is not None:
        df = df[df['date'] >= period_start]
    if period_end is not None:
        df = df[df['date'] <= period_end]

    # Filter to VOLUME-measurable records only
    df = df[df['reps'].notna()]
    if df.empty:
        return pd.DataFrame()

    df = _enrich_records(df, exercises, today)
    df['unrealized_volume'] = df.apply(
        lambda r: compute_unrealized_volume(r['actual_volume'], r['unrealized_pct']),
        axis=1
    )
    df['realized_volume'] = df.apply(
        lambda r: compute_realized_volume(r['actual_volume'], r['unrealized_volume']),
        axis=1
    )
    df['fatigue_volume'] = df.apply(
        lambda r: compute_fatigue_volume(
            r['actual_volume'], r['date'], today,
            STIMULUS_TABLE[r['stimulus']]['fatigue_days']
        ),
        axis=1
    )
    df['workout_type'] = df['exercise_name'].apply(
        lambda x: exercises.get(x.strip().lower(), {}).get('workout_type', 'Unknown')
    )
    df['non_fatigue_volume'] = df['unrealized_volume'] - df['fatigue_volume']

    output = df.groupby(['workout_type', 'exercise_name', 'stimulus']).agg(
        actual_volume=('actual_volume', 'sum'),
        actual_reps=('actual_reps', 'sum'),
        unrealized_volume=('unrealized_volume', 'sum'),
        realized_volume=('realized_volume', 'sum'),
        fatigue_volume=('fatigue_volume', 'sum'),
        non_fatigue_volume=('non_fatigue_volume', 'sum'),
    ).reset_index()

    return output


# ── Vesting Grid ──────────────────────────────────────────────────────────────

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
    df = df[df['reps'].notna()]
    if df.empty:
        return pd.DataFrame()

    df = _enrich_records(df, exercises, today)

    if axis_filter == 'adaptation':
        df = df[df['unrealized_pct'] > 0]

    value_col = 'actual_volume' if metric == 'volume' else 'actual_reps'

    grid = df.pivot_table(
        index='date',
        columns='exercise_name',
        values=value_col,
        aggfunc='sum',
        fill_value=0,
    )

    return grid


def build_color_matrix(user_id: int,
                       records: list,
                       exercises: dict,
                       today: datetime.date) -> dict:
    user_records = [r for r in records if r['user_id'] == user_id]
    if not user_records:
        return {}

    df = pd.DataFrame(user_records)
    df = df[df['reps'].notna()]
    if df.empty:
        return {}

    df = _enrich_records(df, exercises, today)

    color_map = {}
    for (date, exercise), group in df.groupby(['date', 'exercise_name']):
        contributions = []
        for stimulus, stim_group in group.groupby('stimulus'):
            contributions.append({
                'stimulus': stimulus,
                'actual_volume': stim_group['actual_volume'].sum(),
                'unrealized_pct': stim_group['unrealized_pct'].mean(),
            })
        color_map[(date, exercise)] = compute_blended_adaptation(contributions)

    return color_map


# ── Leaderboard ───────────────────────────────────────────────────────────────

def build_leaderboard(records: list,
                      exercises: dict,
                      today: datetime.date,
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
    filtered = list(records)

    if user_ids is not None:
        filtered = [r for r in filtered if r['user_id'] in user_ids]
    if exercise_name is not None:
        key = exercise_name.strip().lower()
        filtered = [r for r in filtered if r['exercise_name'].strip().lower() == key]
    if workout_type is not None:
        filtered = [r for r in filtered
                    if exercises.get(r['exercise_name'].strip().lower(), {}).get('workout_type') == workout_type]
    if movement_plane is not None:
        filtered = [r for r in filtered
                    if exercises.get(r['exercise_name'].strip().lower(), {}).get('movement_plane') == movement_plane]
    if movement_type is not None:
        filtered = [r for r in filtered
                    if exercises.get(r['exercise_name'].strip().lower(), {}).get('movement_type') == movement_type]
    if classification is not None:
        filtered = [r for r in filtered
                    if exercises.get(r['exercise_name'].strip().lower(), {}).get('classification') == classification]
    if period_start is not None:
        filtered = [r for r in filtered if r['date'] >= period_start]
    if period_end is not None:
        filtered = [r for r in filtered if r['date'] <= period_end]

    if not filtered:
        return pd.DataFrame(columns=['rank', 'user_id', 'metric_value'])

    df = pd.DataFrame(filtered)

    # session_count and exercise_count use all records; others filter to VOLUME-measurable
    if metric in ('volume', 'reps', 'max_load'):
        df = df[df['reps'].notna()]
        if df.empty:
            return pd.DataFrame(columns=['rank', 'user_id', 'metric_value'])

    if metric in ('volume', 'reps'):
        df['actual_reps'] = df.apply(
            lambda r: compute_actual_reps(int(r['sets']), int(r['reps']),
                                          int(r['bonus_reps']) if r['bonus_reps'] is not None else 0),
            axis=1
        )
    if metric == 'volume':
        df['laterality'] = df['exercise_name'].apply(
            lambda x: exercises.get(x.strip().lower(), {}).get('laterality', 'Bilateral')
        )
        df['actual_volume'] = df.apply(
            lambda r: compute_actual_volume(r['actual_reps'], r['weight'], r['laterality']),
            axis=1
        )

    if metric == 'volume':
        result = df.groupby('user_id')['actual_volume'].sum()
    elif metric == 'reps':
        result = df.groupby('user_id')['actual_reps'].sum()
    elif metric == 'max_load':
        result = df.groupby('user_id')['weight'].max()
    elif metric == 'session_count':
        result = df.groupby('user_id')['date'].nunique()
    elif metric == 'exercise_count':
        result = df.groupby('user_id')['exercise_name'].nunique()
    else:
        raise ValueError(f"Unknown metric: {metric}")

    result = result.sort_values(ascending=False).reset_index()
    result.columns = ['user_id', 'metric_value']
    result['rank'] = range(1, len(result) + 1)
    result = result[['rank', 'user_id', 'metric_value']]

    if top_n is not None:
        result = result.head(top_n)

    return result
