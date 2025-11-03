import matplotlib.pyplot as plt

#### DO NOT ALTER ANY OF THIS ####
# neutral_color = '#847E70'
neutral_color = '#FFFFFF'
positive_color_one = '#8EA467'
positive_color_two = '#A5B685'
negative_color_one = '#EC4949'
negative_color_two = '#F17676'
negative_color_three = '#F5A4A4'
background_color = '#474747'

plt.style.use('dark_background')
plt.rcParams.update({'font.size': 15,})

fig = plt.figure(figsize=(15,10),facecolor=background_color)
ax1 = plt.subplot(3,2,(1,2),facecolor=background_color)
ax2 = plt.subplot(3,2,3,facecolor=background_color)
ax3 = plt.subplot(3,2,4,facecolor=background_color)
ax4 = plt.subplot(3,2,5,facecolor=background_color)
ax5 = plt.subplot(3,2,6,facecolor=background_color)

ax1.yaxis.set_major_formatter('{x:,.0f}')
ax2.yaxis.set_major_formatter('{x:,.0f}')
ax3.yaxis.set_major_formatter('{x:,.0f}')
ax4.yaxis.set_major_formatter('{x:,.0f}')
ax5.yaxis.set_major_formatter('{x:,.1f}')

##################################################
#################### HOMEWORK ####################
##################################################

from H10_PROPERTY_MODELING_SOLUTIONS import Portfolio

portfolio_inputs = [{'PROPERTY_VALUE':10000000,
                     'REGULAR_UNITS':5,
                     'LUXURY_UNITS':10,
                     'LOAN_YEARS':30,
                     'INTEREST_RATE':5,
                     'ESCALATION':2,
                     'DATE_OF_PURCHASE':2018},
                     {'PROPERTY_VALUE':3000000,
                     'REGULAR_UNITS':5,
                     'LUXURY_UNITS':5,
                     'LOAN_YEARS':30,
                     'INTEREST_RATE':7,
                     'ESCALATION':3,
                     'DATE_OF_PURCHASE':2023},
                     {'PROPERTY_VALUE':6000000,
                     'REGULAR_UNITS':0,
                     'LUXURY_UNITS':10,
                     'LOAN_YEARS':15,
                     'INTEREST_RATE':6,
                     'ESCALATION':3,
                     'DATE_OF_PURCHASE':2026},
                     {'PROPERTY_VALUE':5000000,
                     'REGULAR_UNITS':5,
                     'LUXURY_UNITS':5,
                     'LOAN_YEARS':30,
                     'INTEREST_RATE':5,
                     'ESCALATION':1.5,
                     'DATE_OF_PURCHASE':2030},
                     {'PROPERTY_VALUE':5000000,
                     'REGULAR_UNITS':0,
                     'LUXURY_UNITS':15,
                     'LOAN_YEARS':15,
                     'INTEREST_RATE':6,
                     'ESCALATION':3,
                     'DATE_OF_PURCHASE':2045}]

homework_portfolio = Portfolio(2018,30000000)
homework_portfolio.purchase_property(portfolio_inputs)
homework_portfolio.aggregate_property_data()

###### MUST RUN THIS TO COMPLETE THE BREADCRUMBS
### Sell of Property 3 in year 25
### Your visualization should have a revenue jump in year 2051
homework_portfolio.sell_property(property_key='PROPERTY_3',
                                 price_of_sale=9000000,
                                 closing_cost=3,
                                 year_of_sale=25)


#### DATA OUTPUT - DO NOT ALTER
yearly_ops_data = homework_portfolio.portfolio_operations_df.groupby(homework_portfolio.portfolio_operations_df.index.year).sum()
yearly_loans_data = homework_portfolio.portfolio_debt_df.groupby(homework_portfolio.portfolio_debt_df.index.year).sum()
yearly_non_aggregate_ops_data = homework_portfolio.portfolio_operations_df.groupby(homework_portfolio.portfolio_operations_df.index.year).last()
yearly_non_aggregate_loans_data = homework_portfolio.portfolio_debt_df.groupby(homework_portfolio.portfolio_debt_df.index.year).last()

