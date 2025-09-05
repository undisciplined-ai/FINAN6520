#### CONTROL FLOW AND LOGIC

## Logic in programming allows us to have pathways for code to operate in. If/when certain conditions are met, programs 
## begin to do different portions of code. "Logic" in this case relates to conditional statements. 

## Conditional statements:
# A statement which has a hypothesis and a conclusion
# If A then B 
    # This is a simple conditional statement.
    # If A is of some state, in our case "True", then our program will do B. 

# Conditional statements in python are boolean, i.e. True or False. 
# Boolean values can be objects themselves or the result of some comparison between objects. 

## Booleans
## Takes in a comparison of one or more booleans
## Booleans result from binary/logical algebra. 
## Solid walkthrough on the behind the scenes
## https://byjus.com/maths/boolean-algebra/#:~:text=Boolean%20algebra%20is%20the%20category,Binary%20Algebra%20or%20logical%20Algebra.

True # --> 1
False # --> 0

## Conditional practice

my_var = False

another_var = True

### Two objects to test with native comparison operation

### And / Or
# and / & ---> two or more items should be true
# or / | ---> one or more objects should be true. 
# not / != --> Python built in method for determining if a variable is an object
    # Only unary operater in python (Single input)
    # Always returns a boolean data type

# is --> Python built in method for determining if two variables refer to the same objectn (==)
# in ---> Built in method, returns true/false if a target value is found in an iterable. 
    ## This will come up later. 
## Traditional Comparison Operators
## We'll use these downstream. 
# > < >= <=

my_var == my_var
my_var is my_var

# Not checks if an object is true or false. Returns the opposite of the single object
not my_var # True

# Not True is False
not 1 # False
not 0 # True

# For an And operator to be satisfied, both comparisons must result in true

my_var & my_var # Returns False

(my_var is my_var) & (my_var == my_var) # True

(my_var is my_var) & (another_var) # True

(my_var is my_var) & (another_var) # True

(my_var is my_var) and (another_var == another_var) # True

(my_var == my_var) or another_var # True

(my_var == another_var) or another_var # True

(my_var == another_var) or my_var # False

(my_var is another_var) | my_var # False

## A bit wonky 

not another_var # False

another_var is another_var # True

another_var is not another_var ## False

another_var is not my_var ## True

True is not False ## True

True != False # True

True is not True # False

True is not another_var #False

## Booleans are numbers, meaning they can be manipulated by numbers and arithmetic 

True + True # 2
True - 1 # 0 
bool(True-1) # False
bool(True+True) # True
## ANY NUMBER OTHER THAN 0 RESULTS IN A TRUE WHEN USING BOOL()
## Other than Empty objects, Bool() returns true

# Nested Conditional
((my_var is my_var) and another_var) # True

((my_var or another_var) or another_var) and (another_var or (my_var)) # True
#((True) or True) and (True or (False))
# True and True
# True

(((my_var and another_var) and another_var) and my_var) and my_var # False
# (((False) and True) and False) and False
# ((False) and False) and False
# (False) and False 
# False


## Simple Number Examples

1 > 0 # True
1 != 0 # True
1 == 0 # False
1 <= 1 # True
1 < 2 # True
1 >= 0 # True
1 == 1 # True
1 is 1 ## This throws a warning but is still True
# <stdin>:1: SyntaxWarning: "is" with a literal. Did you mean "=="?
## This is operator is referencing object checks. 1 is a built in "literal" in the language and not a stand alone object. 
# A literal in Python is a syntax that is used to completely express a fixed value of a specific data type.
# Us the standard conditional statements to compare literals, not the built in reserve words


###########################################################
## Lets get a bit more complicated -- Have class spend 10-15 minutes doing this on their own
##### SOLVE BY HAND #####

x = True
y = False

# 1
((((x is y) and x) or y) or x)

# 2
(((x is not y and x) and y is not x) and (False and True) and False)


# 3 
bool(((bool(1-0) and True or False and True and False and True) or False) + 1)

# 4
(((((bool(True) + (1 == 1) and (2 <= 2)) or False and True) is not False) > 0 ) and False ) or False

# 5 
(True is ((bool((((10 * 69 < 100) * 42)^2 > 100000000) + 1) + True and True) is True and not False or False) and (x == y))

# 6
## This one is just dumb and mean and rude

bool((True and 1==0) is ((((True is True) and False is not False) is bool(4) and not 4) or True == 1) * 1) and True | (False | True)

##### Control Flow
## control flow allows us to create pathways for our systems. 
## Certain things happen, then other portions of code run.

## If statements
# if 
# elif
# else

# Basic idea
# I have a condition, if it is of value x, do this, else do that
variable1 = True

if variable1 == True:
    print('super cool')
else:
    print('so sad')

## PROPER PYTHON
## When a variable is known to be a boolean we use this type of syntax. 
if variable1:
    print('super cool')
else:
    print('so sad')    

if variable1:
    print('super cool')
