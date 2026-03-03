# Conceptual Overview

## 1. Purpose & Background

This system is a multi-user workout logging, adaptation tracking, and training planning platform. It operates on two interconnected layers:

1. **Logging & Adaptation Layer** — records every completed workout and quantifies how much training volume has been **realized** (the body has fully adapted) versus **unrealized** (still within the adaptation window and actively paying out physiological benefits).
2. **Planning Layer** — built on top of the logging layer, this layer uses the **Matrix** to define weekly movement targets across planes and patterns, guide exercise and stimulus selection, and evaluate weekly training balance.

The model assumes a **straight-line vesting schedule**: immediately after a workout, 100% of the stimulus is unrealized. Over the adaptation window specific to that stimulus type, the unrealized portion decays linearly to 0%. This creates a principled way to visualize training load, recovery status, and cumulative adaptation across time.

---

## 2. Core Concepts

### Stimulus Types
Every exercise set is classified into one of four stimulus types based on **reps per set** (the `Reps` field — not total or actual reps). The classification logic follows a strict ordered IFS:

| Reps per Set | Stimulus | Name |
|---|---|---|
| ≤ 3 | N | Neural |
| 4 – 6 | MT | Mechanical Tension |
| 7 – 15 | MD | Muscle Damage |
| ≥ 16 | MS | Metabolic Stress |

Full reference with adaptation windows, fatigue windows, and visualization colors:

| Stimulus | Name | Rep Range | Adaptation Days | Fatigue Days | Base Color |
|---|---|---|---|---|---|
| N | Neural | 1–3 reps | 21 | 1 | `#00C853` |
| MT | Mechanical Tension | 4–6 reps | 56 | 3 | `#FF6A00` |
| MD | Muscle Damage | 7–15 reps | 42 | 5 | `#FF2D95` |
| MS | Metabolic Stress | 16+ reps | 28 | 2 | `#007BFF` |

### Adaptation Window
The number of days over which a stimulus's benefit is fully absorbed. Drives the **unrealized vesting %** calculation.

### Fatigue Window
A shorter window immediately following a workout during which the athlete is still recovering. Drives the **Fatigue Volume** calculation — a separate straight-line decay independent of the adaptation curve.

### Volume Buckets
Two non-overlapping buckets account for all volume:

- **Unrealized Volume** — the portion of actual volume still within the adaptation window (`Unrealized Vesting % > 0`). Straight-line decay over adaptation days.
- **Realized Volume** — the fully vested portion (`Actual Volume − Unrealized Volume`).

`Unrealized Volume + Realized Volume = Total Actual Volume`

**Fatigue Volume** is a separate metric — not a third accounting bucket. It measures the portion of unrealized volume still within the fatigue window, using its own straight-line decay over fatigue days:

$$\text{Fatigue Volume} = \text{Actual Volume} \times \max\!\left(0,\ 1 - \frac{\text{days elapsed}}{\text{Fatigue Days}}\right)$$

Fatigue Volume is always ≤ Unrealized Volume. It answers: *"of the volume still adapting, how much is also still in the recovery window?"* It is used as a sub-filter within adaptation, not as a standalone accounting category.

### Blended Color Visualization
When a single exercise session contains sets across multiple stimulus types (e.g., a neural warmup + muscle damage working sets), the visualization blends colors and percentages proportionally by volume contribution:

$$w_s = \frac{V_s}{V_{total}}$$

$$\%_{unrealized,blend} = \sum_{s} w_s \times \%_{unrealized,s}$$

$$R_{blend} = \sum_{s} w_s \times R_s \quad \text{(same for G, B)}$$

### Volume vs. Reps Toggle
All visualizations support either **actual volume (lbs)** or **actual reps** as the base metric. A toggle switches between the two modes globally, updating all summary and vesting grid views simultaneously.

### The Matrix
The Matrix is a 4×8 planning grid — the backbone of the weekly programming layer. Rows represent anatomical movement planes; columns represent movement type patterns. Each cell intersection is assigned a **priority rating** that defines a weekly training frequency target.

