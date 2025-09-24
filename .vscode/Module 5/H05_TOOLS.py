
import math
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import timedelta, datetime



def continuous_returns(stock_data: pd.DataFrame, frequency: str) -> pd.DataFrame:
    ### Monthly sampling allows us to minimize the noise created by trading
    filtered_stocks=stock_data.resample(frequency).last()

    # Continuous Returns
    ## Taking the log of the month to month difference simulates normally distributed percentage changes
    ## Equity products are fat-tailed, meaning they do not have a standard distribution
    ## Also, we are measuring returns over time. 
    ## Securities move up and down over each period. But a decrease of 5% on day and increase of 5% the next does
    ## not result in the same value, i.e. we cannot add the two days together to produce the total return. 
    ## Log returns do not have that issue, they are additive and the sum of any two periods is the total return 
    ## Log returns are also normally distributed, which then allows us to generate traditional statistics. 

    ## We must alter our data to a format we can utilize for statistical inference.
    ## Shift slides the dataframe down by 1, then the original dataframe is comparing t to t-1
    filtered_stocks = np.log(filtered_stocks/filtered_stocks.shift(1))
    ## Drop any nulls, generally only the first row since this is a period/period comparison. 
    filtered_stocks = filtered_stocks.dropna()
    # Return the results
    return filtered_stocks

def beta_calculator(return_df: pd.DataFrame) -> float:
    ## Gather SPY returns as a series object
    market = return_df['SPY'].copy()
    ## Gather target security returns as a series object
    focus_security = return_df.loc[:, ~return_df.columns.isin(['SPY'])].iloc[:,0].copy()
    
    ## Covariance matrix of market and focus security
    ## Select first row, second column is the covariance value. 
    ## Round the result to the fifth decimal place. 
    covariance = round(float(np.cov(market, focus_security)[0][1]),5)
    ## Generate Security Beta
    beta = covariance/ np.var(market)
    # Return Beta
    return beta
    
def gather_risk_free() -> float:
    ## Gather 10 year yield index
    panel_data = yf.download('^TNX','2023-08-01',datetime.today())
    ### Select Only Adjusted Close values. 
    stock_data = panel_data['Adj Close']
    # Return most recent yield value. 
    return stock_data.iloc[-1]

def capm(market_return: float, risk_free_rate: float, beta: float) -> float:
## The expected return of a security is equal to the risk-free return plus a risk premium, which is based on the beta of that security. 
    return risk_free_rate + beta * (market_return - risk_free_rate)
