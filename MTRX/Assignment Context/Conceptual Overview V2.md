# Conceptual Overview

## 1. Purpose

This system is a multi-user workout logging, adaptation tracking, and training planning platform. It serves athletes who want to train consistently, recover intelligently, and maintain structural balance across movement patterns. It supports three decisions: understanding what training load is still paying out versus fully absorbed, evaluating whether training is meeting programmed coverage targets, and selecting appropriate loads for each session.

---

## 2. System Parameters

The following values are fixed system-wide constants. They are not user-configurable.

### Stimulus Types

Every exercise set produces one of four stimulus types, determined solely by the number of reps per set.

| Stimulus | Name | Rep Range | Adaptation Window | Fatigue Window | Display Color | Description |
|---|---|---|---|---|---|---|
| N | Neural | 1–3 reps | 21 days | 1 day | `#00C853` | Nervous system training — faster, harder fiber recruitment and coordination. Drives strength and power without significant hypertrophy. |
| MT | Mechanical Tension | 4–6 reps | 56 days | 3 days | `#FF6A00` | Primary driver of myofibrillar hypertrophy and strength. Force experienced by fibers recruited near maximal capacity. |
| MD | Muscle Damage | 7–15 reps | 42 days | 5 days | `#FF2D95` | Structural stress and microtrauma from repeated contractions under stretch or fatigue. Triggers satellite cell activation and fiber remodeling. |
| MS | Metabolic Stress | 16+ reps | 28 days | 2 days | `#007BFF` | Accumulation of metabolites (lactate, hydrogen ions, inorganic phosphate) during high-rep contractions. Biochemical trigger for sarcoplasmic hypertrophy. |

The **Adaptation Window** is the number of days over which a stimulus's benefit is fully absorbed. The **Fatigue Window** is the shorter recovery period immediately following a session.

**Color rendering:** Display color is applied as continuous opacity proportional to the unrealized vesting percentage. A session logged today renders at full opacity (100% unrealized); the same session at full adaptation renders with no fill (0% unrealized). The hex values above are the full-opacity anchors.

### Canonical Schemes

Four set/rep schemes serve as reference points for load selection and DDM derivation.

| Scheme | Stimulus | % of DDM | Priority |
|---|---|---|---|
| 3×5 | Mechanical Tension | 80% | Primary |
| 3×10 | Muscle Damage | 65% | Primary |
| 3×2 | Neural | 95% | Secondary |
| 3×20 | Metabolic Stress | 50% | Secondary |

Primary schemes (3×5 and 3×10) are the standard DDM inputs for most exercises. Secondary schemes are used for power-dominant exercises or supplementary load checks.

These percentages represent the appropriate load for 3 working sets at RPE 7–8 (2–3 reps in reserve after the bonus rep on the final set). They are not derived from a 1-rep max formula and should not be interpreted as such.

---

## 3. Stored Data

### Users

Represents a registered athlete. One record per user.

| Attribute | Description |
|---|---|
| User ID | Unique identifier |
| Username | Unique login name |
| Display Name | Name shown in the interface and on leaderboards |
| Email | Used for authentication; unique |
| Join Date | Date of first registration |

---

### User Measurements

A time-series record of an athlete's body composition. One record per measurement event.

| Attribute | Description |
|---|---|
| Measurement ID | Unique identifier |
| User ID | The user this measurement belongs to |
| Date | Date of measurement |
| Bodyweight (lbs) | Used as the working weight for bodyweight exercises |
| Additional Metrics | Optional fields (e.g., waist, chest) |

The most recent bodyweight recorded on or before a workout date is used as the load for any bodyweight exercise logged on that date.

---

### Exercise Library

A shared, public reference of exercises. Any authenticated user may add an exercise. All attributes are required on creation. Duplicate exercise names are rejected. Existing entries may be edited by any authenticated user.

| Attribute | Description | Allowed Values |
|---|---|---|
| Exercise Name | Unique name for the exercise | Text |
| Workout Type | Classification of the activity | Conditioning, Weightlifting, Mobility, Recovery |
| Laterality | Whether the movement is performed on one side or both | Bilateral, Unilateral |
| Default Load Type | The equipment typically used; auto-fills the load type on new workout records, overridable per record | Band, Barbell, Bodyweight, Cable, Curl Bar, Dumbbell, Kettlebell, Machine, Medicineball, N/A |
| Movement Type | The movement pattern; maps to a Matrix column | Accessory/Isolation, Carry/Bracing, Gait/Locomotion, Hinge, Pull, Push, Rotation, Squat |
| Movement Plane | The anatomical plane; maps to a Matrix row | Sagittal, Frontal, Transverse, Neutral |

