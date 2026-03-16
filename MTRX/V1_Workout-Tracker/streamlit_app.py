"""
Workout Tracker — Streamlit Frontend
Pure consumer of WorkoutApp. Does not modify any core module.
"""

import datetime
import os

import streamlit as st

from app import WorkoutApp
from constants import (
    LOAD_TYPES,
    MOVEMENT_PLANES_ORDERED,
    MOVEMENT_TYPES_ORDERED,
    SEGMENT_TEMPLATES,
    STIMULUS_TABLE,
    WORKOUT_TYPES,
    LATERALITY,
)

# ── Session State ─────────────────────────────────────────────────────────────

SAVE_PATH = os.path.join(os.path.dirname(__file__), 'workout_data.json')

if 'app' not in st.session_state:
    st.session_state.app = WorkoutApp()
    if os.path.exists(SAVE_PATH):
        st.session_state.app.load(SAVE_PATH)

app: WorkoutApp = st.session_state.app


def _get_users() -> dict:
    return app._WorkoutApp__db.get_all_users()


def _get_exercises() -> dict:
    return app._WorkoutApp__db.get_all_exercises()


# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title='Workout Tracker', layout='wide')
st.title('Workout Tracker')

# ── Sidebar: Persistence ─────────────────────────────────────────────────────

with st.sidebar:
    st.header('Data')
    col_s, col_l = st.columns(2)
    with col_s:
        if st.button('Save', use_container_width=True):
            app.save(SAVE_PATH)
            st.success('Saved')
    with col_l:
        if st.button('Load', use_container_width=True):
            if os.path.exists(SAVE_PATH):
                app.load(SAVE_PATH)
                st.success('Loaded')
            else:
                st.warning('No save file found')

    st.divider()
    users = _get_users()
    exercises = _get_exercises()
    st.caption(f'{len(users)} users · {len(exercises)} exercises')

# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs([
    'Users',
    'Exercises',
    'Measurements',
    'Log Workout',
    'Summary Matrix',
    'Vesting Grid',
    'Color Matrix',
    'Weight Guidance',
    'Leaderboard',
])

# ── Tab: Users ────────────────────────────────────────────────────────────────

with tabs[0]:
    st.subheader('Register User')
    with st.form('register_user', clear_on_submit=True):
        r_username = st.text_input('Username')
        r_display = st.text_input('Display Name')
        r_email = st.text_input('Email')
        r_c1, r_c2 = st.columns(2)
        with r_c1:
            r_age = st.number_input('Age', min_value=1, max_value=120, value=25)
        with r_c2:
            r_exp = st.number_input('Training Experience (years)', min_value=0, value=0)
        submitted = st.form_submit_button('Register')
        if submitted:
            if not r_username or not r_display or not r_email:
                st.error('Username, Display Name, and Email are required.')
            else:
                try:
                    result = app.register_user(r_username, r_display, r_email,
                                               age=r_age,
                                               training_experience=r_exp)
                    st.success(f"Registered **{result['display_name']}** (ID: {result['user_id']})")
                except ValueError as e:
                    st.error(str(e))

    st.subheader('Current Users')
    users = _get_users()
    if users:
        for uid, u in users.items():
            st.write(f"**{uid}** — {u['display_name']} ({u['username']}) · {u['email']}")
    else:
        st.info('No users registered yet.')

# ── Tab: Exercises ────────────────────────────────────────────────────────────

with tabs[1]:
    st.subheader('Add Exercise')

    with st.form('add_exercise', clear_on_submit=True):
        e_name = st.text_input('Exercise Name')
        e_c1, e_c2, e_c3 = st.columns(3)
        with e_c1:
            e_workout_type = st.selectbox('Workout Type', sorted(WORKOUT_TYPES))
        with e_c2:
            e_laterality = st.selectbox('Laterality', sorted(LATERALITY))
        with e_c3:
            e_load_type = st.selectbox('Default Load Type', sorted(LOAD_TYPES))

        e_c4, e_c5 = st.columns(2)
        with e_c4:
            e_plane = st.selectbox('Movement Plane', MOVEMENT_PLANES_ORDERED)
        with e_c5:
            e_mtype = st.selectbox('Movement Type', MOVEMENT_TYPES_ORDERED)

        # Build classification options from the BLANK template
        blank_grid = SEGMENT_TEMPLATES['BLANK']['grid']
        cell = blank_grid.get((e_plane, e_mtype), {'categories': []})
        class_options = [c['name'] for c in cell['categories']]
        e_class = st.selectbox('Classification', class_options if class_options else ['(none)'])

        submitted = st.form_submit_button('Add Exercise')
        if submitted:
            if not e_name:
                st.error('Exercise name is required.')
            elif e_class == '(none)':
                st.error('No classifications available for this plane/type combination.')
            else:
                try:
                    result = app.add_exercise(e_name, e_workout_type, e_laterality,
                                              e_load_type, e_mtype, e_plane, e_class)
                    st.success(f"Added **{result['exercise_name']}**")
                except ValueError as e:
                    st.error(str(e))

    st.subheader('Exercise Library')
    exercises = _get_exercises()
    if exercises:
        import pandas as pd
        ex_df = pd.DataFrame(exercises.values())
        st.dataframe(ex_df, use_container_width=True, hide_index=True)
    else:
        st.info('No exercises added yet.')

