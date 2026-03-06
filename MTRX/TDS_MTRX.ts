// ================================================================================
//   MTRX — Technical Design Specification (TypeScript)
// ================================================================================

// ── Document Purpose ──────────────────────────────────────────────────────────
export const PURPOSE = `
This document is a complete technical design specification for the MTRX workout
tracking application. It maps every component of the system described in this
specification to the specific TypeScript constructs, data structures, and
patterns used in the implementation. The resolution target is: a senior developer
should be able to build the full application using only this document, without
external references.

The document is organized into seven sections mirroring the system's logical
layers, followed by an Implementation Roadmap.

TYPESCRIPT TRANSLATION NOTE:
This document is a direct translation of the Python TDS (TDS_MTRX.py). All
design intent, rationale, and structural decisions are preserved. Differences
from the Python version are explicitly called out inline where they occur.
Python snake_case identifiers are converted to camelCase throughout per
TypeScript convention; the mapping is noted on first occurrence in each section.
`;

// ── System Architecture Overview ──────────────────────────────────────────────
export const ARCHITECTURE = `
The application is organized into four files with a strict dependency hierarchy.
Each layer imports only from the layer(s) below it.

    mtrxConstants.ts   <- no imports; pure type and data definitions
            |
    mtrxFunctions.ts   <- imports: mtrxConstants
            |
    mtrxDatabase.ts    <- imports: mtrxConstants, mtrxFunctions
            |
    mtrxApp.ts         <- imports: mtrxDatabase, mtrxFunctions

WHY THIS SEPARATION ELIMINATES TELEPHONE-GAME ERRORS:
Every derived metric is defined once, as a pure function in mtrxFunctions.ts,
with explicit typed inputs and outputs. The database never recomputes anything --
it stores only raw records. The app never accesses raw state directly -- it calls
database methods and passes the results to functions. A bug in any calculation
is isolated to one function in one file.

TYPESCRIPT UPGRADE: Because all function signatures are statically typed, a
discrepancy between a caller's argument and a function's expected parameter is
a compile error, not a runtime surprise. The telephone-game failure mode the
Python version guards against architecturally is guarded here both architecturally
and by the type checker.
`;


///////////////////////////////////////////////////////////////////////////////
// SECTION 1: SYSTEM-WIDE CONSTANTS  (mtrxConstants.ts)
///////////////////////////////////////////////////////////////////////////////
// These values are fixed program-wide. They are never mutated at runtime.
// Any module that needs them imports this file directly.
//
// VOCABULARY TYPES: TypeScript requires type definitions before first use.
// All controlled-vocabulary union types are declared here at the top of
// Section 1 so they are available to the constant definitions in Sections
// 1.1–1.4. Their runtime ReadonlySet counterparts and ordered arrays appear in
// Section 1.5, where their documentation lives.
//
// Two validation layers exist, each serving a distinct role:
//   Compile-time: union types below. The type checker rejects any literal not
//     in the union before the program runs. No Python equivalent exists.
//   Runtime: ReadonlySet<string> constants in Section 1.5. Used in write-path
//     validation for values that arrive as dynamic strings (user input, JSON
//     deserialization) where the compiler cannot see the value.
//
// The Sets are typed as ReadonlySet<string> rather than ReadonlySet<MovementPlane>
// etc. because their purpose is to validate unknown strings: .has(unknownString)
// must compile without a cast. The compile-time union types handle narrowing
// after validation passes.

export type StimulusKey   = 'N' | 'MT' | 'MD' | 'MS';
export type SchemeKey     = '3x2' | '3x5' | '3x10' | '3x20';
export type MovementPlane = 'Sagittal' | 'Frontal' | 'Transverse' | 'Neutral';
export type MovementType  = 'Accessory/Isolation' | 'Carry/Bracing' | 'Gait/Locomotion'
                          | 'Hinge' | 'Pull' | 'Push' | 'Rotation' | 'Squat';
