
### FOR THE REMAINDER OF CLASS WE WILL GET TO KNOW A FEW BASICS

## These will be done in a live python instance in terminal

### EVERYTHING IN PYTHON IS AN OBJECT

## when we create variables, python's underbelly references your variable name to an object.
## The object an be anything in the language. A class, function, strings, etc. 

## Objects have values and they have identities.
## Values are what object the variable is referencing to. 
## Identity is a location inside of computer memory where the object exists. 
## IDs are unique in memory. Even variables with the same value have differing Identities. 

#### VARIABLES

# a variable is placeholder for data/information
# the python community types variables in a particular way, referred to as "snake case"
# my_variable_name
# we have text paired with underscores. Variables are generally all lower case. 

# Constants are generally uppercase
# MY_CONSTANT


## CREATION
## Variable = Value 
my_var = 1

## Variables can be manipulated
my_var * 2

## Alter the value of a variable
### PYTHON IS A DYNAMICALLY TYPED LANGUAGE, MEANING WE DO NOT HAVE TO ASSIGN THE VARIABLE DATA TYPE ON CREATION OR UPDATE
my_var = 'hello'

## Assigned to another variable
my_var_2 = my_var
my_var_2
my_var

## Chained Assignment
x = y = z = my_var

x
y
z
my_var

## Multiple Assignment
# utilizing tuples in the background, we'll talk more about tuples
# a is equal to the first value
# b is equal to the second value
a, b = 300, 400
a
b

#### RESERVED WORDS
### These are all words with underlying use cases in the language.
### You should not be creating variables with these names as they will overwrite underlying tools.

# False	def	if	raise
# None	del	import	return
# True	elif	in	try
# and	else	is	while
# as	except	lambda	with
# assert	finally	nonlocal	yield
# break	for	not	
# class	from	or	
# continue	global	pass	

### OPERATORS
# Play value
x = 500
# + addition
# - subtraction
# * multiplication
# / division
# ** exponentiation
# % modulus
# // floor division

x + 50
x - 50
x * 2
x / 2
x ** 2
x % 2 # provides the remainder of a division
x // 2 # rounds result down to nearest whole number


x == 500
x == 400

# == is checks if values are equal to one another. 
# != is spoken as "Not Equal" 

### Assignment Operators

# __ the value on the right to the value referenced in the object and reassigns the object
# += addition
# -= subtraction
# /= division
# *= multiplication
# **= exponentiation

x = 500

# Updates value to 500 + 200
# etc
x += 200
x -= 200
x *= 200
x /= 200
x **= 200
x %= 2

### And / Or
# and / & ---> two or more items should be true
# or / | ---> one or more objects should be true. 
## We'll go over more logic next week. 

(4==4)&(5==5)

(4==4)and(5==5)

(4==4)&(5==5)and(6==6)

(4==5)&(4==4)

(4==4)|(5==5)

(4==4)or(5==5)

(4==3)or(4==2)

# > < >= <=
# comparison operators we all know and love
a = 5
b = 6

a < b

a <= b

b > a

b >= a

##### DATA TYPES
## 5 examples each
## Description
## type()
## The type reserved word allows us to check what data type our variable is referencing. 


## the type() keyword helps us understand what our object is. 
## Python has built in types and we can write objects with unique types. We'll discuss this later. 

## NUMBERS
## Int / Float
# Integers are whole numbers
## Not iterable. Numbers are numbers, they cannot be looped upon. 

my_int = 1
type(my_int)

my_int * 1

my_int % 2 

my_float = 2.0
type(my_float)

my_float + 1

my_float / 2

## LIST / ARRAY
# Iterable
# not restricted to one type per array/list
type([1,2,3])

a_list  = [1,2,3]
a_list

a_list[0] = 4
a_list

another_list = ['1',1,'one']
another_list

type(another_list[1]) # type of the first index in the list

## Removes last item
another_list.pop()

## Adds item to the end of the list
another_list.append(47)


## TUPLE
# imutable - meaning it cannot be mutated
# iterable
type((4,5))
tup = (4,5)
tup

tup[0] = 5

tuple([4,5]) # transforms list into a tuple