The `Movement Type` and `Movement Plane` combination is the sole join key between the Exercise Library and the Matrix. An exercise's contribution to a Matrix cell is determined by these two attributes only — not by its Workout Type classification.

---

### Workout Records

The primary log. One record per exercise per session. Records are automatically associated with the signed-in user.

**System-assigned fields:**

| Attribute | Description |
|---|---|
| Record ID | Unique identifier; auto-assigned; unique per row regardless of user, date, or exercise |
| User ID | The user who logged the record; set automatically from the active session |

**Recorded fields:**

| Attribute | Description |
|---|---|
| Date | Date of the session |
| Exercise | The exercise performed; selected from the Exercise Library |
| Sets | Number of sets performed |
| Reps | Reps prescribed per set; drives stimulus classification and load selection |
| Bonus Reps | Additional reps performed beyond the prescribed count on the final set; 1 by convention |
| Weight (lbs) | Load used; for bodyweight exercises, auto-sourced from the most recent User Measurements bodyweight on or before the workout date |
| RPE | Athlete's rate of perceived exertion, evaluated immediately after the bonus rep on the final set |
| Load Type | Equipment used; defaults from the Exercise Library entry for the exercise, overridable per record |
| Notes | Free-text field for annotations |

---

### Matrix Plan

Each user's priority configuration for the 4×8 Plane × Movement grid. One record per user per cell. Seeded from system defaults at registration. User-editable per cell at any time.

| Attribute | Description | Allowed Values |
|---|---|---|
| User ID | The user this plan belongs to | — |
| Movement Plane | Matrix row | Sagittal, Frontal, Transverse, Neutral |
| Movement Type | Matrix column | Accessory/Isolation, Carry/Bracing, Gait/Locomotion, Hinge, Pull, Push, Rotation, Squat |
| Priority | The user's weekly frequency target for this cell | High (3×/week), Medium (2×/week), Low (1×/week), N/A (not targeted) |

**System default priority grid:**

| | Accessory / Isolation | Carry / Bracing | Gait / Locomotion | Hinge | Pull | Push | Rotation | Squat |
|---|---|---|---|---|---|---|---|---|
| **Sagittal** | Low | High | High | High | High | High | N/A | High |
| **Frontal** | Low | Medium | Medium | N/A | Low | N/A | N/A | Medium |
| **Transverse** | Low | Medium | Medium | N/A | Medium | Medium | High | N/A |
| **Neutral** | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

Neutral is a catch-all for exercises that do not cleanly fit any of the three named planes.

**Default weekly touch targets:** 7 High cells × 3 = 21 sessions/week; 7 Medium cells × 2 = 14 sessions/week; Low cells contribute approximately 4–5 sessions/week.

---

## 4. Measurement Conventions

### The Bonus Rep

On the final set of every exercise, the athlete performs one rep beyond the prescribed count. This additional rep is the **bonus rep**. RPE is evaluated immediately after the bonus rep.

This convention creates a standardized measurement moment across all rep schemes. A set of 3×5 and a set of 3×20 end at very different absolute points of fatigue — evaluating RPE at the last prescribed rep makes them incomparable. Evaluating RPE after the bonus rep places all sessions at the same relative question: *"How many more reps could I do right now, starting from the first rep beyond what was prescribed?"*

### RPE

RPE is logged for per-user longitudinal analysis only. It has no downstream effect on any calculation in the system. Cross-user RPE comparison is excluded. The value of tracking RPE operates on a longer timescale: consistent self-assessment over time builds an athlete's ability to accurately perceive their own output capacity.

| Reps in Reserve (after bonus rep) | RPE | Interpretation |
|---|---|---|
| 3+ | ≤ 7 | Weight too light |
| 2–3 | 7–8 | Target zone |
| 1 | 9 | Near limit |
| 0 (barely completed) | 9.5 | At limit |
| Could not complete bonus rep | 10 | Exceeded capacity |