export type WorkoutType   = 'Conditioning' | 'Weightlifting' | 'Mobility' | 'Recovery';
export type Laterality    = 'Bilateral' | 'Unilateral';
export type LoadType      = 'Band' | 'Barbell' | 'Bodyweight' | 'Cable' | 'Curl Bar'
                          | 'Dumbbell' | 'Kettlebell' | 'Machine' | 'Medicineball' | 'N/A';
export type Priority      = 'High' | 'Medium' | 'Low' | 'N/A';

// ── 1.1 Stimulus Table ────────────────────────────────────────────────────────
// Python: dict with string keys 'N', 'MT', 'MD', 'MS' (untyped).
// TypeScript: Record<StimulusKey, {...}> -- the compiler enforces that all four
// keys are present and each value satisfies the declared shape. A fifth key or
// a missing entry is a compile error.
//
// adaptationDays, fatigueDays: camelCase equivalents of Python's adaptation_days,
// fatigue_days. The 1:1 field mapping is exact; only casing changes.

export const STIMULUS_TABLE: Record<StimulusKey, {
  name:           string;
  adaptationDays: number;
  fatigueDays:    number;
  hex:            string;
}> = {
  N:  { name: 'Neural',             adaptationDays: 21, fatigueDays: 1, hex: '#00C853' },
  MT: { name: 'Mechanical Tension', adaptationDays: 56, fatigueDays: 3, hex: '#FF6A00' },
  MD: { name: 'Muscle Damage',      adaptationDays: 42, fatigueDays: 5, hex: '#FF2D95' },
  MS: { name: 'Metabolic Stress',   adaptationDays: 28, fatigueDays: 2, hex: '#007BFF' },
};

export const STIMULUS_TABLE_NOTES = `
repMin and repMax are intentionally absent. Stimulus classification is defined
by an ordered if/else chain in classifyStimulus (Section 4.1) -- not by
iterating this table. Including those fields here would suggest a table-driven
classification approach to any developer reading constants before functions, and
would create a second place to update if boundaries ever changed. This table's
sole purpose is to supply adaptationDays, fatigueDays, and hex by stimulus key.
`;

// ── 1.2 Canonical Schemes ─────────────────────────────────────────────────────
// Python: dict with string keys '3x5', '3x10', '3x2', '3x20' (untyped).
// TypeScript: Record<SchemeKey, {...}>. pctOfDdm is the camelCase equivalent of
// Python's pct_of_ddm.
//
// The Record type guarantees all four scheme keys are present. Adding a fifth
// scheme requires updating the SchemeKey union -- a single, explicit change that
// the compiler will enforce at every usage site throughout the spec.

export const CANONICAL_SCHEMES: Record<SchemeKey, {
  sets:     number;
  reps:     number;
  stimulus: StimulusKey;
  pctOfDdm: number;
  priority: 'Primary' | 'Secondary';
}> = {
  '3x5':  { sets: 3, reps: 5,  stimulus: 'MT', pctOfDdm: 0.80, priority: 'Primary'   },
  '3x10': { sets: 3, reps: 10, stimulus: 'MD', pctOfDdm: 0.65, priority: 'Primary'   },
  '3x2':  { sets: 3, reps: 2,  stimulus: 'N',  pctOfDdm: 0.95, priority: 'Secondary' },
  '3x20': { sets: 3, reps: 20, stimulus: 'MS', pctOfDdm: 0.50, priority: 'Secondary' },
};

export const CANONICAL_SCHEMES_NOTES = `
The key structure is 'setsXreps' as a string. sets and reps are explicit fields --
not parsed from the key string -- so computeDdm (Section 4.8) reads
CANONICAL_SCHEMES[schemeKey].sets and .reps directly from the single source of
truth. DDM derivation and weight suggestion functions use .pctOfDdm directly.
`;

// ── 1.3 Priority Targets ──────────────────────────────────────────────────────
// Record<Priority, number> enforces exhaustive coverage: the compiler rejects
// this definition if any Priority value is missing. Adding a new priority level
// to the union type immediately surfaces every point in the codebase that must
// be updated -- PRIORITY_TARGETS included. This is a compile-time equivalent of
// Python's runtime KeyError for an unmapped priority.

