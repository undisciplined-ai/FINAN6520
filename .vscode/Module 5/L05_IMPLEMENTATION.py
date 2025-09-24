import math
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import timedelta
    
## This week is a conversation of "lets apply some programming knowledge to finance"
## You have learned a lot of tools over the last few weeks, now lets apply them to our domain. 
## "Implemenation" does not have to be "heres a massive set of repetative non-domain specific leetcode challenges"
## The value of this week is to display how we use code to think about finance centric topics as well as some leetcode stuff

########################### GENERATING BETA OF EQUITY PRODUCTS #####################################
## This is a user input focused stock beta calculator. Returns STD, Covar, Corr, and Beta related to SPY. 
## Beta is the measure of systematic risk of a security, in our case and equity product(s).
## Beta can be positive or negative. 
## The value of 1 represents the beta of a target market. 
## Values larger than 1 have more volatility than the market
## Values less than 1 mean they are less volatile than the market. 
## Negative beta values suggest oppostive movement of the market

## So, a beta of 1.5 means the security in question moves 50% more and in the same direction as the Market. 

# Beta Coefficient:
### RETURNS
# Covariance(Re, Rm)
# ---------------------
# Variance(Rm)

# Re - Return of Equity Product
# Rm - Return of Market
# Covariance - The relationship between two variables
    ## sum((x_i - x_hat)(y_i - y_hat))/ n-1
# Variance - The spread of values from their average
    ## (sum((x_i - x_hat)^2))/n - 1
    ## How far data is from the mean. 
    ## How wide or narrow our distribution of data is. 

#### DO NOT READ THIS ####
## Quick stats refresh 
## To derive the variance
## We find the average of the values (mu)
## subtract Mu from each value, square this result, then sum all the results. 
## We then divide the above sum by the count of our data points minus 1. 
## This gives us the variance of the sample. 
## If we take the square root of this value, we have the standard deviation of the sample. 

## Variance is the full dispersion of data points on hand
    ### The average of the squared differences from the mean
## Standard deviation is the degree to which the values are spread with respect to the mean. \
    ## Measure of typical distance of data points and the mean. 



###### REQUIREMENTS
### Goal:
## Create functions allowing us to calculate a security's beta. 
## We want to calculate beta for 1:n securities 

### Needs:
## We need te target security, and period of observation
    ## Ticker, beginning and ending dates. 
    ## Count of Securities, then the securities themselves. 

## Gather the target data based on our user inputs

## Calculate continuous returns of our target securities 

## Calculate Beta

def security_time_gathering():
    ### Will be a running function until we exit. 
    while True:
        try:
            ## Gather User Ticker Count
            sec_count = int(input('How many securities are you selecting? Please enter a number.\n:'))
            securities = []
            # Gather User Tickers
            for tickers in range(0,sec_count):
                    tick = input('Please enter a ticker\n: ').upper()
                    securities.append(tick)
            
            ## Display User inputs
            print(f'Here are the securities you selected\n{securities}')
            print('\n')

            input('Now you will assign your time periods. Ready to continue? Press enter.')
            ### Ask User for inital date value. 
            beginning_date = input('What date do you want to start from?\nNOTE: Enter (YYYY-MM-DD) Format\n: ')
            ## Error handle for bad date, we could be more complex, but for now we are ok. 
            if len(beginning_date) == 0:
                print('Bad date format. Try again.')            
                continue
            else:
                pass
            ## Ask user for final date value
            ending_date = input('What date do you want to end on?\nNOTE: Enter (YYYY-MM-DD) Format\n: ')
            ## Error handle for bad date, we could be more complex, but for now we are ok. 
            if len(ending_date) == 0:
                print('Bad date format. Try again.')
                continue
            else:
                pass
            ## Display chosen dates for the User. 
            print('Here are your dates.')
            print(f'Beginning Date: {beginning_date}')
            print(f'Ending Date: {ending_date}')
            input('Ready to continue? Press enter.')

            return beginning_date, ending_date, securities

        except ValueError:
            print('Bad Format. Try Again:')
            continue

