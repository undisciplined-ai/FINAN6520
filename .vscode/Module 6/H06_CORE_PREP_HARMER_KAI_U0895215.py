
student_name = "HARMER_KAI_U0895215"

import pandas as pd
import yfinance as yf

######################
##### Question 1 #####
######################
### Your function has a single integer input
## Determine if an input is an boolean. 
## Return the appropriate boolean statement for each input. 

def question_1(input1):
    return isinstance(input1, bool)

######################
##### Question 2 #####
######################
### Your function has a single integer input
## Cast the input provided in as a boolean
## Return the resulting object. 

def question_2(input1):
    return bool(input1)

######################
##### Question 3 #####
######################
### Your function has a single input of any type. 
## Return the type of input one. 

def question_3(input1):
    return type(input1)

######################
##### Question 4 #####
######################
### Your function has two lists as inputs.
## Create a dictionary object with the two list inputs
## Return the key/value pair at the 4th index as a tuple

def question_4(list1, list2):
    d = dict(zip(list1, list2))
    # 4th index means zero-based index 4
    return list(d.items())[4]

######################
##### Question 5 #####
######################
### Your function has a single dictionary input. 
## Pop the key "TARGET" from the dictionary.
## Create a new variable called "keys", which is an empty list. 
## Write a for loop to iterate upon input one and it's keys, your iterable value will be "key"
    ## In the loop, append each key value to the keys list. 
## After the loop, return the keys list. 

def question_5(input1):
    input1.pop("TARGET", None)
    keys = []
    for key in input1:
        keys.append(key)
    return keys

######################
##### Question 6 #####
######################
## Your function has a single dictionary input. 
## Clear input one of all data. 
## Update input one with the key/value pair of "key1"/4
## Update input one dictionary with the key/value pair of "key2"/7
## return input one

def question_6(input1):
    input1.clear()
    input1.update({"key1": 4, "key2": 7})
    return input1

######################
##### Question 7 #####
######################
## Write a function to take in one dictionary input. 
## Gather the value of the "TARGET" key using the .get() method, save the value to a new variable named "value1"
## Multiply value1 by 14 and return the result. 

def question_7(input1):
    value1 = input1.get("TARGET")
    return value1 * 14

######################
##### Question 8 #####
######################
## Your function has one dictionary input. 
## Create and if/else statement. 
## If there is a key named "TARGET" in input one, enter a new code section, else return False
    ## if the value of "TARGET" equals 4, return True, else return False

def question_8(input1):
    if "TARGET" in input1:
        return input1["TARGET"] == 4
    else:
        return False

######################
##### Question 9 #####
######################
### Your function takes in a single dictionary input. 
    ## This dictionary is nested, meaning a dictionary of dictionaries
## In the first dictionary, keys are notated as "KEY_X"
## In the second dictionary, keys are notated "INNER_KEY_X"

## Select KEY_1, INNER_KEY_1, and save the value to "variable1"
## Select KEY_2, INNER_KEY_3, and save the value to "variable2"
## Return variable1 and variable2 as a tuple 

def question_9(input1):
    variable1 = input1["KEY_1"]["INNER_KEY_1"]
    variable2 = input1["KEY_2"]["INNER_KEY_3"]
    return (variable1, variable2)

#######################
##### Question 10 #####
#######################
### Your function has one list input
    ## This list is full of values similar to "KEY_X"
## Create an empty dictionary called "output"
## Create a for loop to iterate upon input one using the enumerate() function. 
    ## Utilize "i" to represent the index value
    ## utilize "key" to represent the iterable value

## Inside the loop:
    ## Update the dictionary with each loop's key
    ## The associated value is i times 4

## Return the output object

def question_10(input1):
    output = {}
    for i, key in enumerate(input1):
        output[key] = i * 4
    return output

#######################
##### Question 11 #####
#######################
### Your function has one integer input. 
## Create an empty list named "output"
## Using input one, create a for loop that runs at the length of the provided value.
    ## utilize "i" to represent the iterable value
## Inside the loop: 
    ## Multiply i times 4, then append the result to output. 
## After the loop, return the output object. 

def question_11(input1):
    output = []
    for i in range(input1):
        output.append(i * 4)
    return output

#######################
##### Question 12 #####
#######################
### Your function has one list input. 
## Create an empty list named "output"
## Write a for loop that will iterate upon input one. 
    ## utilize "i" to represent the iterable value
## Inside the loop: 
    ## If i is an even number, append the value to output, else pass
## When the loop is finished, return the output object.
    
def question_12(input1):
    output = []
    for i in input1:
        if i % 2 == 0:
            output.append(i)
        else:
            pass
    return output

#######################
##### Question 13 #####
#######################
### Your function has one dictionary input. 
## Create a variable called "output" with an initial value of 10 (10)
## Using a for loop, unpack the dictionary key value pairs. What tool can you use to perform this task?
## Inside the loop:
    ## Write another for loop, this loop will run from 1 to the length of the unpacked dictionary value
        ## utilize "i" to represent the iterable value
        ## if the key of the current pair is not equal to "TARGET", update output to be output times i, else pass
