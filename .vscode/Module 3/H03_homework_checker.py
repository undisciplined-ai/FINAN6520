import H03_CONTROL_FLOW as H03

# Helper to check and print results
def check_result(func_name, args, expected):
    try:
        result = getattr(H03, func_name)(*args)
        correct = result == expected
        print(f"{func_name}{tuple(args)} => {result} | Expected: {expected} | {'✔️' if correct else '❌'}")
        return correct
    except Exception as e:
        print(f"{func_name}{tuple(args)} => ERROR: {e}")
        return False

results = []

# Question 1
results.append(check_result('question_1', [True, False, True], False))
results.append(check_result('question_1', [False, False, True], True))

# Question 2
results.append(check_result('question_2', [False, True], True))
results.append(check_result('question_2', [True, True], False))

# Question 3
results.append(check_result('question_3', [True, False, True, False], False))
results.append(check_result('question_3', [False, False, True, True], False))
results.append(check_result('question_3', [True, True, False, False], True))

# Question 4
results.append(check_result('question_4', [True], False))
results.append(check_result('question_4', [False], True))

# Question 5 (if implemented)
if hasattr(H03, 'question_5'):
    results.append(check_result('question_5', [10, 15], False))
    results.append(check_result('question_5', [15, 10], True))
    results.append(check_result('question_5', [10, 10], True))
    results.append(check_result('question_5', [15, 15], True))

print(f"\nSummary: {results.count(True)} correct, {results.count(False)} incorrect.")
