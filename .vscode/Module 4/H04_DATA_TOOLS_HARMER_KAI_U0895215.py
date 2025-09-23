student_name = "HARMER_KAI_U0895215"

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

def question_1(input1: int, input2: int, input3: int):
    arr = np.array([input1, input2, input3])
    return arr  

######################
##### Question 2 #####
######################
### Your function has two integer inputs
## Input one is your row count and input two is your column count. 
## Return the matrix. 

def question_2(rows: int, cols: int):
    mat = np.ones((rows, cols))
    return mat   

######################
##### Question 3 #####
######################
### Your function takes in two arrays.
## Add two to each array value
## Multiply input one by input two and return the result. 

def question_3(arr1: np.ndarray, arr2: np.ndarray):
    a1 = arr1 + 2
    a2 = arr2 + 2
    result = a1 * a2
    return result   

######################
##### Question 4 #####
######################
### Your function has a single array input. 
## Gather the max value from the array and assign it to a new variable called "max_value"
## Gather the index location of the max value and assign it to a new variable called "max_value_index"
## Return max_value and max_value_index as a tuple

def question_4(arr: np.ndarray):
    max_value = int(np.max(arr))
    max_value_index = int(np.argmax(arr))
    return (max_value, max_value_index)   

######################
##### Question 5 #####
######################
### Your function takes in a single array input. 
## Apply the natural logarithm to the array and reassign the results to input one.
## Multiply input one by itself and return the result. 

def question_5(arr: np.ndarray):
    arr = np.log(arr)
    result = arr * arr
    return result   

######################
##### Question 6 #####
######################
### Your function takes in a single array input. 
## Derive the mean, median, and standard deviation of input one, then assign each to a new variable. 
## Return the mean, median, and standard deviation of the array as a tuple. 
def question_6(arr: np.ndarray):
    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    std_val = float(np.std(arr))
    return (mean_val, median_val, std_val)   

######################
##### Question 7 #####
######################
### Your function takes in a single array input. 
## Gather the first 2 elements of the array and save them to variable called "first_2"
## Gather the value at the second index and assign the value to a variable called "index_2"
## Gather the last two values from input one and assign them to a variable called "last_2"
## Return first_2, index_2, and last_2 as a tuple

def question_7(arr: np.ndarray):
    first_2 = arr[:2]
    index_2 = int(arr[2])
    last_2 = arr[-2:]
    return (first_2, index_2, last_2)   

######################
##### Question 8 #####
######################
### Your function has three list inputs
## Build a dictionary object:
    ## Each key is to have the naming convention of  "COL_X", which increases by one (1) for each column. 
    ## Each list input will be a value for each column key.
## Create a dataframe with your dictionary object and return the result. 

def question_8(list1: list, list2: list, list3: list):
    data = {"COL_1": list1, "COL_2": list2, "COL_3": list3}
    df = pd.DataFrame(data)
    return df   

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

def question_9(list1: list, list2: list, list3: list):
    df = pd.DataFrame({"COL_1": list1, "COL_2": list2, "COL_3": list3})
    out1 = df.describe()
    out2 = float(df["COL_2"].mean())
    out3 = float(df["COL_1"].std())
    return (out1, out2, out3)    

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

def question_10(list1: list, list2: list, list3: list, list4: list):
    df = pd.DataFrame({"COL_1": list1, "COL_2": list2, "COL_3": list3, "COL_4": list4})
    shape = df.shape
    columns = df.columns
    index = df.index
    dtypes = df.dtypes
    return (shape, columns, index, dtypes)     

######################
##### Question 11 ####
######################
### Your function takes in a single dataframe input. 
## Group the dataframe by the first column ("COL_1") and return the mean. 

def question_11(df: pd.DataFrame):
    return df.groupby("COL_1").mean(numeric_only=True)    

######################
##### Question 12 ####
######################
### Your function takes in a single dataframe input. 
## Gather the value in row 1, column 2 and save it to a variable called "value1"
## Gather column 1 and save it to a variable called "col1"
## Gather the values from row 1 and save it to a variable called "row1"
## Gather the values from row 4, columns 1 AND 2 and save it to a variable called "multi"
## Return value1, col1, row1, and multi as a tuple

def question_12(df: pd.DataFrame):
    value1 = float(df.iloc[0, 1])
    col1 = df["COL_1"]
    row1 = df.loc[0]
    multi = df.loc[3, ["COL_1", "COL_2"]]
    return (value1, col1, row1, multi)      

######################
##### Question 13 ####
######################
### Your function takes in a single dataframe input. 
## Shift the dataframe by 4 and return the result

def question_13(df: pd.DataFrame):
    return df.shift(4)       

######################
##### Question 14 ####
######################
### Your function has two inputs, a dataframe and a string. 
## Replace all NA values with the input string.
## Return the results 

def question_14(df: pd.DataFrame, fill_value: str):
    return df.fillna(fill_value)       

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

def question_15(ticker: str, beginning_date, ending_date):
    # Request non-adjusted prices so 'Adj Close' is present and suppress progress output
    stock_data = yf.download(ticker, beginning_date, ending_date, auto_adjust=False, progress=False)
    # If MultiIndex columns are returned (e.g., by ticker), select the specified ticker
    if isinstance(stock_data.columns, pd.MultiIndex):
        try:
            if ticker in stock_data.columns.get_level_values(-1):
                stock_data = stock_data.xs(ticker, axis=1, level=-1)
            elif ticker in stock_data.columns.get_level_values(0):
                stock_data = stock_data.xs(ticker, axis=1, level=0)
        except Exception:
            pass
    stock_data.index = pd.to_datetime(stock_data.index)
    # Ensure expected OHLCV columns in conventional order if available
    cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    existing = [c for c in cols if c in stock_data.columns]
    result = stock_data[existing]
    return result.tail(2)   
