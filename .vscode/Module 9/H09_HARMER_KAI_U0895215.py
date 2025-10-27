student_name = "HARMER_KAI_U0895215"

##########################
##### Question 1 - 3 #####
##########################
######### VEHICLE ########

### Breadcrumb One:
## Creating an instance of your Vehicle class with the inputs of 
## 2018, Black, Audi, S3 will result in the following:
## BLACK 2018 AUDI S3

### Breadcrumb Two:
## Utilizing both check_fuel and refuel will result in None. 
## RECALL WHY THIS WILL BE THE CASE. 

class Vehicle:
    ### Remove the "pass" when finished. 

    ##########################
    ####### Question 1 #######
    ##########################
    ### Instantiate your class with the __init__ constructor. 
    ### This class will have 4 inputs during instantiation:
    ## Year: int -- Year of vehicle
    ## Color: str -- Exterior color -- set all letters as uppercase
    ## Brand: str -- The brand of vehicle -- set all letters as uppercase
    ## Model: str -- The model of the car -- set all letters as uppercase

    ### You'll also have other class attributes to set during instantiation:
    ## Terrain Type -- Value of "NULL"
    ## Fuel Level -- Value of 100, representing a percentage of fuel in the tank. 
    ## Efficienty -- Value of 0
    ## Top Speed -- value of 0

    def __init__(self, year, color, brand, model):
        self.year = int(year)
        self.color = str(color).upper()
        self.brand = str(brand).upper()
        self.model = str(model).upper()
        self.terrain_type = "NULL"
        self.fuel_level = 100
        self.efficiency = 0
        self.top_speed = 0

    ##########################  
    ####### Question 2 #######
    ##########################
    ### Create a string representation method. 
    ## You'll return an f-string of color, year, brand, and model all seperated by single spaces. 
    ## Example output: "BLACK 2023 AUDI R8"
    def __str__(self):
        return f"{self.color} {self.year} {self.brand} {self.model}"
        
    ##########################
    ####### Question 3 #######
    ##########################
    ### Create two empty methods.
    ## First, check_fuel(), which will only pass for now
    ## Second, refuel(), which will only pass for now
    def check_fuel(self):
        pass
    def refuel(self):
        pass
    

##########################
##### Question 4 - 8 #####
##########################
####### Automobile #######

####### Question 4 #######
### Pass the vehicle class into automobile. 

class Automobile(Vehicle):
    ### Remove the "pass" when finished. 
    pass
    ##########################
    ####### Question 4 #######
    ##########################
    ### Instantiate your class with the __init__ constructor. 
    ## You'll pass in the same 4 values as the Vehicle class:
    ## Year, color, brand, and model. 
    ## These must be passed to the Vehicle class, there are two ways to do this activity. 
    #*** Use the most efficient and future-proof option. ***#
        ## Refer to lecture materials if you're lost. 

    ### You'll be reassigning/creating other variables in the instantiation:
    ## Terrain Type -- Value of "LAND"
    ## Fuel Size -- Value of 20, representing 20 gallons of fuel. 
    ## Efficiency -- Value of 35, representing 35 Miles Per Hour (MPH)
    ## Top Speed -- Value of 250, the top speed possible for the vehicle. 
    def __init__(self, year, color, brand, model):
        super().__init__(year, color, brand, model)
        self.terrain_type = "LAND"
        self.fuel_size = 20
        self.efficiency = 35
        self.top_speed = 250

    ##########################
    ####### Question 5 #######
    ##########################
    ### Alter the functionality of the two abstract methods found in Vehicle. 
    ### check_fuel: you'll return an f-string saying the following:
        ## Example output: "Fuel "Fuel is at 100%"
    ### refuel: 
      ## Using the current fuel level, create a local variable representing the amount of fuel you used to refuel. 
        ## Round your output to 2 decimal places
      ## Set the fuel level back to 100%. 
      ## return an f-string saying the following:
        ## Example output: "Filled 40% of fuel tank for full capacity."    
    def check_fuel(self):
        return f"Fuel is at {self.fuel_level}%"

    def refuel(self):
        filled = round(100 - self.fuel_level, 2)
        self.fuel_level = 100
        if filled == 0:
            filled_str = "0"
        else:
            filled_str = f"{filled:.2f}"
        return f"Filled {filled_str}% of fuel tank for full capacity."

    ##########################
    ####### Question 6 #######
    ##########################
    ### Create a class method called "r8"
    ### You'll use this method to return a class object with the following values as inputs. 
    ## Year -- 2023
    ## Color -- "BLACK"
    ## Brand -- "AUDI"
    ## Model -- "R8"
    @classmethod
    def r8(cls):
        return cls(2023, "BLACK", "AUDI", "R8")
    
    ##########################
    ####### Question 7 #######
    ##########################
    ### Create a class method called "roma"
    ### You'll use this method to return a class object with the following values as inputs. 
    ## Year -- 2023
    ## Color -- "RED"
    ## Brand -- "FERRARI"
    ## Model -- "ROMA"
    @classmethod
    def roma(cls):
        return cls(2023, "RED", "FERRARI", "ROMA")
    
    ##########################
    ####### Question 8 #######
    ##########################
    ### Create a static method called "honk"
    ## The method will only return the following:
        ## "HONK"
    @staticmethod
    def honk():
        return "HONK"
    
    ##########################
    ####### Question 9 #######
    ##########################
    ### Create a method called "drive"
    ### This method has one input:
    ## distance:int -- An integer value representing miles to be driven. 

    ### Create a local variable representing gallons of gas used on the trip. 
    ## It will be filled with the value of distance divided by efficiency as a float variable. 
        ## Round this value to the second decimal. 
        #** Don't overthink this. **#
            ## Simply we are dividing out distance by how efficient the vehicle is. 
    ## Create a Percentage value representing the fuel used on the trip. 
        ## Divide gallons used by the size of the fuel tank, then multiply by 100. This is a whole percentage value. 
    ### Set the fuel level as the difference between the current fuel level and the fuel used to travel the distance. 
    ## The outcome is rounded to the second decimal place. 
    ### return an f-string in the following format:
        ## Example Output: "BLACK 2019 AUDI R8 drove 40 miles and used 5 gallons of gas."        
    def drive(self, distance):
        gallons_used = round(distance / self.efficiency, 2)
        percent_used = gallons_used / self.fuel_size * 100
        self.fuel_level = round(self.fuel_level - percent_used, 2)
        return f"{self} drove {int(distance)} miles and used {gallons_used:.2f} gallons of gas."

#######################
###### Question 10 ####
#######################
### Write a generator function with a single integer input. 
### Inside of the function do the following:
## Create an empty list
## Write a for loop to run from range 0 to the integer value passed into the function
    ## Your iterable value will be represented by "i"
## If i is even, create a Ferrari Roma class and add it into your empty list.
## Otherwise, create an Audi r8 class and add it into your empty list. 
## When the for loop is complete, return the list filled with class objects. 

def vehicle_generator(n):
    output = []
    for i in range(0, int(n)):
        if i % 2 == 0:
            output.append(Automobile.roma())
        else:
            output.append(Automobile.r8())
    return output

def vehicle_generator_solution(n):
    return vehicle_generator(n)
