
student_name = "SOLUTIONS"

import pandas as pd
import numpy as np
import yfinance as yf

#################################################################################
#################################### EXAM 1 #####################################
#################################################################################

######################
##### Question 1 #####
######################
### Your function has a single input
### Determine if an input is an integer. Return the appropriate boolean statement for each input. 

def question_1(input_one):

    return isinstance(input_one, int)

######################
##### Question 2 #####
######################
### Your function has two lists as inputs.
## Create a dictionary object with input one as your keys and input two as your values
## Then return the key/value pair at index four (4) as a tuple. 

def question_2(input_one, input_two):

    new_dict = {}

    for index in range(len(input_one)):
        new_dict[input_one[index]] = input_two[index]

    items = list(new_dict.items())

    return items[4]

######################
##### Question 3 #####
######################
### Your function has three boolean inputs. 
## Determine if all inputs are equal, save this result as a variable
## Determine if the first and third inputs are equal, save this result as a variable
## Compare the two saved variables, determine if they are the same value, then return the outcome of this comparison. 

def question_3(input_one, input_two, input_three):

    all_equal = input_one == input_two == input_three
    first_third_equal = input_one == input_three

    return all_equal == first_third_equal

######################
##### Question 4 #####
######################
### Your function takes in one integer input. 
## Create a variable called "counter" and assign it the value of zero (0)
## Using input one, create a for loop that runs at the length of the provided value.
## Update the counter value once per loop by adding three to the current value. 
## When the loop is finished, return the counter. 

def question_4(input_one):

    counter = 0

    for _ in range(input_one):
        counter = counter + 3

    return counter

######################
##### Question 5 #####
######################
### Your function has a single dictionary input.
## Create a variable called "output" and assign it the value of ten (10)
## Create a for loop to iterate up on the dictionary items.
## Inside the for loop, update the output variable by adding each dictionary value to it
## When the for loop is finished, return the output variable. 

def question_5(input_one):

    output = 10

    for value in input_one.values():
        output = output + value

    return output

######################
##### Question 6 #####
######################
### Your function takes in a single dictionary input.
    ## This dictionary is nested, meaning a dictionary of dictionaries
## In the first dictionary, keys are notated as "KEY_X"
## In the second dictionary, keys are notated "INNER_KEY_X"

## Select KEY_3, INNER_KEY_4, and save the value to "variable1"
## Select KEY_1, INNER_KEY_2, and save the value to "variable2"
## Select KEY_4, INNER_KEY_3, and save the value to "variable3"

## Save the following aggregation to "output"
    ## Add all new variables together, multiply them by 4, then divide by 7.
## Return output. 

def question_6(input_one):

    variable1 = input_one['KEY_3']['INNER_KEY_4']
    variable2 = input_one['KEY_1']['INNER_KEY_2']
    variable3 = input_one['KEY_4']['INNER_KEY_3']

    output = (variable1 + variable2 + variable3) * 4 / 7

    return output 

######################
##### Question 7 #####
######################
## Your function has a single integer input
## Create an empty list variable called "output"
## Using input one, create a for loop that runs at the length of input one. 
    ## utilize "i" to represent the iterable value
## inside the loop:
    ## multiply i by 47
    ## Add each loop's result into the output list.
## When the for loop is finished, return the output variable. 

def question_7(input_one):

    output = []

    for i in range(input_one):
        output.append(i * 47)

    return output

######################
##### Question 8 #####
######################
### Your function has two integer inputs and one list input. 
## Loop over the third input (the list) and assign your iterable value to "i"
## Inside your loop:
    ## If i is greater than input one, add 3 to input two. 
    ## elif i is less than input one, add 3 to input one. 
    ## else, set the input two to equal the value of the first input. 
## return the updated version of input 2 when the loop is finished. 

def question_8(input_one, input_two, input_three):

    for i in input_three:
        if i > input_one:
            input_two = input_two + 3
        elif i < input_one:
            input_one = input_one + 3
        else:
            input_two = input_one

    return input_two

######################
##### Question 9 #####
######################
### Your function has a single dictionary input
## Pop the key "TARGET" from the dictionary and save the value to a new variable called "output"
## Update the output variable to be equal to itself times 10
## Update the output variable again to be equal to itself plus 2 .
## Update the output variable again to be equal to itself divided by 5.
## Return the output variable. 

