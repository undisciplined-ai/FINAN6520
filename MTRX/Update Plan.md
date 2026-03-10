# Plan: Draft TDS_MTRX_V1.0.2.py

## TL;DR
V1.0.2 is V1.0.1 with every change from `TDS_MTRX_Updates_v2.md` applied. The file is still a Python TDS spec doc (string constants, inline code comment specs, docstrings). Base = V1.0.1. Apply all 16 numbered changes from the update spec's Change Summary table. The document is written section by section; V1.0.2 is the complete merged output.

---

## Phase 1 — Header + Section 1 (Constants)

1. Update version string in the header to V1.0.2.
2. **Update `PURPOSE` and add `SYSTEM_IDENTITY`**: Replace / augment the existing `PURPOSE` string to reflect the new system identity from the update spec: the system is now a training management system with an adaptive forward-looking prescription engine, a competitive platform layer, and an AI-driven data access layer. Add a `DESIGN_PHILOSOPHY` string capturing the "living target / recalibrate, not penalize" narrative from the update spec's Design Philosophy section.
3. Update `ARCHITECTURE` docstring: "4×8 grid" → "3×8 grid" wherever referenced. Note: "Section 4.8" references (DDM subsection number) are coincidental — leave those untouched.
4. **REMOVE** `PRIORITY_TARGETS` dict (Section 1.3) **and** `PRIORITY_OPTIONS` set (Section 1.5). Add note: both replaced by per-category weights in `PRESET_MATRIX_CONFIGS`. `PRIORITY_OPTIONS` was used only to validate `update_matrix_cell(priority: str)` which no longer accepts a priority string.
5. **REPLACE** `DEFAULT_MATRIX_GRID` (Section 1.4) with:
   - `MEASUREMENT_UNITS` constant (5 units: VOLUME, DURATION, DISTANCE, LOAD_DISTANCE, REPS_ONLY with fields + formula)
   - `PRESET_MATRIX_CONFIGS` dict with GPP preset fully defined for all 24 cells (Sagittal×8, Frontal×8, Transverse×8). Each cell has `'categories'` list with name, weight, measurement_unit, exercise_examples. Stub entries (name + comment "TBD") for STRENGTH, HYPERTROPHY, POWERLIFTING, FUNCTIONAL.
   - `DEFAULT_PRESET = 'GPP'`
   - Include notes explaining: parent weight = derived (never stored), tuple key preserved, same join key as before.
6. Update Section 1.5: Remove 'Neutral' from `MOVEMENT_PLANES` set and `MOVEMENT_PLANES_ORDERED` list. Remove `PRIORITY_OPTIONS` (see step 4). Update comment "building the 4x8 grid" → "building the 3x8 grid".

## Phase 2 — Section 2 (Class Architecture)

7. Update `MtrxDatabase.__init__` to add:
   - `self.__config_counter = 1`
   - `self.__plan_history = {}`
   - `self.__block_counter = 1`
   - `self.__training_blocks = {}`
   - Update `__matrix_plans` type annotation: `dict[int, dict[tuple, dict]]` (was `dict[tuple, str]`)
8. Update MULTI_USER_BOUNDARY_TABLE: matrix_plans row updated to reflect hierarchical structure. Add rows for `Plan History` and `Training Blocks`.

## Phase 3 — Section 3 (Data Layer)

