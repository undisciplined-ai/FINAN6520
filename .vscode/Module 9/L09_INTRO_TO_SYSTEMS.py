

##### Week 9
## Goal: Continue to introduce OOP Concepts and Build a simple "system"

#### Super
#### Decorators
#### Class/Static/Instance Methods
### Point of Sale (POS) System

### Super()
## Super is a built in function providing a shortcut for calling in base/parent classes. 
## Parent classes are also referred to as Super classes
## Super accesses the parent class object and all its attributes/methods. 
## Super makes future code maintenence simpler. 
## When a parent class has an update, subsequent changes must flow to subclasses. If your subclass is
## using parent class methods/attributes, then you'll have to update as necessary
## Utilizing super() takes in the CURRENT instance of the parent class and code maintenence is less necessary.
# https://realpython.com/python-super/

class Animal:
    ## Construct the class
    def __init__(self,name):
        self.name = name

    ### A new method to discuss utilization down stream. 
    def migrate(self):
        return self.name + ' migrated'

class Elephant(Animal):

    def __init__(self, name, tusks):
        ### We inherit the abstract function and instantiate custom values.
        ## super takes on the entire parent function. 
        ## We can use all associated pieces using super() and python knows where to look
        # Animal().__init__(name) -- These are doing the same thing.
        super().__init__(name)
        self.tusks = tusks
    
    def migrate(self):
        ### We can use parent class functions in this manner. 
        ### Again, we are hoping to future proof our code base, so we want to use super() as much as possible. 
        return super().migrate() + ' to the west for water.'

    def speak(self):
        # Forgive the attempt to write out a dolphin sound. 
        return self.name + " says I'm an elephant!"

################### Conversation of Class/Static/Instance methods ###################

# https://realpython.com/instance-class-and-static-methods-demystified/

#### Decorators
# https://towardsdatascience.com/python-decorators-in-oop-3189c526ead6
# https://realpython.com/primer-on-python-decorators/#first-class-objects
# https://realpython.com/python-kwargs-and-args/

## Decorators are functions or classes which provide enhanced functionality to another function
## We wont be building out many custom decorators in the course, but we must know how they work.
## Decorators are functions themselves. They do specific operations before and/or after provided functions.
## They wrap themselves around provided functions and alter the way the provided function operates. 

## First lets build a simple function:
def our_fn(x,y):
    return x * y

our_fn(3,5)

### Our first decorator
## All we want to do is run two print statements. One before and one after our passed in function runs. 
## This is the function to call our decorator --> @our_decorator will access this function

def our_decorator(func):
    ## The inner function actually doing the heavy lifting. 
    ### We require *args/**kwargs here because the decorator is agnostic towards what is passed in.
    ### Our internal function knows what it needs, but the decorator can never accomodate every scenario. 
    ### More on *args/**kwargs in a moment. 
    def wrapper(*args,**kwargs):
        ## Our first print statement
        print('Did this before the function ran')
        ## Running our function
        print(func(*args,**kwargs))
        ### Second print statement
        print("Did this after the function ran")
    ### When the decorator is called we return the inner fuction and it runs. 
    return wrapper

#### Quick comments on *args, **kwargs
### Single star (*) and double star (**) are unpacking operators. 
## Single star unpacks element by element. So lists and tuples it will do the following:
test_list = ['a','b','c']
print(*test_list)
### This prints out each element by their representation value. 
### Works with any iterable. 


## double star upacks by key/value. So it expects dictionary type objects.
test_dict = {'key1':4,'key2':5}
### We usually use f-strings, but this is the older version of the same thing
## We will unpack each value from the targeted keys. 
output = "{key1} is less than {key2}".format(**test_dict)
print(output)


### *args
## Stands for "arguements"
## So now, *args are iterables we can upack into our functions. 
## We can use an unlimited amount of inputs in our functions (danger)
## args can be renamed into anything --> *birds
def my_sum(*args):
    ## Args is iterable, so we can loop over it and sum as many values as we want. 
    ## This is what sum does under the hood. 
    return sum(i for i in args)
my_sum(4)

my_sum(4,4,4,4)

### **kwargs
## Stands for key word arguments
## Allows our function to take in an infinite amount of keys and values.
## Kwargs can be renamed into anything --> **birds
def make_big_string(**kwargs):
    ### We're going to create a string out of everything passed in. 
    output = ""
    ## Kwargs is a dictionary. 
    for arg in kwargs.values():
        output += arg
    return output
## Keys are unrestricted!
make_big_string(x='1', b='2', key='3', four='4')


##### Finally this is how we implement a decorator. 
@our_decorator
def our_fn(x,y):
    return x * y

## Using our newly decorated function
our_fn(5,6)

### Instance Methods
## These are methods which work with current instances of the object
## Include the self keyword as an input
## They can modify anything in the instance of the class and have access to the whole object
## The most common method type, which we've used throughout today. 

### Class Methods
## utilizes the @classmethod decorator
## has an in put of "cls" in the method as an input, instead of self. 
## We're passing in a class object to the method. 
## These work with the object rather than the instance of the object
## cannot modify instance state 
## Can modify class state

### Static Methods
## @staticmethod decorator 
## They have no reserved word requirements to be passed in. 
## Cannot modify the instances of a class or the class state
## Python itself recognizes that this type of method cannot access instance or class data
## and subsequently restricts access even if we dont build out access. Essentially a second safeguard. 

class Example6:
    def method(self):
        return 'An Instance method:', self

    @classmethod
    def classmethod(cls):
        return 'A Class Method:', cls

    @staticmethod
    def staticmethod():
        return 'A Static Method'
    