**Priority → Weekly Frequency Target:**
| Priority | Target Sessions/Week |
|---|---|
| High | 3 |
| Medium | 2 |
| Low | 1 |
| N/A | 0 — not considered necessary for a complete program |

**Default Priority Grid:**

| | Accessory / Isolation | Carry / Bracing | Hinge | Pull | Push | Rotation | Squat | Gait / Locomotion |
|---|---|---|---|---|---|---|---|---|
| **Sagittal** | Low | High | High | High | High | N/A | High | High |
| **Frontal** | Low | Medium | N/A | Low | N/A | N/A | Medium | Medium |
| **Transverse** | Low | Medium | N/A | Medium | Medium | High | N/A | Medium |
| **Neutral** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

**Default weekly touch targets:** 7 High cells × 3 = 21 touches; 7 Medium cells × 2 = 14 touches; Low cells = variable (~4–5/week). Neutral is a catch-all for exercises that don't cleanly fit any of the three named planes.

Priority settings are **user-configurable** — each user maintains their own Matrix plan, enabling cross-user structural comparison and competitive benchmarking.

### Intra-Cell Exercise Variation
Within any Matrix cell, the goal is to rotate through **different exercises** each session. The system tracks which exercises fill each cell within a given week and flags same-exercise repetition.

**Example — Sagittal Push (High, 3x/week):**
| Day 1 | Day 2 | Day 3 |
|---|---|---|
| Strict Press | Bench Press | Tricep Dips |

### Stimulus Interleaving
Each time a specific exercise appears in a session, the system checks the previous session of that same exercise and flags if the same stimulus type is repeated.

**Example:** If Bench Press was last performed at 3×5 (MT), the system flags a repeat if the next Bench Press session also uses MT.

### Canonical Set/Rep Schemes and Reference Weights
Four canonical schemes anchor the weight selection system. Each scheme targets a specific stimulus type and corresponds to a percentage of a user's reference weight for that exercise:

| Scheme | Stimulus | Est. % of Reference Weight | Priority |
|---|---|---|---|
| 3×5 | MT — Mechanical Tension | ~80% | Primary |
| 3×10 | MD — Muscle Damage | ~65% | Primary |
| 3×2 | N — Neural | ~95% | Secondary |
| 3×20 | MS — Metabolic Stress | ~50% | Secondary |

The **DDM** for any exercise is the implied 100% reference ceiling derived from recent session weights. Given the weight used in any scheme, the system back-calculates the implied ceiling and surfaces recommended weights for all other schemes as **editable programming suggestions** — not enforced values. Users can accept or override any suggestion when planning a session.

### Bonus Rep and RPE Standardization
On the **final set** of every session, the athlete performs one additional rep beyond the prescribed count (the **bonus rep**). RPE is evaluated immediately after the bonus rep: "How many more reps could I do right now?"

| Reps in Reserve (after bonus rep) | RPE | Interpretation |
|---|---|---|
| 3+ | ≤ 7 | Weight too light — consider increasing |
| 2–3 | 7–8 | Target zone (correctly calibrated) |
| 1 | 9 | Near limit |
| 0 (barely completed) | 9.5 | At limit |
| Could not complete bonus rep | 10 | Exceeded capacity |

This approach makes RPE **comparable across rep schemes and across sessions** — a 3×5 and a 3×20 are evaluated at the same question, at the same relative moment.

RPE is logged but has **no downstream effect on any calculation**. It is displayed for per-user trend analysis only. Cross-user RPE comparison is excluded.

---

## 3. Data Tables

### `Users`
Core identity table. One row per registered user.

| Field | Description | Type |
|---|---|---|
| User ID | Auto-increment primary key | Integer (PK) |
| Username | Unique login identifier | Text (unique) |
| Display Name | Name shown in the UI and on leaderboards | Text |
| Email | Used for authentication | Text (unique) |
| Join Date | Date the user first registered in the app | Date |

---

