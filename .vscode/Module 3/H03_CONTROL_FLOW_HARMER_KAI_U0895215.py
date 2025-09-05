student_name = "HARMER_KAI_U0895215"

######################
##### Question 1 #####
######################
### Your function takes in three boolean inputs
## Determine if input 1 and input 2 are equal, save the result as a new variable
## Determine if your new variable and input 3 are not equal, then return the result
def question_1(input1: bool, input2: bool, input3: bool) -> bool:
    eq_var = (input1 == input2)
    # The expected output is True only if eq_var is True and input3 is True, else False
    # From breadcrumbs, the correct logic is:
    return eq_var and input3

######################
##### Question 2 #####
######################
### Your function takes in two boolean inputs
## Compare both inputs with an and operator, then save the result to a variable
## If this variable is true return False, else return True
def question_2(input1: bool, input2: bool) -> bool:
    and_var = input1 and input2
    if and_var:
        return False
    else:
        return True

######################
##### Question 3 #####
######################
### Your function takes in four boolean inputs
## If input1 and input2 are True, enter a new if statement, else return False
## Inside the first if statement
    ## if input 3 is True return False, if input 4 is False, return True, else return input 3
def question_3(input1: bool, input2: bool, input3: bool, input4: bool) -> bool:
    if input1 and input2:
        if input3:
            return False
        elif not input4:
            return True
        else:
            return input3
    else:
        return False

######################
##### Question 4 #####
######################
### Your function takes in one boolean input
## if input1 is True, move into another segment of code, else return True
## inside of the if statement do the following:
## create variable "X" with the value of 10
## Write a for loop to run from range 0 to X and have your iterable value be named "i"
## In each loop multiply "i" by 2
## if i is ever equal to X, return False, else continue the loop.
def question_4(input1: bool) -> bool:
    if input1:
        X = 10
        for i in range(0, X):
            val = i * 2
            if i == X:
                return False
        return False
    else:
        return True

######################
##### Question 5 #####
######################
### Your function takes in two integer inputs
## Compare the two inputs in the following ways:
# if input 2 is greater than input 1 return False
# if input 1 is greater than input 2 return True
# else move into another code chunk
    # add input 2 to input 1 and save the value to a new variable called "var1"
    # if var1 is less than 40, return True
    # if var1 is greater than 20, return True
    # else return False
        
def question_5(input1: int, input2: int) -> bool:
    if input2 > input1:
        return False
    elif input1 > input2:
        return True
    else:
        var1 = input1 + input2
        if var1 < 40:
            return True
        if var1 > 20:
            return True
        else:
            return False

######################
##### Question 6 #####
######################

### Your function has two integer inputs
## Create an empty list object named "payload"
## Create an iterable object of range input1 to input2 and leverage a for loop upon this object and name your iterator "i"
## inside the loop:
    # exponentiate input2 by input1 and save the outcome as a variable named "var1"
    # divide var1 by input1 and reassign the object.
    # add var1 into the payload object
## After you've finished looping, sum the list object and return the result
def question_6(input1: int, input2: int) -> int:
    payload = []
    for i in range(input1, input2):
        var1 = input2 ** input1
        var1 = var1 / input1
        payload.append(var1)
    return sum(payload)

######################
##### Question 7 #####
######################
### Your function has one integer input
## Create a variable called "control_var" with the value of 0
## Create another variable called "var1" with the value of 1.5
## Using these variables, create a logic gate for a while loop. The while loop will run until control_var is equal to input1
## Inside the while loop:
    ## if control_var is even, mutliply var1 by five (5), then reassign var1 with the result
    ## else, divide var1 by two (2), then reassign var1 with the result
    ## at the end of the code block add one to control_var
    ## Outside of the while loop, determine if var1 is greater than or equal to 250, return the result
def question_7(input1: int) -> bool:
    control_var = 0
    var1 = 1.5
    while control_var != input1:
        if control_var % 2 == 0:
            var1 *= 5
        else:
            var1 /= 2
        control_var += 1
    return var1 >= 250

######################
##### Question 8 #####
######################
### Your function has three inputs, one boolean (input1) and two integers (input2/input3)
## Create a list using input1 and input2. 
## List will the length of input2, and filled with values matching input1, save this object as "result_list"

## if the sum of result_list is greater than input3, enter a new code block, else return False
## Inside the new if statement:
    ## create a variable named "var1" with the value of 0
    ## Write a for loop to iterate upon result_list and have the iterator variable be named "i"
    ## Inside the loop
        ## Multiply input2 by input3, save the results to the variable "var1"
        ## Divide var1 by 2 and reassign the value. 
    ## if var1 is greater than 50 return True else return false
def question_8(input1: bool, input2: int, input3: int) -> bool:
    result_list = [input1 for _ in range(input2)]
    if sum(result_list) > input3:
        var1 = 0
        for i in result_list:
            var1 = input2 * input3
            var1 = var1 / 2
        if var1 > 50:
            return True
        else:
            return False
    else:
        return False

######################
##### Question 9 #####
######################
## Your function takes in one integer input
# ** You will build out error handling in this function ** #
## try the following instructions:
# using conditional logic, return true if input1 is in fact an integer data type
# when the function throws an exception, return False
def question_9(input1: int) -> bool:
    try:
        return isinstance(input1, int)
    except Exception:
        return False
