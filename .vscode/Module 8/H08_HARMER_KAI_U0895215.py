import numpy as np

student_name = "HARMER_KAI_U0895215"

#############################
####### Question 1 - 4 ######
#############################
######### CALCULATOR ########

class Calculator:
    ### Remove the "pass" when finished. 

    ##########################
    ####### Question 1 #######
    ##########################
    ### Create an "add" method.
    ## Your method has two number inputs. 
    ## Add input one to input two and return the result. 
    def add(self, number1, number2):
        return number1 + number2

    ##########################
    ####### Question 2 #######
    ##########################
    ### Create an "subtract" method.
    ## Your method has two number inputs. 
    ## Subtract input one and input two and return the result. 

    def subtract(self, input1, input2):
        return input1 - input2
    
    ##########################
    ####### Question 3 #######
    ##########################
    ### Create an "multiply" method.
    ## Your method has two number inputs. 
    ## Multiply input one and input two and return the result. 

    def multiply(self, input1, input2):
        return input1 * input2
    
    ##########################
    ####### Question 4 #######
    ##########################
    ### Create an "divide" method.
    ## Your method has two number inputs. 
    ## Division by zero (0) is not a legal math function. 
    ## If input two is zero, continue into a new code section, else return "Cannot divide by zero."
        ## Divide input one by input two and return the result. 

    def divide(self, input1, input2):
        # Return an explanatory message for division by zero
        if input2 == 0:
            return "Cannot divide by zero."
        result = input1 / input2
        if isinstance(result, float) and result.is_integer():
            return int(result)
        return result

#########################
##### Question 5 - 6 ####
#########################
######### CIRCLE ########

class Circle:
    """Circle data: radius, diameter, area, circumference."""
### Remove the "pass" when finished. 
    
    ##########################
    ####### Question 5 #######
    ##########################
    ### Instantiate your class with the __init__ constructor. 
    ## You have a single input called "r" which is a number. 
    ## Create the following instance variables:
        ## radius, equal to the input "r"
        ## diameter, equal to (2 x r)
        ## area, equal to (pi x r^2)
        ## cicumference, equal to (2 x pi x r)

    #### NOTES: utilize numpy for any reference to pi (π).

    def __init__(self, r):
        self.radius = r
        self.diameter = 2 * r
        self.area = np.pi * (r ** 2)
        self.circumference = 2 * np.pi * r

    ##########################
    ####### Question 6 #######
    ##########################
    ### Create a string representation method. 
    ## Your string representation will return a formatted-string in the following way:
        ### CONSIDER THE \n STRING TOOL!
    ## Radius: W
    ## Diameter: X
    ## Area: Y
    ## Circumference: Z
    

    def __str__(self):
        return (
            f"Radius: {self.radius}\n"
            f"Diameter: {self.diameter}\n"
            f"Area: {self.area}\n"
            f"Circumference: {self.circumference}"
        )

#########################
#### Question 7 - 10 ####
#########################
####### EMPLOYEE ########

class Employee:
    """Employee record with name, salary and department."""

    ### Remove the "pass" when finished. 
      
    ##########################
    ####### Question 7 #######
    ##########################
    ### Instantiate your class with the __init__ constructor. 
    ## You have four inputs:
        # first_name: str
        # last_name: str
        # salary: int
        # department: str
    ## Each of these inputs must be assigned to an instance variable. 
    ## Ensure all string values are uppercase. 

    def __init__(self, first_name, last_name, salary, department):
        self.first_name = first_name.upper()
        self.last_name = last_name.upper()
        self.salary = salary
        self.department = department.upper()

    ##########################
    ####### Question 8 #######
    ##########################
    ### Create a "reassign_department" method.
    ## This method takes in a single string input. 
        ## This input is a newly assigned department. 
    ## Update the department instance variable with the input from this method. 
    ## Ensure all string values are uppercase. 

    def reassign_department(self, new_department):
        self.department = new_department.upper()

    ##########################
    ####### Question 9 #######
    ##########################
    ### Create a "update_salary" method. 
    ## This method has a single number input.
        ## The provide input will be used to update the current salary, i.e. give the employee a raise. 
    ## Add the input value to the salary instance object.

    def update_salary(self, amount):
        self.salary += amount

    
    ###########################
    ####### Question 10 #######
    ###########################
    ### Create a string representation method. 
    ## Your string representation will return a formatted-string in the following way:
    ## Name: FIRST LAST
    ## Salary: SALARY
    ## Department: DEPARTMENT

    def __str__(self):
        return (
            f"Name: {self.first_name} {self.last_name}\n"
            f"Salary: {self.salary}\n"
            f"Department: {self.department}"
        )