### `User.Measurements`
Time-series table for athlete body composition and physical metrics. One row per weigh-in or measurement event. Bodyweight logged here is used to calculate volume for bodyweight exercises.

| Field | Description | Type |
|---|---|---|
| Measurement ID | Auto-increment primary key | Integer (PK) |
| User ID | Foreign key → `Users` | Integer (FK) |
| Date | Date of measurement | Date |
| Bodyweight (lbs) | Athlete's bodyweight — used as `Weight` for bodyweight exercises | Decimal |
| Additional Metrics | Optional fields (e.g., waist, chest, etc.) — flexible schema | Decimal |

---

### `Workout.Records`
The primary log table. One row per exercise per session. Records are automatically associated with the signed-in user — no manual name entry required.

#### System Fields
| Field | Description | Type |
|---|---|---|
| Record ID | Auto-increment primary key — unique per row regardless of athlete, date, or exercise | Integer (PK) |
| User ID | Foreign key → `Users`; set automatically from the active session | Integer (FK) |

#### Manual Input Fields
| Field | Description | Type |
|---|---|---|
| Date | Date of workout | Date |
| Exercise | Exercise performed | Dropdown → `Lookup.Workout` |
| Sets | Number of sets | Integer |
| Reps | Reps per set — drives stimulus classification and is the input to the weight conversion system | Integer |
| Bonus Reps | By convention, always 1 on the final set — the standardized RPE measurement point. Additional bonus reps beyond 1 may be recorded but are exceptional. | Integer |
| Weight (lbs) | Load used; for bodyweight exercises, auto-populated from most recent `User.Measurements.Bodyweight` on or before the workout date | Decimal |
| RPE | Rate of Perceived Exertion (subjective effort, 1–10 scale) | Decimal |
| Load Type | Equipment used; auto-filled from `Lookup.Workout` default, user-editable per record | Dropdown (Band, Barbell, Bodyweight, Cable, Curl Bar, Dumbbell, Kettlebell, Machine, Medicineball, N/A) |
| Notes | Free-text annotations | Text |

#### Calculated Fields
| Field | Logic |
|---|---|
| Day | Day of week derived from Date (Mon, Tue, Wed, etc.) |
| Type | Lookup from `Lookup.Workout` by Exercise |
| Laterality | Lookup from `Lookup.Workout` by Exercise |
| Movement Type | Lookup from `Lookup.Workout` by Exercise |
| Movement Plane | Lookup from `Lookup.Workout` by Exercise |
| Stimulus | Assigned from `Reps` per set: ≤3 → N, 4–6 → MT, 7–15 → MD, ≥16 → MS |
| Actual Reps | `(Sets × Reps) + Bonus Reps` |
| Actual Volume | Bilateral: `Actual Reps × Weight`; Unilateral: `Actual Reps × Weight × 2` |
| Unrealized Vesting % | `max(0, min(1, 1 − (today − date).days / Adaptation Days))` |
| Unrealized Volume | `round(Actual Volume × Unrealized Vesting %)` |
| Realized Volume | `Actual Volume − Unrealized Volume` |
| Fatigue Volume | `round(Actual Volume × max(0, 1 − (today − date).days / Fatigue Days))` |

---

### `Vesting_Lookup`
Reference table defining adaptation and fatigue parameters per stimulus type, including the color gradient used for visualization.

| Stimulus | Stimulus Name | Adaptation Days | Fatigue Days | Reps | Description |
|---|---|---|---|---|---|
| N | Neural | 21 | 1 | 1–3 reps | Nervous system training — faster, harder fiber recruitment and coordination. Drives strength and power without significant hypertrophy. |
| MT | Mechanical Tension | 56 | 3 | 4–6 reps | Primary driver of myofibrillar hypertrophy and strength. Force experienced by fibers recruited near maximal capacity. |
| MD | Muscle Damage | 42 | 5 | 7–15 reps | Structural stress and microtrauma from repeated contractions under stretch or fatigue. Triggers satellite cell activation and fiber remodeling. |
| MS | Metabolic Stress | 28 | 2 | 16+ reps | Accumulation of metabolites (lactate, hydrogen ions, inorganic phosphate) during high-rep contractions. Biochemical trigger for sarcoplasmic hypertrophy. |

