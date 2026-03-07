# MTRX — TDS Update Specification v2

This document specifies all changes to `TDS_MTRX.py` required to bring the
system from its current state (a backward-looking fitness accounting system)
to its desired state (a fitness accounting system with an adaptive
forward-looking prescription engine, a competitive platform layer, and an
AI-driven data access and visualization layer).

The developer reading this should have already read `TDS_MTRX.py` in full.
Every change below references the existing section it modifies, or declares
itself as net-new. Changes are grouped by type: MODIFY, REMOVE, ADD.

---

## System Identity

<!-- Fitness accounting system analogy. Budget vs. actual. Absorb and recalibrate. -->

---

## MODIFY: Section 1.4 — Matrix Structure (Chart of Accounts)

### Remove Neutral Plane

<!-- 4×8 grid (32 cells) → 3×8 grid (24 cells). Neutral was a placeholder.
     Non-compliant exercises get new parent accounts as needed. -->

### Hierarchical Cell Structure

<!-- Flat dict[tuple, str] → hierarchical parent/sub-account model.
     Each cell is a parent account. Sub-accounts carry individual weights.
     Parent weight = sum of children. Resolution increases by adding children. -->

### Measurement Unit Taxonomy

<!-- Sub-accounts declare their own measurement unit.
     Cannot assume sets × reps × weight universally.
     Define canonical measurement types as constants. -->

### V1 Chart of Accounts

The 24-cell matrix with initial sub-accounts per cell. 3 planes × 8
movement types. Each sub-account lists its measurement unit. Parent weight
= sum of child weights. Resolution increases by adding children without
structural change.

Measurement unit key:
- `VOLUME` — sets × reps × weight
- `DURATION` — time under load or effort
- `DISTANCE` — distance covered
- `LOAD_DISTANCE` — weight × distance
- `REPS_ONLY` — bodyweight or unweighted repetitions

---

#### Sagittal Plane

##### Push
- Vertical Press (overhead press, push press) — `VOLUME`
- Horizontal Press (bench press, floor press) — `VOLUME`
- Downward Press (dips, decline press) — `VOLUME`

##### Pull
- Vertical Pull (pull-up, chin-up, lat pulldown) — `VOLUME`
- Horizontal Pull (barbell row, cable row, chest-supported row) — `VOLUME`

##### Squat
- Bilateral Squat (back squat, front squat, goblet squat) — `VOLUME`
- Unilateral Squat (lunge, split squat, step-up) — `VOLUME`

##### Hinge
- Bilateral Hinge (deadlift, RDL, good morning) — `VOLUME`
- Unilateral Hinge (single-leg RDL, single-leg deadlift) — `VOLUME`

##### Carry/Bracing
- Loaded Carry (farmer walk, front rack carry) — `LOAD_DISTANCE`
- Static Brace (plank, dead bug, pallof hold) — `DURATION`

##### Gait/Locomotion
- Running / Sprinting — `DISTANCE`
- Sled Push / Drag — `LOAD_DISTANCE`
- Stair / Incline — `DISTANCE`

##### Rotation
- N/A for sagittal plane (pure sagittal movement has no rotation axis)

##### Accessory/Isolation
- Arm Flexion (bicep curl variations) — `VOLUME`
- Arm Extension (tricep extension variations) — `VOLUME`
- Calf / Ankle (calf raise, tibialis raise) — `VOLUME`

---

#### Frontal Plane

##### Push
- Lateral Raise (dumbbell, cable lateral raise) — `VOLUME`
- Landmine Press (angled lateral press) — `VOLUME`

##### Pull
- Upright Row (barbell, dumbbell, cable) — `VOLUME`
- Face Pull (cable, band) — `VOLUME`

##### Squat
- Lateral Squat (cossack squat, lateral lunge) — `VOLUME`
- Curtsy Lunge — `VOLUME`

##### Hinge
- Lateral Hinge (side-bending deadlift patterns) — `VOLUME`

##### Carry/Bracing
- Suitcase Carry (single-arm loaded carry) — `LOAD_DISTANCE`
- Side Plank / Lateral Brace — `DURATION`

##### Gait/Locomotion
- Lateral Shuffle / Skater — `DISTANCE`
- Lateral Sled Drag — `LOAD_DISTANCE`

##### Rotation
- Lateral Flexion (side bend, windmill) — `VOLUME`

##### Accessory/Isolation
- Adduction (adductor machine, Copenhagen plank) — `VOLUME`
- Abduction (abductor machine, banded walks) — `VOLUME`
- Rear Delt (reverse fly, band pull-apart) — `VOLUME`

---

#### Transverse Plane

##### Push
- Rotational Press (single-arm cable press with rotation) — `VOLUME`
- Landmine Rotation Press — `VOLUME`

##### Pull
- Rotational Row (single-arm cable row with rotation) — `VOLUME`
- Woodchop Pull (high-to-low cable) — `VOLUME`

