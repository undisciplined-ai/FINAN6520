# Imports 
import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt

####################################
######### NUMPY and PANDAS #########
####################################

################## NUMPY ##################

### Vectors and Matrices

a_list = [1,2,3]
np.array(a_list)

a_matrix = [[1,2,3],[4,5,6],[7,8,9]]
np.array(a_matrix)

### Built in Methods
# Vector
np.zeros((5))
# Matrix
np.zeros((5,5))

np.linspace(0,100,50)

np.random.rand(10)

# Random Uniform
np.random.rand(5,5)

## Random Normal 
np.random.randn()

an_array = np.arange(25)
random_array = np.random.randint(0,50,10)

an_array

random_array

an_array.reshape(5,5)

an_array.reshape(25,1)
# an_array.reshape(25,2)
# This cannot be performed beacuse the total value count (25) is not divisible by the 
# product of the reshape demensions, (25,2), is

random_array.max()

random_array.argmax()

random_array.min()

random_array.argmin()

## Indexing

an_array

an_array[8]

# Slicing
an_array[1:5]

new_matrix = an_array.reshape(5,5)

new_matrix[1]

new_matrix[3][1]

new_matrix[:2] # Up to row at index 1

## Math Operations
#### ARRAYS MUST BE THE SAME LENGTH FOR THIS TO BE POSSIBLE 
new_array = np.arange(0,10)

new_array - new_array

new_array + new_array

new_array * new_array

new_array / new_array

new_array**3

np.exp(new_array)

np.log(new_array)

np.sin(new_array)

np.cos(new_array)


## Basic Statistics

np.mean(new_array)

np.median(new_array)

np.std(new_array)


################## PANDAS ##################


## Series Objects

col_labels = ['col_1','col_2','col_3']
row_labels = ['a','b','c']
my_list = [10,20,30]
ser_array = np.array([10,20,30])
vals_cols_dict = {'a':10,'b':20,'c':30}

pd.Series(data=my_list)

pd.Series(data=ser_array)

pd.Series(my_list,row_labels)

pd.Series(vals_cols_dict)

pd.Series(data=row_labels)

pd.Series(data = row_labels,index = ['index_0', 'index_1','index_2'])

## DataFrames
np.random.seed(47)
df = pd.DataFrame(np.random.randn(3,3),index=row_labels,columns=col_labels)

df['col_2']

df[['col_1','col_2']]

df['New_Col'] = df['col_1'] + df['col_2']

df.drop('New_Col',axis=1)

## Inplace
df.drop('New_Col',axis=1,inplace=True)


df.drop('a',axis=0)

## DataFrame Indexing

df.loc['a']

df.iloc[0]

df.loc['a','col_2']

df.loc[['a','b'],['col_2','col_3']]

## Conditional Selection
df>0 # Displays only boolean values of the dataframe

df[df>0]['col_1'] 

df[(df > 0) & (df > 1.5)]


## Indexing Tricks
df.reset_index()

new_index = ['a','new','index']

df['new_index'] = new_index

df.set_index('new_index')

df.set_index('new_index',inplace=True)

### Groupby
data = {'Company':['AAPL','AAPL','SQ','SQ','DIS','DIS'],
       'Revenue':[200,120,340,124,243,350]}
df = pd.DataFrame(data)
df

df.groupby('Company').mean()

df.groupby('Company').describe()

df.groupby('Company').describe().loc['AAPL']

# DataFrame Operations 

df['Company'].value_counts()

df['Company'].unique()

df['Company'].nunique()

df['Revenue'].sum() 

df.sort_values(by='Company')

## Applying Functions to Frames

def times2(x):
    return x*2


df['Revenue'].apply(times2)

## Lambda functions are "one-off" functions meant to only be used once. 
## If you are going to use the operation again make a function
df['Revenue'].apply(lambda x: x * 2)

# NAs and Fills

df = pd.DataFrame({'A':[1,2,np.nan],
                  'B':[5,np.nan,np.nan],
                  'C':[1,2,3]})

df.dropna()

df.dropna(thresh=2)


df.fillna(value='FILL VALUE')

## Shifting Data
df.shift(1)

df.shift(2,fill_value='FILL VALUE')

##################################
######### DATA GATHERING #########
##################################
securities = ['MSFT','AAPL','NVDA'] 

# Dates
beginning_date = '2015-1-1'
ending_date = '2022-12-31'

## Yfinance
stock_data = yf.download(securities,beginning_date,ending_date)
stock_data.index = pd.to_datetime(stock_data.index.date).copy()
stock_data.head()

# # Basic stats of all seurities
stock_data.describe()

stock_data.info()

adj_close_data = stock_data['Adj Close'].copy()

# stock_data['MSFT']
adj_close_data.plot()

