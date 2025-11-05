

student_name = "HARMER_KAI_U0895215"

import pandas as pd
from dataclasses import dataclass

@dataclass
class RegularUnit:
    sqft: int = 800
    dollar_per_sqft: float = 1.5
    added_margin: float = 0.3
    vacancy_rate: float = 0.15
    expense_ratio: float = 0.1
    per_unit_rent = (dollar_per_sqft * sqft) * (1 + added_margin)
    per_unit_expense = per_unit_rent * expense_ratio

@dataclass
class LuxuryUnit:
    sqft: int = 1600
    dollar_per_sqft: float = 2.5
    added_margin: float = 0.5
    vacancy_rate: float = 0.05
    expense_ratio: float = 0.15
    per_unit_rent = (dollar_per_sqft * sqft) * (1 + added_margin)
    per_unit_expense = per_unit_rent * expense_ratio
    
class ResidentialProperty:
    def __init__(self, property_value:int, regular_units:int, luxury_units: int, 
                       loan_years:int, rate: float, down_payment_percent:float,
                       escalation: float, date_of_purchase:str):
        self.property_value = property_value
        self.regular_unit_data = RegularUnit()
        self.luxury_unit_data = LuxuryUnit()
        self.regular_units = regular_units        
        self.luxury_units = luxury_units
        self.total_units = self.regular_units + self.luxury_units 
        self.loan_years = loan_years
        self.loan_months = self.loan_years * 12 ## Month Count of Loan Life
        self.rate = rate / 100 ## Assumes whole percentage. 
        self.down_payment_percent = down_payment_percent / 100 ## Assumes whole percentage. 
        self.monthly_escalation = escalation / 100 / 12 ## Assumes whole percentage. 
        self.monthly_e_factor = 1 + self.monthly_escalation
        self.date_of_purchase = str(date_of_purchase)
        self.model_month_lifetime = (2070 - int(date_of_purchase)) * 12 ## All properties model out to 2070
        self.model_lifetime = '2070' ## Final Year of Model
        self.loan_df = None ## Placeholder Instance Variable
        self.operations_report_df = None ## Placeholder Instance Variable
        self.asset_sold = False
        ## Automatically run model functions
        self.loan_model()
        self.monthly_operations_statement()
        self.operations_report() 

    def loan_model(self,) -> None:
                    
        self.principal = self.property_value - (self.property_value * self.down_payment_percent)
        
        self.payment = self.payment(self.rate, self.loan_months, self.principal)

        interest_pmt = round((self.rate/12) *  self.principal,2)
        principal_pmt = round(self.payment - interest_pmt,)
        ending_principal_balance = round(self.principal - principal_pmt,2)
        equity = round(principal_pmt + (self.property_value * self.down_payment_percent),2)

        self.loan_df = pd.DataFrame(columns=['BEGINNING_BALANCE','PAYMENT','INTEREST_PAID',
                                             'PRINCIPAL_PAID','ENDING_BALANCE','EQUITY'],
                                             index=pd.date_range(str(self.date_of_purchase), 
                                                                 self.model_lifetime, freq='M',))        
        self.loan_df.fillna(0,inplace=True)

        for row in range(len(self.loan_df)):
            if row == 0:
                self.loan_df.iloc[row,:] = [self.principal,
                                            self.payment,
                                            interest_pmt,
                                            principal_pmt,
                                            ending_principal_balance,
                                            equity]
                
            elif (row!=0) and (row<self.loan_months):
                inner_beginning_balance = round(self.loan_df.iloc[row-1].ENDING_BALANCE,2)
                inner_interest_pmt = round((self.rate/12) * inner_beginning_balance,2)
                inner_principal_pmt = round(self.payment - inner_interest_pmt,2)
                inner_ending_balance = round(inner_beginning_balance - inner_principal_pmt,2)
                inner_equity = round(inner_principal_pmt + self.loan_df.iloc[row-1].EQUITY,2) 

                self.loan_df.iloc[row,:] = [inner_beginning_balance,
                                            ## Does not update intentionally. 
                                            self.payment,
                                            inner_interest_pmt,
                                            inner_principal_pmt,
                                            inner_ending_balance,
                                            inner_equity]
            
            elif row==self.loan_months:
                ## Final loan month can go negative, this accomodates that risk. 
                self.loan_df.iloc[row,:] = [0,0,0,0,0,self.property_value]         

            else:
                ## Model Lifetime Equity Valuation
                ## Could be updated with growth projections. 
                final_equity = round(self.loan_df.iloc[self.loan_months,:].EQUITY)
                self.loan_df.iloc[row,:] = [0,0,0,0,0,final_equity]
    
    def monthly_operations_statement(self,) -> None:  
        ## Metadata
        self.total_sqft = (self.regular_unit_data.sqft * self.regular_units) + (self.luxury_unit_data.sqft * self.luxury_units)

        ## REVENUE
        reg_unit_revenue = (self.regular_unit_data.per_unit_rent * self.regular_units) * (1 - self.regular_unit_data.vacancy_rate)
        lux_unit_revenue = (self.luxury_unit_data.per_unit_rent * self.luxury_units) * (1 - self.luxury_unit_data.vacancy_rate)

        self.monthly_total_revenue = reg_unit_revenue + lux_unit_revenue 
        
        ## EXPENSE        
        self.reg_unit_expense = self.regular_unit_data.per_unit_expense * self.regular_units
        self.lux_unit_expense = self.luxury_unit_data.per_unit_expense * self.luxury_units
        

    def operations_report(self,) -> None:

        ### Initial Values
        dynamic_revenue = self.monthly_total_revenue
        dynamic_loan_expense = self.payment + self.reg_unit_expense + self.lux_unit_expense
        dynamic_non_loan_expense = self.reg_unit_expense + self.lux_unit_expense

        self.operations_report_df = pd.DataFrame(columns=['REVENUE','EXPENSE','NET_INCOME',
                                                          'TOTAL_SQFT','TOTAL_UNITS'],
                                                          index=pd.date_range(str(self.date_of_purchase), 
                                                                              self.model_lifetime, freq='M',))        
        self.operations_report_df.fillna(0,inplace=True)

        for row in range(len(self.operations_report_df)):            

            if row <= self.loan_months:    
                dynamic_revenue = (dynamic_revenue * self.monthly_e_factor) 
                dynamic_expense = (dynamic_loan_expense * self.monthly_e_factor)
                # dynamic_net_income = (dynamic_revenue - dynamic_expense) / ((1 + (0.02/12)) ** i)
                dynamic_net_income = (dynamic_revenue - dynamic_expense)

                self.operations_report_df.iloc[row,:] = [dynamic_revenue,
                                                         dynamic_expense,
                                                         dynamic_net_income,
                                                         self.total_sqft,
                                                         self.total_units,]

            else:
                dynamic_revenue = (dynamic_revenue * self.monthly_e_factor)
                dynamic_expense = (dynamic_non_loan_expense * self.monthly_e_factor)
                # dynamic_net_income = (dynamic_revenue - dynamic_expense) / ((1 + (0.02/12)) ** i)
                dynamic_net_income = (dynamic_revenue - dynamic_expense)

                self.operations_report_df.iloc[row,:] = [dynamic_revenue,
                                                         dynamic_expense,
                                                         dynamic_net_income,
                                                         self.total_sqft,
                                                         self.total_units,]
                
    def payment(self, rate: float, loan_months: int, principal: int) -> None:
        #calculate monthly payment
        return round((rate/12) * (1/(1 - (1 + rate/12) ** (-loan_months))) * principal, 2)

    ########################################################
    ##################### QUESTION 1 #######################
    ########################################################
    ### Your method has three inputs:
        ## Price of Sale: An integer value related to the sale price of the property.
            ## ex: 10000000
        ## Closing Cost: A float value related to the cost of the sale owed to an agent as a whole percentage.
            ## ex: 3
        ## Year of Sale: An integer value related to the year of ownership the property is sold.
            ## ex: 15
            ## "I am selling this property in the 15th year of owning it."
    ## We have an instance variable called "asset_sold". 
        ## if asset_sold equals True, return None, else enter a new code section.
            ## Set asset_sold equal to True
            ## Create two variables:
                ## cost of close: closing cost divided by 100 times the price of sale input. 
                ## loan month: year of sale times 12
        ### UTILIZE THE LOAN MONTH VALUE AS AN INDEX FOR THE FOLLOWING TASKS ###
            ## Gather loan remainder. This is the BEGINNING_BALANCE in the loan dataframe at the current loan month. 
            ## Derive net of sale value. This is the price of sale minus cost of sale minus loan remainder. 
            ## Update Operations Report data frame:
                ## Add net of sale to revenue inplace
                ## Add net of sale to net income inplace
                ## Set all values after the sell month to zero (0)
            ## Update the Loan data frame:
                ## Set all values after the sell month to zero (0)

    def sale_of_property(self, price_of_sale: int, closing_cost: float, year_of_sale: int) -> None:
        if self.asset_sold:
            return None

        self.asset_sold = True

        cost_of_close = (closing_cost / 100) * price_of_sale
        loan_month = year_of_sale * 12  

        loan_remainder = float(self.loan_df.iloc[loan_month].BEGINNING_BALANCE)

        net_of_sale = price_of_sale - cost_of_close - loan_remainder

        ops = self.operations_report_df

        revenue_col_idx = ops.columns.get_loc('REVENUE')
        net_income_col_idx = ops.columns.get_loc('NET_INCOME')
        ops.iloc[loan_month, revenue_col_idx] = ops.iloc[loan_month, revenue_col_idx] + net_of_sale
        ops.iloc[loan_month, net_income_col_idx] = ops.iloc[loan_month, net_income_col_idx] + net_of_sale

        after_row = loan_month + 1
        if after_row < len(ops):
            ops.iloc[after_row:, :] = 0
        if after_row < len(self.loan_df):
            self.loan_df.iloc[after_row:, :] = 0

