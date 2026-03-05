# Core Concepts

## Python Basics

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

## Core Language Features

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
  - Bit shifting: `<<` (left shift), `>>` (right shift); e.g., `1 << 3` evaluates to `8`.

- Core Data Types
  - Numbers (int, float): numeric, non-iterable; `type()` to inspect.
  - List: ordered, mutable, mixed types allowed; indexing, `append`, `pop`.
  - Tuple: ordered, immutable; convert via `tuple([..])`.
  - Dictionary: key/value store; `keys`, `values`, `items`, `update`, building from `zip` then indexing `list(x.items())[0]`.
  - String: quotes, triple-quoted multiline, methods `upper`, `lower`, slicing and reverse `[::-1]`.
  - Set: unique elements, non-indexable.

- Casting Between Types
  - Examples: `float(4)`, `str(1)`; use `type()` to confirm.
  - `isinstance(x, SomeType)` returns True if x is an instance of SomeType or any subclass.
  - `type(x) is SomeType` performs strict type checking — exact type only, not subclasses. Example: `isinstance(True, int)` returns True (bool is a subclass of int); `type(True) is int` returns False.

- Functions
  - Define with `def`, call vs reference; `return` sends a value back to the caller.
  - Example: `some_math(x)` modifies then returns; capture with `our_math_solution = some_math(5)`.

- Scope: Global vs Local
  - Globals exist throughout script; locals inside functions/blocks; return locals to use outside.

- Script Execution and __name__ Guard
  - `if __name__ == "__main__":` runs only when executed as a script; when imported, `__name__` differs.


## Control Flow and Iteration

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

- Applied Patterns
  - Even-number detection and formatted f-strings in loop output.
  - Grading logic using `if/elif/else` and `zip(name_list, grade_payload)` to build dicts.
  - Number Guessing game: validates input range, counts guesses, provides proximity hints, and uses `break`.
  - Nested conditionals with a nested dictionary (day/week attributes) to generate contextual responses.

## Data Libraries

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

## Financial Analysis Applications

- Imports
  - math, pandas, numpy, yfinance, matplotlib, datetime.timedelta.

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

- Visualization and Output
  - Build `investment_total`, `weights`, and `investment_dollar_amounts` from weights.
  - Run `portfolio_value_tracking(...)` to compute `equity_data` and `portfolio_metadata`.
  - Plot with matplotlib: overall Total_Equity and individual security equity; format y-axis as dollars; show legend and print metadata.

## Quick Reference Patterns

- Booleans, Types, and Casting
  - `isinstance(x, bool)`, `bool(x)` truthiness, `type(x)` to inspect runtime type.

- Dicts: Build, Mutate, Access
  - Create dict from two lists with `zip`, index via `list(d.items())[i]`.
  - `pop('TARGET', None)`, iterating keys, `clear()`, `update({...})`.
  - `get('TARGET')` access, membership `if 'TARGET' in d` and equality checks.
  - Nested dict access `d['KEY_1']['INNER_KEY_1']` and tuple returns.
  - Use `enumerate` to build dict values based on index.

- Loops and Comprehensions
  - Range-based loops to build lists; conditional even filtering; nested loops with conditional multiply.
  - List comprehension for elementwise transforms `[x*4 for x in seq]`.

- Boolean Logic and Control Flow
  - Nested if/else with booleans; identity vs equality in checks used explicitly; combining booleans with `or` then arithmetic on truth values.
  - Numeric branching: thresholds and exponentiation; chained if/elif/else precedence; staged arithmetic transforms and comparisons.
  - Simple f-strings for formatted outputs.

- String and Sequence Utilities
  - f-strings with embedded values; arithmetic-derived strings; list construction by concatenating literal and index in loops.

- pandas DataFrame Basics
  - `pd.DataFrame.from_dict` to create DataFrames; compute Series statistics (median), assign as column.
  - `.iloc[row_slice, col_slice]` for positional selection.
  - Column arithmetic and inplace drop: `df['COL_3'] = df['COL_3']*df['COL_3']`; `df.drop(columns=['COL_2'], inplace=True)`.

- pandas Series Ops
  - Slice with `.iloc[2:8]`; compute mean; find positional index of max via `np.argmax(series.to_numpy())`.

- Descriptive Stats from Lists via DataFrame
  - Build DataFrame with COL_1/COL_2; gather median, std, mean into a tuple.

- Market Data with yfinance
  - Download with `yf.download(ticker, start, end, auto_adjust=False, progress=False)`.
  - Normalize index to `DatetimeIndex`; if multi-index columns, flatten to top-level names and reorder to desired OHLCV.
  - Return full DataFrame or just its `columns`.

## Object-Oriented Programming

- Class Basics
  - Define with `class ClassName:` (title case convention); instantiate with `obj = ClassName()`.
  - Python built-in types like `int`, `list`, and `dict` are themselves class objects; `type()` and `isinstance()` confirm this.
  - `__init__(self, ...)` sets up initial instance state; `self` represents the current instance internally.
  - Instance variables: unique per object (e.g., `self.var1 = input1`).
  - Class variables: shared across all instances, defined at class scope (e.g., `class_attribute = 'WE_ALL_HAVE_THIS'`).
  - Methods are functions defined inside a class; called via `obj.method(args)`.

