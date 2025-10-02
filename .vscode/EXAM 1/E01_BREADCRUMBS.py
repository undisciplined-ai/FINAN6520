import HARMER_KAI_U0895215_E01 as E01
import warnings
import pandas as pd
warnings.simplefilter(action='ignore', category=FutureWarning)

###### INPUT OBJECTS ######
breadcrumb_list1 = [1,2,3,4,5]
breadcrumb_list2 = [5,4,3,2,1]
breadcrumb_list3 = [55,44,33,22,11]
breadcrumb_list4 = [11,22,33,44,55]

breadcrumb_dict1 = {'KEY1':47,"KEY2":240}
breadcrumb_dict2 = {'TARGET':240,'NON_TARGET':16} 
breadcrumb_dict3 = {'TARGET':240,'NON_TARGET':16} 
breadcrumb_dict4 = {'KEY_1':{'INNER_KEY_1':20,
                             'INNER_KEY_2':40,
                             'INNER_KEY_3':50,
                             'INNER_KEY_4':50},
                    'KEY_2':{'INNER_KEY_1':100,
                             'INNER_KEY_2':300,
                             'INNER_KEY_3':40,
                             'INNER_KEY_4':600},
                    'KEY_3':{'INNER_KEY_1':1000,
                             'INNER_KEY_2':100,
                             'INNER_KEY_3':7234,
                             'INNER_KEY_4':3333},
                    'KEY_4':{'INNER_KEY_1':2222,
                             'INNER_KEY_2':3456,
                             'INNER_KEY_3':6665,
                             'INNER_KEY_4':763}}


######################
##### Question 1 #####
######################
print('--- QUESTION 1 - Example 1 ---')
print(E01.question_1('Test'))
### False
print('--- QUESTION 1 - Example 2 ---')
print(E01.question_1(3000))
### True

######################
##### Question 2 #####
######################
print('--- QUESTION 2 - Example 1 ---')
print(E01.question_2(breadcrumb_list1,breadcrumb_list2))
# ### (5, 1)
print('--- QUESTION 2 - Example 2 ---')
print(E01.question_2(breadcrumb_list2,breadcrumb_list1))
# ### (1, 5)

######################
##### Question 3 #####
######################
print('--- QUESTION 3 - Example 1 ---')
print(E01.question_3(True, False, True))
### False
print('--- QUESTION 3 - Example 2 ---')
print(E01.question_3(True, True, False))
### True

######################
##### Question 4 #####
######################
print('--- QUESTION 4 - Example 1 ---')
print(E01.question_4(10))
### 30
print('--- QUESTION 4 - Example 2 ---')
print(E01.question_4(64))
### 192

######################
##### Question 5 #####
######################
print('--- QUESTION 5 - Example 1 ---')
print(E01.question_5(breadcrumb_dict1))
### 297

######################
##### Question 6 #####
######################
print('--- QUESTION 6 - Example 1 ---')
print(E01.question_6(breadcrumb_dict4))
### 5736.0

######################
##### Question 7 #####
######################
print('--- QUESTION 7 - Example 1 ---')
print(E01.question_7(5))
### [0, 47, 94, 141, 188]
print('--- QUESTION 7 - Example 1 ---')
print(E01.question_7(12))
### [0, 47, 94, 141, 188, 235, 282, 329, 376, 423, 470, 517]

######################
##### Question 8 #####
######################
print('--- QUESTION 8 - Example 1 ---')
print(E01.question_8(5,6,breadcrumb_list1))
### 6
print('--- QUESTION 8 - Example 2 ---')
print(E01.question_8(4,7,breadcrumb_list2))
### 4

######################
##### Question 9 #####
######################
print('--- QUESTION 9 - Example 1 ---')
print(E01.question_9(breadcrumb_dict2))
### 480.4

#######################
##### Question 10 #####
#######################
print('--- QUESTION 10 - Example 1 ---')
print(E01.question_10(breadcrumb_list1, 3))
### 3
print('--- QUESTION 10 - Example 2 ---')
print(E01.question_10(breadcrumb_list2, 5))
### 5

#######################
##### Question 11 #####
#######################
print('--- QUESTION 11 - Example 1 ---')
print(E01.question_11(27))
### 1350
print('--- QUESTION 11 - Example 2 ---')
print(E01.question_11(53))
### 530

