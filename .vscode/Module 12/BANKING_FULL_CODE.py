import numpy as np
import random
import pickle
import warnings
import sys
warnings.filterwarnings('ignore')

# prevents pycache
sys.dont_write_bytecode = True

class Database:
    def __init__(self, branch_id, total_reserves, reserve_rate):

        self.__assets = {'TOTAL_RESERVES':round(float(total_reserves),2),
                         'REQUIRED_RESERVES':round(total_reserves * reserve_rate,2),
                         'EXCESS_RESERVES':round(total_reserves * (1 - reserve_rate),2),
                         'LOAN_BALANCE': 0.0}
        self.__liabilities = {'CHECKED_DEPOSITS': 0.0,
                               ### Is meant to equal owners equity.                                             
                              'OWNERS_EQUITY':float(total_reserves),}
        ### Initially empty.
        ### ID, $ Balance, Loan Count, Current Principal, Current Interest
        #{ account_id: {'BALANCE':0,'LOAN_COUNT':0,'CURRENT_PRINCIPAL':0,'CURRENT_INTEREST':0}}
        self.__accounts = {}

        self.__database = {'BRANCH': branch_id,
                           'BALANCE_SHEET': {'ASSETS':self.__assets,
                                             'LIABILITIES': self.__liabilities},
                           'ACCOUNTS':self.__accounts}
        
        self.reserve_rate = reserve_rate

    def update_reserves(self, credit, dollar_value):
        
        initial_required_reserves = self.__database['BALANCE_SHEET']['ASSETS']['REQUIRED_RESERVES']
        initial_excess_reserves = self.__database['BALANCE_SHEET']['ASSETS']['EXCESS_RESERVES']
        initial_total_reserves = self.__database['BALANCE_SHEET']['ASSETS']['TOTAL_RESERVES']

        ### Credit is decrease
        if credit:
            new_total_reserves = initial_total_reserves - dollar_value
            new_excess_reserves = new_total_reserves - (new_total_reserves * self.reserve_rate)
            new_required_reserves = new_total_reserves - new_excess_reserves

            self.__database['BALANCE_SHEET']['ASSETS']['REQUIRED_RESERVES'] = new_required_reserves
            self.__database['BALANCE_SHEET']['ASSETS']['EXCESS_RESERVES'] = new_excess_reserves
            self.__database['BALANCE_SHEET']['ASSETS']['TOTAL_RESERVES'] = round(new_required_reserves + new_excess_reserves,2)
        else:
            new_required_reserves = (dollar_value * self.reserve_rate) + initial_required_reserves
            new_excess_reserves = ((1-self.reserve_rate) * dollar_value) + initial_excess_reserves
            
            self.__database['BALANCE_SHEET']['ASSETS']['REQUIRED_RESERVES'] = new_required_reserves
            self.__database['BALANCE_SHEET']['ASSETS']['EXCESS_RESERVES'] = new_excess_reserves
            self.__database['BALANCE_SHEET']['ASSETS']['TOTAL_RESERVES'] = round(new_required_reserves + new_excess_reserves,2)

    def update_deposits(self, credit, dollar_value):
 
        initial_balance = self.__database['BALANCE_SHEET']['LIABILITIES']['CHECKED_DEPOSITS']
        if credit:
            new_balance = initial_balance + dollar_value 
        else:
            new_balance = initial_balance - dollar_value

        self.__database['BALANCE_SHEET']['LIABILITIES']['CHECKED_DEPOSITS'] = new_balance

    def update_loans(self, principal, interest, payoff):
        ### Excess Reserves decrease, Loan value increases, interest paid is owners equity...

        initial_total_reserves = self.__database['BALANCE_SHEET']['ASSETS']['TOTAL_RESERVES']
        initial_required_reserves = self.__database['BALANCE_SHEET']['ASSETS']['REQUIRED_RESERVES']
        initial_excess_reserves = self.__database['BALANCE_SHEET']['ASSETS']['EXCESS_RESERVES']
        initial_loan_receivables = self.__database['BALANCE_SHEET']['ASSETS']['LOAN_BALANCE']
        initial_owners_equity = self.__database['BALANCE_SHEET']['LIABILITIES']['OWNERS_EQUITY']

        if payoff:
            
            new_total_reserves = round(initial_total_reserves + principal + interest,2)
            new_excess_reserves = round(initial_excess_reserves + principal + interest,2)
            ### We recognize interest revenue here
            new_owners_equity = initial_owners_equity + interest

            self.__database['BALANCE_SHEET']['ASSETS']['EXCESS_RESERVES'] = new_excess_reserves
            self.__database['BALANCE_SHEET']['ASSETS']['TOTAL_RESERVES'] = new_total_reserves
            self.__database['BALANCE_SHEET']['LIABILITIES']['OWNERS_EQUITY'] = new_owners_equity
            self.__database['BALANCE_SHEET']['ASSETS']['LOAN_BALANCE'] = 0
            
        else:
            ### We are issuing a loan
            new_total_reserves = initial_total_reserves - principal
            new_excess_reserves = initial_excess_reserves - principal
            new_loan_balance = initial_loan_receivables + principal

            self.__database['BALANCE_SHEET']['ASSETS']['EXCESS_RESERVES'] = new_excess_reserves
            self.__database['BALANCE_SHEET']['ASSETS']['TOTAL_RESERVES'] = new_total_reserves
            self.__database['BALANCE_SHEET']['ASSETS']['LOAN_BALANCE'] = new_loan_balance

            ### WE ARE NOT ACCOUNTING FOR INTEREST RECEIVABLE, WE RECOGNIZE IT UPON PAYMENT. 

    def create_account(self, account_id, initial_balance):
        self.__database['ACCOUNTS'][account_id] = {'BALANCE':initial_balance,
                                                   'LOAN_COUNT':0,
                                                   'CURRENT_PRINCIPAL':0,
                                                   'CURRENT_INTEREST':0}

    def check_account(self, account_id):
        # accounts_table = self.__database['ACCOUNTS']
        # if len(accounts_table[accounts_table.ACCOUNT_ID==account_id])==0:
        if account_id not in self.__database['ACCOUNTS']:                
            return "Account Does Not Exist."
        else:
            # return accounts_table[accounts_table.ACCOUNT_ID==account_id].copy()  
            return self.__database['ACCOUNTS'][account_id]

    def check_account_checking_balance(self, account_id):
        if account_id not in self.__database['ACCOUNTS']:        
            return "Account Does Not Exist."
        else:
            return self.__database['ACCOUNTS'][account_id]['BALANCE']

    def update_account(self, account_id, dollar_value, credit):
        if account_id not in self.__database['ACCOUNTS']:             
            return "Account Does Not Exist."           
        else:
           account_balance = self.__database['ACCOUNTS'][account_id]['BALANCE']

           if credit:
               ## Decrease Account
               new_account_balance = account_balance - dollar_value
               self.__database['ACCOUNTS'][account_id]['BALANCE'] = new_account_balance
               return new_account_balance
           else:
                ## Increase account 
                new_account_balance = account_balance + dollar_value          
                self.__database['ACCOUNTS'][account_id]['BALANCE'] = new_account_balance
                return new_account_balance                                    
    ### We set initial None values here to make the input optional for payoff activity. 
    def update_account_loans(self, account_id, principal=None, interest=None, payoff=False):
        ### Loans can only be approved, we assume everyone doesn't default. (haha)
        if account_id not in self.__database['ACCOUNTS']:                        
            return "Account Does Not Exist."            
        else:
            if payoff:
                self.__database['ACCOUNTS'][account_id]['LOAN_COUNT'] = 0                
                self.__database['ACCOUNTS'][account_id]['CURRENT_PRINCIPAL'] = 0
                self.__database['ACCOUNTS'][account_id]['CURRENT_INTEREST'] = 0
            else:
                self.__database['ACCOUNTS'][account_id]['LOAN_COUNT'] = 1          
                self.__database['ACCOUNTS'][account_id]['CURRENT_PRINCIPAL'] = principal
                self.__database['ACCOUNTS'][account_id]['CURRENT_INTEREST'] = interest
        
    def data_output(self):    
        return self.__database
    
    def __str__(self):
        branch_id = self.__database['BRANCH']
        assets = self.__database['BALANCE_SHEET']['ASSETS']
        liabilities = self.__database['BALANCE_SHEET']['LIABILITIES']
        accounts = self.__database['ACCOUNTS']

        output = f'''
BRANCH ID: {branch_id}
ACCOUNTS: {len(accounts)}
BALANCE SHEET:
    ASSETS - {round(assets['TOTAL_RESERVES'] + assets['LOAN_BALANCE'],2):,.0f}: 
        - TOTAL RESERVES: {assets['TOTAL_RESERVES']:,.0f}
            - REQUIRED: {assets['REQUIRED_RESERVES']:,.0f}
            - EXCESS: {assets['EXCESS_RESERVES']:,.0f}
            - LOANS RECEIVABLE: {assets['LOAN_BALANCE']:,.0f}
    LIABILITES - {round(liabilities['CHECKED_DEPOSITS'] + liabilities['OWNERS_EQUITY'],2):,.0f}: 
        - CHECKED_DEPOSITS: {liabilities['CHECKED_DEPOSITS']:,.0f}
        - OWNERS EQUITY: {liabilities['OWNERS_EQUITY']:,.0f}
        '''
        return output

