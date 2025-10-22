
###############################################################################
######################### OBJECT ORIENTED PROGRAMMING #########################
###############################################################################
## Goal: Introduce OOP and Major Concepts.
## Comparing Functions and Classes
### instance / class variables
### Methods
#### Inheritance
#### Polymorphism
#### Encapsulation
#### Built-in Class Methods

## Regular function
def function(x,y):
    ## Do some internal thing
    x += 2
    ## Return the results
    return x * y

## In passed lectures we utilized functions to do perform tasks/jobs. 
## Each function had a task to complete and we used them together when necessary. 

## In advanced settings, functions are only part of the puzzle. 
## Functions are "Action-Focused" they are there to accomplish a given "action" and perform tasks in a sequence. 
## Task 1 leads into task 2 which leads into task 3, then the program is finished running. 

## Today we go over class objects, but it is not your first time seeing and using classes.

print(type(1))
print(type([]))
print(type({}))

## Clases objects exists in the base language and we utilize them every time we code.
## Whats important here is that objects are meant to be used for many different tasks,
## but they have a defined set of tools and duties they can do. 

## The power of programming languages comes from our ability to write custom classes and using "Object Oriented Programming"
## These objects can be simple, complex, or somewhere in between. 

## Classes are "State-Based" tools. 
## This really means we want to have multiple objects representing unique information, but having similar capabilties. 
## Think of bank accounts, properties, animals, and anything with unique attributes in similar taxonomies. 

##### Our first class
## Similar syntax as a function
## Define the object type as Example1. 
## Classes have leading capital letters, i.e. title format
class Example1:
    pass

## We "instantiate" the object as the variable "x"
    ## We create an INSTANCE of the class
x = Example1()
print(type(x))

### A Real Class
class Example2:
    ## Inititalization Method
    def __init__(self,input1):
        ### the init method takes in required inputs and sets them up inside the class
        ### This is an instance variable
            ### Instance variables only exist inside the class and represent one "instance" of the class / class data. 
        self.var1 = input1
        ## Self represents the object internally. Everything inside of the class is accessible through self.
        ## Pass in an input, assign the input to self.input ##

## Classes have attributes and methods
## Attributes are variables inside of the class
## Methods are functions within the class

first_class = Example2("inner_value")
second_class = Example2("another_value")

print(first_class.var1)
print(second_class.var1)

class Example3:
    ## This is an attribute every instance of Example3 will have. 
    ## Class variable. 
    class_attribute = 'WE_ALL_HAVE_THIS'
    def __init__(self, input1):
        self.var1 = input1

first_class = Example3("inner_value")
second_class = Example3("another_value")
third_class = Example3("yet_another_value")

print(first_class.var1, first_class.class_attribute)
print(second_class.var1, second_class.class_attribute)
print(third_class.var1, third_class.class_attribute)


### Methods
class Example4:
    def __init__(self, input1):
        self.var1 = input1
    def add(self,input2):
        return self.var1 + input2
    def subtract(self,input3):
        return self.var1 - input3

x = Example4(4)
x.add(3)

x.subtract(4)
x
### Notice var1 is not being altered
y = Example4(5)
y.add(1)
y


######################### PILLARS OF OOP #########################

### An animal class we'll use to display the pillars
class Animal:
    name = "No Name"
    def __init__(self):
        pass   
    def eat(self):
        print(f'{self.name.title()} is now eating.')
    def set_name(self,name):
        self.name = name

animal1 = Animal()
animal1.name
animal1.eat()

################### INHERITANCE ###################
# Inheritance is the procedure in which one class inherits the attributes and methods of another class. 
# The class whose properties and methods are inherited is known as the Parent class. 
# And the class that inherits the properties from the parent class is the Child class.

## Dog will *inherit* all methods and attributes of the Animal class
class Dog(Animal):
    ## We expect no new inputs upon instantiation
    def __init__(self):        
        ## Instantiates the parent class and attributes. 
        Animal.__init__(self)        
    def speak(self):
        return self.name.title() + ' is barking.'
        
dog = Dog()
## Will be the inherited name
dog.name
dog.eat()
dog.set_name('Homer')
dog.name
dog.speak()

################### POLYMORPHISM ###################
# This is a Greek word. If we break the term Polymorphism, we get “poly”-many and “morph”-forms.
# So Polymorphism means having many forms. 
# In OOP it refers to the functions having the same names but carrying different functionalities.