### Burger class showcasing these tools.     
class Burger:
    def __init__(self, title,  ingredients):
        self.title = title
        ### Ingredients here is a list. 
        self.ingredients = ingredients

    ## Instance Method
    def __repr__(self):
        return f'Title: {self.title}\nIngredients: {self.ingredients}'
    ### these are "factory" functions, which build new class objects based on the calling
    ### of the class method. 
    ### With these we do not need to create new __init__ functions, they are already solved for us above. 
    @classmethod
    ### These create instances of the class with differing inputs. 
    def double_cheese(cls):
        ### Notice how cls refers to the class object without referencing the name. 
        ### This allows us to update the name of the class and not have to rehash old code with new convention.         
        return cls('Double Cheese Burger',['chedder', 'chedder', 'tomatoes', 'lettuce', 'patty'])

    @classmethod
    def pastrami(cls):
        return cls('Pastrami and Swiss', ['pastrami','swiss', 'tomatoes', 'lettuce', 'patty'])
    
    @staticmethod
    def proclaim_deliciousness():
        return "That's a yummy burger!"
        
# Class methods
Burger.double_cheese()
Burger.pastrami()

# Static Method
the_kinkade = Burger('The Kinkade',['chedder','chedder','lettuce','tomato','fried-egg', 'patty'])
the_kinkade.proclaim_deliciousness()

## Generator
### we can use class methods to generate many different instances of our class
### Here we'll create a list full of burgers, every positive integer will be a pastrami burger and the others are double cheese
### We'll use these in future lectures. 
burger_list = []

for i in range(0,9):

    if i % 2 == 0:
        burger_list.append(Burger.pastrami())
    else:
        burger_list.append(Burger.double_cheese())

burger_list


###### Point of Sale System
###### POS for a coffee shop 

import datetime as dt

# Product:
# Attributes: ID, name, price, category, quantity in stock, etc.

# Inventory:
# Attributes: products dict
# Methods: Add product, remove product, update quantity, check stock level, etc.

# Transaction:
# Attributes: basket, total value, ID
# Methods: Add product to basket, remove product from basket, generate sale and receipt

          
class Product:
    def __init__(self, product_id, name, price,quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        
    def __repr__(self):
        return f"{self.name} - ${self.price:.2f} - Count: {self.quantity}"

class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        if product.product_id not in self.products:
            self.products[product.product_id] = product
        else:
            raise ValueError("Product ID already exists.")

    def remove_product(self, product_id):
        if product_id in self.products:
            del self.products[product_id]
        else:
            raise ValueError("Product ID not found.")

    def update_quantity(self, product_id, new_quantity):
        if product_id in self.products:
            self.products[product_id].quantity = new_quantity
        else:
           raise ValueError("Product ID not found.")

    def check_stock_level(self, product_id):
        if product_id in self.products:
            return self.products[product_id].quantity
        else:
            raise ValueError("Product ID not found.")
        
class Transactions:
    
    def __init__(self):
        self.basket = {}
        self.total_amount = 0
        self.transaction_id = 1

    def add_to_basket(self, product_id, quantity):
        ### Add product to basket
        if product_id in self.products:
            product = self.products[product_id]
            if product.quantity >= quantity:
                self.basket[product_id] = {'DOLLAR_VALUE': product.price * quantity, 'QUANTITY': quantity}
                # self.total_amount += product.price * quantity
                self.update_quantity(product_id, product.quantity - quantity)
            else:
                raise ValueError("Insufficient stock.")
        else:
            raise ValueError("Product ID not found.")

    def remove_from_basket(self, product_id, quantity):
        ### Remove product from basket
        if product_id in self.basket.keys():
            product = self.products[product_id]
            if self.basket[product_id]['QUANTITY'] >= quantity:
                new_quantity = self.basket[product_id]['QUANTITY'] - quantity
                self.basket[product_id] = {'DOLLAR_VALUE': product.price * new_quantity,'QUANTITY': new_quantity}
                # self.total_amount += product.price * quantity
                self.update_quantity(product_id, product.quantity + quantity)
            else:
                raise ValueError("Cannot remove that many items.")
        else:
            raise ValueError("Product ID not found.")   

    def generate_sale_and_receipt(self):

        sale_value = 0

        print(f"Transaction ID: {self.transaction_id}")
        print(f"Time of Transaction: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("Items sold:")
        for product_id, product_details in self.basket.items():
            
            sale_value += product_details['DOLLAR_VALUE']
            
            print(f"    {self.products[product_id].name}: {product_details['QUANTITY']} - ${product_details['DOLLAR_VALUE']:.2f}")
        print("="*25)
        print(f"Total amount: ${sale_value:.2f}")

        self.basket = {}

### We inherit inventory and transactions classes to allow for the POS to utilize our pre-built tools
class SmallBusiness(Inventory, Transactions,):
    def __init__(self, ):        
        Inventory.__init__(self)
        Transactions.__init__(self)
        
magic_dirt_coffee_house = SmallBusiness()

magic_dirt_coffee_house.add_product(Product(1, 'Latte', 5, 50))
magic_dirt_coffee_house.add_product(Product(2, 'Americano', 4.50, 50))
magic_dirt_coffee_house.add_product(Product(3, 'Espresso', 3, 50))
magic_dirt_coffee_house.add_product(Product(4, 'Drip Coffee', 3, 50 ))


magic_dirt_coffee_house.products

magic_dirt_coffee_house.check_stock_level(1)

magic_dirt_coffee_house.remove_product(2)

magic_dirt_coffee_house.check_stock_level(2)

magic_dirt_coffee_house.add_to_basket(1,4)
magic_dirt_coffee_house.add_to_basket(2,4)

magic_dirt_coffee_house.generate_sale_and_receipt()

magic_dirt_coffee_house.basket