def gather_data():
        ## Ask user for necessary data
        beginning_date, ending_date, securities = security_time_gathering()
        ## Adding in SPY
        ## This is our market benchmark. 
        securities.append("SPY")
        ## Download all data    
        panel_data = yf.download(securities,beginning_date,ending_date)
        ### Select Only Adjusted Close values. 
        stock_data = panel_data['Adj Close']

        ## Save file as CSV, but not necessary for our lecture. 
        # date_value = datetime.datetime.strftime(datetime.datetime.today(),format='%b-%d-%Y_%X')
        # file_name = 'stock_data/stock_data_'+date_value+".csv"
        # stock_data.to_csv(file_name) # Useful to not have to continually download the same portfolio
        return stock_data

### DISCUSS WHAT ADJ CLOSE VALUES ARE 
    ## They reflect dividends and stock splits

### DISCUSS CONT. RETURNS
    ## Taking the log of the month to month difference simulates normally distributed percentage changes
    ## Equity products are fat-tailed, meaning they do not have a standard distribution
    ## Also, we are measuring returns over time. 
    ## Securities move up and down over each period. But a decrease of 5% on day and increase of 5% the next does
    ## not result in the same value, i.e. we cannot add the two days together to produce the total return. 
    ## Log returns do not have that issue, they are additive and the sum of any two periods is the total return 
    ## Log returns resemble a normal distribution, which then allows us to generate traditional statistics. 

    ## We must alter our data to a format we can utilize for statistical inference.
    ## Shift slides the dataframe down by 1, then the original dataframe is comparing t to t-1

def continuous_returns(stock_data: pd.DataFrame, frequency: str) -> pd.DataFrame:
    ### Monthly sampling allows us to minimize the noise created by trading
    filtered_stocks=stock_data.resample(frequency).last()
    # Continuous Returns
    filtered_stocks = np.log(filtered_stocks/filtered_stocks.shift(1))
    ## Drop any nulls, generally only the first row since this is a period/period comparison. 
    filtered_stocks = filtered_stocks.dropna()
    # Return the results
    return filtered_stocks

def beta_calculator(return_df: pd.DataFrame) -> None:
    market = return_df['SPY']
    market_return = market.sum()
    ## Remove this to prevent any wonky calculations
    return_df.drop(columns=['SPY'],inplace=True)

    count_stocks = len(return_df.columns)
    return_list = []
    alpha_list = []
    security_list = []
    beta_list = []

    for i in range(0,count_stocks):
        column_val = i

        ## Gather series object from dataframe
        focus_security = return_df.iloc[:,column_val]
        # Save ticker name to list. 
        security_list.append(return_df.columns[column_val])

        ## Cumulative return
        security_return = focus_security.sum()
        return_list.append(security_return)
        ## Alpha value of return appended to list
        alpha_list.append(security_return - market_return)

        ## Covariance matrix of market and focus security
        ## Select first row, second column is the covariance value. 
        ## Round the result to the fifth decimal place. 
        covariance = round(float(np.cov(market, focus_security)[0][1]),5)
        ## Generate Security Beta
        beta = covariance / np.var(market)
        beta_list.append(beta)

    # Adding Market values to output lists
    security_list.append('Market')
    return_list.append(market_return)
    alpha_list.append(0)
    beta_list.append(1)

    beta_df = pd.DataFrame({'Beta': beta_list,
                            'Period Return': return_list,
                            'Period Alpha': alpha_list}, index=security_list)

    print('Given Period Beta Values\n------------------------------')
    print(beta_df)

########################### DEVELOPMENT OF PORTFOLIO VALUE TRACKING #####################################
##### Portfolio Value Tracking
## We want to know what a portfolio value looks like after an investment.
## Generally we focus on return values in some sort of percentage, but how could we see the dollar value over time?
## We'll build out a function to do just that for us using continuous returns


## What do we need?
# Share count, price of share at purchase, total principal value, and portfolio weights

## Once we have all that, we can move forward to generate a few things:
    # A function to generate continous returns. 
    # Need initial portfolio allocations based on share prices at t0
    # Once we have that, we can utilize continuous 

