---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---


# Basics and Course Overview

The course is divided into modules which contain a specific task/assignment which aids in completing the overall goal of the course. There is no need to worry if the concepts seem extremely easy to you or difficult there is something for everyone. The purpose of these sections it that it can also be used as a quick reference for some basic concepts before and after the course.

## General programming

Programming is giving the computer a list of instructions for computing in a language it can understand. In this material the language used is Python, specifically Jupyter Notebooks and Pywidgets. 

A language means a set of specific predefined semantics, instructions, and syntax rules, which are used for writing necessary instructions. It is strictly defined, meaning that 99.99% of all errors in the code are made by the coder, not by the computer.

Python scripts run with the help of a Python interpreter, but they can be written by using different software tools. Just like as you write your essay (you can type it in Word, Google Docs, Overleaf, or even on plain paper) you can write your Python code with different editors. You could use the default notepad, notepad++, find a proper website with an inbuilt code editor & interpreter (IDEone, for example), or use specialized Python code editors (Spyder, PyCharm, Visual Studio, etc). In all cases you will produce a set of instructions, which are stored in a file with the *.py extension and the interpreter will run it completely (from top to bottom).

For this course we will use a slightly different approach to developing a Python script: IPython and Jupyter Notebooks. Think of these as two freely-available tools that add extra functionality to the basic Python programming language. As an example, imagine the camera built into your phone: on it’s own it can take pictures, but there are many apps that add filters or sharing via social media that make the impact of your photos much more powerful. 

## OOPS

Throughout the project, you will write over 20 functions and a couple hundred lines of code. As you will find, there is exponential difficulty with the increase in project size. Writing many functions and testing challenges are all part of the project. The goal is to communicate with the car and interpret the data received, accurately find the car’s location, plan how to drive to the final destination,generate steering commands, and adjust the plan while you drive and discover objects. This short tutorial introduces object-oriented programming (OOP) concepts in Python, which is a programming method that provides flexibility. It is highly recommended that you learn how to use OOP, which will be useful throughout this project and future projects. The manual will provide code examples, assuming you understand basic OOP concepts to enhance the functionality of the KITT car project.

## Classes and Objects

```{code-cell}
class KITT:
def __init__(self, model, color):
self.model = model
self.color = color
self.is_engine_on = False
```
```{code-cell}
def start_engine(self):
self.is_engine_on = True
print(f"{self.model}'s engine started.")
```

```{code-cell}
def stop_engine(self):
self.is_engine_on = False
print(f"{self.model}'s engine stopped.")
```

**Attributes:** These are characteristics or properties that describe the state of an object. In the real world, consider attributes as the features defining an object. In the class definition, attributes are represented by variables. In the example, we have defined a class 'KITT' with attributes 'model', 'color', and 'is_engine_on'. Which are just some characteristic of KITT we could define.
**Methods:** These are functions that define the behavior of an object. They represent the actions that an object can perform. Methods are defined within the class and are used to manipulate the object’s state
(attributes) or perform some action associated with the object. Continuing with the car example, the
methods ’start_engine’ and ’stop_engine’ control the car’s engine.
**Self:** Within the class definition, ‘self’ is used to refer to the object.
**The __init__method** is a special method called the constructor. It is automatically called when a new
object is created. In this method, we initialize the model, color, and is_engine_on variables to the
values passed.

```{code-cell}
if __name__ == "__main__":
car1 = KITT("TRX4", "black") # Make the first instance of KITT
car2 = KITT("Rustler", "red") # Make the second instance of KITT
car2.color = "blue" # Change the color of car2
car1.start_engine() # Start the engine of car1
print(car1.is_engine_on) # Output: "True"
print(car1.model) # Output: "TRX4"
print(car1.color) # Output: "black"
```

First, two instances of KITT are made. They are made from the same KITT class (template) but are a
different model and color. These are stored as attributes to the instance (also called object). It is possible to change an attribute of an object after it has been made. In this example, the color of the second car is changed to blue. The state of the engine is also stored as an attribute. It is defaulted to False (the engine is off). Now, the engine of car 1 is started. When checked, car1 outputs that the engine is now set to on.

## Useful tips

* Go through all introductions for OOPS concepts and KITT project as this will lay a good foundation for the preliminary exercise and prepare you for the more difficult challenges in the course. 
- Also consider exploring on your own a little as this is a vast field and there is always room for improvement.
* When writing the code to implement functionalities required for this project, partition the code into separate functions and always include a header block with a function. In this header block, you should briefly describe the function, the required inputs, and what the output will do. Including a changelog with author names and dates is also good practice.
* Use meaningful variable names and write many comments so that others can understand what the code is doing.
* Define variables for constants such as *Fs* rather than using numbers throughout the code. That way, you give meaning to that number; if the number changes, you have to change it only at a single location.
* Avoid the use of globals. If a function needs a parameter, include it in the function call. If you must use globals, write the variable names in capitals. The risk of using globals is that if their value changes, it affects functions that depend on them while that dependency is hidden.
* Avoid the use of globals. If a function needs a parameter, include it in the function call. If you must use globals, write the variable names in capitals. The risk of using globals is that if their value changes, it affects functions that depend on them while that dependency is hidden.
- The test itself should also be in a script, so that you can frequently rerun it in case some of the functions have changed and need to be tested again.
* In your report, describe the overall structure of the code and the main variables so that others can quickly find their way into your code.
* Test every function in your code! For every ‘if’ statement in the code, you have two branches to test.







