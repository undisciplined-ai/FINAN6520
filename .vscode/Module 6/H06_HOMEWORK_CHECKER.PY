import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

# Provide a minimal yfinance stub if the package is not installed so we can import H06
import sys, types
try:
    import yfinance as _yf  # noqa: F401
except Exception:
    yf_stub = types.ModuleType("yfinance")
    def _stub_download(*args, **kwargs):
        try:
            import pandas as _pd
            dates = _pd.to_datetime(["2021-12-30", "2021-12-31"])  # two rows
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
            raise RuntimeError("yfinance not available in this environment")
    yf_stub.download = _stub_download
    sys.modules['yfinance'] = yf_stub

import H06_CORE_PREP_HARMER_KAI_U0895215 as H06


# ---------- Helpers ----------
def safe_call(func_name, *args, **kwargs):
    try:
        fn = getattr(H06, func_name)
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
                ok = ok and (type(g) is int) and (g == e)
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
                    ok = ok and isinstance(g, type(e)) and (list(g) == list(e)) and (g.name == e.name)
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
exp_q1_a = False
got_q1_a = safe_call('question_1', 4)
ok_q1_a = (not is_exception(got_q1_a)) and (got_q1_a is exp_q1_a)
print_result("question_1(4)", got_q1_a, exp_q1_a, ok_q1_a)
results.append(ok_q1_a)

exp_q1_b = True
got_q1_b = safe_call('question_1', True)
ok_q1_b = (not is_exception(got_q1_b)) and (got_q1_b is exp_q1_b)
print_result("question_1(True)", got_q1_b, exp_q1_b, ok_q1_b)
results.append(ok_q1_b)

# Q2
exp_q2_a = True
got_q2_a = safe_call('question_2', 4)
ok_q2_a = (not is_exception(got_q2_a)) and (got_q2_a is exp_q2_a)
print_result("question_2(4)", got_q2_a, exp_q2_a, ok_q2_a)
results.append(ok_q2_a)

exp_q2_b = False
got_q2_b = safe_call('question_2', 0)
ok_q2_b = (not is_exception(got_q2_b)) and (got_q2_b is exp_q2_b)
print_result("question_2(0)", got_q2_b, exp_q2_b, ok_q2_b)
results.append(ok_q2_b)

# Q3
exp_q3_a = bool
got_q3_a = safe_call('question_3', False)
ok_q3_a = (not is_exception(got_q3_a)) and (got_q3_a is exp_q3_a)
print_result("question_3(False)", got_q3_a, exp_q3_a, ok_q3_a)
results.append(ok_q3_a)

exp_q3_b = int
got_q3_b = safe_call('question_3', 5635)
ok_q3_b = (not is_exception(got_q3_b)) and (got_q3_b is exp_q3_b)
print_result("question_3(5635)", got_q3_b, exp_q3_b, ok_q3_b)
results.append(ok_q3_b)

# Q4
exp_q4_a = (5, 5)
got_q4_a = safe_call('question_4', [1,2,3,4,5,6],[1,2,3,4,5,6])
ok_q4_a = (not is_exception(got_q4_a)) and tuples_equal_exact(got_q4_a, exp_q4_a)
print_result("question_4(list,list) A", got_q4_a, exp_q4_a, ok_q4_a)
results.append(ok_q4_a)

exp_q4_b = (9, 10)
got_q4_b = safe_call('question_4', [1,3,5,7,9],[2,4,6,8,10])
ok_q4_b = (not is_exception(got_q4_b)) and tuples_equal_exact(got_q4_b, exp_q4_b)
print_result("question_4(list,list) B", got_q4_b, exp_q4_b, ok_q4_b)
results.append(ok_q4_b)

# Q5
exp_q5_a = ['NOT_TARGET']
got_q5_a = safe_call('question_5', {'TARGET':4,'NOT_TARGET':5})
ok_q5_a = (not is_exception(got_q5_a)) and (got_q5_a == exp_q5_a)
print_result("question_5(dict) A", got_q5_a, exp_q5_a, ok_q5_a)
results.append(ok_q5_a)

exp_q5_b = ['WALMART', 'SMITHS']
got_q5_b = safe_call('question_5', {'TARGET':15,'WALMART':30, 'SMITHS':45})
ok_q5_b = (not is_exception(got_q5_b)) and (got_q5_b == exp_q5_b)
print_result("question_5(dict) B", got_q5_b, exp_q5_b, ok_q5_b)
results.append(ok_q5_b)

