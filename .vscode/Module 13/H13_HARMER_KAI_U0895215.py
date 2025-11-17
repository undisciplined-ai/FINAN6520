import datetime as dt 

student_name = "HARMER_KAI_U0895215"

######################
##### Question 1 #####
######################
### Your function has two inputs. You'll compare input1 to input2. 
### Utilize isinstance to determine input1 is the same type as input2. 
### Your function will return a boolean value. 

### Breadcrumb: 
## Passing in 1 and int will resutl in True
## Passing in 1 and bool will result in False
## Passing in [1,2] and int will result in False

def question_1(input1, input2):
    output = isinstance(input1, input2)
    return output

######################
##### Question 2 #####
######################
### Your function has has two inputs. Input1 is a string and input2 is an integer.
## Create a variable called "output" and set it equal to an empty dictionary. 
## Create a for loop to run at the range of input2 and name your iterator "i"
## inside the loop:
    ### Concatenate input1 and the current value of "i" and assign the result to a variable called "new_key".
        ## Note, i will be an integer, you'll have to alter it to a string to concatenate properly.
    ### Create a new key/value pair in your output dictionary. 
        ### the key is your variable new_key and the associated value is the current value of i.
## When the loop is finished, return output. 

### Breadcrumb: 
## Passing in "R" and 4 will result in:
# {'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3}

def question_2(input1: str, input2: int):
    output = {}
    for i in range(input2):
        new_key = input1 + str(i)
        output[new_key] = i
    return output

# print(question_2_solution('R',4))

######################
##### Question 3 #####
######################

### Review this link: https://docs.python.org/3/library/datetime.html#date-objects
## This package is important to the exam. Be sure to understand how the datetime.date inputs work. 
## I import datetime as dt. You'll be able to access the date method using --> dt.date
## While you only have one question like this, play with this object type and become comfortable using it. 

### Your function has five inputs, which are all integers.
## Input1, input2, and input3 represent year inputs, Input3 is a month input, and input4 is a day input. 
## Create 3 date objects using the first three inputs as unique year inputs, then utilize input4 and input5 for all objects

## Compare date1, date2, and date3 using ternary comparison. 
    ## if date2 is within date1 and date3 return True, else return false. 

### Breadcrumb:
## Passing in 2021,2022,2023,5,5 Results in True
## IMPORTANT: This means that the second date lies within the first and third date. 
    ## Be sure to understand how the object is working. 
## Passing in 2021,2025,2023,5,5 Results in False

def question_3(input1: int, input2: int, input3: int, input4: int, input5: int):
    date1 = dt.date(input1, input4, input5)
    date2 = dt.date(input2, input4, input5)
    date3 = dt.date(input3, input4, input5)
    return date1 <= date2 <= date3

# print(question_3_solution(2021,2022,2023,5,5))
# print(question_3_solution(2021,2025,2023,5,5))

######################
##### Question 4 #####
######################

### Your function takes in a single dictionary input. 
## Recall the .items() method in relation to dictionaries. 
    ## https://www.programiz.com/python-programming/methods/dictionary/items

### Create a variable called output, which represents and empty string object. 
## Unpack key value pairs using a for loop and the .items() method of your dictionary. 
## Inside the Loop:
    ## Create an f-string in the following format:
        ## "key -- value\n"
        ## the "\n" is python syntax for new line. Please use this here and study what it does. 
            ### https://stackoverflow.com/questions/60885439/how-the-n-symbol-works-in-python
    ## Add your f-string to output. 
## When your loop is finished, return output. 

### Breadcrumb:
## Passing in {'one':1, 'two': 2} AND PRINTING the results will look like the following:
# one -- 1
# two -- 2
    ## If the output is not printed, then it will look like:
    # 'one -- 1\ntwo -- 2\n'

def question_4(input1: dict):
    output = ""
    for key, value in input1.items():
        output += f"{key} -- {value}\n"
    return output

# print(question_4_solution({'one':1, 'two': 2}))

######################
##### Question 5 #####
######################
### Your function takes in a single dictionary input. 
    ## This is a dictionary of dictionaries. 
## Recall the .keys() dictionary method. https://www.w3schools.com/python/ref_dictionary_keys.asp
## Using the .keys() method, loop over input 1 and assign your iterable value as "key"
## Inside your Loop:
    ## From input1, select a nested dictionary with the key iterable. This will be a dictionary object. 
    ## Select the value from "TARGET" in the nested dictionary and assign it to the variable "inner_value"

    ### Multiply inner_value by 5, then assign it to the value of "NEW_KEY" in the nested dictionary. 
        ## This is the same dictionary where "TARGET" resides.  

## Outside of the loop, return input1
### IMPORTANT: You are going to be taking nested data from input1, altering it, assigning it to new key, then returning input1.
    ## Be sure to spend lots of time working with nested dictionaries and looping upon dictionaries for the exam.

### Breadcrumb:
## Passing in the following dictionary:
    ## {'KEY1':{'TARGET':4},
    ##  'KEY2':{'TARGET':6}}
## Results in:
## {'KEY1': {'TARGET': 4, 'NEW_KEY': 20}, 'KEY2': {'TARGET': 6, 'NEW_KEY': 30}}

def question_5(input1: dict):
    for key in input1.keys():
        inner_dict = input1[key]
        inner_value = inner_dict['TARGET']
        inner_dict['NEW_KEY'] = inner_value * 5
    return input1


######################
##### Question 6 #####
######################
### Your function as one integer input. 
## Check if input1 is greater than or equal to 25, assign the result of the comparison to "output"
## Multiply input1 by 400 and reassign the result to itself. 

## Return output1 and input1 as a tuple. 

## Breadcrumb:
## Passing in 4 results in (False, 1600)
## Passing in 36 results in (True, 14400)

def question_6(input1: int):
    output = input1 >= 25
    input1 *= 400
    return output, input1

######################
##### Question 7 #####
######################
### Your function has one integer input.
## You'll be learning a new concept here. Study this link: https://www.w3schools.com/python/gloss_python_for_else.asp
## For-Else statements are a bit odd, but they are useful. 
## Essentially, the loop will run as expected. If the loop is not stopped by a break statement the the else statement will run. 

## Inside your function, create a loop to run at the range of input1. Name your iterable value "i".
## Inside the loop:
    # create an empty string called "output". 
    # Multiply input1 by 2 and add the value to the output string. Note, the integer will have to be altered to a string object. 
## Write an else statement and inside of the code block, add the word "EXECUTED" to your output variable. 
## Finally, return the output variable. 

### Breadcrumb:
## Passing in 4 will result in '8EXECUTED'
## Passing in 3 will result in '6EXECUTED'

def question_7(input1: int):
    output = ""
    for i in range(input1):
        output = str(input1 * 2)
    else:
        output += "EXECUTED"
    return output