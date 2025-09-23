import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

# Provide a minimal yfinance stub if the package is not installed so we can import H04
import sys, types
try:
	import yfinance as _yf  # noqa: F401
except Exception:
	yf_stub = types.ModuleType("yfinance")
	def _stub_download(*args, **kwargs):
		# Return a tiny OHLCV frame so question_15 can still be validated at a basic level if implemented
		try:
			import pandas as _pd
			dates = _pd.to_datetime(["2023-12-28", "2023-12-29"])  # two rows as expected in breadcrumbs
			df = _pd.DataFrame({
				"Open": [1.0, 2.0],
				"High": [1.0, 2.0],
				"Low": [1.0, 2.0],
				"Close": [1.0, 2.0],
				"Adj Close": [1.0, 2.0],
				"Volume": [100, 200],
			}, index=dates)
			return df
		except Exception:
			# As a last resort, just raise – checker will mark Q15 as incorrect but won't crash
			raise RuntimeError("yfinance not available in this environment")
	yf_stub.download = _stub_download
	sys.modules['yfinance'] = yf_stub

import H04_DATA_TOOLS_HARMER_KAI_U0895215 as H04


# ---------- Helpers ----------
def safe_call(func_name, *args, **kwargs):
	try:
		fn = getattr(H04, func_name)
	except AttributeError as e:
		return e
	try:
		return fn(*args, **kwargs)
	except Exception as e:
		return e


def is_exception(x):
	return isinstance(x, Exception)


def print_result(label, got, expected, ok):
	if is_exception(got):
		print(f"{label} => ERROR: {got}")
	else:
		status = "✔️" if ok else "❌"
		print(f"{label} => {status}")


def arrays_equal_exact(a, b, atol=1e-12):
	try:
		a = np.asarray(a)
		b = np.asarray(b)
		# Require same dtype and shape
		if a.shape != b.shape:
			return False
		if a.dtype != b.dtype:
			return False
		if np.issubdtype(a.dtype, np.floating):
			return np.allclose(a, b, atol=atol, rtol=0)
		return np.array_equal(a, b)
	except Exception:
		return False


def tuples_equal_exact(got, exp, atol=1e-12):
	try:
		if not isinstance(got, tuple) or not isinstance(exp, tuple):
			return False
		if len(got) != len(exp):
			return False
		ok = True
		for g, e in zip(got, exp):
			if isinstance(e, int) and not isinstance(e, bool):
				# Require Python built-in int, not numpy integer
				ok = ok and (type(g) is int) and (g == e)
			elif isinstance(e, (np.integer,)):
				ok = ok and isinstance(g, (np.integer,)) and (g == e)
			elif isinstance(e, float):
				ok = ok and isinstance(g, (float, np.floating)) and np.isclose(g, e, atol=atol, rtol=0)
			elif isinstance(e, (np.ndarray, list, tuple)):
				ok = ok and arrays_equal_exact(g, e, atol=atol)
			elif isinstance(e, pd.DataFrame):
				try:
					assert_frame_equal(g, e, check_dtype=True, atol=atol, rtol=0)
				except Exception:
					ok = False
			elif isinstance(e, pd.Series):
				try:
					assert_series_equal(g, e, check_dtype=True, check_names=True, atol=atol, rtol=0)
				except Exception:
					ok = False
			elif isinstance(e, pd.Index):
				try:
					ok = ok and isinstance(g, type(e)) and (list(g) == list(e))
				except Exception:
					ok = False
			else:
				ok = ok and (g == e)
		return ok
	except Exception:
		return False


# ---------- Tests ----------
results = []

# Q1
exp_q1 = np.array([3, 4, 6])
got_q1 = safe_call('question_1', 3, 4, 6)
ok_q1 = (not is_exception(got_q1)) and isinstance(got_q1, np.ndarray) and arrays_equal_exact(got_q1, exp_q1)
print_result("question_1(3, 4, 6)", got_q1, exp_q1, ok_q1)
results.append(ok_q1)

# Q2
exp_q2 = np.ones((3, 4))
got_q2 = safe_call('question_2', 3, 4)
ok_q2 = (not is_exception(got_q2)) and isinstance(got_q2, np.ndarray) and arrays_equal_exact(got_q2, exp_q2)
print_result("question_2(3, 4)", got_q2, exp_q2, ok_q2)
results.append(ok_q2)

# Q3
arr_a = np.array([1, 2, 3, 4])
arr_b = np.array([1, 2, 3, 4])
exp_q3a = np.array([9, 16, 25, 36])
got_q3a = safe_call('question_3', arr_a, arr_b)
ok_q3a = (not is_exception(got_q3a)) and isinstance(got_q3a, np.ndarray) and arrays_equal_exact(got_q3a, exp_q3a)
print_result("question_3([1,2,3,4],[1,2,3,4])", got_q3a, exp_q3a, ok_q3a)
results.append(ok_q3a)