# Q6
exp_q6 = {'key1': 4, 'key2': 7}
got_q6_a = safe_call('question_6', {'TARGET':4,'NOT_TARGET':5})
ok_q6_a = (not is_exception(got_q6_a)) and (got_q6_a == exp_q6)
print_result("question_6(dict) A", got_q6_a, exp_q6, ok_q6_a)
results.append(ok_q6_a)

got_q6_b = safe_call('question_6', {'TARGET':15,'WALMART':30, "SMITHS": 45})
ok_q6_b = (not is_exception(got_q6_b)) and (got_q6_b == exp_q6)
print_result("question_6(dict) B", got_q6_b, exp_q6, ok_q6_b)
results.append(ok_q6_b)

# Q7
exp_q7_a = 56
got_q7_a = safe_call('question_7', {'TARGET':4,'KEY1':5})
ok_q7_a = (not is_exception(got_q7_a)) and (got_q7_a == exp_q7_a)
print_result("question_7(dict) A", got_q7_a, exp_q7_a, ok_q7_a)
results.append(ok_q7_a)

exp_q7_b = 210
got_q7_b = safe_call('question_7', {'TARGET':15,'WALMART':30, "SMITH'S": 45})
ok_q7_b = (not is_exception(got_q7_b)) and (got_q7_b == exp_q7_b)
print_result("question_7(dict) B", got_q7_b, exp_q7_b, ok_q7_b)
results.append(ok_q7_b)

# Q8
exp_q8_a = True
got_q8_a = safe_call('question_8', {'TARGET':4,'NOT_TARGET':5})
ok_q8_a = (not is_exception(got_q8_a)) and (got_q8_a is exp_q8_a)
print_result("question_8(dict) A", got_q8_a, exp_q8_a, ok_q8_a)
results.append(ok_q8_a)

exp_q8_b = False
got_q8_b = safe_call('question_8', {'TARGET':15,'WALMART':30, "SMITH'S": 45})
ok_q8_b = (not is_exception(got_q8_b)) and (got_q8_b is exp_q8_b)
print_result("question_8(dict) B", got_q8_b, exp_q8_b, ok_q8_b)
results.append(ok_q8_b)

# Q9
exp_q9_a = (4,5)
got_q9_a = safe_call('question_9', {'KEY_1':{'INNER_KEY_1':4, 'INNER_KEY_3':5}, 'KEY_2':{'INNER_KEY_1':4, 'INNER_KEY_3':5}})
ok_q9_a = (not is_exception(got_q9_a)) and tuples_equal_exact(got_q9_a, exp_q9_a)
print_result("question_9(nested) A", got_q9_a, exp_q9_a, ok_q9_a)
results.append(ok_q9_a)

exp_q9_b = (30,120)
got_q9_b = safe_call('question_9', {'KEY_1':{'INNER_KEY_1':30, 'INNER_KEY_3':60}, 'KEY_2':{'INNER_KEY_1':90, 'INNER_KEY_3':120}})
ok_q9_b = (not is_exception(got_q9_b)) and tuples_equal_exact(got_q9_b, exp_q9_b)
print_result("question_9(nested) B", got_q9_b, exp_q9_b, ok_q9_b)
results.append(ok_q9_b)

# Q10
exp_q10_a = {'KEY_1': 0, 'KEY_2': 4, 'KEY_3': 8, 'KEY_4': 12}
got_q10_a = safe_call('question_10', ['KEY_1','KEY_2','KEY_3','KEY_4'])
ok_q10_a = (not is_exception(got_q10_a)) and (got_q10_a == exp_q10_a)
print_result("question_10(list) A", got_q10_a, exp_q10_a, ok_q10_a)
results.append(ok_q10_a)

exp_q10_b = {'AAPL': 0, 'NVDA': 4, 'MMM': 8, 'NKE': 12}
got_q10_b = safe_call('question_10', ['AAPL','NVDA','MMM','NKE'])
ok_q10_b = (not is_exception(got_q10_b)) and (got_q10_b == exp_q10_b)
print_result("question_10(list) B", got_q10_b, exp_q10_b, ok_q10_b)
results.append(ok_q10_b)

# Q11
exp_q11_a = [0, 4, 8, 12, 16, 20]
got_q11_a = safe_call('question_11', 6)
ok_q11_a = (not is_exception(got_q11_a)) and (got_q11_a == exp_q11_a)
print_result("question_11(6)", got_q11_a, exp_q11_a, ok_q11_a)
results.append(ok_q11_a)

