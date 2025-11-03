import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np

import HARMER_KAI_U0895215_E01 as E01


def safe_call(fn, *args, **kwargs):
    try:
        return True, fn(*args, **kwargs)
    except Exception as e:
        return False, e


def check_equal(expected, actual):
    return expected == actual


def check_list(expected, actual):
    return isinstance(actual, list) and expected == actual


def check_tuple(expected, actual):
    return isinstance(actual, tuple) and expected == actual


def check_dict(expected, actual):
    return isinstance(actual, dict) and expected == actual


def check_series_tuple(expected, actual):
    return (
        isinstance(actual, tuple)
        and len(actual) == 2
        and actual[0] == expected[0]
        and actual[1] == expected[1]
    )


def check_df_exact(expected: pd.DataFrame, actual: pd.DataFrame):
    if not isinstance(actual, pd.DataFrame):
        return False
    if expected.shape != actual.shape:
        return False
    if not expected.index.equals(actual.index):
        return False
    if not expected.columns.equals(actual.columns):
        return False
    if not (expected.dtypes == actual.dtypes).all():
        return False
    return np.array_equal(expected.to_numpy(), actual.to_numpy())


def check_df_struct_q17(actual: pd.DataFrame, ticker: str):
    if not isinstance(actual, pd.DataFrame):
        return False
    if actual.shape[1] != 1:
        return False
    if not isinstance(actual.index, pd.DatetimeIndex):
        return False
    if actual.columns.tolist() != [ticker]:
        return False
    if len(actual) != 200:
        return False
    return True