# ── Tab: Measurements ────────────────────────────────────────────────────────

with tabs[2]:
    st.subheader('Log Bodyweight Measurement')
    users = _get_users()
    if not users:
        st.info('Register a user first.')
    else:
        with st.form('log_measurement', clear_on_submit=True):
            m_uid = st.selectbox('User', list(users.keys()),
                                 format_func=lambda x: f"{x} — {users[x]['display_name']}")
            m_c1, m_c2 = st.columns(2)
            with m_c1:
                m_date = st.date_input('Date', value=datetime.date.today())
            with m_c2:
                m_bw = st.number_input('Bodyweight (lbs)', min_value=0.0, value=0.0,
                                       step=0.1, format='%.1f')
            submitted = st.form_submit_button('Log Measurement')
            if submitted:
                if m_bw <= 0:
                    st.error('Bodyweight must be greater than 0.')
                else:
                    result = app.log_measurement(m_uid, m_date, m_bw)
                    st.success(f"Measurement logged (ID: {result['measurement_id']})")

# ── Tab: Log Workout ─────────────────────────────────────────────────────────

with tabs[3]:
    st.subheader('Log Workout')
    users = _get_users()
    exercises = _get_exercises()
    if not users:
        st.info('Register a user first.')
    elif not exercises:
        st.info('Add an exercise first.')
    else:
        with st.form('log_workout', clear_on_submit=True):
            w_uid = st.selectbox('User', list(users.keys()),
                                 format_func=lambda x: f"{x} — {users[x]['display_name']}",
                                 key='workout_user')
            w_exercise = st.selectbox('Exercise',
                                      [v['exercise_name'] for v in exercises.values()])
            w_date = st.date_input('Date', value=datetime.date.today(), key='workout_date')

            w_c1, w_c2, w_c3 = st.columns(3)
            with w_c1:
                w_sets = st.number_input('Sets', min_value=1, value=3)
            with w_c2:
                w_reps = st.number_input('Reps', min_value=1, value=5)
            with w_c3:
                w_bonus = st.number_input('Bonus Reps', min_value=0, value=0)

            w_c4, w_c5, w_c6 = st.columns(3)
            with w_c4:
                w_weight = st.number_input('Weight', min_value=0.0, value=0.0,
                                           step=2.5, format='%.1f')
            with w_c5:
                w_rpe = st.number_input('RPE', min_value=6.0, max_value=10.0,
                                        value=7.0, step=0.5, format='%.1f')
            with w_c6:
                w_load_type = st.selectbox('Load Type', sorted(LOAD_TYPES), key='w_lt')

            w_notes = st.text_input('Notes', value='')

            submitted = st.form_submit_button('Log Workout')
            if submitted:
                try:
                    result = app.log_workout(
                        user_id=w_uid,
                        date=w_date,
                        exercise_name=w_exercise,
                        sets=w_sets,
                        reps=w_reps,
                        bonus_reps=w_bonus if w_bonus > 0 else None,
                        weight=w_weight if w_weight > 0 else None,
                        rpe=w_rpe,
                        load_type=w_load_type,
                        notes=w_notes,
                    )
                    msg = f"Logged (Record ID: {result['record_id']})"
                    if result['ddm'] is not None:
                        msg += f" · DDM: {result['ddm']}"
                    if result['weight_suggestions'] is not None:
                        msg += f" · Suggestions: {result['weight_suggestions']}"
                    st.success(msg)
                except (ValueError, KeyError) as e:
                    st.error(str(e))

# ── Tab: Summary Matrix ──────────────────────────────────────────────────────

with tabs[4]:
    st.subheader('Summary Matrix')
    users = _get_users()
    if not users:
        st.info('Register a user first.')
    else:
        s_c1, s_c2, s_c3 = st.columns(3)
        with s_c1:
            s_uid = st.selectbox('User', list(users.keys()),
                                 format_func=lambda x: f"{x} — {users[x]['display_name']}",
                                 key='sm_user')
        with s_c2:
            s_start = st.date_input('Period Start', value=None, key='sm_start')
        with s_c3:
            s_end = st.date_input('Period End', value=None, key='sm_end')

        if st.button('Generate Summary', key='sm_btn'):
            df = app.get_summary_matrix(
                user_id=s_uid,
                period_start=s_start if s_start else None,
                period_end=s_end if s_end else None,
            )
            if df.empty:
                st.info('No data for this user/period.')
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