class Portfolio:
    def __init__(self, year_established:int, capital: int):
        self.year_established = year_established
        ### Capital deployed to begin business operations
        self.capital = capital
        ### This is an ID counter for property objects, ID begins at 1
        self.property_counter = 1
        ### This is our initial state of the database
        self.property_database = {}

        self.model_lifetime = '2070'

        self.portfolio_operations_df = None
        self.portfolio_debt_df = None

    def purchase_property(self, property_attributes: list):

        for attributes in property_attributes:
            ### DECISION: EACH NEW PROPERTY IS PROVIDED 10% OF CAPITAL
            startup_capital = 0.1 * self.capital 
            if startup_capital > self.capital:
                ## Cannot Purchase Property
                return None
            else:
                self.capital -= startup_capital
                down_payment_percentage = (startup_capital/attributes['PROPERTY_VALUE']) * 100

                key = 'PROPERTY_' + str(self.property_counter)
       
                self.property_database[key] = ResidentialProperty(attributes['PROPERTY_VALUE'],attributes['REGULAR_UNITS'],
                                                                  attributes['LUXURY_UNITS'],attributes['LOAN_YEARS'],
                                                                  attributes['INTEREST_RATE'],down_payment_percentage,
                                                                  attributes['ESCALATION'],attributes['DATE_OF_PURCHASE'])    
                self.property_counter += 1
     
    def query_property(self, property_key: str):

        return self.property_database[property_key]

    def aggregate_property_data(self):
        
        ### Values reset upon every run of the method. 
        self.portfolio_operations_df = pd.DataFrame(columns=['REVENUE','EXPENSE','NET_INCOME','TOTAL_SQFT','TOTAL_UNITS'],
                                                    index=pd.date_range(str(self.year_established),self.model_lifetime, freq='M',))
        
        self.portfolio_operations_df.fillna(0,inplace=True)

        ### Values reset upon every run of the method. 
        self.portfolio_debt_df = pd.DataFrame(columns=['BEGINNING_BALANCE','PAYMENT','INTEREST_PAID',
                                                       'PRINCIPAL_PAID','ENDING_BALANCE','EQUITY'],
                                              index=pd.date_range(str(self.year_established),self.model_lifetime, freq='M',))
        
        self.portfolio_debt_df.fillna(0,inplace=True)
        
        ### Loop over all ResidentialProperties
        for property in self.property_database.values():
            ## Loop over column count to update all target operations categories. 
            # for column_idx, column_name in enumerate(self.portfolio_operations_df.columns):
            for column_idx in range(len(self.portfolio_operations_df.columns)):
            
                self.portfolio_operations_df.iloc[:,column_idx] = pd.concat([self.portfolio_operations_df.iloc[:,column_idx],
                                                                              property.operations_report_df.iloc[:,column_idx]], 
                                                                              axis=1).fillna(0).sum(axis=1)
            # ### Loop over all ResidentialProperties
            for column_idx in range(len(self.portfolio_debt_df.columns)):
            #     ## Loop over column count to update all target operations categories. 
                self.portfolio_debt_df.iloc[:,column_idx] = pd.concat([self.portfolio_debt_df.iloc[:,column_idx],
                                                                             property.loan_df.iloc[:,column_idx]], 
                                                                             axis=1).fillna(0).sum(axis=1)

    ########################################################
    ##################### QUESTION 2 #######################
    ########################################################
    ### Your method has four inputs:
        ## Property Key: A string value representing a target key in the Portfolio database dictionary.
            ## ex: "PROPERTY_1"
        ## Price of Sale: An integer value related to the sale price of the property.
            ## ex: 10000000
        ## Closing Cost: A float value related to the cost of the sale owed to an agent as a whole percentage.
            ## ex: 3
        ## Year of Sale: An integer value related to the year of ownership the property is sold.
            ## ex: 15
    
    ## if the property key exists in the database, enter a new code section, else return None
        ## Access the target ResidentialProperty object using the property key passed into the method. 
        ## Utilize your sale_of_property method to sell the property. 
        ## After selling the property, run the aggregate_property_date method.

    def sell_property(self, property_key: str, price_of_sale: int, closing_cost: float, year_of_sale: int) -> None:
        if property_key not in self.property_database:
            return None
        prop = self.property_database[property_key]
        prop.sale_of_property(price_of_sale, closing_cost, year_of_sale)
        self.aggregate_property_data()
        