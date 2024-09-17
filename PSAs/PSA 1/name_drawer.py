"""
Module: name_drawer

A program to draw a name using one (or more) turtles.

Authors:
1) Cam Colucci - ccolucci@sandiego.edu 9/15/24
"""
import turtle

# Create a screen
screen = turtle.Screen()

# Create a turtle
tilly = turtle.Turtle()

# Get user input for pen color, pencil icon will be black
color = input("Enter desired pen color: ")
tilly.color(color,"black")

#Create a pencil shaped icon
pencil_shape = ((0, 0), (-5, 10), (-5, 50), (5, 50), (5, 10),  (0, 0))

# Register the shape with turtle
screen.register_shape("pencil", pencil_shape)

# Set the shape of the turtle to the custom pencil shape
tilly.shape("pencil")

# Begin drawing the "C"
tilly.pendown()
tilly.left(180)
tilly.forward(50)
tilly.left(90)
tilly.forward(100)
tilly.left(90)
tilly.forward(50)
tilly.penup()

# Begin drawing the "A"
tilly.goto(25, -100)
tilly.pendown()
tilly.goto(50, 0)
tilly.goto(75, -100)
tilly.penup()
tilly.goto(42, -50)  
tilly.pendown()
tilly.forward(16)
tilly.penup()

# Begin drawing the "M"
tilly.goto(100, -100)
tilly.pendown()
tilly.goto(100, 0)
tilly.goto(125, -50)
tilly.goto(150, 0)
tilly.goto(150, -100)
tilly.penup()

# Keep the turtle window open until clicked
turtle_window = turtle.Screen()
turtle_window.exitonclick()