exp_q11_b = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92]
got_q11_b = safe_call('question_11', 24)
ok_q11_b = (not is_exception(got_q11_b)) and (got_q11_b == exp_q11_b)
print_result("question_11(24)", got_q11_b, exp_q11_b, ok_q11_b)
results.append(ok_q11_b)

# Q12
exp_q12_a = [2, 4]
got_q12_a = safe_call('question_12', [1,2,3,4])
ok_q12_a = (not is_exception(got_q12_a)) and (got_q12_a == exp_q12_a)
print_result("question_12(list) A", got_q12_a, exp_q12_a, ok_q12_a)
results.append(ok_q12_a)

exp_q12_b = [2, 4, 6]
got_q12_b = safe_call('question_12', [2,4,5,6,7,9])
ok_q12_b = (not is_exception(got_q12_b)) and (got_q12_b == exp_q12_b)
print_result("question_12(list) B", got_q12_b, exp_q12_b, ok_q12_b)
results.append(ok_q12_b)

# Q13
exp_q13_a = 240
got_q13_a = safe_call('question_13', {'TARGET':4,'KEY1':5})
ok_q13_a = (not is_exception(got_q13_a)) and (got_q13_a == exp_q13_a)
print_result("question_13(dict) A", got_q13_a, exp_q13_a, ok_q13_a)
results.append(ok_q13_a)

exp_q13_b = 7200
got_q13_b = safe_call('question_13', {'TARGET':2,'WALMART':4, "SMITH'S": 6})
ok_q13_b = (not is_exception(got_q13_b)) and (got_q13_b == exp_q13_b)
print_result("question_13(dict) B", got_q13_b, exp_q13_b, ok_q13_b)
results.append(ok_q13_b)

# Q14
exp_q14_a = [4, 8, 12, 16]
got_q14_a = safe_call('question_14', [1,2,3,4])
ok_q14_a = (not is_exception(got_q14_a)) and (got_q14_a == exp_q14_a)
print_result("question_14(list) A", got_q14_a, exp_q14_a, ok_q14_a)
results.append(ok_q14_a)

exp_q14_b = [20, 40, 60, 80]
got_q14_b = safe_call('question_14', [5,10,15,20])
ok_q14_b = (not is_exception(got_q14_b)) and (got_q14_b == exp_q14_b)
print_result("question_14(list) B", got_q14_b, exp_q14_b, ok_q14_b)
results.append(ok_q14_b)

# Q15
exp_q15_a = False
got_q15_a = safe_call('question_15', True, False, True)
ok_q15_a = (not is_exception(got_q15_a)) and (got_q15_a is exp_q15_a)
print_result("question_15(True,False,True)", got_q15_a, exp_q15_a, ok_q15_a)
results.append(ok_q15_a)

exp_q15_b = True
got_q15_b = safe_call('question_15', True, False, False)
ok_q15_b = (not is_exception(got_q15_b)) and (got_q15_b is exp_q15_b)
print_result("question_15(True,False,False)", got_q15_b, exp_q15_b, ok_q15_b)
results.append(ok_q15_b)

# Q16
exp_q16_a = True
got_q16_a = safe_call('question_16', True, False)
ok_q16_a = (not is_exception(got_q16_a)) and (got_q16_a is exp_q16_a)
print_result("question_16(True,False)", got_q16_a, exp_q16_a, ok_q16_a)
results.append(ok_q16_a)

exp_q16_b = False
got_q16_b = safe_call('question_16', False, False)
ok_q16_b = (not is_exception(got_q16_b)) and (got_q16_b is exp_q16_b)
print_result("question_16(False,False)", got_q16_b, exp_q16_b, ok_q16_b)
results.append(ok_q16_b)

# Q17
exp_q17_a = 40 ** 40
got_q17_a = safe_call('question_17', 40)
ok_q17_a = (not is_exception(got_q17_a)) and (got_q17_a == exp_q17_a)
print_result("question_17(40)", got_q17_a, exp_q17_a, ok_q17_a)
results.append(ok_q17_a)

exp_q17_b = 24 ** 24
got_q17_b = safe_call('question_17', 24)
ok_q17_b = (not is_exception(got_q17_b)) and (got_q17_b == exp_q17_b)
print_result("question_17(24)", got_q17_b, exp_q17_b, ok_q17_b)
results.append(ok_q17_b)

