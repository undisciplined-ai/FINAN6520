import math
import numbers

import H05_IMPLEMENTATION_HARMER_KAI_U0895215 as H05


def safe_call(fn, *args, **kwargs):
    try:
        return True, fn(*args, **kwargs)
    except Exception as e:
        return False, e


def assert_equal(actual, expected, label):
    ok = actual == expected
    print(f"{label} => {'✔️' if ok else '❌'}")
    return ok


def assert_float_close(actual, expected, tol, label):
    ok = isinstance(actual, numbers.Real) and math.isfinite(actual) and abs(actual - expected) <= tol
    print(f"{label} => {'✔️' if ok else '❌'}")
    return ok


def main():
    total = 0
    passed = 0

    # Q1
    total += 1; passed += assert_equal(H05.question_1(1000, 2, 10, 6), 1806.11, "question_1(1000,2,10,6)")
    total += 1; passed += assert_equal(H05.question_1(400000, 4, 15, 6), 977287.91, "question_1(400000,4,15,6)")

    # Q2
    total += 1; passed += assert_equal(H05.question_2(5000, 2, 10, 6), 2768.38, "question_2(5000,2,10,6)")
    total += 1; passed += assert_equal(H05.question_2(500000, 2, 10, 10), 188444.74, "question_2(500000,2,10,10)")

    # Q3 (live data: validate type, finiteness, and proximity to breadcrumb values)
    ok, val = safe_call(H05.question_3, 'AAPL')
    total += 1
    if ok:
        passed += assert_float_close(float(val), 13.22, 0.75, "question_3('AAPL')")
    else:
        print("question_3('AAPL') => ❌")

    ok, val = safe_call(H05.question_3, 'COST')
    total += 1
    if ok:
        passed += assert_float_close(float(val), 9.86, 0.75, "question_3('COST')")
    else:
        print("question_3('COST') => ❌")

    # Q4
    total += 1; passed += assert_equal(H05.question_4(6, 30, 500000), 2997.75, "question_4(6,30,500000)")
    total += 1; passed += assert_equal(H05.question_4(10, 30, 600000), 5265.43, "question_4(10,30,600000)")

    print(f"\nSummary: {passed} correct, {total - passed} incorrect.")


if __name__ == "__main__":
    main()
