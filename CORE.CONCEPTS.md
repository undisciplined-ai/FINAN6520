# Core Concepts

## Module 1

- Variables and Assignment
  - Defining a variable with a string value: e.g., `my_variable = "Hello, World!"`
  - Names bind to values; later code can reference the name to access its bound value.
  - Strings are immutable sequences of characters, commonly delimited with single or double quotes.

- Printing Output
  - Using `print(...)` to display values to standard output: `print(my_variable)`.
  - Printing is useful to verify state and observe results while learning basics.

- Basic Script Structure
  - A Python file can contain definitions and executable statements; when run, statements execute top-to-bottom.
  - Minimal program example demonstrates variable creation then printing its value.

## Module 2

- Everything Is an Object
  - Variables reference objects (values) that live at unique identities in memory.
  - Identity vs value: same value can exist at different identities.

- Variables and Naming
  - Snake case for regular variables, e.g., `my_var_name`. Constants in uppercase, e.g., `MY_CONSTANT`.
  - Creation and reassignment: `my_var = 1`; dynamic typing allows `my_var = 'hello'` later.
  - Assignment variations: simple arithmetic updates (`+=, -=, *=, /=, **=, %=`), chained assignment (`x = y = z = my_var`), multiple assignment (`a, b = 300, 400`).
  - Aliasing: `my_var_2 = my_var` binds two names to the same object.

- Reserved Words (avoid as identifiers)
  - `False, None, True, and, as, assert, break, class, continue, def, del, elif, else, except, finally, for, from, global, if, import, in, is, lambda, nonlocal, not, or, pass, raise, return, try, while, with, yield`.

- Operators
  - Arithmetic: `+ - * / ** % //` (modulus gives remainder; floor division rounds down).
  - Comparison: `== != > < >= <=`.
  - Logical: `and / or`; bitwise `& / |` examples used with booleans.

- Core Data Types
  - Numbers (int, float): numeric, non-iterable; `type()` to inspect.
  - List: ordered, mutable, mixed types allowed; indexing, `append`, `pop`.
  - Tuple: ordered, immutable; convert via `tuple([..])`.
  - Dictionary: key/value store; `keys`, `values`, `items`, `update`, building from `zip` then indexing `list(x.items())[0]`.
  - String: quotes, triple-quoted multiline, methods `upper`, `lower`, slicing and reverse `[::-1]`.
  - Set: unique elements, non-indexable.

- Casting Between Types
  - Examples: `float(4)`, `str(1)`; use `type()` to confirm.

- Functions
  - Define with `def`, call vs reference; `return` sends a value back to the caller.
  - Example: `some_math(x)` modifies then returns; capture with `our_math_solution = some_math(5)`.

- Scope: Global vs Local
  - Globals exist throughout script; locals inside functions/blocks; return locals to use outside.

- Script Execution and __name__ Guard
  - `if __name__ == "__main__":` runs only when executed as a script; when imported, `__name__` differs.

- Homework Pattern (preview)
  - Write functions with precise inputs/outputs; they’ll be tested separately; follow naming conventions.

## Module 3

- Control Flow and Logic Overview
  - Logic enables different code paths based on conditions.
  - Conditionals are evaluated as booleans (True/False).

- Booleans and Logical Operations
  - Boolean literals: `True (1)`, `False (0)`; booleans participate in arithmetic (e.g., `True + True == 2`).
  - Logical operators: `and`, `or`, `not`; bitwise forms `&`, `|` shown with booleans.
  - Identity and membership: `is` (same object), `in` (membership in iterables).
  - Comparison operators: `==`, `!=`, `>`, `<`, `>=`, `<=`.
  - Notes: Avoid using `is` with literals; use `==` for value equality.

- Evaluating Compound Expressions
  - Nested boolean expressions, precedence, and step-by-step evaluation by hand.
  - Examples include mixing `and/or/not`, arithmetic with `bool(...)`, and chained comparisons.

- If/Elif/Else Statements
  - Basic branching: `if`, `elif`, `else`.
  - Pythonic boolean checks (e.g., `if variable1:` vs `if variable1 == True:`).
  - Membership checks in conditionals (e.g., `if target in collection:`) and `pass` as a placeholder.
  - Only the first satisfied branch executes; later branches are skipped.

- Loop Control Keywords
  - `pass`: do nothing and continue executing the block.
  - `continue`: skip to the next loop iteration.
  - `break`: exit the loop immediately.

- For Loops and Iteration
  - Iterate over iterables with a loop variable (e.g., `for i in seq:`).
  - Use temporary variables inside loops; `_` as a throwaway variable.
  - Building new lists by appending within a loop.

- Patterns and Nested Loops
  - Nested loops to generate patterns (e.g., triangles using `#`), control spacing and repeated characters.

- Iterating Dictionaries
  - Unpack key/value pairs with `for key, value in dict.items():`.
  - `enumerate(iterable)` yields `(index, value)` pairs for indexed iteration.

- List Comprehensions
  - Concise syntax: `[expr for item in iterable if condition]`.
  - Create filtered or transformed lists; examples include presence checks and simple replications.