# ── Tab: Vesting Grid ────────────────────────────────────────────────────────

with tabs[5]:
    st.subheader('Vesting Grid')
    users = _get_users()
    if not users:
        st.info('Register a user first.')
    else:
        v_c1, v_c2, v_c3 = st.columns(3)
        with v_c1:
            v_uid = st.selectbox('User', list(users.keys()),
                                 format_func=lambda x: f"{x} — {users[x]['display_name']}",
                                 key='vg_user')
        with v_c2:
            v_axis = st.selectbox('Axis Filter', ['adaptation', 'all'], key='vg_axis')
        with v_c3:
            v_metric = st.selectbox('Metric', ['volume', 'reps'], key='vg_metric')

        if st.button('Generate Vesting Grid', key='vg_btn'):
            df = app.get_vesting_grid(
                user_id=v_uid,
                axis_filter=v_axis,
                metric=v_metric,
            )
            if df.empty:
                st.info('No data for this user.')
            else:
                st.dataframe(df, use_container_width=True)

# ── Tab: Color Matrix ────────────────────────────────────────────────────────

with tabs[6]:
    st.subheader('Color Matrix')
    users = _get_users()
    if not users:
        st.info('Register a user first.')
    else:
        cm_uid = st.selectbox('User', list(users.keys()),
                              format_func=lambda x: f"{x} — {users[x]['display_name']}",
                              key='cm_user')
        if st.button('Generate Color Matrix', key='cm_btn'):
            color_map = app.get_color_matrix(user_id=cm_uid)
            if not color_map:
                st.info('No data for this user.')
            else:
                import pandas as pd
                rows = []
                for (date, exercise), vals in color_map.items():
                    rows.append({
                        'Date': date,
                        'Exercise': exercise,
                        'Blended %': f"{vals['blended_pct']:.2%}",
                        'Color': vals['blended_hex'],
                    })
                cm_df = pd.DataFrame(rows)

                def _color_row(row):
                    return [f'background-color: {row["Color"]}; color: white'] * len(row)

                st.dataframe(
                    cm_df.style.apply(_color_row, axis=1),
                    use_container_width=True,
                    hide_index=True,
                )

# ── Tab: Weight Guidance ──────────────────────────────────────────────────────

with tabs[7]:
    st.subheader('Weight Guidance')
    users = _get_users()
    exercises = _get_exercises()
    if not users or not exercises:
        st.info('Register a user and add exercises first.')
    else:
        wg_c1, wg_c2 = st.columns(2)
        with wg_c1:
            wg_uid = st.selectbox('User', list(users.keys()),
                                  format_func=lambda x: f"{x} — {users[x]['display_name']}",
                                  key='wg_user')
        with wg_c2:
            wg_ex = st.selectbox('Exercise',
                                 [v['exercise_name'] for v in exercises.values()],
                                 key='wg_ex')

        if st.button('Get Guidance', key='wg_btn'):
            result = app.get_weight_guidance(wg_ex, wg_uid)
            if result['ddm'] is None:
                st.warning(result['note'])
            else:
                st.metric('DDM', f"{result['ddm']} lbs")
                st.write('**Suggested Working Weights:**')
                import pandas as pd
                sugg_df = pd.DataFrame([
                    {'Scheme': k, 'Weight': f"{v} lbs"}
                    for k, v in result['suggestions'].items()
                ])
                st.dataframe(sugg_df, use_container_width=True, hide_index=True)
                st.caption(result['note'])

# ── Tab: Leaderboard ─────────────────────────────────────────────────────────

with tabs[8]:
    st.subheader('Leaderboard')
    lb_c1, lb_c2, lb_c3 = st.columns(3)
    with lb_c1:
        lb_metric = st.selectbox('Metric',
                                 ['volume', 'reps', 'max_load', 'session_count', 'exercise_count'],
                                 key='lb_metric')
    with lb_c2:
        lb_start = st.date_input('Period Start', value=None, key='lb_start')
    with lb_c3:
        lb_end = st.date_input('Period End', value=None, key='lb_end')

    exercises = _get_exercises()
    lb_ex = st.selectbox('Filter by Exercise', ['All'] + [v['exercise_name'] for v in exercises.values()],
                         key='lb_ex')

    if st.button('Generate Leaderboard', key='lb_btn'):
        df = app.get_leaderboard(
            metric=lb_metric,
            exercise_name=lb_ex if lb_ex != 'All' else None,
            period_start=lb_start if lb_start else None,
            period_end=lb_end if lb_end else None,
        )
        if df.empty:
            st.info('No data available.')
        else:
            # Map user_ids to display names
            users = _get_users()
            df['user'] = df['user_id'].apply(
                lambda x: users.get(x, {}).get('display_name', f'User {x}')
            )
            st.dataframe(df[['rank', 'user', 'metric_value']],
                         use_container_width=True, hide_index=True)
