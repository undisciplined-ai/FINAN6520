import H03_CONTROL_FLOW_HARMER_KAI_U0895215 as H03

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

# Question 6
results.append(check_result('question_6', [5, 7], 6722.8))
results.append(check_result('question_6', [1, 7], 42.0))

# Question 7
results.append(check_result('question_7', [50], True))
results.append(check_result('question_7', [10], False))

# Question 8
results.append(check_result('question_8', [True, 700, 600], True))
results.append(check_result('question_8', [False, 0, 7], False))
results.append(check_result('question_8', [True, 4, 7], False))

# Question 9
results.append(check_result('question_9', [47], True))
results.append(check_result('question_9', ['47'], False))

print(f"\nSummary: {results.count(True)} correct, {results.count(False)} incorrect.")