### Unilateral Volume

For unilateral exercises, actual volume is calculated on both sides: weight × reps × 2. Load selection and DDM always reference the per-side working weight as recorded — the doubling applies to volume calculations only.

---

## 5. Derived Metrics

All derived metrics are computed at runtime from stored data. None are stored.

### Stimulus

The training effect a set targets. Determined by the `Reps` field (reps per set) using the classification table in Section 2. The `Reps` field — not total reps or actual reps — is the input.

### Actual Reps

The total reps performed across all sets, including bonus reps: `(Sets × Reps) + Bonus Reps`.

### Actual Volume

The total mechanical work for a record. For bilateral exercises: `Actual Reps × Weight`. For unilateral exercises: `Actual Reps × Weight × 2`.

### Volume Accounting Identity

All volume is partitioned into exactly two non-overlapping buckets:

> **Unrealized Volume + Realized Volume = Actual Volume**

This identity always holds. Fatigue Volume is a subset of Unrealized Volume — it is not a third accounting bucket.

### Unrealized Vesting %

The proportion of a session's volume still within the adaptation window. Decays from 1.0 immediately after a session to 0.0 at the end of the adaptation window, clamped to [0, 1]:

$$\text{Unrealized Vesting \%} = \max\!\left(0,\, \min\!\left(1,\, 1 - \frac{\text{days elapsed}}{\text{Adaptation Days}}\right)\right)$$

Days elapsed is calculated from the workout date to today.

### Unrealized Volume

The portion of actual volume still within the adaptation window:

$$\text{Unrealized Volume} = \text{round}(\text{Actual Volume} \times \text{Unrealized Vesting \%})$$

This straight-line model was chosen for signal clarity and its behavioral properties (see [Design Philosophy](Design%20Philosophy.md)) rather than for physiological precision.

### Realized Volume

The fully absorbed portion of actual volume. `Actual Volume − Unrealized Volume`.

### Fatigue Volume

Of the unrealized volume, the portion also still within the recovery window:

$$\text{Fatigue Volume} = \text{round}\!\left(\text{Actual Volume} \times \max\!\left(0,\, 1 - \frac{\text{days elapsed}}{\text{Fatigue Days}}\right)\right)$$

Fatigue Volume is always less than or equal to Unrealized Volume. It answers: *"Of the volume still adapting, how much is also still in the recovery window?"*

### Mixed-Stimulus Sessions

A single exercise record may span multiple stimulus types within the same session (e.g., warmup sets at Neural + working sets at Muscle Damage). When this occurs, each set's contribution is tracked under its own stimulus type. Adaptation state and display color are blended proportionally, weighted by each stimulus type's share of the session's total volume for that exercise:

$$w_s = \frac{V_s}{V_{total}}$$

$$\%_{unrealized,blend} = \sum_{s} w_s \times \%_{unrealized,s}$$

$$RGB_{blend} = \sum_{s} w_s \times RGB_s \quad \text{(applied independently to R, G, and B channels)}$$

The blended unrealized percentage is applied as continuous opacity against the blended base color.

### DDM (Desirable Difficulty Max)

The implied current-state weight ceiling for a given exercise and user. DDM is computed at runtime — never stored — and recalculates automatically as new sessions are logged.

**Step 1 — Query all four canonical schemes within the lookback window (90 days):**

All four schemes (3×2, 3×5, 3×10, 3×20) are treated equally. For each scheme, the system finds the most recent session matching that exact sets/reps combination within the 90-day window. Schemes with no qualifying session are skipped — they do not block the calculation. DDM returns `None` only if no qualifying sessions exist in any scheme within the window.

**Step 2 — Back-calculate the implied 100% reference from each contributing scheme:**

$$\text{Implied Reference} = \frac{\text{Weight Used}}{\text{Scheme \%}}$$

DDM is the average of all implied references found (1–4 schemes may contribute):

$$\text{DDM} = \frac{\sum_{i} \text{Implied Reference}_i}{n}$$

**Step 3 — Derive suggested weights per scheme:**

$$\text{Suggested Weight} = \text{DDM} \times \text{Scheme \%}$$

**Example — Bench Press (3×2 outside the 90-day window; 3 schemes contribute):**

