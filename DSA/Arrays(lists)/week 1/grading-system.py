# Problem 2: If-else Basics
# Grading System

# Write a program that:
# Takes a student's marks (out of 100) as input.
# Based on the marks, prints their grade according to this scheme:
# Marks Range	Grade
# 90 - 100	A
# 75 - 89	B
# 60 - 74	C
# 40 - 59	D
# Below 40	F

# Example:
# Input: 85
# Output: Grade: B
# Input: 35
# Output: Grade: F

Marks = int(input("Input: "))

if Marks >= 100 and Marks < 0:
    print("In valid input")
elif Marks >= 90 and Marks <= 100 :
    print("Grade: A")
elif Marks >= 75 and Marks <= 89 :
    print("Grade: B")
elif Marks >= 60 and Marks <= 74 :
    print("Grade: C")
elif Marks >= 40 and Marks <= 59 :
    print("Grade: D")
else: 
    print("Grade: F")

    