export const PRIORITY_TARGETS: Record<Priority, number> = {
  High:   3,
  Medium: 2,
  Low:    1,
  'N/A':  0,
};

// ── 1.4 Default Matrix Grid ───────────────────────────────────────────────────
// Python: dict keyed by (movement_plane, movement_type) tuples.
// TypeScript: Record<MovementPlane, Record<MovementType, Priority>>.
//
// WHY NESTED RECORD OVER FLAT STRING KEYS:
// JavaScript has no hashable tuple type. The natural migration path from Python
// tuple keys is a flat string key such as 'Sagittal|Push'. This is rejected
// in favor of the nested Record for three structural reasons:
//
// 1. COMPLETENESS ENFORCEMENT: Record<MovementPlane, Record<MovementType, Priority>>
//    instructs the compiler to verify that all 4 planes and all 8 movement types
//    are present for every plane. A missing cell is a compile error. A flat
//    string-key map provides no such guarantee -- a missing entry is silent until
//    runtime.
//
// 2. ACCESS PATTERN ALIGNMENT: Every consumer of this grid iterates as
//    for plane → for type (see buildProgramBalance, Section 6.3). The nested
//    structure matches the dominant access pattern exactly:
//    plan[plane][type] rather than plan[`${plane}|${type}`].
//    Lookup is two direct property accesses, not a string
//    construction step.
//
// 3. CONSISTENCY WITH matrixPlans (Section 3.5): the per-user matrix plan uses
//    the same type (MatrixPlan = Record<MovementPlane, Record<MovementType, Priority>>),
//    making seedMatrixPlan a structuredClone call with no key transformation.
//
// STRUCTURAL NOTE: This is a deliberate departure from the Python spec's tuple-key
// approach. Both encode the same 4×8 grid with the same semantics. The nested
// Record is idiomatic TypeScript; the tuple key is idiomatic Python.
// Key: plan[plane][type]   (compare: Python plan[(plane, type)])

export const DEFAULT_MATRIX_GRID: Record<MovementPlane, Record<MovementType, Priority>> = {
  Sagittal: {
    'Accessory/Isolation': 'Low',
    'Carry/Bracing':       'High',
    'Gait/Locomotion':     'High',
    Hinge:                 'High',
    Pull:                  'High',
    Push:                  'High',
    Rotation:              'N/A',
    Squat:                 'High',
  },
  Frontal: {
    'Accessory/Isolation': 'Low',
    'Carry/Bracing':       'Medium',
    'Gait/Locomotion':     'Medium',
    Hinge:                 'N/A',
    Pull:                  'Low',
    Push:                  'N/A',
    Rotation:              'N/A',
    Squat:                 'Medium',
  },
  Transverse: {
    'Accessory/Isolation': 'Low',
    'Carry/Bracing':       'Medium',
    'Gait/Locomotion':     'Medium',
    Hinge:                 'N/A',
    Pull:                  'Medium',
    Push:                  'Medium',
    Rotation:              'High',
    Squat:                 'N/A',
  },
  Neutral: {
    'Accessory/Isolation': 'N/A',
    'Carry/Bracing':       'N/A',
    'Gait/Locomotion':     'N/A',
    Hinge:                 'N/A',
    Pull:                  'N/A',
    Push:                  'N/A',
    Rotation:              'N/A',
    Squat:                 'N/A',
  },
};

// ── 1.5 Controlled Vocabulary ─────────────────────────────────────────────────
// As described at the top of this section, runtime validation uses
// ReadonlySet<string> and compile-time enforcement uses the union types above.
// These sets mirror Python's set literals exactly -- same members, same purpose.
// Set.has() is O(1) and communicates intent: these are membership-check
// structures, not ordered sequences.
//
// The runtime validation pattern used throughout the database (Section 3):
//   if (!MOVEMENT_PLANES.has(value)) throw new Error(`Invalid movement plane: ${value}`)
//
// ORDERING: Python maintains a separate ordered list alongside every set for
// deterministic iteration. TypeScript does the same: the ReadonlySet above
// handles validation; the readonly array below handles iteration.

