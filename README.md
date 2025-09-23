# FINAN6520 – Weekly Homework Workflow

This repository contains weekly modules (1–12). Each module includes:
- Lecture notes (e.g., `L0X_*.py`, `M0X_LECTURE_NOTES.md`)
- Breadcrumbs script to demonstrate expected outputs (e.g., `H0X_BREADCRUMBS.py`)
- Student homework file (e.g., `H0X_*_HARMER_KAI_U0895215.py`)
- Homework checker (e.g., `H0X_homework_checker.py` or `H0X_HOMEWORK_CHECKER.PY`)

We follow a consistent, repeatable process every week.

## Weekly Process (Modules 5–12)

1) Verify module layout
- Ensure the week’s files exist under `.vscode/Module X/` with the naming conventions above.

2) Create the homework checker
- Model it after the previous week’s checker.
- Import the student homework file directly: `import H0X_*_HARMER_KAI_U0895215 as H0X`.
- Implement tests for each question using ONLY expectations visible in that module’s breadcrumbs file.
- Be strict: outputs must match breadcrumb formatting exactly (values, shapes, dtypes, indexes, scalar types). No dtype coercion or index resets.
- Provide safe execution with a `safe_call` wrapper to avoid crashing on student errors.
- For any data tool fetching (e.g., yfinance), validate structure not values unless the breadcrumbs show a stable format. If the breadcrumbs expect specific columns (e.g., `Adj Close`), ensure the function or the checker accounts for API defaults (e.g., `auto_adjust=False`).

3) Run and refine
- Run the breadcrumbs script to observe exact printed outputs.
- Run the homework checker you created; tighten comparisons until the checker matches the breadcrumb outputs exactly.

4) Complete the homework
- Implement each function in the student homework file using only concepts covered up to that module (Modules 1..X).
- When numeric or scalar type formatting matters (e.g., Q4/Q7 ints vs numpy ints, Python float vs numpy float), cast explicitly to match breadcrumbs.
- Re-run the checker to confirm all pass.

5) Document any deviations
- If a live data source’s output can vary (e.g., yfinance), either:
  - Keep the checker structural (shape, index, required columns), or
  - Normalize the function output (e.g., `auto_adjust=False`, flatten MultiIndex columns) to match breadcrumbs consistently.

## Checker Strictness Guidelines

- Arrays: same shape and dtype; float arrays compared with tight tolerance; int/bool arrays exact equality.
- Tuples: enforce element types and values; if breadcrumbs show Python int, require `int`; if they show numpy scalar, require `np.*` scalar.
- Pandas DataFrames/Series: require exact equality with `check_dtype=True`, `check_names=True`; no index resetting.
- Scalars (means/stds/selected values): cast to Python `float`/`int` where breadcrumbs show those types.

## Environment Setup

- Python packages used in lectures: `numpy`, `pandas`, `yfinance`, `matplotlib`.
- If a dependency is missing, install it into the active environment.

## How to Run

- Run breadcrumbs for a module (example for Module 4):
  - `python ".vscode/Module 4/H04_BREADCRUMBS.py"`

- Run the homework checker (example for Module 4):
  - `python ".vscode/Module 4/H04_HOMEWORK_CHECKER.PY"`

## Conventions to Preserve

- Do not edit files outside the target module unless explicitly requested.
- Keep function names/signatures consistent with breadcrumbs.
- Use only concepts covered so far when completing homework.
- Prefer small, targeted changes; avoid refactors unrelated to the weekly task.

## Notes for Future Weeks

- Start by copying the most recent checker as a template; update inputs/expected outputs from the new week’s breadcrumbs.
- For any ambiguity in expected output, rely on the breadcrumbs printout.
- Validate frequently: run breadcrumbs and the checker after each set of changes.
- If you hit a data-source variability issue, propose two options: normalize function output vs relax the checker (document which one you choose).