def main():
    passed = 0
    total = 0

    breadcrumb_list1 = [1, 2, 3, 4, 5]
    breadcrumb_list2 = [5, 4, 3, 2, 1]
    breadcrumb_list3 = [55, 44, 33, 22, 11]
    breadcrumb_list4 = [11, 22, 33, 44, 55]

    breadcrumb_dict1 = {"KEY1": 47, "KEY2": 240}
    breadcrumb_dict2 = {"TARGET": 240, "NON_TARGET": 16}
    breadcrumb_dict3 = {"TARGET": 240, "NON_TARGET": 16}
    breadcrumb_dict4 = {
        "KEY_1": {"INNER_KEY_1": 20, "INNER_KEY_2": 40, "INNER_KEY_3": 50, "INNER_KEY_4": 50},
        "KEY_2": {"INNER_KEY_1": 100, "INNER_KEY_2": 300, "INNER_KEY_3": 40, "INNER_KEY_4": 600},
        "KEY_3": {"INNER_KEY_1": 1000, "INNER_KEY_2": 100, "INNER_KEY_3": 7234, "INNER_KEY_4": 3333},
        "KEY_4": {"INNER_KEY_1": 2222, "INNER_KEY_2": 3456, "INNER_KEY_3": 6665, "INNER_KEY_4": 763},
    }

    def record(name, ok):
        nonlocal passed, total
        total += 1
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if ok:
            passed += 1

    ok, res = safe_call(E01.question_1, "Test")
    record("Q1.1", ok and check_equal(False, res))
    ok, res = safe_call(E01.question_1, 3000)
    record("Q1.2", ok and check_equal(True, res))

    ok, res = safe_call(E01.question_2, breadcrumb_list1, breadcrumb_list2)
    record("Q2.1", ok and check_tuple((5, 1), res))
    ok, res = safe_call(E01.question_2, breadcrumb_list2, breadcrumb_list1)
    record("Q2.2", ok and check_tuple((1, 5), res))

    ok, res = safe_call(E01.question_3, True, False, True)
    record("Q3.1", ok and check_equal(False, res))
    ok, res = safe_call(E01.question_3, True, True, False)
    record("Q3.2", ok and check_equal(True, res))

    ok, res = safe_call(E01.question_4, 10)
    record("Q4.1", ok and check_equal(30, res))
    ok, res = safe_call(E01.question_4, 64)
    record("Q4.2", ok and check_equal(192, res))

    ok, res = safe_call(E01.question_5, breadcrumb_dict1)
    record("Q5.1", ok and check_equal(297, res))

    ok, res = safe_call(E01.question_6, breadcrumb_dict4)
    record("Q6.1", ok and check_equal(5736.0, res))

    ok, res = safe_call(E01.question_7, 5)
    record("Q7.1", ok and check_list([0, 47, 94, 141, 188], res))
    ok, res = safe_call(E01.question_7, 12)
    record("Q7.2", ok and check_list([0, 47, 94, 141, 188, 235, 282, 329, 376, 423, 470, 517], res))

    ok, res = safe_call(E01.question_8, 5, 6, breadcrumb_list1)
    record("Q8.1", ok and check_equal(6, res))
    ok, res = safe_call(E01.question_8, 4, 7, breadcrumb_list2)
    record("Q8.2", ok and check_equal(4, res))

    ok, res = safe_call(E01.question_9, breadcrumb_dict2)
    record("Q9.1", ok and check_equal(480.4, res))

    ok, res = safe_call(E01.question_10, breadcrumb_list1, 3)
    record("Q10.1", ok and check_equal(3, res))
    ok, res = safe_call(E01.question_10, breadcrumb_list2, 5)
    record("Q10.2", ok and check_equal(5, res))

    ok, res = safe_call(E01.question_11, 27)
    record("Q11.1", ok and check_equal(1350, res))
    ok, res = safe_call(E01.question_11, 53)
    record("Q11.2", ok and check_equal(530, res))

    ok, res = safe_call(E01.question_12, 4, 6, 0)
    record("Q12.1", ok and check_equal("Input1: 4, Input2: 6, Input3: 0", res))
    ok, res = safe_call(E01.question_12, 23, 8, 89)
    record("Q12.2", ok and check_equal("Input1: 23, Input2: 8, Input3: 89", res))

    ok, res = safe_call(E01.question_13, 4, 6, 0)
    record("Q13.1", ok and check_equal("The final value is 1.0", res))
    ok, res = safe_call(E01.question_13, 23, 8, 89)
    record("Q13.2", ok and check_equal("The final value is 5886.125", res))

    ok, res = safe_call(E01.question_14, [4, 5], [10, 20])
    record(
        "Q14.1",
        ok
        and check_list(
            [10.0, 20.0, 12.5, 25.0, 10.0, 20.0, 12.5, 25.0, 10.0, 20.0, 12.5, 25.0, 10.0, 20.0, 12.5, 25.0],
            res,
        ),
    )
    ok, res = safe_call(E01.question_14, [3, 4], [12, 22])
    record(
        "Q14.2",
        ok and check_list([9.0, 16.5, 12.0, 22.0, 9.0, 16.5, 12.0, 22.0, 9.0, 16.5, 12.0, 22.0, 9.0, 16.5, 12.0, 22.0], res),
    )

    ok, res = safe_call(E01.question_15, 3, 3)
    record("Q15.1", ok and check_dict({"KEY0": 0, "KEY1": 3, "KEY2": 6}, res))
    ok, res = safe_call(E01.question_15, 4, 7)
    record("Q15.2", ok and check_dict({"KEY0": 0, "KEY1": 7, "KEY2": 14, "KEY3": 21}, res))

    ok, res = safe_call(E01.question_16, breadcrumb_dict3)
    record("Q16.1", ok and check_equal(240, res))

    ok, res = safe_call(E01.question_17, "JPM", "2020-01-01", "2023-12-31")
    record("Q17.1", ok and check_df_struct_q17(res, "JPM"))
    ok, res = safe_call(E01.question_17, "AAPL", "2015-01-01", "2023-12-31")
    record("Q17.2", ok and check_df_struct_q17(res, "AAPL"))

    ok, res = safe_call(E01.question_18, pd.Series(breadcrumb_list1))
    record("Q18.1", ok and check_series_tuple((5, 4), res))
    ok, res = safe_call(E01.question_18, pd.Series(breadcrumb_list2))
    record("Q18.2", ok and check_series_tuple((5, 0), res))

    expected_q19 = pd.DataFrame(
        {
            "COL_2": [3, 2, 1],
            "COL_3": [33, 22, 11],
            "NEW_COL": [3.0, 3.0, 3.0],
            "NEW_MEAN": [2.0, 2.0, 2.0],
        },
        index=[2, 3, 4],
    )
    ok, res = safe_call(
        E01.question_19,
        {"COL_1": breadcrumb_list1, "COL_2": breadcrumb_list2, "COL_3": breadcrumb_list3},
    )
    record("Q19.1", ok and check_df_exact(expected_q19, res))

    expected_q20 = pd.DataFrame(
        {
            "COL_1": [1, 4, 9, 16, 25],
            "COL_2": [5, 4, 3, 2, 1],
            "COL_3": [55, 44, 33, 22, 11],
            "NEW_COL": [503284375, 3748096, 35937, 484, 11],
        }
    )
    ok, res = safe_call(
        E01.question_20,
        breadcrumb_list1,
        breadcrumb_list2,
        breadcrumb_list3,
        breadcrumb_list4,
    )
    record("Q20.1", ok and check_df_exact(expected_q20, res))

    print(f"\nRESULT: {passed}/{total} passed")


if __name__ == "__main__":
    main()