| Source | Scheme | Recorded Weight | Implied Reference |
|---|---|---|---|
| 3×2 (N) | 95% | — | No session within 90 days — skipped |
| Most recent 3×5 | MT (80%) | 255 lbs | 255 / 0.80 ≈ 319 |
| Most recent 3×10 | MD (65%) | 205 lbs | 205 / 0.65 ≈ 315 |
| Most recent 3×20 | MS (50%) | 160 lbs | 160 / 0.50 = 320 |
| **DDM** | | | **(319 + 315 + 320) / 3 ≈ 318** |

| Scheme | Calculation | Suggested Weight |
|---|---|---|
| 3×20 (MS) | 318 × 0.50 | ~159 lbs |
| 3×10 (MD) | 318 × 0.65 | ~207 lbs |
| 3×5 (MT) | 318 × 0.80 | ~254 lbs |
| 3×2 (N) | 318 × 0.95 | ~302 lbs |
| Absolute ceiling | 318 × 1.00 | 318 lbs |

As the athlete logs sessions across more schemes, each new qualifying session adds its implied reference to the pool and DDM self-corrects toward a more accurate estimate. A single-scheme history produces a valid DDM; more schemes produce a more representative one.

DDM rises as training consistency builds. It falls as training lapses — this is intentional. DDM reflects current capacity, not career peak. The rationale is in [Design Philosophy](Design%20Philosophy.md).

> **Unilateral exercises:** DDM is always derived from the per-side working weight as recorded. The ×2 unilateral multiplier applies to volume calculations only.

### DDM-Derived Weight Suggestions

For any exercise the athlete is about to train, the system surfaces a suggested weight for each canonical scheme based on DDM × scheme percentage. All suggestions are user-overridable.

---

## 6. System Behaviors

These tracking behaviors operate independently of any specific view and are surfaced across the application.

### Intra-Cell Exercise Variation

Within any Matrix cell in a given program week, the system tracks which exercises have been used and flags when the same exercise fills the same cell more than once. The goal is rotation through different exercises across sessions within the same cell.

**Example — Sagittal Squat (High priority, 3 sessions/week):**

| Session 1 | Session 2 | Session 3 |
|---|---|---|
| Back Squat | Front Squat | Bulgarian Split Squat |

Repeating an exercise across sessions in the same cell triggers a flag. The system surfaces the flag; the athlete decides.

### Stimulus Interleaving

Each time a specific exercise appears in a session, the system checks the most recent prior session of that same exercise and flags if the same stimulus type is used consecutively.

**Example:** If Bench Press was last performed at a Mechanical Tension stimulus (3×5), the next Bench Press session flags a repeat if it also uses Mechanical Tension.

The system surfaces the flag; it does not enforce a different choice.

---

## 7. The Matrix

The Matrix is a 4×8 planning grid — a coverage map of how training is distributed across movement planes and movement types.

- **Rows:** Movement planes — Sagittal, Frontal, Transverse, Neutral
- **Columns:** Movement types — Accessory/Isolation, Carry/Bracing, Gait/Locomotion, Hinge, Pull, Push, Rotation, Squat
- **Each cell** represents a Plane × Movement intersection with a user-configured priority (from Matrix Plan) that defines a weekly session frequency target

An exercise contributes to the cell matching its `Movement Plane` + `Movement Type` attributes in the Exercise Library. Workout Type classification has no effect on Matrix credit.

A cell target is considered **met** for a given period when the required number of sessions have been completed in that cell. The System Behaviors in Section 6 (intra-cell exercise variation and stimulus interleaving) are tracked at the cell level and surfaced alongside target progress.

---

## 8. What the System Surfaces

Three views support the three decisions described in Section 1. Each view answers a specific question.

### Summary Matrix

**Answers:** *"What is the current state of my total training volume?"*

A cross-tabulation of volume by category and exercise. Rows represent volume categories; columns drill from a total across all exercises down to individual exercises within each workout type.

**Row structure:**

| Row | Volume Represented | Filter |
|---|---|---|
| Realized | Realized Volume | Unrealized Vesting % = 0 |
| Adaptation | Unrealized Volume | Unrealized Vesting % > 0 |
| &nbsp;&nbsp;&nbsp;└ Fatigue | Fatigue Volume | Sub-row of Adaptation; Fatigue Volume > 0 |
| &nbsp;&nbsp;&nbsp;└ Non-Fatigue | Unrealized Volume − Fatigue Volume | Sub-row of Adaptation; Fatigue Volume = 0 |
| Total | Actual Volume | None |