##### Squat
- Rotational Lunge (lunge with trunk rotation) — `VOLUME`
- Pivot Squat — `VOLUME`

##### Hinge
- Rotational Hinge (single-arm dumbbell snatch, rotational clean) — `VOLUME`

##### Carry/Bracing
- Offset Carry (asymmetric load carry) — `LOAD_DISTANCE`
- Anti-Rotation Hold (pallof press iso, bird dog) — `DURATION`

##### Gait/Locomotion
- Agility / Cutting (cone drills, shuttle runs) — `DISTANCE`
- Rotational Sled Work — `LOAD_DISTANCE`

##### Rotation
- Anti-Rotation (pallof press, cable chop) — `VOLUME`
- Rotational Power (med ball throw, Russian twist) — `REPS_ONLY`
- Thoracic Rotation (open book, seated rotation) — `REPS_ONLY`

##### Accessory/Isolation
- Oblique Isolation (cable twist, woodchop) — `VOLUME`
- Rotator Cuff (internal/external rotation) — `VOLUME`
- Forearm Rotation (pronation/supination) — `VOLUME`

### Preset Configs

<!-- Presets define sub-account weights, not flat priority strings.
     Each preset is a full chart of accounts with weighted sub-accounts. -->

---

## MODIFY: Section 1.5 — Controlled Vocabulary Updates

### Remove Neutral from MOVEMENT_PLANES

<!-- MOVEMENT_PLANES = {'Sagittal', 'Frontal', 'Transverse'}
     MOVEMENT_PLANES_ORDERED = ['Sagittal', 'Frontal', 'Transverse'] -->

---

## MODIFY: Section 3.1 — Users & Configuration Ledger

### Expanded Identity Fields

<!-- Add age and training_experience as data-only fields.
     Not used in any calculation or handicap logic. -->

### Configuration Ledger

### Simplified Definition

<!-- Append-only timestamped snapshots of the full matrix state.
     Triggered on any matrix modification.
     No training parameters (days_per_week, exercises_per_session).
     Budget-side historical data for budget-vs-actual analysis. -->

### Methods

<!-- add_config_snapshot, get_active_config, get_config_ledger -->

---

## MODIFY: Section 3.5 — Matrix Plans (Structural Change)

### Updated Data Model

<!-- __matrix_plans changes from dict[int, dict[tuple, str]]
     to the hierarchical structure matching the chart of accounts. -->

### Seeding from Presets

<!-- Seeding reads from selected preset's hierarchical grid. -->

---

## REMOVE: Section 5 — System Behaviors (Flags)

<!-- Remove check_intra_cell_variation, check_stimulus_interleaving.
     Remove all downstream references. Logic absorbed by prescription engine. -->

---

## ADD: Section 4.11 — Prescription Engine

### Session Generation

<!-- Generates a complete workout session, not a ranked menu.
     Each slot: primary recommendation + dropdown variations
     matching same stimulus/muscle category.
     User modifies in real time before or during session. -->

### Sub-Account Level Operation

<!-- Targets expressed in each sub-account's measurement unit.
     Remaining value calculation handles heterogeneous units.
     Variety and stimulus rotation logic internal to engine. -->

---

## MODIFY: Section 4 — log_workout Return Value

### Remove Flag Keys

<!-- Remove repeat_exercise_flag and repeat_stimulus_flag. -->

---

## MODIFY: Section 7.2 — Training Blocks

### User-Defined Programming Periods

<!-- Remove hardcoded 5-week block logic.
     Blocks are user-defined with goal targets at sub-account level.
     Programming view tracks budget vs. actual across active block.
     Progress tracking analogous to FloQast month-end close view. -->

---

## ADD: Section 8 — Competitive Platform (Intent Specification)

### Deterministic Scoring
### Relative Performance
### Handicap System
### Peer Group Comparison
### Multi-Dimensional Leaderboards
### Radar Grid Positioning
### Temporal Challenges

---

## ADD: Section 9 — Data Access & Visualization Layer

### API Connection Points

<!-- Python layer exposes structured, well-defined API endpoints
     for AI agent consumption. -->

### AI-Driven Jupyter Notebook Integration

<!-- LLM agent navigates the data access layer to generate:
     charts, graphs, gap analysis, natural language recommendations.
     Not feature-per-dataset — a general data access layer. -->

### Dynamic Filtering & Complex Visualizations

<!-- Leaderboards filterable by lift, dimension, peer group.
     Historical data, matrix history, body metrics all feed same engine. -->

### Agentic Programming Modification

<!-- The visualization agent can modify user programming
     based on its analysis. -->

---

## MODIFY: Implementation Roadmap

### Stage 1 — Constants
### Stage 2 — Pure Functions
### Stage 3 — Database
### Stage 4 — App Controller
### Stage 5 — Visualization & Reports
### Stage 6 — Persistence
### Stage 7 — Competitive Platform (Future)
### Stage 8 — AI Visualization Layer (Future)

---

## Change Summary

<!-- Summary table of all changes by number, type, section, description. -->