- Pillars of OOP
  - Inheritance: child class inherits attributes and methods from parent; syntax `class Dog(Animal):`; initialize parent via `Animal.__init__(self)` or `super().__init__()`.
  - Polymorphism: child classes define methods with the same name that behave differently (e.g., `Dog.speak()` vs `Cat.speak()`); each class is self-referencing and cannot accidentally invoke the wrong tool.
  - Encapsulation: `self.__attr` (double underscore) is fully private and inaccessible outside the class; `self._attr` (single underscore) is protected by convention but still accessible; regular `self.attr` is public.
  - Abstraction: abstract classes serve as formal blueprints requiring subclasses to implement declared methods; defined via `ABC` in Python's `abc` module.

- Dunder (Magic) Methods
  - Built-in methods that integrate custom classes with the Python ecosystem; only add them as needed.
  - `__repr__(self)`: official representation string for debugging; shown in the REPL.
  - `__str__(self)`: human-readable string used by `print()`.
  - `__eq__(self, other)`: customize `==` comparison; use `isinstance(other, ClassName)` to guard against type mismatches.
  - `__iter__(self)`: make class iterable; return a generator expression over internal values (e.g., `return (i for i in (self.length, self.width))`).
  - `__mul__(self, number)` / `__rmul__(self, other)`: support `*` on both sides; validate type with `isinstance(number, (int, float))`; raise `TypeError` otherwise; can return a new class instance (recursion pattern).

- Reference Implementations
  - `Rectangle(length, width)`: demonstrates all dunder methods above, including recursive `__mul__` returning a new `Rectangle`.
  - `Animal / Dog / Cat`: demonstrate inheritance and polymorphism; `Dog.speak()` and `Cat.speak()` share a name but produce different output.
  - `Example5`: demonstrates all three encapsulation levels in a single class.

- Class Design Examples
  - `Calculator()`: no init inputs; methods `add(a,b)`, `subtract(a,b)`, `multiply(a,b)`, `divide(a,b)`.
  - `Circle(r)`: stores radius; `__str__` prints radius, diameter (`2r`), area (`π r²`), circumference (`2πr`).
  - `Employee(name, last_name, salary, department)`: `__str__` prints full name, salary, and department; `reassign_department(new_dept)` and `update_salary(raise_amount)` mutate instance state.

## Advanced OOP Patterns

- `super()`
  - Built-in shortcut for calling parent class methods without hardcoding the parent class name.
  - `super().__init__(...)` applies parent setup to the current instance; child can then add its own attributes.
  - Preferred over `ParentClass.__init__(self)` for easier future maintenance.

- Decorators
  - Functions that wrap other functions to inject behavior before and/or after execution.
  - Structure: outer function takes `func`; inner `wrapper(*args, **kwargs)` runs pre/post logic and calls `func(*args, **kwargs)`; outer returns `wrapper`.
  - Apply to a function with `@decorator_name` on the line above `def`.

- `*args` and `**kwargs`
  - `*args`: collects unlimited positional arguments into an iterable tuple; loop or aggregate freely.
  - `**kwargs`: collects unlimited keyword arguments into a dict; iterate via `.values()` or `.items()`.
  - Used in decorator wrappers to remain agnostic about the wrapped function's signature.
  - Unpacking operators: `*iterable` unpacks elements individually; `**dict` unpacks key/value pairs (e.g., `"{key1}".format(**d)`).

- Method Types
  - Instance methods: take `self`; can access and modify all instance state; most common type.
  - Class methods: `@classmethod` decorator with `cls` parameter; operate on the class itself; used as factory functions to create preset instances (e.g., `Burger.double_cheese()`).
  - Static methods: `@staticmethod` decorator; no `self` or `cls`; Python blocks access to instance and class data; pure utility logic.

- POS System (Multi-Class Example)
  - `Product(product_id, name, price, quantity)`: individual inventory item.
  - `Inventory`: manages a `products` dict; methods: `add_product`, `remove_product`, `update_quantity`, `check_stock_level`.
  - `Transactions`: manages a `basket` dict and `total_amount`; methods: `add_to_basket`, `remove_from_basket`, `generate_sale_and_receipt` (prints itemized receipt with `dt.datetime.now()`).
  - `SmallBusiness(Inventory, Transactions)`: multiple inheritance combining both parent classes via chained `__init__` calls; demonstrates composition of independent systems.

- Class Design Examples
  - `Vehicle(year, color, make, model)`: base class; `__str__` prints `COLOR YEAR MAKE MODEL`; `check_fuel()` and `refuel()` are stubs (return `None`) — overridden in child.
  - `Automobile(Vehicle)`: extends Vehicle via `super()`; `check_fuel()` reports percentage remaining; `refuel()` fills to 100% and reports what was added; `drive(miles)` consumes 2.86 gallons per 100 miles and reports usage; `honk()` returns `'HONK'`; class methods `r8()` and `roma()` return preset Audi R8 and Ferrari Roma instances.
  - `vehicle_generator_solution(count)`: factory function returning a list of `count` `Automobile` instances.