class Branch:
    def __init__(self, branch_id, startup_capital, reserve_rate):
        self.branch_id = branch_id        
        self.initial_reserves = startup_capital
        self.reserve_rate = reserve_rate
        self.account_counter = 1
        self.__database = Database(self.branch_id, self.initial_reserves, self.reserve_rate)

    # @classmethod
    # def new_branch(cls, branch_id, startup_capital, reserve_rate):
    #     return cls(branch_id, startup_capital, reserve_rate)
    
    def check_branch_accounts(self):
        return self.__database
    
    def create_account(self, initial_balance):
        ## Initial Account Creation and Checking Account Balance Increase
        self.__database.create_account(self.account_counter, initial_balance)
        self.account_counter += 1

        ### Updates to Bank Balance Sheet
        self.__database.update_deposits(credit=True, dollar_value=initial_balance)
        self.__database.update_reserves(credit=False, dollar_value=initial_balance)

        return f"Account {self.account_counter-1} Created"

    def deposit(self, account_id, dollar_value):

        new_account_balance = self.__database.update_account(account_id=account_id, dollar_value=dollar_value, credit=False)
        
        if isinstance(new_account_balance, str):
            return "Account Does Not Exist."
        else:
            ### Updates to Bank Balance Sheet
            self.__database.update_deposits(credit=True, dollar_value=dollar_value)
            self.__database.update_reserves(credit=False, dollar_value=dollar_value)

            return f'Depositing ${dollar_value}\nNew Balance: ${new_account_balance}'
    
    def withdraw(self, account_id, dollar_value):
        current_balance = self.__database.check_account_checking_balance(account_id)
        if isinstance(current_balance, str):
            return "Account Does Not Exist."
        else:
            if current_balance < dollar_value:
                return 'Cannot withdraw funds'
                
            else:
                new_account_balance = self.__database.update_account(account_id=account_id, dollar_value=dollar_value, credit=True)
                if isinstance(new_account_balance, str):
                    return "Account Does Not Exist."
                else:
                    self.__database.update_deposits(credit=False, dollar_value=dollar_value)
                    self.__database.update_reserves(credit=True, dollar_value=dollar_value)            

                    return f'Withdrawing ${dollar_value}\nRemaining Balance: ${new_account_balance}'       
                    
    def check_account(self, account_id):
        account_dict = self.__database.check_account(account_id)
        if isinstance(account_dict, str):
            return "Account Does Not Exist."
        else:
            return account_dict

    ## For our credit model. 
    def payment(self, rate: float, years: int, principal: float) -> float:

        month_life = years * 12
        month_rate = rate / 100 / 12
        payment = round(principal * ((month_rate)*(1+month_rate)**(month_life))/((1+month_rate)**(month_life)-1),2)
        lifetime_interest = round(payment * month_life, 2)

        return (payment, lifetime_interest)

    def consumer_credit_model(self,account_id, term, urban_rural, loan_principal):

        account_dict = self.check_account(account_id)
        loan_count = account_dict['LOAN_COUNT']
        if loan_count > 0 :
            return "Cannot Offer Another Loan"
        else:            
            ### We could build out safety parameters here.
            ### Generate a single row of data for the model. 
            ## Existing Customer, Months, Urban or Rural Customer, Principal
            X = np.array([[1,term,urban_rural,loan_principal]])
            loaded_model = pickle.load(open('ConsumerCreditModel2023.sav', 'rb'))
            # Predict probability of loan default
            prediction = loaded_model.predict_proba(X)
            ### Probability of default as a decimal value. 
            prob_default = prediction[:,1]

            ### Business logic
            ### These are annual interest rates. 
            ## If default prob above 75%, reject candidate
            ## if prob between 51 - 75%, offer 30% interest rate
            ## if prob between 26 - 50%, offer 15% interest rate
            ## if prob between 0 - 25% offer 5% interest rate.  
            if prob_default > 0.75: 
                return "Application Rejected"
            else:            
            
                if (0 < prob_default <= 0.25):
                    interest_rate = 5
                elif (0.26 < prob_default <= 0.50):
                    interest_rate = 15
                elif (0.51 < prob_default <= 0.75):
                    interest_rate = 30
                else:
                    ## Loan above 75%
                    pass

                ### Generate Payment Value
                payment_amount, lifetime_interest = self.payment(interest_rate, (term/12), loan_principal)
                ### Output Data
                payload = {'PRINCIPAL': loan_principal,
                           'ANNUALIZED_TERM': round(term/12,2),
                           'APR': interest_rate,
                           'MONTHLY PAYMENT': payment_amount}

                for key, value in payload.items():
                    print(f"{key}: {value}")

                ### Update Account Data
                self.__database.update_account_loans(account_id, loan_principal, lifetime_interest, payoff=False)
                ### Update Bank Statement
                self.__database.update_loans(loan_principal, lifetime_interest, payoff=False)

                return "Application Approved"

    def payoff_account_loan(self, account_id):
        account_dict = self.check_account(account_id)      

        if isinstance(account_dict, str):
            return "Account Does Not Exist."
        else: 
            loan_count = account_dict['LOAN_COUNT']
            if loan_count == 0:                
                return "No Loans to Repay."
            else:
                loan_principal = account_dict['CURRENT_PRINCIPAL']
                lifetime_interest = account_dict['CURRENT_INTEREST']

                self.__database.update_account_loans(account_id, payoff=True)

                self.__database.update_loans(loan_principal, lifetime_interest, payoff=True)
                
                return f"Account {account_id} paid off their current loan liabilities."

    def __repr__(self):
        return f'BRANCH: {self.branch_id}'            
    