Fatigue and Non-Fatigue sub-rows sum to their parent Adaptation row. Each row and sub-row is further broken out by stimulus type (MS / MD / MT / N).

**Column structure:** Total → Workout Type subtotals (Weightlifting, Conditioning, etc.) → individual exercises within each type. Color formatting applies at the individual exercise column level only; Total and Workout Type columns display raw sums without color.

The metric toggle (volume in lbs or total reps) applies globally to this view and the Vesting Grid simultaneously.

### Vesting Grid

**Answers:** *"Which sessions are still actively adapting, and how much load remains unrealized?"*

A Date × Exercise grid showing currently vesting training load with color-coded adaptation state.

- **Rows:** Calendar dates with day name
- **Columns:** Individual exercises only — no aggregate columns; color has no meaning at aggregation level
- **Cell value:** Total actual volume (or reps) for that date/exercise combination

**Color logic:** For each cell, color is determined by blending across all stimulus types present in that session for that exercise (see Mixed-Stimulus Sessions in Section 5). The blended unrealized percentage is applied as continuous opacity against the blended base color: 0% unrealized = no fill; 100% unrealized = full color.

**Axis filters (applies independently to both rows and columns):**
- **All** — all dates and exercises with any recorded volume
- **Adaptation** — only dates/exercises where at least one stimulus is still within its adaptation window (unrealized vesting % > 0)

### Program Balance View

**Answers:** *"Is training hitting its Matrix targets?"*

The 4×8 Matrix grid with three selectable view modes. Period selection covers week, month, year-to-date, and custom date ranges. All cell values and targets reflect the selected period.

**Exposure View** (default)

Each cell shows sessions completed vs. target for the period, exercises used (intra-cell repetition flag from Section 6), and stimulus types used (stimulus interleaving flag from Section 6).

Cell status labels:

| Status | Meaning |
|---|---|
| On Track | Sessions in progress toward target; period not yet complete |
| Behind | Fewer sessions than expected given days elapsed in the period |
| Complete | Target sessions met |
| Exceeded | Sessions logged beyond the target |
| N/A | Cell priority is N/A; not part of the program |

**Volume View**

Each cell shows volume contributed to that Plane × Movement cell for the selected period. Sub-filter options:

| Sub-filter | Value Shown |
|---|---|
| Total | Actual Volume |
| Realized | Realized Volume |
| Adaptation | Unrealized Volume |
| Fatigue | Fatigue Volume |

**Reps View**

Same as Volume View using actual reps in place of lbs. The same sub-filter options apply.

The metric toggle (volume or reps) applies globally across the Volume View, Reps View, Summary Matrix, and Vesting Grid simultaneously.

### Weight Guidance View

**Answers:** *"What load should I use for each scheme today?"*

Surfaces DDM-derived suggested weights for all four canonical schemes for any selected exercise. All suggestions are user-overridable. DDM recalculates automatically as new sessions are logged.

---

## 9. Program Calendar

The system groups workout records into program weeks and named training blocks. All users are evaluated against the same program calendar, ensuring that Matrix coverage targets, leaderboard features, and competitive benchmarking operate over consistent shared periods.

The calendar defines which dates belong to which program week and which training block label (e.g., "Round 1 | Week 3") applies to each week. This shared temporal reference is what makes cross-user comparison structurally meaningful.

---

## 10. Multi-User Boundaries

| Component | Shared | Per-User |
|---|---|---|
| Exercise Library | ✓ All users share one library | — |
| System Parameters | ✓ Fixed system-wide | — |
| Program Calendar | ✓ All users on same calendar | — |
| Default Matrix Priorities | ✓ Seeded from system defaults at registration | — |
| Workout Records | — | ✓ Isolated per user |
| User Measurements | — | ✓ Isolated per user |
| Matrix Plan | — | ✓ Per-user after initial seed |
| DDM | — | ✓ Computed per user per exercise |

Matrix Plan configuration is the primary lever for cross-user structural comparison: users may adjust their priorities differently, and the system can compare whether users are meeting their own targets — not each other's.
