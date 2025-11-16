
import numpy as np

student_name = "LAST_FIRST_UNID"

####################################
######### SIMULATION CLASS #########
####################################

### Overview ###
## This simulation class will allow us to ensure all of our moving parts are operating correctly. 
## We will use Bank, Branch, and Database class instances simultaneously in this new class.
## Our goal is to run a simulation by means of creating branches, accounts, running transactions and providing loans. 

class Simulation:
    ######################
    ##### Question 1 #####     
    ######################
    ### Define the initialization method. 
    ### Overview ###
    ## This is your standard init function found in most classes. 
    ## It will take in a bank class object only. 
    ## This object will set up a single self referencing object. 

    ### Instruction ###
    ## You have a single input, which is a bank class. 
    ## Assign the input to a class attribute called "bank".
    def __init__():
        pass
        
    ######################
    ##### Question 2 #####     
    ######################        
    ### Define the "open_branches" method.
    ### Overview ###
    ## This method will work to open a prescribed amount of branches for a given bank class. 
    ## Recall the class generator we built in class. We built out a method in our bank class to automatically 
    ## create a branch and handle the necessary background processing. 
    ## We'll use that generator here to build out a target set of branches. 
    
    ### Instruction ### 
    ## Your function has a single integer input called "branch_count".
        ## The single input represents the number of branches to "open".
    ## Assign branch_count as a class attribute by the same name.     
    ## Create a for loop to run at the length of branch_count.
    ## Inside your loop:
        ## Use the "open_branch" generator method from the Bank class to open a new branch. 
    ## Your method does not have a return statement. 
    def open_branches():
        pass

    ######################
    ##### Question 3 #####     
    ######################     
    ### Define the "open_accounts" method
    ### Overview ###
    ## Here we are working to open a set number of accounts at each branch of our bank. 
    ## We'll pass in a target number of accounts for each branch and open them using our developed methods. 

    ### Instruction ###
    ### Your function has a single integer input called "account_count"
    ## First, assign account_count as a class attribute by the same name. 
    ## Next, you'll write a for loop which will run with a range.
        ## The range runs from one to the length of the branch_count plus one. 
        ## Your iterable value will be "id"
    ## Inside your loop:
        ## Gather the branch object from the database. 
            ## You'll use the id from the loop as a key to select the object from the bank class database. 
        ## Write another for loop to run at the length of account_count.
            ## The iterable value will not be used in the loop. 
        ## Inside your loop:
            ###** Utilize numpy random seed set to 47. **###
            ## Create a variable called "account_deposit". This will hold a dollar amount to be deposited. 
                ## Using Numpy generate a random integer value from 1,000 to 100,000 and assign to account_deposit. 
            ## Pass account_deposit into the "create_account" method from the branch class to create the account. 
    ## Your method does not have a return statement.  
    def open_accounts():
        pass

    ######################
    ##### Question 4 #####     
    ######################    
    ### Define the "transactions" method
    ### Overview ###  
    ## Here we will simulate account activity at each branch. 

    ### Instruction ###
    ## Your method takes in a single integer input called "transaction_count"
    ## First, you'll write a for loop which will run with a range.
        ## The range runs from one to the length of the branch_count plus one. 
        ## Your iterable value will be "id"    
    ## Inside your loop:
        ## Gather the branch object from the database. 
        ## Write another for loop from one to the length of account_count plus one. "account" will be your iterable value. 
        ## Inside your loop:
            ## Write another loop to run the length of transaction_count. Your iterable value will called "i"
            ## Inside your loop:
                ###** Utilize numpy random seed set to 47. **###
                ## Create a variable called "dollar_value". This will hold a dollar amount to be deposited or withdrawn 
                    ## Using Numpy generate a random integer value from 1,000 to 10,000 and assign to dollar_value.             
                ## if i is an even number, withdraw the dollar amount, else deposit the dollar amount.
                    ## You will be using the branch class methods withdraw and deposit for this.
                    ## Both methods require the account id to be passed in before dollar_value. 

    ## Your method does not have a return statement. 
    def transactions():
        pass


    ######################
    ##### Question 5 #####     
    ######################    
    ### Define the "loans" method
    ### Overview ###  
    ## In this method we will work with out credit business line. 
    ## We'll simulate a target amount of loans at each branch.
    ## Each branch will handle credit worthiness, offer/not offer the loan, then realize payment of the loan back to the branch. 

    ### Instruction ###
    ### Your method takes in a single integer input called "loan_count"
    ## First, you'll write a for loop which will run with a range.
        ## The range runs from one to the length of the branch_count plus one. 
        ## Your iterable value will be "id"    
    ## Inside your loop:
        ## Gather the branch object from the database. 
        ## Write another for loop from one to the length of account_count plus one. "account" will be your iterable value. 
        ## Inside your loop:
            ## Write another loop to run the length of loan_count. Your iterable value will not be used inside the loop. 
            ## Inside your loop:
                ###** Utilize numpy random seed set to 47. **### 
                ## Create a variable named "term"
                    ## Assign 24, 36, 48, 60, or 72 to term based on a random selection made by Numpy. 
                ## Create a variable named "urban_rural"
                    ## Assign 0, 1, or 2 to urban_rural based on a random selection made by Numpy.  
                ## Create a variable named "loan_principal"
                    ## Assign a dollar value from 10,000 to 100,000 to loan_principal based on a random selection made by Numpy.     
                ## Pass account, term, urban_rural, and loan_principal into the branch class method consumer_credit_model
                ## Pay off the loan balance using the branch class method payoff_account_loan       
                            
    ## Your method does not have a return statement. 
    def loans():
        pass

    ######################
    ##### Question 6 #####     
    ###################### 
    ### Define the "run_simulation" method
    ### Overview ###   
    ## Here we will use all of the previous methods and run our simulation. 
    ## This functions is the most important since it powers the simulation. 
                     
    ### Instruction ###
    ## Your method has four integer inputs:
        ## "branches", "accounts", "transactions", and "loans"
    ## All of the below functions are used with the self keyword. 
    ## Run the open_branches method using the branches input
    ## Run the open_accounts method using the accounts input
    ## Run the transactions method using the transactions input
    ## Run the loans method using the loans input
    ## Utilize the "balance_sheet_aggregation" method of the bank object to aggregate all the previous activity. 
    ## Return the statement "Simulation Complete."
    
    def run_simulation():
        pass