from BANKING_FULL_CODE import Bank,Simulation


##################################################
#################### HOMEWORK ####################
##################################################

# ## Input
branches = 15
accounts = 10
transactions = 20
loans = 0

breadcrumb_bank = Bank('BREADCRUMB BANK', 2023, 1_000_000_000)
    
submission_sim = Simulation(breadcrumb_bank)


submission_sim.run_simulation(branches = branches,
                              accounts = accounts,
                              transactions = transactions,
                              loans = loans)


print(breadcrumb_bank)

### BREADCRUMB OUTPUT

#### Corporation: BREADCRUMB BANK, established 2023
#### BRANCHES: 15
#### ACCOUNTS: 150
#### BALANCE SHEET:
####     ASSETS - 1,007,811,700
####         - TOTAL RESERVES: 801,920,568
####             - REQUIRED: 80,192,057
####             - EXCESS: 721,728,511
####             - LOANS RECEIVABLE: 0
####     LIABILITIES - 1,007,811,700: 
####         - CHECKED_DEPOSITS: 7,811,700
####         - OWNERS EQUITY: 794,108,868