elif variable1 == 4:
    print('for some reason this is set to 4')
else:
    print('so sad')

## You can have many elif statements, technically as many as you'd like. 
if variable1:
    print('super cool')
elif variable1 == 4:
    print('for some reason this is set to 4')
elif variable1 == 8:
    print('for some reason this is set to 8')    
else:
    print('so sad')

## Remember the "in" statement?

name_list = ['Jeff','Steve','Zac']

target_name = 'Zac'

if target_name in name_list:
    print('Target name in list')
else:
    pass    

## IF STATEMENTS ARE SOLVED INCREMENTALLY.
## Each conditional check is checked before the next
## if any if/elif is satisfied your program will branch into that space for the remainder of the program
## i.e. no other conditions will be met. 

### OTHER CONTROL FLOW CONCEPTS
### pass
# Requests the segment to not continue processing 
# if a condition is met, pass the remaining code in the segment. 
# If in a loop, a pass statement will not kill the current loop instance, 
# rather it will finish processing the code segment. 


### continue
# Similar to pass, this allows a condition to be met, but the remaining portion of the segment to run 
# If a continue is seen in a loop, the loop instances will stop and begin again. 


### break
## stops a segment of code from continuing its run. Generally useful in loops.
## When a condition is met, break the segment etc

###### LOOPS
## Loops deal with iterative objects. Iterables are quite literally objects we can iterate upon. 
## Loops do exactly as they sound, they run in a "circle" persay until they are finished looping over an iterable, 
## A condition is met, or they are told to stop explicitly. 
## Python loops are "AUTO-INCREMENTING"
## Meaning interally python knows to continue looping if provided logic holds
## Other languages request incrementation by the program author. 

# increment = 0
# for i < 5:
    # do task
    # increment+=1


## This for loop will iterate over our variable
# i is a placeholder variable assigned a value in each subsequent loop. 
# In this case we have have an object of length 5, which means we will "loop" 5 times
variable2 = [1,2,2,3,3]

for i in variable2:
    print(i)

### loops are great because we can interact with objects as well as iterate upon them

variable2 = [1,2,2,3,3]

variable3 = []
for i in variable2:
    inner_var = i * 2
    print(inner_var)
    variable3.append(inner_var)

## You also do not have to use the iterable value
## the _ is a temporary variable here and is not saved outside of the loop mechanism. 

for _ in variable3:
    print('this is a super cool loop')
    
#### Examples of pass/continue/break

my_list = [1,2,3,3,3,3,3,3]

# Continue
for i in my_list:
    if i == 2:
        print("Number is 2")
        continue
    print(i*2)


# pass
for i in my_list:
    if i == 2:
        print("Number is 2")
        pass
    print(i*2)    

# break
for i in my_list:
    if i == 2:
        print("Number is 2")
        break
    print(i*2)        


### Lets make some patterns with loops
## Lets create a triangle using hashtag symbols
# Start with a single value in the first row, then grow by length one with each loop. 

######## HAVE CLASS PONDER ON HOW TO DO THIS FOR A MOMENT #########

for i in range(1,10):
    for character in range(i):
        print('#',end='')
    print('')

## Lets just make a triangle:

# we need a defined height to work with. 
height = 15

# Loop throught range of 1 to height +1
for i in range(1, height + 1):
    ## create spaces of height minus 1, then add the number of character elements to that shape. 
    print(' ' * (height - i) + '# ' * i)    


### LOOPS INTERACTING WITH DICTIONARY

list1 = ['key1','key2','key3','key4','key5','key6']
list2 = ['this','is','a','list','of','values']
my_dict = dict(zip(list1,list2))

for key,value in my_dict.items():
    print(key,value)

##### LIST COMPRHENSION

# List comprehension offers a shorter syntax when you want to create a new list based on the values of an existing list.

animals = ["cat", "dog", "horse", "kiwi", "chicken"]
my_list = []

for i in animals:
  if "e" in i:
    my_list.append(x)

print(my_list)

animals = ["cat", "dog", "horse", "kiwi", "chicken"]

my_list = [i for i in animals if "e" in i]

print(my_list)

# ** Conditional statement is optional ** #
# newlist = [expression for item in iterable if condition == True]

## Creates the same list, but uses the internal variables in "my_lsit"
[i for i in animals]

## Utilizing a previously built iterable, we generate a list of the same length wiht new values
['NEW_VALUE' for i in animals]


## utilizing the range object and the _ placeholder 
### Generate a list of "True" values of length 10. 
var1 = True

[var1 for _ in range(0,10)]


## While 
### A conditionally controllable looping mechanism
## Runs until a condition is met or otherwise told to break the run. 
## Enter Loop
## Test Condition
    # If True --> Perform Loop tasks
    # All true conditions run the while loop
    # If False --> Exit looping

while True:
    print('Nice')
    ## THIS WILL RUN FOREVER, BE CAREFUL. 
    # Control/option C will kill a program. 

    ## break is for notes only. 
    break


