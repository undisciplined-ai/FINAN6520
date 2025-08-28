student_name = "HARMER_KAI_U0895215"

######################
##### Question 1 #####
######################
### Write a function to determine if an input is a string. Return the appropriate boolean statement for each input. 
## EX: input of 6 returns False
def question_1(INPUT1):

    OUTPUT = isinstance(INPUT1, str)

    return OUTPUT

######################
##### Question 2 #####
######################
### Write a function with two inputs. These inputs will be multiplied by one another. Return the outcome. 

def question_2(INPUT1, INPUT2):

    OUTPUT = INPUT1 * INPUT2

    return OUTPUT   

######################
##### Question 3 #####
######################
### Write a function to take in a list of numbers and return the sum of the list. 

def question_3(INPUTLIST):

    OUTPUT = sum(INPUTLIST)

    return OUTPUT

######################
##### Question 4 #####
######################
### Write a function to remove duplicate values inside of a list. Return the result as a list.

def question_4(INPUTLIST):

    OUTPUT = list(set(INPUTLIST))

    return OUTPUT

######################
##### Question 5 #####
######################
### Write a function which has two inputs. 
## Multiply each in put by 5
## Divide each input by 3
## Exponentiate the first input by the second input
## Return the result. 

def question_5(INPUT1 , INPUT2):

    OUTPUT1 = (INPUT1 * 5) / 3

    OUTPUT2 = (INPUT2 * 5) / 3

    OUTPUT3 = OUTPUT1 ** OUTPUT2
    
    return OUTPUT3

######################
##### Question 6 #####
######################

### DO YOUR BEST NOT TO GOOGLE THIS QUESTION. SOLVE IT ON YOUR OWN. 
## Review what operators you have at your disposal. 
### Write a function which takes in a single integer input.
## Determine if the input is an even number, then return the boolean outcome of that comparison. 

def question_6(INPUT1: int):

    OUTPUT = INPUT1 % 2 == 0

    return OUTPUT

######################
##### Question 7 #####
######################

## Write a function to take in two lists.
## Using the two lists, create a dictionary object and return the result. 
## The first input is a list of keys and the second is a list of values. 

def question_7(LIST1, LIST2):

    OUTPUT = dict(zip(LIST1, LIST2))

    return OUTPUT

######################
##### Question 8 #####
######################
## Review this link: https://www.w3schools.com/python/python_lists_methods.asp
## Write a function to take in two lists.
## Reverse the first list, then append the integer 4 to it. 
## In the second input, alter the second value to equal 10
## Extend the second list with the values from the first and return the result. 

def question_8(LIST1, LIST2):

    LIST1.reverse()
    LIST1.append(4)
    LIST2[1] = 10
    LIST2.extend(LIST1)

    return LIST2

######################
##### Question 9 #####
######################

## Write a function to take in two lists
## Create a new dictionary. The key values are to be "list1" and "list2". The values are respective inputs 1 and 2. 
## Select the second value of the list represented by "list1" key. Save this as an object. 
## Select the fifth value of the list represented by the "list2" key, then save it as an object also. 
## Return these two values as a tuple.

def question_9(INPUT1, INPUT2):

    OUTPUT = {"LIST1": INPUT1, "LIST2": INPUT2}

    VALUE1 = OUTPUT["LIST1"][2]
    VALUE2 = OUTPUT["LIST2"][5]

    return (VALUE1, VALUE2)


######################
##### Question 10 ####
######################

## Write a function to take in a string
## Reverse the string
## Make all the characters upper case
## Replace all instances of "K" with "D"
## Return the result

def question_10(INPUT1: str):
    OUTPUT1 = INPUT1[::-1]
    OUTPUT2 = OUTPUT1.upper()
    OUTPUT3 = OUTPUT2.replace("K", "D")

    return OUTPUT3