**Color per stimulus** (base hex at 100% unrealized):

| Stimulus | Base Color |
|---|---|
| MS | `#007BFF` |
| MD | `#FF2D95` |
| MT | `#FF6A00` |
| N | `#00C853` |

Color intensity is applied as **continuous opacity** proportional to the unrealized vesting %: a workout completed today renders at full opacity (100% unrealized); the same workout fully vested renders with no fill (0% unrealized). The base color values above correspond to the ≥80% band from the original Excel implementation, which is used as the 100% opacity anchor for the continuous scale.

---

### `Lookup.Workout`
Master exercise reference table. Source for all exercise-level attribute lookups in `Workout.Records`. The `Movement` and `Plane` columns are the join key between the exercise library and the Matrix — they determine which Matrix cell a given exercise contributes to.

| Column | Description | Allowed Values |
|---|---|---|
| Exercise | Exercise name (primary key) | Text (e.g., "Back Squat", "Bench Press") — standard readable names used in dropdowns |
| Type | Workout classification | Conditioning, Weightlifting, Mobility, Recovery |
| Laterality | Movement sidedness | Bilateral, Unilateral |
| Load Type | Default equipment for the exercise — auto-fills `Workout.Records.Load Type` but can be overridden per record | Band, Barbell, Bodyweight, Cable, Curl Bar, Dumbbell, Kettlebell, Machine, Medicineball, N/A |
| Movement | Movement pattern — maps to Matrix column | Accessory/Isolation, Carry/Bracing, Gait/Locomotion, Hinge, Pull, Push, Rotation, Squat |
| Plane | Anatomical plane — maps to Matrix row | Sagittal, Frontal, Transverse, Neutral |

> **Matrix eligibility:** Credit toward a Matrix cell is determined solely by the `Movement` + `Plane` combination — not by the `Type` classification. A Back Squat logged as Weightlifting credits the Sagittal × Squat cell the same as any other Sagittal Squat exercise.

---

### `Lookup.Date`
Program calendar table mapping dates to standardized training weeks and blocks. This table serves two purposes: (1) it enables the system to evaluate whether a user met their Matrix cell targets for any given week by grouping workout records into program weeks, and (2) it provides a shared temporal reference for competition, leaderboard, and monthly challenge features — ensuring all users are measured against the same program calendar.

| Column | Description |
|---|---|
| Date | Calendar date (MM/DD/YYYY) |
| Week | Week number within the program |
| Day | Day of the week |
| Name | Training block label (e.g., "Round 1 \| Week 1") |

---

### `Matrix.Plan`
Stores each user's priority setting for every Matrix cell (Plane × Movement intersection). One row per user per cell. This table is the user-configurable layer that drives weekly programming targets and enables cross-user comparative analysis and competitive benchmarking.

| Field | Description | Type |
|---|---|---|
| Plan ID | Auto-increment primary key | Integer (PK) |
| User ID | Foreign key → `Users` | Integer (FK) |
| Plane | Movement plane (Matrix row) | Sagittal, Frontal, Transverse, Neutral |
| Movement | Movement type (Matrix column) | Accessory/Isolation, Carry/Bracing, Gait/Locomotion, Hinge, Pull, Push, Rotation, Squat |
| Priority | User's target for this cell | High, Medium, Low, N/A |

The default priority values are seeded from the system defaults (documented in the Matrix section above) when a user first registers. Users may update individual cells at any time.

---

## 4. Calculated Field Reference

All fields are computed in Python at the data layer. This section is the single authoritative source for all derived fields.

---

### 4.1 `Workout.Records` — Derived Fields