- While Loops
  - Loop runs while a condition is True; update the condition inside the loop.
  - Commonly used for interactive or sentinel-controlled processes; beware of infinite loops.

- Input, Try/Except/Finally
  - `input()` to get user input (string); cast as needed.
  - `try` to attempt a block, `except` to handle specific exceptions (e.g., `ValueError`), `finally` always runs.

- Worked Examples
  - Even-number detection and formatted f-strings in loop output.
  - Grading logic using `if/elif/else` and `zip(name_list, grade_payload)` to build dicts.
  - Number Guessing game: validates input range, counts guesses, provides proximity hints, and uses `break`.
  - Nested conditionals with a nested dictionary (day/week attributes) to generate contextual responses.

## Module 4

- Libraries and Imports
  - pandas as `pd`, numpy as `np`, datetime as `dt`, yfinance as `yf`, matplotlib.pyplot as `plt`.

- NumPy Basics
  - Arrays from lists and nested lists; vectors vs matrices via `np.array`.
  - Constructors: `np.zeros((n))`, `np.zeros((r,c))`, `np.linspace(start, stop, num)`, `np.arange(n)`.
  - Random: `np.random.rand(n[,m])` (uniform), `np.random.randn()` (normal), `np.random.randint(low, high, size)`.
  - Reshaping: `.reshape(r,c)`; shape must match element count.
  - Aggregations and arg locations: `.max()/.min()`, `.argmax()/.argmin()`.
  - Indexing and slicing: `arr[i]`, `arr[a:b]`, 2D selection like `mat[r]`, `mat[r][c]`, `mat[:k]`.
  - Elementwise math: `+ - * / **`, `np.exp`, `np.log`, `np.sin`, `np.cos` (arrays must align in length).
  - Basic stats: `np.mean`, `np.median`, `np.std`.

- pandas Series and DataFrames
  - Series creation from list/ndarray/dict; custom index.
  - DataFrame from `np.random.randn(r,c)` with seed and labeled index/columns.
  - Column selection: `df['col']`, multiple columns with list; new column assignment; `drop(..., axis=1)`; `inplace=True`.
  - Row drop: `df.drop('row_label', axis=0)`.
  - Indexing: `.loc[row]`, `.iloc[i]`, `.loc[row, col]`, `.loc[[r1,r2],[c1,c2]]`.
  - Conditional selection: comparisons produce boolean DataFrames; filter with masks and chained conditions using `&`.
  - Index tricks: `reset_index()`, add a column, `set_index(col[, inplace=True])`.

- GroupBy and DataFrame Operations
  - `df.groupby('key').mean()`, `.describe()`, and selecting group with `.loc['AAPL']` on described stats.
  - Value methods: `value_counts`, `unique`, `nunique`; aggregations like `.sum()`; `sort_values(by=...)`.
  - Apply functions: define `def times2(x): return x*2`; use `.apply(func)` or `.apply(lambda x: ...)`.

- Handling Missing Data and Shifts
  - `dropna()` and `dropna(thresh=k)` for row-wise NA handling.
  - `fillna(value='...')` to impute.
  - `shift(periods[, fill_value=...])` to offset data.

- Data Gathering with yfinance (and Tiingo example)
  - Download: `yf.download(tickers, start, end)`; convert index to datetime dates; inspect with `.head()`, `.describe()`, `.info()`.
  - Select adjusted close slice: `stock_data['Adj Close']`; simple `.plot()` on Series/DataFrame.
  - Tiingo API helper demonstrates REST client usage, JSON to DataFrame, datetime parsing, renaming columns to OHLCV, and assembling multi-ticker panel data.

- Visualization with Matplotlib (stateful API)
  - Basic line plots: `plt.plot(x, y, 'g')`; add labels/titles; subplots via `plt.subplot(nrows,ncols,idx)`.
  - Multiple lines, colors, markers, line styles, and linewidth (`lw`); legends via `ax.legend()`.
  - Figure/axes via object-oriented API: `fig, ax = plt.subplots()` or `fig.add_axes([...])`; set with `set_xlabel`, `set_ylabel`, `set_title`.
  - Inset axes pattern with two axes on one figure; save with `fig.savefig(..., bbox_inches='tight')`.

- pandas Plotting
  - Data prep: download multi-ticker adjusted close and set datetime index.
  - `DataFrame.plot()` basics; specify y columns list; adjust `figsize` and `colormap`.
  - Subplots per column: `plot(subplots=True, figsize=(w,h), colormap='...')`.

## Module 5

- Goal and Theme
  - Apply programming tools to finance problems: compute equity betas, transform returns, and track portfolio value over time.

- Imports and Context
  - math, pandas, numpy, yfinance, matplotlib, datetime.timedelta; scripts show separation between implementation and runner.

- Beta of Equity Products
  - Concept: Beta measures systematic risk vs market (SPY baseline beta = 1). >1 more volatile; <1 less volatile; negative implies opposite direction.
  - Formula: Beta = Covariance(Re, Rm) / Variance(Rm); where Re is equity return, Rm is market return.
  - Supporting stats: variance measures dispersion; std dev = sqrt(variance); covariance captures joint movement.