## Similar to our conversation about other language for loops
condition = 1

while condition < 10:
    print('cool')
    # will print "cool" 9 times
    condition+=1


## Usually while loops utilize some conditional variable that alters in another set of logic
## While loops are great for keeping programs alive when interacting with users

# input()
# This is a tool for a user to input a string value into a program.

control_var = True

while control_var:
    number = int(input('Enter a number: '))
    if number == 5:
        print('Killing Program')
        control_var = False
    else:
        print(number)
        pass

## THIS EXAMPLE HAS A SEGWAY ERROR POTENTIAL

## User can input something that does not convert well to an integer. 

### Try
## Quite literally "try" the following code snippet

## Except
## a catch area for a certain type of exception
## There can be may one or more exception types for any try statement
## 

### Finally
## Portions of code always run along side the other two statements.

control_var = True

while control_var:
    try:
        ## Try to run this code segment
        number = int(input('Enter a number: '))
        if number == 5:
            print('Killing Program')
            control_var = False
        else:
            print(number)
            pass
    except ValueError:
        ## If a ValueError results from a bad input, do the following
        print("That's not a value integer input.")
        ## Continue to the top of the loop and attempt again. 
        continue
    ## Brings the code pathway back into the original while loop level. 
    finally:
        print('I just think running this line is neat.')

#################### EXAMPLE SECTION ####################

## Example 1
my_list = [4,5,6,6,7,7,7]

for i in my_list:
    if i % 2 == 0 :
        ## F-strings are great. 
        print(f'The number {i} is an even number')
    else:
        continue

### Example 2
# A list of even numbers
scores = [75,85,96,100,100,20,40]

name_list = ['Jeff', 'Steve', 'Zac', 'Sarah', 'Stacy', 'Ashley', 'Peggy']

grade_payload = []

for score in scores:
    if score >= 90:
        grade_payload.append("A")    
    elif score >= 80:
        grade_payload.append("B")
    elif score >= 70:
        grade_payload.append("C")
    else:
        grade_payload.append("F")

course_grades = dict(zip(name_list,grade_payload))    

print(course_grades)

## Example 4:
### Guess a number between 1 and 50
import random
secret_value = random.randint(1,50)
## Placeholder list with initial value of zero
guesses = [0]
while True:
    ## Input fn for user to play the game
    user_guess = int(input("I have a value between 1 and 50. What do you think it is? "))
    if user_guess < 1 or user_guess > 50:
        ### If this is true, then we go back to the top of the while loop
        print('Try guessing a number between 1 and 50 instead. ')
        continue
    # here we compare the player's guess to our number
    if user_guess == secret_value:
        print(f'Thats correct and it only too you {len(guesses)} guesses.')
        break
    # if guess is incorrect, add guess to the list
    guesses.append(user_guess)
    # when testing the first guess, guesses[-2]==0, which evaluates to False
    # and brings us down to the second section    
    if guesses[-2]:  
        if abs(secret_value-user_guess) < abs(secret_value-guesses[-2]):
            print('Getting Close')
        else:
            print('Not very close!')
    else:
        if abs(secret_value-user_guess) <= 10:
            print('Getting Close')
        else:
            print('Not very close')

### Example 5:
### Here we'll make a nested dictionary object to handle a fun set of if statements. 
## Basic goal:
# We get a response depending on the day of the week, if we have office hours, and if its a nice day outside.

## We need to create some data, then write our response pipeline. 

## Enumerate is another reserved word
# Generates a tuple of an index and value to be utilized in a loop.

fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits):
    print(f"Index {index}: {fruit}")    

## Creating Data:
days_data = {}

days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

days_attributes = {}

weekend_list = [False,False,False,False,False,True,True]
weather_list = [False,False,True,True,False,True,True]
office_hours_list = [False,False,False,False,False,True,False]

for i, day in enumerate(days):    
    days_data[day] = {'is_weekend':weekend_list[i],
                      'is_sunny':weather_list[i],
                      'have_office_hours':office_hours_list[i]}
    
## Generating Responses:    
for day in days:
    is_weekend = days_data[day]['is_weekend']
    is_sunny = days_data[day]['is_sunny']
    having_office_hours = days_data[day]['have_office_hours']
    print(f'Day of the Week: {day}')
    if is_weekend:
        if is_sunny:
            print('Wow its so great outside!')
            if having_office_hours:
                print('TOO BAD WE HAVE OFFICE HOURS!')
            else:
                print("I'm going on a nice walk. ")
        else:
            print('Looks like a good day to be inside.')
            if having_office_hours:
                print('Good thing I have office hours to keep me occupied.')
            else:
                print("Im going to make some tea and watch a movie")    
    else:
        print("No free time for you, go to work!")

####################################################################################################################


## ONLY IF THERE IS A NEED FOR MATERIAL TBH
# maybe we use python 3.1 and use case when? Seems wise 
# match x:
#   case xyz:
#        do thing