| Field | Python Logic | Notes |
|---|---|---|
| Day | `date.strftime('%a')` | Mon, Tue, Wed, etc. |
| Type | `lookup_workout[exercise]['type']` | From `Lookup.Workout` |
| Laterality | `lookup_workout[exercise]['laterality']` | Bilateral or Unilateral |
| Movement Type | `lookup_workout[exercise]['movement']` | Squat, Hinge, Push, etc. |
| Movement Plane | `lookup_workout[exercise]['plane']` | Sagittal, Frontal, Transverse, Neutral |
| Stimulus | `'N' if reps<=3 else 'MT' if reps<=6 else 'MD' if reps<=15 else 'MS'` | Based on `Reps` per set |
| Actual Reps | `sets * reps + bonus_reps` | |
| Actual Volume | `actual_reps * weight * (1 if bilateral else 2)` | For bodyweight exercises, `weight` is sourced from the most recent `User.Measurements.Bodyweight` on or before the workout date |
| Unrealized Vesting % | `max(0, min(1, 1 - (today - date).days / adaptation_days))` | Straight-line decay; clamped to [0, 1] |
| Unrealized Volume | `round(actual_volume * unrealized_pct)` | |
| Realized Volume | `actual_volume - unrealized_volume` | |
| Fatigue Volume | `round(actual_volume * max(0, 1 - (today - date).days / fatigue_days))` | Straight-line decay over fatigue window; always ≤ Unrealized Volume; fatigue days from `Vesting_Lookup` by Stimulus |

---

### 4.2 Scheme % Reference Table

The four canonical set/rep schemes and their implied percentage of DDM. These percentages assume 3 working sets at RPE 7–8 (2–3 reps in reserve after the bonus rep on the final set).

| Scheme | Stimulus | % of DDM |
|---|---|---|
| 3×2 | N — Neural | 95% |
| 3×5 | MT — Mechanical Tension | 80% |
| 3×10 | MD — Muscle Damage | 65% |
| 3×20 | MS — Metabolic Stress | 50% |

---

### 4.3 DDM (Desirable Difficulty Max)

DDM is the implied weight ceiling for a given exercise and user, derived from recent session data. It is calculated at runtime — not stored — and surfaces as editable suggested weights for each canonical scheme at session planning time. Users can accept or override any suggestion.

**Calculation:**

**Step 1 — Back-calculate implied reference from recent sessions:**

For each recorded session, divide the working weight by its scheme % to back-calculate the implied 100% ceiling:

$$\text{Implied Reference} = \frac{\text{Weight Used}}{\text{Scheme \%}}$$

**Step 2 — DDM = average of implied references from recent exposures:**

$$\text{DDM} = \frac{\sum_{i} \text{Implied Reference}_i}{n}$$

The standard inputs are the user's most recent 3×5 and most recent 3×10 session weights for that exercise (one implied reference each, averaged). For exercises unlikely to be trained at high rep ranges (e.g., Power Cleans), use 3×2 and 3×5 instead.

> **Unilateral exercises:** DDM is always based on the **per-side working weight** as recorded — never the doubled volume weight. The ×2 unilateral multiplier applies to volume calculations only.

**Example — Bench Press:**

| Source | Scheme | Recorded Weight | Implied Reference |
|---|---|---|---|
| Most recent 3×10 | MD (65%) | 205 lbs | 205 / 0.65 ≈ 315 |
| Most recent 3×5 | MT (80%) | 255 lbs | 255 / 0.80 ≈ 319 |
| **DDM** | | | **≈ 317 (average)** |

**Step 3 — Suggested weights per scheme:**

$$\text{Suggested Weight} = \text{DDM} \times \text{Scheme \%}$$

| Scheme | Calculation | Suggested Weight |
|---|---|---|
| 3×20 (MS) | 317 × 0.50 | ~158 lbs |
| 3×10 (MD) | 317 × 0.65 | ~206 lbs |
| 3×5 (MT) | 317 × 0.80 | ~254 lbs |
| 3×2 (N) | 317 × 0.95 | ~301 lbs |
| Absolute ceiling | 317 × 1.00 | 317 lbs |