arr_c = np.array([4, 3, 2, 1])
arr_d = np.array([4, 3, 2, 1])
exp_q3b = np.array([36, 25, 16, 9])
got_q3b = safe_call('question_3', arr_c, arr_d)
ok_q3b = (not is_exception(got_q3b)) and isinstance(got_q3b, np.ndarray) and arrays_equal_exact(got_q3b, exp_q3b)
print_result("question_3([4,3,2,1],[4,3,2,1])", got_q3b, exp_q3b, ok_q3b)
results.append(ok_q3b)

# Q4
arr_q4_a = np.array([4, 3, 2, 1])
exp_q4a = (4, 0)
got_q4a = safe_call('question_4', arr_q4_a)
ok_q4a = (not is_exception(got_q4a)) and tuples_equal_exact(got_q4a, exp_q4a)
print_result("question_4([4,3,2,1])", got_q4a, exp_q4a, ok_q4a)
results.append(ok_q4a)

arr_q4_b = np.array([3, 6, 9, 12])
exp_q4b = (12, 3)
got_q4b = safe_call('question_4', arr_q4_b)
ok_q4b = (not is_exception(got_q4b)) and tuples_equal_exact(got_q4b, exp_q4b)
print_result("question_4([3,6,9,12])", got_q4b, exp_q4b, ok_q4b)
results.append(ok_q4b)

# Q5
arr_q5 = np.array([4, 3, 2, 2])
exp_q5 = (np.log(arr_q5) ** 2)
got_q5 = safe_call('question_5', arr_q5)
ok_q5 = (not is_exception(got_q5)) and isinstance(got_q5, np.ndarray) and arrays_equal_exact(got_q5, exp_q5)
print_result("question_5([4,3,2,2])", got_q5, exp_q5, ok_q5)
results.append(ok_q5)

# Q6
arr_q6 = np.array([4, 3, 2, 1, 2, 3, 4])
exp_q6 = (float(arr_q6.mean()), float(np.median(arr_q6)), float(arr_q6.std()))
got_q6 = safe_call('question_6', arr_q6)
ok_q6 = (not is_exception(got_q6)) and tuples_equal_exact(got_q6, exp_q6)
print_result("question_6([4,3,2,1,2,3,4])", got_q6, exp_q6, ok_q6)
results.append(ok_q6)

# Q7
arr_q7 = np.array([5, 5, 5, 53, 32, 2, 22, 2])
exp_q7 = (np.array([5, 5]), 5, np.array([22, 2]))
got_q7 = safe_call('question_7', arr_q7)
ok_q7 = (not is_exception(got_q7)) and tuples_equal_exact(got_q7, exp_q7)
print_result("question_7([5,5,5,53,32,2,22,2])", got_q7, exp_q7, ok_q7)
results.append(ok_q7)

# Q8
L1, L2, L3 = [4, 3, 2, 1], [1, 2, 3, 4], [4, 3, 2, 1]
df_q8_exp = pd.DataFrame({"COL_1": L1, "COL_2": L2, "COL_3": L3})
got_q8 = safe_call('question_8', L1, L2, L3)
ok_q8 = False
if not is_exception(got_q8) and isinstance(got_q8, pd.DataFrame):
	try:
		assert_frame_equal(got_q8, df_q8_exp, check_dtype=True)
		ok_q8 = True
	except Exception:
		ok_q8 = False
print_result("question_8(lists)", got_q8, df_q8_exp, ok_q8)
results.append(ok_q8)

# Q9
df_q9 = pd.DataFrame({"COL_1": L1, "COL_2": L2, "COL_3": L3})
out1_exp = df_q9.describe()
# Expect Python floats to match breadcrumb text formatting exactly
out2_exp = float(df_q9["COL_2"].mean())
out3_exp = float(df_q9["COL_1"].std())  # sample std (ddof=1)
got_q9 = safe_call('question_9', L1, L2, L3)
ok_q9 = False
if not is_exception(got_q9) and isinstance(got_q9, tuple) and len(got_q9) == 3:
	g1, g2, g3 = got_q9
	try:
		if isinstance(g1, pd.DataFrame):
			assert_frame_equal(g1, out1_exp, check_dtype=True, atol=1e-12, rtol=0)
		else:
			raise AssertionError("out1 should be a DataFrame")
		ok_num = (type(g2) is float) and np.isclose(g2, out2_exp, atol=1e-12, rtol=0)
		ok_std = (type(g3) is float) and np.isclose(g3, out3_exp, atol=1e-12, rtol=0)
		ok_q9 = ok_num and ok_std
	except Exception:
		ok_q9 = False
print_result("question_9(lists)", got_q9, ("df.describe()", out2_exp, out3_exp), ok_q9)
results.append(ok_q9)

