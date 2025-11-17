import H13_HARMER_KAI_U0895215 as H13

######################
##### Question 1 #####
######################
print(H13.question_1(1, int))
### True

print(H13.question_1(1, bool))
### False

print(H13.question_1([1,2], int))
### False

######################
##### Question 2 #####
######################
print(H13.question_2('R',4))
### {'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3}

print(H13.question_2('TEST',6))
### {'TEST0': 0, 'TEST1': 1, 'TEST2': 2, 'TEST3': 3, 'TEST4': 4, 'TEST5': 5}

######################
##### Question 3 #####
######################
print(H13.question_3(2021,2022,2023,5,5))
### True

print(H13.question_3(2021,2025,2023,5,5))
### False

######################
##### Question 4 #####
######################
print(H13.question_4({'one':1, 'two': 2}))
### one -- 1
### two -- 2

print(H13.question_4({'test':2, 'run': 4}))
### test -- 2
### run -- 4

######################
##### Question 5 #####
######################
print(H13.question_5({'KEY1':{'TARGET':4},'KEY2':{'TARGET':6}}))
### {'KEY1': {'TARGET': 4, 'NEW_KEY': 20}, 'KEY2': {'TARGET': 6, 'NEW_KEY': 30}}

print(H13.question_5({'TEST1':{'TARGET':3},'TEST2':{'TARGET':7}}))
### {'TEST1': {'TARGET': 3, 'NEW_KEY': 15}, 'TEST2': {'TARGET': 7, 'NEW_KEY': 35}}

######################
##### Question 6 #####
######################
print(H13.question_6(4))
### (False, 1600)

print(H13.question_6(36))
### (True, 14400)

######################
##### Question 7 #####
######################
print(H13.question_7(4))
### 8EXECUTED

print(H13.question_7(64))
### 128EXECUTED