def question_9(input_one):

    output = input_one.pop('TARGET')
    output = output * 10
    output = output + 2
    output = output / 5

    return output

#######################
##### Question 10 #####
#######################
### Your function has two inputs, a list and an integer.
## Create an empty list named "output"
## Create a loop to iterate upon input one. 
    ## Utilize "i" to represent the iterable value
## inside the loop do the following:
    ## if i is greater than input two, append False to output, else append True to output. 

## After the loop, return the sum of the output list. 

def question_10(input_one, input_two):

    output = []

    for i in input_one:
        if i > input_two:
            output.append(False)
        else:
            output.append(True)

    return sum(output)

#######################
##### Question 11 #####
#######################
### Your function has a single integer input. 
## This function will have many logic gates.
## If the input is larger than 10, enter into a new code section, else return input one unaltered. 
    ## If the value is less than 50, enter into a new code section, else return the first input as 10 times itself
        ## If the value is both greater than 15 and less than 35, enter a new code section, else return input divided by 5
            ## If the value is equal to 25, then return the input as is, otherwise enter another code block. 
                ## If the value is less than 30 and greater than 20, return the input * 50, else return zero (0)

def question_11(input_one):

    if input_one > 10:
        if input_one < 50:
            if input_one > 15 and input_one < 35:
                if input_one == 25:
                    return input_one
                else:
                    if input_one < 30 and input_one > 20:
                        return input_one * 50
                    else:
                        return 0
            else:
                return input_one / 5
        else:
            return input_one * 10
    else:
        return input_one

#######################
##### Question 12 #####
#######################
### Your function has three integer inputs
## Return an f-string with the following format:
    ## "Input1: X, Input2: Y, Input3: Z"
## The X, Y, and Z, should be filled with the inputs provided to the function. 

def question_12(input_one, input_two, input_three):

    return f"Input1: {input_one}, Input2: {input_two}, Input3: {input_three}"

#######################
##### Question 13 #####
#######################
### Your function has three integer inputs. 
## If the first input is greater than 20, enter a new code section, else pass
    ## If the second input is less than 10:
        # Multiply the third input by the first input and assign the result to input three, else enter a new code section. 
        ## If input three is greater than 100, update input one to be 600 times input two, else pass. 

## After all above conditional logic, create a new variable named "output" equal to the value of input two
## Set output to equal input one times input three plus input two, then divided that equation by the value of output. 
    ## Remember your parentheses!

## Return an f-string in the following format:
    ## "The final value is X"
## X should be the value of output. 

def question_13(input_one, input_two, input_three):

    if input_one > 20:
        if input_two < 10:
            input_three = input_three * input_one
        else:
            if input_three > 100:
                input_one = 600 * input_two

    output = input_two
    output = (input_one * input_three + input_two) / output

    return f"The final value is {output}"

#######################
##### Question 14 #####
#######################

### Your function takes in two lists as inputs. 
### Create an empty list called "output"
### Create a variable called "counter" and assign it the value of zero (0)
### Create a for loop to iterate upon input one, your iterable value is "i"
    ## Inside the for loop, iterate upon input two, your iterable value is "j"
        ## Inside this loop add 1 to counter and reassign counter inplace
        ## Multiply i and j together, then append this result to the output list. 
## After running the loops, divide each list value of "output" by 4, then reassign the result to itself. 
## Multiply the output list by the counter variable, then return the result.

def question_14(input_one, input_two):

    output = []
    counter = 0

    for i in input_one:
        for j in input_two:
            counter = counter + 1
            output.append(i * j)

    for index in range(len(output)):
        output[index] = output[index] / 4

    output = output * counter

    return output

#######################
##### Question 15 #####
#######################
### Your function has two integer inputs. 
## Create an empty dictionary called "output"
## Using input one, create a for loop that runs at the length of the provided value.
    ## utilize "i" to represent the iterable value
## Inside the loop:
    ## create a new variable called "key".
    ## "key" will be a string, this string will be the word "KEY" plus the current value of i.
        ## Results will be similar to "KEY10" for example.
        ## Each loop will create a new key value!
    ## Update the dictionary with your generated key variable as the key.
        ## Your value will be input two times i.