class Bank:
    def __init__(self, corporation_name, year_established, capital):
        self.corporation = corporation_name
        self.year_established = year_established
        ### Capital deployed to begin business operations
        ### WHEN AGGREGATING, THIS WILL BE EXCESS DEPOSIT AND OWNERS EQUITY. 
        self.capital = capital
        ### Theoretical Reserve Rate
        self.required_reserve_rate = 0.1
        ### This is an ID counter for us to track branch data. ID begins at 1
        self.branch_counter = 1
        ### This is our initial state of the database    
        self.branch_database = {}

        ### Overall corporation accounts initial state
        self.required_reserves = 0
        self.excess_reserves = 0
        self.total_reserves = 0
        self.loan_balance = 0 
        self.checked_deposits = 0 
        self.owners_equity = 0
        self.accounts = 0
        self.total_assets = self.total_reserves + self.loan_balance + self.capital  
        self.total_liabilities = (self.owners_equity + self.capital) + self.checked_deposits
    
    def open_branch(self):
        ### USE BRANCH CLASS GENERATOR
        ### DECISION: EACH NEW BRANCH IS PROVIDED 10% of total bank capital. 
        startup_capital = .1 * self.capital 
        if startup_capital > self.capital:
            return "Cannot Open Branch"
        else:
            self.capital -= startup_capital

            self.branch_database[self.branch_counter] = Branch(self.branch_counter, startup_capital, self.required_reserve_rate)
            self.branch_counter += 1

            return "Created New Branch"

    def balance_sheet_aggregation(self):
        for id in range(1,len(self.branch_database)+1):

            branch = self.branch_database[id].check_branch_accounts().data_output()    

        
            self.required_reserves += branch['BALANCE_SHEET']['ASSETS']['REQUIRED_RESERVES']
            self.excess_reserves += branch['BALANCE_SHEET']['ASSETS']['EXCESS_RESERVES']
            self.total_reserves = self.required_reserves + self.excess_reserves
            self.loan_balance += branch['BALANCE_SHEET']['ASSETS']['LOAN_BALANCE']
            self.checked_deposits += branch['BALANCE_SHEET']['LIABILITIES']['CHECKED_DEPOSITS']
            self.owners_equity += branch['BALANCE_SHEET']['LIABILITIES']['OWNERS_EQUITY'] 
            self.accounts += len(branch['ACCOUNTS'])

            self.total_assets = self.total_reserves + self.loan_balance + self.capital
            self.total_liabilities = self.owners_equity + self.checked_deposits + self.capital
            
    def __repr__(self):
        output = f"""
Corporation: {self.corporation}, established {self.year_established}
BRANCHES: {len(self.branch_database)}
ACCOUNTS: {self.accounts}
BALANCE SHEET:
    ASSETS - {round(self.total_assets,2):,.0f}
        - TOTAL RESERVES: {round(self.total_reserves,2):,.0f}
            - REQUIRED: {round(self.required_reserves,2):,.0f}
            - EXCESS: {round(self.excess_reserves,2):,.0f}
            - LOANS RECEIVABLE: {round(self.loan_balance,2):,.0f}
    LIABILITES - {round(self.total_liabilities,2):,.0f}: 
        - CHECKED_DEPOSITS: {round(self.checked_deposits):,.0f}
        - OWNERS EQUITY: {round(self.owners_equity):,.0f}
"""
        return output