# Q10
L4 = [4, 3, 2, 1]
df_q10 = pd.DataFrame({"COL_1": L1, "COL_2": L2, "COL_3": L3, "COL_4": L4})
shape_exp = df_q10.shape
cols_exp = df_q10.columns
index_exp = df_q10.index
dtypes_exp = df_q10.dtypes
got_q10 = safe_call('question_10', L1, L2, L3, L4)
ok_q10 = False
if not is_exception(got_q10) and isinstance(got_q10, tuple) and len(got_q10) == 4:
	g_shape, g_cols, g_index, g_dtypes = got_q10
	try:
		ok_shape = (g_shape == shape_exp)
		ok_cols = isinstance(g_cols, type(cols_exp)) and list(g_cols) == list(cols_exp)
		ok_index = isinstance(g_index, type(index_exp)) and list(g_index) == list(index_exp)
		ok_dtypes = isinstance(g_dtypes, pd.Series) and g_dtypes.equals(dtypes_exp)
		ok_q10 = ok_shape and ok_cols and ok_index and ok_dtypes
	except Exception:
		ok_q10 = False
print_result("question_10(lists)", got_q10, (shape_exp, cols_exp, index_exp, dtypes_exp), ok_q10)
results.append(ok_q10)

# Build test_df for Q11-Q14 as in breadcrumbs
test_df = pd.DataFrame({
	"COL_1": [1, 2, np.nan, 4, 5, 5, 5],
	"COL_2": [1, 2, 4, 4, np.nan, 5, 5],
	"COL_3": [1, 2, 4, 4, 5, 5, np.nan],
	"COL_4": [1, 2, 4, 4, 5, np.nan, 5],
}, index=[0, 1, 2, 3, 4, 5, 6])

# Q11
exp_q11 = test_df.groupby("COL_1").mean(numeric_only=True)
got_q11 = safe_call('question_11', test_df.copy())
ok_q11 = False
if not is_exception(got_q11) and isinstance(got_q11, pd.DataFrame):
	try:
		assert_frame_equal(got_q11, exp_q11, check_dtype=True)
		ok_q11 = True
	except Exception:
		ok_q11 = False
print_result("question_11(groupby mean)", got_q11, exp_q11, ok_q11)
results.append(ok_q11)

# Q12
# Expect Python float for value1 to match breadcrumb text formatting
value1_exp = float(test_df.iloc[0, 1])
col1_exp = test_df["COL_1"]
row1_exp = test_df.loc[0]
multi_exp = test_df.loc[3, ["COL_1", "COL_2"]]
got_q12 = safe_call('question_12', test_df.copy())
ok_q12 = False
if not is_exception(got_q12) and isinstance(got_q12, tuple) and len(got_q12) == 4:
	g_val, g_col1, g_row1, g_multi = got_q12
	try:
		ok_val = (type(g_val) is float) and (g_val == value1_exp)
		assert_series_equal(g_col1, col1_exp, check_dtype=True, check_names=True)
		assert_series_equal(g_row1, row1_exp, check_dtype=True, check_names=True)
		assert_series_equal(g_multi, multi_exp, check_dtype=True, check_names=True)
		ok_q12 = ok_val
	except Exception:
		ok_q12 = False
print_result("question_12(indexing)", got_q12, (value1_exp, col1_exp, row1_exp, multi_exp), ok_q12)
results.append(ok_q12)

# Q13
exp_q13 = test_df.shift(4)
got_q13 = safe_call('question_13', test_df.copy())
ok_q13 = False
if not is_exception(got_q13) and isinstance(got_q13, pd.DataFrame):
	try:
		assert_frame_equal(got_q13, exp_q13, check_dtype=True)
		ok_q13 = True
	except Exception:
		ok_q13 = False
print_result("question_13(shift by 4)", got_q13, exp_q13, ok_q13)
results.append(ok_q13)

# Q14
exp_q14 = test_df.fillna("TEST")
got_q14 = safe_call('question_14', test_df.copy(), "TEST")
ok_q14 = False
if not is_exception(got_q14) and isinstance(got_q14, pd.DataFrame):
	try:
		assert_frame_equal(got_q14, exp_q14, check_dtype=True)
		ok_q14 = True
	except Exception:
		ok_q14 = False
print_result("question_14(fillna with string)", got_q14, exp_q14, ok_q14)
results.append(ok_q14)

# Q15 - Network dependent: validate shape & columns lightly
got_q15 = safe_call('question_15', 'AAPL', '2020-01-01', '2024-01-01')
ok_q15 = False
required_cols = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
if not is_exception(got_q15) and isinstance(got_q15, pd.DataFrame):
	try:
		has_cols = required_cols.issubset(set(got_q15.columns))
		has_two_rows = len(got_q15.index) == 2
		idx_ok = isinstance(got_q15.index, pd.DatetimeIndex)
		ok_q15 = has_cols and has_two_rows and idx_ok
	except Exception:
		ok_q15 = False
print_result("question_15(yfinance last two rows)", got_q15, "DataFrame with 2 rows & OHLCV cols", ok_q15)
results.append(ok_q15)


print(f"\nSummary: {results.count(True)} correct, {results.count(False)} incorrect.")

