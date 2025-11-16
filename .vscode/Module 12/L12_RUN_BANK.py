from L12_RUN_BANK import Bank, Branch

# # ####### BRANCH #######
# 
# test_branch = Branch(1, 10_000_000, 0.10)

# # ### Initial Methods ###
# # ### Initial Branch, 10m Capital, 10% Reserve Rate
# print(test_branch)
# print(test_branch.check_branch_accounts())

# # ### Create and Check Account ###
# # ## Initial Cash Balance of 10k
# test_branch.create_account(10000)
# print(test_branch.check_account(1))
# print(test_branch.check_account(47))
# print(test_branch.check_branch_accounts())

# # ### Deposit and Withdraw ###
# # Initial Cash Balance of 10k
# test_branch.create_account(10000)
# test_branch.deposit(1,15000)
# test_branch.deposit(1,15000)
# test_branch.deposit(1,15000)
# test_branch.deposit(1,15000)
# test_branch.deposit(1,15000)
# test_branch.deposit(1,15000)
# test_branch.deposit(1,15000)
# test_branch.deposit(1,15000)

# test_branch.withdraw(1, 1000)
# print(test_branch.check_account(1))
# # # # ### Attempt to withdraw 10m
# print(test_branch.withdraw(1, 10000000))

# print(test_branch.check_branch_accounts())

# # ### Loans ### 
# test_branch.create_account(10000)

# # # # ### 36 months 100k loan for an Not city dweller resident. 
# print(test_branch.consumer_credit_model(1, 36, 2, 100_000))
# # # # ### 72 months 400k loan for an Urban resident. 
# print(test_branch.consumer_credit_model(1, 72, 1, 400_000))
# print(test_branch.check_account(1))

# print(test_branch.payoff_account_loan(1))
# print(test_branch.check_account(1))
# print(test_branch.check_branch_accounts())

# ####### BANK #######

# ### Initial ####
# zions = Bank("ZIONS",1873, 100_000_000)
# print(zions) 

# ### Branch Related Work ###
# # ### FIRST
# zions.open_branch()
# # print(zions.branch_database[1].check_branch_accounts())
# zions.branch_database[1].create_account(100_000)
# zions.branch_database[1].deposit(1, 4000)
# zions.branch_database[1].withdraw(1, 1000)
# print(zions.branch_database[1].check_branch_accounts())

# print(zions)
# ### SECOND
# print(zions.branch_database[1].consumer_credit_model(1, 12, 1, 1000))
# # print(zions.branch_database[1].check_branch_accounts())
# zions.branch_database[1].payoff_account_loan(1)
# print(zions.branch_database[1].check_branch_accounts())

### Balance Sheet Aggregation
# print(zions)
# zions.open_branch()

# for i in range(1,5):
#     zions.branch_database[1].create_account(100000)
#     print(zions.branch_database[1].deposit(i,4000))
#     print(zions.branch_database[1].withdraw(i,1000))

# zions.balance_sheet_aggregation()

# print(zions)


#### Homework

# # # Input
# branches = 15
# accounts = 10
# transactions = 20
# loans = 3

# from H12_BANKING_SOLUTIONS import SimulationSolution

# test_bank = Bank('STUDENT BANK', 2023, 1_000_000_000)
    
# submission_sim = SimulationSolution(test_bank)


# submission_sim.run_simulation(branches = branches,
#                               accounts = accounts,
#                               transactions = transactions,
#                               loans = loans)

# print(test_bank)