Suggested weights are surfaced at session planning time and are always user-editable. DDM recalculates automatically as new sessions are logged.

---

## 5. Visualizations

### Summary Matrix (Volume Breakdown)
A cross-tabulation of volume by category and exercise.

- **Rows:** Three top-level volume categories, each with MS / MD / MT / N sub-rows and a category subtotal. Adaptation is further broken into two indented sub-rows:

| Row | Field Summed | Filter |
|---|---|---|
| Realized | `Realized Volume` | `Unrealized Vesting % = 0` |
| Adaptation | `Unrealized Volume` | `Unrealized Vesting % > 0` |
| &nbsp;&nbsp;&nbsp;└ Fatigue | `Fatigue Volume` | Fatigue Volume > 0 (sub-row of Adaptation) |
| &nbsp;&nbsp;&nbsp;└ Non-Fatigue | `Unrealized Volume − Fatigue Volume` | Fatigue Volume = 0 (sub-row of Adaptation) |
| Total | `Actual Volume` | None |

Fatigue and Non-Fatigue sub-rows sum to their parent Adaptation row. Each row and sub-row breaks out by stimulus type (MS / MD / MT / N).

- **Columns:** All → Type totals (Weightlifting, Conditioning, etc.) → individual exercises within each type. Total and Type-total columns contain **raw sums only** — no color formatting is applied at these aggregation levels.
- **Filtered by:** Athlete (from session) + Stimulus (sub-row) + Type + Exercise
- **Metric toggle:** Switchable between Actual Volume (lbs) and Actual Reps

### Vesting Grid (Date × Exercise)
The primary adaptation visualization showing currently "vesting" training load.

- **Rows:** Each calendar date with day name
- **Columns:** Individual exercises only (no All or Type total columns in this view — those columns carry no color meaning at aggregation level)
- **Cell value:** Total actual volume (or reps) for that date/exercise
- **Color logic (blended):**
  1. For each date/exercise cell, calculate each stimulus type's share of total volume: $w_s = V_s / V_{total}$
  2. Blend unrealized %: $\%_{blend} = \sum w_s \times \%_{unrealized,s}$
  3. Blend RGB color: $RGB_{blend} = \sum w_s \times RGB_s$
  4. Apply blended unrealized % as continuous opacity against the blended base color (0% = no fill, 100% = full color)
- **Axis filters:** Both row (date) and column (exercise) axes support the following view filters:
  - **All** — shows every date and exercise with any recorded volume
  - **Adaptation** — shows only dates/exercises where at least one stimulus is still within its adaptation window (unrealized % > 0)
- **Metric toggle:** Switchable between Actual Volume (lbs) and Actual Reps

### Matrix View
A 4×8 grid visualization of training balance and volume distribution across the Plane × Movement cell structure.

- **Rows:** Movement planes (Sagittal, Frontal, Transverse, Neutral)
- **Columns:** Movement types (Accessory/Isolation, Carry/Bracing, Gait/Locomotion, Hinge, Pull, Push, Rotation, Squat)
- **Period selector:** Week / Month / YTD / Custom date range. All cell values and targets reflect the selected period.

**Primary toggle — three views of the same grid:**

**Exposure View** (default)
- Each cell shows: sessions completed vs. target for the period, exercises used (intra-cell repetition flag), stimulus types used (stimulus repetition flag)
- Cell status color: On Track / Behind / Complete / Exceeded / N/A

**Volume View**
- Each cell shows total volume (lbs) contributed to that Plane × Movement cell for the selected period
- Sub-filter (applies to Volume and Reps views):

| Sub-filter | Value Shown |
|---|---|
| Total | `Actual Volume` |
| Realized | `Realized Volume` |
| Adaptation | `Unrealized Volume` |
| Fatigue | `Fatigue Volume` |

**Reps View**
- Same as Volume View but using actual reps in place of lbs. Same sub-filter options apply.

- **Filtered by:** Signed-in user + selected period
