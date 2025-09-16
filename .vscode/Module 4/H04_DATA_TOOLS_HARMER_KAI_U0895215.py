student_name = "LAST_FIRST_UNID"

import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime 

######################
##### Question 1 #####
######################

### Your function has three integer inputs.
## Create a Numpy array object, then return it. 

def question_1():
    return   

######################
##### Question 2 #####
######################
### Your function has two integer inputs
## Input one is your row count and input two is your column count. 
## Return the matrix. 

def question_2():
    return   

######################
##### Question 3 #####
######################
### Your function takes in two arrays.
## Add two to each array value
## Multiply input one by input two and return the result. 

def question_3():
    return   

######################
##### Question 4 #####
######################
### Your function has a single array input. 
## Gather the max value from the array and assign it to a new variable called "max_value"
## Gather the index location of the max value and assign it to a new variable called "max_value_index"
## Return max_value and max_value_index as a tuple

def question_4():
    return   

######################
##### Question 5 #####
######################
### Your function takes in a single array input. 
## Apply the natural logarithm to the array and reassign the results to input one.
## Multiply input one by itself and return the result. 

def question_5():
    return   

######################
##### Question 6 #####
######################
### Your function takes in a single array input. 
## Derive the mean, median, and standard deviation of input one, then assign each to a new variable. 
## Return the mean, median, and standard deviation of the array as a tuple. 
def question_6():
    return   

######################
##### Question 7 #####
######################
### Your function takes in a single array input. 
## Gather the first 2 elements of the array and save them to variable called "first_2"
## Gather the value at the second index and assign the value to a variable called "index_2"
## Gather the last two values from input one and assign them to a variable called "last_2"
## Return first_2, index_2, and last_2 as a tuple

def question_7():
    return   

######################
##### Question 8 #####
######################
### Your function has three list inputs
## Build a dictionary object:
    ## Each key is to have the naming convention of  "COL_X", which increases by one (1) for each column. 
    ## Each list input will be a value for each column key.
## Create a dataframe with your dictionary object and return the result. 

def question_8():
    return   

######################
##### Question 9 #####
######################
### Your function has three list inputs
## Build a dictionary object:
    ## Each key is to have the naming convention of  "COL_X", which increases by one (1) for each column. 
    ## Each list input will be a value for each column key.
## Create a dataframe with your dictionary object and save it to a variable called "df"
## Generate the description of the dataframe and assign it to "out1"
## Generate the Mean of column 2 and assign it to "out2"
## Generate the standard deviation of column 1 and assign it to "out3"
## Return out1, out2, and out3 as a tuple

def question_9():
    return    

######################
##### Question 10 ####
######################

### Your function has four list inputs
## Build a dictionary object:
    ## Each key is to have the naming convention of  "COL_X", which increases by one (1) for each column. 
    ## Each list input will be a value for each column key.
## Create a dataframe with your dictionary object and save it to a variable called "df"
## Gather the shape of the dataframe and assign it to "shape"
## Gather the columns and assign them to "columns"
## Gather the index and assign it to "index"
## Gather the data types of all columns and assign them to "dtypes"
## Return shape, columns, index, and dtypes as a tuple.

def question_10():
    return     

######################
##### Question 11 ####
######################
### Your function takes in a single dataframe input. 
## Group the dataframe by the first column ("COL_1") and return the mean. 

def question_11():
    return    

######################
##### Question 12 ####
######################
### Your function takes in a single dataframe input. 
## Gather the value in row 1, column 2 and save it to a variable called "value1"
## Gather column 1 and save it to a variable called "col1"
## Gather the values from row 1 and save it to a variable called "row1"
## Gather the values from row 4, columns 1 AND 2 and save it to a variable called "multi"
## Return value1, col1, row1, and multi as a tuple

def question_12():
    return      

######################
##### Question 13 ####
######################
### Your function takes in a single dataframe input. 
## Shift the dataframe by 4 and return the result

def question_13():
    return       

######################
##### Question 14 ####
######################
### Your function has two inputs, a dataframe and a string. 
## Replace all NA values with the input string.
## Return the results 

def question_14():
    return       

######################
##### Question 15 ####
######################
### Your function has three inputs:
    ## Company ticker (string)
    ## Beginning date (datetime)
    ## Ending date (datetime)
## Use the inputs to gather stock data using yfinance, save the results to "stock_data"
## Update the index to be pandas datetime data type. 
## Return the last two rows of the dataframe. 

def question_15():
    return   