### Altering data to be in millions - DO NOT ALTER
yearly_ops_data[['REVENUE','EXPENSE','NET_INCOME']] = yearly_ops_data[['REVENUE','EXPENSE','NET_INCOME']]/1000000
yearly_loans_data = yearly_loans_data/1000000
yearly_non_aggregate_loans_data = yearly_non_aggregate_loans_data/1000000

# ### OPERATIONS VISUALIZATIONS - DO NOT ALTER
yearly_ops_data.REVENUE.plot(kind='bar',ax=ax1,color=positive_color_one)
yearly_ops_data.EXPENSE.plot(kind='bar',ax=ax1,color=negative_color_one,)
yearly_ops_data.NET_INCOME.plot(kind='line',ax=ax1,color=neutral_color,lw=3,use_index=False)
# #FF9900
yearly_non_aggregate_ops_data[['TOTAL_UNITS']].plot(ax=ax2,color=positive_color_two,lw=3)
yearly_non_aggregate_ops_data[['TOTAL_SQFT']].plot(ax=ax3,color=positive_color_two,lw=3)

### DEBT SERVICING VISUALIZATIONS - DO NOT ALTER
yearly_non_aggregate_loans_data.BEGINNING_BALANCE.plot(kind='line',ax=ax4,color=negative_color_two,label='PRINCIPAL',lw=3)
yearly_non_aggregate_loans_data.EQUITY.plot(kind='line',ax=ax4,color=positive_color_two,lw=3)

yearly_loans_data.PAYMENT.plot(kind='line',ax=ax5,color=negative_color_two,lw=3)
yearly_loans_data.INTEREST_PAID.plot(kind='line',ax=ax5,color=negative_color_three,lw=3)
yearly_loans_data.PRINCIPAL_PAID.plot(kind='line',ax=ax5,color=positive_color_two,lw=3)
 
### VISUALIZATION SETTINGS - DO NOT ALTER
ax1.set_title('Income Statement (Millions)')
ax1.tick_params('x',labelrotation=45,)
ax1.legend();

ax2.legend();
ax3.legend();

ax4.set_title('Principal Composition (Millions)')
ax4.legend();

ax5.set_title('Debt Service Composition (Millions)')
ax5.legend();

plt.tight_layout();
plt.show();


##### BREADCRUMB DATA - DO NOT ALTER
print('Yearly Ops Data')
print(yearly_ops_data[['REVENUE','EXPENSE','NET_INCOME']].tail())
print()

#### Yearly Ops Data
####        REVENUE   EXPENSE  NET_INCOME
#### 2065  6.099578  0.406918    5.692660
#### 2066  6.253904  0.406918    5.846985
#### 2067  6.412349  0.406918    6.005431
#### 2068  6.575029  0.406918    6.168110
#### 2069  6.742061  0.406918    6.335143

##### BREADCRUMB DATA - DO NOT ALTER
print('Yearly Non-Aggregate Operations Data')
print(yearly_non_aggregate_ops_data[['TOTAL_UNITS','TOTAL_SQFT']].tail())
print()

#### Yearly Non-Aggregate Operations Data
####       TOTAL_UNITS  TOTAL_SQFT
#### 2065         50.0     68000.0
#### 2066         50.0     68000.0
#### 2067         50.0     68000.0
#### 2068         50.0     68000.0
#### 2069         50.0     68000.0

##### BREADCRUMB DATA - DO NOT ALTER
print('Yearly Loans Data')
print(yearly_loans_data[['BEGINNING_BALANCE','PAYMENT','INTEREST_PAID','PRINCIPAL_PAID','EQUITY']].tail())
print()

#### Yearly Loans Data
####       BEGINNING_BALANCE  PAYMENT  INTEREST_PAID  PRINCIPAL_PAID  EQUITY
#### 2065                0.0      0.0            0.0             0.0   276.0
#### 2066                0.0      0.0            0.0             0.0   276.0
#### 2067                0.0      0.0            0.0             0.0   276.0
#### 2068                0.0      0.0            0.0             0.0   276.0
#### 2069                0.0      0.0            0.0             0.0   276.0