# Q18
exp_q18_a = False
got_q18_a = safe_call('question_18', 40)
ok_q18_a = (not is_exception(got_q18_a)) and (got_q18_a is exp_q18_a)
print_result("question_18(40)", got_q18_a, exp_q18_a, ok_q18_a)
results.append(ok_q18_a)

exp_q18_b = True
got_q18_b = safe_call('question_18', 18)
ok_q18_b = (not is_exception(got_q18_b)) and (got_q18_b is exp_q18_b)
print_result("question_18(18)", got_q18_b, exp_q18_b, ok_q18_b)
results.append(ok_q18_b)

# Q19
exp_q19_a = False
got_q19_a = safe_call('question_19', 40, 50)
ok_q19_a = (not is_exception(got_q19_a)) and (got_q19_a is exp_q19_a)
print_result("question_19(40,50)", got_q19_a, exp_q19_a, ok_q19_a)
results.append(ok_q19_a)

exp_q19_b = True
got_q19_b = safe_call('question_19', 1, 2)
ok_q19_b = (not is_exception(got_q19_b)) and (got_q19_b is exp_q19_b)
print_result("question_19(1,2)", got_q19_b, exp_q19_b, ok_q19_b)
results.append(ok_q19_b)

# Q20
exp_q20_a = 0
got_q20_a = safe_call('question_20', 40)
ok_q20_a = (not is_exception(got_q20_a)) and (got_q20_a == exp_q20_a)
print_result("question_20(40)", got_q20_a, exp_q20_a, ok_q20_a)
results.append(ok_q20_a)

exp_q20_b = 207
got_q20_b = safe_call('question_20', 7)
ok_q20_b = (not is_exception(got_q20_b)) and (got_q20_b == exp_q20_b)
print_result("question_20(7)", got_q20_b, exp_q20_b, ok_q20_b)
results.append(ok_q20_b)

# Q21
exp_q21_a = "Input one is equal to 40"
got_q21_a = safe_call('question_21', 40)
ok_q21_a = (not is_exception(got_q21_a)) and (got_q21_a == exp_q21_a)
print_result("question_21(40)", got_q21_a, exp_q21_a, ok_q21_a)
results.append(ok_q21_a)

exp_q21_b = "Input one is equal to 64"
got_q21_b = safe_call('question_21', 64)
ok_q21_b = (not is_exception(got_q21_b)) and (got_q21_b == exp_q21_b)
print_result("question_21(64)", got_q21_b, exp_q21_b, ok_q21_b)
results.append(ok_q21_b)

# Q22
exp_q22_a = "The final value is 100.0"
got_q22_a = safe_call('question_22', 40, 50)
ok_q22_a = (not is_exception(got_q22_a)) and (got_q22_a == exp_q22_a)
print_result("question_22(40,50)", got_q22_a, exp_q22_a, ok_q22_a)
results.append(ok_q22_a)

exp_q22_b = "The final value is 80.0"
got_q22_b = safe_call('question_22', 20, 80)
ok_q22_b = (not is_exception(got_q22_b)) and (got_q22_b == exp_q22_b)
print_result("question_22(20,80)", got_q22_b, exp_q22_b, ok_q22_b)
results.append(ok_q22_b)

# Q23
exp_q23_a = ['KEY0', 'KEY1', 'KEY2', 'KEY3', 'KEY4', 'KEY5', 'KEY6', 'KEY7', 'KEY8', 'KEY9']
got_q23_a = safe_call('question_23', 10)
ok_q23_a = (not is_exception(got_q23_a)) and (got_q23_a == exp_q23_a)
print_result("question_23(10)", got_q23_a, exp_q23_a, ok_q23_a)
results.append(ok_q23_a)

exp_q23_b = ['KEY0', 'KEY1', 'KEY2', 'KEY3', 'KEY4', 'KEY5']
got_q23_b = safe_call('question_23', 6)
ok_q23_b = (not is_exception(got_q23_b)) and (got_q23_b == exp_q23_b)
print_result("question_23(6)", got_q23_b, exp_q23_b, ok_q23_b)
results.append(ok_q23_b)

# Q24
inp_q24_a = {'COL_1':[4,2],'COL_2':[5,6]}
exp_q24_a = pd.DataFrame.from_dict(inp_q24_a)
exp_q24_a['MEDIAN'] = exp_q24_a['COL_2'].median()
got_q24_a = safe_call('question_24', inp_q24_a)
ok_q24_a = False
if not is_exception(got_q24_a) and isinstance(got_q24_a, pd.DataFrame):
    try:
        assert_frame_equal(got_q24_a, exp_q24_a, check_dtype=True)
        ok_q24_a = True
    except Exception:
        ok_q24_a = False