export const MOVEMENT_PLANES:  ReadonlySet<string> = new Set(['Sagittal', 'Frontal', 'Transverse', 'Neutral']);
export const MOVEMENT_TYPES:   ReadonlySet<string> = new Set(['Accessory/Isolation', 'Carry/Bracing', 'Gait/Locomotion', 'Hinge', 'Pull', 'Push', 'Rotation', 'Squat']);
export const WORKOUT_TYPES:    ReadonlySet<string> = new Set(['Conditioning', 'Weightlifting', 'Mobility', 'Recovery']);
export const LATERALITY:       ReadonlySet<string> = new Set(['Bilateral', 'Unilateral']);
export const LOAD_TYPES:       ReadonlySet<string> = new Set(['Band', 'Barbell', 'Bodyweight', 'Cable', 'Curl Bar', 'Dumbbell', 'Kettlebell', 'Machine', 'Medicineball', 'N/A']);
export const PRIORITY_OPTIONS: ReadonlySet<string> = new Set(['High', 'Medium', 'Low', 'N/A']);

// Ordered arrays for deterministic iteration (e.g. building the 4×8 grid).
// Validation uses the Sets above; iteration uses these arrays for stable
// row/column order. readonly prevents mutation at both compile-time and runtime.

export const MOVEMENT_PLANES_ORDERED: readonly MovementPlane[] = [
  'Sagittal', 'Frontal', 'Transverse', 'Neutral',
];
export const MOVEMENT_TYPES_ORDERED: readonly MovementType[] = [
  'Accessory/Isolation', 'Carry/Bracing', 'Gait/Locomotion',
  'Hinge', 'Pull', 'Push', 'Rotation', 'Squat',
];

// ── 1.6 Program Calendar Anchor and Date Utilities ────────────────────────────
// Python uses datetime.date objects throughout. TypeScript uses ISO 8601 date
// strings ('YYYY-MM-DD'). This is the canonical date representation for this
// application. The choice is deliberate:
//
//   -- ISO strings are JSON-native: no serialization transform is needed on
//      save/load, unlike datetime.date objects which require .isoformat() and
//      datetime.date.fromisoformat() in the Python spec's Stage 6 serialization
//      logic. In TypeScript, dates round-trip through JSON transparently.
//
//   -- ISO date-only strings are lexicographically sortable: string comparison
//      ('2026-01-12' > '2026-01-05') correctly reflects chronological order.
//      This allows [...arr].sort((a, b) => a.date.localeCompare(b.date)) to
//      replace Python's sorted(list, key=lambda m: m['date']).
//
//   -- Date.parse() of ISO date-only strings yields UTC midnight milliseconds
//      (ES2015+ specification). This makes day arithmetic exact integer
//      operations without any DST edge cases.
//
//   -- No external date library is required.
//
// The DateString type alias documents intent without restricting the compiler-
// level type (it remains `string` at runtime). System boundary validation
// (user input, deserialization) is handled at the database write path.
//
// The three utility functions below give Section 4 functions clean named calls
// in place of inline Date arithmetic, exactly as datetime.timedelta provides
// clean calls in the Python version. They are pure functions with explicit
// typed inputs and outputs, consistent with the design principle that
// derivations are named, isolated, and independently testable.
//
// today() returns the LOCAL calendar date, matching Python's
// datetime.date.today() behavior. addDays() and daysDiff() operate in UTC
// throughout to guarantee exact integer day counts.

export type DateString = string;  // ISO 8601: 'YYYY-MM-DD'

export const PROGRAM_START_DATE: DateString = '2026-01-05';  // First Monday of the program