## DICTIONARY
# both keys and values can be any data type
# mutable - meaning it can be mutated
# can be hold many data types
# can be used as a "bucket" to hold data
# Iterable
type({'key':'value'})

### Dict keyword takes in key=value pairs in this format.
dict(key=4,value=5)

dict_1 = {'key':'value'}
dict_1

dict_1.keys() # Returns a list of keys

dict_1.values() # Returns a list of values

dict_1.update(key2 = 5)
dict_1

## Returns a list of each key:value pair as a tuple. 
dict_1.items()

# The zip object yields n-length tuples, where n is the number of iterables passed as positional arguments to zip(). 
# The i-th element in every tuple comes from the i-th iterable argument to zip(). This continues until the shortest argument is exhausted.
list1 = [1,2,3,3,3]
keys = ['key1','key2','key3','key4','key5']
dict(zip(keys,list1))

x = dict(zip(keys,list1))
### You can use the list() operator to transform the dict_items object to a list. 
### Then we can utilizing index selection on the dictionary pairs. 
list(x.items())[0]


### STRING
## Strings are character/text data. Notated by single or double quotes
### Iterable and we'll discuss more later. 
my_string = 'Hello'

my_string_2 = "Hello"

multi_string = """ Hi i am a really long string
you can write over many lines with this string and the language will know what to do with it. 
"""

### STRING BUILT IN FUNCTIONS
# https://www.w3schools.com/python/python_ref_string.asp

my_string.upper()
my_string.lower()

### Strings are iterable and can be manipulated like list objects
# input1[::-1]

my_string[0]

my_string[:0]

## Reverses the string
# The slice statement [::-1] means start at the end of the string and end at position 0, 
# move with the step -1, negative one, which means one step backwards.
my_string[::-1]


## BOOLEAN

True # represented by 1
False # represented by 0

## SET
## Much like lists with a few caveats
## They are immutable, i.e they cannot be altered once created. 
## Cannot contain duplicate information. 

set({'one','one','two'})

my_set = {"apple", "banana", "cherry"}

my_set

### DOES NOT EXECUTE
my_set[0]


###### Casting

x = 4
type(x)

x = float(x)
x

x = 1 
x = str(x)
x


##### Functions

# def - define
# function_name - can be named anything
# () - where inputs are provided
def function_name():
    print('you created a function!')


## Calling a function, i.e. utilizing a pair of parenthesis to use the function 
function_name()    

function_name # notice the lack of ()

def some_math(x):
    x **= 4
    return x # return provides the value itself back into your code

our_math_solution = some_math(5) # assigning the value of some_math to the variable - 'instantiation'
our_math_solution

##### Global / Local Variables

# Global Variable
# Exists in our scripts and can be utilized at any time
x = 6

# local variable
def local_var_test(x):
    if x==6:
        z = 5
        ### Z ONLY EXISTS IN THE PORTION OF THE CODE BASE AND NOT OUTSIDE OF IT. 

# how to gather a local variable
def give_me_my_var(x):
    if x==6:
        z = 5
        return z      
### HOMEWORK OVERVIEW and SCRIPTING PRACTICE. 

### Create new file. 

## We'll write some off the cuff code. Then run the code. 
## First, we run just a simple .py file in the terminal. 

## Next we use a function
## Run the script

## introduce main and how to utilize it. 

## if __name__ == "__main__":
## pass

## What this saying, is that the code below the if statement will only run when the file is executed as a script. 

## So we write code in the initial portion of our file

## zyx do code things

## then we run the above if statement

## if __name__ == "__main__":

    ## run zyx do things code


## __name__ is a variable itself, which holds information to where your code is running.
## __main__ is the "top-level" of python executable code, meaning it is the first file python sees
## When it begins running your systems. 
## When we run a new python file the __name__ is always equal to '__main__'. 

## When we import code, which we will do a lot of later, our python files have different values 
## associated with __name__. Generally they are the module's name.


#### Homework

### The premise here is that you will write functions to accomplish the tasks set out in each question prompt. 
## I will take your functions, pass inputs to them, then determine points based on your function's performance. 

## display an example

## New file, random function, then test inputs. 

### Write a function that has a single integer input. 
## Multiply this integer input by 1 and return the result. 

## def test_function(input1):
    # return input1 * 1

## Emphasis on naming conventions. 