9. **Section 3.1 Users**: Expand `add_user` signature with `age: int = None`, `training_experience: int = None`, `preset_key: str = None`. Update example state to include those fields. Update seeding logic: replace `dict(DEFAULT_MATRIX_GRID)` with `import copy; copy.deepcopy(PRESET_MATRIX_CONFIGS[preset or DEFAULT_PRESET]['grid'])`. Add `self.__plan_history[user_id] = []` and `self.__training_blocks[user_id] = []` to `add_user`.
10. **ADD Section 3.1b Plan History**: New subsection immediately after Users. Include `__plan_history` structure with example state. Three methods: `save_config_snapshot`, `get_active_config`, `get_plan_history`. Notes on deepcopy and auto-trigger.
11. **Section 3.3 Exercises**: In `get_all_exercises` docstring, trim the clause "and flag functions (check_intra_cell_variation)" — keep the view function references ("Required by view functions (build_summary_matrix, build_vesting_grid, build_program_balance)").
12. **Section 3.4 Records**: Expand record schema with `'duration_seconds': None` and `'distance_meters': None` (nullable). Update `add_record` spec with step 3b: "Validate required fields for measurement_unit — look up the exercise's cell via the exercise library, resolve the category's measurement_unit, and verify the record supplies the fields listed in MEASUREMENT_UNITS[unit]['fields']."
13. **Section 3.5 Matrix Plans**: Full rewrite.
    - `__matrix_plans: dict[int, dict[tuple, dict]]`. Update example state to show hierarchical structure.
    - WHY section updated (values are now dicts with categories, not strings — deepcopy required on seeding).
    - SEEDING section updated (deepcopy from preset grid; not shallow copy).
    - Methods: `update_matrix_cell(user_id, movement_plane, movement_type, categories: list)`, `add_category(user_id, movement_plane, movement_type, name, weight, measurement_unit, exercise_examples=None)`, `get_matrix_plan(user_id)`, `get_cell_weight(user_id, movement_plane, movement_type)` (returns `sum(cat['weight'] for cat in cell['categories'])`).
    - Remove `get_cell_priority` (no longer exists).
    - Note that `update_matrix_cell` and `add_category` both call `self.save_config_snapshot(user_id)`.
14. **ADD Section 3.6 Training Blocks**: New subsection. `__training_blocks: dict[int, list[dict]]` structure with example state. Three methods: `add_training_block`, `get_active_block`, `get_block_progress`.

## Phase 4 — Section 4 (Derived Metrics)

15. Sections 4.1–4.10: Carry forward unchanged from V1.0.1.
16. **ADD Section 4.11 Prescription Engine**: `build_session` function with full docstring (inputs, outputs per slot dict, 5-step logic), and `pass` body. Include notes on category-level operation, heterogeneous units, variety/stimulus rotation absorbed from removed Section 5.

## Phase 5 — Section 5 REMOVAL

17. Replace entire Section 5 with a tombstone:
```
###############################################################################
# SECTION 5: REMOVED IN V1.0.2
###############################################################################
# check_intra_cell_variation and check_stimulus_interleaving were removed.
# Their underlying queries — "which exercises used in this cell this week" and
# "what stimulus was last used for this exercise" — are now internal steps
# within build_session (Section 4.11). They are not standalone outputs.
# See TDS_MTRX_Updates_v2.md § REMOVE: Section 5 for rationale.
```

## Phase 6 — Section 6 (Views)

18. **6.1 Summary Matrix**: Carry forward unchanged.
19. **6.2 Vesting Grid**: Carry forward unchanged.
20. **6.3 Program Balance**: Update.
    - Replace "4x8 output grid" comment → "3x8 output grid".
    - Replace `MOVEMENT_PLANES_ORDERED` iteration (now 3 planes, no Neutral).
    - Replace `PRIORITY_TARGETS[priority]` / `weekly_target` logic with category-weight-based logic: `cell_weight = sum(cat['weight'] for cat in matrix_plan.get(cell_key, {}).get('categories', []))`.
    - Remove `'priority'` and `'repeat_flag'` from output row. Keep `'stimuli_used'` (still useful data even without flag functions). Add `'cell_weight'` column.
    - **Add REVIEW_NOTE**: Insert an inline comment/note in the V1.0.2 document flagging that `cell_weight` as `weekly_target` may not be the correct interpretation. The old `PRIORITY_TARGETS` mapped priority labels to session counts (High=3, Medium=2, Low=1). Category weight sums in GPP can be larger (e.g., Sagittal Push = 3+3+1 = 7). If `weekly_target = cell_weight`, that implies 7 sessions/week in one cell — likely not intended. The correct source for session targets may be the training block's `targets` dict (Section 3.6), with `cell_weight` serving as relative prioritization weight only. This discrepancy requires resolution before implementation. Mark as `# TODO: V1.0.2 REVIEW — resolve weekly_target derivation`.
21. **6.4 Weight Guidance**: Carry forward unchanged.

## Phase 7 — Section 7 (Calendar + Training Blocks)