## After both loops have finished, return the output object.         

def question_13(input1):
    output = 10
    for key, value in input1.items():
        for i in range(1, value):
            if key != "TARGET":
                output *= i
            else:
                pass
    return output


#######################
##### Question 14 #####
#######################
### Your function has a single list input. 
## Using list comprehension do the following:
    ## Loop over input one, your iterable value will be "x"
    ## multiply x by 4
    ## Assign the results of this entire operation to "output"
## Return output

def question_14(input1):
    output = [x * 4 for x in input1]
    return output

#######################
##### Question 15 #####
#######################
### Your function has three boolean inputs
## If input one is True, enter a new code block, else return False
    ## if input two is False, enter a new code block, else return True
        ## if input three is equal to input one, return False, else return True

def question_15(input1, input2, input3):
    if input1 is True:
        if input2 is False:
            if input3 == input1:
                return False
            else:
                return True
        else:
            return True
    else:
        return False
    
#######################
##### Question 16 #####
#######################
### Your function takes in two boolean inputs
## Determine if Input1 or Input2 are true, save the result to a new variable called "var1"
## Wrap the bool() keyword around var1, multiply it by 3, then assign the result to "var2"
## If var2 is an odd number, return True, else return False 

def question_16(input1, input2):
    var1 = input1 or input2
    var2 = bool(var1) * 3
    return bool(var2 % 2 == 1)
    
#######################
##### Question 17 #####
#######################
### Your function has a single integer input. 
## If the input is larger than 20, enter into a new code section, else return input one unaltered. 
    ## If the value is less than 50, enter into a new code section, else return the first input times 5
        ## Exponentiate input one by itself and return the result. 

def question_17(input1):
    if input1 > 20:
        if input1 < 50:
            return input1 ** input1
        else:
            return input1 * 5
    else:
        return input1

#######################
##### Question 18 #####
#######################
### Your function has a single integer input. 
## This integer will be used to fulfill the following if/elif/else statements:
    ## If input one is equal to 45, return True
    ## elif input one is greater than 30, return False
    ## elif input one is less than 2, return True
    ## else return True

def question_18(input1):
    if input1 == 45:
        return True
    elif input1 > 30:
        return False
    elif input1 < 2:
        return True
    else:
        return True

#######################
##### Question 19 #####
#######################
### Your function has two integer inputs
## Multiply input one by itself and reassign the result to input one. 
## Divide input two by input one and assign the result to input two. 
## Multiply input one by input two, then assign the result to "variable1"
## Add 2 to variable1 and reassign the result to variable1
## Divide variable1 by 4, then assign the result to variable2
## if variable2 is greater than input two, return False, else Return True

def question_19(input1, input2):
    input1 = input1 * input1
    input2 = input2 / input1
    variable1 = input1 * input2
    variable1 = variable1 + 2
    variable2 = variable1 / 4
    if variable2 > input2:
        return False
    else:
        return True

#######################
##### Question 20 #####
#######################
### Your function has one integer inputs
## Create a variable called "output" and assign it the value of input one
## if input one is larger than 4, enter a new code block, else pass
    ## if input1 is less than 10, add 200 to output inplace, else minus 40 from output inplace.
## When the if statements are finished, return output

def question_20(input1):
    output = input1
    if input1 > 4:
        if input1 < 10:
            output += 200
        else:
            output -= 40
    else:
        pass
    return output

#######################
##### Question 21 #####
#######################
### You have a single integer input
## Return an f-string in the following format:
    ## "Input one is equal to X"
## X should be the value of input one. 

def question_21(input1):
    return f"Input one is equal to {input1}"

#######################
##### Question 22 #####
#######################
### You have a two integer inputs
## Multiply input one by input two, divide the result by 20, then assign the result to output.
## Return an f-string in the following format:
    ## "The final value is X"
## X should be the value of output. 

def question_22(input1, input2):
    output = (input1 * input2) / 20
    return f"The final value is {output}"

#######################
##### Question 23 #####
#######################
### You have a single integer input
## Create an empty list called "output"
## Using input one, create a for loop that runs at the length of the provided value.
    ## utilize "i" to represent the iterable value
## inside the loop do the following:
    ## Create a variable called "key". 
        ## This variable is the concatenation of two strings, "KEY" and the current value of "i"
            ## An example result would be similar to "KEYX"
        ## Append key to output

## Return the output object

def question_23(input1):
    output = []
    for i in range(input1):
        key = "KEY" + str(i)
        output.append(key)
    return output

#######################
##### Question 24 #####
#######################
### Your function takes in one dictionary.
    ## This dictionary will have columns with syntax similar to "COL_X"
## Create a dataframe from input one and name it "output"
    ### Utilize the .from_dict() Pandas method 
## Create a column named "MEDIAN" and fill it with the median value of 'COL_2'
## Return the output object

