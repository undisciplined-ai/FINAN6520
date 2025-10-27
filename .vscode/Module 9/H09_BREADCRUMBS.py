import H09_HARMER_KAI_U0895215 as H09

################################
######## Question 1 - 3 ########
################################

### Create an instance of your Vehicle class
breadcrumb_vehicle = H09.Vehicle(2018,'Black','Audi','S3')
print(breadcrumb_vehicle)
### BLACK 2018 AUDI S3
print(breadcrumb_vehicle.check_fuel())
### None
print(breadcrumb_vehicle.refuel())
### None

################################
######## Question 4 - 9 ########
################################

### Creating an instance of your Vehicle class with the inputs of 
### 2018, Black, Audi, S3 will result in the following:
breadcrumb_vehicle = H09.Automobile(2018,'Black','Audi','S3')
print(breadcrumb_vehicle)
### BLACK 2018 AUDI S3


### Checking your fuel after immediately creating the class will result in:
print(breadcrumb_vehicle.check_fuel())
### Fuel is at 100%

### Refueling your vehicle immediately after creating the class will result in:
print(breadcrumb_vehicle.refuel())
### Filled 0% of fuel tank for full capacity.

### Using the honk method will result in:
print(breadcrumb_vehicle.honk())
### HONK


### Driving 100 miles will result in an output of:
print(breadcrumb_vehicle.drive(100))
### BLACK 2018 AUDI S3 drove 100 miles and used 2.86 gallons of gas.

### Driving 100 miles will result in an output of:
print(breadcrumb_vehicle.drive(100))
### BLACK 2018 AUDI S3 drove 100 miles and used 2.86 gallons of gas.

### Checking your fuel after driving 200 miles will result in:
print(breadcrumb_vehicle.check_fuel())
### Fuel is at 71.4%

### Filling your tank of fuel after driving 200 miles will result in:
print(breadcrumb_vehicle.refuel())
### Filled 28.60% of fuel tank for full capacity.

### Utilizing the class method "r8" will result in:
print(breadcrumb_vehicle.r8())
### BLACK 2023 AUDI R8

### Utilizing the class method "roma" will result in:
print(breadcrumb_vehicle.roma())
### RED 2023 FERRARI ROMA

################################
########## Question 10 #########
################################

## Utilizing this function with an input of 2 will result in a list of two "Automobile" objects. 
## If you loop over the output and print each value you will see the following:
breadcrumb_payload = H09.vehicle_generator_solution(2)
for i in breadcrumb_payload:
    print(i)

### RED 2023 FERRARI ROMA
### BLACK 2023 AUDI R8