export function daysDiff(a: DateString, b: DateString): number {
  // Returns the number of days from a to b. Positive when b is after a,
  // matching Python's (b - a).days convention.
  // Date.parse of ISO date-only strings is UTC midnight; result is always
  // an exact integer.
  return (Date.parse(b) - Date.parse(a)) / 86_400_000;
}

export function addDays(d: DateString, n: number): DateString {
  // Adds n days (positive or negative) to d.
  // Stays in UTC throughout to avoid DST discontinuities.
  // Python equivalent: date + datetime.timedelta(days=n)
  const ms = Date.parse(d) + n * 86_400_000;
  const r   = new Date(ms);
  return [
    r.getUTCFullYear(),
    String(r.getUTCMonth() + 1).padStart(2, '0'),
    String(r.getUTCDate()).padStart(2, '0'),
  ].join('-');
}

export function today(): DateString {
  // Returns the local calendar date as 'YYYY-MM-DD'.
  // Python equivalent: datetime.date.today()
  const d = new Date();
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, '0'),
    String(d.getDate()).padStart(2, '0'),
  ].join('-');
}

// ── 1.7 Shared Type Interfaces ────────────────────────────────────────────────
// Python's duck-typed dicts communicate entity shapes through "Example state"
// blocks in Section 3. TypeScript requires explicit interface declarations.
// These interfaces are the TypeScript formalization of those Example state
// blocks -- same fields, same semantics, compiler-enforced.
//
// WHY mtrxConstants.ts AND NOT mtrxDatabase.ts:
// These are data contracts imported by all four modules. Locating them in the
// database file would invert the dependency hierarchy: mtrxFunctions.ts cannot
// import from mtrxDatabase.ts (that import direction is forbidden by the
// architecture in Section 2). Interfaces live here so every layer can import
// them without creating a circular dependency.
//
// VIEW OUTPUT SHAPES (SummaryRow, VestingRow, BalanceRow) ARE NOT DEFINED HERE.
// They are rendering contracts specific to how each view surfaces data. They
// live in Section 6 alongside the functions that produce them.
//
// NAMING: Python dict keys use snake_case ('exercise_name', 'join_date').
// TypeScript interfaces use camelCase ('exerciseName', 'joinDate') per
// convention. The field mapping is 1:1 throughout.

export interface UserRecord {
  username:    string;
  displayName: string;  // Python: 'display_name'
  email:       string;
  joinDate:    DateString;  // Python: 'join_date' as datetime.date
}

export interface Measurement {
  measurementId: number;    // Python: 'measurement_id'
  date:          DateString;
  bodyweight:    number;
  additional:    Record<string, number>;  // Python: dict  (str -> float)
}

export interface ExerciseRecord {
  exerciseName:    string;    // Python: 'exercise_name'
  workoutType:     WorkoutType;    // Python: 'workout_type'
  laterality:      Laterality;
  defaultLoadType: LoadType;    // Python: 'default_load_type'
  movementType:    MovementType;    // Python: 'movement_type'
  movementPlane:   MovementPlane;    // Python: 'movement_plane'
}

// ExerciseUpdatableFields: the type accepted by updateExercise() (Section 3.3).
// Python: **kwargs validated at runtime against known field names. The database
// must explicitly check 'exercise_name' is not in kwargs and raise ValueError.
//
// TypeScript: Partial<Omit<ExerciseRecord, 'exerciseName'>> -- the permitted
// fields are a compiler-enforced contract. Passing exerciseName as an update
// key, or passing any unknown field, is a compile error.
//
// STRUCTURAL UPGRADE: Python's runtime validation is replaced by a compile-time
// contract. The invariant 'exerciseName cannot be changed' is structurally
// impossible to violate from a caller -- not just check-and-throw. The runtime
// error path in the Python version is eliminated entirely.
export type ExerciseUpdatableFields = Partial<Omit<ExerciseRecord, 'exerciseName'>>;

