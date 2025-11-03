from L10_PROPERTY_MODELING import ResidentialProperty, Portfolio
import matplotlib.pyplot as plt


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

##################################################
############### PROPERTY SHOWCASE ################
##################################################

property_1 = {'PROPERTY_VALUE':4000000,
                'REGULAR_UNITS':5,
                'LUXURY_UNITS':5,
                'LOAN_YEARS':30,
                'INTEREST_RATE':5,
                'DOWN_PAYMENT_PERCENTAGE':20,
                'ESCALATION':2,
                'DATE_OF_PURCHASE':2018}

first_property = ResidentialProperty(property_1['PROPERTY_VALUE'],property_1['REGULAR_UNITS'],
                                     property_1['LUXURY_UNITS'],property_1['LOAN_YEARS'],
                                     property_1['INTEREST_RATE'],property_1['DOWN_PAYMENT_PERCENTAGE'],
                                     property_1['ESCALATION'],property_1['DATE_OF_PURCHASE']) 

yearly_ops_data = first_property.operations_report_df.groupby(first_property.operations_report_df.index.year).sum()
yearly_loans_data = first_property.loan_df.groupby(first_property.loan_df.index.year).sum()
yearly_non_aggregate_ops_data = first_property.operations_report_df.groupby(first_property.operations_report_df.index.year).last()
yearly_non_aggregate_loans_data = first_property.loan_df.groupby(first_property.loan_df.index.year).last()

fig = plt.figure(figsize=(30,15),facecolor=background_color)
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

### Altering data to be in millions
yearly_ops_data[['REVENUE','EXPENSE','NET_INCOME']] = yearly_ops_data[['REVENUE','EXPENSE','NET_INCOME']]
yearly_loans_data = yearly_loans_data
yearly_non_aggregate_loans_data = yearly_non_aggregate_loans_data

# ### OPERATIONS VISUALIZATIONS
yearly_ops_data.REVENUE.plot(kind='bar',ax=ax1,color=positive_color_one)
yearly_ops_data.EXPENSE.plot(kind='bar',ax=ax1,color=negative_color_one,)
yearly_ops_data.NET_INCOME.plot(kind='line',ax=ax1,color=neutral_color,lw=3,use_index=False)
# #FF9900
yearly_non_aggregate_ops_data[['TOTAL_UNITS']].plot(ax=ax2,color=positive_color_two,lw=3)
yearly_non_aggregate_ops_data[['TOTAL_SQFT']].plot(ax=ax3,color=positive_color_two,lw=3)

### DEBT SERVICING VISUALIZATIONS
yearly_non_aggregate_loans_data.BEGINNING_BALANCE.plot(kind='line',ax=ax4,color=negative_color_two,label='PRINCIPAL',lw=3)
yearly_non_aggregate_loans_data.EQUITY.plot(kind='line',ax=ax4,color=positive_color_two,lw=3)

yearly_loans_data.PAYMENT.plot(kind='line',ax=ax5,color=negative_color_two,lw=3)
yearly_loans_data.INTEREST_PAID.plot(kind='line',ax=ax5,color=negative_color_three,lw=3)
yearly_loans_data.PRINCIPAL_PAID.plot(kind='line',ax=ax5,color=positive_color_two,lw=3)
 
ax1.set_title('Income Statement')
ax1.tick_params('x',labelrotation=45,)
ax1.legend();

ax2.legend();
ax3.legend();

ax4.set_title('Principal Composition')
ax4.legend();

ax5.set_title('Debt Service Composition')
ax5.legend();

plt.tight_layout();
plt.show();

##################################################
############## PORTFOLIO SHOWCASE ################
##################################################

# portfolio_inputs = [{'PROPERTY_VALUE':10000000,
#                      'REGULAR_UNITS':5,
#                      'LUXURY_UNITS':10,
#                      'LOAN_YEARS':30,
#                      'INTEREST_RATE':5,
#                      'ESCALATION':2,
#                      'DATE_OF_PURCHASE':2018},
#                      {'PROPERTY_VALUE':3000000,
#                      'REGULAR_UNITS':5,
#                      'LUXURY_UNITS':5,
#                      'LOAN_YEARS':30,
#                      'INTEREST_RATE':7,
#                      'ESCALATION':3,
#                      'DATE_OF_PURCHASE':2023},
#                      {'PROPERTY_VALUE':6000000,
#                      'REGULAR_UNITS':0,
#                      'LUXURY_UNITS':10,
#                      'LOAN_YEARS':15,
#                      'INTEREST_RATE':6,
#                      'ESCALATION':3,
#                      'DATE_OF_PURCHASE':2026},
#                      {'PROPERTY_VALUE':5000000,
#                      'REGULAR_UNITS':5,
#                      'LUXURY_UNITS':5,
#                      'LOAN_YEARS':30,
#                      'INTEREST_RATE':5,
#                      'ESCALATION':1.5,
#                      'DATE_OF_PURCHASE':2030},
#                      {'PROPERTY_VALUE':5000000,
#                      'REGULAR_UNITS':0,
#                      'LUXURY_UNITS':15,
#                      'LOAN_YEARS':15,
#                      'INTEREST_RATE':6,
#                      'ESCALATION':3,
#                      'DATE_OF_PURCHASE':2045}]