- User Input and Data Gathering
  - `security_time_gathering()` loop: prompt for ticker count, collect tickers (uppercased), prompt for begin/end dates (YYYY-MM-DD); simple input validation and re-prompt on errors.
  - `gather_data()`: calls the above, appends 'SPY' as market benchmark, downloads prices via `yf.download`, selects `Adj Close`.
  - Note on Adj Close: reflects dividends and splits.

- Continuous Returns (log returns)
  - `continuous_returns(df, frequency)`: resample by frequency (e.g., 'M', 'D') with `.last()`, compute log returns `np.log(df/df.shift(1))`, drop NA, return DataFrame.
  - Rationale: log returns are additive across periods and more normal-like; supports statistical inference.

- Beta Calculator
  - `beta_calculator(return_df)`: separates market series (`SPY`), removes SPY column for per-security loop.
  - For each security: cumulative return, alpha (security_return - market_return), covariance using `np.cov(market, security)[0][1]`, beta via covariance/var(market).
  - Builds and prints a summary DataFrame with index=security names plus 'Market', columns: Beta, Period Return, Period Alpha.

- Portfolio Value Tracking
  - Purpose: see equity value over time in dollars using continuous returns, given initial investment amounts and weights.
  - Inputs: price DataFrame (Adj Close), `weights` list, `investment_dollar_amounts` list.
  - Share allocation: floor division to compute share counts at t0; compute initial equity per security and total portfolio equity.
  - Transform: compute daily log returns; simulate compounding equity each period using `math.exp(return)` on last dollar value.
  - Build `equity_df` with per-security equity and a Date column; set Date as index; add `Total_Equity` column (row-wise sum).
  - Metadata: dict per security with SHARES, ENTRY_PRICE, CURRENT_PRICE, initial/current portfolio values/weights, cumulative return, and SD; includes a TOTAL_PORTFOLIO summary (initial value, outcome value, cumulative return, SD of portfolio returns).

- Runner Script Usage
  - Example tickers and download; build `investment_total`, `weights`, and `investment_dollar_amounts` from weights.
  - Run `portfolio_value_tracking(...)` to compute `equity_data` and `portfolio_metadata`.
  - Plot with matplotlib: overall Total_Equity and individual security equity; format y-axis as dollars; show legend and print metadata.

## Module 6

- Focus and Format
  - Core prep with 30 targeted functions mixing Python fundamentals and pandas/yfinance usage.
  - Each function has precise I/O requirements validated by a breadcrumbs runner.

- Booleans, Types, and Casting (Q1–Q3)
  - `isinstance(x, bool)`, `bool(x)` truthiness, `type(x)` to inspect runtime type.

- Dicts: Build, Mutate, Access (Q4–Q10)
  - Create dict from two lists with `zip`, index via `list(d.items())[i]`.
  - `pop('TARGET', None)`, iterating keys, `clear()`, `update({...})`.
  - `get('TARGET')` access, membership `if 'TARGET' in d` and equality checks.
  - Nested dict access `d['KEY_1']['INNER_KEY_1']` and tuple returns.
  - Use `enumerate` to build dict values based on index.

- Loops and Comprehensions (Q11–Q14)
  - Range-based loops to build lists; conditional even filtering; nested loops with conditional multiply.
  - List comprehension for elementwise transforms `[x*4 for x in seq]`.

- Boolean Logic and Control Flow (Q15–Q20)
  - Nested if/else with booleans; identity vs equality in checks used explicitly; combining booleans with `or` then arithmetic on truth values.
  - Numeric branching: thresholds and exponentiation; chained if/elif/else precedence; staged arithmetic transforms and comparisons.
  - Simple f-strings for formatted outputs.

- String and Sequence Utilities (Q21–Q23)
  - f-strings with embedded values; arithmetic-derived strings; list construction by concatenating literal and index in loops.

- pandas DataFrame Basics (Q24–Q26)
  - `pd.DataFrame.from_dict` to create DataFrames; compute Series statistics (median), assign as column.
  - `.iloc[row_slice, col_slice]` for positional selection.
  - Column arithmetic and inplace drop: `df['COL_3'] = df['COL_3']*df['COL_3']`; `df.drop(columns=['COL_2'], inplace=True)`.

- pandas Series Ops (Q27)
  - Slice with `.iloc[2:8]`; compute mean; find positional index of max via `np.argmax(series.to_numpy())`.

- Descriptive Stats from Lists via DataFrame (Q28)
  - Build DataFrame with COL_1/COL_2; gather median, std, mean into a tuple.

- Market Data with yfinance (Q29–Q30)
  - Download with `yf.download(ticker, start, end, auto_adjust=False, progress=False)`.
  - Normalize index to `DatetimeIndex`; if multi-index columns, flatten to top-level names and reorder to desired OHLCV.
  - Return full DataFrame (Q29) or just its `columns` (Q30).