#######################
##### Question 12 #####
#######################
print('--- QUESTION 12 - Example 1 ---')
print(E01.question_12(4, 6, 0))
### Input1: 4, Input2: 6, Input3: 0
print('--- QUESTION 12 - Example 12 ---')
print(E01.question_12(23, 8, 89))
### Input1: 23, Input2: 8, Input3: 89

#######################
##### Question 13 #####
#######################
print('--- QUESTION 13 - Example 1 ---')
print(E01.question_13(4, 6, 0))
### The final value is 1.0
print('--- QUESTION 13 - Example 2 ---')
print(E01.question_13(23, 8, 89))
### The final value is 5886.125

#######################
##### Question 14 #####
#######################
print('--- QUESTION 14 - Example 1 ---')
print(E01.question_14([4,5],[10,20]))
### [10.0, 20.0, 12.5, 25.0, 10.0, 20.0, 12.5, 25.0, 10.0, 20.0, 12.5, 25.0, 10.0, 20.0, 12.5, 25.0]
print('--- QUESTION 14 - Example 2 ---')
print(E01.question_14([3,4],[12,22]))
### [9.0, 16.5, 12.0, 22.0, 9.0, 16.5, 12.0, 22.0, 9.0, 16.5, 12.0, 22.0, 9.0, 16.5, 12.0, 22.0]

#######################
##### Question 15 #####
#######################
print('--- QUESTION 15 - Example 1 ---')
print(E01.question_15(3,3))
### 'KEY0': 0, 'KEY1': 3, 'KEY2': 6}
print('--- QUESTION 15 - Example 2 ---')
print(E01.question_15(4,7))
### {'KEY0': 0, 'KEY1': 7, 'KEY2': 14, 'KEY3': 21}

#######################
##### Question 16 #####
#######################
print('--- QUESTION 16 - Example 1 ---')
print(E01.question_16(breadcrumb_dict3))
### 240


#######################
##### Question 17 #####
#######################
print('--- QUESTION 17 - Example 1 ---')
print(E01.question_17('JPM','2020-01-01', '2023-12-31'))
### Ticker             JPM
### 2023-03-16  122.925331
### 2023-03-17  118.280945
### 2023-03-20  119.531364
### 2023-03-21  122.737297
### 2023-03-22  119.568970
### ...                ...
### 2023-12-22  160.884949
### 2023-12-26  161.836411
### 2023-12-27  162.807098
### 2023-12-28  163.672058
### 2023-12-29  163.479858
### 
### [200 rows x 1 columns]

print('--- QUESTION 17 - Example 2 ---')
print(E01.question_17('AAPL', '2015-01-01', '2023-12-31'))
### Ticker            AAPL
### 2023-03-16  153.917221
### 2023-03-17  153.077759
### 2023-03-20  155.448013
### 2023-03-21  157.304688
### 2023-03-22  155.872696
### ...                ...
### 2023-12-22  191.974686
### 2023-12-26  191.429306
### 2023-12-27  191.528458
### 2023-12-28  191.954834
### 2023-12-29  190.913651
###
### [200 rows x 1 columns]

######################
##### Question 18 ####
######################
print('--- QUESTION 18 - Example 1 ---')
print(E01.question_18(pd.Series(breadcrumb_list1)))
### (5, 4)
print('--- QUESTION 18 - Example 2 ---')
print(E01.question_18(pd.Series(breadcrumb_list2)))
### (5, 0)

#######################
##### Question 19 #####
#######################
print('--- QUESTION 19 - Example 1 ---')
print(E01.question_19({'COL_1':breadcrumb_list1,
                       'COL_2':breadcrumb_list2,
                       'COL_3':breadcrumb_list3}))
###    COL_2  COL_3  NEW_COL  NEW_MEAN
### 2      3     33      3.0       2.0
### 3      2     22      3.0       2.0
### 4      1     11      3.0       2.0
#######################
##### Question 20 #####
#######################
print('--- QUESTION 20 - Example 1 ---')
print(E01.question_20(breadcrumb_list1,
                      breadcrumb_list2,
                      breadcrumb_list3,
                      breadcrumb_list4,))
###    COL_1  COL_2  COL_3    NEW_COL
### 0      1      5     55  503284375
### 1      4      4     44    3748096
### 2      9      3     33      35937
### 3     16      2     22        484
### 4     25      1     11         11