# black_mountain_real_estate = Portfolio(2018,30000000)
# black_mountain_real_estate.purchase_property(portfolio_inputs)
# black_mountain_real_estate.aggregate_property_data()

# fig = plt.figure(figsize=(30,15),facecolor=background_color)
# ax1 = plt.subplot(3,2,(1,2),facecolor=background_color)
# ax2 = plt.subplot(3,2,3,facecolor=background_color)
# ax3 = plt.subplot(3,2,4,facecolor=background_color)
# ax4 = plt.subplot(3,2,5,facecolor=background_color)
# ax5 = plt.subplot(3,2,6,facecolor=background_color)

# ax1.yaxis.set_major_formatter('{x:,.0f}')
# ax2.yaxis.set_major_formatter('{x:,.0f}')
# ax3.yaxis.set_major_formatter('{x:,.0f}')
# ax4.yaxis.set_major_formatter('{x:,.0f}')
# ax5.yaxis.set_major_formatter('{x:,.1f}')

# yearly_ops_data = black_mountain_real_estate.portfolio_operations_df.groupby(black_mountain_real_estate.portfolio_operations_df.index.year).sum()
# yearly_loans_data = black_mountain_real_estate.portfolio_debt_df.groupby(black_mountain_real_estate.portfolio_debt_df.index.year).sum()
# yearly_non_aggregate_ops_data = black_mountain_real_estate.portfolio_operations_df.groupby(black_mountain_real_estate.portfolio_operations_df.index.year).last()
# yearly_non_aggregate_loans_data = black_mountain_real_estate.portfolio_debt_df.groupby(black_mountain_real_estate.portfolio_debt_df.index.year).last()

# yearly_ops_data = yearly_ops_data/1000000
# yearly_loans_data = yearly_loans_data/1000000
# yearly_non_aggregate_loans_data = yearly_non_aggregate_loans_data/1000000

# # ### OPERATIONS VISUALIZATIONS
# yearly_ops_data.REVENUE.plot(kind='bar',ax=ax1,color=positive_color_one)
# yearly_ops_data.EXPENSE.plot(kind='bar',ax=ax1,color=negative_color_one,)
# yearly_ops_data.NET_INCOME.plot(kind='line',ax=ax1,color=neutral_color,lw=3,use_index=False)
# # #FF9900
# yearly_non_aggregate_ops_data[['TOTAL_UNITS']].plot(ax=ax2,color=positive_color_two,lw=3)
# yearly_non_aggregate_ops_data[['TOTAL_SQFT']].plot(ax=ax3,color=positive_color_two,lw=3)

# ### DEBT SERVICING VISUALIZATIONS
# yearly_non_aggregate_loans_data.BEGINNING_BALANCE.plot(kind='line',ax=ax4,color=negative_color_two,label='PRINCIPAL',lw=3)
# yearly_non_aggregate_loans_data.EQUITY.plot(kind='line',ax=ax4,color=positive_color_two,lw=3)

# yearly_loans_data.PAYMENT.plot(kind='line',ax=ax5,color=negative_color_two,lw=3)
# yearly_loans_data.INTEREST_PAID.plot(kind='line',ax=ax5,color=negative_color_three,lw=3)
# yearly_loans_data.PRINCIPAL_PAID.plot(kind='line',ax=ax5,color=positive_color_two,lw=3)
 
# ax1.set_title('Income Statement (Millions)')
# ax1.tick_params('x',labelrotation=45,)
# ax1.legend();

# ax2.legend();
# ax3.legend();

# ax4.set_title('Principal Composition (Millions)')
# ax4.legend();

# ax5.set_title('Debt Service Composition (Millions)')
# ax5.legend();

# plt.tight_layout();
# plt.show();