class Cat(Animal):
    def __init__(self):
        Animal.__init__(self)
    def speak(self):
        return self.name.title() + ' is meowing.'

cat = Cat()
cat.name 
cat.eat() 
cat.set_name('Ernie')
cat.name
## Notice how the above Dog class has the same function name(s), but they do something different. 
## This is polymorphism in action
## Classess are self referencing, meaning they do not know what other objects method names are
## and cannot accidentally utilize the wrong tool. 
cat.speak()

## To emphasize the point:
for pet in [dog,cat]:
    ## We have two classes with the same method and we have no issues using both. 
    print(pet.speak())


################### ENCAPSULATION ###################
# Private data and syntax 

# Basically, it hides the data from the access of outsiders. 
# Such as, if an organization wants to protect an object/information from unwanted access by clients or any unauthorized person, 
# then encapsulation is the way to ensure this.

# You can declare the methods or the attributes protected by using a single underscore before their names, 
# such as _self.name or def _method( ); Both of these lines tell that the attribute and method are protected and 
# should not be used outside the access of the class and sub-classes but can be accessed by class methods and objects.

# Though Python uses _ just as a coding convention, it tells that you should use these attributes/methods within the scope of 
# the class. But you can still access the variables and methods which are defined as protected, as usual.

# Now to actually prevent the access of attributes/methods from outside the scope of a class, you can use “private members“. 
# In order to declare the attributes/method as private members, use double underscore ( ) in the prefix. 
# Such as – self.name or def __method(); Both of these lines tell that the attribute and method are private and 
# access is not possible from outside the class.

class Example5:
    def __init__(self,input1,input2,input3):
        ## Total encapsulation (private), we cannot reference this value outside of the class
        self.__input1 = input1
        ## Symantically encapsulated, we can access the value from outside, but we recommened not to. 
        self._input2 = input2
        ## A regular attribute
        self.input3 = input3

    def description(self):
        return f'This is {self.__input1}, this is {self._input2}, and this is {self.input3}'
    
    def __secret_method(self):
        return len(self.__input1) * len(self.input3)
    
    def do_secret_thing(self):
        return self.__secret_method()

test = Example5('secret_var', "not_so_secret", 'public')
## Will print out both values, because __input1 is an internal "private" variable
## It is built in such a way that activities outside the class are not possible when referencing __input1. 
test.description()
## Breaks intentionally, cannot be referenced. 
test.__input1
## Can be referenced, but is expressed as an internal value by syntax 
test._input2
test.input3

test.__secret_method()
test.do_secret_thing()

### Thought exercise:
## When would this matter? If we are building tools to utilize information and data in/outside our classes, 
## then why would we want to hide some of the data?

## Think of a web-application for a few moments. What sorts of information would we want to protect?

## social security, passport data, private user identification data are great examples. 
## These may be totally necessary, but we may not want to pass them out of the backend ever. 


################### ABSTRACTION ###################
## Put confusingly, an abstract class is a class with one or more abstract methods. 
## Abstract methods are declared but not implemented, meaning subclasses will have to implent them 
## *** Abstract classes act as formal blueprints for other classes *** ##

#### We will not study this concept. It is generally reserved for more sophisticated examples and broad systems. 


################### PYTHONIC CLASS METHODS ################### 
### We've seen dunder methods before, they are built-in tools in the language with a prescribed action. 
## __init__ is a tool we use to build out an initial state of a class. 
## We don't need to go over its usage again.

## There are many built-in methods like __init__
# https://mathspp.com/blog/pydonts/dunder-methods#list-of-dunder-methods-and-their-interactions
### In-depth conversation of each dunder
# https://www.tutorialsteacher.com/python/magic-methods-in-python

## We will go over a few we'll use the rest of semester. These tools make our custom classes more useful and robust.

## The story here is that we can use built-in methods to make our classes adhere to the rest of the python ecosystem
## We can build class objects to be divided as if they were numbers, operate with dictionary tools, and more. 
## The biggest key here:
#*** YOU DO NOT HAVE TO USE THESE WITH EVERY CLASS **#
## They are tools, they are not --required-- tools. They really should only be used as they come into necessity. 
## If you are working on systems not accessible to the open source community, you likely dont need to build out as many.
## On the other hand, some open source packages become quite strict on how they operate and provide tools to their users. 
## This means they will likely build out pythonic tooling to make use of their custom tools cohesive with the rest of the ecosystem. 