export interface WorkoutRecord {
  recordId:     number;    // Python: 'record_id'
  userId:       number;    // Python: 'user_id'
  date:         DateString;
  exerciseName: string;    // Python: 'exercise_name'
  sets:         number;
  reps:         number;
  bonusReps:    number;    // Python: 'bonus_reps'
  weight:       number;
  rpe:          number;
  loadType:     LoadType;    // Python: 'load_type'
  notes:        string;
}

// MatrixPlan: the per-user matrix plan type (Section 3.5).
// Python: dict[int, dict[tuple, str]] -- the inner dict maps (plane, type)
// tuples to a Priority string.
// TypeScript: the inner structure is Record<MovementPlane, Record<MovementType, Priority>>,
// consistent with DEFAULT_MATRIX_GRID (Section 1.4). Seeding a new user's plan
// uses structuredClone(DEFAULT_MATRIX_GRID) -- see Section 3.5 for why
// structuredClone is required here where Python used a shallow dict() copy.
// Lookup: plan[plane][type]  (Python: plan[(plane, type)])
export type MatrixPlan = Record<MovementPlane, Record<MovementType, Priority>>;

// BlendedAdaptation: return type of computeBlendedAdaptation (Section 4.10).
export interface BlendedAdaptation {
  blendedPct: number;  // Python: 'blended_pct'
  blendedHex: string;  // Python: 'blended_hex'
}

// WeightGuidanceResult: return type of buildWeightGuidance (Section 6.4).
export interface WeightGuidanceResult {
  exercise:    string;
  ddm:         number | null;  // Python: float | None
  suggestions: Record<SchemeKey, number> | null;
  note:        string;
}

// ── End of Section 1 ──────────────────────────────────────────────────────────


///////////////////////////////////////////////////////////////////////////////
// SECTION 2: CLASS ARCHITECTURE  (mtrxDatabase.ts)
///////////////////////////////////////////////////////////////////////////////
// Two classes. The file structure mirrors the Python version exactly.
// Module-level imports for mtrxDatabase.ts:
//
//   import {
//     DEFAULT_MATRIX_GRID, LOAD_TYPES, MOVEMENT_PLANES, MOVEMENT_TYPES,
//     PRIORITY_OPTIONS, WORKOUT_TYPES, LATERALITY,
//     MOVEMENT_PLANES_ORDERED, MOVEMENT_TYPES_ORDERED,
//     DateString, ExerciseRecord, ExerciseUpdatableFields, MatrixPlan,
//     Measurement, MovementPlane, MovementType, Priority,
//     UserRecord, WorkoutRecord,
//   } from './mtrxConstants';
//   import * as fn from './mtrxFunctions';
//
// PANDAS / MATPLOTLIB REMOVAL:
// The Python version's mtrx_app.py imports pandas and matplotlib. Neither has
// an equivalent import here. View functions in Section 6 return typed arrays
// (SummaryRow[], BalanceRow[], etc.) -- they have no library dependency.
// Visualization is a display-layer concern in mtrxApp.ts only; a library such
// as Chart.js is imported there at the point of use, keeping the data pipeline
// entirely library-free. This is documented in Section 6.

// ── 2.1  MtrxDatabase ─────────────────────────────────────────────────────────
// The internal state store. All five data entities live here as private fields.
// No external code accesses them directly.
//
// TYPESCRIPT UPGRADE — private IS COMPILER-ENFORCED:
// Python's name-mangling convention (self.__attr) obfuscates private attributes
// but does not prevent access: instance._MtrxDatabase__users is legally
// reachable from any Python code at runtime. TypeScript's private keyword is a
// compile-time guarantee: any expression outside the class body that references
// a private field is a type error. The Repository contract (described below
// under Interface Contract) is therefore enforced structurally by the type
// checker, not just by convention.
//
// FIELD TYPE MAPPING (Python → TypeScript):
//   __users:        dict[int, dict]              → Map<number, UserRecord>
//   __measurements: dict[int, list[dict]]        → Map<number, Measurement[]>
//   __exercises:    dict[str, dict]              → Map<string, ExerciseRecord>
//   __records:      list[dict]                   → WorkoutRecord[]
//   __matrixPlans:  dict[int, dict[tuple, str]]  → Map<number, MatrixPlan>
//
// The Map type replaces Python's dict throughout. Map<number, V> provides O(1)
// keyed lookup, explicit key typing, and clean .has() / .get() / .set() /
// .delete() semantics. It is preferred over a plain object index signature
// (Record<number, V>) for mutable runtime collections because Map keys are
// first-class values, .size is a native property, and iteration order is
// insertion-ordered by specification.
//
// WorkoutRecord[] (flat array) is the direct equivalent of Python's list[dict]
// for the records store. The rationale for this structure is in Section 3.4.
//
// Full method signatures are specified in Section 3. All methods that could
// fail throw new Error(message) with descriptive messages on bad input. The
// MtrxApp call site wraps these in try/catch (Python: try/except).
//
// camelCase mapping: __user_counter → userCounter, __measure_counter →
// measureCounter, __record_counter → recordCounter, __matrix_plans → matrixPlans.

