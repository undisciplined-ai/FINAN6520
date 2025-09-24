#### THIS IS OUR SCRIPT TO RUN TARGET FUNCTIONS

import math
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import timedelta
    
## Import Modules in the same directory
## Display this power to then use the beta calculator in the homework. 
from L05_IMPLEMENTATION import security_time_gathering, gather_data, continuous_returns, beta_calculator , portfolio_value_tracking

########################### USAGE OF BETA CALCULATOR #####################################

# stock_data = gather_data()
# filtered_stocks = continuous_returns(stock_data, frequency="M")
# beta_calculator(filtered_stocks)


# ########################### USAGE OF PORTFOLIO VALUE TRACKING #####################################

securities = ['JPM','AAPL','NVDA','GE']
stock_data = yf.download(securities,'2015-01-01','2024-02-05')
stock_data.index = pd.to_datetime(stock_data.index.date).copy()
stock_data = stock_data['Adj Close']

# # * Create **investment_total** variable of $1,000,000
# # * Create **weights** list object
# #     * Allocate the portfolio accordingly: 30%, 40%, and 30%.
# #     * **note**: Can a portfolio be allocated above 100%?

investment_total = 1000000 

weights = [.3,.4,.2,.1]

investment_dollar_amounts = []
for i in weights:
    # print(investment_total * i)
    investment_dollar_amounts.append(investment_total * i)

### Run our target function
equity_data, portfolio_metadata = portfolio_value_tracking(stock_data, weights, investment_dollar_amounts)

fig, ax = plt.subplots(2,1, figsize=(15,15))

fig.set_facecolor('#BEBEBE')
ax[0].set_facecolor('#BEBEBE')
ax[1].set_facecolor('#BEBEBE')


equity_data['Total_Equity'].plot(colormap='inferno', ax=ax[0])
ax[0].set_title('Total Portfolio Equity')
## Set Y axis Values to $
ax[0].yaxis.set_major_formatter('${x:,.0f}')
## Alter Label Location
ax[0].yaxis.set_tick_params(which='major', labelcolor='black',
                            labelleft=False, labelright=True)

equity_data.loc[:, ~equity_data.columns.isin(['Total_Equity'])].plot(colormap='magma', ax=ax[1])
ax[1].set_title('Individual Ticker Equity')
## Set Y axis Values to $
ax[1].yaxis.set_major_formatter('${x:,.0f}')
## Alter Label Location
ax[1].yaxis.set_tick_params(which='major', labelcolor='black',
                         labelleft=False, labelright=True)
## Set legend to left side of chart(s)
plt.legend(loc=2,facecolor='#BEBEBE')
plt.show();

## Output Portfolio Metadata
for key, data in portfolio_metadata.items():
    print()
    print(key)
    print('----------------')
    for attribute, value in data.items():
        print(f'{attribute} : {value}')