## Real Estate Investment Modeling

- Python Dataclasses
  - `from dataclasses import dataclass`; `@dataclass` decorator auto-generates `__init__` from class-level field annotations with defaults.
  - `RegularUnit`: `sqft=800`, `dollar_per_sqft=1.5`, `added_margin=0.3`, `vacancy_rate=0.15`, `expense_ratio=0.1`; computed `per_unit_rent` and `per_unit_expense`.
  - `LuxuryUnit`: `sqft=1600`, `dollar_per_sqft=2.5`, `added_margin=0.5`, `vacancy_rate=0.05`, `expense_ratio=0.15`; same computed fields at higher rates.

- `ResidentialProperty` Class
  - Inputs: `property_value`, `regular_units`, `luxury_units`, `loan_years`, `rate`, `down_payment_percent`, `escalation`, `date_of_purchase`.
  - `payment(rate, loan_months, principal)`: standard mortgage formula `(rate/12) * (1 / (1 - (1 + rate/12)^(-n))) * principal`.
  - `loan_model()`: builds a monthly DataFrame with `pd.date_range(..., freq='M')` index; columns: `BEGINNING_BALANCE`, `PAYMENT`, `INTEREST_PAID`, `PRINCIPAL_PAID`, `ENDING_BALANCE`, `EQUITY`; iterates row-by-row; zeroes out balances post-payoff and holds final equity flat.
  - `monthly_operations_statement()`: computes revenue per unit type (applying vacancy rate) and per-unit expenses.
  - `operations_report()`: builds `operations_report_df` with `REVENUE`, `EXPENSE`, `NET_INCOME`, `TOTAL_SQFT`, `TOTAL_UNITS`; applies monthly escalation factor `(1 + escalation/12)` each period; expense structure changes after loan payoff (debt service drops out).
  - All properties modeled to 2070; `__init__` auto-runs all three modeling methods on instantiation.

- `Portfolio` Class
  - Inputs: `year_established`, `capital`; maintains `property_database` dict and `property_counter`.
  - `purchase_property(property_attributes: list)`: iterates list of attribute dicts; allocates 10% of capital as down payment per property; names each `PROPERTY_1`, `PROPERTY_2`, etc.; instantiates `ResidentialProperty` objects.
  - `query_property(key)`: returns a property object by key from `property_database`.
  - `aggregate_property_data()`: sums operations and debt DataFrames across all properties using `pd.concat(..., axis=1).fillna(0).sum(axis=1)` column-by-column.
  - `sell_property(property_key, price_of_sale, closing_cost)`: removes property from portfolio database and reflects the sale in portfolio financials; triggers a revenue event visible in the aggregated operations report.

## Banking System Modeling

- Banking and Accounting Concepts
  - Double-entry bookkeeping identity: Assets = Liabilities + Owner's Equity.
  - Asset structure: `TOTAL_RESERVES` (required + excess) and `LOAN_BALANCE`.
  - Liability structure: `CHECKED_DEPOSITS` and `OWNERS_EQUITY`.
  - Reserve mechanics: `REQUIRED = total_reserves * reserve_rate`; `EXCESS = total * (1 - reserve_rate)`.
  - Deposit flow: reserves increase (asset ↑) and checked deposits increase (liability ↑); loan issuance: excess reserves decrease, loan balance increases.

- `Database` Class (Internal Ledger)
  - Private attributes (`__assets`, `__liabilities`, `__accounts`) enforce full encapsulation.
  - Methods: `create_account`, `check_account`, `update_account`, `update_reserves`, `update_deposits`, `update_loans`, `update_account_loans`, `data_output`.

- `Branch` Class
  - Wraps `Database` via a private `self.__database` instance attribute (composition pattern).
  - `create_account(initial_balance)`: creates account in the ledger, then updates deposits and reserves on the balance sheet.
  - `deposit` / `withdraw`: updates account balance, then adjusts bank liabilities and reserves in lockstep.
  - `consumer_credit_model(account_id, term, urban_rural, loan_principal)`: loads a pickled scikit-learn model via `pickle.load(open(..., 'rb'))`; calls `.predict_proba()` to get probability of default; APR logic: ≤0.25 → 5%, ≤0.50 → 15%, ≤0.75 → 30%, >0.75 → rejected; computes monthly payment via amortization formula and updates account and bank records on approval.
  - `payoff_account_loan(account_id)`: clears loan records on both the account and bank balance sheet.

- `Bank` Class
  - Manages a `branch_database` dict; `open_branch()` allocates 10% of capital per new branch as startup reserves.
  - `balance_sheet_aggregation()`: iterates all branches, calls `data_output()` on each `Database`, and sums assets and liabilities to produce a corporation-wide balance sheet.
  - `__repr__` renders a formatted balance sheet string showing all asset and liability line items.

- `Simulation` Class
  - `Simulation(bank)`: wraps a `Bank` instance as a test harness.
  - `run_simulation(branches, accounts, transactions, loans)`: programmatically opens branches, creates accounts with random balances, executes random deposits/withdrawals, and optionally issues loans; validates the bank's balance sheet aggregation at scale.