### TINGO
def tiingo_api(user_key,tickers,b_date,e_date,freq='Daily'):
    from tiingo import TiingoClient
    config = {}
    config['session'] = True
    config['api_key'] = user_key
    # Initialize
    client = TiingoClient(config)

    if isinstance(tickers, list):
        data_store = {}
        for ticker in tickers:
            data = pd.DataFrame(client.get_ticker_price(ticker,fmt='json',
                                            startDate=b_date,endDate=e_date,
                                            frequency=freq))
            index = data['date'].apply(lambda x: dt.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))
            data_store[ticker] = data

        panel_data = pd.concat(data_store).unstack(level=0)
        panel_data = panel_data.set_index(index)
        panel_data.drop(['date','adjOpen','adjLow','adjHigh','adjVolume','divCash','splitFactor'],
                        axis=1,inplace=True)
        cols = {'close':'Close','open':'Open',
               'high':'High','low':'Low',
               'adjClose':'Adj Close','volume':'Volume'}
        panel_data.rename(columns=cols,inplace=True)
        return panel_data
    else:
        data = pd.DataFrame(client.get_ticker_price(tickers,fmt='json',
                                        startDate=b_date,endDate=e_date,
                                        frequency=freq))
        index = data['date'].apply(lambda x: dt.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ"))

        data = data.set_index(index)
        data.drop(['date','adjOpen','adjLow','adjHigh','adjVolume','divCash','splitFactor'],
                        axis=1,inplace=True)
        cols = {'close':'Close','open':'Open',
               'high':'High','low':'Low',
               'adjClose':'Adj Close','volume':'Volume'}
        data.rename(columns=cols,inplace=True)
        return data
    

tiingo_data = tiingo_api("260bd51f909ce128a2d5ecf946f9033a51b8a471",securities,beginning_date,ending_date)

tiingo_data['Adj Close']


##################################
######### VISUALIZATION ##########
##################################

##### MATPLOTLIB #####

## Basic plotting
x = np.linspace(0, 7, 14)
y = x ** 2


plt.plot(x, y, 'g') # 'g' is the color green

plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.title('Overall Title')
# plt.show()


# plt.subplot(nrows, ncols, plot_number)
plt.subplot(1,2,1)
plt.plot(x, y, 'g-')
plt.subplot(1,2,2)
plt.plot(y, x, 'g-+')

# plt.subplot(nrows, ncols, plot_number)
plt.subplot(1,2,1)
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.title('First Title')
plt.plot(x, y, 'g-')

plt.subplot(1,2,2)
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.title('Seconed Title')
plt.plot(y, x, 'r*-')


#### SEE NOTES ####
### MatPlot Object-Oriented Methods

# Create Figure (empty canvas) of 1 row and 1 column (default)
fig, ax = plt.subplots()

fig = plt.figure()
# Add set of axes to figure
axes = fig.add_axes([0.5, 0.5, 2, 1]) # left, bottom, width, height
axes.plot(x, y, 'b')

# Axes assignments require the usage of set_ operators
# This is how the previous method labeled and axis: plt.xlabel('X Axis')

axes.set_xlabel('X Label')
axes.set_ylabel('y Label')
axes.set_title('Overall Title')

# Creates blank canvas
fig = plt.figure()

axes1 = fig.add_axes([0.1, 0.1, 2, 0.8]) # main axes
axes2 = fig.add_axes([1.5, 0.25, 0.5, 0.25]) # inset
# axes left, bottom, width, height

# Figure 1
axes1.plot(x, y, 'black') # full color inputs work as well
axes1.set_xlabel('X_axes1')
axes1.set_ylabel('Y_axes1')
axes1.set_title('Figure 1')

# Figure 2
axes2.plot(y, x, 'g')
axes2.set_xlabel('X_axes2')
axes2.set_ylabel('Y_axes2')
axes2.set_title('Figure 2')

#### Save Figures
fig.savefig("single.png",bbox_inches='tight')


### Legends

fig = plt.figure()

ax = fig.add_axes([0,0,1,1])

ax.plot(x, x**4,color='blue', label="x**4")
ax.plot(x, x**5,color='green', label="TEST")
ax.legend()

###### Extensive example of the many options available for plotting. 
fig, ax = plt.subplots(figsize=(20,4)) # Easily assign the size of the figure with figsize=(width,height)

ax.plot(x, x+1, color="#474747", linewidth=0.25)
ax.plot(x, x+2, color="r", linewidth=0.50)
ax.plot(x, x+3, color="#000066", linewidth=1.00)

# possible linestype options ‘-‘, ‘–’, ‘-.’, ‘:’, ‘steps’
ax.plot(x, x+4, color="orange", lw=4, linestyle='-.')
ax.plot(x, x+5, color="red", lw=5, ls='-.')
ax.plot(x, x+6, color="#330066", lw=6, ls='--')
ax.plot(x, x+7, color="#990055", lw=6, ls=':')

##### PANDAS PLOTTING #####

# Gathering Data
stock_data = yf.download(['AAPL','SPY','MSFT'],'2014-12-31','2023-08-30')
stock_data.index = pd.to_datetime(stock_data.index.date).copy()
stock_data = stock_data['Adj Close']
stock_data.head()

stock_data.head()
# Simple .plot() function
stock_data.plot()

# .plot() with specified X with the INDEX naturally assuming the X 
stock_data.plot(y='AAPL')

# Resizing the output with multiple columns
# Notice the list object in the Y assignment
stock_data.plot(y=['AAPL','MSFT'],figsize=(12,6))

# Formatting alterations
# Matplotlib Colormaps: https://matplotlib.org/examples/color/colormaps_reference.html
# stock_data.plot()
stock_data.plot(y=['AAPL','MSFT','SPY'],figsize=(12,6),colormap='copper')

# Subplotting each variable in the dataset
stock_data.plot(subplots=True,figsize=(16,8),colormap='Set2')