print_result("question_24(dict) A", got_q24_a, exp_q24_a, ok_q24_a)
results.append(ok_q24_a)

inp_q24_b = {'COL_1':[4,2],'COL_2':[5,3],'COL_3':[6,4],'COL_4':[7,5]}
exp_q24_b = pd.DataFrame.from_dict(inp_q24_b)
exp_q24_b['MEDIAN'] = exp_q24_b['COL_2'].median()
got_q24_b = safe_call('question_24', inp_q24_b)
ok_q24_b = False
if not is_exception(got_q24_b) and isinstance(got_q24_b, pd.DataFrame):
    try:
        assert_frame_equal(got_q24_b, exp_q24_b, check_dtype=True)
        ok_q24_b = True
    except Exception:
        ok_q24_b = False
print_result("question_24(dict) B", got_q24_b, exp_q24_b, ok_q24_b)
results.append(ok_q24_b)

# Q25
inp_q25_a = {
    'COL_1':list(range(1,11)),
    'COL_2':list(range(1,11)),
    'COL_3':list(range(1,11)),
    'COL_4':list(range(1,11)),
    'COL_5':list(range(1,11)),
}
df25a = pd.DataFrame.from_dict(inp_q25_a)
exp_q25_a = df25a.iloc[1:5, 3:5]
got_q25_a = safe_call('question_25', inp_q25_a)
ok_q25_a = False
if not is_exception(got_q25_a) and isinstance(got_q25_a, pd.DataFrame):
    try:
        assert_frame_equal(got_q25_a, exp_q25_a, check_dtype=True)
        ok_q25_a = True
    except Exception:
        ok_q25_a = False
print_result("question_25(dict) A", got_q25_a, exp_q25_a, ok_q25_a)
results.append(ok_q25_a)

inp_q25_b = {
    'COL_1':[1,3,5,7,9],
    'COL_2':[2,4,6,8,10],
    'COL_3':[1,3,5,7,9],
    'COL_4':[2,4,6,8,10],
    'COL_5':[1,3,5,7,9],
}
df25b = pd.DataFrame.from_dict(inp_q25_b)
exp_q25_b = df25b.iloc[1:5, 3:5]
got_q25_b = safe_call('question_25', inp_q25_b)
ok_q25_b = False
if not is_exception(got_q25_b) and isinstance(got_q25_b, pd.DataFrame):
    try:
        assert_frame_equal(got_q25_b, exp_q25_b, check_dtype=True)
        ok_q25_b = True
    except Exception:
        ok_q25_b = False
print_result("question_25(dict) B", got_q25_b, exp_q25_b, ok_q25_b)
results.append(ok_q25_b)

# Q26
inp_q26_a = {
    'COL_1':[1,2,3,4],
    'COL_3':[1,2,3,4],
    'COL_2':[1,2,3,4],
    'COL_4':[1,2,3,4],
    'COL_5':[1,2,3,4]
}
df26a = pd.DataFrame.from_dict(inp_q26_a)
df26a['COL_3'] = df26a['COL_3'] * df26a['COL_3']
df26a.drop(columns=['COL_2'], inplace=True)
exp_q26_a = df26a
got_q26_a = safe_call('question_26', inp_q26_a)
ok_q26_a = False
if not is_exception(got_q26_a) and isinstance(got_q26_a, pd.DataFrame):
    try:
        assert_frame_equal(got_q26_a, exp_q26_a, check_dtype=True)
        ok_q26_a = True
    except Exception:
        ok_q26_a = False
print_result("question_26(dict) A", got_q26_a, exp_q26_a, ok_q26_a)
results.append(ok_q26_a)

inp_q26_b = {
    'COL_1':[1,2,3,4],
    'COL_3':[5,6,7,8],
    'COL_2':[9,10,11,12],
    'COL_4':[13,14,15,16],
    'COL_5':[17,18,19,20]
}
df26b = pd.DataFrame.from_dict(inp_q26_b)
df26b['COL_3'] = df26b['COL_3'] * df26b['COL_3']
df26b.drop(columns=['COL_2'], inplace=True)
exp_q26_b = df26b
got_q26_b = safe_call('question_26', inp_q26_b)
ok_q26_b = False
if not is_exception(got_q26_b) and isinstance(got_q26_b, pd.DataFrame):
    try:
        assert_frame_equal(got_q26_b, exp_q26_b, check_dtype=True)
        ok_q26_b = True
    except Exception:
        ok_q26_b = False
