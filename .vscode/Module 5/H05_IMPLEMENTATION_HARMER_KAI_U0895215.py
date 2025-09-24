

student_name = "HARMER_KAI_U0895215"

import numpy as np
import yfinance as yf
from H05_TOOLS import continuous_returns, beta_calculator, gather_risk_free, capm
######################
##### Question 1 #####
######################
### Future Value Function
### Your function takes in four inputs
## Present value
## Periods - As in the interest payment period (Semi-Annual, Quarterly, etc.)
## Time in form of years
## Interest rate in whole percentages - Would you need to alter this?
## Round all output to the fourth decimal. 

## You'll want to handle all of the inputs to have a proper function. Consider how periods, time, and rate interact. 

## Future Value Equation
# fv = pv * (1 + i/n)^(n*t)

def question_1(present_value, periods, time, rate):
    i = rate / 100.0
    n = periods
    t = time
    fv = present_value * (1 + i / n) ** (n * t)
    return round(float(fv), 2)

######################
##### Question 2 #####
######################
### Present Value Function
### Your function takes in four inputs
## Future value
## Periods - As in the interest payment period (Semi-Annual, Quarterly, etc.)
## Time in form of years
## Interest rate in whole percentages. - Would you need to alter this?
## Round all output to the fourth decimal. 

## You'll want to handle all of the inputs to have a proper function. Consider how periods, time, and rate interact. 

## Present Value Equation
# pv = fv/(1+i/n)^(n x t)

def question_2(future_value, periods, time, rate):
    i = rate / 100.0
    n = periods
    t = time
    pv = future_value / ((1 + i / n) ** (n * t))
    return round(float(pv), 2)

######################
##### Question 3 #####
######################
### Utilize the Beta Calculator to generate Expected Return for a target security
## Import the tools from H05_TOOLS.py
    ### You'll need the continuous return, beta, gather risk free, and capm functions. 
## Using those materials do the following:
## Your only function input should be an equity ticker, e.g. AAPL
## Gather data for a target equity ticker and the market (SPY), then generate continuous returns on both. 
    ## Consider how you would gather both SPY and your target value efficiently 
    ## Beginning date is 2019-12-31 and ending date is 2024-01-01
    ## You'll be working with monthly continuous returns. 
## Generate the Expected Market Return -- This is not the cumulative return we utilized in the lecture. 
    ## This is the average return over the period.
    ## The resulting value should be altered to a whole percent and be annualized. 
## Utilize provided functions to gather the risk-free rate
## Generate the beta value of the target security. 
## Using all of these materials, utilize the CAPM forumula to generate an expected return for the target product. 
    ### CAPM Formula
    ## Risk Free + [Beta * (Market Expected Return - Risk Free)]
## Return the expected return value rounded to the fourth decimal.

def question_3(ticker):
    start = '2019-12-31'
    end = '2024-01-01'
    panel = yf.download([ticker, 'SPY'], start=start, end=end, auto_adjust=False, progress=False)
    if 'Adj Close' in panel.columns:
        prices = panel['Adj Close']
    else:
        prices = panel['Close']
    returns = continuous_returns(prices, 'M')
    market_exp = float(returns['SPY'].mean() * 12 * 100)
    beta = float(beta_calculator(returns))
    try:
        rf = float(gather_risk_free())
    except Exception:
        tnx = yf.download('^TNX', start='2023-08-01', auto_adjust=False, progress=False)
        if 'Adj Close' in tnx.columns:
            rf = float(tnx['Adj Close'].iloc[-1])
        elif 'Close' in tnx.columns:
            rf = float(tnx['Close'].iloc[-1])
        else:
            rf = float(tnx.iloc[-1, -1])
    expected = capm(market_exp, rf, beta)
    return round(float(expected), 2)

######################
##### Question 4 #####
######################
### Write a function to provide the monthly loan payment of a given set of variables
## you'll have 3 inputs
## Rate - To be entered as a whole number and handled appropriately
## Years - Count of years for the lifetime of the mortgage
## Principal - Total $ amount being borrowed. 
## Round all output the the fourth decimal.

# Payment Formula
# principal x ((rate/100/12) x 1 + (rate/100/12)^(years x 12)) / ((1 + rate/100/12)^(years x 12)-1)

def question_4(rate, years, principal):
    r = rate / 100.0 / 12.0
    n = int(years) * 12
    payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    return round(float(payment), 2)