## Finally, return the output variable. 

def question_15(input_one, input_two):

    output = {}

    for i in range(input_one):
        key = "KEY" + str(i)
        output[key] = input_two * i

    return output

#######################
##### Question 16 #####
#######################
### Your function has one dictionary input.
## Create a variable called "output" with an initial value of zero (0)
## Using a for loop, unpack the dictionary key/value pairs.
## Inside the loop:
    ## If a key is called "TARGET", enter a new code block, else continue the loop
        ## Update "output" with the value associated with "TARGET"
## Return the output object

def question_16(input_one):

    output = 0

    for key, value in input_one.items():
        if key == 'TARGET':
            output = value

    return output

#######################
##### Question 17 #####
#######################
### Your function takes in multiple inputs:
    ## ticker: a single ticker or list of tickers
    ## Beginning Date: Initial date of data.
    ## Ending Date: Final date of data

## With these inputs you'll request data from YahooFinance and save it into a dataframe called "output" inside your function. 
## Select the adjusted close column and reassign "output" with the results. 
    ## Recall this column being named "Close"
## Alter the date column to a pandas datetime object and set it as the index. 
## Select the most recent 200 rows of data and save the result to output. 
## Return the output dataframe. 

def question_17(ticker, beginning_date, ending_date):

    output = yf.download(ticker, start=beginning_date, end=ending_date, auto_adjust=True, progress=False)

    if output.empty:
        return output

    output.index = pd.to_datetime(output.index)
    output.index.name = None

    if isinstance(ticker, str):
        output = output[['Close']].copy()
        output.columns = [ticker]
    else:
        if isinstance(output.columns, pd.MultiIndex):
            output = output['Close'].copy()
        else:
            output = output[['Close']].copy()

    output.columns.name = 'Ticker'
    output = output.tail(200)

    return output

#######################
##### Question 18 #####
#######################
### Your function takes in one pandas series object. 
## Find the max value of the series and save this to a variable named "max_value"
## Find the index location of the value and save this to "max_index". Do not use .idxmax(). 
## return max_value and max_index as a tuple

def question_18(input_one):

    max_value = input_one.max()
    if hasattr(max_value, 'item'):
        max_value = max_value.item()
    values_list = input_one.tolist()
    max_index = values_list.index(max_value)

    return (max_value, max_index)

#######################
##### Question 19 #####
#######################
### Your function takes in one dictionary.
    ## This dictionary will have columns with syntax similar to "COL_X"
## Create a dataframe from input one and name it "output"
## Create a new column called "NEW_COL" and fill it with the median value of 'COL_1'
## Create another columns named "ANOTHER_COL" and fill the new column with the value of 1

## Select rows two (2) up to and not including six (6) and columns one (1) up to and not including four (4) using index location and save the result to your output object.
## Create another column called "NEW_MEAN" and fill it with the average value of 'COL_2'
## Return the output dataframe. 

def question_19(input_one):

    output = pd.DataFrame(input_one)
    output['NEW_COL'] = output['COL_1'].median()
    output['ANOTHER_COL'] = 1

    output = output.iloc[2:6, 1:4].copy()
    output['NEW_MEAN'] = output['COL_2'].mean()

    return output

#######################
##### Question 20 #####
#######################
### Your function takes in four lists. 
## Create a dataframe with all inputs and name it "output"
## Your columns will have "COL_X" syntax and increment by 1. 
## Multiply COL_1 by itself and reassign COL_1 with the results
## Drop COL_4 and be sure it is dropped inplace. 
## Raise the values in COL_3 to the power of COL_2 values and assign the results to a new column named "NEW_COL"

## Return the output dataframe

def question_20(input_one, input_two, input_three, input_four):

    output = pd.DataFrame({
        'COL_1': input_one,
        'COL_2': input_two,
        'COL_3': input_three,
        'COL_4': input_four
    })

    output['COL_1'] = output['COL_1'] * output['COL_1']
    output.drop('COL_4', axis=1, inplace=True)
    output['NEW_COL'] = output['COL_3'] ** output['COL_2']

    return output