print_result("question_26(dict) B", got_q26_b, exp_q26_b, ok_q26_b)
results.append(ok_q26_b)

# Q27
exp_q27_a = (5.5, 5)
got_q27_a = safe_call('question_27', pd.Series([1,2,3,4,5,6,7,8,9,10]))
ok_q27_a = (not is_exception(got_q27_a)) and tuples_equal_exact(got_q27_a, exp_q27_a)
print_result("question_27(series) A", got_q27_a, exp_q27_a, ok_q27_a)
results.append(ok_q27_a)

exp_q27_b = (8.0, 2)
got_q27_b = safe_call('question_27', pd.Series([2,4,6,8,10]))
ok_q27_b = (not is_exception(got_q27_b)) and tuples_equal_exact(got_q27_b, exp_q27_b)
print_result("question_27(series) B", got_q27_b, exp_q27_b, ok_q27_b)
results.append(ok_q27_b)

# Q28
exp_q28_a = (4.0, 1.7994708216848745, 3.7142857142857144)
got_q28_a = safe_call('question_28', [1,2,3,4,5,5,6], [1,2,3,4,5,5,6])
ok_q28_a = (not is_exception(got_q28_a)) and tuples_equal_exact(got_q28_a, exp_q28_a)
print_result("question_28(lists) A", got_q28_a, exp_q28_a, ok_q28_a)
results.append(ok_q28_a)

exp_q28_b = (5.0, 3.1622776601683795, 5.0)
got_q28_b = safe_call('question_28', [1,3,5,7,9], [2,4,6,8,10])
ok_q28_b = (not is_exception(got_q28_b)) and tuples_equal_exact(got_q28_b, exp_q28_b)
print_result("question_28(lists) B", got_q28_b, exp_q28_b, ok_q28_b)
results.append(ok_q28_b)

# Q29 - Network dependent: validate structure & columns
got_q29_a = safe_call('question_29', 'TSLA', '2010-12-31', '2022-01-01')
ok_q29_a = False
required_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
if not is_exception(got_q29_a) and isinstance(got_q29_a, pd.DataFrame):
    try:
        cols_ok = list(got_q29_a.columns) == required_cols
        idx_ok = isinstance(got_q29_a.index, pd.DatetimeIndex)
        non_empty = len(got_q29_a) > 0
        ok_q29_a = cols_ok and idx_ok and non_empty
    except Exception:
        ok_q29_a = False
print_result("question_29(TSLA)", got_q29_a, "DataFrame with OHLCV cols and DatetimeIndex", ok_q29_a)
results.append(ok_q29_a)

got_q29_b = safe_call('question_29', 'AAPL', '2011-12-31', '2023-01-01')
ok_q29_b = False
if not is_exception(got_q29_b) and isinstance(got_q29_b, pd.DataFrame):
    try:
        cols_ok = list(got_q29_b.columns) == required_cols
        idx_ok = isinstance(got_q29_b.index, pd.DatetimeIndex)
        non_empty = len(got_q29_b) > 0
        ok_q29_b = cols_ok and idx_ok and non_empty
    except Exception:
        ok_q29_b = False
print_result("question_29(AAPL)", got_q29_b, "DataFrame with OHLCV cols and DatetimeIndex", ok_q29_b)
results.append(ok_q29_b)

# Q30 - Validate columns index content and type
got_q30_a = safe_call('question_30', 'TSLA', '2010-12-31', '2022-01-01')
ok_q30_a = False
if not is_exception(got_q30_a) and isinstance(got_q30_a, pd.Index):
    try:
        ok_q30_a = list(got_q30_a) == required_cols and (got_q30_a.name is None)
    except Exception:
        ok_q30_a = False
print_result("question_30(TSLA)", got_q30_a, pd.Index(required_cols), ok_q30_a)
results.append(ok_q30_a)

got_q30_b = safe_call('question_30', 'AAPL', '2011-12-31', '2023-01-01')
ok_q30_b = False
if not is_exception(got_q30_b) and isinstance(got_q30_b, pd.Index):
    try:
        ok_q30_b = list(got_q30_b) == required_cols and (got_q30_b.name is None)
    except Exception:
        ok_q30_b = False
print_result("question_30(AAPL)", got_q30_b, pd.Index(required_cols), ok_q30_b)
results.append(ok_q30_b)


print(f"\nSummary: {results.count(True)} correct, {results.count(False)} incorrect.")