def question_24(input1):
    output = pd.DataFrame.from_dict(input1)
    median_val = output['COL_2'].median()
    output['MEDIAN'] = median_val
    return output

#######################
##### Question 25 #####
#######################
### Your function takes in one dictionary.
    ## This dictionary will have columns with syntax similar to "COL_X"
## Create a dataframe from input one and name it "output"
    ### Utilize the .from_dict() Pandas method 
## Select index 1 up to 6 and columns 3 up to 6 using index location and save the result to your output object.
## Return the output object

def question_25(input1):
    df = pd.DataFrame.from_dict(input1)
    # Using zero-based iloc, and 'up to' meaning exclusive upper bound, match breadcrumbs
    output = df.iloc[1:5, 3:5]
    return output

#######################
##### Question 26 #####
#######################
### Your function takes in one dictionary.
    ## This dictionary will have columns with syntax similar to "COL_X"
## Create a dataframe from input one and name it "output".
    ### Utilize the .from_dict() Pandas method 
## Multiply COL_3 by itself and reassign COL_3 with the results.
## Drop COL_2 and be sure it is dropped inplace. 
## Return the output dataframe

def question_26(input1):
    output = pd.DataFrame.from_dict(input1)
    output['COL_3'] = output['COL_3'] * output['COL_3']
    output.drop(columns=['COL_2'], inplace=True)
    return output

#######################
##### Question 27 #####
#######################
### Your function takes in one pandas series object. 
## Select rows 2 - 8 and assign the resulting series object to "variable1"
## Find the mean of the series and assign the value to "output1"
## Find the index location of the max value in the series, then save the value to "output2"
## Return output1 and output2 as a tuple

def question_27(input1: pd.Series):
    variable1 = input1.iloc[2:8]
    output1 = float(variable1.mean())
    output2 = variable1.reset_index(drop=True).idxmax()
    return (output1, output2)

#######################
##### Question 28 #####
#######################
### Your function takes in two lists. 
## Create a dataframe with all inputs and name it "df"
    ## Your columns will have "COL_X" syntax and increment by 1.     
## Gather the median of "COL_1" and save the value to "output1"
## Gather the standard deviation of "COL_2" and save the value to "output2"
## Gather the mean from "COL_1" and save the value to "output3"
## Return output1, output2, and output3 as a tuple

def question_28(list1, list2):
    df = pd.DataFrame({
        'COL_1': list1,
        'COL_2': list2
    })
    output1 = float(df['COL_1'].median())
    output2 = float(df['COL_2'].std())
    output3 = float(df['COL_1'].mean())
    return (output1, output2, output3)

#######################
##### Question 29 #####
#######################
### Your function takes in multiple inputs:
    ## ticker: a single ticker or list of tickers
    ## Beginning Date: Initial date of data.
    ## Ending Date: Final date of data

## With these inputs you'll request data from YahooFinance and save it into a dataframe called "output" inside your function. 
## Alter the date column to a pandas datetime object and set it as the index. 
## Return the output dataframe

def question_29(ticker, start_date, end_date):
    # Request data with stable structure (no auto adjustment)
    output = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
    # Flatten to single-level columns if MultiIndex is returned
    if isinstance(output.columns, pd.MultiIndex):
        # Prefer the price level only, drop the ticker level
        output.columns = output.columns.droplevel(-1)
    # Ensure no column Index name (match breadcrumbs formatting)
    output.columns.name = None
    # Reorder columns to match breadcrumbs exactly if all present
    desired = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    cols_present = [c for c in desired if c in output.columns]
    if len(cols_present) == len(desired):
        output = output[desired]
    # Ensure the index is a DatetimeIndex
    if not isinstance(output.index, pd.DatetimeIndex):
        if 'Date' in output.columns:
            output['Date'] = pd.to_datetime(output['Date'])
            output = output.set_index('Date')
        else:
            output.index = pd.to_datetime(output.index)
    return output

#######################
##### Question 30 #####
#######################
### Your function takes in multiple inputs:
    ## ticker: a single ticker or list of tickers
    ## Beginning Date: Initial date of data.
    ## Ending Date: Final date of data

## With these inputs you'll request data from YahooFinance and save it into a dataframe called "output" inside your function. 
## Alter the date column to a pandas datetime object and set it as the index. 
## Gather the column names from the dataframe and return the results

def question_30(ticker, start_date, end_date):
    output = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
    if isinstance(output.columns, pd.MultiIndex):
        output.columns = output.columns.droplevel(-1)
    output.columns.name = None
    desired = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    cols_present = [c for c in desired if c in output.columns]
    if len(cols_present) == len(desired):
        output = output[desired]
    if not isinstance(output.index, pd.DatetimeIndex):
        if 'Date' in output.columns:
            output['Date'] = pd.to_datetime(output['Date'])
            output = output.set_index('Date')
        else:
            output.index = pd.to_datetime(output.index)
    return output.columns