22. Keep `get_program_week_bounds` unchanged.
23. Keep `get_block_label` but annotate it as display-only; blocks are now user-defined structures (Section 3.6), not derived arithmetically from `PROGRAM_START_DATE`.
24. Add Section 7.2 subsection: User-Defined Training Blocks. **Cross-reference Section 3.6** for data structure and method specs (do not duplicate them). Include notes on plan-vs-completed tracking and weekly breakdown logic using `get_block_progress`.

## Phase 8 — Section 8 (Competitive Platform — NEW)

25. Add full intent specification from Updates_v2.md Section 8. Version annotation: "Version 2 — intent only, no implementation spec." Include all sub-sections: Deterministic Scoring, Relative Performance, Handicap System, Peer Group Comparison, Multi-Dimensional Leaderboards, Radar Grid Positioning, Temporal Challenges, Data Model Dependencies.

## Phase 9 — Section 9 (Data Access & Visualization — NEW)

26. Add full intent specification from Updates_v2.md Section 9. Version annotation: "Version 2 — intent only." Include: API Connection Points, AI-Driven Jupyter Notebook Integration, Dynamic Filtering, Agentic Programming Modification.

## Phase 10 — Implementation Roadmap

27. Replace `IMPLEMENTATION_ROADMAP` string content with updated version:
    - **Stage 1** (Constants): Updated test — verify 24 cells in GPP preset, MEASUREMENT_UNITS present, 'Neutral' absent from MOVEMENT_PLANES, PRIORITY_TARGETS and PRIORITY_OPTIONS absent.
    - **Stage 2** (Functions): Remove item 7 (flag functions). Add `build_session` test cases (empty week, partial week, off-plan workout, heterogeneous units, verify slot output schema).
    - **Stage 3** (Database): Item 1 expanded `add_user` (age, training_experience, preset_key). Item 4 record schema expansion (duration_seconds, distance_meters, measurement_unit validation). Item 5 hierarchical matrix (deepcopy seeding, `update_matrix_cell` with categories, `add_category`, `get_cell_weight`). Add item 6 plan_history (snapshot on every matrix mutation, deepcopy isolation). Add item 7 training_blocks (date validation, target-category validation, block progress).
    - **Stage 4** (App Controller): Remove flag function calls and flag keys from `log_workout` return. Updated return value: `{'record_id': int, 'ddm': float|None, 'weight_suggestions': dict|None}`. Add `generate_session`, `add_training_block`, `get_block_progress`, `get_plan_history`. `register_user` passes `preset_key` to `db.add_user`.
    - **Stage 5** (Views): 3×8 Program Balance (category-weight basis), new Block Progress view.
    - **Stage 6** (Persistence): Handle hierarchical `__matrix_plans` (nested dict/list values — json.dump handles natively, deserialize must reconstruct categories list structure). Add plan_history, config_counter, training_blocks, block_counter to serialized state. Record schema includes nullable duration_seconds and distance_meters. SCHEMA_VERSION = 2.
    - **Stage 7** (Competitive Platform): Stubs/intent — implemented when mechanics defined.
    - **Stage 8** (AI Layer): LLM tool manifest, notebook templates, agentic modification.

---

## Relevant Files
- `MTRX/TDS_MTRX_V1.0.1.py` — base document (1376 lines)
- `MTRX/TDS_MTRX_Updates_v2.md` — all 16 changes to apply
- `MTRX/TDS_MTRX_V1.0.2.py` — output (currently blank)

## Decisions
- Section numbering NOT renumbered after removing Section 5 (tombstone used instead).
- STRENGTH/HYPERTROPHY/POWERLIFTING/FUNCTIONAL preset stubs included but not fully defined (marked TBD).
- `PRIORITY_TARGETS` AND `PRIORITY_OPTIONS` both removed (both orphaned by hierarchical categories).
- `get_block_label` retained as display-only utility.
- Section 3.6 added for Training Blocks data spec; Section 7.2 cross-references it (no duplication).
- `'stimuli_used'` kept in Program Balance output (still useful data).
- `'repeat_flag'` removed from Program Balance output (was the V1.0.1 field name at line 1105).
- System Identity and Design Philosophy added to header (Phase 1 step 2).
- `build_program_balance` weekly_target discrepancy flagged inline in V1.0.2 doc as a TODO for later review (not resolved in this version).
