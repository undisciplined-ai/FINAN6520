import H02_BASICS_HARMER_KAI_U0895215 as H02

# Helper function to check type and value
def check_answer(func_name, result, expected, expected_type):
    if isinstance(result, Exception):
        print(f"{func_name}: Ungraded (Error: {result})")
        return
    correct_type = isinstance(result, expected_type)
    correct_value = result == expected
    if correct_type and correct_value:
        print(f"{func_name}: Correct! Value: {result} (Type: {type(result).__name__})")
    else:
        print(f"{func_name}: Incorrect. Got {result} (Type: {type(result).__name__}), Expected {expected} (Type: {expected_type.__name__})")

def safe_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return e

# Question 1
test1a = safe_call(H02.question_1, 'A STRING')
check_answer('question_1', test1a, True, bool)
test1b = safe_call(H02.question_1, 4)
check_answer('question_1', test1b, False, bool)

# Question 2
test2 = safe_call(H02.question_2, 4, 4)
check_answer('question_2', test2, 16, int)

# Question 3
test3 = safe_call(H02.question_3, [0,1,2,3,4])
check_answer('question_3', test3, 10, int)

# Question 4
test4a = safe_call(H02.question_4, [0,1,2,3,4])
check_answer('question_4', test4a, [0,1,2,3,4], list)
test4b = safe_call(H02.question_4, [0,1,0,1,0])
check_answer('question_4', sorted(test4b) if not isinstance(test4b, Exception) else test4b, [0,1], list)

# Question 5
test5 = safe_call(H02.question_5, 2, 3)
check_answer('question_5', test5, 411.5226337448561, float)

# Question 6
test6a = safe_call(H02.question_6, 4)
check_answer('question_6', test6a, True, bool)
test6b = safe_call(H02.question_6, 3)
check_answer('question_6', test6b, False, bool)

# Question 7
test7 = safe_call(H02.question_7, ['key1','key2','key3','key4','key5'],[0,1,2,3,4])
check_answer('question_7', test7, {'key1': 0, 'key2': 1, 'key3': 2, 'key4': 3, 'key5': 4}, dict)

# Question 8
test8 = safe_call(H02.question_8, [0,1,2,3,4],[0,1,2,3,4])
check_answer('question_8', test8, [0, 10, 2, 3, 4, 4, 3, 2, 1, 0, 4], list)

# Question 9
test9a = safe_call(H02.question_9, [0,1,2,3,4,5],[0,1,2,3,4,5])
check_answer('question_9', test9a, (2, 5), tuple)
test9b = safe_call(H02.question_9, [4,3,2,1,0,9],[0,1,2,3,4,8])
check_answer('question_9', test9b, (2, 8), tuple)

# Question 10
test10a = safe_call(H02.question_10, 'A STRING WITH SOME K AND D CHARACTERS')
check_answer('question_10', test10a, 'SRETCARAHC D DNA D EMOS HTIW GNIRTS A', str)
test10b = safe_call(H02.question_10, 'ANOTHER STRING')
check_answer('question_10', test10b, 'GNIRTS REHTONA', str)