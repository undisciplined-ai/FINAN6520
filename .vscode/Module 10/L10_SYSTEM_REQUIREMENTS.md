# PROPERTY MODELING

### Scenario
We are a real estate management fund who recently raised capital from limited partners and are ready to invest in our local market. Our strategy relates to investing in residential properties and we will not develop any new property. Before we invest in the market we want to model our theorized portfolios. We have a need for a portfolio modeling tool. We are biased towards using a programmatic implementation rather than an excel model. 

<!-- <h3 style="color: #A5B685;">Goal</h3> -->
### Goal
Develop a modeling tool to display the lifetime value of a portfolio of residential properties. 

## Requirements
#### Property Requirements

* All properties will be modeled out to 2070. 

* Ability to model the lifetime of a loan related to a property. 
    * Utilize a traditional mortgage calculator
        * Loan Model is based on: 
            * Property Value
            * Down Payment Value
            * Interest Rate
            * Loan Lifetime (Years)
            
        * Data tracking should display the lifetime values of all following variables per month:
            * Beginning Loan Balance
            * Payment Value
                * Interest Paid
                * Principal Paid 
            * Ending Loan Balance
            * Equity
        * Lifetime data tracking of property should accommodate the payoff of debt. 

* Data tracking of property operations. 
    * Revenue
    * Expense
        * Should be dynamic as we will not always have to service debt. 
    * Net Income

    * Revenue and Expense will have an escalation value applied monthly. 

* Allows for multiple property types. 
    * We have two main types we provide, luxury and standard units. 
    * Each unit type must have different economics, but both have the following:
        * Square Feet
        * Dollar Value per Square Foot
        * Vacancy Rate
            * Percent value of units not occupied. 
        * Expense Ratio
            * Percent value of rent attributed to expenses.
        * Added Profit Margin
        * Per Unit Rent
        * Per Unit Expense
    
#### Portfolio Requirements

* Generic Pieces:
    * Year Portfolio is Established
    * Capital Pool
        * All properties will be purchased from this capital pool.
        * Some accommodation is necessary to prevent purchasing a property when there is not enough capital. 
        * All properties will receive a down payment value equal to 10% of the current capital pool. 
    * Model lifetime, which is 2070 like the underlying properties. 
    * Property database

* Accommodation of one or more properties. 

* Aggregate operations report of all properties
    * Portfolio level view of revenue, expense, and net income. 

* Aggregate loan models of all properties. 
    * Portfolio level view of loan liabilities in the portfolio. 


## Class Functionality
#### Residential Property Class

* Initialization Method
    * Setup method for instance variables.
* Payment Method
    * Derives the monthly payment of the property's loan. 
* Loan Model Method
    * Generates the lifetime value of the loan. 
* Monthly Operations Statement
    * Generates instances variables related to revenue and expenses. 
* Operations Report
    * Actual aggregation of property income statement values. 

#### Portfolio Class

* Initialization Method
    * Setup method for instance variables.
* Purchase Property
    * "Purchase" property by creating an instance of residential property in the portfolio database. 
    * Inputs for this method should be a list, meaning we can pass in all potential properties as one list.
* Query Property
    * Gather a specific property object by key key from portfolio database.
* Aggregate Property Data   
    * Aggregate all properties in the database to generate a portfolio. 
    * This includes operations reports and loan reports. 
   