export const MTRX_DATABASE_STUB = `
class MtrxDatabase {

  private userCounter:    number = 1;
  private measureCounter: number = 1;
  private recordCounter:  number = 1;

  private users:       Map<number, UserRecord>      = new Map();
  private measurements:Map<number, Measurement[]>   = new Map();
  private exercises:   Map<string, ExerciseRecord>  = new Map();
  private records:     WorkoutRecord[]              = [];
  private matrixPlans: Map<number, MatrixPlan>      = new Map();

  toString(): string {
    return \`MtrxDatabase | Users: \${this.users.size} | \`
         + \`Exercises: \${this.exercises.size} | \`
         + \`Records: \${this.records.length}\`;
  }

  // Full method signatures: Section 3
}
`;

// toString() is the TypeScript equivalent of Python's __repr__. It uses a
// template literal (Python: f-string) and accesses Map.size (Python: len(dict))
// and Array.length (Python: len(list)).

// ── 2.2  MtrxApp ──────────────────────────────────────────────────────────────
// The public controller. Holds one MtrxDatabase instance. All user-facing
// operations flow through this class. Calls mtrxFunctions (imported as fn) for
// every derived computation; never reimplicates them inline.
//
// MtrxApp methods are thin orchestrators: pull data from the database, pass it
// to a function, return or display the result. No business logic lives here.
//
// ERROR HANDLING AT THE CALL SITE:
// Python wraps database calls in try/except at the MtrxApp level.
// TypeScript equivalent: try { ... } catch (e) { ... } at each MtrxApp method
// that delegates to a database method that can throw. The database methods
// themselves throw new Error(message) -- they do not swallow errors.
//
// INTERFACE CONTRACT (Repository Pattern):
// MtrxDatabase's public methods -- getRecords(), getExercise(), getUser(), etc.
// -- are a stable contract. No code outside MtrxDatabase ever touches the
// private fields (users, exercises, records, etc.) directly. In TypeScript,
// this contract is enforced by the compiler: any attempt to access a private
// field from MtrxApp is a type error, not just a convention violation.
//
// This boundary is what makes the storage backend swappable: replacing
// in-memory Maps with SQLite queries requires changing only MtrxDatabase
// internals; MtrxApp and all view functions are completely untouched. At
// thousands of users this swap is a localized change, not a rewrite. Treat
// this boundary as an invariant: if a view function ever accesses a private
// field directly, the contract is broken.

export const MTRX_APP_STUB = `
import * as fn from './mtrxFunctions';
import { MtrxDatabase } from './mtrxDatabase';

class MtrxApp {

  private db: MtrxDatabase = new MtrxDatabase();

  toString(): string {
    return \`MtrxApp | \${this.db}\`;
  }

  // Full method signatures: Section 3 (database delegation) and Section 6
  // (view orchestration). Visualization methods import Chart.js at the top
  // of mtrxApp.ts -- not shown here -- and are the only methods in the
  // application with a library dependency.
}
`;

// ── End of Section 2 ──────────────────────────────────────────────────────────