def portfolio_value_tracking(stock_data: pd.DataFrame, weights: list, investment_dollar_amounts: int) -> (pd.DataFrame, dict):
    ## Set up payload lists
    share_count = []
    initial_share_value = []
    equity_values = []
    security_names = [] 

    ## Loop over each security
    for i in range(0,len(stock_data.columns)):
        # Gather security 
        security_names.append(stock_data.columns[i])
        # Share amount possible for allocation
        ## Floor division provides the nearest whole number.
        share_count.append(investment_dollar_amounts[i] // float(stock_data.iloc[0][i]))
        # Single Share Value
        initial_share_value.append(float(stock_data.iloc[0][i]))
        # Total Equity based on potential share count and current share value
        equity_values.append(initial_share_value[i] * share_count[i])

    ## This is a dollar value         
    portfolio_equity = np.sum(equity_values)
    
    stock_returns = continuous_returns(stock_data,frequency='D')
    
    # Houses all security return values period by period
    equity_df = pd.DataFrame([pd.Series(equity_values, index=security_names)])
    equity_df['Date'] = None
    
    
    for j in range(0,len(stock_returns)): # For the row values
        
        row_returns = []
        for i in range(0,len(stock_returns.columns)): # For column values            
            # Generates the equity gain for the period
            ## Dollar value * continuous return
            row_returns.append(float(equity_df.iloc[j][i]) * math.exp(float(stock_returns.iloc[j][i])))

        # Adds all of curreutn period returns to the dataframe for later visualization
        inner_equity_df = pd.DataFrame([pd.Series(row_returns, index=security_names)])
        inner_equity_df['Date'] = stock_returns.iloc[j,:].name
        equity_df = pd.concat([equity_df, inner_equity_df])
            
    ## Gather Appropriate time values.
    ## Gathers the last day of the first month in equity_df. 
    print(equity_df)
    equity_df.iloc[0,-1] = equity_df.iloc[1,-1].replace(day=1) - timedelta(days=1)     

    equity_df = equity_df.set_index('Date')
    ## Sum by row
    equity_df['Total_Equity'] = equity_df.sum(axis=1)

    current_prices = stock_data.iloc[-1,:]

    meta_dict = {}
    for i, security in enumerate(security_names):    
        meta_dict[security] = {'SHARES': share_count[i],
                               'ENTRY_PRICE': round(initial_share_value[i],2),
                               'CURRENT_PRICE': round(current_prices.iloc[i],2),
                               'INITIAL_PORTFOLIO_VALUE': round(equity_df[security].iloc[0],2),
                               'CURRENT_PORTFOLIO_VALUE': round(equity_df[security].iloc[-1],2),
                               'INITIAL_PORTFOLIO_WEIGHT': round(weights[i]*100,2),
                               'CURRENT_PORTFOLIO_WEIGHT': round((equity_df[security].iloc[-1] / 
                                                                  equity_df['Total_Equity'].iloc[-1])*100,2),
                               'CUMULATIVE_RETURN': round(stock_returns[security].sum(),2),
                               'STANDARD_DEVIATION': round(stock_returns[security].std()*100,2)}

    meta_dict['TOTAL_PORTFOLIO'] = {'INITIAL_PORTFOLIO_VALUE': round(portfolio_equity,2),
                                    'OUTCOME_PORTFOLIO_VALUE': round(equity_df.iloc[-1,-1],2),
                                    'CUMULATIVE_RETURN': round(stock_returns.sum().sum(),2),
                                    'STANDARD_DEVIATION': round(stock_returns.sum(axis=1).std()*100,2)}
    print(equity_df)
    return equity_df, meta_dict


########################### HOMEWORK MATERIALS ###########################

### For your homework you will build out multiple tools
## I want you to build a game. You'll build out rock, paper, scissors to play by yourself. 
## You're going to utilize the Future / Present Value equations in a give set of functions.
## As a teaser for some content later, you'll write out a loan payment calculator.

## Part of the challenge this week is to do some digging on material. 
## We'll be working with the standard fv/pv equations
## Mortgage loans are all fixed rate equations for our purposes. 
## Essentially we will be writing the payment function in excel, but instead its a function in python. 