### Displays many built-in methods already present in any object. 
dir(object())

class Rectangle:

    def __init__(self,length, width):
        self.length = length
        self.width = width
    
    def perimeter(self):
        return 2 * (self.length + self.width)

    def area(self):
        return self.length * self.width

    def __repr__(self):
        ### An official string of information related to the object
        ### Meant for debugging and differentiation of objects    
        return f"Rectangle({self.length} x {self.width})"    

    def __str__(self):
        ### A human readable output for user consumption
        return f"Rectangle of length {self.length} and width of {self.width}"

    ## First, run comparison without this. 
    def __eq__(self, other):
        ### Will utilize internal attributes to compare equality. 
        ## We know both objects are not referencing the same instance object.      
        ## We want to compare apples to apples here   

        ## Third step is to build out isinstance()
        ## isinstance() is a tool we can use to compare typing in a clean way. 
        ## Pass in the object type, then the comparison object
        if isinstance(other, Rectangle):
            return (self.length == other.length) & (self.width == other.width)
        else:
            return False

    ## First, run without iteration
    ## TypeError: 'Rectangle' object is not iterable
    def __iter__(self):
        ## We have to think about what an iteration of our object would look like
        ## We have two data points, length and width
        ## Our object logic should present this information in the way it was passed in
        ## First we return length, then width because we want cohesion with loading data in and out. 
        return (i for i in (self.length, self.width))
        ## This is a tuple unpacking for loop.
        ## i is returned in ever iteration in an external loop. 
        ## We create a tuple object with our length and width to offload. 

    ##### STEP ONE #####
    ## First, run without 
    ## TypeError: unsupported operand type(s) for *: 'Rectangle' and 'int'
    def __mul__(self, number):
        ## we only want int or float values 
        ## The tuple allows us to compare the target value to both types
        if isinstance(number, (int, float)):
            ## We want to multiply both length and width by the number
            ## This does nothing to our base object
            ## We offer the internal values multiplied by the passed in value as a tuple
            ##### STEP TWO #####
            # return (self.length * number, self.width * number)
            ##### STEP THREE #####
            #**** This is RECURSION ****#
            ## Recursion is when a class or object is utilized within itself. 
            ## We are utilizing the new number to alter our current values
            ## Then use them to create a new rectangle object. 
            return Rectangle(self.length * number, self.width * number)

        ## Proper error handling 
        ## We do not need the else statement here. 
        raise TypeError(f'Cannot multiply a Rectangle with {type(number)}') 
    
    ### This allows us to manage both sides of operations.
    ## We re-use the method we built above to do the same task on both sides. 
    def __rmul__(self, other): 
        return self.__mul__(other)    

### This output is the representation string, this is what python automatically runs with. 
# Rectangle(4,4)

### Utilizing the print statement upon the object
# x = Rectangle(4,4)
# print(x)

### Check the methods we built
# x.perimeter()
# x.area()

### First we see how the equality conditional will operate
# y = Rectangle(4,4)
# x == y ## False, they are not referencing the same underlying object in our python instance.
## After creating the __eq__ call run again
# y = Rectangle(4,4)  -- Dont forget to rebuild the object
# x == y # True
## Then perform this:
# x == 4 -- Which will break because integers to not have the correct attributes to check equality here. 
## Add in new isinstance() and check again
# x = Rectangle(4,4)  -- Dont forget to rebuild the object
# x == 4 # False
## This does not work, because the Rectangle and Int are not comparable in this way. 
# x >= 4

### Utilizing __iter__
# for i in x:
#     print(i)
## After building, try again
# x = Rectangle(4,4) -- Dont forget to rebuild the object
# for i in x:
#     print(i)

### A conversation on mathematical methods
## __mult__
# x * 4
## This will work, because the objects compared are allowed to be compared. 
# x.length * 4
## We want to mutiply the internal objects by the passed in value
# x = Rectangle(4,4)
# x * 4
#** All of this would have to be built for each type of mathematical operation **#
## Finally, what if we wanted to re-use the outcome?
# x = Rectangle(4,4)
# print(x)
# x * 4
### The result of this action is a new object, we could reassign this to our previous variable and continue
# x = x * 4
##### ONE LAST THING!!!
## if we attempted the following we would fail. 
## We do not have a built in capability to manage operations on both sides of a math operation
# 4 * x

##### DEPENDING ON TIME, BEGIN THE NEXT LECTURE. 